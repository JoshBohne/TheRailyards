"""Save a staged V10 replay and export the existing venue for browser playback.

Run against preserved railyards-v9.blend. Static geometry stays source-derived;
hero motion, flight, splash and browser material approximations are illustrative.
"""
import bpy
import argparse
import json
import math
import sys
import hashlib
from pathlib import Path
from mathutils import Vector

OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT))
from r2_lighting import apply_lighting

parser=argparse.ArgumentParser()
parser.add_argument('--version',type=int,choices=[10,11,12,13,14],default=10)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
VERSION=args.version
SOURCE=Path(bpy.data.filepath)
SOURCE_SHA=hashlib.sha256(SOURCE.read_bytes()).hexdigest()

DEST = OUT.parent / 'sites/replay/public/model'
DEST.mkdir(parents=True, exist_ok=True)
scene = bpy.data.scenes['Railyards v4']
bpy.context.window.scene = scene
apply_lighting(scene, 'south')
for name in ['D2_Future development', 'D2_Proposed soccer stadium', 'D2_South source rail links',
             'D2_South source landing buildings', 'D2_South source medical branding', 'D2_Players']:
    col = bpy.data.collections.get(name)
    if col:
        col.hide_render = True
        col.hide_viewport = True
for obj in scene.objects:
    if obj.name.startswith('D2_Distance atmosphere'):
        obj.hide_render = True
        obj.hide_set(True)

FPS = 60
CONTACT = 1.55
FLIGHT = 6.1 if VERSION >= 11 else math.sqrt(464 / 9.81)
DURATION = 10.5
LANDING = Vector((142, 16 if VERSION >= 11 else 30, 0))
ARC = 150 if VERSION >= 11 else 232

def ball_at(t):
    if t < .35:
        return Vector((12.72, 12.72, 13.9))
    if t < CONTACT:
        u = (t - .35) / (CONTACT - .35)
        return Vector((12.72 * (1-u), 12.72 * (1-u), 13.9 - .9*u + .20*math.sin(u*math.pi)))
    u = min(1, (t-CONTACT)/FLIGHT)
    return Vector((LANDING.x*u, LANDING.y*u, 13*(1-u)+ARC*u*(1-u)))

def web(v):
    return [round(v[0], 5), round(v[2], 5), round(-v[1], 5)]

# Validate the shared flight against original, full-resolution static geometry.
dg = bpy.context.evaluated_depsgraph_get()
collisions = []
for i in range(199):
    a = ball_at(CONTACT + FLIGHT*i/200)
    b = ball_at(CONTACT + FLIGHT*(i+1)/200)
    delta = b-a
    hit, at, normal, face, obj, matrix = scene.ray_cast(dg, a, delta.normalized(), distance=delta.length)
    if hit and not any(s in obj.name.lower() for s in ['player', 'spectator', 'fan', 'atmosphere']):
        collisions.append({'object': obj.name, 'at': list(at)})
if collisions:
    raise RuntimeError('Replay flight intersects static architecture: '+json.dumps(collisions))

# Read actual point geometry, not stale scene count metadata.
instances = []
for obj in scene.objects:
    if obj.type != 'MESH' or len(obj.data.polygons) or not len(obj.data.vertices):
        continue
    if not obj.visible_get() or obj.hide_render:
        continue
    sources = [n.inputs['Object'].default_value for m in obj.modifiers if m.type == 'NODES'
               for n in m.node_group.nodes if n.type == 'OBJECT_INFO']
    if not sources:
        continue
    rot = obj.data.attributes.get('rotation')
    scale = obj.data.attributes.get('scale')
    row_elevation = obj.data.attributes.get('row_elevation')
    entries = []
    for i, v in enumerate(obj.data.vertices):
        p = obj.matrix_world @ v.co
        r = rot.data[i].vector if rot else Vector((0,0,0))
        s = scale.data[i].vector if scale else Vector((1,1,1))
        if VERSION>=13 and s.length_squared<1e-10:
            continue
        entry=[*[round(c,4) for c in p], *[round(c,5) for c in r], *[round(c,4) for c in s]]
        if row_elevation:
            entry.append(round(row_elevation.data[i].value,4))
        entries.append(entry)
    instances.append({'name':obj.name, 'prototype':sources[0].name, 'points':entries})
