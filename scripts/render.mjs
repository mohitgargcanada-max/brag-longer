// Renders chapters frame by frame in headless Chromium and pipes them to ffmpeg.
//   node render.mjs <workspace> video [1,2,...]       -> build/out/video/chNN-<hash>.mp4 (reused while inputs are unchanged)
//   node render.mjs <workspace> stills N [t1 t2 ...]  -> build/out/stills/chNN-<t>.png (default: every scene + mid-transitions)
// A chapter's hash covers the engine, kit, player, its chapter file, everything in brand/ and its timeline entry, so an
// edit re-renders exactly the chapters it touches. Progress with an ETA per chapter: build/out/video/progress-chNN.txt.
// Needs playwright-core (set PLAYWRIGHT_CORE to its folder if it is not resolvable) and a Chromium headless shell
// (set CHROME_PATH, or install with `npx playwright install chromium-headless-shell`).
import { createRequire } from 'node:module';
import { spawn, execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const [rootArg, mode, ...args] = process.argv.slice(2);
const ROOT = path.resolve(rootArg);
const require = createRequire(path.join(ROOT, 'noop.js'));
const { chromium } = require(process.env.PLAYWRIGHT_CORE || 'playwright-core');
const cfg = JSON.parse(fs.readFileSync(path.join(ROOT, 'video.json'), 'utf8'));
const FPS = cfg.fps || 30;
const SCENES = path.join(ROOT, 'build', 'scenes');
const OUT = path.join(ROOT, 'build', 'out');
const FFMPEG = execFileSync('python', ['-c', 'import imageio_ffmpeg as f;print(f.get_ffmpeg_exe())']).toString().trim();

function findChrome() {
  if (process.env.CHROME_PATH) return process.env.CHROME_PATH;
  const bases = [process.env.PLAYWRIGHT_BROWSERS_PATH, process.env.LOCALAPPDATA && path.join(process.env.LOCALAPPDATA, 'ms-playwright'),
    path.join(os.homedir(), 'Library', 'Caches', 'ms-playwright'), path.join(os.homedir(), '.cache', 'ms-playwright')].filter(Boolean);
  for (const base of bases) {
    if (!fs.existsSync(base)) continue;
    for (const d of fs.readdirSync(base).filter(d => d.startsWith('chromium_headless_shell-')).sort().reverse()) {
      for (const sub of fs.readdirSync(path.join(base, d))) {
        for (const exe of ['chrome-headless-shell.exe', 'chrome-headless-shell']) {
          const p = path.join(base, d, sub, exe);
          if (fs.existsSync(p)) return p;
        }
      }
    }
  }
  throw new Error('No Chromium headless shell found: run `npx playwright install chromium-headless-shell` or set CHROME_PATH');
}

const timeline = JSON.parse(fs.readFileSync(path.join(OUT, 'timeline.json'), 'utf8'));
const videoOpts = { chapterLabels: cfg.chapter_labels !== false };
const timelineJs = `window.TIMELINE = ${JSON.stringify(timeline)};\nwindow.VIDEO_OPTS = ${JSON.stringify(videoOpts)};\n`;
const timelinePath = path.join(OUT, 'timeline.js');
// Several renders run at once; only write when the content changed so none reads a half-written file.
if (!fs.existsSync(timelinePath) || fs.readFileSync(timelinePath, 'utf8') !== timelineJs) fs.writeFileSync(timelinePath, timelineJs);

const pad = n => String(n).padStart(2, '0');
const filesUnder = dir => !fs.existsSync(dir) ? [] : fs.readdirSync(dir, { withFileTypes: true }).flatMap(e =>
  e.isDirectory() ? filesUnder(path.join(dir, e.name)) : [path.join(dir, e.name)]).sort();

function inputHash(n) {
  const h = createHash('sha1');
  for (const f of ['engine.js', 'kit.js', 'kit.css', 'player.html', `ch${pad(n)}.js`]) h.update(fs.readFileSync(path.join(SCENES, f)));
  for (const f of filesUnder(path.join(ROOT, 'brand'))) h.update(fs.readFileSync(f));
  h.update(JSON.stringify(timeline.find(c => c.n === n)));
  h.update(JSON.stringify(videoOpts));
  return h.digest('hex').slice(0, 10);
}

async function openChapter(browser, n) {
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  await page.goto(pathToFileURL(path.join(SCENES, 'player.html')).href + `?ch=${n}`);
  try { await page.waitForFunction('window.ready === true', null, { timeout: 30000 }); }
  catch { throw new Error(`ch${pad(n)} never became ready: ${errors.join(' | ') || 'no error logged'}`); }
  if (errors.length) throw new Error(`ch${pad(n)} page errors: ${errors.join(' | ')}`);
  return page;
}

async function renderVideo(browser, n) {
  const dir = path.join(OUT, 'video');
  fs.mkdirSync(dir, { recursive: true });
  const target = path.join(dir, `ch${pad(n)}-${inputHash(n)}.mp4`);
  if (fs.existsSync(target)) { console.log(`ch${pad(n)}: reusing ${path.basename(target)}`); return path.basename(target); }
  const page = await openChapter(browser, n);
  const frames = Math.round((await page.evaluate('window.chapterDuration')) * FPS);
  const tmp = target.replace('.mp4', '.partial.mp4');
  const ff = spawn(FFMPEG, ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-r', String(FPS), tmp]);
  let ffErr = '';
  ff.stderr.on('data', d => { ffErr += d; });
  const done = new Promise((res, rej) => ff.on('close', c => (c === 0 ? res() : rej(new Error(`ffmpeg ch${pad(n)}: ${ffErr}`)))));
  const started = Date.now();
  const progress = path.join(dir, `progress-ch${pad(n)}.txt`);
  for (let f = 0; f < frames; f++) {
    await page.evaluate(t => window.seek(t), f / FPS);
    const buf = await page.screenshot({ type: 'jpeg', quality: 93 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 150 === 0) fs.writeFileSync(progress, `ch${pad(n)} ${f}/${frames} frames, ETA ${Math.round((Date.now() - started) / (f + 1) * (frames - f) / 1000)}s\n`);
  }
  ff.stdin.end();
  await done;
  await page.close();
  fs.renameSync(tmp, target);
  const secs = Math.round((Date.now() - started) / 1000);
  fs.writeFileSync(progress, `ch${pad(n)} done: ${frames} frames in ${secs}s\n`);
  console.log(`ch${pad(n)}: ${path.basename(target)} (${frames} frames, ${secs}s)`);
  return path.basename(target);
}

async function renderStills(browser, n, times) {
  const dir = path.join(OUT, 'stills');
  fs.mkdirSync(dir, { recursive: true });
  const page = await openChapter(browser, n);
  if (!times.length) {
    for (const [from, to] of await page.evaluate('window.sceneTimes')) {
      times.push(from + Math.min(2.5, (to - from) / 2), Math.max(from, to - 0.6));
      if (from > 0) times.push(from + 0.2);  // mid-transition
    }
  }
  for (const t of times) {
    await page.evaluate(x => window.seek(x), t);
    const file = path.join(dir, `ch${pad(n)}-${t.toFixed(1).padStart(5, '0')}.png`);
    await page.screenshot({ path: file });
    console.log(file);
  }
  await page.close();
}

const browser = await chromium.launch({ executablePath: findChrome(), args: ['--hide-scrollbars', '--force-color-profile=srgb', '--allow-file-access-from-files'] });
try {
  if (mode === 'stills') await renderStills(browser, +args[0], args.slice(1).map(Number));
  else if (mode === 'video') {
    const queue = args[0] ? args[0].split(',').map(Number) : timeline.map(c => c.n);
    // manifest.json names the render that belongs to the CURRENT timeline for each chapter; mix.py reads only that,
    // so a chapter that failed to re-render can never be silently replaced by an older file.
    const manifestPath = path.join(OUT, 'video', 'manifest.json');
    const timelineHash = createHash('sha1').update(fs.readFileSync(path.join(OUT, 'timeline.json'))).digest('hex');
    let manifest = fs.existsSync(manifestPath) ? JSON.parse(fs.readFileSync(manifestPath, 'utf8')) : {};
    if (manifest.timeline !== timelineHash) manifest = { timeline: timelineHash, chapters: {} };
    const worker = async () => {
      while (queue.length) {
        const n = queue.shift();
        manifest.chapters[n] = await renderVideo(browser, n);
        fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 1));
      }
    };
    await Promise.all(Array.from({ length: Math.min(4, queue.length) }, worker));
  } else throw new Error('mode must be "video" or "stills"');
} finally {
  await browser.close();
}
