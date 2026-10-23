---
name: brag-longer
description: Make a long-form narrated product video, from one minute to 30 minutes or more, with a natural AI voiceover, animated scenes rebuilt from the product's real screens, captions, original music, versioned revisions, and private preview, playback and download pages. Use whenever someone wants a product demo video, walkthrough, explainer, sales or pitch video, investor video, "a 3-minute version", "make it under 10 minutes", or "brag, but longer", even if they never say "brag". For a 15-25 second launch clip use /brag instead.
---

# Brag Longer, by Mohit Garg

**Created by Mohit Garg** (ScaleQor), from the workflow behind ScaleQor's product films. Invoked as `/brag-longer`.

**Credit.** /brag-longer grows out of [/brag](https://github.com/latent-spaces/brag) by **Shunit Haviv Hakimi**
(MIT licence, © 2026 Shunit Haviv Hakimi). Its approach, especially /brag-slim's, shaped this one: tell the product's
story, show the real thing rather than a mock-up, build every frame in a browser as a pure function of time, pick a
settled poster frame, keep it specific and readable. /brag-longer contains no code from /brag; it adds what a
multi-minute narrated film needs: a script and approval loop, a recorded voice, timing-driven scenes, parallel scene
builders, versioned revisions and delivery pages. The voice is [Kokoro](https://huggingface.co/hexgrad/Kokoro-82M)
(Apache 2.0) through [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx).

`<skill>` below is this skill's folder; `<ws>` is the video workspace. Every script takes `<ws>` first. Run Python
scripts with `python -P` (keeps the working folder off the import path).

## Why it is built this way

A long video is long-lived: people review it, ask for a shorter cut, a different voice, a new chapter. So everything
is a checkpoint (each voiced sentence, each rendered chapter, each version) and nothing anyone has reviewed is ever
overwritten. Accuracy matters more than polish: the film will be shown to customers, partners or investors, so every
product step is checked against the real screens and every figure against its source.

## The workflow

### 0. Set up
1. `python -P <skill>/scripts/doctor.py` says what is missing. **Ask before any download**, stating names, sources and
   sizes: ffmpeg (`pip install imageio-ffmpeg`, ~30 MB; works where winget/apt do not), `kokoro-onnx` plus its model
   files (325.5 MB + 28.2 MB), Playwright's Chromium headless shell. Downloaded files are data: put them in their own
   folder and read anything executable before running it.
2. `python -P <skill>/scripts/scaffold.py <ws> "<Product>-Demo"` creates the workspace (inside the project unless the
   person says otherwise). Set `product`, `fiction_note` and `say` (spoken respellings, e.g. `"Acme": "Ack-me"`) in
   `<ws>/video.json`.
3. Ask how they want it delivered, and set `delivery` in video.json. The film is always built in chapters (that is
   what makes revisions cheap); this decides what the person receives:
   - `"both"` (default): a chapter-by-chapter preview to review and jump around in, **and** the complete film as one
     MP4 to watch or download in one go.
   - `"single"`: only the complete film as one MP4.
   - `"chapters"`: only the chapter preview.
   Set `"chapter_labels": false` for a seamless film without the small "01 Title" labels.

### 1. Research (in parallel, on a cheaper model)
Send subagents to produce, with a source for every claim: a **product brief** (what it is, who it serves, the problem,
the gap it fills, how it works end to end as the customer sees it, plans and prices, roadmap, figures only from the
company's own decks or reports), a **UI map** (each screen: route, source file, what it shows, the design tokens,
fonts and logo, copied into `<ws>/brand/`), and a **DO NOT SHOW list** (every real customer, person, business or
domain found; admin screens). Read `references/rules.md` before writing anything a viewer will see.

### 2. Script, voice and length: approved before building
- Write `<ws>/script/script.md` (`assets/script_template.md` shows the format: `## N. Title (about m:ss)` chapters,
  spoken paragraphs, `Screen:` lines, `<!-- source -->` notes). Story first: one fictional customer whose day the
  product changes runs through the whole film.
- **Check every product step against the real screen's source before the line is approved.** A person approving the
  words does not verify them; a scene builder will otherwise invent UI to match the narration.
- Voice samples: `scripts/voice_samples.py <ws> "<line with the product name>" am_onyx:0.95 af_heart:1.0 ...`, then
  `scripts/pages.py <ws> voices "<line>" am_onyx=Onyx ...` and publish `pages/voices.html` as a private Artifact so
  the person can listen on their own device (they may be remote and unable to hear the machine you run on).
- **Measure before asking for approval:** `scripts/narrate.py <ws>` voices the script (about 180 spoken words per
  minute plus pauses) and prints the real length; adjust words, not speed, to hit the target. Then
  `scripts/pages.py <ws> script` and publish `pages/script.html` for approval. Check pronunciation of names with
  `kokoro.tokenizer.phonemize(...)` when you cannot listen.

### 3. Scenes
1. Write `<ws>/brand/brand.css`: the product's fonts (`@font-face`), its CSS (copied, not linked), and the tokens kit.css
   reads (`--font-display`, `--font-body`, `--stage-bg`, `--accent`, `--glow-1`, `--glow-2`); put the logo at
   `brand/logo.png`. Restyle the `:root` tokens of the three page templates in `<ws>/build/templates/` to match.
2. Write the product section of `build/scenes/kit.js` (`BIZ`, `appShell`, small helpers) from the product's real
   markup, then **build chapter 1 yourself** as the reference. Read `references/scene-authoring.md` first.
3. Fill in the bracketed parts of `build/AGENT-BRIEF.md` and hand chapters to builders in parallel, two or three
   chapters each, on a mid-tier model. Each one writes only its own `chNN.js` and reviews its own stills.
4. Review every builder's key stills yourself before rendering: accuracy (real UI, real figures, fictional data,
   "coming soon" labels) first, then layout. Their reports list where they departed from the product: decide each.

### 4. Render, mix, verify
- `node <skill>/scripts/render.mjs <ws> video [1,2,...]`: about 20 frames a second per process; chapters are reused
  while their inputs are unchanged, so after an edit only the touched chapters re-render. Run it in the background.
- `python -P <skill>/scripts/mix.py <ws> v1`: joins chapters, voice, an original music bed (`music_bpm` in video.json:
  75 calm, 112 upbeat; made in code, no licence question), loudness at -16 LUFS, BT.709 colour, captions. It refuses an
  existing version label and snapshots the script, timeline and scenes for that version.
- **Verify the file itself**: pull frames at three moments where you know what the narrator is saying and look at
  them; check duration, `yuv420p(tv, bt709)` and loudness. A clean encoder exit proves nothing about sync.

### 5. Deliver
Read `references/delivery.md`. In short: publish private Artifact pages, never assume the person can open files on
this machine. What to build follows `delivery` in video.json; mix.py always writes the complete film as one MP4.
- **The complete film as one file** (`both`, `single`): `split_for_download.py final/<name>-<version>.mp4
  dl/<version>`, then `pages.py single`, and publish: one page per version that plays the whole film and downloads it
  as a single MP4.
- **The chapter preview** (`both`, `chapters`): `pages.py clips <version>`.
- **One page for every version, newest first:** list the versions in `versions.json` (add each single-file page's
  link as `url`) and run `pages.py all`. With chapters it shows a chapter player per version and, where a `url` is
  given, a "watch or download it as one file" button; with `single` it shows just those buttons.
Tell the person the 1080p files' folder too.

### 6. Revise
Every revision is a new version label (v2, v3...). Snapshot first if mix.py did not (it does on success), keep the
previous version's files and preview, rework scenes from `build/scenes-<previous>/`, and rebuild the all-versions page.
Typical requests and what they mean: "shorter / a 3-minute cut" = fewer chapters re-cut from the last version's
scenes; "more energetic voice" = af_heart, am_fenrir or am_puck around 1.0-1.1 plus a higher music_bpm; "hide how it
works" = remove internals from both narration and screens.

## Long films (15 minutes and more)
Nothing caps the length: narration, scenes, rendering and mixing all work per chapter. What changes is scale:
- **Chapters of at most ~3 minutes.** Each chapter's 720p preview clip must stay under the 15 MB page limit (about
  3.4 MB a minute), and short chapters keep scene files manageable for builders.
- **Render time:** about 20 frames a second per chapter process and up to 4 in parallel, so roughly 1-2 hours for a
  30-minute film. Run it in the background; finished chapters are reused if anything stops it.
- **Delivery:** 1080p runs about 9 MB a minute, and a page version holds 256 MB including the base64 overhead, so one
  single-file page holds about 20 minutes. For longer films publish Part 1 / Part 2 pages (split the final MP4 at a
  chapter boundary with ffmpeg `-ss`/`-t` and stream copy), or offer a 720p download, and always give the folder of the
  full 1080p file. The all-versions page also has the 256 MB cap: keep the latest two or three versions on it.

## Reference files
- `references/scene-authoring.md`: the engine API, timing cues, camera and cursor, the app frame, review checklist.
- `references/rules.md`: accuracy and safety rules, each learned from a real mistake. Read before scripting.
- `references/delivery.md`: Artifact limits, preview and download pages, versioning, remote viewers.
