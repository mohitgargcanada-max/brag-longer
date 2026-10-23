"""Check what brag-longer needs, and say how to get what is missing. Installs nothing.

python -P doctor.py [<workspace>]
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ok = True


def check(label, good, fix):
    global ok
    print(f"{'ok     ' if good else 'MISSING'} {label}" + ("" if good else f"\n        -> {fix}"))
    ok &= bool(good)


check("python packages numpy, scipy", all(importlib.util.find_spec(m) for m in ("numpy", "scipy")),
      "python -m pip install --user numpy scipy")
check("ffmpeg with libx264 + libass (imageio-ffmpeg)", importlib.util.find_spec("imageio_ffmpeg"),
      "python -m pip install --user imageio-ffmpeg   (~30 MB from PyPI; works where winget/apt are unavailable)")
check("Kokoro voice engine (kokoro-onnx)", importlib.util.find_spec("kokoro_onnx"),
      "python -m pip install --user kokoro-onnx   (small packages from PyPI)")
check("node", shutil.which("node"), "install Node.js 18+")
pw = subprocess.run(["node", "-e", "require.resolve('playwright-core')"], capture_output=True, cwd=sys.argv[1] if len(sys.argv) > 1 else None)
check("playwright-core (resolvable from the workspace, or PLAYWRIGHT_CORE set)",
      pw.returncode == 0 or os.environ.get("PLAYWRIGHT_CORE"),
      "npm install playwright-core in the workspace, or set PLAYWRIGHT_CORE to an existing node_modules/playwright-core")
bases = [os.environ.get("PLAYWRIGHT_BROWSERS_PATH"), os.environ.get("LOCALAPPDATA") and Path(os.environ["LOCALAPPDATA"]) / "ms-playwright",
         Path.home() / "Library/Caches/ms-playwright", Path.home() / ".cache/ms-playwright"]
shell = os.environ.get("CHROME_PATH") or any(Path(b).exists() and any(Path(b).glob("chromium_headless_shell-*")) for b in bases if b)
check("Chromium headless shell", shell, "npx playwright install chromium-headless-shell   (or set CHROME_PATH)")
if len(sys.argv) > 1:
    root = Path(sys.argv[1])
    cfg = json.loads((root / "video.json").read_text(encoding="utf-8")) if (root / "video.json").exists() else {}
    kd = Path(cfg.get("kokoro_dir", "tools/kokoro"))
    kd = kd if kd.is_absolute() else root / kd
    check(f"Kokoro model files in {kd}", (kd / "kokoro-v1.0.onnx").exists() and (kd / "voices-v1.0.bin").exists(),
          "download kokoro-v1.0.onnx (325 MB) and voices-v1.0.bin (28 MB) from "
          "https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0 - ask the person first, stating names and sizes")
    check("brand/brand.css", (root / "brand" / "brand.css").exists(), "write brand/brand.css (see SKILL.md, step 3)")
print("\nAll set." if ok else "\nFix the MISSING items; ask the person before any download.")
