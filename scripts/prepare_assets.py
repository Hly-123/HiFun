"""Prepare traceable web assets from the author's local submission materials.

Run with --workspace and --paper. Requires ffmpeg, pdftoppm and Pillow.
Source documents and original videos are never modified.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import urllib.request
import zipfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def run(*args):
    subprocess.run([str(x) for x in args], check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--paper', type=Path, required=True)
    parser.add_argument('--rebuttal', type=Path, required=True)
    args = parser.parse_args()
    assets = ROOT / 'assets'
    for sub in ['media', 'posters', 'figures', 'documents', 'fonts']:
        (assets / sub).mkdir(parents=True, exist_ok=True)
    manifest = []
    with tempfile.TemporaryDirectory(prefix='hifun-assets-') as tmp:
        tmp = Path(tmp)
        ppt = args.workspace / 'PPT/CORL/Video_0530.pptx'
        with zipfile.ZipFile(ppt) as z:
            for i in [2, 8, 17, 18, 19, 20, 21, 22, 23, 24]:
                with z.open(f'ppt/media/media{i}.mp4') as src, open(tmp / f'media{i}.mp4', 'wb') as dst:
                    shutil.copyfileobj(src, dst)
        edited = args.workspace / 'video/剪辑后'
        supp = args.workspace / 'Submission/Supplementary Video.mp4'

        def encode(name, source, start=0, duration=None, width=960, note='', provenance=None, keep_audio=False):
            dest = assets / 'media' / f'{name}.mp4'
            cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-ss', str(start), '-i', str(source)]
            if duration is not None:
                cmd += ['-t', str(duration)]
            cmd += ['-map', '0:v:0', '-vf', f'scale={width}:-2,fps=30,setsar=1']
            cmd += ['-map', '0:a?', '-c:a', 'aac', '-b:a', '128k'] if keep_audio else ['-an']
            cmd += ['-c:v', 'libx264', '-preset', 'fast', '-crf', '25', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-threads', '4', str(dest)]
            run(*cmd)
            poster = tmp / f'{name}.png'
            run('ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-ss', '2.5' if name == 'contact-recovery' else '0.25', '-i', dest, '-frames:v', '1', poster)
            Image.open(poster).save(assets / 'posters' / f'{name}.webp', quality=86)
            manifest.append({'asset': f'assets/media/{name}.mp4', 'source': provenance or str(source.relative_to(args.workspace)), 'start_seconds': start, 'duration_seconds': duration, 'timing': note or 'Source timing preserved; original recording multiplier not documented.', 'audio': 'preserved when present' if keep_audio else 'removed for silent inline playback'})
            print('Prepared', name, flush=True)

        for name, i in [('thin-handle', 2), ('pipette', 17), ('bit-removal', 18), ('power-drill', 19), ('angle-spreader', 20), ('thin-shaft', 21)]:
            encode(name, tmp / f'media{i}.mp4', width=540 if i == 17 else 960,
                   provenance=f'PPT/CORL/Video_0530.pptx:ppt/media/media{i}.mp4',
                   note='5x, as identified by slide movie name pipette-eval-5X-20.' if i == 17 else '')
        encode('contact-recovery', supp, 27, 7, width=1280, note='1x, labeled in the submitted supplementary video.')
        encode('size-transfer', edited / 'Hand-Skill_Generalization-2X.mp4', note='2x, labeled in source filename.')
        encode('spreader-disturbance', tmp / 'media24.mp4', provenance='PPT/CORL/Video_0530.pptx:ppt/media/media24.mp4')
        encode('shaft-disturbance', tmp / 'media23.mp4', provenance='PPT/CORL/Video_0530.pptx:ppt/media/media23.mp4')
        encode('supplementary', supp, width=1280, note='Playback multipliers are burned into the submitted video.', keep_audio=True)

        # A silent 20-second teaser; no speed changes or generative robot imagery.
        sources = [(tmp / 'media2.mp4', 0, 7), (tmp / 'media19.mp4', 5, 6), (supp, 27, 7)]
        chunks = []
        for i, (source, start, seconds) in enumerate(sources):
            chunk = tmp / f'hero-{i}.mp4'
            run('ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-ss', start, '-i', source, '-t', seconds,
                '-vf', 'scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,fps=30,setsar=1',
                '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '24', '-pix_fmt', 'yuv420p', '-threads', '4', chunk)
            chunks.append(chunk)
        concat = tmp / 'concat.txt'
        concat.write_text(''.join(f"file '{c.as_posix()}'\n" for c in chunks), encoding='utf-8')
        run('ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', concat,
            '-c', 'copy', '-movflags', '+faststart', assets / 'media/hero.mp4')
        run('ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-ss', '2', '-i', assets / 'media/hero.mp4', '-frames:v', '1', tmp / 'hero.png')
        Image.open(tmp / 'hero.png').save(assets / 'posters/hero.webp', quality=90)
        manifest.append({'asset': 'assets/media/hero.mp4', 'segments': [{'source': 'PPT media2', 'start': 0, 'duration': 7}, {'source': 'PPT media19', 'start': 5, 'duration': 6}, {'source': 'Submission/Supplementary Video.mp4', 'start': 27, 'duration': 7}], 'timing': 'No additional acceleration; source edits retained.'})

        def crop_pdf(pdf, page, name, box):
            dest = tmp / name
            run('pdftoppm', '-f', page, '-l', page, '-scale-to', '2400', '-singlefile', '-png', pdf, dest)
            im = Image.open(str(dest) + '.png')
            im.crop(tuple(round(v * (im.width if k % 2 == 0 else im.height)) for k, v in enumerate(box))).save(assets / 'figures' / f'{name}.webp', quality=95)
            manifest.append({'asset': f'assets/figures/{name}.webp', 'source': pdf.name, 'page': page, 'normalized_crop': box})

        crop_pdf(args.paper, 3, 'method', (0.162, 0.507, 0.840, 0.676))
        crop_pdf(args.workspace / 'Submission/Appendix.pdf', 5, 'training-curves', (0.17, 0.088, 0.83, 0.55))
        crop_pdf(args.workspace / 'Submission/Appendix.pdf', 6, 'coordination-analysis', (0.18, 0.274, 0.83, 0.445))

    for source, name in [(args.paper, 'paper.pdf'), (args.workspace / 'Submission/Appendix.pdf', 'appendix.pdf'), (args.rebuttal, 'additional-evidence.pdf')]:
        shutil.copy2(source, assets / 'documents' / name)
        manifest.append({'asset': f'assets/documents/{name}', 'source': source.name, 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()})

    url = 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    css = urllib.request.urlopen(req).read().decode()
    for font_url in set(re.findall(r'url\((https://[^)]+)\)', css)):
        ext = '.woff2' if '.woff2' in font_url else '.ttf'
        filename = hashlib.sha256(font_url.encode()).hexdigest()[:16] + ext
        (assets / 'fonts' / filename).write_bytes(urllib.request.urlopen(font_url).read())
        css = css.replace(font_url, filename)
    (assets / 'fonts/fonts.css').write_text(css, encoding='utf-8')
    for family in ['inter', 'spacegrotesk']:
        license_url = f'https://raw.githubusercontent.com/google/fonts/main/ofl/{family}/OFL.txt'
        (assets / 'fonts' / f'{family}-OFL.txt').write_bytes(urllib.request.urlopen(license_url).read())
    (assets / 'sources.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Assets complete.', flush=True)


if __name__ == '__main__':
    main()
