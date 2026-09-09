import bpy,json,sys,os,hashlib
from pathlib import Path
from mathutils import Vector
SOURCE_SHA=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
root=Path(__file__).resolve().parents[1]/'railyards-v4';sys.path.insert(0,str(root))
from r2_lighting import apply_lighting
s=bpy.data.scenes['Railyards v4'];bpy.context.window.scene=s
apply_lighting(s,'night');s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=1280;s.render.resolution_y=800;s.render.resolution_percentage=100
if os.environ.get('RAILYARDS_GPU')=='1':s.cycles.device='GPU'
out=Path(os.environ.get('RAILYARDS_STILLS_OUT',str(root.parent/'work/night-game/stills')));out.mkdir(parents=True,exist_ok=True)
cam=bpy.data.objects.new('Site gallery camera',bpy.data.cameras.new('Site gallery camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.clip_end=18000
views=json.loads((root/'experience-cameras.json').read_text())
views.update({name:{'position':p,'target':t,'lens':l} for name,p,t,l in [('home-plate',(-24,-30,30),(80,100,28),22),('above-diamond',(-54,-68,102),(46,32,19),32),('rf-corner',(158,15,63),(30,45,20),25),('east-bank-waterfront',(205,65,10),(48,65,24),24),('east-bank-terrace',(250,65,28),(35,65,24),32),('east-bank-north',(199,180,18),(30,48,27),27)]})
selected=set(filter(None,os.environ.get('VIEWS','').split(',')))
for name,v in views.items():
 if selected and name not in selected:continue
 cam.location=v['position'];cam.data.lens=v['lens'];cam.rotation_euler=(Vector(v['target'])-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(out/f'{name}.png');bpy.ops.render.render(write_still=True)
 image=Path(s.render.filepath)
 image.with_suffix('.render.json').write_text(json.dumps({'sourceStaticSha256':SOURCE_SHA,'imageSha256':hashlib.sha256(image.read_bytes()).hexdigest(),'camera':v,'generator':Path(__file__).name},indent=2)+'\n')
