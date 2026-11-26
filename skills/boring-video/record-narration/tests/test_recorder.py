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
        if path == '/api/takes' and isinstance(data, dict):
            data = {'script': self.store.state()['script'], **data}
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
    def test_relaunch_reuses_live_address_and_updates_draft(self):
        endpoint = self.store.root / 'recorder-server.json'
        endpoint.write_text(json.dumps({'port': self.server.server_port, 'token': self.server.token}))
        draft = self.root / 'draft.txt'
        draft.write_text('新版口播稿')
        original_port = self.server.server_port
        self.assertEqual(r.reuse_server(self.store.root, draft), self.url + '/#' + self.server.token)
        self.assertEqual(self.server.server_port, original_port)
        self.assertEqual(self.call('/api/state')['script'], '新版口播稿')
        endpoint.write_text(json.dumps({'port': original_port, 'token': 'wrong'}))
        with self.assertRaises(RuntimeError):
            r.reuse_server(self.store.root, draft)

    def test_revised_draft_keeps_old_take_script_and_handoff(self):
        original = self.store.state()['script']
        take = self.call('/api/takes', {'mime': 'audio/webm'})['id']
        with self.assertRaises(urllib.error.HTTPError):
            self.call('/api/script', {'text': '新版'})
        self.assertEqual(self.store.state()['script'], original)
        self.call(f'/api/takes/{take}/chunks/0', b'old')
        self.call(f'/api/takes/{take}/finalize', {'chunks': 1})
        self.call('/api/ready', {'take': take})
        self.call('/api/script', {'text': '新版'})
        self.assertFalse((self.store.root / 'handoff.json').exists())
        self.assertIsNone(self.store.state()['selected'])
        self.call('/api/ready', {'take': take})
        handoff = json.loads((self.store.root / 'handoff.json').read_text())
        self.assertEqual(Path(handoff['script']).read_text(), original)
        new_take = self.call('/api/takes', {'mime': 'audio/webm'})['id']
        self.assertEqual((self.store.root / 'takes' / new_take / 'script.txt').read_text(), '新版')
        self.assertEqual((self.store.root / 'takes' / take / 'original.webm').read_bytes(), b'old')

    def test_abandoned_empty_or_broken_take_allows_draft_revision(self):
        for broken in (False, True):
            with self.subTest(broken=broken):
                take = self.call('/api/takes', {'mime': 'audio/webm'})['id']
                if broken:
                    self.call(f'/api/takes/{take}/chunks/1', b'preserved')
                with self.assertRaises(urllib.error.HTTPError):
                    self.call('/api/script', {'text': f'blocked {broken}'})
                with self.assertRaises(urllib.error.HTTPError):
                    self.call(f'/api/takes/{take}/finalize', {'chunks': int(broken)})
                self.call(f'/api/takes/{take}/abandon', {})
                self.call('/api/script', {'text': f'new {broken}'})
                self.assertEqual(self.store.state()['script'], f'new {broken}')
                self.assertTrue(self.store.take(take)['abandoned'])
                if broken:
                    self.assertEqual((self.store.root / 'takes' / take / '000001.chunk').read_bytes(), b'preserved')
                self.assertTrue((self.store.root / 'takes' / take / 'script.txt').exists())
                for action, body in [('finalize', {'chunks': 1}), ('chunks/0', b'late'), ('abandon', {})]:
                    if action == 'abandon':
                        self.call(f'/api/takes/{take}/{action}', body)
                    else:
                        with self.assertRaises(urllib.error.HTTPError):
                            self.call(f'/api/takes/{take}/{action}', body)
                with self.assertRaises(urllib.error.HTTPError):
                    self.call('/api/ready', {'take': take})
        resumed = r.Store(self.store.root, self.root / 'draft.txt')
        resumed.update_script('restart and revise')
        self.assertTrue(all(t.get('abandoned') for t in resumed.data['takes']))

    def test_stale_display_cannot_create_take_after_draft_update(self):
        displayed = self.call('/api/state')['script']
        self.call('/api/script', {'text': '新的口播稿'})
        for stale in (displayed, None):
            with self.assertRaises(urllib.error.HTTPError) as error:
                self.call('/api/takes', {'mime': 'audio/webm', 'script': stale})
            self.assertEqual(error.exception.code, 409)
        self.assertEqual(self.store.state()['takes'], [])
        self.assertFalse((self.store.root / 'takes').exists())
        take = self.call('/api/takes', {'mime': 'audio/webm', 'script': '新的口播稿'})
        self.assertEqual((self.store.root / 'takes' / take['id'] / 'script.txt').read_text(), '新的口播稿')
        with self.assertRaises(urllib.error.HTTPError):
            self.call('/api/script', {'text': '录音期间又改稿'})

    def test_abandon_other_take_preserves_submitted_handoff(self):
        complete = self.call('/api/takes', {'mime': 'audio/webm'})['id']
        self.call(f'/api/takes/{complete}/chunks/0', b'audio')
        self.call(f'/api/takes/{complete}/finalize', {'chunks': 1})
        partial = self.call('/api/takes', {'mime': 'audio/webm'})['id']
        self.call('/api/ready', {'take': complete})
        handoff_path = self.store.root / 'handoff.json'
        original_handoff = handoff_path.read_bytes()
        for _ in range(2):
            self.call(f'/api/takes/{partial}/abandon', {})
            state = self.call('/api/state')
            handoff = json.loads(handoff_path.read_text())
            self.assertEqual(state['status'], 'ready')
            self.assertEqual(state['selected'], handoff['take'])
            self.assertEqual(state['selected'], complete)
            self.assertEqual(handoff_path.read_bytes(), original_handoff)
            self.assertTrue(Path(handoff['audio']).is_file())
            self.assertTrue(Path(handoff['script']).is_file())
        resumed = r.Store(self.store.root, self.root / 'draft.txt')
        self.assertEqual(resumed.state()['status'], 'ready')

    def test_camera_container_recovery_and_handoff(self):
        for mime, suffix in [('video/webm;codecs=vp8,opus', '.webm'), ('video/mp4', '.mp4')]:
            take = self.call('/api/takes', {'mime': mime, 'capture': {'width': 1280, 'height': 720, 'frameRate': 30, 'deviceId': 'private'}})
            tid = take['id']
            self.call(f'/api/takes/{tid}/chunks/0', b'camera-and-microphone')
            self.call(f'/api/takes/{tid}/finalize', {'chunks': 1})
            self.call('/api/ready', {'take': tid})
            handoff = json.loads((self.store.root / 'handoff.json').read_text())
            self.assertEqual(handoff['video'], handoff['audio'])
            self.assertEqual(Path(handoff['video']).suffix, suffix)
            self.assertEqual(Path(handoff['video']).read_bytes(), b'camera-and-microphone')
            resumed = r.Store(self.store.root, self.root / 'draft.txt')
            self.assertEqual(resumed.take(tid)['video'], resumed.take(tid)['audio'])
            self.assertEqual(resumed.take(tid)['capture'], {'width': 1280, 'height': 720, 'frameRate': 30})
            with urllib.request.urlopen(urllib.request.Request(self.url + f'/api/takes/{tid}/audio', headers={'X-Recorder-Token': self.server.token})) as response:
                self.assertEqual(response.headers['Content-Type'], mime)
                self.assertEqual(response.read(), b'camera-and-microphone')
            with self.assertRaises(urllib.error.HTTPError):
                self.call(f'/api/takes/{tid}/audio', token=False)

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
