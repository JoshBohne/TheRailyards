"""Build the separate reference-calibrated gray scene. Invoke through Blender MCP.

This stage deliberately exposes massing and camera errors before detailed dressing.
The original study is retained as another scene and its original file is untouched.
"""
import bpy
import json
import math
from pathlib import Path
from mathutils import Matrix, Vector

OUT=Path(__file__).resolve().parent
SPEC=json.loads((OUT/'scene-spec.json').read_text())
PREFIX='R2_'
for obj in list(bpy.data.objects):
    if obj.name.startswith(PREFIX):bpy.data.objects.remove(obj,do_unlink=True)
for collection in list(bpy.data.collections):
    if collection.name.startswith(PREFIX):bpy.data.collections.remove(collection)
scene=bpy.data.scenes.get('Railyards v4') or bpy.data.scenes.new('Railyards v4')
bpy.context.window.scene=scene
collections={}
def collection(name):
    if name not in collections:
        col=bpy.data.collections.new(PREFIX+name);scene.collection.children.link(col);collections[name]=col
    return collections[name]
def material(name,color,rough=.75):
    mat=bpy.data.materials.get(PREFIX+name) or bpy.data.materials.new(PREFIX+name)
    mat.use_nodes=True;mat.diffuse_color=(*color,1)
    bsdf=mat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(*color,1);bsdf.inputs['Roughness'].default_value=rough
    return mat
mats={'structure':material('Gray structure',(.55,.57,.58)), 'field':material('Gray field',(.29,.34,.31)), 'water':material('Gray river',(.13,.20,.24),.2), 'ground':material('Gray ground',(.38,.40,.41)), 'roof':material('Gray canopy',(.31,.34,.37)), 'screen':material('Gray screens',(.045,.06,.07)), 'line':material('Field markings',(.8,.8,.76)), 'track':material('Gray infield',(.43,.40,.35)), 'glass':material('Gray glazing',(.16,.19,.21),.3)}
def mesh(name,verts,faces,mat='structure',group='Architecture'):
    data=bpy.data.meshes.new(PREFIX+name);data.from_pydata(verts,[],faces);data.materials.append(mats[mat]);data.update()
    obj=bpy.data.objects.new(PREFIX+name,data);collection(group).objects.link(obj);return obj
def box(name,center,size,mat='structure',group='Architecture',angle=0):
    x,y,z=center;w,d,h=[v/2 for v in size]
    co,si=math.cos(angle),math.sin(angle)
    vs=[(x+a*w*co-b*d*si,y+a*w*si+b*d*co,z+c*h) for a,b,c in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    return mesh(name,vs,[(3,2,1,0),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],mat,group)
def extrude(name,footprint,z0,z1,mat='structure',group='Architecture'):
    n=len(footprint);vs=[(x,y,z)for z in [z0,z1]for x,y in footprint]
    fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)]
    return mesh(name,vs,fs,mat,group)
def ribbon(name,a,b,mat='structure',group='Bowl'):
    vs=[tuple(p) for pair in zip(a,b) for p in pair]
    return mesh(name,vs,[(2*i,2*i+1,2*i+3,2*i+2)for i in range(len(a)-1)],mat,group)
def path_at(t,z):
    return [(a[0]*(1-t)+b[0]*t,a[1]*(1-t)+b[1]*t,z)for a,b in zip(SPEC['bowl_front'],SPEC['bowl_back'])]
def rod(name,a,b,radius,mat='line',group='Field'):
    data=bpy.data.curves.new(PREFIX+name,'CURVE');data.dimensions='3D';data.bevel_depth=radius;data.bevel_resolution=1
    spl=data.splines.new('POLY');spl.points.add(1)
    spl.points[0].co=(*a,1);spl.points[1].co=(*b,1);data.materials.append(mats[mat])
    obj=bpy.data.objects.new(PREFIX+name,data);collection(group).objects.link(obj);return obj

