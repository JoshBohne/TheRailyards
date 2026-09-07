"""Save a separate V8 night scene after the V4-V7 generator chain."""
import sys
from pathlib import Path
import bpy

OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT))
from r2_lighting import apply_lighting

scene = bpy.data.scenes['Railyards v4']
bpy.context.window.scene = scene
apply_lighting(scene, 'night')
scene.camera = bpy.data.objects['R3_v4_press_box']
scene['stage'] = 'V8: V7 geometry with illustrative landmark windows and night lighting'
scene['night_assumptions'] = '3.0 m window bays, 3.8 m floors, deterministic illustrative occupancy; not surveyed interiors'
bpy.ops.wm.save_as_mainfile(filepath=str(__import__('pathlib').Path(__import__('os').environ.get('RAILYARDS_STAGE_DIR',str(OUT)))/'railyards-v8.blend'), compress=True)
print('Saved V8:', bpy.data.filepath)
