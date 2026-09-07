"""V12 acceptance views on a saved scene: fixed pedestrian/aerial cameras for the
left-center bank, RF corner, dugouts/foul lines and tower flag, plus the V11
arrival floor probes. Set RAILYARDS_SCENE_LABEL to tag outputs (v11/v12)."""
import bpy,json,math,sys,os
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
from r2_lighting import apply_lighting
from r3_public_realm import deck_z
from r11_circulation import ARRIVAL_XY,terrace_z
label=os.environ.get('RAILYARDS_SCENE_LABEL','v12')
OUT=str(ROOT/os.environ.get('RAILYARDS_OUTDIR','review/v12'));os.makedirs(OUT,exist_ok=True)
scene=bpy.data.scenes['Railyards v4'];bpy.context.window.scene=scene
spec=json.load(open(str(ROOT/'scene-spec.json')))
dg=bpy.context.evaluated_depsgraph_get()
def architectural_probe(origin,direction,distance):
    origin=Vector(origin);direction=Vector(direction).normalized();travelled=0.0
    for _ in range(80):
        hit,loc,n,index,obj,matrix=scene.ray_cast(dg,origin,direction,distance=distance-travelled)
        if not hit:return None
        step=(loc-origin).length
        if not any(word in obj.name.lower() for word in ['visitor','spectator','tree','fan','r10_','atmosphere']):return {'object':obj.name,'at':list(loc),'distance':travelled+step}
        travelled+=step+.02
        if travelled>=distance:return None
        origin=loc+direction*.02
    raise RuntimeError('Too many non-architectural hits')
info={'scene':bpy.data.filepath}
route=[]
for a,b in zip(ARRIVAL_XY,ARRIVAL_XY[1:]):
    a,b=Vector(a),Vector(b);length=(b-a).length
    for i in range(max(2,round(length))):
        p=a.lerp(b,i/max(1,round(length)-1));floor=terrace_z(p.y)
        # The guide surface is linear across the grand stair; a landing puts the
        # treads up to a metre off it, so the floor window is +-1 m.
        route.append({'xy':list(p),'ground':architectural_probe((p.x,p.y,floor+1.0),(0,0,-1),2.0),'body':architectural_probe((p.x,p.y,floor+1.6),((b-a).x,(b-a).y,0),1.0)})
info['arrival_gaps']=[r for r in route if r['ground'] is None];info['arrival_obstructions']=[r for r in route if r['body'] is not None];info['arrival_samples']=len(route)
# V12: walk from the plaza edge down the left-center bank's first aisle to the wall.
if scene.get('v12_proportions'):
    v12=json.loads(scene['v12_proportions']);e0,e1=[Vector(p) for p in v12['left_center_bank']['plaza_edge']]
    along=(e1-e0).normalized();n=Vector((along.y,-along.x))
    if n.dot(-e0)<0:n=-n
    start=e0+along*6.0;steps=[]
    for k in range(0,80):
        p=start+n*(k*.25);probe=architectural_probe((p.x,p.y,40),(0,0,-1),40)
        steps.append({'xy':[round(p.x,2),round(p.y,2)],'floor':round(probe['at'][2],2) if probe else None,'object':probe['object'] if probe else None})
    info['lc_aisle_profile']=steps
    drops=[(a['floor']-b['floor']) for a,b in zip(steps,steps[1:]) if a['floor'] is not None and b['floor'] is not None]
    info['lc_aisle_max_step']=round(max(drops),2) if drops else None
    info['lc_aisle_gaps']=[s for s in steps if s['floor'] is None]
# Foul-line clearances actually present in the built scene.
def clearance(point,direction):
    probe=architectural_probe((point[0],point[1],12.6),direction,40);return round(probe['distance'],2) if probe else None
info['clearance_from_3b_line_to_seats']={str(y):clearance((0,y),(-1,0,0)) for y in (20,40,60,80)}
info['clearance_from_1b_line_to_seats']={str(x):clearance((x,0),(0,-1,0)) for x in (20,40,60,80)}
info['backstop_from_home']=clearance((0,0),(-1,-1,0))
json.dump(info,open(f'{OUT}/{label}-geometry.json','w'),indent=1)
print('V12_VERIFY',json.dumps({k:v for k,v in info.items() if k not in ('lc_aisle_profile',)},indent=0)[:3000])
if info['arrival_gaps'] or info['arrival_obstructions']:raise RuntimeError('Arrival route gap/obstruction')
apply_lighting(scene,'south')
for g in ['D2_Future development','D2_Proposed soccer stadium','D2_South source rail links','D2_South source landing buildings','D2_South source medical branding']:
    c=bpy.data.collections.get(g)
    if c:c.hide_render=True
