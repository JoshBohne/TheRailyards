"""Serve the live agent dashboard without exposing the workspace.

python3 tools/live-review/serve.py [--state work/live/state.json] [--port 8863]

State paths are operator-authored (via dash.py), never supplied by HTTP
clients. Older V13/V14 live.json files (note + views only) still work.
"""
import argparse,json,subprocess,sys,time
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import state as S

parser=argparse.ArgumentParser()
parser.add_argument('--state',type=Path,default=None)
parser.add_argument('--port',type=int,default=8863)
args=parser.parse_args()
STATE=S.state_path(args.state)
HERE=Path(__file__).resolve().parent
MODES=['current','before','source']
_git=dict(time=0,log=[])

def git_log():
    if time.time()-_git['time']>20:
        try:
            out=subprocess.run(['git','log','--format=%h%x1f%s%x1f%ct','-12'],capture_output=True,text=True,cwd=S.ROOT,timeout=5).stdout
            _git['log']=[dict(zip(['hash','subject','time'],l.split('\x1f'))) for l in out.splitlines() if l]
            for c in _git['log']:c['time']=int(c['time'])
        except Exception:_git['log']=[]
        _git['time']=time.time()
    return _git['log']

def enrich(state):
    for key,view in state['views'].items():
        for mode in MODES:
            item=view.get(mode)
            if not item:continue
            file=Path(item['path'])
            view[mode]=dict(modified=file.stat().st_mtime,label=item.get('label',mode.title()),name=file.name) if file.is_file() else None
        cur=view.get('current')
        if cur:view['status']=view.get('status') or ('Latest saved render' if cur['modified']>=view.get('requested_after',0) else 'Updating — showing the previous saved render')
        view['stale']=bool(cur) and cur['modified']<view.get('requested_after',0)
    ar=state.get('active_render')
    if ar:
        ar['elapsed_seconds']=round(time.time()-ar['started_at'],1)
        if ar.get('remaining_seconds') is None and ar.get('expected_seconds'):
            ar['remaining_seconds']=max(0,round(ar['expected_seconds']-ar['elapsed_seconds'],1))
            if not ar.get('progress'):ar['progress']=min(.97,ar['elapsed_seconds']/ar['expected_seconds'])
    for v in state.get('versions',[]):v['views']=sorted(v.get('views',{}))
    state['git']=git_log();state['server_time']=time.time();state['state_file']=str(STATE)
    return state

def image_path(state,parts):
    # /image/<view>/<mode>  or  /version/<id>/<view>
    if parts[0]=='image' and len(parts)==3:
        item=state['views'].get(parts[1],{}).get(parts[2]);return item and item['path']
    if parts[0]=='version' and len(parts)==3:
        v=next((v for v in state.get('versions',[]) if v['id']==parts[1]),None);return v and v['views'].get(parts[2])
    if parts[0]=='evidence' and len(parts)==2:
        t=next((t for t in state.get('checklist',[]) if t['id']==parts[1]),None);return t and t.get('evidence')

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*a):pass
    def do_GET(self):
        path=self.path.split('?',1)[0].strip('/');parts=path.split('/') if path else []
        try:
            if not parts:data=(HERE/'index.html').read_bytes();kind='text/html; charset=utf-8'
            elif parts==['state'] or parts==['manifest']:data=json.dumps(enrich(S.load(STATE))).encode();kind='application/json'
            else:
                file=image_path(S.load(STATE),parts)
                if not file or not Path(file).is_file():self.send_error(404);return
                data=Path(file).read_bytes();kind={'.jpg':'image/jpeg','.jpeg':'image/jpeg','.svg':'image/svg+xml','.webp':'image/webp'}.get(Path(file).suffix.lower(),'image/png')
        except Exception as e:
            self.send_error(500,str(e)[:200]);return
        self.send_response(200);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(data)

print(f'Live agent dashboard: http://127.0.0.1:{args.port}/  (state: {STATE})',flush=True)
ThreadingHTTPServer(('127.0.0.1',args.port),Handler).serve_forever()
