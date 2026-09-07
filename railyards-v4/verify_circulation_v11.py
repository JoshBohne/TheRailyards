"""Repeat Fable's fixed pedestrian-camera and entrance-probe review on a saved scene."""
import bpy,json,math,sys,os
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from r3_reference_projection import source_to_grade
from r2_lighting import apply_lighting
OUT=str(ROOT/os.environ.get('RAILYARDS_OUTDIR','review/v11'));os.makedirs(OUT,exist_ok=True)
scene=bpy.data.scenes['Railyards v4'];bpy.context.window.scene=scene
spec=json.load(open(str(ROOT/'public-realm-spec.json')))
P=spec['parameters'];ROAD_Y,ROAD_Z,GRADE,LOWER_Z=P['ROAD_Y'],P['ROAD_Z'],P['GRADE'],P['LOWER_Z']
deck_z=lambda y:ROAD_Z+GRADE*(ROAD_Y-y)
cam=bpy.data.objects['R2_north']
proj=lambda px:source_to_grade(scene,cam,px,(1944,1294),ROAD_Y,ROAD_Z,GRADE)[:2]
roof=[proj(p) for p in P['ROOF_PIXELS']];entrance=[proj(p) for p in [(695,736),(808,668),(1050,689),(810,790)]]
info={'roof':[[round(x,1),round(y,1)] for x,y in roof],'entrance':[[round(x,1),round(y,1)] for x,y in entrance],'entrance_deck_z':[round(deck_z(y),2) for x,y in entrance]}
ec=Vector(( sum(p[0] for p in entrance)/4, sum(p[1] for p in entrance)/4 ));info['entrance_center']=[round(ec.x,1),round(ec.y,1),round(deck_z(ec.y),2)]
# what's in front of a pedestrian at the entrance landing walking toward the field (toward home plate)
dg=bpy.context.evaluated_depsgraph_get()
def probe(origin,direction,dist=80):
    hit,loc,n,idx,obj,mat=scene.ray_cast(dg,Vector(origin),Vector(direction).normalized(),distance=dist)
    return {'hit':bool(hit),'object':obj.name if hit else None,'at':[round(v,1) for v in loc] if hit else None,'distance':round((Vector(loc)-Vector(origin)).length,1) if hit else None}
eye=Vector((ec.x,ec.y,deck_z(ec.y)+1.6))
toward=Vector((0,0,0))-Vector((ec.x,ec.y,0));toward.z=0
info['probe_from_entrance_toward_home']=[probe(eye,toward,120)]
for dz in (-1.2,0,2,5):
    d=toward.normalized().copy();d.z=dz/20;info[f'probe_pitch_{dz}']=probe(eye,d,120)
# vertical probe: what is the ground below the entrance center at various points along the route to home
for f in [0,.15,.3,.45,.6]:
    p=Vector((ec.x,ec.y,0))+toward*f;p.z=60
    info[f'ground_at_{f}']=probe(p,(0,0,-1),80)
# Walk the delivered arrival path, probing the floor and body clearance.
from r11_circulation import ARRIVAL_XY,terrace_z
route=[]
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
    raise RuntimeError('Too many non-architectural hits along circulation probe')
for a,b in zip(ARRIVAL_XY,ARRIVAL_XY[1:]):
    a,b=Vector(a),Vector(b);length=(b-a).length
    for i in range(max(2,round(length))):
        p=a.lerp(b,i/max(1,round(length)-1));floor=terrace_z(p.y)
        ground=architectural_probe((p.x,p.y,floor+.4),(0,0,-1),.85)
        obstruction=architectural_probe((p.x,p.y,floor+1.1),((b-a).x,(b-a).y,0),1.0)
        route.append({'xy':list(p),'expected_floor':floor,'ground':ground,'body_obstruction':obstruction})
info['arrival_route']=route
info['arrival_route_gaps']=[p for p in route if p['ground'] is None]
info['arrival_route_obstructions']=[p for p in route if p['body_obstruction'] is not None]
print('V11_ROUTE',json.dumps({'samples':len(route),'gaps':len(info['arrival_route_gaps']),'obstructions':info['arrival_route_obstructions']}))
# objects near the entrance (bbox overlap)
near=[]
for o in scene.objects:
    if o.type!='MESH' or o.hide_render:continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box];xs=[v.x for v in bb];ys=[v.y for v in bb];zs=[v.z for v in bb]
    if min(xs)<ec.x+40 and max(xs)>ec.x-40 and min(ys)<ec.y+25 and max(ys)>ec.y-45 and max(zs)>8 and o.name not in ('D2_Background terrain paving',):
        if len(o.data.vertices)>0:near.append((o.name,[round(min(xs)),round(max(xs)),round(min(ys)),round(max(ys)),round(min(zs),1),round(max(zs),1)]))
