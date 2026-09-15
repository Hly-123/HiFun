
# HiFun project page

Static research homepage with locally hosted fonts, traceable evidence figures and on-demand video playback. No bundler or backend is required. The layout takes visual inspiration from the LaST-HD project page; its content and implementation are specific to HiFun.

## Public website and automatic deployment

- GitHub Pages: https://hly-123.github.io/HiFun/
- Cloudflare mirror: https://hifun-cfu.pages.dev/
- Official implementation (coming soon): https://github.com/Hly-123/HiFun-code

This website repository is public. Every push to `master` triggers `.github/workflows/pages.yml`, which rebuilds the page and deploys only the referenced assets from `dist/` to GitHub Pages. Cloudflare continues to build the same branch independently.

For a GitHub Pages build, run `python scripts/build_public_site.py --base-path /HiFun/`. The default build uses `/` for Cloudflare. The base path keeps the 404 page's styles and home link inside the project site.

## Local preview

From this directory:

```sh
python scripts/serve_preview.py
```

Open http://127.0.0.1:8765/. This local-only static server supports byte-range requests so video seeking works. Use it rather than opening the HTML directly so browser media and clipboard behavior can be checked consistently.

## Editing

- `scripts/build_page.py` contains the content and builds `index.html` using only the Python standard library. Run `python scripts/build_page.py` after content changes.
- `styles.css` controls the warm paper, blue hand-skill and green coordination visual system. Captions and supporting prose share `--reading-size` (17 px desktop, 16 px mobile). The task introduction spans the content width, with a middle-dot title that fits one desktop line and wraps naturally on narrow screens.
- `script.js` handles video playback, navigation, figure dialogs and citation copying.
- `assets/sources.json` records the documents, PDF crops and video segments behind the displayed evidence.
- `assets/fonts/` contains self-hosted Inter and Space Grotesk fonts and their OFL licenses.

The committed HTML is directly usable on a static server; visitors do not need Python or JavaScript to read the research text. JavaScript enhances video loading and interactions. Without it, a direct supplementary-video link remains available.

Original files in `images/`, `static/` and `videos/` remain in the checkout for reference but are not loaded by this page. No tracking scripts or external runtime dependencies are included.

## Rebuilding media and figures

The current web assets are already generated. Rebuilding them requires the author's source bundle, Pillow, ffmpeg and Poppler's `pdftoppm`:

```sh
python scripts/prepare_assets.py --workspace "PATH_TO_SUPPLEMENTAL_VIDEO_WORKSPACE" --paper "PATH_TO_PAPER.pdf" --rebuttal "PATH_TO_REBUTTAL.pdf" --recovery-image "PATH_TO_key-finger-level adaptation-V2.png"
```

The script extracts the six task clips from the supplied PPTX, creates a 25-second teaser, encodes H.264 MP4s with fast-start metadata, makes WebP posters and verified figure crops, and copies the PDFs and unmodified five-frame recovery PNG. Source files are never modified. The full supplementary video retains its audio. Font acquisition requires internet access during asset preparation, not while viewing the page.

The teaser uses PPT media2 (0–7 s), `Powerdrill_Actuation_AND_Bit_removal.mp4` (0–11 s), and the submitted supplementary video (27–34 s), with no extra acceleration. Its caption boundaries are 7 s and 18 s.

## Page narrative

Title and authors → Overview video → expanded Abstract → Task Challenges → Method → six-task results, recovery/generalization and long-horizon execution → Challenges & Insights → 25-second highlights and metrics → Citation.

Videos load when visible and pause offscreen, respecting reduced motion. Overview attempts playback with sound and retains native controls; browsers that block audible autoplay show a play button. Other clips autoplay muted with playback and fullscreen buttons. These controls do not prevent retrieval of public media URLs.


Each Challenge includes the author's selected visual: the full `Unlock_pin_tool_Clean.mp4`; the method overview's multi-head critic module beside Appendix Fig. 4A; side-by-side Full-DoF HIL-SERL (`Pin-Tool-HILSERL-Full-DoF.mp4`) and HiFun (`ppt-1-xhand-dig-tool-7s_x264.mp4`); and the method overview's IAW module. The qualitative comparison clips keep their original lengths and speeds and loop independently, with a shared play/pause control. Method modules are cropped from a 7200-pixel rendering of paper page 3, preserving the original formulas and labels. Experimental subplots stack vertically on mobile and open individually for inspection. All selected media are reproducible through `prepare_challenge_assets` in the asset preparation script. Abstract paragraphs use justified alignment with English auto-hyphenation and a left-aligned final line.

The task walkthrough follows the Introduction (pp. 1–2): precise contact, synchronized arm–hand motion, and recovery from small contact errors. The IAW explanation follows §3.3, Eqs. (7)–(8): compare intervention and policy actions in the same state using the target critic ensemble; weight imitation by their estimated return difference.

