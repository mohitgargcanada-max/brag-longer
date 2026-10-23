# Writing scenes

Scenes are HTML in `build/scenes/chNN.js`, one file per chapter, loaded by `player.html` with `engine.js`, `kit.js`,
`kit.css`, the brand CSS and `build/out/timeline.js` (written by render.mjs from timeline.json).

## The engine (engine.js)
```js
Demo.chapter(3, C => [
  { from: 0, demo: true, hideLabel: true, build(layer, C) {     // product scene: demo chip on, chapter label off
      const { app, cam, body } = appShell({...});              // kit.js, per product
      layer.append(app);
      const cur = makeCursor(layer);
      return (t, T) => {                                        // t = seconds into the scene, T = chapter time
        camera(cam, T, [{ t: 0, x: 0, y: 0, s: 1 }, { t: C.word('every statement'), x: -300, y: -120, s: 1.4 }]);
        reveal(body.querySelector('.card'), T, C.sent(2));      // fade + rise in on sentence 2
        cur(T, [{ t: C.sent(3) - 1, x: 1500, y: 900 }, { t: C.sent(3), x: 820, y: 610, click: true }]);
      };
  } },
  { from: C.para(2), build(layer) { brandBackdrop(layer); /* brand scene */ return t => {}; } },
]);
```
- Cues: `C.sent(i)` / `C.sentEnd(i)` (sentence i of the chapter), `C.para(p)` / `C.paraEnd(p)` (paragraph p),
  `C.word('exact phrase')` (estimated time a phrase is spoken; throws if the phrase is not in the timeline, which is
  how stale cues are found). Never hand-type seconds.
- Helpers: `h(html)`, `prog(t, start, dur, ease)`, `reveal(el, t, start, {dur, dy, dx, scale})`,
  `typeText(el, text, t, start, cps)`, `countUp(el, value, t, start, dur, fmt)`, `camera(el, t, keys)`,
  `makeCursor(layer)` -> `(t, points)`. Eases: `ease.out`, `ease.inOut`, `ease.back`, `ease.linear`.
- Scene `to` defaults to the next scene's `from`. The engine dips through the background between scenes (no muddy
  cross-fades) and fades each chapter in and out. Scenes per chapter: about one per paragraph.
- Deterministic: everything is set in `update`. Override any CSS transition or animation the product CSS carries.
  Measure positions (for rings and cursor targets) after the camera call in `update`, from `getBoundingClientRect`.

## The app frame
The logged-in product is built at 1440x810 inside `.app` (kit.css scales it by 1.333 to fill 1080p). Copy markup and
class names from the product's real components; fill them with the fictional `BIZ`. Push the camera in (scale 1.2-1.8)
on what the narration names so 15px app text becomes legible. Long pages: unclip the frame inside the chapter file.
Light auth or onboarding screens can sit in a browser-window frame on the brand stage.

## Brand scenes
Kinetic type, cards, diagrams and charts on `brandBackdrop(layer)` with `.title-xl/.title-l/.title-m/.body-l/.panel`.
Charts are drawn to scale with labelled axes and a source line. One idea per scene; something arrives every 2-4 s.

## Checking
`node <skill>/scripts/render.mjs <ws> stills N [t ...]` renders every scene and mid-transition. Look at them: overflow,
collisions, contrast, text that arrives late or leaves early, a frame where nothing has happened for too long, and
accuracy (real labels, fictional names, coming-soon tags). Two review rounds at least. Text meant to be read stays
still ~0.3 s per word; nothing essential in the bottom 140 px (captions and the demo chip live there).

## Typical pacing
Narration runs at about 180 spoken words a minute plus pauses (gaps in video.json). A 3-minute cut is about 430 spoken
words in 7 chapters; 8 minutes about 1,150 words in 13; 13 minutes about 1,700.