info['objects_near_entrance']=near[:80]
json.dump(info,open(OUT+'/entrance-geometry.json','w'),indent=1);print(json.dumps({k:v for k,v in info.items() if k not in ['objects_near_entrance','arrival_route']},indent=0))
if info['arrival_route_gaps'] or info['arrival_route_obstructions']:
    raise RuntimeError('V11 arrival route has a missing floor or architectural obstruction; see entrance-geometry.json')
# Diagnostic cameras along the route (eye level 1.6 m), day preset
apply_lighting(scene,'south')
for g in ['D2_Future development','D2_Proposed soccer stadium','D2_South source rail links','D2_South source landing buildings','D2_South source medical branding']:
    c=bpy.data.collections.get(g)
    if c:c.hide_render=True
if bpy.data.collections.get('D2_Pedestrian rail bridges'):bpy.data.collections['D2_Pedestrian rail bridges'].hide_render=False
col=bpy.data.collections['R2_Cameras']
shots={
 'I_corner_stair_close':((124,282,6.6),(103,298,10),24),
 'J_lf_stair':((57,132,23.7),(30,116.8,14.5),22),
 'L_lf_stair_lower':((21,107,16),(45,121,21),24),
 'M_lf_stair_side':((60,114,26),(38,119,18),24),
 'K_rf_stair':((118,94,22.8),(111,65,13.4),22),
 'A_roosevelt_sidewalk':((60,306,deck_z(306)+1.6),(ec.x,ec.y,deck_z(ec.y)+2),24),
 'B_park_mid':((ec.x+18,ec.y+70,deck_z(ec.y+70)+1.6),(ec.x,ec.y,deck_z(ec.y)+2),24),
 'C_entrance_landing':((ec.x,ec.y+8,deck_z(ec.y+8)+1.6),(ec.x+toward.normalized().x*30,ec.y+toward.normalized().y*30,deck_z(ec.y)+1),22),
 'D_entrance_look_back':((ec.x+toward.normalized().x*6,ec.y+toward.normalized().y*6,deck_z(ec.y)+1.6),(ec.x,ec.y+60,deck_z(ec.y+60)+2),22),
 'E_outfield_concourse':((108,60,13.4+1.6),(60,105,15),22),
 'F_riverwalk_under_deck':((118,215,5.0+1.6),(110,260,8),22),
 'G_corner_stair':((124,175,5.0+1.6),(90,205,14),22),
 'H_entrance_from_field':((60,95,14),(ec.x,ec.y,deck_z(ec.y)+2),30),
}
selected=os.environ.get('RAILYARDS_VIEWS','').split(',')
for name,(pos,tgt,lens) in shots.items():
    if selected!=[''] and name not in selected:continue
    c=bpy.data.cameras.new('FR_'+name);o=bpy.data.objects.new('FR_'+name,c);col.objects.link(o)
    o.location=pos;o.rotation_euler=(Vector(tgt)-Vector(pos)).to_track_quat('-Z','Y').to_euler();c.lens=lens;c.clip_start=.3;c.clip_end=20000
    scene.camera=o;scene.render.resolution_x=int(os.environ.get('RAILYARDS_WIDTH','1200'));scene.render.resolution_y=round(scene.render.resolution_x*.625);scene.cycles.samples=int(os.environ.get('RAILYARDS_SAMPLES','24'))
    scene.render.filepath=f'{OUT}/{name}.png';bpy.ops.render.render(write_still=True);print('RENDERED',name)
if os.environ.get('RAILYARDS_SKIP_PLAN')=='1':sys.exit(0)
# plan of the north end
c=bpy.data.cameras.new('FR_plan');o=bpy.data.objects.new('FR_plan',c);col.objects.link(o);c.type='ORTHO';c.ortho_scale=260;o.location=(70,190,400);o.rotation_euler=(0,0,0);c.clip_end=2000
scene.camera=o;scene.render.resolution_x=1600;scene.render.resolution_y=1600;scene.render.filepath=f'{OUT}/plan_north_end.png';bpy.ops.render.render(write_still=True);print('RENDERED plan')
