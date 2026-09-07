"""Isolated form comparisons, explicitly not stadium sightlines."""
import bpy,sys,os,math,bmesh
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent;sys.path.insert(0,str(OUT))
from r2_lighting import apply_lighting
from r3_skyline import _center
scene=bpy.data.scenes['Railyards v4'];apply_lighting(scene,'south')
for collection in bpy.data.collections:
 if collection.name.startswith('D2_'):collection.hide_render=collection.name!='D2_Skyline landmarks'
for obj in scene.objects:
 if not obj.name.startswith('D2_Skyline landmarks') and obj.type not in ['LIGHT','CAMERA']:obj.hide_render=True
scene.render.engine='BLENDER_EEVEE';scene.eevee.taa_render_samples=64;scene.render.resolution_x=900;scene.render.resolution_y=900;scene.render.resolution_percentage=100
cam=bpy.data.objects.new('R9_Form comparison',bpy.data.cameras.new('R9_Form comparison'));scene.collection.objects.link(cam);scene.camera=cam;cam.data.type='ORTHO';cam.data.clip_start=.1;cam.data.clip_end=1000
originals=[o for o in scene.objects if o.type=='MESH' and o.name.startswith('D2_Skyline landmarks')]
folder=OUT/'review/v9/forms';folder.mkdir(parents=True,exist_ok=True)
for name,identifier,height in [('willis','willis-tower',527),('regis','st-regis-chicago',362.9),('pru','two-prudential-plaza',303.3)]:
 cx,cy=_center(identifier)
 copies=[]
 radius={'willis':70,'regis':65,'pru':42}[name]
 for original in originals:
  original.hide_render=True
  data=original.data.copy();mesh=bmesh.new();mesh.from_mesh(data)
  remove=[v for v in mesh.verts if math.hypot(v.co.x-cx,v.co.y-cy)>radius]
  bmesh.ops.delete(mesh,geom=remove,context='VERTS');mesh.to_mesh(data);mesh.free()
  if len(data.polygons):
   obj=bpy.data.objects.new('R9_Form mesh',data);scene.collection.objects.link(obj);copies.append(obj)
  else:bpy.data.meshes.remove(data)
 aim=Vector((cx,cy,8+height/2));cam.location=aim+Vector((280,-470,90));cam.rotation_euler=(aim-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=height*1.15
 scene.render.filepath=str(folder/f'{name}-{os.environ.get("RAILYARDS_LABEL","after")}.png');bpy.ops.render.render(write_still=True)
 for obj in copies:
  data=obj.data;bpy.data.objects.remove(obj,do_unlink=True);bpy.data.meshes.remove(data)
