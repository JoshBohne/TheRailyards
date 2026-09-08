"""Saved-scene geometry checks for the V13 seating and park passage."""
import bpy
import json
import sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
scene=bpy.data.scenes['Railyards v4'];bpy.context.window.scene=scene
if not scene.get('v13_outfield'):raise ValueError('Expected V13 saved scene')

def tree(objects):
    vertices=[];faces=[]
    for obj in objects:
        if obj.type!='MESH' or not obj.data.polygons or obj.hide_render:continue
        start=len(vertices)
        vertices.extend(tuple(obj.matrix_world@v.co) for v in obj.data.vertices)
        faces.extend(tuple(start+i for i in p.vertices) for p in obj.data.polygons)
    return BVHTree.FromPolygons(vertices,faces)

architecture=[]
for obj in scene.objects:
    if obj.type!='MESH' or not obj.data.polygons or obj.hide_render:continue
    if any(s in obj.name.lower() for s in ['spectator','visitor','fan','tree','atmosphere']):continue
    points=[obj.matrix_world@Vector(c) for c in obj.bound_box]
    if max(p.x for p in points)<-70 or min(p.x for p in points)>130 or max(p.y for p in points)<-130 or min(p.y for p in points)>180:continue
    architecture.append(obj)
arch=tree(architecture)
receipt={'scene':bpy.data.filepath,'route':[],'missing_seat_floors':[],'low_seat_clearance':[]}
for x in [49.5,51,52.5]:
    for i in range(139):
        y=174-i*.5
        expected=15.38 if y>=109.5 else 13.4+(y-105)*(15.38-13.4)/4.5
        hit=arch.ray_cast(Vector((x,y,expected+.45)),Vector((0,0,-1)),1)
        floor=hit[0].z if hit[0] is not None else None
        body=arch.ray_cast(Vector((x,y,(floor if floor is not None else expected)+1.6)),Vector((0,-1,0)),.48)
        ceiling=arch.ray_cast(Vector((x,y,(floor if floor is not None else expected)+.1)),Vector((0,0,1)),2.0)
        receipt['route'].append({'x':x,'y':y,'floor':None if floor is None else round(floor,4),
          'blocked':body[0] is not None,'low_ceiling':ceiling[0] is not None})
for side in ['RF','LF']:
    collection=bpy.data.collections['D2_V13 '+side+' seating return']
    floor_tree=tree([o for o in collection.objects if o.name.endswith('concrete')])
    obj=bpy.data.objects['D2_'+side+' return individual seats']
    for i,v in enumerate(obj.data.vertices):
        p=v.co
        hit=floor_tree.ray_cast(p+Vector((0,0,.09)),Vector((0,0,-1)),.5)
        if hit[0] is None:receipt['missing_seat_floors'].append({'side':side,'index':i,'position':list(p)})
        ceiling=arch.ray_cast(p+Vector((0,0,.95)),Vector((0,0,1)),1.15)
        if ceiling[0] is not None:receipt['low_seat_clearance'].append({'side':side,'index':i,'position':list(p),'clearance':ceiling[3]+.95})
rf_seats=bpy.data.objects['D2_RF return individual seats']
receipt['river_side_upper_seats']=[list(v.co) for v in rf_seats.data.vertices if v.co.z>24.1]
if receipt['river_side_upper_seats']:raise RuntimeError('Rejected river-side upper seating returned')
receipt['route_gaps']=[r for r in receipt['route'] if r['floor'] is None]
receipt['route_obstructions']=[r for r in receipt['route'] if r['blocked'] or r['low_ceiling']]
receipt['max_route_step']=max(abs(a['floor']-b['floor']) for a,b in zip(receipt['route'],receipt['route'][1:]) if a['x']==b['x'] and a['floor'] is not None and b['floor'] is not None)
(ROOT/'review/v13/geometry-verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('V13_VERIFY',json.dumps({k:len(v) if isinstance(v,list) else v for k,v in receipt.items()}))
if receipt['route_gaps'] or receipt['route_obstructions'] or receipt['missing_seat_floors'] or receipt['low_seat_clearance']:
    raise RuntimeError('V13 geometry checks failed; inspect geometry-verification.json')
