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

DEFAULT_MAX_CHARS = 16
MAX_READING_CPS = 9


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


def word_cues(words, max_chars=DEFAULT_MAX_CHARS, max_duration=5.0, pause_gap=.45, segment_ends=()):
    """Regroup at lexical/ASR boundaries, prioritizing punctuation and pauses."""
    if (not isinstance(max_chars, int) or max_chars < 1 or
            not math.isfinite(max_duration) or max_duration <= 0 or
            not math.isfinite(pause_gap) or pause_gap <= 0):
        raise ValueError('Subtitle limits must be positive')
    cleaned, previous_end = [], 0.0
    for index, original in enumerate(words):
        word = dict(original)
        word['word'] = ' '.join(word['word'].splitlines())
        start, end = float(word['start']), float(word['end'])
        if not math.isfinite(start) or not math.isfinite(end) or start < 0:
            raise ValueError('Invalid word timestamp')
        word['start'], word['end'] = max(previous_end, start), end
        if not word['word'].strip():
            continue
        if end <= word['start']:
            raise ValueError('识别词缺少有效时长；需要重新对齐，避免字幕漏字')
        word['source_word_indices'] = word.get('source_word_indices', [index])
        cleaned.append(word)
        previous_end = end
    if not cleaned:
        return []
    text = ''.join(w['word'] for w in cleaned)
    try:
        import jieba
    except ImportError as error:
        raise RuntimeError('字幕分词需要 jieba：安装此 Skill 的 requirements.txt') from error
    jieba.setLogLevel(30)
    lexical_ends = {end for _, _, end in jieba.tokenize(text, HMM=False)}
    # ASR "words" can be single Chinese characters or partial English words.
    # Only boundaries shared by lexical tokens and timed units can be used.
    atoms, group, offset = [], [], 0
    for i, word in enumerate(cleaned):
        group.append(word)
        offset += len(word['word'])
        following = text[offset:].lstrip()
        safe = offset in lexical_ends and not (following and following[0] in '，。！？；：、,.!?;:）】》”’')
        if safe or i == len(cleaned) - 1:
            atoms.append({'word': ''.join(w['word'] for w in group), 'start': group[0]['start'],
                          'end': group[-1]['end'], 'source_word_indices': sorted({j for w in group for j in w['source_word_indices']})})
            group = []
    # Preserve source clauses where their boundary is also a complete lexical unit.
    from bisect import bisect_right
    buckets = [bisect_right(segment_ends, (a["start"] + a["end"]) / 2) for a in atoms]
    n = len(atoms)
    costs, choices = [float('inf')] * (n + 1), [None] * n
    costs[n] = 0
    target = max_chars * .75
    for i in range(n - 1, -1, -1):
        combined = ''
        for j in range(i, n):
            if j > i:
                prev = atoms[j - 1]['word'].rstrip()
                gap = atoms[j]['start'] - atoms[j - 1]['end']
                if buckets[j] != buckets[j - 1] or gap >= pause_gap or prev.endswith(('。', '！', '？', '!', '?', '；', ';')):
                    break
            combined += atoms[j]['word']
            length = len(combined.strip())
            duration = atoms[j]['end'] - atoms[i]['start']
            if length > max_chars or duration > max_duration:
                break
            ending = combined.rstrip()
            gap = atoms[j + 1]['start'] - atoms[j]['end'] if j + 1 < n else 0
            natural = (j == n - 1 or buckets[j + 1] != buckets[j] or gap >= pause_gap or ending.endswith(('。', '！', '？', '!', '?', '；', ';')))
            penalty = 0 if natural else 1 if ending.endswith(('，', ',', '：', ':', '、')) else 4
            # Balance clauses so a hard limit does not strand a tiny final cue.
            cost = 2 + ((length - target) / max(1, target)) ** 2 + penalty
            if length < min(4, max_chars) and not natural:
                cost += 3
            if cost + costs[j + 1] < costs[i]:
                costs[i], choices[i] = cost + costs[j + 1], j + 1
    if choices[0] is None:
        raise ValueError('无法在完整词和已有时间边界内满足字幕长度/时长限制；需要更细的词时间或人工对齐')
    cues, i = [], 0
    while i < n:
        end = choices[i]
        group = atoms[i:end]
        cues.append({'id': len(cues) + 1, 'start': group[0]['start'], 'end': group[-1]['end'],
                     'text': ''.join(w['word'] for w in group).strip(),
                     'source_word_indices': sorted({j for w in group for j in w['source_word_indices']})})
        i = end
    return cues