if bpy.data.collections.get('D2_Pedestrian rail bridges'):bpy.data.collections['D2_Pedestrian rail bridges'].hide_render=False
col=bpy.data.collections['R2_Cameras']
tx,ty,tz=spec['anchors']['tower_roof']
shots={
 'N1_lc_bank_from_plaza':((56,131,terrace_z(131)+1.7),(30,108,15),24),
 'N2_lc_bank_from_field':((30,70,13.6),(35,120,20),28),
 'N3_lc_bank_aerial':((-10,60,75),(45,118,18),35),
 'N4_lc_bank_top_aisle':((58,121,terrace_z(121)+1.7),(20,120,18),22),
 'N5_park_to_bleachers':((60,200,deck_z(200)+4.5),(40,116,18),30),
 'R1_rf_corner_from_field':((40,20,14.5),(95,-8,16),30),
 'R2_rf_corner_from_river':((135,-45,7),(96,-8,16),28),
 'R3_rf_corner_aerial':((150,-70,70),(92,5,15),35),
 'R4_rf_board_from_lf':((-5,90,16),(104,37,22),40),
 'R5_rf_from_upper_deck':((-30,-30,44),(100,20,20),32),
 'D1_third_base_line':((10,-8,14.2),(-8,60,13),35),
 'D2_dugouts_from_upper':((-30,-30,44),(15,15,13),28),
 'D3_home_to_3b':((3,3,13.7),(-12,45,14),30),
 'D4_backstop':((-34,-34,30),(4,4,13),35),
 'F1_flag_close':((tx+30,ty-18,tz+6),(tx+4.6,ty+4.6,tz+8),60),
 'F2_tower_context':((tx+95,ty-120,30),(tx,ty,45),45),
 'C_entrance_landing':((92,196,deck_z(196)+1.6),(70,158,20),24),
 'E_outfield_concourse':((108,60,13.4+1.6),(60,105,15),22),
 'H_entrance_from_field':((60,95,14),(66.9,161.8,deck_z(161.8)+2),30),
}
selected=os.environ.get('RAILYARDS_VIEWS','').split(',')
for name,(pos,tgt,lens) in shots.items():
    if selected!=[''] and name not in selected:continue
    c=bpy.data.cameras.new('FR12_'+name);o=bpy.data.objects.new('FR12_'+name,c);col.objects.link(o)
    o.location=pos;o.rotation_euler=(Vector(tgt)-Vector(pos)).to_track_quat('-Z','Y').to_euler();c.lens=lens;c.clip_start=.3;c.clip_end=20000
    scene.camera=o;scene.render.resolution_x=int(os.environ.get('RAILYARDS_WIDTH','1200'));scene.render.resolution_y=round(scene.render.resolution_x*.625);scene.cycles.samples=int(os.environ.get('RAILYARDS_SAMPLES','24'))
    scene.render.filepath=f'{OUT}/{label}-{name}.png';bpy.ops.render.render(write_still=True);print('RENDERED',name)
if os.environ.get('RAILYARDS_SKIP_PLAN')=='1':sys.exit(0)
# Dimensioned plan (ortho) of the whole stadium and two sections.
def ortho(name,loc,scale,rot=(0,0,0),res=(1600,1600),clip=(0.1,2000)):
    c=bpy.data.cameras.new('FR12_'+name);o=bpy.data.objects.new('FR12_'+name,c);col.objects.link(o);c.type='ORTHO';c.ortho_scale=scale;o.location=loc;o.rotation_euler=rot;c.clip_start,c.clip_end=clip
    scene.camera=o;scene.render.resolution_x,scene.render.resolution_y=res;scene.render.filepath=f'{OUT}/{label}-{name}.png';bpy.ops.render.render(write_still=True);print('RENDERED',name)
ortho('P1_plan_stadium',(40,40,400),300)
ortho('P2_plan_north_end',(60,150,400),200)
# Section through left-center: camera looking along the plaza edge direction, thin clip slab.
ortho('S1_section_left_center',(41+120*math.cos(math.radians(-12)),123.6+120*math.sin(math.radians(-12)),25),70,(math.pi/2,0,math.radians(78)),(1600,900),(112,128))
ortho('S2_section_rf_corner',(90+150*0.645,-10-150*0.765,18),60,(math.pi/2,0,math.atan2(-0.765,0.645)+math.pi/2),(1600,900),(140,160))
ortho('S3_section_third_base',(-60,40,20),60,(math.pi/2,0,-math.pi/2),(1600,900),(40,80))
