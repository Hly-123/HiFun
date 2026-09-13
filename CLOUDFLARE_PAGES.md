# Publish HiFun with a private GitHub repository

Production URL: **https://hifun-cfu.pages.dev/**. Cloudflare project: `hifun`.

Use Cloudflare Pages **Git integration** and authorize only `Hly-123/HiFun` in the Cloudflare GitHub app. Keep the GitHub repository private.

In Cloudflare: **Workers & Pages → Create application → Pages → Connect to Git**.

| Setting | Value |
| --- | --- |
| GitHub repository | `Hly-123/HiFun` |
| Project name | `hifun` |
| Production branch | `master` |
| Framework preset | None |
| Build command | `python3 scripts/build_public_site.py` |
| Build output directory | `dist` |
| Root directory | Leave blank (repository root) |

Pushes to `master` trigger production builds automatically through the connected Cloudflare GitHub app. Preview branch deployments and PR comments are disabled. This repository does not need deployment tokens or GitHub Actions secrets with Git integration.

## What is published

The build regenerates `index.html` and follows its links, lazy video sources, posters, zoom targets and CSS font references. It copies only the site files and referenced assets into `dist`, with the font licenses and a 404 page. The generator scripts, source manifest, README, original `videos` directory, unused media and Git history are not included. The build rejects missing resources, references outside the repository and files above Cloudflare Pages' 25 MiB per-file limit.

Build locally with `python scripts/build_public_site.py`. The build uses Python's standard library and the committed web assets; it does not require FFmpeg, original recordings or access to the author's local drives. `dist` is generated and ignored by Git.

On `*.pages.dev`, a requested video is downloaded into a browser Blob before playback so native seeking works despite Pages' lack of HTTP byte-range responses. The play button shows loading progress as a loading state; initial entry still downloads no video bodies. This keeps hosting entirely static with no Functions, paid storage or streaming service. Video startup depends on downloading the selected clip (the overview is about 21 MB).

## Verification after deployment

- Open the production URL while signed out of GitHub.
- Check Overview video playback and seeking, Challenge figure zoom and both XHand task videos.
- Let the pipette composite finish: it should retain its final frame without automatically replaying.
- Open the Paper/Appendix links and test the mobile navigation.
- Check the Cloudflare deployment's commit matches the intended `master` commit.

Official documentation: [Git integration](https://developers.cloudflare.com/pages/get-started/git-integration/) · [Static HTML](https://developers.cloudflare.com/pages/framework-guides/deploy-anything/) · [Limits](https://developers.cloudflare.com/pages/platform/limits/)
