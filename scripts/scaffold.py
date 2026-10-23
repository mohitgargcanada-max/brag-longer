"""Create a brag-longer video workspace.

python -P scaffold.py <workspace dir> "<Name>"     e.g.  scaffold.py C:/proj/demo-video "Acme-Demo"

Copies the scene engine, player, base styles, page templates and the scene-builder brief into the workspace, and writes
a starter video.json and script. Existing files are never overwritten, so it is safe to run again after an upgrade of
the skill (it only adds what is missing).
"""
import json
import shutil
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
root, name = Path(sys.argv[1]).resolve(), sys.argv[2]

for d in ("script", "brand", "build/scenes", "build/templates", "build/out", "final", "tools"):
    (root / d).mkdir(parents=True, exist_ok=True)


def put(src, dst):
    if dst.exists():
        print(f"kept   {dst.relative_to(root)}")
    else:
        shutil.copyfile(src, dst)
        print(f"added  {dst.relative_to(root)}")


A = SKILL / "assets"
for f in ("engine.js", "kit.css", "kit.js", "player.html"):
    put(A / f, root / "build" / "scenes" / f)
for f in ("page_template.html", "preview_all_template.html", "single_video_template.html"):
    put(A / f, root / "build" / "templates" / f)
put(A / "AGENT-BRIEF.md", root / "build" / "AGENT-BRIEF.md")
put(A / "script_template.md", root / "script" / "script.md")
cfg = root / "video.json"
if not cfg.exists():
    cfg.write_text(json.dumps({"name": name, "voice": "af_heart", "speed": 0.96, "say": {}, "music_bpm": 112,
                               "kokoro_dir": "tools/kokoro", "delivery": "both", "chapter_labels": True}, indent=2) + "\n", encoding="utf-8")
    print("added  video.json")
print(f"\nWorkspace ready: {root}\nNext: put the product's fonts, CSS and logo in brand/ (SKILL.md, step 3),"
      " write script/script.md, then run narrate.py.")
