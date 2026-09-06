"""Fixed V4 review cameras for structure, geography and skyline evidence.

These are diagnostic views, not fitted to source images. They are persisted in
the saved scene so before/after comparisons are reproducible from the file.
"""
import bpy,json
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
scene=bpy.data.scenes["Railyards v4"];col=bpy.data.collections['R2_Cameras']
shots={
 'home_plate_skyline':{'position':[-4.5,-4.5,13.7],'target':[45,60,44],'lens_mm':16,'purpose':'New view: from behind home plate, field level, the Loop and Museum Park towers over the outfield'},
 'press_box':{'position':[-33,-33,44],'target':[52,52,30],'lens_mm':24,'purpose':'New view: upper deck behind home plate looking out over the whole bowl to the skyline'},
 'roosevelt_bridge_west':{'position':[70,332,17.5],'target':[60,140,22],'lens_mm':28,'purpose':'New view: standing on Roosevelt Road looking south over the raised park to the outfield entry'},
 'north_park_entry':{'position':[92,240,23.5],'target':[35,105,24],'lens_mm':24,'purpose':'New view: on the raised park deck approaching the outfield entrance above the bleachers'},
 'riverwalk_north':{'position':[119.5,-60,9.6],'target':[121,320,14],'lens_mm':24,'purpose':'New view: lower riverwalk walking north, arcade left, river right, Roosevelt bridge ahead'},
 'east_bank':{'position':[200,62,9.5],'target':[75,-5,32],'lens_mm':30,'purpose':'New view: from the east bank across the river, the tower, board and river arcade'},
 'aerial_west':{'position':[-620,-140,270],'target':[160,160,20],'lens_mm':35,'purpose':'New aerial from the west over the rail yards, stadium and Museum Park cluster toward the lake'},
 'rf_corner_exterior':{'position':[175,-40,14],'target':[95,-10,20],'lens_mm':28,'purpose':'Low exterior view of the right-field / clock-tower end from the east bank'},
 'rf_corner_low_river':{'position':[135,60,6],'target':[100,-30,18],'lens_mm':24,'purpose':'Riverwalk-level view under the RF board toward the tower'},
 'rf_underside':{'position':[118,-8,9],'target':[90,10,16],'lens_mm':20,'purpose':'Close-up beneath the RF bleachers and board supports'},
 'rf_plan_ortho':{'position':[95,0,300],'target':[95,0,0],'ortho_scale':160,'purpose':'Orthographic plan of the RF corner: field polygon, board, supports, riverwalk'},
 'rf_section':{'position':[110,-320,20],'target':[110,20,20],'ortho_scale':70,'purpose':'Orthographic north-facing section through the RF board, bleachers, podium and riverwalk (use with clip)'},
 'rf_tower_junction':{'position':[150,-135,32],'target':[72,-72,26],'lens_mm':30,'purpose':'South-east view of the bowl end wall, link block and clock tower base (compare the south source crop)'},
 'east_lake':{'position':[-40,-40,60],'target':[3000,600,0],'lens_mm':24,'purpose':'Elevated east-facing view toward Lake Michigan over the near South Loop'},
 'east_lake_high':{'position':[-60,-60,140],'target':[2500,500,0],'lens_mm':30,'purpose':'Higher east view to confirm the shoreline beyond real land'},
 'geo_map':{'position':[1200,700,6000],'target':[1200,700,0],'ortho_scale':5200,'purpose':'Orthographic geographic map: shoreline, stadium, river, landmarks; +Y is north'},
}
for name,shot in shots.items():
    obj=bpy.data.objects.get('R3_v4_'+name)
    if obj is None:
        data=bpy.data.cameras.new('R3_v4_'+name);obj=bpy.data.objects.new(data.name,data);col.objects.link(obj)
    obj.location=shot['position'];obj.rotation_euler=(Vector(shot['target'])-obj.location).to_track_quat('-Z','Y').to_euler()
    if 'ortho_scale' in shot:obj.data.type='ORTHO';obj.data.ortho_scale=shot['ortho_scale']
    else:obj.data.type='PERSP';obj.data.lens=shot['lens_mm']
    obj.data.sensor_width=36;obj.data.sensor_fit='HORIZONTAL';obj.data.clip_start=.5;obj.data.clip_end=30000
    obj['purpose']=shot['purpose']
(OUT/'review-cameras.json').write_text(json.dumps(shots,indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath or str(OUT/'railyards-v4-detail.blend'))
