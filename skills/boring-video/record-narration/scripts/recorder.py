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

ASSETS = Path(__file__).resolve().parents[1] / 'assets'
MIMES = {'audio/webm': '.webm', 'audio/mp4': '.m4a', 'audio/ogg': '.ogg'}
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

    def save(self):
        atomic(self.manifest, json.dumps(self.data, ensure_ascii=False, indent=2).encode())

    def state(self):
        with self.lock:
            result = json.loads(json.dumps(self.data))
            result['script'] = (self.root / 'script.txt').read_text(encoding='utf-8')
            for take in result['takes']:
                take['chunks'] = len(list((self.root / 'takes' / take['id']).glob('*.chunk')))
            return result

    def take(self, take_id):
        return next(t for t in self.data['takes'] if t['id'] == take_id)

    def create(self, mime):
        base = mime.split(';')[0]
        if base not in MIMES:
            raise ValueError('不支持的录音格式')
        with self.lock:
            take = {'id': uuid.uuid4().hex, 'mime': mime, 'complete': False}
            (self.root / 'takes' / take['id']).mkdir(parents=True)
            self.data['takes'].append(take)
            self.data['status'] = 'recording'
            self.data.pop('audio', None)
            (self.root / 'handoff.json').unlink(missing_ok=True)
            self.save()
            return take

    def chunk(self, take_id, index, data):
        with self.lock:
            take = self.take(take_id)
            if take['complete'] or not 0 <= index < 100000 or not data:
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
                'script': str(self.root / 'script.txt'),
                'audio': str(self.root / take['audio']), 'take': take_id,
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
            if path in ('/', '/recorder.js'):
                # UI token is supplied in the URL fragment; never embedded in a public response.
                if self.headers.get('Host') != f'127.0.0.1:{self.server.server_port}':
                    return self.respond({'error': 'Invalid host'}, 403)
                name = 'index.html' if path == '/' else 'recorder.js'
                return self.respond((ASSETS / name).read_bytes(), mime='text/html; charset=utf-8' if path == '/' else 'text/javascript')
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
                if path == '/api/takes':
                    return self.respond(store.create(body['mime']))
                if path == '/api/ready':
                    return self.respond(store.ready(body['take']))
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--script', type=Path, required=True)
    parser.add_argument('--session', type=Path, required=True)
    parser.add_argument('--port', type=int, default=8765, help='0 chooses an available port')
    parser.add_argument('--no-open', action='store_true')
    args = parser.parse_args()
    store = Store(args.session, args.script)
    server = make_server(store, args.port)
    url = f'http://127.0.0.1:{server.server_port}/#{server.token}'
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
