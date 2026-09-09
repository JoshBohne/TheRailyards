#!/usr/bin/env python3
"""Agent-facing CLI for the live dashboard. Every mutation appends an event so
the reviewer can follow along. Default state: work/live/state.json
(override with --state or RAILYARDS_LIVE_STATE).

  dash.py note "Rebuilding LF seating banks"
  dash.py view set lf-terrace --label "LF terrace" --current path.png [--before p] [--source p] [--status "…"]
  dash.py view expect lf-terrace            # mark current as stale until a newer file lands
  dash.py task add "Fix RF scoreboard pylons" [--id rf-pylons]
  dash.py task done rf-pylons [--evidence review/v15/rf.png]
  dash.py task set rf-pylons doing|blocked|todo
  dash.py queue add lf-terrace [--label "…"] [--expect 40]
  dash.py queue clear
  dash.py render start lf-terrace [--label "…"] [--expect 40] [--blend file]
  dash.py render progress 0.4 [--remaining 25]
  dash.py render finish [--seconds 38.2] [--output path.png]   # also pops it from the queue
  dash.py render cancel
  dash.py run --views a,b,c -- blender -b scene.blend --python render_review.py
  dash.py gallery add <dir> [--glob 'v15-*.png'] [--prefix v15-] [--label-from-name]  # register every image as a view
  dash.py version snapshot "V15 draft 3" [--blend f] [--note "…"]   # copies view images + git commit
  dash.py reset [--all]                     # new session; keeps per-view timings unless --all
  dash.py review list [--pending]           # thumbs up/down + feedback Josh left on the page
  dash.py review ack <view>                 # agent has acted on the feedback
  dash.py source add <path> --title T [--credit C] [--kind render|map|mockup|photo|data|doc] [--note N]
  dash.py source scan <dir> [--kind K] [--credit C] [--glob '*.jpg']   # register every image in a folder
  dash.py source list                       # committed manifest (reconstruction-references/sources.json) + ad hoc
  dash.py source missing                    # manifest entries whose file is not on disk yet
  dash.py show
"""
import argparse,json,os,re,shutil,subprocess,sys,time,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import state as S

def now():return time.time()
def short(text):return text if len(text)<=140 else text[:137]+'…'

def cmd_note(a):
    with S.edit(a.state) as s:s['note']=a.text;S.event(s,'note',short(a.text))

def cmd_view(a):
    with S.edit(a.state) as s:
        v=s['views'].setdefault(a.key,dict(label=a.key,requested_after=0))
        if a.action=='set':
            if a.label:v['label']=a.label
            for mode in ['current','before','source']:
                p=getattr(a,mode)
                if p:v[mode]=dict(path=str(Path(p).resolve()),label=getattr(a,mode+'_label') or mode.title())
            if a.status is not None:v['status']=a.status
            if a.current:
                v['requested_after']=0
                if not a.no_review:v['needs_review']=now()
            S.event(s,'view',f'{v["label"]}: updated {", ".join(m for m in ["current","before","source"] if getattr(a,m))}')
        elif a.action=='expect':
            v['requested_after']=now();S.event(s,'view',f'{v["label"]}: waiting for a new render')
        elif a.action=='remove':
            s['views'].pop(a.key,None);S.event(s,'view',f'{a.key}: removed')

def cmd_task(a):
    with S.edit(a.state) as s:
        items=s['checklist']
        if a.action=='add':
            tid=a.id or re.sub(r'[^a-z0-9]+','-',a.text.lower()).strip('-')[:40] or uuid.uuid4().hex[:8]
            if any(t['id']==tid for t in items):sys.exit(f'task {tid} exists')
            items.append(dict(id=tid,text=a.text,status='todo',evidence=None,updated_at=now()));S.event(s,'task',f'added: {short(a.text)}');print(tid);return
        t=next((t for t in items if t['id']==a.id),None)
        if not t:sys.exit(f'no task {a.id}')
        if a.action=='done':t['status']='done'
        elif a.action=='set':t['status']=a.status
        elif a.action=='remove':items.remove(t);S.event(s,'task',f'removed: {short(t["text"])}');return
        if getattr(a,'evidence',None):t['evidence']=str(Path(a.evidence).resolve())
        t['updated_at']=now();S.event(s,'task',f'{t["status"]}: {short(t["text"])}')

def cmd_queue(a):
    with S.edit(a.state) as s:
        if a.action=='add':
            for key in a.views:
                s['queue'].append(dict(id=uuid.uuid4().hex[:8],view=key,label=a.label or s['views'].get(key,{}).get('label',key),expected_seconds=a.expect or S.expected_seconds(s,key),added_at=now()))
            S.event(s,'queue',f'queued {", ".join(a.views)}')
        elif a.action=='clear':s['queue']=[];S.event(s,'queue','cleared')
        elif a.action=='remove':s['queue']=[q for q in s['queue'] if q['view']!=a.view and q['id']!=a.view];S.event(s,'queue',f'removed {a.view}')