# Ground and registered linear context.
box('West district ground',(-822,300,3),(1356,3000,10),'ground','Site')
box('Stadium district ground',(15,300,3),(218,3000,10),'ground','Site')
box('East district ground',(598,300,3),(804,3000,10),'ground','Site')
box('River channel',(159.5,100,-.7),(63,2300,1.4),'water','Site')
box('River west quay',(124,100,2),(8,2200,4),'structure','Site')
box('River east quay',(195,100,2),(8,2200,4),'structure','Site')
box('Rail cutting',(-119,50,1.7),(50,1800,3.4),'screen','Site')
for x in [-137,-129,-121,-113,-105]:
    for dx in [-.75,.75]:rod('Rail',(x+dx,-850,6.65),(x+dx,950,6.65),.08,'line','Site')
box('Canal Street',(-220,40,8.1),(27,1800,.2),'screen','Site')
box('Roosevelt bridge',(15,316,12),(680,26,4),'structure','Bridges')
box('Roosevelt road',(15,316,14.1),(680,19,.2),'screen','Bridges')
for x in [125,195]:
    box('Bridge abutment',(x,316,5),(7,31,18),'structure','Bridges')
    for y in [300,332]:box('Bridge tender house',(x,y,18),(6,6,8),'structure','Bridges')

# Playing field and recognizable regulation diamond, with an explicit scale prior.
front=SPEC['bowl_front'];field=SPEC['field_boundary']
outline=[p[:2]for p in front]+[p[:2]for p in reversed(field)]
extrude('Playing platform',outline,10.5,12,'field','Field')
base=27.432
extrude('Infield clay',[(-4,-4),(39,-4),(39,39),(-4,39)],12.01,12.03,'track','Field')
extrude('Infield grass',[(2.5,2.5),(24.9,2.5),(24.9,24.9),(2.5,24.9)],12.04,12.06,'field','Field')
for i,(x,y)in enumerate([(0,0),(base,0),(base,base),(0,base)]):box('Base '+str(i),(x,y,12.15),(.7,.7,.18),'line','Field')
rod('First base foul line',(0,0,12.2),(100,0,12.2),.09)
rod('Third base foul line',(0,0,12.2),(0,100,12.2),.09)
for x,y in [(100,0),(0,100)]:rod('Foul pole',(x,y,12),(x,y,36),.13)
for a,b in zip(field,field[1:]):
    ribbon('Outfield fence',[a,b],[(a[0],a[1],16),(b[0],b[1],16)],'screen','Field')

# Four separated decks; geometry follows traced, asymmetric front/back curves.
tiers=[(.0,.34,14,24,24),(.40,.49,27,30,8),(.55,.65,33,36,9),(.70,.93,39,47,18)]
for tier,(ta,tb,za,zb,rows)in enumerate(tiers):
    for row in range(rows):
        t0=ta+(tb-ta)*row/rows;t1=ta+(tb-ta)*(row+1)/rows;z=za+(zb-za)*row/rows
        ribbon(f'Tier {tier+1} row {row+1}',path_at(t0,z),path_at(t1,z))
        ribbon(f'Tier {tier+1} riser {row+1}',path_at(t1,z),path_at(t1,z+(zb-za)/rows))
    ribbon(f'Tier {tier+1} fascia',path_at(ta,za-.9),path_at(ta,za))
    if tier<3:ribbon(f'Tier {tier+1} concourse glass',path_at(tb+.025,zb),path_at(tb+.025,zb+2.5),'glass')
upper=SPEC['bowl_back'];inner=SPEC['canopy_inner']
ribbon('Canopy',inner,upper,'roof')
ribbon('Outer stadium facade',[(x,y,8)for x,y,z in upper],[(x,y,z-.3)for x,y,z in upper])
for i in range(0,len(upper),8):rod('Roof seam',inner[i],upper[i],.12,'structure','Bowl')

