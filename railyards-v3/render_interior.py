"""Small fixed-camera interior previews; sunlight exposes geometry clearly."""
import bpy,json,time,sys,os
from pathlib import Path
OUT=Path(__file__).resolve().parent;sys.path.insert(0,str(OUT))
from r2_lighting import apply_lighting
scene=bpy.data.scenes['Railyards v3'];bpy.context.window.scene=scene
shots=json.loads((OUT/'interior-cameras.json').read_text());receipts=[]
apply_lighting(scene,'south')
bpy.data.collections['D2_Future development'].hide_render=True
for group in ['D2_South source rail links','D2_South source landing buildings','D2_Proposed soccer stadium','D2_South source medical branding']:
    if bpy.data.collections.get(group):bpy.data.collections[group].hide_render=True
if bpy.data.collections.get('D2_Pedestrian rail bridges'):bpy.data.collections['D2_Pedestrian rail bridges'].hide_render=False
for name in os.environ.get('RAILYARDS_INTERIOR_VIEWS',','.join(shots)).split(','):
    scene.camera=bpy.data.objects['R3_'+name];scene.render.resolution_x=int(os.environ.get('RAILYARDS_WIDTH','1600'));scene.render.resolution_y=round(scene.render.resolution_x*.625);scene.cycles.samples=int(os.environ.get('RAILYARDS_SAMPLES','48'))
    scene.render.use_border=False;scene.render.filepath=str(OUT/('interior-'+name+'.png'));t=time.monotonic();bpy.ops.render.render(write_still=True)
    receipts.append({'view':name,'seconds':round(time.monotonic()-t,3),'source_scene':bpy.data.filepath,'purpose':'Geometry and visibility review, not final fidelity'})
(OUT/'interior-renders.json').write_text(json.dumps(receipts,indent=2)+'\n');print(json.dumps(receipts))