seats = next(g for g in instances if g['name'] == 'D2_Individual seats')

actors = bpy.data.collections.new('R10_Authored replay actors')
scene.collection.children.link(actors)

def material(name, color, emission=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color,1)
    m.use_nodes = True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=.72
    if emission:
        p.inputs['Emission Color'].default_value=(*color,1)
        p.inputs['Emission Strength'].default_value=emission
    return m

white=material('R10_Home white',(.76,.78,.75))
black=material('R10_Charcoal',(.018,.023,.027))
skin=material('R10_Skin',(.40,.23,.14))
wood=material('R10_Bat',(.60,.36,.14))
ballmat=material('R10_Ball',(.98,.95,.80))

def move(obj, parent=None):
    for col in list(obj.users_collection): col.objects.unlink(obj)
    actors.objects.link(obj)
    if parent: obj.parent=parent
    return obj

def empty(name, position, parent=None):
    obj=bpy.data.objects.new(name,None)
    actors.objects.link(obj)
    obj.parent=parent
    obj.location=position
    return obj

def ellipsoid(name, p, s, mat, parent):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=10,ring_count=6,radius=1,location=p)
    obj=move(bpy.context.object,parent)
    obj.name=name;obj.scale=s;obj.data.materials.append(mat)
    for poly in obj.data.polygons: poly.use_smooth=True
    return obj

def limb(name,a,b,r,mat,parent):
    a,b=Vector(a),Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=r,depth=(b-a).length,location=(a+b)/2)
    obj=move(bpy.context.object,parent)
    obj.name=name;obj.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();obj.data.materials.append(mat)
    return obj

def person(name, p, uniform=white, crouch=False):
    root=empty(name,p)
    root.rotation_euler.z=-math.pi/4
    hips=empty(name+'_hips',(0,0,.62 if crouch else .88),root)
    torso=empty(name+'_torso',(0,0,0),hips)
    ellipsoid(name+'_shirt',(0,0,.32),(.22,.14,.34),uniform,torso)
    limb(name+'_neck',(0,0,.55),(0,0,.80),.065,skin,torso)
    ellipsoid(name+'_head',(0,0,.82),(.105,.10,.13),skin,torso)
    ellipsoid(name+'_cap',(0,0,.94),(.12,.13,.055),black,torso)
    for sign in [-1,1]:
        if crouch:
            limb(name+'_thigh',(sign*.1,0,0),(sign*.22,.26,-.25),.075,white,hips)
            limb(name+'_shin',(sign*.22,.26,-.25),(sign*.22,.08,-.56),.065,white,hips)
        else:
            limb(name+'_leg',(sign*.1,0,0),(sign*.18,.015,-.78),.075,white,hips)
        ellipsoid(name+'_shoe',(sign*.18,.07,-.56 if crouch else -.82),(.08,.15,.055),black,hips)
    return root, torso

batter, chest = person('R10_Batter',(.65,-.65,12.06))
# At contact the bat crosses the home-plate launch point. Other poses are staged.
for sign in [-1,1]:
    limb('R10_Batter upper arm',(sign*.17,0,.44),(-.24,.13,.23),.065,white,chest)
    limb('R10_Batter forearm',(-.24,.13,.23),(-.32,.0,.06),.05,skin,chest)
limb('R10_Bat',(-.29,0,.06),(-1.20,0,.06),.029,wood,chest)
for t, angle in [(0,-1.9),(1.13,-1.9),(1.37,-1.15),(CONTACT,0),(1.78,1.65),(2.2,1.8),(3.2,.3),(DURATION,.3)]:
    chest.rotation_euler.z=angle
    chest.keyframe_insert(data_path='rotation_euler',frame=t*FPS)

