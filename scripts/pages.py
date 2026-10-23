"""Build the review and delivery pages for a brag-longer workspace (published afterwards with the Artifact tool).

python -P pages.py <workspace> script                     -> pages/script.html (the script, for approval)
python -P pages.py <workspace> voices "<line>" id=Label ... -> pages/voices.html (samples/ mp3s embedded, to pick by ear)
python -P pages.py <workspace> clips <version>            -> preview-<version>/chNN.mp4 (720p captioned chapter clips)
python -P pages.py <workspace> all                        -> pages/all-versions.html + prints the `files` map
python -P pages.py <workspace> single <version> <poster seconds> "<title>" "<description>"
                                                          -> video-<version>/index.html + poster.jpg + prints the `files` map

`all` reads versions.json in the workspace: a list, newest first, of {"version", "title", "description"}. Every
version's clips and timeline snapshot must exist. `single` needs split_for_download.py run on final/<name>-<version>.mp4
into dl/<version>/ first. Templates come from build/templates (copied there by scaffold.py; restyle them per brand).
video.json may set "product" (shown on pages) and "fiction_note" (the line saying which data is invented).
"""
import base64
import hashlib
import html
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -P drops the script folder; common.py lives here
from common import Workspace, ffmpeg

ws, mode, args = Workspace(sys.argv[1]), sys.argv[2], sys.argv[3:]
product = ws.cfg.get("product", ws.cfg["name"])
note = ws.cfg.get("fiction_note", "")
pages = ws.root / "pages"
pages.mkdir(exist_ok=True)


def fill(template, values):
    s = (ws.templates / template).read_text(encoding="utf-8")
    for k, v in values.items():
        assert s.count(k) >= 1, f"{template}: placeholder {k} missing"
        s = s.replace(k, v)
    return s


def mmss(seconds):
    return f"{int(seconds // 60)}:{int(seconds % 60):02d}"


def chapters(version):
    fps, off, rows = ws.cfg["fps"], 0.0, []
    for c in ws.timeline(version):
        d = round(c["duration"] * fps) / fps
        rows.append({"n": c["n"], "title": c["title"], "start": round(off, 1), "dur": round(d, 1)})
        off += d
    return rows, off


if mode == "script":
    title_line, rest = ws.script.read_text(encoding="utf-8").split("\n", 1)
    intro, body_md = rest.split("---", 1)
    out, words = [], 0
    for b in re.split(r"\n\s*\n", body_md):
        b = " ".join(b.split())
        if not b:
            continue
        if b.startswith("## "):
            out.append(f'</section><section class="ch"><h2>{html.escape(b[3:])}</h2>')
        elif b.startswith("Screen:"):
            out.append(f'<p class="screen"><b>On screen</b>{html.escape(b[7:].strip())}</p>')
        elif b.startswith("<!--"):
            out.append(f'<p class="src">{html.escape(b.strip("<!-> "))}</p>')
        else:
            words += len(b.split())
            out.append(f'<p class="say">{html.escape(b)}</p>')
    body = "".join(out).replace("</section>", "", 1) + "</section>"
    notes = "".join(f'<p class="note">{html.escape(" ".join(p.split()))}</p>' for p in intro.strip().split("\n\n") if p.strip())
    style = """<style>
.ch { display: grid; gap: 12px; border-top: 1px solid var(--line); padding-top: 22px; }
.ch h2 { font: 600 21px/1.3 var(--display); color: var(--brand); margin: 0; }
.say { color: var(--ink); font-size: 17px; line-height: 1.65; }
.screen { font-size: 13px; color: var(--muted); background: var(--card); border: 1px solid var(--line); border-radius: 10px; padding: 8px 12px; }
.screen b { font: 600 11px var(--display); letter-spacing: .08em; text-transform: uppercase; color: var(--accent); margin-right: 6px; }
.src { font-size: 12px; color: var(--gold); }
.note { font-size: 14px; }
main { max-width: 720px; }
</style>"""
    body = (f'<section><p class="eyebrow">{html.escape(title_line.lstrip("# "))} &middot; {words:,} spoken words</p>'
            f'<h1>{html.escape(product)} video script</h1>{notes}<p class="note">Large text is spoken. Boxed lines describe what '
            f'is on screen. Gold lines name the source behind each figure.</p></section>{body}')
    page = fill("page_template.html", {"/*TITLE*/": f"{product} Video Script", "/*BODY*/": style + body})
    (pages / "script.html").write_text(page, encoding="utf-8")
    print(pages / "script.html", f"{words} spoken words")

elif mode == "voices":
    line, labels = args[0], [a.split("=", 1) for a in args[1:]]
    cards = "".join(
        f'<article class="voice"><header><h2>{html.escape(label)}</h2><span class="tag">{html.escape(v)}</span></header>'
        f'<audio controls preload="metadata" src="data:audio/mpeg;base64,'
        f'{base64.b64encode((ws.root / "samples" / f"sample-{v}.mp3").read_bytes()).decode()}"></audio></article>'
        for v, label in labels)
    body = (f'<section><p class="eyebrow">{html.escape(product)} video narration</p><h1>Pick the voice</h1>'
            f'<p>Every sample reads the same line. Play each, then say which one you want.</p></section>'
            f'<blockquote>{html.escape(line)}</blockquote><section class="voices">{cards}</section>')
    page = fill("page_template.html", {"/*TITLE*/": f"{product} Video Voices", "/*BODY*/": body})
    (pages / "voices.html").write_text(page, encoding="utf-8")
    print(pages / "voices.html", f"{len(page) // 1024} KB")

