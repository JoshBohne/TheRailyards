"""Small fixed-camera previews from a saved scene, with hash provenance."""
import hashlib,json,os,sys
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from r2_lighting import apply_lighting
if os.environ.get('V15_CAMERA_STUDY')=='1':
    from r15_cameras import apply
    apply()
scene=bpy.data.scenes['Railyards v4'];bpy.context.window.scene=scene
source=Path(bpy.data.filepath);sha=hashlib.sha256(source.read_bytes()).hexdigest()
out=Path(os.environ.get('V15_OUT','work/v15/review'));out.mkdir(parents=True,exist_ok=True)
label=os.environ.get('V15_LABEL','after')
shots={'concourse':((69,181,21),(64,119,17),26),
       'passage':((51,174,15.1),(51,119,15.1),24),
       'overlook':((51,117,15.1),(43,55,12),24),
       'home':((-17,-23,20),(48,96,27),28),
       'lf':((73,64,64),(-3,125,24),45),
       'lf-section-stack':((75,72,58),(-10,139,28),48),  # V14 audit camera Josh annotates
       'rf':((167,39,75),(77,-33,26),45),
       'geography':((100,1500,2800),(100,900,0),45)}
for name in os.environ.get('V15_VIEWS','north,bridge,concourse,home').split(','):
    apply_lighting(scene,name if name in ['north','south','bridge'] else 'south')
    if name in ['north','south','bridge']:scene.camera=bpy.data.objects['R2_'+name]
    else:
        pos,target,lens=shots[name]
        camera=bpy.data.cameras.new('V15 '+name);obj=bpy.data.objects.new(camera.name,camera);scene.collection.objects.link(obj)
        obj.location=pos;obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler();camera.lens=lens;camera.clip_end=20000
        if name=='geography':camera.type='ORTHO';camera.ortho_scale=3800
        scene.camera=obj
    scene.render.engine='CYCLES';scene.cycles.samples=int(os.environ.get('V15_SAMPLES','12'))
    if os.environ.get('V15_GPU')=='1':scene.cycles.device='GPU'
    scene.render.resolution_x=int(os.environ.get('V15_WIDTH','1000'));scene.render.resolution_y=round(scene.render.resolution_x*2/3);scene.render.resolution_percentage=100
    scene.render.filepath=str(out/f'{label}-{name}.png');bpy.ops.render.render(write_still=True)
    receipt={'sceneSha256':sha,'camera':{'position':list(scene.camera.location),'rotation':list(scene.camera.rotation_euler),'lens':scene.camera.data.lens},'imageSha256':hashlib.sha256(Path(scene.render.filepath).read_bytes()).hexdigest()}
    Path(scene.render.filepath).with_suffix('.json').write_text(json.dumps(receipt,indent=2)+'\n')
    if label=='after':
        ready=[p.stem.removeprefix('after-') for p in out.glob('after-*.png')]
        (out/'status.json').write_text(json.dumps({'message':'V15 saved-scene preview. Geometry is under review; unfinished views retain the V14 baseline.','ready':ready,'updated':sha[:12]}))