pitcher, pitchchest=person('R10_Pitcher',(12.72,12.72,12.06))
pitcher.rotation_euler.z=3*math.pi/4
arm=empty('R10_Pitching arm',(.18,0,.46),pitchchest)
limb('R10_Pitch upper',(0,0,0),(0,.12,.32),.062,white,arm)
limb('R10_Pitch forearm',(0,.12,.32),(0,.25,.56),.044,skin,arm)
limb('R10_Pitch glove arm',(-.18,0,.4),(-.1,.35,.15),.065,white,pitchchest)
for t,angle in [(0,-.7),(.24,-1.1),(.35,1.3),(.7,2.7),(1.4,2.2),(DURATION,2.2)]:
    arm.rotation_euler.x=angle;arm.keyframe_insert(data_path='rotation_euler',frame=t*FPS)

for name,pos in [('First base',(26,1.25)),('Second base',(21.5,21)),('Shortstop',(14.7,20.1)),('Third base',(1.25,26)),('Right field',(65,17)),('Center field',(48,48)),('Left field',(17,65)),('Catcher',(-.92,-.92))]:
    root,torso=person('R10_'+name,(*pos,12.06),crouch=name=='Catcher')
    for sign in [-1,1]:limb('R10_Ready arm',(sign*.18,0,.45),(sign*.24,.18,.10),.057,white,torso)
    if 'field' in name:
        original=root.location.copy()
        for t,delta in [(0,0),(2.1,0),(4.8,2),(DURATION,2)]:
            root.location=original+Vector((delta,-delta*.3,0));root.keyframe_insert(data_path='location',frame=t*FPS)

# The authoring file contains the same sampled ball motion used by the website.
ball=ellipsoid('R10_Baseball',ball_at(0),(.0366,)*3,ballmat,None)
for frame in range(round(DURATION*FPS)+1):
    ball.location=ball_at(frame/FPS)
    ball.keyframe_insert(data_path='location',frame=frame)
scene.frame_start=0;scene.frame_end=round(DURATION*FPS);scene.render.fps=FPS
scene['stage']=f'V{VERSION}: shared-clock interactive river replay'
scene['replay_note']='Imagined future play. Authored generic figures and flight; modeled seats are not ticket sightline guarantees.'
for name, position, target, lens in [
    ('contact',(3,-5,14.8),(0,0,13),48),
    ('aerial',(232,-140,170),(48,43,24),33),
    ('boat',(181,18,2.6),(142,30,4),32)]:
    cam=bpy.data.objects.new('R10_'+name,bpy.data.cameras.new('R10_'+name))
    scene.collection.children['R2_Cameras'].objects.link(cam)
    cam.location=position;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;cam.data.clip_end=18000
scene.camera=bpy.data.objects['R10_contact']
scene.frame_set(round(CONTACT*FPS))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/f'railyards-v{VERSION}.blend'),compress=True)

samples=[web(ball_at(i/FPS)) for i in range(round(DURATION*FPS)+1)]
metadata={'version':VERSION,'duration':DURATION,'sampleRate':FPS,'contact':CONTACT,'splash':CONTACT+FLIGHT,
          'sourceStaticScene':SOURCE.name,'sourceStaticSha256':SOURCE_SHA,
          'waterCrossing':CONTACT+FLIGHT*128/142,'ballSamples':samples,'landing':web(LANDING),
          'waterDistanceFt':round(math.hypot(LANDING.x,LANDING.y)*128/142/.3048),'splashDistanceFt':round(math.hypot(LANDING.x,LANDING.y)/.3048),
          'seatCount':sum(len(g['points']) for g in instances if 'individual seats' in g['name'].lower()),'sourceScene':f'railyards-v{VERSION}.blend','instances':instances,
          'cameras':json.loads((OUT/'experience-cameras.json').read_text()),
          'note':'Imagined future play. Seat positions come from the saved model, not an official seating plan. Flight and animation are illustrative.'}
