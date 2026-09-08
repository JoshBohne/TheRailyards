"""Fixed preview cameras for the user-visible V13 live review."""
import bpy,sys,os
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from r2_lighting import apply_lighting
s=bpy.data.scenes['Railyards v4'];bpy.context.window.scene=s
out=Path(__file__).resolve().parent/'review/v13';out.mkdir(exist_ok=True)
apply_lighting(s,'south')
s.render.engine='CYCLES';s.cycles.samples=12
s.render.resolution_x=1200;s.render.resolution_y=750;s.render.resolution_percentage=100
shots={'corner':((197,55,98),(82,-43,30),48),'field':((8,28,16),(40,115,24),26),'tower':((25,20,28),(89,-51,33),30),'entrance':((51,176,17.05),(51,117,16.3),26),'lf':((30,68,17),(-4,131,26),32)}
label=os.environ.get('LABEL','before');selected=os.environ.get('VIEWS','field,tower,entrance,lf,north').split(',')
for name in selected:
 if name in ['north','south','bridge']:
  apply_lighting(s,name);s.camera=bpy.data.objects['R2_'+name]
  s.render.resolution_y=round(1200*1294/1944)
 else:
  apply_lighting(s,'south');pos,target,lens=shots[name]
  c=bpy.data.cameras.new('Review '+name);o=bpy.data.objects.new('Review '+name,c);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-Vector(pos)).to_track_quat('-Z','Y').to_euler();c.lens=lens;c.clip_end=20000;s.camera=o;s.render.resolution_y=750
 s.render.filepath=str(out/f'{label}-{name}.png');bpy.ops.render.render(write_still=True)
