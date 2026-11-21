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
    def test_word_cues_follow_actual_timestamps(self):
        words = [{'start': i, 'end': i + .5, 'word': '测试'} for i in range(10)]
        cues = p.word_cues(words, max_chars=6)
        self.assertEqual(len(cues), 4)
        self.assertEqual(cues[1]['start'], 3)
        self.assertEqual(cues[-1]['end'], 9.5)
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
