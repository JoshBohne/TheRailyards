"""Render fixed experience views or a sampled camera move from saved V9.

All image frames are native Blender renders. Encoding is a separate step.
"""
import bpy,json,os,sys,math,time
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent;sys.path.insert(0,str(OUT))
from r2_lighting import apply_lighting
from r3_public_realm import deck_z
scene=bpy.data.scenes['Railyards v4'];bpy.context.window.scene=scene
apply_lighting(scene,os.environ.get('RAILYARDS_PRESET','south'))
for name in ['D2_Future development','D2_Proposed soccer stadium','D2_South source rail links','D2_South source landing buildings','D2_South source medical branding']:
 col=bpy.data.collections.get(name)
 if col:col.hide_render=True
# Keep the public scenes focused on present-day skyline context.
engine=os.environ.get('RAILYARDS_ENGINE','CYCLES');scene.render.engine=engine
width=int(os.environ.get('RAILYARDS_WIDTH','1600'));scene.render.resolution_x=width;scene.render.resolution_y=round(width*9/16);scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.cycles.samples=int(os.environ.get('RAILYARDS_SAMPLES','32'))
if engine=='BLENDER_EEVEE':
 scene.eevee.taa_render_samples=int(os.environ.get('RAILYARDS_SAMPLES','32'))
# Ambient volume is expensive/noisy in motion. Retain it for Cycles stills.
if engine=='BLENDER_EEVEE':
 for obj in scene.objects:
  if obj.name.startswith('D2_Distance atmosphere'):obj.hide_render=True
mode=os.environ.get('RAILYARDS_MOTION','still');names=os.environ.get('RAILYARDS_VIEWS','arrival,left_center,boat,river_shot,skyline_west,skyline_east').split(',')
folder=OUT/os.environ.get('RAILYARDS_OUTDIR','review/v9');folder.mkdir(parents=True,exist_ok=True);receipts=[]
for name in names:
 key='R9_'+name
 if key not in bpy.data.objects:
  shot=json.loads((OUT/'experience-cameras.json').read_text())[name]
  cam=bpy.data.objects.new(key,bpy.data.cameras.new(key));scene.collection.objects.link(cam)
  cam.location=shot['position'];cam.rotation_euler=(Vector(shot['target'])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=shot['lens'];cam.data.clip_end=12000
 scene.camera=bpy.data.objects[key]
 count=int(os.environ.get('RAILYARDS_FRAMES','120')) if mode!='still' else 1
 dest=folder/name if mode!='still' else folder
 dest.mkdir(parents=True,exist_ok=True)
 for index in range(count):
  t=index/max(1,count-1);smooth=t*t*(3-2*t)
  if mode!='still':
   if name=='arrival':
    y=294-111*smooth;x=50
    scene.camera.location=(x,y,deck_z(y)+1.7)
    aim=Vector((29,112,25))
   elif name=='left_center':
    x=37+8*smooth-2.5*math.exp(-((smooth-.5)/.13)**2);y=166-34*smooth
    scene.camera.location=(x,y,deck_z(y)+1.7);aim=Vector((8,40,19))
   elif name=='boat':
    scene.camera.location=(179,200-85*smooth,2.6+.07*math.sin(t*math.tau))
    aim=Vector((50,20,23))
   else:aim=scene.camera.location+scene.camera.rotation_euler.to_quaternion()@Vector((0,0,-1))
   scene.camera.rotation_euler=(aim-scene.camera.location).to_track_quat('-Z','Y').to_euler()
  scene.render.filepath=str(dest/(f'{index:04d}.png' if mode!='still' else f'{name}.png'))
  start=time.monotonic();bpy.ops.render.render(write_still=True)
  receipts.append({'view':name,'frame':index,'path':str(Path(scene.render.filepath).relative_to(OUT)),'seconds':round(time.monotonic()-start,2),'camera':list(scene.camera.location)})
(folder/f'{mode}-{names[0]}-receipt.json').write_text(json.dumps({'scene':bpy.data.filepath,'engine':engine,'width':width,'frames':receipts},indent=2)+'\n')
