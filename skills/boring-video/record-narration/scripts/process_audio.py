#!/usr/bin/env python3
"""Normalize recorded narration, transcribe locally, and apply agent-reviewed corrections."""
import argparse
import copy
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from importlib.metadata import version


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def timestamp(seconds):
    if not math.isfinite(seconds) or seconds < 0:
        raise ValueError('Invalid subtitle time')
    ms = round(seconds * 1000)
    hours, ms = divmod(ms, 3600000)
    minutes, ms = divmod(ms, 60000)
    seconds, ms = divmod(ms, 1000)
    return f'{hours:02}:{minutes:02}:{seconds:02},{ms:03}'


def srt(data):
    blocks = []
    previous = 0
    for index, segment in enumerate(data['segments'], 1):
        start, end, text = segment['start'], segment['end'], segment['text'].strip()
        if not text or not math.isfinite(end) or end <= start or start < previous:
            raise ValueError('Invalid or overlapping subtitle cue')
        previous = end
        blocks.append(f'{index}\n{timestamp(start)} --> {timestamp(end)}\n{text}\n')
    return '\n'.join(blocks)


def correct(data, changes):
    result = copy.deepcopy(data)
    by_id = {cue['id']: cue for cue in result['segments']}
    seen = set()
    for change in changes:
        cue_id = change['id']
        text = change['text']
        if cue_id not in by_id or cue_id in seen or not isinstance(text, str) or not text.strip() or '\n\n' in text or '-->' in text:
            raise ValueError('Corrections require unique existing cue IDs and nonempty text')
        seen.add(cue_id)
        by_id[cue_id]['text'] = text.strip()
    srt(result)
    return result


def word_cues(words, max_chars=24):
    cues, group = [], []
    def flush():
        if group:
            cues.append({'id': len(cues) + 1, 'start': group[0]['start'],
                         'end': group[-1]['end'], 'text': ''.join(w['word'] for w in group).strip()})
            group.clear()
    previous_end = 0
    for word in words:
        word = dict(word)
        word['start'] = max(previous_end, float(word['start']))
        word['end'] = float(word['end'])
        if not word['word'].strip() or word['end'] <= word['start']:
            continue
        if group and (len(''.join(w['word'] for w in group)) + len(word['word']) > max_chars
                      or word['end'] - group[0]['start'] > 5
                      or word['start'] - group[-1]['end'] > .8):
            flush()
        group.append(word)
        previous_end = word['end']
        if word['word'].rstrip().endswith(('。', '！', '？', '.', '!', '?')):
            flush()
    flush()
    return cues


def prepare(source, output):
    source, output = Path(source).resolve(), Path(output).resolve()
    if not source.is_file():
        raise ValueError(f'Audio not found: {source}')
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
        raise RuntimeError('需要 FFmpeg：在 macOS 使用 brew install ffmpeg')
    output.mkdir(parents=True, exist_ok=True)
    target = output / 'narration.wav'
    if target.exists():
        raise FileExistsError(f'已有处理后的音频，使用新输出目录或继续 transcribe：{target}')
    try:
        from ffmpeg_normalize import FFmpegNormalize, FFmpegNormalizeError
    except ImportError as error:
        raise RuntimeError('需要 ffmpeg-normalize：在处理用的虚拟环境执行 pip install -r <skill-dir>/requirements.txt') from error
    with tempfile.TemporaryDirectory(prefix='.prepare-', dir=output) as tmp:
        decoded = Path(tmp)/'decoded.wav'
        temp = Path(tmp)/'normalized.wav'
        # Decode first: streaming WebM has no reliable duration header, and
        # loudness must be measured after the same resampling/downmix as export.
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-n', '-i', str(source),
                        '-map', '0:a:0', '-ar', '48000', '-ac', '1', '-c:a', 'pcm_s16le', str(decoded)],
                       check=True, capture_output=True)
        normalizer = FFmpegNormalize(target_level=-16, true_peak=-1.5,
            keep_loudness_range_target=True, auto_lower_loudness_target=True,
            audio_codec='pcm_s16le', sample_rate=48000, audio_channels=1,
            video_disable=True, subtitle_disable=True, metadata_disable=True, progress=False)
        normalizer.add_media_file(str(decoded), str(temp))
        try:
            normalizer.run_normalization()
        except FFmpegNormalizeError as error:
            raise RuntimeError(f'ffmpeg-normalize 处理失败：{error}') from error
        stats = list(normalizer.media_files[0].get_stats())
        modes = [item.get('ebu_pass2', {}).get('normalization_type') for item in stats]
        if not modes or any(mode != 'linear' for mode in modes):
            raise RuntimeError('响度处理未保持线性，已停止导出以免抬高安静片段。保留原录音并检查输入。')
        probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_format', '-of', 'json', str(temp)]))
        duration = float(probe['format']['duration'])
        if not math.isfinite(duration) or duration <= 0:
            raise ValueError('录音没有可用音频')
        for item in stats:
            item['input_file'] = str(source)
            item['output_file'] = str(target)
        temp.replace(target)
    write_json(output / 'processing.json', {'source': str(source), 'audio': str(target), 'duration': duration,
               'status': 'normalized', 'normalization': {'engine': 'ffmpeg-normalize',
               'version': version('ffmpeg-normalize'), 'mode': 'linear', 'target_lufs': -16,
               'true_peak_db': -1.5, 'auto_lower_target': True, 'stats': stats},
               'cuts': [], 'speed': 1.0, 'denoise': False})
    return target


