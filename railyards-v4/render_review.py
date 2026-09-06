"""Render the persisted V4 review cameras with the daylight (south) preset."""
import bpy,json,time,os,sys
from pathlib import Path
OUT=Path(__file__).resolve().parent;sys.path.insert(0,str(OUT))
from r2_lighting import apply_lighting
scene=bpy.data.scenes['Railyards v4'];bpy.context.window.scene=scene
shots=json.loads((OUT/'review-cameras.json').read_text())
apply_lighting(scene,'south')
for group in ['D2_Future development','D2_Proposed soccer stadium','D2_South source rail links','D2_South source landing buildings','D2_South source medical branding']:
    if bpy.data.collections.get(group):bpy.data.collections[group].hide_render=True
if bpy.data.collections.get('D2_Pedestrian rail bridges'):bpy.data.collections['D2_Pedestrian rail bridges'].hide_render=False
label=os.environ.get('RAILYARDS_LABEL','review');outdir=OUT/os.environ.get('RAILYARDS_OUTDIR','review');outdir.mkdir(exist_ok=True)
width=int(os.environ.get('RAILYARDS_WIDTH','1400'));samples=int(os.environ.get('RAILYARDS_SAMPLES','32'))
receipts=[]
for name in os.environ.get('RAILYARDS_REVIEW_VIEWS',','.join(shots)).split(','):
    cam=bpy.data.objects['R3_v4_'+name];scene.camera=cam
    if name=='rf_section':cam.data.clip_start=300;cam.data.clip_end=345  # slice y in [-20,25]
    scene.render.resolution_x=width;scene.render.resolution_y=round(width*(1.0 if name=='geo_map' else .625))
    scene.cycles.samples=samples;scene.render.filepath=str(outdir/f'{label}-{name}.png');t=time.monotonic()
    bpy.ops.render.render(write_still=True)
    receipts.append({'view':name,'image':Path(scene.render.filepath).name,'seconds':round(time.monotonic()-t,2),'source_scene':bpy.data.filepath,'purpose':shots[name]['purpose']})
(outdir/f'{label}-review-renders.json').write_text(json.dumps(receipts,indent=2)+'\n');print(json.dumps(receipts))
