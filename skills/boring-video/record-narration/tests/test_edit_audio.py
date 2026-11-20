import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import wave

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/edit_audio.py'
spec = importlib.util.spec_from_file_location('edit_audio', SCRIPT)
e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)

class EditTests(unittest.TestCase):
    def test_ranges_and_source_to_output_mapping(self):
        cuts = [{'start': 1., 'end': 2., 'reason': 'abandoned attempt'}]
        kept = e.keep_ranges(cuts, 5.)
        self.assertEqual(kept, [
            {'source_start': 0., 'source_end': 1., 'output_start': 0., 'output_end': 1.},
            {'source_start': 2., 'source_end': 5., 'output_start': 1., 'output_end': 4.}])
    def test_invalid_edits_rejected(self):
        for cuts in [[{'start': 2, 'end': 1}], [{'start': -1, 'end': 1}],
                     [{'start': 0, 'end': 5}], [{'start': 4, 'end': 6}],
                     [{'start': 1, 'end': float('nan')}],
                     [{'start': 1, 'end': 3}, {'start': 2, 'end': 4}]]:
            with self.subTest(cuts=cuts), self.assertRaises(ValueError):
                e.keep_ranges(cuts, 5.)
    @unittest.skipUnless(shutil.which('ffmpeg'), 'FFmpeg required')
    def test_real_edit_preserves_source_and_exact_duration(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'source.wav'
            subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'sine=frequency=440:duration=3', '-ar', '48000', '-ac', '1', str(source)], check=True)
            before = source.read_bytes()
            result = e.edit(source, [{'start': .5, 'end': 1.5, 'reason': 'retake'}], root/'edited')
            with wave.open(str(result)) as audio:
                self.assertEqual(audio.getnframes(), 96000)
            self.assertEqual(before, source.read_bytes())
            report = json.loads((root/'edited/edit-report.json').read_text())
            self.assertEqual(report['duration_after'], 2.)
            self.assertEqual(report['source_sha256'], hashlib.sha256(before).hexdigest())
            self.assertEqual(len(report['kept']), 2)
            with self.assertRaises(FileExistsError): e.edit(source, [], root/'edited')
    def test_missing_source_fails_without_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): e.edit(Path(tmp)/'missing.wav', [], Path(tmp)/'edited')
            self.assertFalse((Path(tmp)/'edited').exists())

if __name__ == '__main__': unittest.main()
