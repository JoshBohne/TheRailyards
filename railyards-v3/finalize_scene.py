"""Finalize the editable scene; also safe to execute in live Blender through MCP."""
import bpy,json,sys,importlib
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent;sys.path.insert(0,str(OUT))
import r2_lighting
importlib.reload(r2_lighting)
from r2_lighting import apply_lighting
scene=bpy.data.scenes['Railyards v3'];bpy.context.window_manager.windows[0].scene=scene
for other in list(bpy.data.scenes):
    if other!=scene:bpy.data.scenes.remove(other)
for obj in list(bpy.data.objects):
    if not obj.name.startswith(('R2_','R3_','D2_')):bpy.data.objects.remove(obj,do_unlink=True)
if not bpy.data.objects.get('R2_site'):
    data=bpy.data.cameras.new('R2_site');data.type='ORTHO';data.ortho_scale=800;data.sensor_fit='HORIZONTAL';data.clip_end=4000;data.clip_start=1
    obj=bpy.data.objects.new('R2_site',data);bpy.data.collections['R2_Cameras'].objects.link(obj);obj.location=(0,-225,1400)
if not bpy.data.objects.get('R3_southern_rail_detail'):
    data=bpy.data.cameras.new('R3_southern_rail_detail');data.lens=43;data.clip_start=.5;data.clip_end=10000
    obj=bpy.data.objects.new(data.name,data);bpy.data.collections['R2_Cameras'].objects.link(obj);obj.location=(320,-535,135)
    obj.rotation_euler=(Vector((152,-378,29))-obj.location).to_track_quat('-Z','Y').to_euler()
apply_lighting(scene,'north');scene.camera=bpy.data.objects['R2_north']
scene.render.resolution_x=1800;scene.render.resolution_y=1198;scene.cycles.samples=64
scene['stage']='Comprehensive v3 source reconstruction; conceptual geometry and documented view variants'
scene['source_manifest']='SOURCE-AND-ASSUMPTIONS.md';scene['generator']='build_blockout.py → build_detail.py → add_interior_cameras.py → finalize_scene.py'
scene['tool_split']='CLI scripts, batch renders and exports; MCP live inspection and edits; computer use visual review'
scene.unit_settings.system='METRIC';scene.unit_settings.length_unit='METERS';scene.unit_settings.scale_length=1
for obj in scene.objects:
    obj.hide_set(bool(obj.hide_render) or obj.name.startswith('D2_Distance atmosphere'))
scene.camera.data.passepartout_alpha=1
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.overlay.show_overlays=False;area.spaces.active.shading.type='SOLID';area.spaces.active.shading.color_type='MATERIAL'
            area.spaces.active.clip_start=1;area.spaces.active.clip_end=10000;area.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'railyards-v3.blend'),compress=True)
print(json.dumps({'saved':bpy.data.filepath,'scenes':[s.name for s in bpy.data.scenes],'objects':len(scene.objects),'cameras':[o.name for o in scene.objects if o.type=='CAMERA']}))
