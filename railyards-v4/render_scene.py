"""Render selected v2 views from the active scene; invoked through Blender MCP."""
import bpy,json,time,os,sys
from pathlib import Path
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT))
from r2_lighting import apply_lighting
spec=json.loads((OUT/'scene-spec.json').read_text())
scene=bpy.data.scenes['Railyards v4'];bpy.context.window.scene=scene
views=os.environ.get('RAILYARDS_VIEWS','north,south,bridge').split(',')
label=os.environ.get('RAILYARDS_LABEL','gray')
width=int(os.environ.get('RAILYARDS_WIDTH','1200'));samples=int(os.environ.get('RAILYARDS_SAMPLES','24'))
receipts=[]
for name in views:
    if label!='gray':apply_lighting(scene,name)
    scene.camera=bpy.data.objects['R2_'+name]
    w,h=spec['cameras'][name]['size'];scene.render.resolution_x=width;scene.render.resolution_y=round(width*h/w)
    scene.cycles.samples=samples;scene.render.filepath=str(OUT/f'{label}-{name}.png')
    start=time.monotonic();bpy.ops.render.render(write_still=True)
    receipts.append({'camera':name,'image':Path(scene.render.filepath).name,'width':scene.render.resolution_x,'height':scene.render.resolution_y,'samples':samples,'seconds':round(time.monotonic()-start,3),'device':scene.cycles.device,'source_scene':bpy.data.filepath})
(OUT/f'{label}-renders.json').write_text(json.dumps(receipts,indent=2)+'\n')
print(json.dumps(receipts))
