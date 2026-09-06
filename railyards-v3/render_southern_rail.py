"""Geographic close-up of the rail bascules outside the fitted B6 crop."""
import bpy,sys,json,time,os
from pathlib import Path
OUT=Path(__file__).resolve().parent;sys.path.insert(0,str(OUT))
from r2_lighting import apply_lighting
scene=bpy.data.scenes['Railyards v3'];bpy.context.window.scene=scene
apply_lighting(scene,'south')
scene.camera=bpy.data.objects['R3_southern_rail_detail']
scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.cycles.samples=48
scene.render.filepath=str(OUT/'southern-rail-detail.png');start=time.monotonic()
bpy.ops.render.render(write_still=True)
(OUT/'southern-rail-render.json').write_text(json.dumps({'file':bpy.data.filepath,'camera':scene.camera.name,'image':'southern-rail-detail.png','seconds':round(time.monotonic()-start,3),'purpose':'Inspect geolocated rail bridge geometry; not a fitted AECOM view'},indent=2)+'\n')
