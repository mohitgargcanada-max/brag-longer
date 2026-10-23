# Delivering the video

The person often reviews remotely and cannot hear audio or open files on the machine you run on, and email from there
may not exist. Private Artifact pages on claude.ai work on their own computer or phone. Pages are private until the
person shares them from the page's Share menu; say so when handing over a link.

## Artifact limits that shape everything
- Each published file is at most 15 MB; one publish sends at most 64 MB; a version holds up to 256 MB. Files left out
  of a later publish to the same page are kept, so large sets go up in batches.
- Only web file types are served (pages, css/js, json/txt/md/csv, images, mp3/wav/ogg/mp4/webm, fonts, pdf).
  Arbitrary binary (`application/octet-stream`) is refused.
- A page cannot start a download through a link. The `downloads` capability (`claude.use("downloads")`,
  `save({filename, data})`) offers a file through a confirmation prompt, with no size limit on the saved file.
- Publishing from some temp folders can be blocked by a read rule; publish from inside the workspace.

## The pages (scripts/pages.py)
- `voices` and `script`: review pages; publish, share the link, wait for the choice or approval.
- `clips <version>`: 720p captioned chapter clips (a 13-minute film is about 30 MB in total), one file per chapter so
  each stays under 15 MB. Then `all` builds one page holding every version listed in `<ws>/versions.json`, newest
  first, each with a player that runs straight through its chapters. Rebuild it on every new version.
- `single <version> ...`: a page that plays and downloads the full 1080p file. Run
  `scripts/split_for_download.py final/<name>-<version>.mp4 dl/<version>` first: it writes base64 `.txt` chunks under
  15 MB (text is a served type) and proves they rejoin byte for byte. The page fetches the chunks, decodes and joins
  them, checks the SHA-256 against the original, then plays from a blob or saves through `downloads`. Publish with
  `capabilities: {"downloads": true}`, `root` = the workspace, and the printed `files` map, in batches under 64 MB.

## Sizes to plan with (measured)
1080p final: about 9 MB a minute. 720p captioned preview: about 3.4 MB a minute. Base64 chunks add a third. So a
chapter clip under 15 MB means chapters under ~4 minutes (plan 3), and one single-file page (256 MB per version) holds
about 20 minutes of 1080p. `pages.py single` warns when a film will not fit; split it into parts at a chapter boundary
(`ffmpeg -ss <start> -t <length> -i final.mp4 -c copy part1.mp4`), give each part its own page, and name the 1080p
folder for the whole file.

## After publishing
List the page's files (`Artifact` action list, scope files) to confirm every chunk is stored at its exact size, and
read one chunk back to compare its sha256 with the local file. Tell the person what you could not test from here
(in-viewer playback and the save prompt) and the folder holding the 1080p originals.
