"""Saved-scene stadium diagnostics; failures are evidence, not acceptance waivers.

Includes retained seats and guards. Human/foot offsets are diagnostic envelopes,
not a building-code or engineering certificate. Route coverage is explicit.
"""
import bpy,json,math,hashlib
from pathlib import Path
from collections import Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parent
scene=bpy.data.scenes['Railyards v4'];bpy.context.window.scene=scene
if not scene.get('v14_audit'):raise ValueError('Expected a saved V14 audit scene')
vertices=[];faces=[];owners=[]
for obj in scene.objects:
    if obj.type!='MESH' or not obj.data.polygons or obj.hide_render or any(c.hide_render for c in obj.users_collection):continue
    if any(k in obj.name.lower() for k in ['spectator','fan ','visitor','crowd','player','tree','plant','lamp','flag']):continue
    bounds=[obj.matrix_world@Vector(p) for p in obj.bound_box]
    if max(p.x for p in bounds)<-160 or min(p.x for p in bounds)>160 or max(p.y for p in bounds)<-160 or min(p.y for p in bounds)>180:continue
    start=len(vertices);vertices.extend(obj.matrix_world@v.co for v in obj.data.vertices)
    for p in obj.data.polygons:
        faces.append(tuple(start+i for i in p.vertices));owners.append(obj.name)
tree=BVHTree.FromPolygons(vertices,faces)
failures=[];seat_count=0
for obj in scene.objects:
    if obj.type!='MESH' or obj.data.polygons or 'seat' not in obj.name.lower() or 'source' in obj.name.lower():continue
    scales=obj.data.attributes.get('scale');rotation=obj.data.attributes.get('rotation')
    for i,v in enumerate(obj.data.vertices):
        if scales and scales.data[i].vector.length<.1:continue
        p=obj.matrix_world@v.co;seat_count+=1
        def record(kind,offset,hit,distance):
            failures.append({'kind':kind,'object':obj.name,'index':i,'point':list(p),
                'offset':offset,'obstruction':owners[hit] if hit is not None else None,'distance':distance})
        angle=rotation.data[i].vector.z if rotation else 0
        for dx,dy in [(0,0),(-.2475,-.15),(.2475,-.15),(.2475,.15),(-.2475,.15)]:
            offset=Vector((dx*math.cos(angle)-dy*math.sin(angle),dx*math.sin(angle)+dy*math.cos(angle),.05))
            point,normal,hit,distance=tree.ray_cast(p+offset,Vector((0,0,-1)),.35)
            if point is None:record('center_floor' if dx==dy==0 else 'foot_floor',list(offset),hit,distance)
        point,normal,hit,distance=tree.ray_cast(p+Vector((0,0,.08)),Vector((0,0,1)),.22)
        if point is not None:record('low_intersection',[0,0,.08],hit,distance+.08)
        point,normal,hit,distance=tree.ray_cast(p+Vector((0,0,.3)),Vector((0,0,1)),1.55)
        if point is not None:record('headroom',[0,0,.3],hit,distance+.3)
        for z in [.75,1.25]:
            for k in range(8):
                direction=Vector((math.cos(k*math.pi/4),math.sin(k*math.pi/4),0))
                point,normal,hit,distance=tree.ray_cast(p+Vector((0,0,z)),direction,.24)
                if point is not None:record('body',[*direction[:2],z],hit,distance)
route_failures=[];route_samples=[]
for x in [49.2,50.1,51,51.9,52.8]:
    for n in range(113):
        y=105+n*.5
        floor,normal,hit,distance=tree.ray_cast(Vector((x,y,17.8)),Vector((0,0,-1)),5)
        if floor is None:route_failures.append({'kind':'floor','point':[x,y]});continue
        route_samples.append(list(floor))
        roof,normal,hit,distance=tree.ray_cast(floor+Vector((0,0,.2)),Vector((0,0,1)),1.8)
        if roof is not None:route_failures.append({'kind':'headroom','point':list(floor),'obstruction':owners[hit]})
        for z in [.6,1.3,1.7]:
            for direction in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]:
                point,normal,hit,distance=tree.ray_cast(floor+Vector((0,0,z)),Vector(direction),.23)
                if point is not None:route_failures.append({'kind':'body','point':list(floor),'obstruction':owners[hit]})
summary={'file':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
    'active_seats':seat_count,'failure_counts':dict(Counter(f['kind'] for f in failures)),
    'route':'Park arcade to field landing only; other stadium routes not yet covered',
    'route_samples':len(route_samples),'route_failures':len(route_failures),
    'limitation':'Raw authored mesh geometry and diagnostic envelopes; no engineering certification'}
out=ROOT/'review/v14';out.mkdir(parents=True,exist_ok=True)
(out/'whole-model-diagnostics.json').write_text(json.dumps({'summary':summary,'seat_failures':failures,
    'route_samples':route_samples,'route_failures':route_failures},indent=2)+'\n')
print(json.dumps(summary,indent=2))
