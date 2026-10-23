"""Render the same line in several Kokoro voices so the person can pick one by ear.

python -P voice_samples.py <workspace> "<sample line>" am_onyx:0.95 bm_george:0.95 af_heart:1.0 ...
writes <workspace>/samples/sample-<voice>.mp3 (and .wav). Use the product's real name in the line, run through the
video.json "say" respellings, so the pronunciation is checked too.

Kokoro voices worth trying: deep male am_onyx, bm_george, am_michael; energetic am_fenrir, am_puck; most natural and
expressive af_heart, af_bella. Faster speed (1.05-1.1) reads as more energetic.
"""
import subprocess
import sys
from pathlib import Path
import wave

import numpy as np
from kokoro_onnx import Kokoro

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -P drops the script folder; common.py lives here
from common import Workspace, ffmpeg

ws = Workspace(sys.argv[1])
line = sys.argv[2]
for k, v in ws.cfg["say"].items():
    line = line.replace(k, v)
out = ws.root / "samples"
out.mkdir(exist_ok=True)
kokoro = Kokoro(str(ws.kokoro / "kokoro-v1.0.onnx"), str(ws.kokoro / "voices-v1.0.bin"))
for spec in sys.argv[3:]:
    voice, speed = spec.split(":")
    audio, rate = kokoro.create(line, voice=voice, speed=float(speed), lang="en-us")
    wav = out / f"sample-{voice}.wav"
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1), w.setsampwidth(2), w.setframerate(rate)
        w.writeframes((np.clip(audio, -1, 1) * 32767).astype("<i2").tobytes())
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", str(wav), "-b:a", "128k", str(wav.with_suffix(".mp3"))], check=True)
    print(f"{wav.with_suffix('.mp3')}: {len(audio) / rate:.1f}s")
