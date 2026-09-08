"""Fixed before/after cameras, rendered from the saved scene in a new process."""
import os
import sys
from pathlib import Path
import bpy
from mathutils import Vector
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT))
from r2_lighting import apply_lighting
scene=bpy.context.scene
apply_lighting(scene,'south')
for name in ['D2_Distance atmosphere','D2_South source rail links','D2_South source landing buildings','D2_South source medical branding']:
 col=bpy.data.collections.get(name)
 if col:col.hide_render=True
scene.render.engine='BLENDER_EEVEE'
scene.eevee.taa_render_samples=24
scene.render.resolution_x=1200;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
dest=OUT/'review'/'v13'/os.environ.get('RAILYARDS_COMPARE','after');dest.mkdir(parents=True,exist_ok=True)
views={'riverfront':((180,-175,47),(315,102,23),34),
       'district':((-280,-620,390),(240,65,8),38),
       'powerhouse':((170,365,47),(94,450,28),50),
       'bridges':((40,-490,53),(197,-380,40),42)}
for name,(position,target,lens) in views.items():
 data=bpy.data.cameras.new('R13_'+name);camera=bpy.data.objects.new('R13_'+name,data);scene.collection.objects.link(camera)
 camera.location=position;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();data.lens=lens;data.clip_end=12000
 scene.camera=camera;scene.render.filepath=str(dest/(name+'.png'));bpy.ops.render.render(write_still=True)
 bpy.data.objects.remove(camera,do_unlink=True)
