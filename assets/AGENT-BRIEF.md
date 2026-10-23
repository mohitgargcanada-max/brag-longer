# Brief for building chapter scenes (brag-longer)

You are building the visuals for one or more chapters of a narrated product video. The voiceover is already recorded;
you write the animated scenes that play under it. Replace the bracketed parts of this brief for the project before
handing it to builders.

Product: [one line on what the product is and who the video is for].
Workspace: [absolute path to the video workspace].

## Files (paths relative to the workspace)

- `script/script.md`: the approved script. Each chapter: spoken paragraphs plus `Screen:` lines = what must be on
  screen. Follow the Screen lines; they are the brief for your scenes.
- `build/out/timeline.json`: exact sentence timings. Print your chapters with:
  `python -c "import json;[print(c['n'],c['title'],c['duration'],*[f\"  p{s['p']} s{s['i']} {s['start']:.2f}-{s['end']:.2f} {s['text']}\" for s in c['sentences']],sep='\n') for c in json.load(open('build/out/timeline.json',encoding='utf8')) if c['n'] in (N,)]"`
- `build/scenes/engine.js`: the scene engine and animation helpers (READ IT FULLY): `Demo.chapter`, scene objects
  `{from, to?, demo?, hideLabel?, build(layer, C) -> update(t, T)}`, `C.para(p)`, `C.sent(i)`, `C.sentEnd(i)`,
  `C.word('exact words from a sentence')`, `prog`, `reveal`, `typeText`, `countUp`, `camera`, `makeCursor`, `h`.
- `build/scenes/kit.js` and `kit.css`: shared building blocks and video styles ([list the product helpers, e.g.
  appShell, pill, claimRow]). `brand/brand.css`: the product's fonts, colours and app CSS.
- `build/scenes/ch01.js`: the finished reference chapter. Match its quality, style and structure.
- [Research notes: product brief, UI map with routes and source files, DO NOT SHOW list.]
- [The product's UI source, e.g. `src/components/**`: read only what you need, grep first.]

## What you write

Only `build/scenes/chNN.js` for your chapters. Do not edit engine.js, kit.js, kit.css, player.html, the script or
anything else; other builders work in parallel. Define any helper inside your chapter file with a chapter prefix
(`ch06Row`). If you find an engine bug, work around it and report it.

## Rules

1. **Deterministic.** Every visual is a pure function of time inside `update(t, T)`. No CSS transitions or animations
   (override any the product CSS carries), no setTimeout, no Date, no Math.random.
2. **Synced to the voice.** Bring each element in as the narrator says it: `C.word('exact phrase')`, `C.sent(i)`,
   `C.para(p)`, never hand-typed seconds. Scene boundaries usually sit at paragraph starts. The first scene has
   `from: 0`. The engine dips through the background between scenes and fades the chapter in and out.
3. **Readable.** At 1080p, text at least 22px on brand scenes; anything to be read stays still for ~0.3s per word.
   Nothing overflows, clips or collides. Keep the bottom 140px free of essentials (captions, the demo chip).
   Something should arrive or move every 3-4 seconds.
4. **Product scenes reuse the real app.** Build them from the product's own markup, class names, labels and wording.
   The app frame is 1440x810 scaled to 1080p; push in with `camera()` on what is being talked about; `makeCursor` for
   clicks and typing. Set `demo: true` and `hideLabel: true` on every scene showing the app or the fictional customer.
   Show only what the product really does: if the narration and the real screen disagree, say so in your report
   rather than inventing UI to match.
5. **Fictional data only.** The customer is `BIZ`. Every other business is invented, with a coined name (not a place
   nickname or a common local name a real business could carry, above all where the scene shows it doing badly);
   phone numbers 555-01xx; emails and websites on the reserved `.example` domain. Nothing from the DO NOT SHOW list.
   No competitor vendor names on screen.
6. **Figures only from the script.** No invented numbers, claims or testimonials about the real product.
7. **Coming soon is labelled.** A feature the product does not have yet carries a clear "Coming soon" tag on every
   scene that shows it.

## Check your work (required)

1. `node <skill>/scripts/render.mjs <workspace> stills N` renders PNGs of every scene and mid-transition to
   `build/out/stills/chNN-*.png` (add times to check moments: `... stills N 12.5 30`). It fails loudly on page errors
   and on a `C.word` phrase that is not in the timeline.
2. Look at the stills. Fix overflow, collisions, low contrast, empty frames, late or early text. Re-render, look
   again: at least two rounds.
3. Do not render video; the lead does that.

## Report back

Under 15 lines: scenes per chapter (one line each), the best stills, anything from the Screen lines you could not do
and why, every place you departed from the real product, and any engine or kit issue.
