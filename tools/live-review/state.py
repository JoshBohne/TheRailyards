"""Shared state helpers for the live dashboard. State is one operator-authored
JSON file (default work/live/state.json); paths inside it are never supplied by
HTTP clients. The schema is a superset of the V13/V14 live.json files.

Top-level keys (all optional except views):
  note            str   headline for the reviewer
  views           {key: {label, current|before|source: {path,label}, requested_after, status}}
  active_render   {view, label, started_at, expected_seconds, progress, remaining_seconds, blend}
  queue           [{id, view, label, expected_seconds, added_at}]
  checklist       [{id, text, status: todo|doing|done|blocked, evidence, updated_at}]
  versions        [{id, label, time, blend, commit, note, views: {key: path}}]
  events          [{time, kind, text}]   (append-only, newest last, capped)
  history         {view: [seconds,...]}  (per-view render durations, newest last)
"""
import json,os,time,fcntl
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
DEFAULT_STATE=ROOT/'work'/'live'/'state.json'
EVENT_CAP=400

def state_path(explicit=None):
    return Path(explicit or os.environ.get('RAILYARDS_LIVE_STATE') or DEFAULT_STATE)

def empty():
    return dict(note='',views={},active_render=None,queue=[],checklist=[],versions=[],events=[],history={})

def load(path=None):
    p=state_path(path)
    if not p.is_file():return empty()
    data=json.loads(p.read_text() or '{}')
    base=empty();base.update(data);return base

def save(data,path=None):
    p=state_path(path);p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_suffix('.json.tmp');tmp.write_text(json.dumps(data,indent=2)+'\n');os.replace(tmp,p)

class edit:
    """with edit() as s: mutate s  — serialised through a lock file, saved atomically."""
    def __init__(self,path=None):self.path=state_path(path)
    def __enter__(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.lock=open(self.path.with_suffix('.lock'),'w');fcntl.flock(self.lock,fcntl.LOCK_EX)
        self.data=load(self.path);return self.data
    def __exit__(self,*exc):
        if exc[0] is None:save(self.data,self.path)
        fcntl.flock(self.lock,fcntl.LOCK_UN);self.lock.close()

def event(data,kind,text):
    data.setdefault('events',[]).append(dict(time=time.time(),kind=kind,text=text))
    del data['events'][:-EVENT_CAP]

def expected_seconds(data,view,fallback=None):
    runs=data.get('history',{}).get(view) or []
    if runs:return round(sum(runs[-3:])/len(runs[-3:]),1)
    return fallback
