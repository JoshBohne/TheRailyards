"""Verify the user's level, open-air entrance against the saved V15 meshes."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
s=bpy.data.scenes['Railyards v4'];bpy.context.window.scene=s
vertices=[];faces=[];owners=[]
for o in s.objects:
    if o.type!='MESH' or not o.data.polygons or o.hide_render or any(c.hide_render for c in o.users_collection):continue
    if any(k in o.name.lower() for k in ['spectator','fan ','visitor','crowd','player','tree','plant','lamp','flag','atmosphere']):continue
    bounds=[o.matrix_world@Vector(p)for p in o.bound_box]
    if max(p.x for p in bounds)<45 or min(p.x for p in bounds)>57 or max(p.y for p in bounds)<105 or min(p.y for p in bounds)>181:continue
    start=len(vertices);vertices.extend(o.matrix_world@v.co for v in o.data.vertices)
    for p in o.data.polygons:faces.append(tuple(start+i for i in p.vertices));owners.append(o.name)
tree=BVHTree.FromPolygons(vertices,faces);failures=[];samples=0
for x in [49.2,51,52.8]:
    for y in range(110,180,2):
        at,normal,index,distance=tree.ray_cast(Vector((x,y,14)),Vector((0,0,-1)),1)
        samples+=1
        if at is None or abs(at.z-13.4)>.025:failures.append({'kind':'level_floor','xy':[x,y],'hit':None if at is None else [owners[index],list(at)]})
        # The shallow arch itself is allowed only at its one-metre wall line.
        if 159.4<y<161:continue
        at,normal,index,distance=tree.ray_cast(Vector((x,y,15.3)),Vector((0,0,1)),100)
        if at is not None:failures.append({'kind':'roof_over_open_route','xy':[x,y],'object':owners[index],'point':list(at)})
result={'sceneSha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'floor_m':13.4,'samples':samples,'failures':failures,'scope':'Open-air arrival through arches and split left-center bank; inferred model, not engineering certification.'}
out=Path('work/v15/arrival-verification.json');out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n')
print('V15_ARRIVAL',samples,'samples',len(failures),'failures')
if failures:raise RuntimeError('Open-air arrival verification failed; inspect '+str(out))
