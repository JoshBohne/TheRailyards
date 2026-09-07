"""Persist V9 geometry and experience cameras without overwriting V8."""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent;sys.path.insert(0,str(OUT))
from r2_lighting import apply_lighting
from r3_public_realm import deck_z
scene=bpy.data.scenes['Railyards v4']
shots={
 'arrival':{'position':[50,227,deck_z(227)+1.76],'target':[29,110,27],'lens':26},
 'left_center':{'position':[45,132,deck_z(132)+1.76],'target':[8,40,19],'lens':24},
 'boat':{'position':[179,165,2.6],'target':[50,20,23],'lens':24},
 'river_shot':{'position':[232,-140,170],'target':[63,48,18],'lens':33},
 'skyline_west':{'position':[-25,25,44],'target':[52,1574,255],'lens':52},
 'skyline_east':{'position':[-25,25,44],'target':[1350,2420,255],'lens':55},
}
col=bpy.data.collections['R2_Cameras']
for name,shot in shots.items():
 key='R9_'+name;cam=bpy.data.objects.get(key)
 if cam is None:
  cam=bpy.data.objects.new(key,bpy.data.cameras.new(key));col.objects.link(cam)
 cam.location=shot['position'];cam.rotation_euler=(Vector(shot['target'])-cam.location).to_track_quat('-Z','Y').to_euler()
 cam.data.lens=shot['lens'];cam.data.clip_start=.15;cam.data.clip_end=12000
# Keep the demonstrated public walking route clear of randomly scattered
# crowd instances. Vertex deletion preserves Geometry Nodes point attributes.
import bmesh
for obj in scene.objects:
 if obj.type=='MESH' and obj.name.startswith('D2_Public deck visitors'):
  mesh=bmesh.new();mesh.from_mesh(obj.data)
  blocked=[v for v in mesh.verts if (abs(v.co.x-50)<3.2 and 140<v.co.y<313) or (33<v.co.x<49 and 126<v.co.y<176)]
  bmesh.ops.delete(mesh,geom=blocked,context='VERTS');mesh.to_mesh(obj.data);mesh.free()
apply_lighting(scene,'south');scene.camera=bpy.data.objects['R9_arrival']
scene['stage']='V9: source-guided left-center arrival, landmark silhouettes, rendered web experiences'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'railyards-v9.blend'),compress=True)
(OUT/'experience-cameras.json').write_text(json.dumps(shots,indent=2)+'\n')
