"""Broadcast-style view from behind home plate for the V12 home-run edit.

Static elevated camera behind the plate (no backstop net in shot: the
protection screen is hidden for this view), sharing the replay's animation
clock.  RAILYARDS_TV_OUT sets the frame folder; RAILYARDS_TV_FRAMES a
comma-separated frame list (default 0-239 at 24 fps).
"""
import bpy,os,sys,json
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent;sys.path.insert(0,str(OUT))
from r2_lighting import apply_lighting
scene=bpy.data.scenes['Railyards v4'];bpy.context.window.scene=scene
apply_lighting(scene,os.environ.get('RAILYARDS_PRESET','south'))
for n in ['D2_Future development','D2_Proposed soccer stadium','D2_South source rail links','D2_South source landing buildings','D2_South source medical branding']:
    c=bpy.data.collections.get(n)
    if c:c.hide_render=True
net=bpy.data.objects.get('D2_Backstop protection metal')
if net:net.hide_render=True
scene.render.engine='BLENDER_EEVEE';scene.eevee.taa_render_samples=int(os.environ.get('RAILYARDS_SAMPLES','16'))
scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
for o in scene.objects:
    if o.name.startswith('D2_Distance atmosphere'):o.hide_render=True
out=Path(os.environ.get('RAILYARDS_TV_OUT',str(OUT/'review/v12/tv')));out.mkdir(parents=True,exist_ok=True)
cam=bpy.data.objects.new('TV home plate',bpy.data.cameras.new('TV home plate'));scene.collection.objects.link(cam);scene.camera=cam
pos=Vector((-15.5,-15.5,17.5));target=Vector((52,52,13.5))
cam.location=pos;cam.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler();cam.data.lens=42;cam.data.clip_end=18000
frames=[int(x) for x in os.environ.get('RAILYARDS_TV_FRAMES','').split(',') if x] or range(240)
for frame in frames:
    scene.frame_set(round(frame/24*60));scene.render.filepath=str(out/f'{frame:04d}.png');bpy.ops.render.render(write_still=True)
(out/'receipt.json').write_text(json.dumps({'scene':bpy.data.filepath,'fps':24,'frames':len(list(frames)),'camera':list(pos),'target':list(target),'lens':42,'net_hidden':bool(net),'note':'Illustrative play; static broadcast-style camera behind the plate.'},indent=2))
print('TV_DONE',out)