def delivery(data, max_chars=DEFAULT_MAX_CHARS, max_duration=5.0, pause_gap=.45):
    """Project reviewed text onto raw timing without inventing intra-word times."""
    from difflib import SequenceMatcher
    import re
    words = data.get('words', [])
    if not words:
        raise ValueError('重新分段需要原始 words 时间；请保留原始转写或重新对齐')
    raw = ''.join(w['word'] for w in words)
    owners = [i for i, word in enumerate(words) for _ in word['word']]
    reviewed, previous_cue = '', None
    for cue in data['segments']:
        text = ' '.join(cue['text'].splitlines()).strip()
        if reviewed and text and re.match(r'[A-Za-z0-9]', text) and re.search(r'[A-Za-z0-9]$', reviewed):
            left = [i for i, w in enumerate(words) if w['start'] < previous_cue['end'] and w['end'] > previous_cue['start']]
            right = [i for i, w in enumerate(words) if w['start'] < cue['end'] and w['end'] > cue['start']]
            if not left or not right or right[0] not in (left[-1], left[-1] + 1):
                raise ValueError('英文跨条目词界无法确定；请依据原始词时间或音频确认后再导出')
            if right[0] != left[-1] and (words[left[-1]]['word'][-1:].isspace() or words[right[0]]['word'][:1].isspace()):
                reviewed += ' '
        reviewed += text
        previous_cue = cue
    projected = []
    for op, a, b, c, d in SequenceMatcher(None, raw, reviewed, autojunk=False).get_opcodes():
        if op == 'delete':
            continue
        if op == 'equal':
            projected.extend((char, [owners[a + k]]) for k, char in enumerate(reviewed[c:d]))
        else:
            # Replacements/insertions share the complete neighboring timed span;
            # treating that span atomically avoids fabricated character timing.
            if op == 'insert' and not any(char.isalnum() for char in reviewed[c:d]):
                # Added punctuation belongs to the preceding spoken word, so
                # its clause boundary remains available without new timing.
                ids = owners[max(0, a - 1):max(1, a)]
            else:
                ids = sorted(set(owners[a:b] or owners[max(0, a - 1):min(len(owners), a + 1)]))
            if not ids:
                raise ValueError('校对文字无法映射回原始词时间')
            projected.extend((char, ids) for char in reviewed[c:d])
    aligned, group_text, group_ids = [], '', set()
    for char, ids in projected:
        if group_ids and min(ids) > max(group_ids):
            aligned.append({'word': group_text, 'start': words[min(group_ids)]['start'],
                            'end': words[max(group_ids)]['end'], 'source_word_indices': sorted(group_ids)})
            group_text, group_ids = '', set()
        group_text += char
        group_ids.update(ids)
    if group_text:
        aligned.append({'word': group_text, 'start': words[min(group_ids)]['start'],
                        'end': words[max(group_ids)]['end'], 'source_word_indices': sorted(group_ids)})
    result = copy.deepcopy(data)
    result['segmentation'] = 'delivery-layout'
    result['source_segments'] = copy.deepcopy(data['segments'])
    boundaries = sorted({s['end'] for s in data['segments'][:-1]})
    result['segments'] = word_cues(aligned, max_chars, max_duration, pause_gap, boundaries)
    if not result['segments']:
        raise ValueError('没有可导出的字幕')
    if re.sub(r'\s+', '', ''.join(cue['text'] for cue in result['segments'])) != re.sub(r'\s+', '', reviewed):
        raise ValueError('重新分段改变了校对正文，停止交付')
    for cue in result['segments']:
        cue['source_cue_ids'] = [s['id'] for s in data['segments'] if s['start'] < cue['end'] and s['end'] > cue['start']]
    result['subtitle_layout'] = {'max_lines': 1, 'max_chars': max_chars, 'max_duration': max_duration,
                                 'pause_gap': pause_gap, 'tokenizer': 'jieba', 'timing': 'raw-word-spans', 'preserve_source_boundaries': True}
    srt(result)
    issues = []
    for cue in result['segments']:
        cps = len(cue['text']) / (cue['end'] - cue['start'])
        if cps > MAX_READING_CPS:
            issues.append({'kind': 'reading-speed', 'cue_id': cue['id'],
                           'start': cue['start'], 'end': cue['end'], 'cps': round(cps, 3)})
    result['subtitle_review'] = {'max_cps': MAX_READING_CPS,
        'counting': 'unicode-codepoints-including-spaces-and-punctuation',
        'status': 'needs-review' if issues else 'checks-passed', 'issues': issues}
    return result


