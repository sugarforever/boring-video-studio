#!/usr/bin/env python3
"""Local teleprompter/recorder. Standard library only; bind to loopback."""
import argparse
import json
import os
from pathlib import Path
import re
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
import uuid
import webbrowser
import urllib.request
import urllib.error

ASSETS = Path(__file__).resolve().parents[1] / 'assets'
MIMES = {'audio/webm': '.webm', 'audio/mp4': '.m4a', 'audio/ogg': '.ogg', 'video/webm': '.webm', 'video/mp4': '.mp4'}
MAX_CHUNK = 32 * 1024 * 1024


def atomic(path, data):
    tmp = path.with_suffix(path.suffix + '.tmp')
    with tmp.open('wb') as file:
        file.write(data)
        file.flush()
        os.fsync(file.fileno())
    tmp.replace(path)


class Store:
    def __init__(self, root, script):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.manifest = self.root / 'session.json'
        if not self.manifest.exists():
            text = Path(script).read_text(encoding='utf-8-sig')
            if not text.strip():
                raise ValueError('口播稿为空')
            atomic(self.root / 'script.txt', text.encode('utf-8'))
            self.data = {'version': 1, 'status': 'idle', 'takes': [], 'selected': None}
            self.save()
        else:
            self.data = json.loads(self.manifest.read_text(encoding='utf-8'))

    def update_script(self, text):
        if not isinstance(text, str) or not text.strip():
            raise ValueError('口播稿为空')
        with self.lock:
            old = (self.root / 'script.txt').read_text(encoding='utf-8')
            if text == old:
                return {'changed': False}
            if any(not take['complete'] and not take.get('abandoned') for take in self.data['takes']):
                raise ValueError('请先完成或恢复未完成的录音，再更新口播稿')
            # Backfill snapshots for recordings made before per-take scripts.
            for take in self.data['takes']:
                target = self.root / 'takes' / take['id'] / 'script.txt'
                if not target.exists():
                    atomic(target, old.encode('utf-8'))
            atomic(self.root / 'script.txt', text.encode('utf-8'))
            self.data.update(status='idle', selected=None)
            self.data.pop('audio', None)
            (self.root / 'handoff.json').unlink(missing_ok=True)
            self.save()
            return {'changed': True}

    def save(self):
        atomic(self.manifest, json.dumps(self.data, ensure_ascii=False, indent=2).encode())

    def state(self):
        with self.lock:
            result = json.loads(json.dumps(self.data))
            result['session'] = str(self.root)
            result['script'] = (self.root / 'script.txt').read_text(encoding='utf-8')
            for take in result['takes']:
                take['chunks'] = len(list((self.root / 'takes' / take['id']).glob('*.chunk')))
            return result

    def take(self, take_id):
        return next(t for t in self.data['takes'] if t['id'] == take_id)

    def create(self, mime, capture=None, expected_script=None):
        if capture is not None and not isinstance(capture, dict):
            raise ValueError('无效的录音设备设置')
        base = mime.split(';')[0]
        if base not in MIMES:
            raise ValueError('不支持的录音格式')
        with self.lock:
            current_script = (self.root / 'script.txt').read_text(encoding='utf-8')
            if expected_script != current_script:
                raise FileExistsError('口播稿已更新，请确认新稿后重新开始录音')
            take = {'id': uuid.uuid4().hex, 'mime': mime, 'complete': False,
                    'capture': {key: value for key, value in (capture or {}).items()
                                if key in ('sampleRate', 'channelCount', 'echoCancellation', 'noiseSuppression', 'autoGainControl', 'width', 'height', 'frameRate')}}
            (self.root / 'takes' / take['id']).mkdir(parents=True)
            atomic(self.root / 'takes' / take['id'] / 'script.txt',
                   current_script.encode('utf-8'))
            self.data['takes'].append(take)
            self.data['status'] = 'recording'
            self.data.pop('audio', None)
            (self.root / 'handoff.json').unlink(missing_ok=True)
            self.save()
            return take

    def abandon(self, take_id):
        with self.lock:
            take = self.take(take_id)
            if take['complete']:
                raise ValueError('完整录音无需放弃，请保留并选择需要的版本')
            take['abandoned'] = True
            if self.data['status'] == 'recording' and not any(
                    not t['complete'] and not t.get('abandoned') for t in self.data['takes']):
                self.data['status'] = 'idle'
            self.save()
            return {'status': 'abandoned'}

    def chunk(self, take_id, index, data):
        with self.lock:
            take = self.take(take_id)
            if take['complete'] or take.get('abandoned') or not 0 <= index < 100000 or not data:
                raise ValueError('无效的音频块')
            path = self.root / 'takes' / take_id / f'{index:06d}.chunk'
            if path.exists():
                if path.read_bytes() != data:
                    raise FileExistsError('音频块内容冲突')
            else:
                atomic(path, data)
            return {'saved': index}

    def finalize(self, take_id, count):
        with self.lock:
            take = self.take(take_id)
            if take.get('abandoned'):
                raise ValueError('该版本已放弃，保存的文件仍保留')
            if take['complete']:
                return take
            directory = self.root / 'takes' / take_id
            chunks = sorted(directory.glob('*.chunk'))
            if count < 1 or count != len(chunks) or any(p.name != f'{i:06d}.chunk' for i, p in enumerate(chunks)):
                raise ValueError('录音块不完整，请重试保存或恢复已保存的录音')
            target = directory / ('original' + MIMES[take['mime'].split(';')[0]])
            temp = target.with_suffix('.tmp')
            with temp.open('wb') as output:
                for chunk in chunks:
                    with chunk.open('rb') as source:
                        while block := source.read(1024 * 1024):
                            output.write(block)
                output.flush()
                os.fsync(output.fileno())
            temp.replace(target)
            take.update(complete=True, audio=str(target.relative_to(self.root)))
            if take['mime'].startswith('video/'):
                take['video'] = take['audio']
            self.data['selected'] = take_id
            self.data['status'] = 'recorded'
            self.save()
            return take

    def ready(self, take_id):
        with self.lock:
            take = self.take(take_id)
            if not take['complete']:
                raise ValueError('请先完成录音保存')
            self.data.update(status='ready', selected=take_id, audio=take['audio'])
            self.save()
            atomic(self.root / 'handoff.json', json.dumps({
                'script': str(self.root / 'takes' / take_id / 'script.txt'
                              if (self.root / 'takes' / take_id / 'script.txt').exists()
                              else self.root / 'script.txt'),
                'audio': str(self.root / take['audio']), 'take': take_id,
                **({'video': str(self.root / take['video'])} if take.get('video') else {}),
            }, ensure_ascii=False, indent=2).encode())
            return {'status': 'ready'}