if VERSION >= 11:
    from r11_circulation import ARRIVAL_XY,terrace_z
    metadata['arrivalPath']=[web((x,y,terrace_z(y)+1.7)) for x,y in ARRIVAL_XY]
    if VERSION>=13:
        # Real park-level arcade passage; the upper roof terrace is a separate level.
        metadata['arrivalPath']=[web(p) for p in [(50,294,15.86),(48,220,16.60),
            (51,181,16.99),(51,161,17.08),(51,140,17.08),(51,121,17.08),
            (51,109.5,17.08),(51,105,15.10)]]
    metadata['architectureVersion']=11
(DEST/'replay.json').write_text(json.dumps(metadata,separators=(',',':'))+'\n')

# Export authored figures as glTF transform animation. Ball is sampled separately.
bpy.ops.object.select_all(action='DESELECT')
for obj in actors.objects:
    if obj != ball:obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(DEST/'actors.glb'),use_selection=True,use_active_scene=True,export_format='GLB',
    export_animations=True,export_animation_mode='SCENE',export_force_sampling=True,export_frame_range=True,
    export_lights=False,export_cameras=False)

# Make an isolated, disposable export scene; never flatten the saved authoring file.
export_scene=bpy.data.scenes.new(f'V{VERSION} browser export')
visible=[o for o in scene.objects if o.visible_get() and not o.hide_render
         and o.type in {'MESH','CURVE','FONT'} and o not in list(actors.objects)
         and not (o.type=='MESH' and len(o.data.polygons)==0)]
for obj in visible:
    clone=obj.copy();clone.data=obj.data.copy();export_scene.collection.objects.link(clone)
bpy.context.window.scene=export_scene
bpy.ops.object.select_all(action='SELECT')
bpy.context.view_layer.objects.active=next(iter(export_scene.objects))
bpy.ops.object.convert(target='MESH')
bpy.ops.object.join()
venue=bpy.context.view_layer.objects.active;venue.name='R10_Venue'
# Procedural node textures are represented by their base palette in this viewer.
for mat in venue.data.materials:
    if not mat or not mat.use_nodes:continue
    p=mat.node_tree.nodes.get('Principled BSDF')
    if p:
        for socket in ['Base Color','Normal','Transmission Weight']:
            for link in list(p.inputs[socket].links):mat.node_tree.links.remove(link)
        if mat.name.startswith('D2_'):p.inputs['Base Color'].default_value=mat.diffuse_color
        p.inputs['Transmission Weight'].default_value=0
        p.inputs['Metallic'].default_value=min(.25,p.inputs['Metallic'].default_value)

# Keep tree prototypes; small seats/crowds use lighter browser instances at the exact points.
prototype_names={g['prototype'] for g in instances if 'tree' in g['prototype'].lower()}
for name in prototype_names:
    original=bpy.data.objects.get(name)
    if original:
        clone=original.copy();clone.data=original.data.copy();clone.name='Prototype_'+name
        clone['prototypeName']=name;export_scene.collection.objects.link(clone)
        modifier=clone.modifiers.new('Browser foliage detail','DECIMATE');modifier.ratio=.22
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(DEST/'venue.glb'),use_selection=True,use_active_scene=True,export_format='GLB',
    export_animations=False,export_lights=False,export_cameras=False,export_extras=True,export_apply=True,
    export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6,
    export_draco_position_quantization=22,export_draco_normal_quantization=10)
receipt={'savedScene':str(OUT/f'railyards-v{VERSION}.blend'),'seatCount':sum(len(g['points']) for g in instances if 'individual seats' in g['name'].lower()),
         'sourceStaticScene':str(SOURCE),'sourceStaticSha256':SOURCE_SHA,
         'staticVertices':len(venue.data.vertices),'staticPolygons':len(venue.data.polygons),
         'flightCollisions':collisions,'contact':CONTACT,'splash':CONTACT+FLIGHT,
         'files':{p.name:p.stat().st_size for p in DEST.iterdir() if p.is_file() and p.name!='export-receipt.json'},
         'limitations':'Browser materials flatten procedural textures. Seats and crowd use simplified instanced geometry.'}
(DEST/'export-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(f'V{VERSION}_EXPORT '+json.dumps(receipt))
