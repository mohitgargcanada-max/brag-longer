"""Pad chapter tails to a three-minute film; narration stays at its recorded speed."""
from pathlib import Path
import json
import wave
import sys

root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent
path = root / 'build/out/timeline.json'
timeline = json.loads(path.read_text(encoding='utf-8'))
fps = 24
total = sum(c['duration'] for c in timeline)
assert total <= 180, f'Narration is already {total}s; edit the script instead of speeding speech.'
if abs(total - 180) > 0.001:
    extra = (180 - total) / len(timeline)
    used = 0
    for i, c in enumerate(timeline):
        frames = round((c['duration'] + extra) * fps) if i < len(timeline)-1 else 180*fps-used
        duration = frames / fps
        file = root / f'build/out/voice/ch{c["n"]:02d}.wav'
        with wave.open(str(file), 'rb') as w:
            params = w.getparams()
            pcm = w.readframes(w.getnframes())
        target = round(duration * params.framerate)
        assert target * params.sampwidth >= len(pcm)
        with wave.open(str(file), 'wb') as w:
            w.setparams(params)
            w.writeframes(pcm + b'\0' * (target * params.sampwidth - len(pcm)))
        c['duration'] = duration
        used += frames
    path.write_text(json.dumps(timeline, indent=1) + '\n', encoding='utf-8')
assert round(sum(c['duration'] for c in timeline) * fps) == 180 * fps
print(f'Film: 180 seconds, {fps} fps; only silence added at chapter tails.')
