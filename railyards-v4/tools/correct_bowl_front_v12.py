"""V12: correct the traced bowl_front so the diamond has regulation-scale foul territory.

The V2 trace put the seating front 5.7 m behind home plate and ~5 m off the
third-base line while the first-base side sat 12.8 m off its line.  Points are
pushed along their own front->back ray (so tier/row indices stay aligned) until
they clear a keep-out region: 12.8 m either side of the foul lines (tapering to
4 m at the poles) and a 16.5 m backstop radius.  The diamond, poles and traced
bowl_back are untouched; the original trace is kept as bowl_front_v11_trace.
Run once from railyards-v4/: python3 tools/correct_bowl_front_v12.py
"""
import json,math
from pathlib import Path
SPEC=Path(__file__).resolve().parent.parent/'scene-spec.json'
spec=json.loads(SPEC.read_text())
front=spec.get('bowl_front_v11_trace') or spec['bowl_front']
back=spec['bowl_back']
SIDE=12.8;POLE=4.0;BACKSTOP=16.5
def clearance(s):
    # distance-from-line requirement as a function of distance along the line
    return SIDE if s<=60 else max(POLE,SIDE-(s-60)/40*(SIDE-POLE))
def keepout(x,y):
    if math.hypot(x,y)<BACKSTOP:return True
    return x>-clearance(y) and y>-clearance(x)
result=[]
for f,b in zip(front,back):
    fx,fy,fz=f;bx,by,_=b
    if not keepout(fx,fy):result.append([fx,fy,fz]);continue
    lo,hi=0.0,1.0
    for _ in range(60):
        t=(lo+hi)/2;x=fx+(bx-fx)*t;y=fy+(by-fy)*t
        if keepout(x,y):lo=t
        else:hi=t
    result.append([fx+(bx-fx)*hi,fy+(by-fy)*hi,fz])
spec['bowl_front_v11_trace']=front
spec['bowl_front']=result
spec['bowl_front_basis']='V12: V2 trace pushed along front->back rays to 12.8 m foul clearance (tapering to 4 m at the poles) and a 16.5 m backstop; the trace had home 5.7 m from the seats. Inferred, symmetric with the traced first-base side.'
SPEC.write_text(json.dumps(spec,indent=2)+'\n')
moved=sum(1 for a,b in zip(front,result) if a!=b)
print('moved',moved,'of',len(front));print('behind home',min(math.hypot(x,y) for x,y,z in result))
for i in range(0,161,10):print(i,[round(v,1) for v in front[i][:2]],'->',[round(v,1) for v in result[i][:2]])