def print_subtitle_review(data):
    review = data['subtitle_review']
    print(f"Reading-speed check: {len(review['issues'])} cue(s) above {review['max_cps']} chars/s; "
          f"{review['status']} (see subtitle_review in transcript JSON)", flush=True)


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


def transcribe(audio, output, model='small', language='zh', max_chars=DEFAULT_MAX_CHARS, max_duration=5.0, pause_gap=.45):
    try:
        from faster_whisper import WhisperModel
    except ImportError as error:
        raise RuntimeError('缺少本地转写依赖。使用 Python 3.11/3.12 虚拟环境安装：pip install "faster-whisper>=1.1,<2"') from error
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    for name in ('transcript.raw.json', 'subtitles.raw.srt', 'transcript.initial.json', 'subtitles.initial.srt'):
        if (output / name).exists():
            raise FileExistsError(f'{name} 已存在，请使用新目录保留旧转写')
    print(f'Loading local Whisper model: {model} (first use may download model weights)', flush=True)
    engine = WhisperModel(model, device='cpu', compute_type='int8')
    segments, info = engine.transcribe(str(audio), language=None if language == 'auto' else language,
                                       word_timestamps=True, vad_filter=True)
    words, raw_segments = [], []
    for segment in segments:
        for word in segment.words or []:
            words.append({'start': word.start, 'end': word.end, 'word': word.word, 'probability': word.probability})
        raw_segments.append({'id': len(raw_segments) + 1, 'start': segment.start,
                             'end': segment.end, 'text': segment.text.strip()})
        print(f'Transcribed through {segment.end:.1f}s', flush=True)
    data = {'audio': str(Path(audio).resolve()), 'language': info.language, 'model': model,
            'words': words, 'segments': raw_segments, 'segmentation': 'asr-original'}
    write_json(output / 'transcript.raw.json', data)
    if not data['segments']:
        raise ValueError('未识别出语音；请试听录音并检查麦克风或语言设置')
    subtitle = srt(data)
    (output / 'subtitles.raw.srt').write_text(subtitle, encoding='utf-8')
    initial = delivery(data, max_chars, max_duration, pause_gap)
    initial['segmentation'] = 'initial-layout'
    write_json(output / 'transcript.initial.json', initial)
    (output / 'subtitles.initial.srt').write_text(srt(initial), encoding='utf-8')
    print_subtitle_review(initial)
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
    layout = commands.add_parser('delivery', help='Regroup reviewed text at pauses and lexical boundaries', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    layout.add_argument('--transcript', type=Path, required=True)
    layout.add_argument('--output', type=Path, required=True)
    for command in (prep, tx, layout):
        command.add_argument('--max-chars', type=int, default=DEFAULT_MAX_CHARS, help='Maximum characters per cue, including punctuation')
        command.add_argument('--max-duration', type=float, default=5.0, help='Maximum cue duration in seconds')
        command.add_argument('--pause-gap', type=float, default=.45, help='Split at word gaps at least this many seconds')
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
                transcribe(target, args.output, args.model, args.language, args.max_chars, args.max_duration, args.pause_gap)
        elif args.command == 'transcribe':
            transcribe(args.audio, args.output, args.model, args.language, args.max_chars, args.max_duration, args.pause_gap)
        elif args.command == 'delivery':
            data = json.loads(args.transcript.read_text(encoding='utf-8'))
            result = delivery(data, args.max_chars, args.max_duration, args.pause_gap)
            args.output.mkdir(parents=True, exist_ok=True)
            if any((args.output / name).exists() for name in ('transcript.delivery.json', 'subtitles.srt')):
                raise FileExistsError('交付字幕已存在，请使用新输出目录')
            write_json(args.output / 'transcript.delivery.json', result)
            (args.output / 'subtitles.srt').write_text(srt(result), encoding='utf-8')
            print(f'Delivery subtitles: {args.output / "subtitles.srt"}')
            print_subtitle_review(result)
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