def _start(s,view,label=None,expect=None,blend=None):
    label=label or s['views'].get(view,{}).get('label',view)
    s['active_render']=dict(view=view,label=label,started_at=now(),expected_seconds=expect or S.expected_seconds(s,view),progress=0.0,remaining_seconds=None,blend=blend,stats='')
    v=s['views'].setdefault(view,dict(label=label,requested_after=0));v['requested_after']=now()
    S.event(s,'render',f'started {label}')

def _finish(s,seconds=None,output=None,cancelled=False):
    ar=s.get('active_render')
    if not ar:return
    secs=seconds if seconds is not None else round(now()-ar['started_at'],1)
    view=ar['view']
    if not cancelled and view!='batch':
        s.setdefault('history',{}).setdefault(view,[]).append(secs);del s['history'][view][:-10]
        v=s['views'].setdefault(view,dict(label=ar['label'],requested_after=0))
        if output:
            old=(v.get('current') or {}).get('path')
            v['current']=dict(path=str(Path(output).resolve()),label=(v['current']['label'] if old==str(Path(output).resolve()) and v.get('current') else 'Latest render'))
        v['requested_after']=0
        if output:v['needs_review']=now()
    else:
        v=s['views'].get(view)
        if v:v['requested_after']=0
    s['queue']=[q for q in s['queue'] if q['view']!=view] if s['queue'] and s['queue'][0]['view']==view else s['queue']
    s['active_render']=None
    S.event(s,'render',('cancelled ' if cancelled else 'finished ')+f'{ar["label"]} in {secs}s')

def cmd_render(a):
    with S.edit(a.state) as s:
        if a.action=='start':
            if s.get('active_render'):_finish(s,cancelled=True)
            _start(s,a.view,a.label,a.expect,a.blend)
        elif a.action=='progress':
            ar=s.get('active_render')
            if ar:ar['progress']=max(0.0,min(1.0,a.value));ar['remaining_seconds']=a.remaining;ar['stats']=a.stats or ar.get('stats','')
        elif a.action=='finish':_finish(s,a.seconds,a.output)
        elif a.action=='cancel':_finish(s,cancelled=True)

