"""Assemble a finished version: chapter videos + voice + an original music bed + captions.

python -P mix.py <workspace> <version>      e.g.  mix.py C:/proj/demo-video v2

Needs every chapter rendered for the current timeline (render.mjs video writes build/out/video/manifest.json). Writes
final/<name>-<version>.mp4, -captioned.mp4 and .srt, and refuses to overwrite a version that already exists: people
review these files, so a rebuild always gets a new version label. After a successful mix it snapshots what produced the
version (script/script-<version>.md, build/out/timeline-<version>.json, build/scenes-<version>/) so it can be rebuilt.
"""
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
import wave

import numpy as np
from scipy.signal import fftconvolve

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -P drops the script folder; common.py lives here
from common import Workspace, ffmpeg as ffmpeg_exe

SR = 48000
COLOUR = ["-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709"]


def run(*args):
    subprocess.run([ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error", *map(str, args)], check=True)


def chapter_videos(ws, timeline):
    manifest_file = ws.out / "video" / "manifest.json"
    if not manifest_file.exists():
        raise SystemExit("no render manifest: run `node render.mjs <workspace> video` first")
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    if manifest["timeline"] != hashlib.sha1((ws.out / "timeline.json").read_bytes()).hexdigest():
        raise SystemExit("the renders are for an older timeline: run `node render.mjs <workspace> video` again")
    vids = []
    for c in timeline:
        name = manifest["chapters"].get(str(c["n"]))
        if not name or not (ws.out / "video" / name).exists():
            raise SystemExit(f"chapter {c['n']} has no render for the current timeline")
        vids.append(ws.out / "video" / name)
    return vids


def voice_track(ws, timeline, fps):
    """Concatenate chapter voice wavs, each padded or trimmed to its video's exact frame length, at 48 kHz."""
    parts = []
    for c in timeline:
        with wave.open(str(ws.out / "voice" / f"ch{c['n']:02d}.wav")) as w:
            pcm = np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(np.float32) / 32768
            rate = w.getframerate()
        x = np.interp(np.arange(0, len(pcm) * SR / rate) * rate / SR, np.arange(len(pcm)), pcm)
        n = round(round(c["duration"] * fps) / fps * SR)
        parts.append(np.pad(x, (0, max(0, n - len(x))))[:n])
    return np.concatenate(parts)


def music_bed(seconds, bpm):
    """Original ambient bed in D major (pads, soft bass, a quiet arpeggio, a soft kick and hat) through a synthetic
    reverb. Made in code so there is never a licence question."""
    n = int(seconds * SR)
    t = np.arange(n) / SR
    note = lambda name: 440 * 2 ** ((("C C# D D# E F F# G G# A A# B".split().index(name[:-1])) + 12 * (int(name[-1]) + 1) - 69) / 12)
    chords = [["D3", "A3", "C#4", "E4", "F#4"], ["B2", "F#3", "A3", "C#4", "D4"],
              ["G2", "D3", "F#3", "A3", "B3"], ["A2", "E3", "B3", "C#4", "E4"]]
    beat = 60 / bpm
    bar = 8 * beat  # two bars of 4/4
    left, right = np.zeros(n), np.zeros(n)
    for k in range(int(seconds / bar) + 2):
        start = k * bar - 1.2
        chord = chords[k % 4]
        a, b = max(0, int(start * SR)), min(n, int((start + bar + 2.4) * SR))
        if a >= b:
            continue
        tt = t[a:b] - start
        env = np.sin(np.pi * np.clip(tt / (bar + 2.4), 0, 1)) ** 1.5  # long swell, overlaps neighbours
        for i, name in enumerate(chord):
            f = note(name)
            for det, pan in ((-0.6, 0.8), (0.6, 0.2), (0.0, 0.5)):
                tone = np.sin(2 * np.pi * (f + det) * tt + i) + 0.18 * np.sin(4 * np.pi * (f + det) * tt)
                left[a:b] += env * tone * pan * 0.05
                right[a:b] += env * tone * (1 - pan) * 0.05
        bass = env * np.sin(2 * np.pi * note(chord[0]) / 2 * tt) * 0.12
        left[a:b] += bass
        right[a:b] += bass
        for step in range(16):  # arpeggio: eighth notes an octave up, quiet bell tones
            s0 = start + 1.2 + step * beat / 2
            i0 = int(s0 * SR)
            if i0 < 0 or i0 >= n:
                continue
            i1 = min(n, i0 + int(1.6 * SR))
            ta = t[i0:i1] - s0
            f = note(chord[[1, 3, 2, 4, 3, 2, 4, 1][step % 8]]) * 2
            bell = np.exp(-ta / 0.35) * (np.sin(2 * np.pi * f * ta) + 0.25 * np.sin(6 * np.pi * f * ta)) * 0.03
            pan = 0.3 + 0.4 * ((step * 3) % 5) / 4
            left[i0:i1] += bell * pan
            right[i0:i1] += bell * (1 - pan)
    rng = np.random.default_rng(7)
    if bpm >= 100:  # pulse for upbeat beds: a soft kick on every beat and a quiet hi-hat on the off-beats
        kt = np.arange(int(0.25 * SR)) / SR
        kick = np.sin(2 * np.pi * (50 * kt + 70 * 0.06 * (1 - np.exp(-kt / 0.06)))) * np.exp(-kt / 0.11) * 0.22
        ht = np.arange(int(0.06 * SR)) / SR
        hat = np.diff(rng.standard_normal(len(ht) + 1)) * np.exp(-ht / 0.015) * 0.018
        for k in range(int(bar / 2 / beat), int(seconds / beat)):
            i = int(k * beat * SR)
            left[i:i + len(kick)] += kick[: n - i]
            right[i:i + len(kick)] += kick[: n - i]
            j = int((k + 0.5) * beat * SR)
            if j < n:
                left[j:j + len(hat)] += hat[: n - j] * 0.8
                right[j:j + len(hat)] += hat[: n - j]
    ir_t = np.arange(int(2.4 * SR)) / SR
    irs = [rng.standard_normal(len(ir_t)) * np.exp(-ir_t / 0.55) for _ in range(2)]
    wet = [fftconvolve(ch, ir)[:n] for ch, ir in zip((left, right), irs)]
    mix = np.stack([left + 0.03 * wet[0], right + 0.03 * wet[1]], axis=1)
    return mix / np.abs(mix).max() * 0.9


def music_gain(timeline, n, fps):
    """Music sits ~20 dB under the voice while someone speaks and rises ~8 dB in the pauses."""
    speech = np.zeros(n, bool)
    offset = 0.0
    for c in timeline:
        for s in c["sentences"]:
            speech[int((offset + s["start"] - 0.25) * SR):int((offset + s["end"] + 0.15) * SR)] = True
        offset += round(c["duration"] * fps) / fps
    target = np.where(speech, 10 ** (-27 / 20), 10 ** (-19 / 20))
    k = int(0.6 * SR)  # smooth over ~0.6 s so the music breathes rather than pumps
    g = fftconvolve(target, np.hanning(k) / np.hanning(k).sum(), mode="same")
    fade = np.minimum(1, np.arange(n) / (2 * SR)) * np.minimum(1, (n - np.arange(n)) / (4 * SR))
    return g * fade


def write_wav(path, stereo):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2), w.setsampwidth(2), w.setframerate(SR)
        w.writeframes((np.clip(stereo, -1, 1) * 32767).astype("<i2").tobytes())


def read_stereo(path):
    with wave.open(str(path)) as w:
        return np.frombuffer(w.readframes(w.getnframes()), "<i2").reshape(-1, 2).astype(np.float32) / 32768


def srt_time(s):
    ms = round(s * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def captions(timeline, fps):
    """One caption per sentence, split at commas/colons into chunks of at most ~84 characters, timed by length."""
    cues, offset = [], 0.0
    for c in timeline:
        for s in c["sentences"]:
            chunks, cur = [], ""
            for part in re.split(r"(?<=[,:;])\s+", s["text"]):
                if cur and len(cur) + len(part) > 84:
                    chunks.append(cur)
                    cur = part
                else:
                    cur = f"{cur} {part}".strip()
            chunks.append(cur)
            total, t = sum(len(x) for x in chunks), offset + s["start"]
            for x in chunks:
                d = (s["end"] - s["start"]) * len(x) / total
                cues.append((t, t + d, x))
                t += d
        offset += round(c["duration"] * fps) / fps
    return "\n".join(f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{x}\n" for i, (a, b, x) in enumerate(cues, 1))


def main():
    ws, version = Workspace(sys.argv[1]), sys.argv[2]
    fps, bpm, stem = ws.cfg["fps"], ws.cfg["music_bpm"], ws.stem(version)
    if any(ws.final.glob(stem + ".*")) or any(ws.final.glob(stem + "-*")):
        raise SystemExit(f"{stem} already exists in {ws.final}; pick a new version label")
    timeline = ws.timeline()
    ws.final.mkdir(exist_ok=True)
    audio = ws.out / "audio"
    audio.mkdir(exist_ok=True)

    vids = chapter_videos(ws, timeline)
    (audio / "concat.txt").write_text("".join(f"file '{v.as_posix()}'\n" for v in vids), encoding="utf-8")
    run("-f", "concat", "-safe", "0", "-i", audio / "concat.txt", "-c", "copy", audio / "video.mp4")

    voice = voice_track(ws, timeline, fps)
    voice *= 10 ** (-20 / 20) / np.sqrt(np.mean(voice[np.abs(voice) > 0.01] ** 2))  # speech at about -20 dBFS RMS
    seconds = int(len(voice) / SR) + 2
    music_file = audio / f"music-{bpm}bpm-{seconds}s.wav"
    if not music_file.exists():
        write_wav(music_file, music_bed(seconds, bpm))
    music = read_stereo(music_file)[: len(voice)]
    mix = music * music_gain(timeline, len(voice), fps)[:, None] + voice[:, None]
    mix /= max(1.0, np.abs(mix).max() / 0.97)
    write_wav(audio / "mix.wav", mix)

    srt = ws.final / f"{stem}.srt"
    srt.write_text(captions(timeline, fps), encoding="utf-8")
    out = ws.final / f"{stem}.mp4"
    # Chapters arrive as full-range BT.601 (decoded from JPEG frames); convert to the limited-range BT.709 that
    # PowerPoint, TVs and browsers expect, and tag it so no player has to guess.
    run("-i", audio / "video.mp4", "-i", audio / "mix.wav", "-map", "0:v", "-map", "1:a",
        "-vf", "scale=in_range=pc:out_range=tv:in_color_matrix=bt601:out_color_matrix=bt709,format=yuv420p",
        *COLOUR, "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", SR, "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
        "-shortest", out)
    style = ("FontName=Lato,FontSize=15,PrimaryColour=&H00FFFFFF,BackColour=&H99120F24,BorderStyle=4,"
             "Outline=0,Shadow=0,MarginV=22,Alignment=2")
    srt_arg = str(srt).replace("\\", "/").replace(":", "\\:")  # ffmpeg filter-syntax escaping
    run("-i", out, "-vf", f"subtitles='{srt_arg}':force_style='{style}'", "-c:v", "libx264", "-preset", "medium",
        "-crf", "18", "-pix_fmt", "yuv420p", *COLOUR, "-c:a", "copy", "-movflags", "+faststart", ws.final / f"{stem}-captioned.mp4")

    # Snapshot what produced this version, so it can be rebuilt after the next revision changes the working copies.
    shutil.copyfile(ws.out / "timeline.json", ws.out / f"timeline-{version}.json")
    shutil.copyfile(ws.script, ws.script.with_name(f"script-{version}.md"))
    shutil.copytree(ws.scenes, ws.build / f"scenes-{version}", dirs_exist_ok=True)
    for f in sorted(ws.final.glob(stem + "*")):
        print(f"{f.name}: {f.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
