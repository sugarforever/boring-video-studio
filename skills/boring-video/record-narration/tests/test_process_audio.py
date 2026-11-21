import array
import importlib.util
import math
import wave
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'process_audio.py'
spec = importlib.util.spec_from_file_location('process_audio', SCRIPT)
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)

class ProcessingTests(unittest.TestCase):
    def test_timestamp_rounding_and_hours(self):
        self.assertEqual(p.timestamp(59.9996), '00:01:00,000')
        self.assertEqual(p.timestamp(3661.123), '01:01:01,123')
    def test_correct_preserves_timing_and_recognition(self):
        data = {'segments': [{'id': 1, 'start': 0.2, 'end': 1.5, 'text': '扣德克斯'}]}
        corrected = p.correct(data, [{'id': 1, 'text': 'Codex'}])
        self.assertEqual(corrected['segments'][0], {'id': 1, 'start': 0.2, 'end': 1.5, 'text': 'Codex'})
        self.assertEqual(data['segments'][0]['text'], '扣德克斯')
        with self.assertRaises(ValueError): p.correct(data, [{'id': 2, 'text': '新增'}])
        with self.assertRaises(ValueError): p.correct(data, [{'id': 1, 'text': ''}])
        with self.assertRaises(ValueError): p.correct(data, [{'id': 1, 'text': 'a'}, {'id': 1, 'text': 'b'}])
    def test_invalid_subtitle_timing(self):
        with self.assertRaises(ValueError): p.srt({'segments': [{'id': 1, 'start': 2, 'end': 1, 'text': '错'}]})
    def words(self, text, pause_after=None):
        result, clock = [], 0
        for i, char in enumerate(text):
            result.append({'start': clock, 'end': clock + .16, 'word': char})
            clock += .18 + (.6 if i == pause_after else 0)
        return result
    def test_subtitles_keep_chinese_words_and_short_lines(self):
        text = '现在把它们放进同一个流程，然后生成字幕，再参照原稿检查识别错误。'
        cues = p.word_cues(self.words(text), max_chars=12)
        self.assertEqual(''.join(c['text'] for c in cues), text)
        self.assertTrue(all(len(c['text']) <= 12 for c in cues))
        self.assertFalse(any(c['text'].endswith('流') or c['text'].startswith('程') for c in cues))
        self.assertTrue(all(c['end'] - c['start'] <= 5 for c in cues))
    def test_subtitles_use_pause_and_punctuation(self):
        text = '准备好了就开始录音完成以后生成字幕。'
        words = self.words(text, pause_after=8)
        cues = p.word_cues(words)
        self.assertEqual(cues[0]['text'], text[:9])
        self.assertEqual(cues[1]['start'], words[9]['start'])
        text = '打开页面，就能看到口播稿。准备好了，点击开始录音。'
        cues = p.word_cues(self.words(text))
        self.assertTrue(any(c['text'].endswith('。') for c in cues[:-1]))
        self.assertEqual(''.join(c['text'] for c in cues), text)
    def test_subtitles_keep_english_words(self):
        words = [{'word': 'Hello', 'start': 0, 'end': .3},
                 {'word': ' trans', 'start': .3, 'end': .6},
                 {'word': 'cription', 'start': .6, 'end': 1.0},
                 {'word': ' works.', 'start': 1, 'end': 1.5}]
        cues = p.word_cues(words, max_chars=14)
        self.assertEqual([c['text'] for c in cues], ['Hello', 'transcription', 'works.'])
    def test_delivery_resegments_corrected_text_and_preserves_evidence(self):
        raw = self.words('整理音量，声称字幕，再称照原稿检查识别错误。')
        data = {'words': raw, 'segments': [{'id': 1, 'start': 0, 'end': raw[-1]['end'],
                'text': '整理音量，生成字幕，再参照原稿检查识别错误。'}]}
        result = p.delivery(data, max_chars=12)
        self.assertEqual(''.join(c['text'] for c in result['segments']), data['segments'][0]['text'])
        self.assertEqual(result['words'], raw)
        self.assertTrue(all(len(c['text']) <= 12 for c in result['segments']))
        self.assertEqual(result['source_segments'], data['segments'])
        p.srt(result)
    def test_added_punctuation_keeps_sentence_boundary_available(self):
        words = self.words('打开页面就能看到口播稿准备好了点击开始录音')
        data = {'words': words, 'segments': [{'id': 1, 'start': 0, 'end': words[-1]['end'],
                'text': '打开页面，就能看到口播稿。准备好了，点击开始录音。'}]}
        result = p.delivery(data)
        self.assertEqual([c['text'] for c in result['segments']],
                         ['打开页面，就能看到口播稿。', '准备好了，点击开始录音。'])
        self.assertEqual(result['segments'][1]['start'], words[11]['start'])
    def test_subtitle_limits_require_real_timing(self):
        with self.assertRaises(ValueError):
            p.word_cues([{'word': '这是一段没有内部时间的超长识别结果', 'start': 0, 'end': 8}], max_chars=10)
        with self.assertRaises(ValueError): p.word_cues(self.words('测试'), max_chars=0)
        with self.assertRaises(ValueError): p.word_cues([{'word': '字', 'start': 0, 'end': 0}])
        with self.assertRaises(ValueError): p.delivery({'words': [], 'segments': [{'text': '测试'}]})
    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFmpeg required')
    def test_real_normalization_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'source.wav'
            subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'sine=frequency=440:duration=1', str(source)], check=True)
            before = source.read_bytes()
            output = p.prepare(source, root / 'processed')
            metadata = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-of', 'json', str(output)]))
            self.assertEqual(metadata['streams'][0]['sample_rate'], '48000')
            self.assertEqual(metadata['streams'][0]['channels'], 1)
            self.assertEqual(before, source.read_bytes())
            with self.assertRaises(FileExistsError): p.prepare(source, root / 'processed')
    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFmpeg required')
    def test_normalization_preserves_quiet_to_speech_ratio(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'quiet-start.wav'
            samples = array.array('h', (round((.0008 if i < 3*48000 else .2) * 32767 * math.sin(2*math.pi*440*i/48000)) for i in range(8*48000)))
            with wave.open(str(source), 'wb') as audio:
                audio.setparams((1,2,48000,len(samples),'NONE','not compressed'))
                audio.writeframes(samples.tobytes())
            output = p.prepare(source, root/'processed')
            with wave.open(str(output)) as audio:
                result = array.array('h'); result.frombytes(audio.readframes(audio.getnframes()))
            def rms(values): return math.sqrt(sum(x*x for x in values)/len(values))
            gain_start = rms(result[12000:36000])/rms(samples[12000:36000])
            gain_speech = rms(result[4*48000:5*48000])/rms(samples[4*48000:5*48000])
            self.assertLess(abs(20*math.log10(gain_start/gain_speech)), .6)
            report = json.loads((root/'processed/processing.json').read_text())
            self.assertEqual(report['normalization']['engine'], 'ffmpeg-normalize')
            self.assertEqual(report['normalization']['mode'], 'linear')

    def test_srt_content(self):
        self.assertEqual(p.srt({'segments': [{'id': 1, 'start': 0, 'end': 1, 'text': '你好'}]}), '1\n00:00:00,000 --> 00:00:01,000\n你好\n')

if __name__ == '__main__': unittest.main()
