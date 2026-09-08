"""Serve a small, auto-refreshing camera review without exposing the workspace.

python3 tools/live-review/serve.py --state work/outfield-v13/live.json --port 8863
State paths are operator-authored, never supplied by HTTP clients.
"""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

parser=argparse.ArgumentParser()
parser.add_argument('--state',type=Path,required=True)
parser.add_argument('--port',type=int,default=8863)
args=parser.parse_args()

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):
        pass
    def do_GET(self):
        path=self.path.split('?',1)[0]
        if path=='/':
            data=Path(__file__).with_name('index.html').read_bytes();kind='text/html; charset=utf-8'
        elif path=='/manifest':
            state=json.loads(args.state.read_text())
            for view in state['views'].values():
                for mode in ['current','before','source']:
                    item=view.get(mode)
                    if not item:continue
                    file=Path(item['path'])
                    view[mode]=dict(modified=file.stat().st_mtime,label=item['label']) if file.is_file() else None
                if view.get('current'):
                    view['status']='Latest saved render' if view['current']['modified']>=view.get('requested_after',0) else 'Updating — showing the previous saved render'
            data=json.dumps(state).encode();kind='application/json'
        elif path.startswith('/image/'):
            parts=path.split('/')
            if len(parts)!=4:
                self.send_error(404);return
            state=json.loads(args.state.read_text())
            item=state['views'].get(parts[2],{}).get(parts[3])
            if not item or not Path(item['path']).is_file():
                self.send_error(404);return
            data=Path(item['path']).read_bytes();kind='image/jpeg' if Path(item['path']).suffix.lower() in ['.jpg','.jpeg'] else 'image/png'
        else:
            self.send_error(404);return
        self.send_response(200);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(data)

print(f'Live model review: http://127.0.0.1:{args.port}/',flush=True)
ThreadingHTTPServer(('127.0.0.1',args.port),Handler).serve_forever()
