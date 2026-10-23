"""Shared paths and settings for a brag-longer video workspace.

A workspace is one folder (for example <project>/demo-video) holding video.json, script/, brand/, build/, final/ and the
preview folders. Every script takes the workspace path as its first argument.
"""
import json
from pathlib import Path

DEFAULTS = {
    "name": "Demo",                 # output files are <name>-<version>.mp4
    "voice": "af_heart",            # Kokoro voice id
    "speed": 0.96,
    "gaps": {"sentence": 0.35, "paragraph": 1.0, "lead_in": 0.8, "tail": 1.1, "end_hold": 4.0},
    "say": {},                      # spoken respellings, e.g. {"ScaleQor": "Scale-core"}; captions keep the real spelling
    "fps": 30,
    "music_bpm": 112,               # original ambient bed made in code; 75 is calm, 112 upbeat
    "kokoro_dir": "tools/kokoro",   # holds kokoro-v1.0.onnx and voices-v1.0.bin (absolute, or relative to the workspace)
    "delivery": "both",             # "both": chapter preview + the one complete file; "single": the complete file only;
                                    # "chapters": the chapter preview only. The film is always built in chapters.
    "chapter_labels": True,         # the small "01 Title" label on brand scenes; false for a seamless film
}


class Workspace:
    def __init__(self, root):
        self.root = Path(root).resolve()
        cfg_file = self.root / "video.json"
        if not cfg_file.exists():
            raise SystemExit(f"{cfg_file} not found; run scaffold.py first")
        cfg = json.loads(cfg_file.read_text(encoding="utf-8"))
        self.cfg = {**DEFAULTS, **cfg, "gaps": {**DEFAULTS["gaps"], **cfg.get("gaps", {})}}
        self.script = self.root / "script" / "script.md"
        self.build = self.root / "build"
        self.scenes = self.build / "scenes"
        self.templates = self.build / "templates"
        self.out = self.build / "out"
        self.final = self.root / "final"
        kd = Path(self.cfg["kokoro_dir"])
        self.kokoro = kd if kd.is_absolute() else self.root / kd

    def timeline(self, version=None):
        name = f"timeline-{version}.json" if version else "timeline.json"
        return json.loads((self.out / name).read_text(encoding="utf-8"))

    def stem(self, version):
        return f"{self.cfg['name']}-{version}"


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def frames(duration, fps):
    """A chapter's length in whole frames; video and audio are both cut to this so they cannot drift."""
    return round(duration * fps)
