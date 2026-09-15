"""Build the public static site using only referenced site files.

Run: python3 scripts/build_public_site.py
No third-party dependencies or original author media are needed.
"""
import argparse
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'dist'
ROOT_FILES = {'index.html', 'styles.css', 'script.js', 'favicon.svg'}
ASSET_TYPES = {'.pdf', '.mp4', '.webp', '.png', '.jpg', '.jpeg', '.svg',
               '.css', '.woff', '.woff2', '.ttf', '.otf'}
MAX_FILE_BYTES = 25 * 1024 * 1024


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        self.urls.extend(value for key, value in attrs
                         if key in {'href', 'src', 'poster', 'data-src', 'data-zoom'} and value)


def local_path(url, parent):
    parsed = urlsplit(url)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    path = ((ROOT if parsed.path.startswith('/') else parent) /
            unquote(parsed.path).lstrip('/')).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError(f'Site reference is outside the repository: {url}')
    relative = path.relative_to(ROOT)
    if (relative.as_posix() not in ROOT_FILES and
            not (relative.parts[0] == 'assets' and path.suffix.lower() in ASSET_TYPES)):
        raise ValueError(f'Reference is not a public site asset: {relative}')
    if not path.is_file():
        raise FileNotFoundError(f'Missing site resource: {relative}')
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-path', default='/', help='Hosting path, e.g. /HiFun/ for GitHub Pages')
    args = parser.parse_args()
    base_path = '/' + args.base_path.strip('/') + '/' if args.base_path.strip('/') else '/'
    if not re.fullmatch(r'/([A-Za-z0-9_-]+/)*', base_path):
        parser.error('base-path must contain only slash-separated letters, numbers, hyphens or underscores')
    subprocess.run([sys.executable, str(ROOT / 'scripts/build_page.py')], check=True)
    pending = [ROOT / name for name in ROOT_FILES]
    selected = set()
    while pending:
        path = pending.pop()
        if path in selected:
            continue
        selected.add(path)
        urls = []
        if path.suffix == '.html':
            parser = References()
            parser.feed(path.read_text(encoding='utf-8'))
            urls = parser.urls
        elif path.suffix == '.css':
            urls = [match[1].strip() for match in
                    re.findall(r'url\(\s*([\'"]?)(.*?)\1\s*\)', path.read_text(encoding='utf-8'))]
        for url in urls:
            dependency = local_path(url, path.parent)
            if dependency is not None:
                pending.append(dependency)
    selected.update((ROOT / 'assets/fonts').glob('*-OFL.txt'))
    for path in selected:
        if path.stat().st_size > MAX_FILE_BYTES:
            raise ValueError(f'Cloudflare Pages 25 MiB file limit exceeded: {path.relative_to(ROOT)}')

    # Delete only this script's fixed output directory, never a symlink or external path.
    if OUTPUT.is_symlink() or OUTPUT.resolve() != ROOT / 'dist':
        raise ValueError('Refusing to replace an unexpected output directory')
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir()
    for path in sorted(selected):
        destination = OUTPUT / path.relative_to(ROOT)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
    (OUTPUT / '404.html').write_text(f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Page not found | HiFun</title><link rel="stylesheet" href="{escape(base_path)}assets/fonts/fonts.css">
<link rel="stylesheet" href="{escape(base_path)}styles.css"></head><body><main class="container section">
<p class="eyebrow">HiFun</p><h1>Page not found</h1><p>The page you requested is unavailable.</p>
<a class="button" href="{escape(base_path)}">Return to HiFun</a></main></body></html>
''', encoding='utf-8')
    total = sum(path.stat().st_size for path in selected)
    print(f'Public build: {len(selected) + 1} files, {total / 1024 / 1024:.1f} MiB -> dist/')


if __name__ == '__main__':
    main()
