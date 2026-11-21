import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import unittest
import urllib.request
import urllib.error

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'recorder.py'
spec = importlib.util.spec_from_file_location('recorder', SCRIPT)
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)

class RecorderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        script = self.root / 'draft.txt'
        script.write_text('第一段。\n\n第二段。', encoding='utf-8')
        self.store = r.Store(self.root / 'session', script)
        self.server = r.make_server(self.store, port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f'http://127.0.0.1:{self.server.server_port}'
    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.tmp.cleanup()
    def call(self, path, data=None, token=True, origin=None):
        headers = {'X-Recorder-Token': self.server.token} if token else {}
        if origin: headers['Origin'] = origin
        if isinstance(data, dict):
            data = json.dumps(data).encode()
            headers['Content-Type'] = 'application/json'
        req = urllib.request.Request(self.url + path, data=data, headers=headers)
        try:
            with urllib.request.urlopen(req) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            error.close()
            raise
    def test_capture_settings_preserved(self):
        settings = {'sampleRate': 48000, 'autoGainControl': False, 'deviceId': 'not needed'}
        take = self.call('/api/takes', {'mime': 'audio/webm', 'capture': settings})
        self.assertEqual(take['capture'], {'sampleRate': 48000, 'autoGainControl': False})
        self.assertEqual(self.call('/api/state')['takes'][0]['capture'], take['capture'])

    def test_snapshot_and_resume(self):
        (self.root / 'draft.txt').write_text('changed')
        again = r.Store(self.root / 'session', self.root / 'draft.txt')
        self.assertEqual(again.state()['script'], '第一段。\n\n第二段。')
    def test_chunks_recovery_and_handoff(self):
        take = self.call('/api/takes', {'mime': 'audio/webm;codecs=opus'})['id']
        self.call(f'/api/takes/{take}/chunks/0', b'first')
        self.call(f'/api/takes/{take}/chunks/0', b'first')
        with self.assertRaises(urllib.error.HTTPError) as cm:
            self.call(f'/api/takes/{take}/chunks/0', b'other')
        self.assertEqual(cm.exception.code, 409)
        self.call(f'/api/takes/{take}/chunks/1', b'second')
        self.call(f'/api/takes/{take}/finalize', {'chunks': 2})
        self.call('/api/ready', {'take': take})
        state = self.call('/api/state')
        self.assertEqual(state['status'], 'ready')
        self.assertEqual((self.root / 'session' / state['audio']).read_bytes(), b'firstsecond')
        self.assertTrue((self.root / 'session' / 'handoff.json').exists())
    def test_incomplete_and_missing_chunks_never_ready(self):
        take = self.call('/api/takes', {'mime': 'audio/mp4'})['id']
        for path, data in [(f'/api/takes/{take}/finalize', {'chunks': 1}), ('/api/ready', {'take': take})]:
            with self.assertRaises(urllib.error.HTTPError): self.call(path, data)
    def test_auth_and_origin(self):
        for kwargs in [{'token': False}, {'origin': 'https://evil.example'}]:
            with self.assertRaises(urllib.error.HTTPError) as cm:
                self.call('/api/takes', {'mime': 'audio/webm'}, **kwargs)
            self.assertEqual(cm.exception.code, 403)
    def test_invalid_paths_and_mime(self):
        for path, data in [('/api/takes', {'mime': '../../bad'}), ('/api/takes/unknown/chunks/0', b'a')]:
            with self.assertRaises(urllib.error.HTTPError): self.call(path, data)
    def test_new_take_invalidates_handoff(self):
        take = self.call('/api/takes', {'mime': 'audio/webm'})['id']
        self.call(f'/api/takes/{take}/chunks/0', b'a')
        self.call(f'/api/takes/{take}/finalize', {'chunks': 1})
        self.call('/api/ready', {'take': take})
        self.call('/api/takes', {'mime': 'audio/webm'})
        self.assertEqual(self.call('/api/state')['status'], 'recording')
        self.assertFalse((self.root / 'session' / 'handoff.json').exists())

if __name__ == '__main__': unittest.main()
