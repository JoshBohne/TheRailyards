"""Repeatable stadium-eye review views for outfield architecture and skyline."""
import bpy,json
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
scene=bpy.data.scenes['Railyards v3'];col=bpy.data.collections['R2_Cameras']
shots={
 'left_field_skyline':{'position':[-28,-33,39],'target':[19,1574,180],'lens_mm':22},
 'home_plate':{'position':[0,0,13.75],'target':[70,70,16],'lens_mm':22},
 'home_upper_deck':{'position':[-36,-41,41],'target':[70,70,24],'lens_mm':25},
 'third_base_seats':{'position':[-25,58,31.3],'target':[78,74,23],'lens_mm':26},
}
for name,shot in shots.items():
    obj=bpy.data.objects.get('R3_'+name)
    if obj is None:
        data=bpy.data.cameras.new('R3_'+name);obj=bpy.data.objects.new(data.name,data);col.objects.link(obj)
    obj.location=shot['position'];obj.rotation_euler=(Vector(shot['target'])-obj.location).to_track_quat('-Z','Y').to_euler()
    obj.data.lens=shot['lens_mm'];obj.data.sensor_width=36;obj.data.sensor_fit='HORIZONTAL';obj.data.clip_start=.12;obj.data.clip_end=15000
    obj['purpose']='Interior outfield visibility and architecture review; not fitted to an existing source image.'
(OUT/'interior-cameras.json').write_text(json.dumps(shots,indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'railyards-v3-detail.blend'))
