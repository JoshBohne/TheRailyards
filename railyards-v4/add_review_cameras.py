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
 'rf_corner_exterior':{'position':[175,-40,14],'target':[95,-10,20],'lens_mm':28,'purpose':'Low exterior view of the right-field / clock-tower end from the east bank'},
 'rf_corner_low_river':{'position':[135,60,6],'target':[100,-30,18],'lens_mm':24,'purpose':'Riverwalk-level view under the RF board toward the tower'},
 'rf_underside':{'position':[118,-8,9],'target':[90,10,16],'lens_mm':20,'purpose':'Close-up beneath the RF bleachers and board supports'},
 'rf_plan_ortho':{'position':[95,0,300],'target':[95,0,0],'ortho_scale':160,'purpose':'Orthographic plan of the RF corner: field polygon, board, supports, riverwalk'},
 'rf_section':{'position':[110,-320,20],'target':[110,20,20],'ortho_scale':70,'purpose':'Orthographic north-facing section through the RF board, bleachers, podium and riverwalk (use with clip)'},
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
