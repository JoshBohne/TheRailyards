"""Repair audited V13 geometry while preserving its saved baseline."""
import bpy,json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from r2_geometry import MeshBatch
from r14_audit import build
source=Path(bpy.data.filepath)
if source.name!='railyards-v13-static.blend':raise ValueError(f'Expected preserved V13 static input, got {source}')
input_hash=hashlib.sha256(source.read_bytes()).hexdigest()
expected_hash='22b7801e6d0bfab64c73d82e2e18efe8dc64aea0fba1e6b5db00dbadd17cbb95'
if input_hash!=expected_hash:raise ValueError(f'Preserved V13 hash mismatch: {source} has {input_hash}')
scene=bpy.data.scenes['Railyards v4'];bpy.context.window.scene=scene
materials={m.name[3:]:m for m in bpy.data.materials if m.name.startswith('D2_') and '.' not in m.name}
batch=MeshBatch(scene,materials)
receipt=build(scene,batch,ROOT)
batch.flush()
from r14_tower import finalize_tower
receipt['A05_final_portals']=finalize_tower(scene,receipt)
active_seats=0
for obj in scene.objects:
    if obj.type!='MESH' or obj.data.polygons or 'seat' not in obj.name.lower() or 'source' in obj.name.lower():continue
    scales=obj.data.attributes.get('scale')
    active_seats+=sum(1 for i in range(len(obj.data.vertices)) if scales is None or scales.data[i].vector.length>.1)
scene['seat_count']=active_seats
receipt['active_seats']=active_seats
receipt['input_sha256']=input_hash
scene['v14_audit']=json.dumps(receipt)
scene['stage']='V14: independent stadium audit repairs'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'railyards-v14-static.blend'),compress=True)
out=ROOT/'review/v14';out.mkdir(parents=True,exist_ok=True)
(out/'build-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('V14_BUILD',json.dumps(receipt))
