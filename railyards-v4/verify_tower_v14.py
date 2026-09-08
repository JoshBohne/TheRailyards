"""Tower tread, doorway and explicit bowl-terrace route diagnostics.

The sampled centerlines and 0.3 m body envelope do not establish structural,
accessibility or capacity compliance. Seat geometry is checked separately.
"""
import bpy,json,math,collections,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
s=bpy.data.scenes['Railyards v4'];bpy.context.window.scene=s
vs=[];fs=[];owners=[]
for o in s.objects:
 if o.type!='MESH' or not o.data.polygons or o.hide_render or any(c.hide_render for c in o.users_collection):continue
 if any(k in o.name.lower()for k in ['spectator','fan ','visitor','crowd','player','tree','plant','lamp','flag']):
  if not o.name.startswith('D2_V14 Rail crossing'):continue
 off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices)
 for p in o.data.polygons:fs.append(tuple(off+i for i in p.vertices));owners.append(o.name)
tree=BVHTree.FromPolygons(vs,fs);record=json.loads(s['v14_audit'])['A05_tower'];samples=[];fail=[]
def probe(label,p):
 samples.append({'label':label,'point':list(p)})
 loc,n,fi,d=tree.ray_cast(p+Vector((0,0,.12)),Vector((0,0,-1)),.3)
 if loc is None:fail.append({'label':label,'kind':'floor','point':list(p)})
 loc,n,fi,d=tree.ray_cast(p+Vector((0,0,.25)),Vector((0,0,1)),1.75)
 if loc is not None:fail.append({'label':label,'kind':'headroom','point':list(p),'object':owners[fi],'distance':d+.25})
 for z in [.7,1.3,1.7]:
  for k in range(8):
   direction=Vector((math.cos(k*math.pi/4),math.sin(k*math.pi/4),0))
   loc,n,fi,d=tree.ray_cast(p+Vector((0,0,z)),direction,.3)
   if loc is not None:fail.append({'label':label,'kind':'body','point':list(p),'object':owners[fi],'distance':d,'z':z})
cx,cy,_=record['new_anchor']
for point in record['internal_stairs']['sampled_tread_centers']:probe('tower:stairs',Vector(point))
for z in record['served_levels']:
 for j in range(13):
  y=cy+2.2+j*.45
  if z in [20,28.6]:break
  probe('tower:north-entry:'+str(z),Vector((cx,y,z)))
 if z in [20,28.6]:
  for j in range(16):probe('tower:west-entry:'+str(z),Vector((cx-9+j*.5,cy-3.5,z)))
for z,end in [(39,-55),(32.6,-50),(26.4,-44)]:
 for j in range(41):
  y=(cy+7.8)+(end-(cy+7.8))*j/40
  probe('tower:terrace:'+str(z),Vector((cx,y,z)))
def line(label,a,b,spacing=.2):
 a,b=Vector(a),Vector(b);count=max(1,math.ceil((b-a).length/spacing))
 for j in range(count+1):probe(label,a.lerp(b,j/count))
for z,path in [(26.4,[(70,-51.5),(82,-52),(94,-50),(108,-50),(109.85,-67)]),
               (32.6,[(68,-64),(80,-64),(94,-63),(108,-62),(109.85,-67)])]:
 for a,b in zip(path,path[1:]):line('tower:bowl-link:'+str(z),(*a,z),(*b,z))
line('tower:upper-approach',(67,-77.35,36),(72,-77.35,36))
for i in range(18):probe('tower:upper-link-stair',Vector((78-(i+.5)/3,-77.35,39-(i+1)/6)))
line('tower:upper-arrival',(78,-77.35,39),(84,-73,39))
line('tower:upper-arrival',(84,-73,39),(96,-63,39))
line('tower:upper-arrival',(96,-63,39),(109.85,-63,39))
line('tower:ground-arrival',(cx,cy+7.8,8),(cx,cy+10.1,8))
# Physical arrival follows the retained riverwalk grade, rather than a
# nominal global lower datum. Confirm the destination against actual mesh.
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from r3_public_realm import quay_z
line('tower:quay-ramp',(cx,cy+10.1,8),(cx,cy+17.1,quay_z(cy+17.1)))
for i in range(16):
 y=cy+17.1+i*.2;probe('tower:quay-destination',Vector((cx,y,quay_z(y))))
shaft_edges=[]
for z in record['served_levels'][1:]:
 for name,point,direction in [('north',(cx,cy+1.8,z),(0,-1,0)),('south',(cx,cy-1.8,z),(0,1,0)),('east',(cx+1.8,cy,z),(-1,0,0))]:
  barriers=[]
  for height in [.6,1.0]:
   hit,normal,face,distance=tree.ray_cast(Vector(point)+Vector((0,0,height)),Vector(direction),.8)
   if hit is not None:barriers.append(owners[face])
  shaft_edges.append({'level':z,'edge':name,'barriers':barriers})
  if len(barriers)!=2:fail.append({'label':'tower:lift-edge:'+name,'kind':'unprotected_edge','point':list(point)})
result={'file':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'samples':len(samples),'shaft_edges':shaft_edges,'failure_counts':dict(collections.Counter(x['kind']for x in fail)),'failures':fail}
(Path(__file__).resolve().parent/'review/v14/tower-route-diagnostics.json').write_text(json.dumps(result,indent=2));print('RESULT',result['samples'],result['failure_counts']);print(collections.Counter(x.get('object')for x in fail))
