"""Unsaved cutaway view of the tower route; never changes the source scene."""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
from r14_tower import cut_box
from r2_lighting import apply_lighting
s=bpy.data.scenes['Railyards v4'];bpy.context.window.scene=s
cx,cy,_=json.loads(s['v14_tower_anchor'])
apply_lighting(s,'south')
keep=['Clock tower','V14 Tower interior','V14 Tower stairs','V14 Tower foundation','V14 Tower lift enclosure']
for obj in s.objects:
    if obj.type=='MESH' and not any(token in obj.name for token in keep):obj.hide_render=True
shell=[obj for obj in s.objects if 'Clock tower' in obj.name]
cut_box(s,shell,(cx-.5,cy-12,7.9),(cx+12,cy+12,48),'Review-only tower section')
c=bpy.data.cameras.new('Tower route cutaway');o=bpy.data.objects.new(c.name,c);s.collection.objects.link(o)
o.location=(cx+45,cy+17,31);o.rotation_euler=(Vector((cx-2,cy,29))-o.location).to_track_quat('-Z','Y').to_euler();c.type='ORTHO';c.ortho_scale=53;s.camera=o
s.render.engine='CYCLES';s.cycles.samples=24;s.render.resolution_x=900;s.render.resolution_y=1200;s.render.resolution_percentage=100
s.render.filepath=str(ROOT/'review/v14/terrace-links/tower-section.png');bpy.ops.render.render(write_still=True)
print('CUTAWAY: east shell removed for review only; source scene was not saved.')
