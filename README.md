# Brag Longer

A customized AI-agent skill for creating long-form narrated product films from
real product screens, with chapter-based rendering, captions, music and versioned
preview pages. Assembled and customized by **Mohit Garg (ScaleQor)**, inspired by
**Shunit Haviv Hakimi's [/brag and /brag-slim](https://github.com/latent-spaces/brag)**.
See [credits](CREDITS.md) and the preserved [original notice](NOTICE.md).

## What it does

- Researches the product and writes a script for review.
- Generates local Kokoro narration and timing data.
- Rebuilds product scenes in a browser and renders chapter MP4s.
- Mixes narration, generated music and captions into versioned films.
- Builds chapter previews and full-film playback/download pages.

This is an agent workflow plus rendering helpers. It does not automatically turn
a URL into a finished film: the agent must author and review scripts, brand assets
and chapter scenes. Private Artifact publishing depends on the agent host; these
scripts build local files and do not supply a hosting service. Longer films require
more render time, disk space and delivery planning.

## Install the skill

For Codex on Windows (PowerShell):

```powershell
git clone https://github.com/mohitgargcanada-max/brag-longer.git "$env:USERPROFILE\.codex\skills\brag-longer"
```

For Claude Code, clone into `~/.claude/skills/brag-longer`. For another compatible
host, use its documented skills directory. `SKILL.md` is at the repository root.
Reload the host if necessary. Multi-agent chapter building and publishing tools
depend on host capabilities.

## Use with an agent

> Use brag-longer to create a three-minute narrated demo of this product from its
> actual screens. Show me the script and voice samples for approval. Deliver both
> the full MP4 and chapter previews, with fictional customer data.

For a revision:

> Use brag-longer to make a shorter v2 from the existing workspace. Preserve v1,
> reuse unchanged chapters, and create updated preview and download pages.

Read [SKILL.md](SKILL.md) before starting. For short launch clips, the skill points
to the separate upstream `/brag` project.

## Dependencies

Python 3.11+ is needed for the documented `python -P` invocation; Node.js 18+ is
the minimum indicated by the supplied diagnostic. Use currently supported releases.
Run the read-only diagnostic first:

```text
python -P scripts/doctor.py
```

It checks package presence, not a complete successful render. After reviewing the
downloads, install into your chosen environment:

```text
python -m pip install numpy scipy imageio-ffmpeg kokoro-onnx
```

The video workspace needs `playwright-core` resolvable from that workspace and a
Chromium headless shell. From the workspace:

```text
npm install playwright-core
npx playwright install chromium-headless-shell
```

The second command can download the Playwright CLI and browser. An existing browser
can instead be selected with `CHROME_PATH`; an existing package with `PLAYWRIGHT_CORE`.
Download `kokoro-v1.0.onnx` (~325 MB) and `voices-v1.0.bin` (~28 MB) separately from
the [kokoro-onnx model release](https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0)
into `<workspace>/tools/kokoro/`, or set `kokoro_dir` in `video.json`.
Models, browsers, dependencies and generated films are not bundled.

## Manual workflow

From this repository, scaffold a workspace:

```text
python -P scripts/scaffold.py video-workspace Product-Demo
python -P scripts/doctor.py video-workspace
```

Then author `script/script.md`, configure `video.json`, provide `brand/brand.css`,
fonts and logo, and customize `build/scenes/kit.js`. Generate narration, then build
`chNN.js` scenes against its timeline using
[scene-authoring.md](references/scene-authoring.md). These authoring steps are
required before the render commands below can work.

```text
python -P scripts/narrate.py video-workspace
node scripts/render.mjs video-workspace stills 1
node scripts/render.mjs video-workspace video
python -P scripts/mix.py video-workspace v1
python -P scripts/pages.py video-workspace clips v1
```

Review the stills before rendering the film. Check the encoded narration, frames,
timing and captions before delivery. Use a new label (`v2`, `v3`, ...) for revisions.
See [delivery.md](references/delivery.md) for full-film pages, download parts and
the all-versions page. Scaffold is a starting point, not a finished demo.

## Repository structure

```text
SKILL.md                 Agent workflow
assets/                  Scene engine, styling, page and script templates
scripts/                 Setup, narration, rendering, mixing and delivery helpers
references/              Scene authoring, content rules and delivery guidance
README.md                Installation and usage
NOTICE.md                Attribution from the supplied archive
CREDITS.md               Source credits and provenance limitations
MODIFICATIONS.md         Publication and modification scope
LICENSE-STATUS.md        Licensing limitations
```

## Attribution and license status

The original approach belongs to Shunit Haviv Hakimi's `/brag` project (MIT upstream).
The supplied notice describes Brag Longer as inspired by it, with no upstream code
or assets included; this publication does not independently certify that comparison.
Do not assume upstream's MIT license licenses this customized repository.
See [CREDITS.md](CREDITS.md) and [LICENSE-STATUS.md](LICENSE-STATUS.md).
