"""Read actual saved meshes to verify the release's tower/arcade alignment."""
import bpy,hashlib,json,math,os
from pathlib import Path
from mathutils import Vector
s=bpy.data.scenes['Railyards v4'];bpy.context.window.scene=s
source=Path(bpy.data.filepath)
tower=bpy.data.objects['D2_Clock tower brick_light'];river_face=max((tower.matrix_world@v.co).x for v in tower.data.vertices)
roof=bpy.data.objects['D2_V14 Flush RF frontage stone'];pts=[roof.matrix_world@v.co for v in roof.data.vertices]
roofz=28.6;roofpts=[(i,p) for i,p in enumerate(pts) if abs(p.z-roofz)<.001]
frontage_face=max(p.x for i,p in roofpts)
corner=min((p for i,p in roofpts if abs(p.x-river_face)<.001),key=lambda p:p.y)
indices={i for i,p in roofpts if (p-corner).length<.001}
neighbors=[]
for edge in roof.data.edges:
 a,b=edge.vertices
 if a in indices or b in indices:
  other=pts[b if a in indices else a]
  if abs(other.z-corner.z)<.001 and (other-corner).length>.001:neighbors.append(other-corner)
angles=[math.degrees(a.angle(b)) for a in neighbors for b in neighbors if a!=b]
right=min(angles,key=lambda a:abs(a-90))
active=0
for obj in s.objects:
 if obj.type=='MESH' and not obj.data.polygons and 'individual seats' in obj.name.lower():
  scales=obj.data.attributes.get('scale');active+=sum(1 for i in range(len(obj.data.vertices)) if not scales or scales.data[i].vector.length>.1)
assert abs(frontage_face-river_face)<.001
assert abs(right-90)<.001
assert active==33997
receipt={'scene':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'towerRiverFaceX':river_face,'arcadeRoofRiverFaceX':frontage_face,'cornerAngleDegrees':right,'activeSeats':active,'limitations':'Checks the named exterior alignment and active seat count. Not full-stadium architectural or feasibility approval.'}
out=Path(os.environ['RAILYARDS_SCENE_CHECK']);out.write_text(json.dumps(receipt,indent=2)+'\n');print('SCENE_CHECK',json.dumps(receipt))
