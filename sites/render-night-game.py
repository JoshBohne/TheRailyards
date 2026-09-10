"""Four fixed night-game cameras from the consolidated, animated V14 scene.

All shots share one clock. Celebration effects and the enlarged ball are
illustrative. Never write back into the preserved input scene.
"""
import bpy, math, os, json, hashlib, sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[1]/'railyards-v4'
sys.path.insert(0,str(ROOT))
from r2_lighting import apply_lighting
scene=bpy.data.scenes['Railyards v4'];bpy.context.window.scene=scene
out=Path(os.environ['RAILYARDS_HERO_OUT']);out.mkdir(parents=True,exist_ok=True)
apply_lighting(scene,'night')
scene.render.engine='CYCLES';scene.cycles.samples=int(os.environ.get('RAILYARDS_HERO_SAMPLES','12'))
if os.environ.get('RAILYARDS_GPU')=='1':scene.cycles.device='GPU'
scene.cycles.use_denoising=True
scene.render.use_persistent_data=True
scene.render.resolution_x=int(os.environ.get('RAILYARDS_HERO_WIDTH','1280'));scene.render.resolution_y=round(scene.render.resolution_x*9/16);scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
for obj in scene.objects:
    if obj.name.startswith('D2_Distance atmosphere'):obj.hide_render=True
cam=bpy.data.objects.new('Night game edit camera',bpy.data.cameras.new('Night game edit camera'));scene.collection.objects.link(cam);scene.camera=cam;cam.data.clip_end=18000
ball=bpy.data.objects['R10_Baseball'];ball.scale*=7

def material(name,color,strength):
    mat=bpy.data.materials.new(name);mat.diffuse_color=(*color,1);mat.use_nodes=True
    bsdf=mat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(*color,1);bsdf.inputs['Emission Color'].default_value=(*color,1);bsdf.inputs['Emission Strength'].default_value=strength
    return mat
white=material('Night splash white',(.63,.83,1),2)
gold=material('Night celebration gold',(1,.55,.10),6)
ballmat=material('Night ball marker',(1,.9,.6),2)
ball.data.materials.clear();ball.data.materials.append(ballmat)
# Water rings and airborne droplets are explicitly authored, deterministic effects.
rings=[]
for i in range(3):
    bpy.ops.mesh.primitive_torus_add(major_radius=1,minor_radius=.045,major_segments=48,minor_segments=6,location=(142,16,.14+i*.025))
    obj=bpy.context.object;obj.name='Night splash ring '+str(i);obj.data.materials.append(white);rings.append(obj)
drops=[]
for i in range(36):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.09)
    obj=bpy.context.object;obj.name='Night splash drop '+str(i);obj.data.materials.append(white);drops.append(obj)
# Three shells above the stadium, visible in the river composition.
sparks=[]
for burst,(center,start) in enumerate([((80,54,67),7.35),((47,114,79),7.9),((92,-30,76),8.6)]):
    for i in range(48):
        az=i*2.399963;vz=1-2*(i+.5)/48;r=math.sqrt(1-vz*vz)
        direction=Vector((math.cos(az)*r,math.sin(az)*r,vz))
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.14)
        obj=bpy.context.object;obj.name=f'Night firework {burst}-{i}';obj.data.materials.append(gold if burst!=1 else white)
        sparks.append((obj,Vector(center),direction,start))
# The RF board is two-sided; temporary HOME RUN screens cover its static game art.
spec=json.loads((ROOT/'scene-spec.json').read_text());top=Vector(spec['anchors']['rf_scoreboard_top']);width=spec.get('rf_scoreboard',{}).get('width_m',39);angle=math.radians(spec.get('rf_scoreboard',{}).get('angle_deg',90))
if scene.get('v15_corrections'):top.z+=2
height=spec.get('rf_scoreboard',{}).get('height_m',20)
tangent=Vector((math.cos(angle),math.sin(angle),0));normal=Vector((-math.sin(angle),math.cos(angle),0))
boardmat=material('Night home run screen',(.008,.021,.04),.5)
boards=[]
for side in [-1,1]:
    bpy.ops.mesh.primitive_cube_add(size=1,location=top+normal*(1.42*side)+Vector((0,0,-height/2)))
    panel=bpy.context.object;panel.name='Night home run panel '+str(side);panel.dimensions=(width-.3,.08,height-.3);panel.rotation_euler.z=angle;panel.data.materials.append(boardmat);boards.append(panel)
    curve=bpy.data.curves.new('Night HOME RUN','FONT');curve.body='HOME\nRUN';curve.align_x='CENTER';curve.align_y='CENTER';curve.size=4.3;curve.space_line=.9;curve.extrude=.005
    text=bpy.data.objects.new('Night home run lettering '+str(side),curve);scene.collection.objects.link(text);text.location=top+normal*(1.51*side)+Vector((0,0,-height/2));text.rotation_euler=(math.pi/2,0,angle+math.pi if side==1 else angle);curve.materials.append(white);boards.append(text)
shots=[('home plate',0,(-12,-15,30),(20,20,12),22),('above the diamond',2.4,(-54,-68,102),(46,32,19),32),('right-field corner',5.0,(158,15,63),(30,45,20),25),('river',6.65,(190,-35,10),(73,32,29),26)]
frames=[int(x) for x in os.environ.get('RAILYARDS_HERO_FRAMES','').split(',') if x] or range(288)
projections=[]
for frame in frames:
    t=frame/24;scene.frame_set(round(min(t,10.5)*60));ball.hide_render=t>=7.65
    for i,ring in enumerate(rings):
        age=t-7.65-i*.16;ring.hide_render=age<0 or age>3.5;ring.scale=(1+max(0,age)*2.5,)*2+(1,)
    for i,obj in enumerate(drops):
        age=t-7.65;az=i*2.399963;speed=1.8+(i%5)*.5
        obj.hide_render=age<0 or age>1.05;obj.location=(142+math.cos(az)*age*speed,16+math.sin(az)*age*speed,max(.12,age*5.5-age*age*5.1))
    for obj,center,direction,start in sparks:
        age=t-start;obj.hide_render=age<0 or age>2.6;obj.location=center+direction*max(0,age)*10+Vector((0,0,-2.7*max(0,age)**2));fade=max(.05,1-age/2.8);obj.scale=(.7*fade,.7*fade,7*fade);obj.rotation_euler=(direction*10+Vector((0,0,-5.4*max(0,age)))).to_track_quat('Z','Y').to_euler()
    for obj in boards:obj.hide_render=t<6.8
    name,start,position,target,lens=next(shot for shot in reversed(shots) if t>=shot[1])
    cam.location=position;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
    bpy.context.view_layer.update()
    if name=='river':
        p=world_to_camera_view(scene,cam,Vector((142,16,.2)));projections.append({'frame':frame,'landingNormalized':[p.x,p.y,p.z]})
    scene.render.filepath=str(out/f'{frame:04d}.png');bpy.ops.render.render(write_still=True)
receipt={'scene':bpy.data.filepath,'sceneSha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'fps':24,'frames':288,'renderedFrames':list(frames),'shots':[{'name':s[0],'startSeconds':s[1],'position':s[2],'target':s[3],'lens':s[4]} for s in shots],'splashSeconds':7.65,'riverProjections':projections,'note':'Illustrative play, fireworks and enlarged ball. Fixed cameras; shared animation clock.'}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