def make_server(store, port=8765):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def respond(self, value, status=200, mime='application/json'):
            payload = json.dumps(value, ensure_ascii=False).encode() if mime == 'application/json' else value
            self.send_response(status)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(payload)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; media-src 'self' blob:; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(payload)

        def authorized(self):
            host = self.headers.get('Host')
            expected = f'127.0.0.1:{self.server.server_port}'
            origin = self.headers.get('Origin')
            return (host == expected and (not origin or origin == f'http://{expected}')
                    and secrets.compare_digest(self.headers.get('X-Recorder-Token', ''), self.server.token))

        def do_GET(self):
            path = urlparse(self.path).path
            static = {'/': ('index.html', 'text/html; charset=utf-8'), '/recorder.js': ('recorder.js', 'text/javascript'),
                      '/ui.css': ('ui.css', 'text/css; charset=utf-8'),
                      '/ui.js': ('ui.js', 'text/javascript'),
                      '/camera-monitor.js': ('camera-monitor.js', 'text/javascript'),
                      '/vendor/wavesurfer.min.js': ('vendor/wavesurfer.min.js', 'text/javascript'),
                      '/vendor/regions.min.js': ('vendor/regions.min.js', 'text/javascript')}
            if path in static:
                # UI token is supplied in the URL fragment; never embedded in a public response.
                if self.headers.get('Host') != f'127.0.0.1:{self.server.server_port}':
                    return self.respond({'error': 'Invalid host'}, 403)
                name, mime = static[path]
                return self.respond((ASSETS / name).read_bytes(), mime=mime)
            if not self.authorized():
                return self.respond({'error': 'Unauthorized'}, 403)
            if path == '/api/state':
                return self.respond(store.state())
            match = re.fullmatch(r'/api/takes/([a-f0-9]{32})/audio', path)
            if match:
                try:
                    take = store.take(match[1])
                    return self.respond((store.root / take['audio']).read_bytes(), mime=take['mime'])
                except (StopIteration, KeyError, OSError):
                    pass
            self.respond({'error': 'Not found'}, 404)

        def do_POST(self):
            if not self.authorized():
                return self.respond({'error': 'Unauthorized'}, 403)
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= MAX_CHUNK:
                    return self.respond({'error': 'Invalid body size'}, 413)
                raw = self.rfile.read(length)
                path = urlparse(self.path).path
                match = re.fullmatch(r'/api/takes/([a-f0-9]{32})/chunks/(\d{1,6})', path)
                if match:
                    return self.respond(store.chunk(match[1], int(match[2]), raw))
                body = json.loads(raw)
                if path == '/api/script':
                    return self.respond(store.update_script(body['text']))
                if path == '/api/takes':
                    return self.respond(store.create(body['mime'], body.get('capture'), body.get('script')))
                if path == '/api/ready':
                    return self.respond(store.ready(body['take']))
                match = re.fullmatch(r'/api/takes/([a-f0-9]{32})/abandon', path)
                if match:
                    return self.respond(store.abandon(match[1]))
                match = re.fullmatch(r'/api/takes/([a-f0-9]{32})/finalize', path)
                if match:
                    return self.respond(store.finalize(match[1], int(body['chunks'])))
                self.respond({'error': 'Not found'}, 404)
            except FileExistsError as error:
                self.respond({'error': str(error)}, 409)
            except (ValueError, KeyError, TypeError, StopIteration) as error:
                self.respond({'error': str(error) or 'Unknown take'}, 400)
            except OSError as error:
                self.respond({'error': f'保存失败：{error}'}, 500)

    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    server.token = secrets.token_urlsafe(32)
    server.daemon_threads = True
    return server


