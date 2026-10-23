"""Split a finished MP4 into base64 text chunks under the page's 15 MB per-file limit, for the page to rejoin.

Artifacts serve only web file types, so the chunks are .txt (base64); the page decodes and rejoins them and checks the
SHA-256 against the original before playing or saving.

python -P split_for_download.py <mp4> <out dir>    prints the chunk list as JSON and proves the chunks rejoin exactly
"""
import base64
import hashlib
import json
import sys
from pathlib import Path

CHUNK = 10_000_000  # raw bytes per chunk; 13.3 MB once base64-encoded
src, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
for old in out.glob(f"{src.stem}.part*"):
    old.unlink()
data = src.read_bytes()
parts = []
for i in range(0, len(data), CHUNK):
    name = f"{src.stem}.part{i // CHUNK + 1:02d}.txt"
    (out / name).write_bytes(base64.b64encode(data[i:i + CHUNK]))
    parts.append(name)
rejoined = b"".join(base64.b64decode((out / p).read_bytes()) for p in parts)
assert hashlib.sha256(rejoined).digest() == hashlib.sha256(data).digest(), "chunks do not rejoin to the original"
assert max((out / p).stat().st_size for p in parts) < 15_000_000, "a chunk is over the page's per-file limit"
print(json.dumps({"file": src.name, "bytes": len(data), "parts": parts}))
