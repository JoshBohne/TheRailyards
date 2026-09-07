"""Render the V12 home-run edit from one shared animation clock."""
import bpy, math, os, json
from pathlib import Path
from mathutils import Vector
scene=bpy.data.scenes['Railyards v4'];bpy.context.window.scene=scene
out=Path(os.environ['RAILYARDS_HERO_OUT']);out.mkdir(parents=True,exist_ok=True)
scene.render.engine='BLENDER_EEVEE';scene.eevee.taa_render_samples=16
scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
for obj in scene.objects:
 if obj.name.startswith('D2_Distance atmosphere'):obj.hide_render=True
cam=bpy.data.objects.new('Overview edit camera',bpy.data.cameras.new('Overview edit camera'));scene.collection.objects.link(cam);scene.camera=cam;cam.data.clip_end=18000
ball=bpy.data.objects['R10_Baseball']
# Enlarge the same animated ball for legibility in a wide view.
ball.scale*=9
mat=bpy.data.materials.new('Overview ball marker');mat.diffuse_color=(1,.8,.25,1);mat.use_nodes=True
bsdf=mat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(1,.8,.25,1);bsdf.inputs['Emission Color'].default_value=(1,.55,.1,1);bsdf.inputs['Emission Strength'].default_value=1.5
ball.data.materials.clear();ball.data.materials.append(mat)
bpy.ops.mesh.primitive_torus_add(major_radius=1,minor_radius=.06,major_segments=48,minor_segments=8,location=(142,16,.12))
ring=bpy.context.object;ring.name='Overview illustrative splash';ring.data.materials.append(mat)
cut=1.55+6.1*128/142-.5
frames=[int(x) for x in os.environ.get('RAILYARDS_HERO_FRAMES','').split(',') if x] or range(252)
for frame in frames:
 t=frame/24;ring.hide_render=t<7.65;ring.scale=(1+max(0,t-7.65)*2,)*2+(1,);ball.hide_render=t>=7.65;scene.frame_set(round(t*60));pos=ball.matrix_world.translation.copy()
 if t<cut:cam.location=(-54,-68,102);target=Vector((46,32,19));cam.data.lens=32
 else:cam.location=(181,8,3.0);target=pos if t<7.65 else Vector((142,16,.2));cam.data.lens=30
 cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
 scene.render.filepath=str(out/f'{frame:04d}.png');bpy.ops.render.render(write_still=True)
(out/'receipt.json').write_text(json.dumps({'scene':bpy.data.filepath,'fps':24,'frames':252,'cutSeconds':cut,'waterCrossing':1.55+6.1*128/142,'note':'Illustrative play and enlarged ball. Camera cut preserves the same animation time.'},indent=2))