# Signature tower, west lantern, screens, and the major adjacent masses.
t=SPEC['anchors']['tower_roof']
box('Clock tower shaft',(t[0],t[1],(8+t[2]-1)/2),(13,14,t[2]-9),'structure')
box('Clock tower cap',(t[0],t[1],t[2]-.5),(15,16,1),'roof')
west=SPEC['anchors']['west_roof_lantern']
box('West canopy lantern',(west[0],west[1],west[2]-4),(12,10,8),'roof')
for key,width in [('cf_scoreboard_top',31),('rf_scoreboard_top',39)]:
    p=SPEC['anchors'][key]
    if key.startswith('cf'):
        box('Center field screen',(p[0],p[1],p[2]-9),(width,1.5,18),'screen',angle=math.radians(135))
        box('Center field pavilion',(p[0]-2,p[1]-7,14),(43,31,20),'structure')
    else:box('River field screen',(p[0],p[1],p[2]-10),(1.5,width,20),'screen')
for b in SPEC['buildings']:extrude(b['name'],b['footprint'],b['base'],b['roof'])
for y in [-113,-48,73,150]:
    box('Rail footbridge',(-121,y,24),(112,7,4),'glass','Bridges')
    box('Rail footbridge roof',(-121,y,26.4),(114,8,.8),'roof','Bridges')
box('North lawn',(63,235,8.3),(93,96,.6),'field','Site')
box('North riverwalk',(117,235,4),(15,155,1),'structure','Site')

# Existing context uses geographic footprints; proposed district structures are
# separate. Missing heights remain explicitly inferred in site-context.json.
context=json.loads((OUT/'site-context.json').read_text())
for building in context['buildings']:
    obj=extrude('OSM '+str(building['osm_way']),building['footprint'],building['base_z'],building['base_z']+building['height_m'],'ground','Context')
    obj['osm_way']=building['osm_way'];obj['height_basis']=building['height_basis'];obj['name']=building.get('name') or '';obj['height_m']=float(building['height_m'])

def make_camera(name,c):
    az,el,roll=c['azimuth'],c['elevation'],c['roll']
    d=Vector((math.cos(az)*math.cos(el),math.sin(az)*math.cos(el),-math.sin(el)))
    r=Vector((math.sin(az),-math.cos(az),0));u=r.cross(d)
    r,u=r*math.cos(roll)+u*math.sin(roll),u*math.cos(roll)-r*math.sin(roll)
    data=bpy.data.cameras.new(PREFIX+name);data.sensor_width=36;data.sensor_fit='HORIZONTAL';data.lens=c['lens_mm'];data.clip_start=1;data.clip_end=10000
    obj=bpy.data.objects.new(PREFIX+name,data);collection('Cameras').objects.link(obj)
    obj.matrix_world=Matrix((r,u,-d)).transposed().to_4x4();obj.location=c['position'];return obj
for name,c in SPEC['cameras'].items():make_camera(name,c)
scene.camera=bpy.data.objects[PREFIX+'north']
world=bpy.data.worlds.get(PREFIX+'World') or bpy.data.worlds.new(PREFIX+'World');scene.world=world;world.use_nodes=True
world.node_tree.nodes.get('Background').inputs[0].default_value=(.65,.72,.82,1);world.node_tree.nodes.get('Background').inputs[1].default_value=.7
data=bpy.data.lights.new(PREFIX+'Sun','SUN');data.energy=2.5;data.angle=.1
sun=bpy.data.objects.new(PREFIX+'Sun',data);collection('Lighting').objects.link(sun);sun.rotation_euler=(.6,-.4,-.8)
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='METAL';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='METAL'
scene.cycles.device='GPU';scene.view_settings.view_transform='AgX'
scene.render.image_settings.file_format='PNG';scene.render.resolution_percentage=100
scene.render.resolution_x=1200;scene.render.resolution_y=round(1200*1294/1944)
scene['stage']='Gray blockout: source and camera calibration, not final fidelity approval'
scene['specification']=str(OUT/'scene-spec.json')
bpy.ops.wm.save_as_mainfile(filepath=str(__import__('pathlib').Path(__import__('os').environ.get('RAILYARDS_STAGE_DIR',str(OUT)))/'railyards-v4-gray.blend'))
print(json.dumps({'stage':'gray scene built','scene':scene.name,'objects':len(scene.objects),'collections':len(scene.collection.children),'vertices':sum(len(o.data.vertices)for o in scene.objects if o.type=='MESH'),'file':bpy.data.filepath}))
