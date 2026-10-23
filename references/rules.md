# Rules for what the viewer sees

Each rule here was learned from a real mistake while making a 13-minute product film and its 8- and 3-minute cuts.
The film is shown to customers, partners and investors, so a wrong claim costs more than a rough edge.

## Truth about the product
- **Narration describes the real product.** Check every product step against the screen's source code in the same
  turn the line is written. ("She enters her name, website and city" was approved; the real form has one field. A
  scene builder then invented two fields to match.) When the narration and the screen disagree, fix the narration.
- **Show the real screens** with the product's own markup, labels and button text. Where the video simplifies,
  simplify by cropping and camera, not by inventing UI.
- **Not built yet = "Coming soon"**, in the narration and as a visible tag on every scene that shows it.
- **Every figure has a source** (the company's deck, report or config), checked in the same turn it is written, with
  the source in a `<!-- -->` note. Ask before using traction figures in a public cut; keep honest caveats with them
  (e.g. "pre-revenue") or leave the figures out; never keep the numbers and drop the caveat.
- **No invented capability in examples.** Reasons, labels and outcomes on screen are the kind the product really
  produces ("matches your ideal customer", not "repair complaints in recent reviews" when it never reads reviews).
- **"Hide how it works"** means no internals anywhere: servers, models, crawlers, pipelines, test counts, data sources.

## Real people and businesses
- **The customer in the story is fictional**, and every product scene carries the "Fictional demo business" chip.
- **No real customer, person, lead or domain** from the DO NOT SHOW list, including in sample rows and seed data.
  Things the product shows publicly can still be real customers' data: check before reusing a landing-page example.
- **Invented businesses get coined names.** Local nicknames and common local names ("Steel City Plumbing",
  "Escarpment Heating", "Burlington Drain") can belong to real businesses, and a scene may show them failing checks.
  Use coinages ("Quellwater Plumbing", "Tinmark Heating"). Phone numbers 555-01xx; email and websites on `.example`.
- **No competitor vendor names on screen**; categories only ("lead lists", "agencies").
- **Pronouns:** never infer anyone's from a name or photo; ask, or use what they state.
- Team or founder videos need each person's consent to their name and photo.

## Sound
- **Music you did not make has a licence question.** The bundled /brag tracks say to verify their licence before
  publishing; mix.py makes an original bed instead.
- Kokoro voices are Apache 2.0. Check the product name's pronunciation (`say` in video.json) before voicing it all.

## Working habits that kept this honest
- **Versions are never overwritten.** A rebuild once overwrote the version the team was reviewing.
- **Write code and anything with backslashes through file tools, not shell heredocs**; a heredoc can silently alter
  escapes. Assert every scripted text replacement actually matched.
- **A check must be able to fail.** Compare against the real file, pull real frames, hash real bytes.
- **Label problems you find in the product as pre-existing**, and record them in the project's tracker; don't let
  them live only in a chat reply.
