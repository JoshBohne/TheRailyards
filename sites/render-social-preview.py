"""Render a measured illustrative flight over the current stadium for link cards."""
import bpy,math,os,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'railyards-v4'))
from r2_lighting import apply_lighting
s=bpy.data.scenes['Railyards v4'];bpy.context.window.scene=s
apply_lighting(s,'north');s.camera=bpy.data.objects['R2_north'];cam=s.camera
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
s.render.resolution_x=1200;s.render.resolution_y=630;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';cam.data.lens*=.90
out=Path(os.environ['RAILYARDS_SOCIAL_OUT']);out.parent.mkdir(parents=True,exist_ok=True)
data=json.loads((ROOT/'sites/replay/public/model/replay.json').read_text())
def emission(name,color,strength=1):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial');e=n.new('ShaderNodeEmission');e.inputs[0].default_value=(*color,1);e.inputs[1].default_value=strength;m.node_tree.links.new(e.outputs[0],out.inputs[0]);return m
white=emission('Social white',(.95,.98,.96));gold=emission('Social trajectory',(1,.61,.16),3);dark=emission('Social backing',(.012,.026,.028))
points=[Vector((p[0],-p[2],p[1])) for p in data['ballSamples'][round(data['contact']*60):round(data['splash']*60)+1]]
curve=bpy.data.curves.new('Illustrative home run trajectory','CURVE');curve.dimensions='3D';curve.bevel_depth=.32;curve.bevel_resolution=3;poly=curve.splines.new('POLY');poly.points.add(len(points)-1)
for p,xyz in zip(poly.points,points):p.co=(*xyz,1)
o=bpy.data.objects.new(curve.name,curve);s.collection.objects.link(o);curve.materials.append(gold)
for radius in [1.5,3,4.5]:
 bpy.ops.mesh.primitive_torus_add(major_radius=radius,minor_radius=.12,major_segments=64,minor_segments=6,location=(142,16,.15));bpy.context.object.data.materials.append(gold)
# Camera-space typography is rendered with the scene, not painted onto an older image.
bpy.context.view_layer.update()
frame=cam.data.view_frame(scene=s);distance=2
halfwidth=max(v.x/-v.z for v in frame)*distance;halfheight=max(v.y/-v.z for v in frame)*distance

def label(body,x,y,size,mat):
 c=bpy.data.curves.new('Social label','FONT');c.body=body;c.size=size*(halfwidth*2/1200);c.space_line=1.05;c.align_y='TOP';c.materials.append(mat)
 obj=bpy.data.objects.new(body,c);s.collection.objects.link(obj);obj.parent=cam;obj.location=(-halfwidth+x/1200*2*halfwidth,halfheight-y/630*2*halfheight,-distance)
 # Camera-attached text faces its parent camera and never casts light/shadows into the model.
 obj.visible_shadow=False
 return obj
# Project the authored 3D arc into a legible diagram overlay at the same camera.
projected=[world_to_camera_view(s,cam,p) for p in points]
for name,depth,radius,mat in [('outline',2.015,3.0,dark),('gold',2.0,1.65,gold)]:
 c=bpy.data.curves.new('Projected flight '+name,'CURVE');c.dimensions='3D';c.bevel_depth=radius*halfwidth*2/1200;c.bevel_resolution=3
 spline=c.splines.new('POLY');spline.points.add(len(projected)-1)
 for point,p in zip(spline.points,projected):point.co=((p.x*2-1)*halfwidth*depth/2,(p.y*2-1)*halfheight*depth/2,-depth,1)
 obj=bpy.data.objects.new(c.name,c);s.collection.objects.link(obj);obj.parent=cam;c.materials.append(mat);obj.visible_shadow=False
label('HOME RUNS\nINTO THE RIVER?',720,36,36,white)
label(str(data['waterDistanceFt'])+' ft',44,465,54,gold)
label('TO THE RIVER EDGE',46,528,18,white)
label(str(data['splashDistanceFt'])+' ft to the illustrated splash',46,554,15,white)
label('The Railyards  /  An illustrative Blender reconstruction',46,585,15,white)
label('Modeled distance, not an official specification',760,590,13,white)
s.render.filepath=str(out);bpy.ops.render.render(write_still=True)
out.with_suffix('.json').write_text(json.dumps({'scene':bpy.data.filepath,'sourceSceneSha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'waterDistanceFt':data['waterDistanceFt'],'splashDistanceFt':data['splashDistanceFt'],'landing':data['landing'],'note':'Horizontal distance along the authored flight direction to x=128 river edge; illustrative geometry and flight, not a ballistics forecast.'},indent=2)+'\n')
