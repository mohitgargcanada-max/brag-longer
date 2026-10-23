"""Voice the script one sentence at a time and lay out each chapter's timeline.

python -P narrate.py <workspace>     writes build/out/voice/chNN/*.wav, build/out/voice/chNN.wav, build/out/timeline.json

Each sentence wav is a checkpoint, named by a hash of its spoken text and voice settings: a restart, or a re-run after
editing one line, voices only what changed. Progress with an ETA goes to build/out/voice/progress.txt.

Script format (script/script.md): a title line and intro, then `---`, then chapters headed `## N. Title (about m:ss)`.
Plain paragraphs are spoken; paragraphs starting `Screen:` (visual direction) or `<!--` (source notes) are not.
"""
import hashlib
import json
import re
import sys
from pathlib import Path
import time
import wave

import numpy as np
from kokoro_onnx import Kokoro

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -P drops the script folder; common.py lives here
from common import Workspace

RATE = 24000


def parse(script):
    chapters = []
    for block in re.split(r"\n\s*\n", script.split("---", 1)[1]):
        b = " ".join(block.split())
        if not b:
            continue
        if b.startswith("## "):
            num, title = re.match(r"## (\d+)\. (.+?) \(about", b).groups()
            chapters.append({"n": int(num), "title": title, "paragraphs": []})
        elif not b.startswith(("Screen:", "<!--")):
            chapters[-1]["paragraphs"].append(re.split(r"(?<=[.?!])\s+(?=[A-Z\"'])", b))
    return chapters


def read_wav(path):
    with wave.open(str(path)) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype="<i2")


def write_wav(path, pcm):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1), w.setsampwidth(2), w.setframerate(RATE)
        w.writeframes(pcm.astype("<i2").tobytes())


def main():
    ws = Workspace(sys.argv[1])
    voice, speed, gaps, say = ws.cfg["voice"], ws.cfg["speed"], ws.cfg["gaps"], ws.cfg["say"]
    def spoken(text):  # the spoken form; captions and the timeline keep the real spelling
        for k, v in say.items():
            text = text.replace(k, v)
        return text

    chapters = parse(ws.script.read_text(encoding="utf-8"))
    out = ws.out / "voice"
    total = sum(len(p) for c in chapters for p in c["paragraphs"])
    kokoro, done, started, timeline = None, 0, time.time(), []
    for ch in chapters:
        folder = out / f"ch{ch['n']:02d}"
        folder.mkdir(parents=True, exist_ok=True)
        pieces, cursor, sentences, idx = [np.zeros(int(gaps["lead_in"] * RATE), "<i2")], gaps["lead_in"], [], 0
        for p, para in enumerate(ch["paragraphs"]):
            for s, text in enumerate(para):
                key = hashlib.sha1(f"{voice}|{speed}|{spoken(text)}".encode()).hexdigest()[:10]
                wav = folder / f"s{idx:03d}-{key}.wav"
                if not wav.exists():
                    kokoro = kokoro or Kokoro(str(ws.kokoro / "kokoro-v1.0.onnx"), str(ws.kokoro / "voices-v1.0.bin"))
                    audio, rate = kokoro.create(spoken(text), voice=voice, speed=speed, lang="en-us")
                    assert rate == RATE, rate
                    write_wav(wav, np.clip(audio, -1, 1) * 32767)
                pcm = read_wav(wav)
                dur = len(pcm) / RATE
                sentences.append({"i": idx, "p": p, "text": text, "start": round(cursor, 3), "end": round(cursor + dur, 3)})
                pieces.append(pcm)
                cursor += dur
                last_s = s == len(para) - 1
                last_p = p == len(ch["paragraphs"]) - 1
                gap = ((gaps["end_hold"] if ch is chapters[-1] else gaps["tail"]) if last_s and last_p
                       else gaps["paragraph"] if last_s else gaps["sentence"])
                pieces.append(np.zeros(int(gap * RATE), "<i2"))
                cursor += gap
                idx += 1
                done += 1
                (out / "progress.txt").write_text(f"{done}/{total} sentences, ETA {(time.time() - started) / done * (total - done):.0f}s\n")
        write_wav(out / f"ch{ch['n']:02d}.wav", np.concatenate(pieces))
        timeline.append({"n": ch["n"], "title": ch["title"], "duration": round(cursor, 3), "sentences": sentences})
        print(f"ch{ch['n']:02d} {ch['title']}: {cursor:.1f}s, {len(sentences)} sentences", flush=True)
    (ws.out / "timeline.json").write_text(json.dumps(timeline, indent=1), encoding="utf-8")
    words = sum(len(s["text"].split()) for c in timeline for s in c["sentences"])
    print(f"total {sum(c['duration'] for c in timeline) / 60:.2f} min, {words} spoken words")


if __name__ == "__main__":
    main()
