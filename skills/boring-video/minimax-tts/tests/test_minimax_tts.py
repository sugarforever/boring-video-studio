"""Exercise the CLI against a local substitute for the paid MiniMax API."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/minimax_tts.py'


class MiniMaxTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.requests = []
        self.api_http_status = 200
        self.subtitle_http_status = 200
        self.omit_subtitle = False
        self.redirect = False
        self.reply = {'base_resp': {'status_code': 0, 'status_msg': 'success'},
                      'trace_id': 'test-trace', 'data': {'audio': '494433', 'status': 2}}
        self.cues = [{'text': '你好。', 'time_begin': 125, 'time_end': 1234},
                     {'text': '世界。', 'time_begin': 1500, 'time_end': 2500}]
        case = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                case.requests.append((self.path, self.headers.get('Authorization'), body))
                reply = dict(case.reply)
                if self.path == '/v1/get_voice':
                    reply = {'base_resp': {'status_code': 0},
                             'system_voice': [{'voice_id': 'test-voice'}]}
                elif reply.get('data') and not case.omit_subtitle:
                    reply['data'] = dict(reply['data'], subtitle_file=case.base + '/subtitles')
                self.send_response(302 if case.redirect else case.api_http_status)
                if case.redirect:
                    self.send_header('Location', case.base + '/redirect-target')
                self.end_headers()
                self.wfile.write(json.dumps(reply).encode())

            def do_GET(self):
                case.requests.append((self.path, self.headers.get('Authorization'), None))
                self.send_response(case.subtitle_http_status)
                self.end_headers()
                self.wfile.write(json.dumps(case.cues).encode())

        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.base = 'http://127.0.0.1:' + str(self.server.server_port)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop_server)
        self.text = self.root / 'narration.txt'
        self.text.write_text('你好。世界。', encoding='utf-8')

    def stop_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def run_cli(self, *args, key='test-secret'):
        env = dict(os.environ, MINIMAX_API_BASE=self.base, MINIMAX_API_KEY=key)
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                              env=env, capture_output=True, text=True)

    def synthesize(self, **kwargs):
        return self.run_cli('synthesize', self.text, self.root / 'out',
                            '--voice-id', 'test-voice', '--speed', '0.9', **kwargs)

    def test_synthesis_delivers_audio_and_millisecond_srt(self):
        result = self.synthesize()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.root / 'out/narration-full.mp3').read_bytes(), b'ID3')
        self.assertEqual((self.root / 'out/narration.srt').read_text(),
                         '1\n00:00:00,125 --> 00:00:01,234\n你好。\n\n'
                         '2\n00:00:01,500 --> 00:00:02,500\n世界。\n\n')
        path, auth, body = self.requests[0]
        self.assertEqual(path, '/v1/t2a_v2')
        self.assertEqual(auth, 'Bearer test-secret')
        self.assertEqual(body['text'], '你好。世界。')
        self.assertEqual(body['voice_setting']['speed'], 0.9)
        self.assertTrue(body['subtitle_enable'])
        self.assertEqual(body['subtitle_type'], 'sentence')
        self.assertFalse(body['stream'])
        self.assertEqual(self.requests[1][1], None, 'Download must not receive API key')
        self.assertNotIn('test-secret', ''.join(p.read_text(errors='replace')
                         for p in (self.root / 'out').iterdir()))

    def test_lists_account_voices(self):
        result = self.run_cli('voices', '--type', 'voice_cloning')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['system_voice'][0]['voice_id'], 'test-voice')
        self.assertEqual(self.requests[0][2], {'voice_type': 'voice_cloning'})

    def test_api_failure_never_reports_success_or_writes_audio(self):
        self.reply = {'base_resp': {'status_code': 1004, 'status_msg': 'authentication failed'},
                      'data': None}
        result = self.synthesize()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('1004', result.stderr)
        self.assertFalse((self.root / 'out/narration-full.mp3').exists())

    def test_rejects_invalid_text_before_paid_call(self):
        for text in ('  ', '字' * 10000):
            with self.subTest(length=len(text)):
                self.text.write_text(text)
                self.assertNotEqual(self.synthesize().returncode, 0)
        self.assertEqual(self.requests, [])

    def test_missing_key_and_invalid_speed_do_not_call_api(self):
        self.assertNotEqual(self.synthesize(key='').returncode, 0)
        result = self.run_cli('synthesize', self.text, self.root / 'out',
                              '--voice-id', 'test-voice', '--speed', 'nan')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.requests, [])

    def test_existing_output_is_preserved_without_paid_call(self):
        out = self.root / 'out'
        out.mkdir()
        (out / 'narration-full.mp3').write_bytes(b'original')
        self.assertNotEqual(self.synthesize().returncode, 0)
        self.assertEqual(self.requests, [])
        self.assertEqual((out / 'narration-full.mp3').read_bytes(), b'original')

    def test_bad_subtitles_preserve_audio_and_raw_data_for_recovery(self):
        self.cues = [{'text': '错', 'time_begin': 100, 'time_end': 50}]
        result = self.synthesize()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.root / 'out/narration-full.mp3').read_bytes(), b'ID3')
        self.assertTrue((self.root / 'out/subtitles.json').exists())
        self.assertFalse((self.root / 'out/narration.srt').exists())

    def test_unwritable_output_fails_before_paid_call(self):
        out = self.root / 'out'
        out.mkdir()
        out.chmod(0o500)
        try:
            self.assertNotEqual(self.synthesize().returncode, 0)
            self.assertEqual(self.requests, [])
        finally:
            out.chmod(0o700)

    def test_http_failure_is_not_retried(self):
        self.api_http_status = 429
        result = self.synthesize()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('429', result.stderr)
        self.assertEqual(len(self.requests), 1)

    def test_authenticated_redirect_is_not_followed(self):
        self.redirect = True
        self.assertNotEqual(self.synthesize().returncode, 0)
        self.assertEqual(len(self.requests), 1)

    def test_subtitle_fetch_failure_keeps_audio_and_can_be_recovered(self):
        self.subtitle_http_status = 503
        self.assertNotEqual(self.synthesize().returncode, 0)
        self.assertEqual((self.root / 'out/narration-full.mp3').read_bytes(), b'ID3')
        response = json.loads((self.root / 'out/response.json').read_text())
        self.subtitle_http_status = 200
        result = self.run_cli('subtitles', '--url', response['data']['subtitle_file'],
                              '--out-dir', self.root / 'out', key='')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(sum(path == '/v1/t2a_v2' for path, _, _ in self.requests), 1)
        self.assertTrue((self.root / 'out/narration.srt').exists())

    def test_missing_subtitle_url_keeps_audio_and_metadata(self):
        self.omit_subtitle = True
        self.assertNotEqual(self.synthesize().returncode, 0)
        self.assertEqual((self.root / 'out/narration-full.mp3').read_bytes(), b'ID3')
        self.assertTrue((self.root / 'out/response.json').exists())

    def test_missing_or_malformed_audio_fails_with_metadata(self):
        for audio in (None, '', 'not-hex'):
            with self.subTest(audio=audio):
                self.reply['data']['audio'] = audio
                self.assertNotEqual(self.synthesize().returncode, 0)
                self.assertTrue((self.root / 'out/response.json').exists())
                self.assertFalse((self.root / 'out/narration-full.mp3').exists())
                (self.root / 'out/response.json').unlink()

    def test_subtitle_download_can_be_retried_without_resynthesis(self):
        result = self.run_cli('subtitles', '--url', self.base + '/subtitles',
                              '--out-dir', self.root / 'out', key='')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.root / 'out/narration.srt').exists())
        self.assertEqual(len(self.requests), 1)
        self.assertIsNone(self.requests[0][1])


if __name__ == '__main__':
    unittest.main()