## Evidence and editorial conventions

- Main evaluation: six tasks, 50 trials each, 295/300 successes (98.3%).
- Rebuttal baseline comparison: four Sharpa tasks. The 12.5%, 46% and 100% values must not be mixed with six-task averages.
- The six-task baseline table is omitted from the homepage. The standalone four-task comparison and component-ablation section are omitted in this focused version; paper and Appendix links are temporarily withheld pending release.
- The ≤60-minute claim describes online HIL coordination only. The ~109-minute total follows the rebuttal's full-pipeline accounting.
- Key recovery is an additional skill example. Fixed-arm evaluations and local size transfer are distinct from the main evaluation.
- Two-hand deployment does not claim zero-shot policy transfer across hand morphologies.
- Source timing is preserved. Known 1×, 2× and 5× playback factors are identified. Several source clips have no documented original recording multiplier; do not relabel them as real time without confirmation from the original recording.
- Accepted to CoRL 2026, as confirmed by the authors. The homepage badge and BibTeX reflect the conference acceptance; the implementation remains not yet publicly released.

## Validation

With a local server running, install or point to Playwright and run:

```sh
node scripts/check_page.cjs
```

Optional environment variables: `HIFUN_PLAYWRIGHT` (absolute Playwright package path), `HIFUN_BROWSER` (installed browser channel, default `msedge`), and `HIFUN_PREVIEW_URL` (default `http://127.0.0.1:8765`).

The check covers local resources, anchors, media decoding, initial video loading, offscreen pause/resume, explicit pause persistence, mobile navigation, figure-dialog focus, clipboard copying, reduced motion, and desktop/mobile overflow. Screenshots and the report are saved under ignored `.preview/`.

## Publication

Cloudflare Pages publishes the `master` branch at https://hifun-cfu.pages.dev/ using `python3 scripts/build_public_site.py` and the `dist` output directory. Pushing to `master` automatically updates the public website; the GitHub repository remains private. The previous full version is preserved by the `full` tag at `52470db`.


### Evaluation presentation

The first four task cards show Sharpa. A separate “Across hand embodiments” heading introduces the two XHand tasks, followed by paired recovery/size-transfer videos and a wide long-horizon sequence. Per-task success-count badges and author-facing provenance disclaimers are omitted from the gallery; the headline result and experiment evidence remain.

`scripts/prepare_xhand_assets.py` prepares the current XHand additions and is also called by `prepare_evaluation_assets`. Three complete pipette source videos (6.2 s, 24.9 s, and 9.1 s) are composed left to right without acceleration. Shorter panels hold their last frame until the longest finishes. The source paths, hashes and exact video-stream durations are recorded in `assets/sources.json`. The two additional XHand cards use `Zoomout-7_x264.mp4` and `Zoomout-9-host.mp4`; the More successful deployment section pairs `0605九宫格_x264.mp4` on the left with `RSS_video_V1-rotate-screw-waterpipe-pipette.mp4` on the right (stacked on mobile). All are re-encoded for inline playback under the Cloudflare 25 MiB per-file limit.

The full `Cross-hand deployment-unlock key-1.3X.mp4` plays at its source 1.3× speed. Thin-Shaft Tool Retrieval retains the full author-selected RSS demo `长程绑线3.19-1.5X.mp4` and its inset camera view.

Section introductions, evidence introductions, subsection descriptions and expanded training/scope text span their available content width. The IAW method illustration retains its 456 px desktop size and appears left of its explanation; mobile stacks the image above the text. Click-to-enlarge access to the original image is preserved.

The pipette composite plays once and retains its final frame using `data-hold-last-frame`. It does not restart on scrolling back into view; the Replay button allows replay. Earlier-finishing panels are frozen directly in the composite, preserving their last frame throughout the remaining playback.

### Code release entry

The public official implementation placeholder is https://github.com/Hly-123/HiFun-code. Its README identifies the CoRL 2026 paper and marks the implementation as coming soon. The project page links to the published paper PDF and this code repository.

Challenges are ordered as exploration, intervention interface, credit assignment, and intervention weighting. Challenge and insight descriptions use justified prose within the same width as their headings. The method section shows its short overview and original paper figure directly; the separate two-level diagram and numbered training-stage block are omitted.

Angle-Spreader Retrieval uses the first 40 seconds of the original PPT `media20.mp4`, published as `angle-spreader-40s.mp4`. Position disturbances uses the complete `Zoomout-6_x264.mp4`; its caption describes re-establishing alignment and contact after a tool-position disturbance. The nine-view montage is encoded at 1920 px width to retain its individual panels.
