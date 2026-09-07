"""Render contact and two replay perspectives from the saved V10 authoring file."""
import bpy
from pathlib import Path
OUT=Path(__file__).resolve().parent
scene=bpy.data.scenes['Railyards v4'];bpy.context.window.scene=scene
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=1400;scene.render.resolution_y=875;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
dest=OUT/'review/v10';dest.mkdir(parents=True,exist_ok=True)
for view,seconds in [('contact',1.55),('aerial',4.3),('boat',8.3)]:
 scene.camera=bpy.data.objects['R10_'+view];scene.frame_set(round(seconds*60))
 scene.render.filepath=str(dest/f'{view}.png');bpy.ops.render.render(write_still=True)
