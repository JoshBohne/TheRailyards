"""Saved-scene checks for this context pass; visual acceptance is separate."""
import hashlib
import json
import sys
from pathlib import Path
import bpy
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT))
from r2_lighting import apply_lighting
scene=bpy.context.scene
assert scene.get('riverfront_v13')
assert bpy.data.collections.get('D2_Future development') is None
assert bpy.data.collections.get('D2_Proposed soccer stadium') is None
assert bpy.data.collections.get('D2_Southern rail bascules') is None
assert bpy.data.objects['R2_OSM 155559109'].hide_render
collections=['R13_McDonalds Park','R13_Union Station powerhouse','R13_Rail bascules']
for mode in ['south','north','bridge','night']:
    apply_lighting(scene,mode)
    for name in collections:
        col=bpy.data.collections[name]
        assert len(col.objects)>0 and not col.hide_render and not col.hide_viewport,(mode,name)
# Scene refers only to packed or available images, excluding generated buffers.
missing=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and i.filepath and not Path(bpy.path.abspath(i.filepath)).exists()]
assert not missing,missing
path=Path(bpy.data.filepath)
report={'scene':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'checks':['speculative layer absent','old venue and bascules replaced','generic powerhouse hidden',
                  'new context visible in four lighting modes','external images available or packed'],
        'visual_evidence':['riverfront','district','powerhouse','bridges'],
        'limits':'Image-derived architecture and raised bridge pose, not surveyed geometry or operational status. Local saved-scene proof only.'}
(OUT/'review/v13/verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