elif mode == "clips":
    version = args[0]
    out = ws.root / f"preview-{version}"
    out.mkdir(exist_ok=True)
    src = ws.final / f"{ws.stem(version)}-captioned.mp4"
    for c in chapters(version)[0]:
        if c["dur"] > 240:
            print(f"WARNING: chapter {c['n']} is {c['dur'] / 60:.1f} min; its clip may pass the 15 MB page limit. Plan chapters under 3 min.")
        clip = out / f"ch{c['n']:02d}.mp4"
        subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-ss", f"{c['start']:.3f}", "-i", str(src), "-t", f"{c['dur']:.3f}",
                        "-vf", "scale=1280:720", "-c:v", "libx264", "-preset", "medium", "-crf", "27", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", str(clip)], check=True)
        print(f"{clip.name}: {clip.stat().st_size / 1e6:.1f} MB")

elif mode == "all":
    # Each entry may carry "url": the version's single-file page (pages.py single, published), shown as a link.
    versions = json.loads((ws.root / "versions.json").read_text(encoding="utf-8"))
    with_clips = ws.cfg["delivery"] != "single"
    data, files = [], {}
    for v in versions:
        rows, total = chapters(v["version"])
        if with_clips:
            for c in rows:
                clip = ws.root / f"preview-{v['version']}" / f"ch{c['n']:02d}.mp4"
                assert clip.exists(), f"missing {clip}: run `pages.py <ws> clips {v['version']}`"
                files[f"{v['version']}/{clip.name}"] = str(clip.relative_to(ws.root)).replace("\\", "/")
        else:
            assert v.get("url"), f"delivery is single: give {v['version']} the url of its single-file page in versions.json"
        data.append({"id": v["version"], "dir": v["version"], "title": v["title"], "length": mmss(total),
                     "description": v["description"], "chapters": rows if with_clips else [], "url": v.get("url", "")})
    page = fill("preview_all_template.html", {"/*VERSIONS*/[]": json.dumps(data), "/*PRODUCT*/": html.escape(product),
                                              "/*NOTE*/": html.escape(note), "/*FINAL_DIR*/": html.escape(str(ws.final))})
    (ws.root / "all-versions.html").write_text(page, encoding="utf-8")
    size = sum((ws.root / p).stat().st_size for p in files.values()) / 1e6
    print(json.dumps(files))
    print(f"{ws.root / 'all-versions.html'}: {len(files)} clips, {size:.1f} MB (publish in batches of under 64 MB)")

elif mode == "single":
    version, poster_t, title, description = args
    final = ws.final / f"{ws.stem(version)}.mp4"
    chunks = ws.root / "dl" / version
    out = ws.root / f"video-{version}"
    out.mkdir(exist_ok=True)
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-ss", poster_t, "-i", str(final), "-frames:v", "1",
                    "-vf", "scale=1280:720", "-q:v", "3", str(out / "poster.jpg")], check=True)
    parts = sorted(p.name for p in chunks.glob(f"{ws.stem(version)}.part*.txt"))
    data = final.read_bytes()
    assert parts and hashlib.sha256(b"".join(base64.b64decode((chunks / p).read_bytes()) for p in parts)).digest() \
        == hashlib.sha256(data).digest(), "chunks missing or stale: run split_for_download.py on the final MP4"
    video = {"version": version.lstrip("v"), "title": title, "description": description,
             "length": mmss(sum(round(c["duration"] * ws.cfg["fps"]) / ws.cfg["fps"] for c in ws.timeline(version))),
             "file": final.name, "label": f"1080p · {len(data) / 1e6:.1f} MB", "sha256": hashlib.sha256(data).hexdigest(),
             "poster": "poster.jpg", "parts": parts}
    page = fill("single_video_template.html", {"/*TITLE*/": html.escape(title), "/*VIDEO*/{}": json.dumps(video),
                                               "/*PRODUCT*/": product.replace("`", ""), "/*NOTE*/": html.escape(note),
                                               "/*FINAL_DIR_JS*/": str(ws.final).replace("\\", "\\\\").replace("'", "")})
    (out / "index.html").write_text(page, encoding="utf-8")
    files = {"poster.jpg": f"video-{version}/poster.jpg", **{p: f"dl/{version}/{p}" for p in parts}}
    total_mb = sum((chunks / p).stat().st_size for p in parts) / 1e6
    if total_mb > 240:  # a page version holds 256 MB in all
        print(f"WARNING: {total_mb:.0f} MB of chunks will not fit on one page (256 MB per version). Split the film into "
              "parts at a chapter boundary and give each part its own page (references/delivery.md).")
    print(json.dumps(files))
    print(f"{out / 'index.html'}: {len(parts)} chunks, {sum((chunks / p).stat().st_size for p in parts) / 1e6:.1f} MB (publish in batches of under 64 MB)")

else:
    raise SystemExit(__doc__)
