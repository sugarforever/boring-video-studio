#!/usr/bin/env python3
"""Apply agent-reviewed retake cuts to an analyzed 48 kHz mono PCM WAV."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import wave


def keep_ranges(cuts, duration):
    if not math.isfinite(duration) or duration <= 0 or len(cuts) > 500:
        raise ValueError('Invalid duration or too many cuts')
    kept, cursor, output = [], 0., 0.
    for cut in cuts:
        start, end = float(cut['start']), float(cut['end'])
        if not all(math.isfinite(t) for t in (start, end)) or not cursor <= start < end <= duration:
            raise ValueError('Cuts must be finite, ordered, nonoverlapping source times within the audio')
        if start > cursor:
            length = start - cursor
            kept.append({'source_start': cursor, 'source_end': start, 'output_start': output, 'output_end': output + length})
            output += length
        cursor = end
    if cursor < duration:
        kept.append({'source_start': cursor, 'source_end': duration, 'output_start': output, 'output_end': output + duration - cursor})
    if not kept:
        raise ValueError('Cuts would remove the entire recording')
    return kept


def edit(source, cuts, output):
    source, output = Path(source).resolve(), Path(output).resolve()
    if not source.is_file():
        raise ValueError(f'Analyzed WAV not found: {source}')
    with wave.open(str(source), 'rb') as audio:
        rate, frames = audio.getframerate(), audio.getnframes()
        if (rate, audio.getnchannels(), audio.getsampwidth()) != (48000, 1, 2):
            raise ValueError('Use the analyzed mono 48 kHz PCM16 narration.wav as the source')
    duration = frames / rate
    keep_ranges(cuts, duration)
    # Record and execute sample-quantized times so the edit map matches the export.
    cuts = [dict(cut, start=round(float(cut['start']) * rate) / rate,
                 end=round(float(cut['end']) * rate) / rate) for cut in cuts]
    kept = keep_ranges(cuts, duration)
    if not shutil.which('ffmpeg'):
        raise RuntimeError('FFmpeg is required')
    if output.exists():
        raise FileExistsError(f'Use a new edit output directory: {output}')
    output.parent.mkdir(parents=True, exist_ok=True)
    hasher = hashlib.sha256()
    with source.open('rb') as file:
        while block := file.read(1024 * 1024):
            hasher.update(block)
    digest = hasher.hexdigest()
    # Stage the complete bundle, then publish only after decoding and duration checks.
    with tempfile.TemporaryDirectory(prefix='.narration-edit-', dir=output.parent) as tmp:
        stage = Path(tmp)
        count = len(kept)
        filters = ['[0:a]asplit=' + str(count) + ''.join(f'[s{i}]' for i in range(count))]
        for index, item in enumerate(kept):
            first, last = round(item['source_start'] * rate), round(item['source_end'] * rate)
            length = (last - first) / rate
            fade = min(.005, length / 4)
            chain = f'[s{index}]atrim=start_sample={first}:end_sample={last},asetpts=PTS-STARTPTS'
            if index:
                chain += f',afade=t=in:d={fade:.9f}'
            if index < count - 1:
                chain += f',afade=t=out:st={length-fade:.9f}:d={fade:.9f}'
            filters.append(chain + f'[k{index}]')
        filters.append(''.join(f'[k{i}]' for i in range(count)) + f'concat=n={count}:v=0:a=1[out]')
        target = stage/'narration.edited.wav'
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-n', '-i', str(source),
                        '-filter_complex', ';'.join(filters), '-map', '[out]', '-ar', str(rate),
                        '-ac', '1', '-c:a', 'pcm_s16le', str(target)], check=True, capture_output=True)
        expected = sum(round(item['source_end'] * rate) - round(item['source_start'] * rate) for item in kept)
        with wave.open(str(target), 'rb') as audio:
            if audio.getnframes() != expected:
                raise ValueError('Export duration differs from edit plan')
        report = {'source': str(source), 'source_sha256': digest, 'timebase': 'source seconds',
                  'cuts': cuts, 'kept': kept, 'join_fade_seconds': .005,
                  'duration_before': duration, 'duration_after': expected / rate,
                  'audio': str(output/'narration.edited.wav')}
        (stage/'edit-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        output.mkdir()
        target.replace(output/target.name)
        (stage/'edit-report.json').replace(output/'edit-report.json')
    return output/'narration.edited.wav'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audio', type=Path, required=True, help='WAV used for the source transcript')
    parser.add_argument('--cuts', type=Path, required=True, help='JSON array: start, end in source seconds, reason')
    parser.add_argument('--output', type=Path, required=True, help='New edit bundle directory')
    args = parser.parse_args()
    try:
        cuts = json.loads(args.cuts.read_text(encoding='utf-8'))
        if not isinstance(cuts, list):
            raise ValueError('Cut plan must be a JSON array')
        print(edit(args.audio, cuts, args.output))
    except (OSError, ValueError, TypeError, KeyError, wave.Error, RuntimeError, subprocess.CalledProcessError) as error:
        detail = error.stderr.decode(errors='replace') if isinstance(error, subprocess.CalledProcessError) and isinstance(error.stderr, bytes) else str(error)
        print(f'Error: {detail}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
