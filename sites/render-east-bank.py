"""Illustrative views from the future McDonald's Park side of the river."""
import bpy, json, os
from pathlib import Path
from mathutils import Vector
scene=bpy.data.scenes['Railyards v4'];bpy.context.window.scene=scene
out=Path(os.environ['RAILYARDS_EAST_OUT']);out.mkdir(parents=True,exist_ok=True)
scene.render.engine='BLENDER_EEVEE'
if hasattr(scene,'eevee'):scene.eevee.taa_render_samples=32
scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='JPEG';scene.render.image_settings.quality=92
for obj in scene.objects:
 if obj.name.startswith('D2_Distance atmosphere'):obj.hide_render=True
cam=bpy.data.objects.new('East bank gallery camera',bpy.data.cameras.new('East bank gallery camera'));scene.collection.objects.link(cam);scene.camera=cam;cam.data.clip_end=18000
views=[('east-bank-waterfront',(205,65,10),(48,65,24),24),('east-bank-terrace',(250,65,28),(35,65,24),32),('east-bank-north',(199,180,18),(30,48,27),27)]
for name,position,target,lens in views:
 cam.location=position;cam.data.lens=lens;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
 scene.render.filepath=str(out/(name+'.jpg'));bpy.ops.render.render(write_still=True)
(out/'east-bank-receipt.json').write_text(json.dumps({'scene':bpy.data.filepath,'views':views,'note':'Illustrative opposite-bank positions near the future Chicago Fire McDonalds Park site, not surveyed spectator sightlines.'},indent=2))
