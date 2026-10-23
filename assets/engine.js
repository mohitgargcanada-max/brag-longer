// Scene engine for brag-longer videos. Every frame is a pure function of time: nothing animates by
// itself (no CSS transitions or animations), window.seek(t) sets every style for chapter time t.
// A chapter file calls Demo.chapter(n, C => [scenes]); each scene is {from, to, demo?, build(layer) -> update(t, T)}
// where t is seconds since the scene started and T is chapter time.

const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, p) => a + (b - a) * p;
const ease = {
  linear: x => x,
  out: x => 1 - Math.pow(1 - x, 3),
  inOut: x => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2),
  back: x => 1 + 2.4 * Math.pow(x - 1, 3) + 1.4 * Math.pow(x - 1, 2),
};
// 0..1 progress of an animation that starts at `start` and lasts `dur` seconds.
const prog = (t, start, dur = 0.6, e = ease.out) => e(clamp((t - start) / dur));

function h(html) {
  const tpl = document.createElement('template');
  tpl.innerHTML = html.trim();
  return tpl.content.firstElementChild;
}

// Fade + rise in. Returns the progress so callers can chain.
function reveal(el, t, start, { dur = 0.6, dy = 24, dx = 0, scale = 1 } = {}) {
  const p = prog(t, start, dur);
  el.style.opacity = p;
  el.style.transform = `translate(${(1 - p) * dx}px, ${(1 - p) * dy}px) scale(${lerp(scale, 1, p)})`;
  return p;
}

// Types `text` into el from `start` at `cps` characters a second, with a caret while typing.
function typeText(el, text, t, start, cps = 28, caret = true) {
  const n = Math.floor(clamp((t - start) * cps, 0, text.length));
  const typing = t >= start && n < text.length;
  el.textContent = text.slice(0, n);
  el.dataset.caret = caret && (typing || (t >= start && Math.floor(t * 2) % 2 === 0 && t < start + text.length / cps + 1.2)) ? '1' : '';
  return n === text.length;
}

function countUp(el, value, t, start, dur = 1.4, fmt = v => Math.round(v).toLocaleString('en-CA')) {
  el.textContent = fmt(value * prog(t, start, dur, ease.out));
}

// Camera: interpolates {t, x, y, s} keyframes (translate in px, then scale) with inOut easing between them.
function camera(el, t, keys) {
  let k = keys[0];
  if (t >= keys[keys.length - 1].t) k = keys[keys.length - 1];
  else for (let i = 0; i < keys.length - 1; i++) {
    const a = keys[i], b = keys[i + 1];
    if (t >= a.t && t < b.t) {
      const d = b.d ?? Math.min(1.2, b.t - a.t);
      const p = ease.inOut(clamp((t - (b.t - d)) / d));
      k = { x: lerp(a.x, b.x, p), y: lerp(a.y, b.y, p), s: lerp(a.s, b.s, p) };
      break;
    }
  }
  el.style.transformOrigin = '0 0';
  el.style.transform = `translate(${k.x}px, ${k.y}px) scale(${k.s})`;
}

// A mouse pointer that glides between {t, x, y, click?} points, with a ripple on click.
function makeCursor(layer) {
  const c = h(`<div class="cursor"><svg width="34" height="34" viewBox="0 0 24 24"><path d="M4 2l16 9.5-7 1.6L9.6 20z" fill="#fff" stroke="#121124" stroke-width="1.4" stroke-linejoin="round"/></svg><i></i></div>`);
  layer.appendChild(c);
  return (t, pts) => {
    let x = pts[0].x, y = pts[0].y, ripple = 0;
    for (let i = 1; i < pts.length; i++) {
      const a = pts[i - 1], b = pts[i], d = b.move ?? 0.7;
      if (t >= b.t - d) {
        const p = ease.inOut(clamp((t - (b.t - d)) / d));
        x = lerp(a.x, b.x, p); y = lerp(a.y, b.y, p);
      }
      if (b.click && t >= b.t && t < b.t + 0.5) ripple = (t - b.t) / 0.5;
    }
    c.style.opacity = prog(t, pts[0].t, 0.3, ease.linear) * (1 - prog(t, pts[pts.length - 1].hide ?? 1e9, 0.3, ease.linear));
    c.style.transform = `translate(${x}px, ${y}px)`;
    const r = c.querySelector('i');
    r.style.opacity = ripple ? 1 - ripple : 0;
    r.style.transform = `translate(-50%, -50%) scale(${0.3 + ripple * 1.4})`;
  };
}

const Demo = {
  defs: {},
  chapter(n, fn) { this.defs[n] = fn; },

  start(n) {
    const tl = window.TIMELINE.find(c => c.n === n);
    const C = {
      n, tl, duration: tl.duration, sentences: tl.sentences,
      sent: i => tl.sentences[i].start,
      sentEnd: i => tl.sentences[i].end,
      // Start / end of spoken paragraph p (0-based, in script order within the chapter).
      para: p => tl.sentences.find(s => s.p === p).start,
      paraEnd: p => tl.sentences.filter(s => s.p === p).pop().end,
      // Time a word first gets spoken, estimated by its character position inside its sentence.
      word: (needle, from = 0) => {
        for (const s of tl.sentences.slice(from)) {
          const k = s.text.indexOf(needle);
          if (k >= 0) return s.start + (s.end - s.start) * (k / s.text.length);
        }
        throw new Error(`word not found: ${needle}`);
      },
    };
    const stage = document.getElementById('stage');
    const label = h(`<div class="chapter-label"><b>${String(n).padStart(2, '0')}</b><span>${tl.title}</span></div>`);
    const chip = h(`<div class="demo-chip">Fictional demo business</div>`);
    const scenes = this.defs[n](C).map(s => {
      const layer = h(`<div class="layer"></div>`);
      stage.appendChild(layer);
      return { ...s, layer, update: s.build(layer, C) };
    });
    stage.append(label, chip);
    scenes.forEach((s, i) => { if (s.to === undefined) s.to = scenes[i + 1]?.from ?? C.duration; });

    window.seek = T => {
      let demo = 0, chrome = 0;
      for (const s of scenes) {
        // Dip through the background between scenes: the old one is out before the new one comes in.
        const inP = s.from <= 0 ? 1 : prog(T, s.from, 0.45, ease.linear);
        const outP = s.to >= C.duration ? 0 : prog(T, s.to - 0.35, 0.35, ease.linear);
        const o = T < s.from || T >= s.to ? 0 : inP * (1 - outP);
        s.layer.style.opacity = o;
        s.layer.style.visibility = o > 0 ? 'visible' : 'hidden';
        if (o > 0) {
          s.update(T - s.from, T);
          if (s.demo) demo = Math.max(demo, o);
          if (!s.hideLabel) chrome = Math.max(chrome, o);
        }
      }
      // Fade the whole chapter in from and out to black at its ends.
      stage.style.opacity = prog(T, 0, 0.5, ease.linear) * (1 - prog(T, C.duration - 0.6, 0.6, ease.linear));
      chip.style.opacity = demo;
      // Chapter labels can be switched off for the whole film (video.json "chapter_labels": false).
      label.style.opacity = window.VIDEO_OPTS && window.VIDEO_OPTS.chapterLabels === false ? 0 : chrome * 0.9;
    };
    window.chapterDuration = C.duration;
    window.sceneTimes = scenes.map(s => [s.from, s.to]);
  },
};
