
# HiFun project page

Static research homepage with locally hosted fonts, traceable evidence figures and on-demand video playback. No bundler or backend is required. The layout takes visual inspiration from the LaST-HD project page; its content and implementation are specific to HiFun.

## Local preview

From this directory:

```sh
python -m http.server 8765 --bind 127.0.0.1
```

Open http://127.0.0.1:8765/. Use an HTTP server rather than opening the HTML directly so browser media and clipboard behavior can be checked consistently.

## Editing

- `scripts/build_page.py` contains the content and builds `index.html` using only the Python standard library. Run `python scripts/build_page.py` after content changes.
- `styles.css` controls the warm paper, blue hand-skill and green coordination visual system.
- `script.js` handles video playback, navigation, figure dialogs and citation copying.
- `assets/sources.json` records the documents, PDF crops and video segments behind the displayed evidence.
- `assets/fonts/` contains self-hosted Inter and Space Grotesk fonts and their OFL licenses.

The committed HTML is directly usable on a static server; visitors do not need Python or JavaScript to read the research text. JavaScript enhances video loading and interactions. Without it, a direct supplementary-video link remains available.

Original files in `images/`, `static/` and `videos/` remain in the checkout for reference but are not loaded by this page. No tracking scripts or external runtime dependencies are included.

## Rebuilding media and figures

The current web assets are already generated. Rebuilding them requires the author's source bundle, Pillow, ffmpeg and Poppler's `pdftoppm`:

```sh
python scripts/prepare_assets.py --workspace "PATH_TO_SUPPLEMENTAL_VIDEO_WORKSPACE" --paper "PATH_TO_PAPER.pdf" --rebuttal "PATH_TO_REBUTTAL.pdf"
```

The script extracts the six task clips from the supplied PPTX, creates a 20-second teaser, encodes H.264 MP4s with fast-start metadata, makes WebP posters and verified figure crops, and copies the PDFs. Source files are never modified. The full supplementary video retains its audio. Font acquisition requires internet access during asset preparation, not while viewing the page.

## Evidence and editorial conventions

- Main evaluation: six tasks, 50 trials each, 295/300 successes (98.3%).
- Rebuttal baseline comparison: four Sharpa tasks. The 12.5%, 46% and 100% values must not be mixed with six-task averages.
- The baseline table retains the Appendix's partial-success-credit explanation.
- The ≤60-minute claim describes online HIL coordination only. The ~109-minute total follows the rebuttal's full-pipeline accounting.
- Key recovery is an additional skill example. Fixed-arm evaluations and local size transfer are distinct from the main evaluation.
- Two-hand deployment does not claim zero-shot policy transfer across hand morphologies.
- Source timing is preserved. Known 1×, 2× and 5× playback factors are identified. Several source clips have no documented original recording multiplier; do not relabel them as real time without confirmation from the original recording.
- The supplied paper is a manuscript. The citation and release labels do not imply acceptance or a public implementation release.

## Validation

With a local server running, install or point to Playwright and run:

```sh
node scripts/check_page.cjs
```

Optional environment variables: `HIFUN_PLAYWRIGHT` (absolute Playwright package path), `HIFUN_BROWSER` (installed browser channel, default `msedge`), and `HIFUN_PREVIEW_URL` (default `http://127.0.0.1:8765`).

The check covers local resources, anchors, media decoding, initial video loading, offscreen pause/resume, explicit pause persistence, mobile navigation, figure-dialog focus, clipboard copying, reduced motion, and desktop/mobile overflow. Screenshots and the report are saved under ignored `.preview/`.

## Publication

This revision is prepared for local review. It does not publish the site, push commits, or change repository visibility. Review author metadata, manuscript links, citation and code release status before a future public deployment.
