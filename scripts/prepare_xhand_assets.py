"""Prepare the author-selected XHand demos and a three-panel pipette video.

Run independently, or via prepare_assets.py. Original videos are never modified.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def run(*args):
    subprocess.run([str(arg) for arg in args], check=True)


def probe(source):
    data = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'stream=duration,nb_frames,avg_frame_rate', '-of', 'json', str(source)]))
    stream = data['streams'][0]
    return float(stream['duration'])


def prepare_xhand_assets(workspace, assets, manifest, rss_root=Path('E:/【RSS Video】')):
    sources = [rss_root / 'Supplemental Video' / name for name in (
        'pipette adaptaion 0207.mp4', 'pipette_adaptaion_new_others.mp4', 'pipette_adaptaion_new.mp4')]
    demos = [
        ('deployment-montage', workspace / 'video/剪辑后/九宫格视频/0605九宫格_x264.mp4'),
        ('position-disturbances', workspace / 'video/剪辑后/九宫格视频/Zoomout-6_x264.mp4'),
        ('xhand-drill', workspace / 'video/剪辑后/九宫格视频/Zoomout-7_x264.mp4'),
        ('xhand-faucet', workspace / 'video/剪辑后/九宫格视频/Zoomout-9-host.mp4'),
        ('more-dexterous-tasks', rss_root / 'RSS Video 素材/RSS_video_V1-rotate-screw-waterpipe-pipette.mp4')]
    for source in sources + [source for _, source in demos]:
        if not source.is_file():
            raise FileNotFoundError(source)
    for directory in ['media', 'posters']:
        (assets / directory).mkdir(parents=True, exist_ok=True)
    durations = [probe(source) for source in sources]
    longest = max(durations)
    filters = []
    inputs = []
    for i, source in enumerate(sources):
        inputs += ['-i', source]
        filters.append(f'[{i}:v]setpts=PTS-STARTPTS,fps=30,'
                       'scale=426:720:force_original_aspect_ratio=decrease:force_divisible_by=2,'
                       'pad=426:720:(ow-iw)/2:(oh-ih)/2:color=0x202622,setsar=1,'
                       f'tpad=stop_mode=clone:stop_duration={longest},trim=duration={longest}[v{i}]')
    filters.append('[v0][v1][v2]hstack=inputs=3:shortest=1,pad=1280:720:1:0:color=0x202622[out]')
    encoding = ['-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
                '-maxrate', '3600k', '-bufsize', '7200k', '-pix_fmt', 'yuv420p',
                '-movflags', '+faststart', '-threads', '4']
    run('ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', *inputs,
        '-filter_complex_threads', '2', '-filter_complex', ';'.join(filters),
        '-map', '[out]', *encoding, assets / 'media/pipette-adaptation.mp4')
    names = ['pipette-adaptation']
    entries = [{
        'asset': 'assets/media/pipette-adaptation.mp4',
        'segments_left_to_right': [
            {'source': str(source), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
             'start_seconds': 0, 'duration_seconds': duration,
             'final_frame_held_until_seconds': longest}
            for source, duration in zip(sources, durations)],
        'duration_seconds': probe(assets / 'media/pipette-adaptation.mp4'),
        'layout': 'Three complete portrait videos side by side in 1280x720; no cropping.',
        'timing': 'Source playback speeds preserved. Each shorter clip freezes on its final frame until the longest ends.',
        'audio': 'removed for silent inline playback'}]
    for name, source in demos:
        run('ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', source,
            '-vf', f'scale={1920 if name == "deployment-montage" else 1280}:-2,fps=30,setsar=1', *encoding, assets / f'media/{name}.mp4')
        names.append(name)
        entries.append({'asset': f'assets/media/{name}.mp4', 'source': str(source),
                        'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                        'start_seconds': 0, 'duration_seconds': probe(assets / f'media/{name}.mp4'),
                        'timing': 'Full supplied clip; embedded playback labels and source timing preserved.',
                        'audio': 'removed for silent inline playback'})
    for name in names:
        video = assets / f'media/{name}.mp4'
        if video.stat().st_size > 25 * 1024 * 1024:
            raise ValueError(f'Cloudflare asset limit exceeded: {video}')
        run('ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-ss', '0.25', '-i', video,
            '-frames:v', '1', '-quality', '90', assets / f'posters/{name}.webp')
    replaced = {entry['asset'] for entry in entries} | {'assets/media/pipette-positions.mp4', 'assets/media/spreader-disturbance.mp4'}
    manifest[:] = [entry for entry in manifest if entry['asset'] not in replaced]
    manifest.extend(entries)
    print('Prepared XHand demos; pipette panel durations:', durations, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, default=ROOT.parents[1])
    parser.add_argument('--rss-root', type=Path, default=Path('E:/【RSS Video】'))
    args = parser.parse_args()
    source_file = ROOT / 'assets/sources.json'
    manifest = json.loads(source_file.read_text(encoding='utf-8'))
    prepare_xhand_assets(args.workspace, ROOT / 'assets', manifest, args.rss_root)
    source_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
