import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

EXPORT = Path(__file__).resolve().parents[1] / 'scripts/export_camera.py'

@unittest.skipUnless(shutil.which('ffmpeg'), 'FFmpeg required')
class CameraExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.video = self.root/'camera.mp4'
        self.audio = self.root/'reviewed.wav'
        self.background = self.root/'content.mp4'
        self.run_ffmpeg('-f', 'lavfi', '-i', 'color=red:s=160x120:r=30:d=2', '-f', 'lavfi', '-i', 'color=blue:s=160x120:r=30:d=2', '-filter_complex', '[0:v][1:v]concat=n=2:v=1:a=0[v]', '-map', '[v]', str(self.video))
        self.run_ffmpeg('-f', 'lavfi', '-i', 'sine=frequency=440:duration=2', '-ar', '48000', str(self.audio))
        self.run_ffmpeg('-f', 'lavfi', '-i', 'color=green:s=320x240:r=30:d=2', str(self.background))
        self.report = self.root/'edit-report.json'
        self.report.write_text(json.dumps({'duration_before': 4, 'duration_after': 2, 'cuts': [{'start': .5, 'end': 2.5}]}))

    def run_ffmpeg(self, *args):
        return subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', *args], check=True, capture_output=True)

    def export(self, *args):
        return subprocess.run(['python3', str(EXPORT), '--video', str(self.video), '--audio', str(self.audio), '--edit-report', str(self.report), '--output', str(self.root/'out.mp4'), *args], capture_output=True, text=True)

    def pixel(self, time, x=0, y=0):
        result = self.run_ffmpeg('-ss', str(time), '-i', str(self.root/'out.mp4'), '-vf', f'crop=2:2:{x}:{y},scale=1:1', '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-')
        return tuple(result.stdout)

    def test_camera_uses_audio_cut_times_and_reviewed_audio(self):
        before = self.video.read_bytes()
        result = self.export()
        self.assertEqual(result.returncode, 0, result.stderr)
        red = self.pixel(.25)
        blue = self.pixel(.75)
        self.assertGreater(red[0], 200)
        self.assertGreater(blue[2], 200)
        probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(self.root/'out.mp4')]))
        self.assertEqual(sorted(s['codec_type'] for s in probe['streams']), ['audio', 'video'])
        self.assertAlmostEqual(float(probe['format']['duration']), 2, delta=.05)
        self.assertEqual(self.video.read_bytes(), before)
        self.assertNotEqual(self.export().returncode, 0)

    def test_many_cuts_do_not_accumulate_frame_rounding_drift(self):
        self.video.unlink()
        self.audio.unlink()
        self.run_ffmpeg('-f', 'lavfi', '-i', 'color=red:s=160x120:r=30:d=8', '-f', 'lavfi', '-i', 'color=blue:s=160x120:r=30:d=2', '-filter_complex', '[0:v][1:v]concat=n=2:v=1:a=0[v]', '-map', '[v]', str(self.video))
        self.run_ffmpeg('-f', 'lavfi', '-i', 'sine=frequency=440:duration=7', str(self.audio))
        self.report.write_text(json.dumps({'duration_before': 10, 'duration_after': 7, 'cuts': [{'start': i*.4+.05, 'end': i*.4+.2} for i in range(20)]}))
        result = self.export()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertGreater(self.pixel(4.9)[0], 200)
        self.assertGreater(self.pixel(5.05)[2], 200)

    def test_camera_preserves_delayed_video_start_against_original_audio(self):
        delayed = self.root/'delayed.mp4'
        self.run_ffmpeg('-itsoffset', '0.3', '-i', str(self.video), '-f', 'lavfi', '-i', 'sine=frequency=440:duration=4.3', '-map', '0:v', '-map', '1:a', '-c:v', 'copy', str(delayed))
        self.video = delayed
        self.audio.unlink()
        self.run_ffmpeg('-f', 'lavfi', '-i', 'sine=frequency=440:duration=4.3', str(self.audio))
        self.report.write_text(json.dumps({'duration_before': 4.3, 'duration_after': 4.3, 'cuts': []}))
        result = self.export()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertGreater(self.pixel(2.1)[0], 200)
        self.assertGreater(self.pixel(2.4)[2], 200)

    def test_picture_in_picture_corner_and_background(self):
        result = self.export('--background', str(self.background), '--corner', 'bottom-left')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertGreater(self.pixel(.25, 30, 170)[0], 200)
        green = self.pixel(.25, 200, 50)
        self.assertGreater(green[1], 100)
        self.assertLess(green[0], 10)

    def test_portrait_camera_and_vertical_margin_must_fit_content(self):
        self.video.unlink()
        self.run_ffmpeg('-f', 'lavfi', '-i', 'color=red:s=120x360:r=30:d=4', str(self.video))
        result = self.export('--background', str(self.background), '--width', '.5')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root/'out.mp4').exists())
        result = self.export('--background', str(self.background), '--margin', '120')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root/'out.mp4').exists())

    def test_mismatch_or_invalid_ranges_never_publish(self):
        for report in [
            {'duration_before': 4, 'duration_after': 3, 'cuts': []},
            {'duration_before': 4, 'duration_after': 2, 'cuts': [{'start': 2, 'end': 1}]},
            {'duration_before': 8, 'duration_after': 2, 'cuts': [{'start': 1, 'end': 7}]},
        ]:
            self.report.write_text(json.dumps(report))
            result = self.export()
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((self.root/'out.mp4').exists())

if __name__ == '__main__': unittest.main()