def transcribe(audio, output, model='small', language='zh'):
    try:
        from faster_whisper import WhisperModel
    except ImportError as error:
        raise RuntimeError('缺少本地转写依赖。使用 Python 3.11/3.12 虚拟环境安装：pip install "faster-whisper>=1.1,<2"') from error
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    for name in ('transcript.raw.json', 'subtitles.raw.srt'):
        if (output / name).exists():
            raise FileExistsError(f'{name} 已存在，请使用新目录保留旧转写')
    print(f'Loading local Whisper model: {model} (first use may download model weights)', flush=True)
    engine = WhisperModel(model, device='cpu', compute_type='int8')
    segments, info = engine.transcribe(str(audio), language=None if language == 'auto' else language,
                                       word_timestamps=True, vad_filter=True)
    words = []
    for segment in segments:
        for word in segment.words or []:
            words.append({'start': word.start, 'end': word.end, 'word': word.word, 'probability': word.probability})
        print(f'Transcribed through {segment.end:.1f}s', flush=True)
    data = {'audio': str(Path(audio).resolve()), 'language': info.language, 'model': model,
            'words': words, 'segments': word_cues(words)}
    if not data['segments']:
        raise ValueError('未识别出语音；请试听录音并检查麦克风或语言设置')
    subtitle = srt(data)
    write_json(output / 'transcript.raw.json', data)
    (output / 'subtitles.raw.srt').write_text(subtitle, encoding='utf-8')
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    prep = commands.add_parser('prepare', help='Normalize selected recording; optionally transcribe')
    source = prep.add_mutually_exclusive_group(required=True)
    source.add_argument('--session', type=Path)
    source.add_argument('--audio', type=Path)
    prep.add_argument('--output', type=Path, required=True)
    prep.add_argument('--transcribe', action='store_true')
    tx = commands.add_parser('transcribe', help='Transcribe final audio, including after a failed model download')
    tx.add_argument('--audio', type=Path, required=True)
    tx.add_argument('--output', type=Path, required=True)
    for command in (prep, tx):
        command.add_argument('--model', default='small', help='Multilingual faster-whisper model name or local model directory')
        command.add_argument('--language', default='zh', help='Language code or auto')
    correction = commands.add_parser('correct', help='Apply agent-reviewed cue text without changing timing')
    correction.add_argument('--transcript', type=Path, required=True)
    correction.add_argument('--corrections', type=Path, required=True)
    correction.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'prepare':
            if args.session:
                handoff = json.loads((args.session / 'handoff.json').read_text(encoding='utf-8'))
                audio = Path(handoff['audio'])
                state = json.loads((args.session / 'session.json').read_text(encoding='utf-8'))
                if state['status'] != 'ready' or state['selected'] != handoff['take']:
                    raise ValueError('请先在录音页面选定版本并点击交给 Codex')
            else:
                audio = args.audio
            target = prepare(audio, args.output)
            print(f'Normalized audio: {target}', flush=True)
            if args.transcribe:
                transcribe(target, args.output, args.model, args.language)
        elif args.command == 'transcribe':
            transcribe(args.audio, args.output, args.model, args.language)
        else:
            data = json.loads(args.transcript.read_text(encoding='utf-8'))
            changes = json.loads(args.corrections.read_text(encoding='utf-8'))
            result = correct(data, changes)
            args.output.mkdir(parents=True, exist_ok=True)
            if any((args.output / name).exists() for name in ('transcript.corrected.json', 'subtitles.srt')):
                raise FileExistsError('校对产物已存在，请使用新目录保留上一版')
            write_json(args.output / 'transcript.corrected.json', result)
            (args.output / 'subtitles.srt').write_text(srt(result), encoding='utf-8')
            print(f'Corrected subtitles: {args.output / "subtitles.srt"}')
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, subprocess.CalledProcessError) as error:
        detail = error.stderr.decode(errors='replace') if isinstance(error, subprocess.CalledProcessError) and isinstance(error.stderr, bytes) else str(error)
        print(f'Error: {detail}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
