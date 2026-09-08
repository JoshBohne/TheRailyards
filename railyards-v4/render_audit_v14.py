"""Fixed audit and source cameras, rendered from the saved correction scene."""
import bpy,sys,os
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from r2_lighting import apply_lighting
s=bpy.data.scenes['Railyards v4'];bpy.context.window.scene=s
s.render.engine='CYCLES';s.cycles.samples=16
s.render.resolution_x=1200;s.render.resolution_y=800;s.render.resolution_percentage=100
shots={'bank-front':((51,91,18),(47,115,18),38),'bank-underneath':((43,142,18),(44,116,19),32),'park-underpass':((51,156,17),(51,107,16),28),'lf-roof-field':((38,115,37),(-15,145,36),35),'lf-roof-rear':((38,181,47),(-12,143,37),38),'tower-access':((65,-47,35),(77,-72,35),24),'south-bridges':((-180,-240,60),(-80,-115,20),40)}
shots['tower-plan']=((70,-35,220),(70,-35,0),48)
shots['tower-corner']=((197,55,98),(98,-43,30),48)
shots['frontage']=((170,-215,58),(59,-103,26),48)
shots['lantern-clearance']=((-48,-7,46),(-64,-7,47),42)
out=Path(os.environ.get('REVIEW_OUT',str(ROOT/'review/v14')));out.mkdir(exist_ok=True,parents=True)
for name in os.environ.get('VIEWS','bank-front,bank-underneath,park-underpass').split(','):
 if name in ['north','south','bridge']:
  apply_lighting(s,name);s.camera=bpy.data.objects['R2_'+name]
 else:
  apply_lighting(s,'south');p,t,lens=shots[name]
  c=bpy.data.cameras.new('V14 review '+name);o=bpy.data.objects.new(c.name,c);s.collection.objects.link(o);o.location=p;o.rotation_euler=(Vector(t)-Vector(p)).to_track_quat('-Z','Y').to_euler();c.lens=lens;c.clip_end=20000;s.camera=o
  if name=='tower-plan':c.type='ORTHO';c.ortho_scale=175
 s.render.filepath=str(out/f'{name}.png');bpy.ops.render.render(write_still=True)
