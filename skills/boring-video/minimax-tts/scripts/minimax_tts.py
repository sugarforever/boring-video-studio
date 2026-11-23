#!/usr/bin/env python3
"""MiniMax narration: standard-library HTTP client, MP3 and sentence-level SRT."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request


def fetch(url, *, body=None, key=None):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in ('http', 'https') or not parsed.netloc:
        raise ValueError('Expected an HTTP(S) API or download URL')
    if parsed.scheme != 'https' and parsed.hostname not in ('localhost', '127.0.0.1', '::1'):
        raise ValueError('Use HTTPS except for local testing')
    headers = {}
    if key:
        headers['Authorization'] = 'Bearer ' + key
    data = None
    if body is not None:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(body, ensure_ascii=False).encode('utf-8')
    request = urllib.request.Request(url, data=data, headers=headers)
    # API calls must not redirect credentials to another host. Downloads use no key.
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None
    opener = urllib.request.build_opener(NoRedirect()) if key else urllib.request.build_opener()
    try:
        with opener.open(request, timeout=180) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        raise ValueError(f'HTTP {exc.code}; request failed (not retried)') from None
    except (urllib.error.URLError, TimeoutError):
        raise ValueError('Network request failed or timed out (not retried)') from None


def api(path, body):
    key = os.environ.get('MINIMAX_API_KEY', '').strip()
    if not key:
        raise ValueError('Set MINIMAX_API_KEY')
    base = os.environ.get('MINIMAX_API_BASE', 'https://api.minimax.io').rstrip('/')
    result = json.loads(fetch(base + '/v1/' + path, body=body, key=key))
    if not isinstance(result, dict):
        raise ValueError('Invalid API response')
    status = result.get('base_resp') or {}
    if status.get('status_code') != 0:
        # Avoid echoing response text that could contain sensitive request data.
        raise ValueError(f"MiniMax API status {status.get('status_code', 'missing')}; check account/input")
    return result


def timestamp(ms):
    hours, rest = divmod(round(ms), 3600000)
    minutes, rest = divmod(rest, 60000)
    seconds, millis = divmod(rest, 1000)
    return f'{hours:02}:{minutes:02}:{seconds:02},{millis:03}'


def to_srt(cues):
    if not isinstance(cues, list) or not cues:
        raise ValueError('Expected a nonempty JSON array of MiniMax subtitle segments')
    blocks = []
    previous_end = 0
    for i, cue in enumerate(cues, 1):
        if not isinstance(cue, dict):
            raise ValueError(f'Invalid subtitle segment {i}')
        start, end, text = cue.get('time_begin'), cue.get('time_end'), cue.get('text')
        if (type(start) not in (int, float) or type(end) not in (int, float)
                or not math.isfinite(start) or not math.isfinite(end)
                or start < previous_end or round(end) <= round(start)
                or not isinstance(text, str) or not text.strip()):
            raise ValueError(f'Invalid subtitle text/timing at segment {i}')
        text = ' '.join(text.split())
        blocks.append(f'{i}\n{timestamp(start)} --> {timestamp(end)}\n{text}\n\n')
        previous_end = end
    return ''.join(blocks)


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def download_subtitles(url, out):
    out.mkdir(parents=True, exist_ok=True)
    raw = fetch(url)  # A signed CDN URL needs no Authorization header.
    (out / 'subtitles.json').write_bytes(raw)
    srt = to_srt(json.loads(raw))
    (out / 'narration.srt').write_text(srt, encoding='utf-8')


def synthesize(args):
    text = args.input.read_text(encoding='utf-8-sig').strip()
    if not text or len(text) >= 10000:
        raise ValueError('Text must contain 1–9999 characters; split long narration into separate parts')
    if not args.voice_id.strip():
        raise ValueError('Choose a nonempty voice ID using the voices command')
    if not math.isfinite(args.speed) or not 0.5 <= args.speed <= 2:
        raise ValueError('Speed must be between 0.5 and 2')
    if args.out_dir.exists() and any(args.out_dir.iterdir()):
        raise ValueError('Output directory must be empty; use a new directory for a new narration revision')
    # Reserve the directory before the paid request, so local write errors happen first.
    args.out_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=args.out_dir) as probe:
        probe.write(b'write check')
        probe.flush()
    body = {'model': args.model, 'text': text, 'stream': False,
            'language_boost': args.language, 'output_format': 'hex',
            'voice_setting': {'voice_id': args.voice_id, 'speed': args.speed, 'vol': 1, 'pitch': 0},
            'audio_setting': {'sample_rate': 32000, 'bitrate': 128000, 'format': 'mp3', 'channel': 1},
            'subtitle_enable': True, 'subtitle_type': 'sentence'}
    response = api('t2a_v2', body)
    data = response.get('data') or {}
    # Retain the download link and trace ID for recovery without another paid call.
    metadata = dict(response, data={k: v for k, v in data.items() if k != 'audio'})
    metadata['source_sha256'] = hashlib.sha256(text.encode('utf-8')).hexdigest()
    metadata['settings'] = {k: v for k, v in body.items() if k != 'text'}
    write_json(args.out_dir / 'response.json', metadata)
    if data.get('status') != 2 or not isinstance(data.get('audio'), str) or not data['audio']:
        raise ValueError('Missing completed audio; see response.json')
    audio = bytes.fromhex(data['audio'])
    if not audio:
        raise ValueError('Empty audio; see response.json')
    (args.out_dir / 'narration-full.mp3').write_bytes(audio)
    if not data.get('subtitle_file'):
        raise ValueError('Audio saved but subtitle_file is missing; see response.json')
    download_subtitles(data['subtitle_file'], args.out_dir)
    print(f'Audio and SRT saved to {args.out_dir}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    voices = commands.add_parser('voices', help='List account voices as JSON')
    voices.add_argument('--type', choices=['all', 'system', 'voice_cloning', 'voice_generation'], default='all')
    speech = commands.add_parser('synthesize', help='Generate MP3 and SRT from a UTF-8 spoken-text file')
    speech.add_argument('input', type=Path)
    speech.add_argument('out_dir', type=Path)
    speech.add_argument('--voice-id', required=True)
    speech.add_argument('--model', default='speech-2.8-hd')
    speech.add_argument('--speed', type=float, default=1)
    speech.add_argument('--language', default='auto')
    subs = commands.add_parser('subtitles', help='Retry subtitle download/conversion without synthesizing audio')
    subs.add_argument('--url', required=True)
    subs.add_argument('--out-dir', required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.command == 'voices':
            print(json.dumps(api('get_voice', {'voice_type': args.type}), ensure_ascii=False, indent=2))
        elif args.command == 'subtitles':
            download_subtitles(args.url, args.out_dir)
            print(f'SRT saved to {args.out_dir}')
        else:
            synthesize(args)
    except (ValueError, OSError, TypeError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
