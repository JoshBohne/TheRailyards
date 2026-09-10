"""Apply V15 corrections to a preserved consolidated V14 source scene."""
import hashlib,json,os,sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from r2_geometry import MeshBatch
import r15_scoreboard
source=Path(bpy.data.filepath)
scene=bpy.data.scenes['Railyards v4'];bpy.context.window.scene=scene
if not scene.get('site_release') or scene.get('v15_corrections'):
    raise ValueError('Expected an unchanged consolidated V14 site scene')
spec=json.loads((ROOT/'scene-spec.json').read_text())
materials={m.name[3:]:m for m in bpy.data.materials if m.name.startswith('D2_') and '.' not in m.name}
batch=MeshBatch(scene,materials)
receipt={'source':str(source),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest()}
receipt['scoreboard']=r15_scoreboard.align_scoreboards(scene,batch,spec)
for name in os.environ.get('V15_MODULES','r15_circulation,r15_seating,r15_rf_corner,r15_cameras,r15_geography,r15_landmarks').split(','):
    if name:
        module=__import__(name)
        receipt[name]=module.build(scene,batch,ROOT)
receipt['cf_centering']=r15_scoreboard.center_cf_on_terrace(scene,spec)
receipt['pinwheels']=r15_scoreboard.build(scene,batch,spec)
batch.flush()
receipt['pinwheel_animation']=r15_scoreboard.animate(scene)
active=0
for obj in scene.objects:
    if obj.type!='MESH' or obj.data.polygons or 'seat' not in obj.name.lower() or 'source' in obj.name.lower():continue
    scales=obj.data.attributes.get('scale')
    active+=sum(1 for i in range(len(obj.data.vertices)) if scales is None or scales.data[i].vector.length>.1)
scene['seat_count']=active
receipt['activeSeats']=active
receipt['generators']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('*15*.py')}
scene['v15_corrections']=json.dumps(receipt)
scene['stage']='V15 seating, concourse and geographic corrections'
scene['v15_cf_scoreboard_top']=json.dumps(spec['anchors']['cf_scoreboard_top'])
out=Path(os.environ.get('V15_SCENE','work/v15/railyards-v15-static.blend'));out.parent.mkdir(parents=True,exist_ok=True)
if out.resolve()==source.resolve():raise ValueError('Preserved input may not be overwritten')
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
receipt['outputSha256']=hashlib.sha256(out.read_bytes()).hexdigest()
out.with_suffix('.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('V15_BUILD',json.dumps(receipt))
