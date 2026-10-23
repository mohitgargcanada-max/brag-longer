// Shared building blocks for this video's scenes. The generic helpers below work for any product; the product
// section is written per project (see references/scene-authoring.md) so product scenes reuse the real app's markup.

const LOGO = '../../brand/logo.png';

// Full-frame brand background with two soft glows. Colours default to the brand tokens.
function brandBackdrop(layer, { glow1 = 'var(--glow-1, #5A56A7)', glow2 = 'var(--glow-2, #D4AF37)' } = {}) {
  layer.appendChild(h(`<div class="glow" style="width:900px;height:900px;left:-250px;top:-300px;background:${glow1}"></div>`));
  layer.appendChild(h(`<div class="glow" style="width:700px;height:700px;right:-200px;bottom:-320px;background:${glow2};opacity:.16"></div>`));
}

// ---- Product section: write these for the product in this video ----------------------------------------------
// BIZ: the fictional customer the story follows (never a real one), e.g.
//   const BIZ = { name: 'Copperline Plumbing & Heating', owner: 'Maria Romano', initials: 'MR', city: 'Hamilton', site: 'copperlineplumbing.ca' };
// appShell({...}) -> {app, cam, body}: the logged-in app's frame (nav, top bar, tabs) built from the product's real
//   markup and class names, sized 1440x810 inside `.app` (kit.css scales it to 1080p); `cam` is what camera() moves.
// Small markup helpers for components that repeat across chapters (a status pill, a table row, a card).
