"""Apply V11 circulation to the preserved V9 source and save a new scene.

Blender -b railyards-v4/railyards-v9.blend --python railyards-v4/build_circulation_v11.py
The V10 replay and all earlier saved scenes remain unchanged.
"""
import bpy,json,sys
from pathlib import Path
OUT=Path(__file__).resolve().parent;sys.path.insert(0,str(OUT))
from r2_geometry import MeshBatch
from r3_public_realm import build_public_realm,ROOF_PIXELS as PARK_PIXELS,ROAD_Y,ROAD_Z,GRADE
from r3_reference_projection import source_to_grade,source_to_plane
from r3_restaurant import ROOF_PIXELS
from r11_circulation import regrade_restaurant,connect_outfield,terrace_z,open_lower_landings,build_terrace_surface
from r2_lighting import apply_lighting
scene=bpy.data.scenes['Railyards v4'];bpy.context.window.scene=scene
if 'v9' not in Path(bpy.data.filepath).stem:raise ValueError('V11 circulation must start from preserved V9')
spec=json.loads((OUT/'scene-spec.json').read_text())
# Inspect both geographic inputs even though this pass retains registration.
skyline=json.loads((OUT/'skyline-buildings.json').read_text())
materials={m.name[3:]:m for m in bpy.data.materials if m.name.startswith('D2_') and '.' not in m.name}
for name in ['D2_Public realm','D2_Riverfront retail','D2_Left center arrival']:
    col=bpy.data.collections.get(name)
    if col:
        for obj in list(col.objects):bpy.data.objects.remove(obj,do_unlink=True)
        bpy.data.collections.remove(col)
batch=MeshBatch(scene,materials)
build_public_realm(scene,spec,batch,materials,circulation=True)
cam=bpy.data.objects['R2_north']
roof=[source_to_plane(scene,cam,p,(1944,1294),22)[:2] for p in ROOF_PIXELS]
entrance=[source_to_grade(scene,cam,p,(1944,1294),ROAD_Y,ROAD_Z,GRADE)[:2] for p in [(695,736),(808,668),(1050,689),(810,790)]]
from r9_arrival import SOURCE_POLYGON
front_terrace=[source_to_grade(scene,cam,p,(1944,1294),ROAD_Y,ROAD_Z,GRADE)[:2] for p in SOURCE_POLYGON]
regrade_restaurant(scene,batch,roof,entrance,front_terrace)
polygons=connect_outfield(batch,front_terrace)
park=[source_to_grade(scene,cam,p,(1944,1294),ROAD_Y,ROAD_Z,GRADE)[:2] for p in PARK_PIXELS]
build_terrace_surface(batch,polygons+[roof,entrance,park])
open_lower_landings(scene,batch,spec)
batch.flush()
# The board sits above, and is supported by, the public terrace. Keep its
# disputed horizontal anchor fixed. No RF-board geometry changes here.
board_base=terrace_z(126);screen_bottom=board_base+3.8;delta=screen_bottom-18
for obj in bpy.data.collections['D2_Scoreboards'].objects:
    if obj.type=='MESH':
        for v in obj.data.vertices:
            if v.co.y<80:continue
            if v.co.z<18:v.co.z=board_base+(v.co.z-13)/5*(screen_bottom-board_base)
            else:v.co.z+=delta
    elif obj.name.startswith('D2_cf_scoreboard_top'):obj.location.z+=delta
scene['v11_circulation']='Public deck continues onto graded restaurant terrace; source-led riverfront arcade, stepped quay and corner stair; inferred outfield-bank connections and supports.'
scene['v11_cf_board_bottom']=screen_bottom
scene['v11_source_boundaries']='Existing calibrated XY and geography retained. Source establishes continuity, arcade and quay section; grades, dimensions and unseen stair/structure design remain inferred.'
scene['stage']='V11: Roosevelt, outfield terrace and riverwalk circulation'
apply_lighting(scene,'south')
scene.camera=bpy.data.objects['R2_north']
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'railyards-v11-static.blend'),compress=True)
print('V11_CIRCULATION',json.dumps({'scene':bpy.data.filepath,'terrace_at_entry':terrace_z(161.8),'cf_board_bottom':screen_bottom,'objects':len(scene.objects)}))
