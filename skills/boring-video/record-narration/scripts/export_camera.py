#!/usr/bin/env python3
"""Export synchronized camera footage, optionally over a finished content video."""
import argparse
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from edit_audio import keep_ranges

CORNERS = {
    'top-left': ('M', 'M'), 'top-right': ('W-w-M', 'M'),
    'bottom-left': ('M', 'H-h-M'), 'bottom-right': ('W-w-M', 'H-h-M'),
}


def probe(path, kind):
    data = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-select_streams', kind + ':0',
        '-show_streams', '-show_format', '-of', 'json', str(path)]))
    if not data['streams']:
        raise ValueError(f'Missing {kind} track: {path}')
    stream = data['streams'][0]
    duration = stream.get('duration', data.get('format', {}).get('duration'))
    if duration is None:
        # Browser streaming WebM has no duration header. Packet times retain pauses removed by MediaRecorder.
        packets = json.loads(subprocess.check_output([
            'ffprobe', '-v', 'error', '-select_streams', kind + ':0',
            '-show_entries', 'packet=pts_time,duration_time', '-of', 'json', str(path)]))['packets']
        times = [(float(p['pts_time']), float(p.get('duration_time', 0))) for p in packets if 'pts_time' in p]
        if not times:
            raise ValueError(f'No timed packets: {path}')
        duration = max(t + d for t, d in times) - min(t for t, _ in times)
    duration = float(duration)
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError(f'Invalid media duration: {path}')
    return duration, stream


def export(video, audio, output, edit_report=None, background=None, corner='bottom-right', width=.25, margin=24):
    video, audio, output = (Path(p).resolve() for p in (video, audio, output))
    if output.exists():
        raise FileExistsError(f'Use a new output path: {output}')
    if output.suffix.lower() != '.mp4':
        raise ValueError('Output must be .mp4')
    if not math.isfinite(width) or not .1 <= width <= .5 or not 0 <= margin <= 500:
        raise ValueError('Width must be 0.1–0.5 and margin 0–500 pixels')
    source_duration, camera_stream = probe(video, 'v')
    offset = 0.
    try:
        original_audio_duration, original_audio_stream = probe(video, 'a')
    except ValueError:
        pass  # Standalone camera sources may have no original audio track.
    else:
        offset = float(camera_stream.get('start_time', 0)) - float(original_audio_stream.get('start_time', 0))
        if not math.isfinite(offset):
            raise ValueError('Invalid camera/audio start offset')
        source_duration = original_audio_duration
    final_duration, _ = probe(audio, 'a')
    duration, cuts = source_duration, []
    if edit_report:
        report = json.loads(Path(edit_report).read_text(encoding='utf-8'))
        duration = float(report['duration_before'])
        if not math.isfinite(duration) or abs(duration - source_duration) > .2:
            raise ValueError('Camera duration differs from the audio edit source; use the matching original take')
        cuts = report['cuts']
    kept = keep_ranges(cuts, duration)
    expected = sum(item['source_end'] - item['source_start'] for item in kept)
    if edit_report and abs(float(report['duration_after']) - expected) > .001:
        raise ValueError('Edit report duration does not match its cuts')
    if abs(expected - final_duration) > .2:
        raise ValueError('Reviewed audio duration differs from camera edit; supply the matching edit report')
    inputs = ['-i', str(video), '-i', str(audio)]
    # Keep source timestamps through every cut. Per-segment PTS resets/concat
    # accumulate rounding at each cut and drift from sample-accurate audio.
    selected = '+'.join(f"gte(t,{item['source_start']:.9f})*lt(t,{item['source_end']:.9f})" for item in kept)
    removed = '+'.join(f"{float(cut['end'])-float(cut['start']):.9f}*gte(T,{float(cut['end']):.9f})" for cut in cuts) or '0'
    filters = [f"[0:v]setpts=PTS-STARTPTS+({offset:.9f})/TB,select='{selected}',setpts='PTS-({removed})/TB',fps=30:start_time=0[camera]"]
    if background:
        background = Path(background).resolve()
        bg_duration, bg = probe(background, 'v')
        if bg_duration + .05 < final_duration:
            raise ValueError('Content video is shorter than reviewed narration')
        w = max(2, int(bg['width'] * width) // 2 * 2)
        height = w * camera_stream['height'] / camera_stream['width']
        if height + margin * 2 > bg['height']:
            raise ValueError('Camera window and margins exceed content height; reduce --width or --margin')
        if margin * 2 + w >= bg['width']:
            raise ValueError('Camera window and margins exceed content width')
        inputs += ['-i', str(background)]
        x, y = (part.replace('M', str(margin)) for part in CORNERS[corner])
        filters += [f'[camera]scale={w}:-2,setsar=1[pip]',
                    '[2:v]setpts=PTS-STARTPTS[content]',
                    f'[content][pip]overlay=x={x}:y={y}:eof_action=repeat[v]']
    else:
        filters.append('[camera]scale=trunc(iw/2)*2:trunc(ih/2)*2,setsar=1[v]')
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.camera-export-', dir=output.parent) as tmp:
        target = Path(tmp)/'camera.mp4'
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-n', *inputs,
                        '-filter_complex', ';'.join(filters), '-map', '[v]', '-map', '1:a:0',
                        '-t', str(final_duration), '-c:v', 'libx264', '-preset', 'fast',
                        '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-movflags', '+faststart', str(target)],
                       check=True, capture_output=True)
        actual, _ = probe(target, 'v')
        if abs(actual - final_duration) > .2:
            raise ValueError('Rendered camera duration differs from narration')
        # Same filesystem, publish atomically without overwriting a concurrent export.
        os.link(target, output)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--video', type=Path, required=True, help='Original camera take from handoff.json')
    parser.add_argument('--audio', type=Path, required=True, help='Final reviewed WAV, including any retake cuts')
    parser.add_argument('--edit-report', type=Path, help='edit_audio.py report for this same original take')
    parser.add_argument('--background', type=Path, help='Finished content video already aligned to the reviewed audio')
    parser.add_argument('--corner', choices=CORNERS, default='bottom-right')
    parser.add_argument('--width', type=float, default=.25, help='Camera width as fraction of content width (0.1–0.5)')
    parser.add_argument('--margin', type=int, default=24, help='Corner inset in pixels')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        print(export(args.video, args.audio, args.output, args.edit_report, args.background, args.corner, args.width, args.margin))
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        detail = error.stderr.decode(errors='replace') if isinstance(error, subprocess.CalledProcessError) and isinstance(error.stderr, bytes) else str(error)
        print(f'Error: {detail}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