def reuse_server(session, script=None):
    """Validate the saved endpoint before reusing it; never replace a live service."""
    endpoint = Path(session) / 'recorder-server.json'
    if not endpoint.exists():
        return None
    saved = json.loads(endpoint.read_text(encoding='utf-8'))
    port = int(saved['port'])
    if not 1 <= port <= 65535:
        raise ValueError('Invalid saved recorder port')
    base = f'http://127.0.0.1:{port}'
    headers = {'X-Recorder-Token': saved['token']}
    try:
        with urllib.request.urlopen(urllib.request.Request(base + '/api/state', headers=headers), timeout=2) as response:
            state = json.load(response)
    except urllib.error.HTTPError as error:
        raise RuntimeError('保存的端口由其他服务占用，请检查后再启动') from error
    except urllib.error.URLError:
        return None
    if state.get('session') != str(Path(session).resolve()):
        raise ValueError('录音服务与会话目录不匹配')
    if script is not None:
        request = urllib.request.Request(base + '/api/script',
            data=json.dumps({'text': Path(script).read_text(encoding='utf-8-sig')}).encode(),
            headers={**headers, 'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(request, timeout=2) as response:
                json.load(response)
        except urllib.error.HTTPError as error:
            detail = json.loads(error.read()).get('error', str(error))
            raise ValueError(detail) from error
    return base + '/#' + saved['token']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--script', type=Path, required=True)
    parser.add_argument('--session', type=Path, required=True)
    parser.add_argument('--port', type=int, default=None, help='Reuse saved port, otherwise 8765; 0 chooses an available port')
    parser.add_argument('--no-open', action='store_true')
    parser.add_argument('--update-script', action='store_true', help='Update the current draft while preserving each take’s script snapshot')
    args = parser.parse_args()
    url = reuse_server(args.session, args.script if args.update_script else None)
    if url:
        print(f'Recorder (reused): {url}\nSession: {args.session.resolve()}', flush=True)
        return
    store = Store(args.session, args.script)
    if args.update_script:
        store.update_script(args.script.read_text(encoding='utf-8-sig'))
    port = args.port
    if port is None:
        endpoint = store.root / 'recorder-server.json'
        port = int(json.loads(endpoint.read_text())['port']) if endpoint.exists() else 8765
    server = make_server(store, port)
    url = f'http://127.0.0.1:{server.server_port}/#{server.token}'
    endpoint = store.root / 'recorder-server.json'
    if endpoint.exists():
        server.token = json.loads(endpoint.read_text())['token']
        url = f'http://127.0.0.1:{server.server_port}/#{server.token}'
    atomic(endpoint, json.dumps({'port': server.server_port, 'token': server.token}).encode())
    endpoint.chmod(0o600)
    print(f'Recorder: {url}\nSession: {store.root}', flush=True)
    if not args.no_open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
