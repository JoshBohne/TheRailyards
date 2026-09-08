"""Apply reproducible V13 corrections to a preserved V12 static scene."""
import hashlib
import json
import sys
from pathlib import Path
import bpy
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT))
from r2_geometry import MeshBatch
from r13_outfield import build
source=Path(bpy.data.filepath)
if source.name!='railyards-v12-static.blend':
    raise ValueError(f'Expected preserved V12 static scene, got {source}')
scene=bpy.data.scenes['Railyards v4']
bpy.context.window.scene=scene
materials={m.name[3:]:m for m in bpy.data.materials if m.name.startswith('D2_') and '.' not in m.name}
spec=json.loads((OUT/'scene-spec.json').read_text())
batch=MeshBatch(scene,materials)
receipt=build(scene,batch,spec)
batch.flush()
receipt['input_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
receipt['seat_count']=int(scene['seat_count'])
scene['v13_outfield']=json.dumps(receipt)
scene['stage']='V13: curved outfield seating and open park passage'
scene.camera=bpy.data.objects['R2_north']
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'railyards-v13-static.blend'),compress=True)
(OUT/'review/v13').mkdir(exist_ok=True,parents=True)
(OUT/'review/v13/build-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('V13_BUILD',json.dumps(receipt))