# Remaining is parsed as MM:SS; renders over an hour (H:MM:SS) would read wrong.
STATS=re.compile(r'Sample (\d+)/(\d+)')
REMAINING=re.compile(r'Remaining: ?(\d+):(\d+(?:\.\d+)?)')
SAVED=re.compile(r"Saved: '([^']+)'")
LOG_FLAGS=['--log','render','--log-level','info']  # Blender 5.x prints Sample x/y only with these
def cmd_run(a):
    """Run a Blender CLI render, tailing Cycles stats into the dashboard.
    Views advance on each 'Saved:' line; progress comes from Sample x/y and Remaining."""
    views=[v for v in (a.views or '').split(',') if v];idx=0
    if not a.command:sys.exit('give the blender command after --')
    cmd=list(a.command)
    if '--log' not in cmd and Path(cmd[0]).name.lower().startswith('blender'):cmd[1:1]=LOG_FLAGS
    a.command=cmd
    with S.edit(a.state) as s:
        if s.get('active_render'):_finish(s,cancelled=True)
        if views:_start(s,views[0],blend=a.blend,expect=a.expect)
        else:s['active_render']=dict(view='batch',label=a.label or 'Batch render',started_at=now(),expected_seconds=a.expect,progress=0.0,remaining_seconds=None,blend=a.blend,stats='')
        S.event(s,'run',short(' '.join(a.command)))
    proc=subprocess.Popen(a.command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
    last=0
    try:
        for line in proc.stdout:
            sys.stdout.write(line)
            m=STATS.search(line);saved=SAVED.search(line)
            if m and now()-last>1.0:
                last=now();remaining=None
                progress=int(m.group(1))/max(1,int(m.group(2)))
                r=REMAINING.search(line)
                if r:remaining=int(r.group(1))*60+float(r.group(2))
                with S.edit(a.state) as s:
                    ar=s.get('active_render')
                    if ar:
                        if progress is not None:ar['progress']=progress
                        ar['remaining_seconds']=remaining;ar['stats']=line.split('|',1)[-1].strip()[:160] if line.count('|')>1 else line.strip()[:160]
            elif saved:
                out=saved.group(1)
                with S.edit(a.state) as s:
                    if views and idx<len(views):
                        _finish(s,output=out);idx+=1
                        if idx<len(views):_start(s,views[idx],blend=a.blend)
                    else:S.event(s,'warning' if views else 'render',(f'saved {Path(out).name} beyond the {len(views)} declared --views; check RAILYARDS_REVIEW_VIEWS matches' if views else f'saved {Path(out).name}'))
    finally:
        code=proc.wait()
        with S.edit(a.state) as s:
            if s.get('active_render'):_finish(s,cancelled=code!=0)
            if code:S.event(s,'error',f'render command exited {code}')
    sys.exit(code)

def cmd_gallery(a):
    """Register every image in a directory as a view (current only, or before/current pairs by prefix)."""
    import glob as G
    root=Path(a.dir).resolve();files=sorted(root.glob(a.glob))
    if not files:sys.exit(f'no {a.glob} in {root}')
    with S.edit(a.state) as s:
        n=0
        for f in files:
            if f.suffix.lower() not in ['.png','.jpg','.jpeg','.webp']:continue
            stem=f.stem
            mode='current'
            if stem.startswith('before-'):mode='before';stem=stem[7:]
            elif stem.startswith('after-'):stem=stem[6:]
            if a.prefix and stem.startswith(a.prefix):stem=stem[len(a.prefix):]
            key=re.sub(r'[^a-z0-9]+','-',stem.lower()).strip('-')
            v=s['views'].setdefault(key,dict(label=stem.replace('_',' ').replace('-',' '),requested_after=0))
            v[mode]=dict(path=str(f),label=a.label or (mode.title()+' · '+f.name))
            n+=1
        S.event(s,'gallery',f'registered {n} images from {root.name}')
    print(n)

def cmd_version(a):
    with S.edit(a.state) as s:
        vid=time.strftime('%Y%m%d-%H%M%S');folder=S.state_path(a.state).parent/'versions'/vid;folder.mkdir(parents=True,exist_ok=True)
        copied={}
        for key,v in s['views'].items():
            cur=v.get('current')
            if cur and Path(cur['path']).is_file():
                dst=folder/(key+Path(cur['path']).suffix);shutil.copy2(cur['path'],dst);copied[key]=str(dst)
        try:commit=subprocess.run(['git','rev-parse','--short','HEAD'],capture_output=True,text=True,cwd=S.ROOT).stdout.strip()
        except Exception:commit=None
        s['versions'].append(dict(id=vid,label=a.label,time=now(),blend=a.blend,commit=commit or None,note=a.note or '',views=copied))
        S.event(s,'version',f'snapshot "{a.label}" ({len(copied)} views)');print(folder)

def cmd_reset(a):
    with S.edit(a.state) as s:
        hist={} if a.all else s.get('history',{})
        s.clear();s.update(S.empty());s['history']=hist;S.event(s,'reset','new session')

def cmd_review(a):
    reviews=S.load_reviews(a.state);s=S.load(a.state)
    if a.action=='list':
        for r in reviews:
            if a.pending and r.get('acked'):continue
            v=s['views'].get(r['view'],{})
            print(f"{'UP  ' if r['verdict']=='up' else 'DOWN'} {r['view']} ({v.get('label',r['view'])}) {time.strftime('%H:%M',time.localtime(r['time']))}{' acked' if r.get('acked') else ''}: {r.get('feedback','')}")
        pending=[k for k,v in s['views'].items() if v.get('needs_review') and not any(r['view']==k and r['image_modified']>=v['needs_review'] for r in reviews)]
        if pending:print('awaiting Josh:',', '.join(pending))
    elif a.action=='ack':
        p=S.reviews_path(a.state)
        for r in reviews:
            if r['view']==a.view:r['acked']=True
        p.write_text(json.dumps(reviews,indent=2))
        with S.edit(a.state) as st:S.event(st,'review',f'acted on feedback for {a.view}')

def cmd_source(a):
    if a.action in ('list','missing'):
        man=json.loads((S.ROOT/'reconstruction-references'/'sources.json').read_text())['sources']
        for x in man+S.load(a.state).get('sources',[]):
            f=x.get('path') and (S.ROOT/x['path']);ok=bool(f and Path(f).is_file())
            if a.action=='missing' and (ok or not x.get('path')):continue
            print(f"{'ok ' if ok else ('url' if not x.get('path') else 'MISSING')}  {x['kind']:<10} {x['id']:<32} {x.get('credit','')}")
        return
    with S.edit(a.state) as s:
        items=s.setdefault('sources',[])
        def add(path,title):
            sid=re.sub(r'[^a-z0-9]+','-',title.lower()).strip('-')[:50] or uuid.uuid4().hex[:8]
            if any(x['id']==sid for x in items):return None
            items.append(dict(id=sid,path=str(Path(path).resolve()),title=title,credit=a.credit or '',kind=a.kind or 'render',note=a.note or '',added_at=now()));return sid
        if a.action=='add':
            sid=add(a.path,a.title or Path(a.path).stem);S.event(s,'source',f'added {sid}');print(sid)
        else:
            n=0
            for f in sorted(Path(a.path).glob(a.glob)):
                if f.suffix.lower() in ['.png','.jpg','.jpeg','.webp','.svg','.pdf','.gif'] and add(f,f.stem.replace('_',' ').replace('-',' ')):n+=1
            S.event(s,'source',f'registered {n} sources from {Path(a.path).name}');print(n)

def cmd_show(a):
    s=S.load(a.state);ar=s.get('active_render')
    print('note:',s.get('note'))
    if ar:print(f'rendering: {ar["label"]} {int((ar.get("progress") or 0)*100)}% expected {ar.get("expected_seconds")}s')
    print('queue:',[q['view'] for q in s['queue']])
    for t in s['checklist']:print(f' [{ {"todo":" ","doing":">","done":"x","blocked":"!"}[t["status"]] }] {t["id"]}: {t["text"]}')
    print('views:',{k:[m for m in ['current','before','source'] if v.get(m)] for k,v in s['views'].items()})
    print('versions:',[v['label'] for v in s['versions']])

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter);p.add_argument('--state')
    sub=p.add_subparsers(dest='cmd',required=True)
    x=sub.add_parser('note');x.add_argument('text');x.set_defaults(f=cmd_note)
    x=sub.add_parser('view');x.add_argument('action',choices=['set','expect','remove']);x.add_argument('key');x.add_argument('--label');x.add_argument('--status')
    for m in ['current','before','source']:x.add_argument('--'+m);x.add_argument(f'--{m}-label')
    x.add_argument('--no-review',action='store_true');x.set_defaults(f=cmd_view)
    x=sub.add_parser('task');x.add_argument('action',choices=['add','done','set','remove']);x.add_argument('text_or_id');x.add_argument('status',nargs='?',choices=['todo','doing','done','blocked']);x.add_argument('--id');x.add_argument('--evidence')
    x.set_defaults(f=lambda a:(setattr(a,'text',a.text_or_id),setattr(a,'id',a.id if a.action=='add' else a.text_or_id),cmd_task(a)))
    x=sub.add_parser('queue');x.add_argument('action',choices=['add','clear','remove']);x.add_argument('views',nargs='*');x.add_argument('--label');x.add_argument('--expect',type=float)
    x.set_defaults(f=lambda a:(setattr(a,'view',a.views[0] if a.views else None),cmd_queue(a)))
    x=sub.add_parser('render');x.add_argument('action',choices=['start','progress','finish','cancel']);x.add_argument('view',nargs='?');x.add_argument('--label');x.add_argument('--expect',type=float);x.add_argument('--blend');x.add_argument('--remaining',type=float);x.add_argument('--stats');x.add_argument('--seconds',type=float);x.add_argument('--output')
    x.set_defaults(f=lambda a:(setattr(a,'value',float(a.view) if a.action=='progress' else 0),cmd_render(a)))
    x=sub.add_parser('run');x.add_argument('--views');x.add_argument('--label');x.add_argument('--blend');x.add_argument('--expect',type=float);x.add_argument('command',nargs=argparse.REMAINDER);x.set_defaults(f=cmd_run)
    x=sub.add_parser('gallery');x.add_argument('action',choices=['add']);x.add_argument('dir');x.add_argument('--glob',default='*.png');x.add_argument('--prefix');x.add_argument('--label');x.set_defaults(f=cmd_gallery)
    x=sub.add_parser('version');x.add_argument('action',choices=['snapshot']);x.add_argument('label');x.add_argument('--blend');x.add_argument('--note');x.set_defaults(f=cmd_version)
    x=sub.add_parser('review');x.add_argument('action',choices=['list','ack']);x.add_argument('view',nargs='?');x.add_argument('--pending',action='store_true');x.set_defaults(f=cmd_review)
    x=sub.add_parser('source');x.add_argument('action',choices=['add','scan','list','missing']);x.add_argument('path',nargs='?');x.add_argument('--title');x.add_argument('--credit');x.add_argument('--kind');x.add_argument('--note');x.add_argument('--glob',default='*');x.set_defaults(f=cmd_source)
    x=sub.add_parser('reset');x.add_argument('--all',action='store_true');x.set_defaults(f=cmd_reset)
    x=sub.add_parser('show');x.set_defaults(f=cmd_show)
    a=p.parse_args(argv)
    if getattr(a,'command',None) and a.command[:1]==['--']:a.command=a.command[1:]
    a.f(a)
if __name__=='__main__':main()
