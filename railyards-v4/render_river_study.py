"""Native rendered distance illustration; the arc is not a flight prediction."""
import bpy,math,json,os,sys,time
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent;sys.path.insert(0,str(OUT))
from r2_lighting import apply_lighting
scene=bpy.data.scenes['Railyards v4'];apply_lighting(scene,'south')
for group in ['D2_Future development','D2_Proposed soccer stadium','D2_South source rail links','D2_South source landing buildings','D2_South source medical branding']:
 col=bpy.data.collections.get(group)
 if col:col.hide_render=True
scene.camera=bpy.data.objects['R9_river_shot']
v11=bool(scene.get('v11_circulation'))
landing=Vector((142,16 if v11 else 30,0));start=Vector((0,0,13.0))
water_x=128.0  # west edge of R2_River channel, verified against its mesh bounds below
river=bpy.data.objects['R2_River channel']
actual=min((river.matrix_world@Vector(p)).x for p in river.bound_box)
assert abs(actual-water_x)<.01,(actual,water_x)
range_m=math.hypot(landing.x,landing.y);edge_m=range_m*water_x/landing.x

def path(t):return Vector((landing.x*t,landing.y*t,13*(1-t)+(150 if v11 else 232)*t*(1-t)))

# Check the illustration against the actual modeled static structures.
dg=bpy.context.evaluated_depsgraph_get();hits=[]
for i in range(1,199):
 a,b=path(i/200),path((i+1)/200);d=b-a
 ok,loc,n,idx,obj,matrix=scene.ray_cast(dg,a,d.normalized(),distance=d.length)
 if ok and not any(word in obj.name.lower() for word in ['atmosphere','player','fan','spectator','r10_']):hits.append({'object':obj.name,'at':list(loc)})
if hits:raise RuntimeError('Illustrated arc intersects modeled structures: '+json.dumps(hits))
col=bpy.data.collections.new('R9_River distance illustration');scene.collection.children.link(col)
mat=bpy.data.materials.new('R9_Ball marker');mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(1,.65,.09,1);p.inputs['Emission Color'].default_value=(1,.36,.03,1);p.inputs['Emission Strength'].default_value=2
bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=.65,location=start)
ball=bpy.context.object;ball.name='R9_Enlarged ball marker';ball.data.materials.append(mat)
for c in list(ball.users_collection):c.objects.unlink(ball)
col.objects.link(ball)
curve=bpy.data.curves.new('R9_Flight trail','CURVE');curve.dimensions='3D';curve.bevel_depth=.12;curve.bevel_resolution=2
spline=curve.splines.new('POLY');spline.points.add(200)
for i,point in enumerate(spline.points):point.co=(*path(i/200),1)
trail=bpy.data.objects.new('R9_Flight trail',curve);col.objects.link(trail);curve.materials.append(mat)
ringcurve=bpy.data.curves.new('R9_Water ring','CURVE');ringcurve.dimensions='3D';ringcurve.bevel_depth=.10;ringcurve.bevel_resolution=2
ringline=ringcurve.splines.new('POLY');ringline.points.add(64)
for i,p in enumerate(ringline.points):p.co=(math.cos(i*math.tau/64),math.sin(i*math.tau/64),.10,1)
ring=bpy.data.objects.new('R9_Water ring',ringcurve);col.objects.link(ring);ring.location=landing;ringcurve.materials.append(mat)
scene.render.engine='BLENDER_EEVEE';scene.eevee.taa_render_samples=int(os.environ.get('RAILYARDS_SAMPLES','32'))
for obj in scene.objects:
 if obj.name.startswith('D2_Distance atmosphere'):obj.hide_render=True
width=int(os.environ.get('RAILYARDS_WIDTH','1600'));scene.render.resolution_x=width;scene.render.resolution_y=round(width*9/16);scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
count=int(os.environ.get('RAILYARDS_FRAMES','168'));dest=OUT/os.environ.get('RAILYARDS_OUTDIR','review/v11/river' if v11 else 'review/v9/river');dest.mkdir(parents=True,exist_ok=True)
for frame in range(count):
 normalized=frame/(count-1);t=max(0,min(1,(normalized-.10)/.75))
 if v11:
  scene.frame_set(round((1.55+t*6.1)*60))
  bpy.data.objects['R10_Baseball'].hide_render=True
 ball.location=path(t);ball.hide_render=t>=1;curve.bevel_factor_end=max(.0001,t)
 ring.hide_render=t<1;size=1+max(0,(normalized-.85)/.15)*5;ring.scale=(size,size,1)
 scene.render.filepath=str(dest/f'{frame:04d}.png');bpy.ops.render.render(write_still=True)
result={'landing_xy_m':list(landing)[:2],'water_edge_x_m':water_x,'to_water_m':round(edge_m,2),'to_water_ft':round(edge_m/0.3048),'landing_m':round(range_m,2),'landing_ft':round(range_m/0.3048),'arc_peak_z_m':round(max(path(i/1000).z for i in range(1001)),2),'static_structure_collisions':hits,'source_scene':bpy.data.filepath,'frames':count,'fps':24,'note':'Horizontal distances in an inferred stadium model. Arc and enlarged ball marker illustrate a route, not aerodynamic flight, exit velocity, or an official home-run distance.'}
(OUT/('river-distance-study-v11.json' if v11 else 'river-distance-study.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
