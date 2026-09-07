"""Apply V11 circulation plus the V12 proportion corrections and save V12.

Runs at the end of the V12 chain (see build_v12.sh) on the freshly built
scene, which already carries the corrected bowl front, dugouts, flag mast,
RF board house and revised outfield banks from the V12 generators.  This
stage adds the V11 public realm, regrades the restaurant, and builds the
left-center bank and right-field corner from r12_outfield.  V11 and older
saved scenes are not touched.
"""
import bpy,json,sys,random,math
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent;sys.path.insert(0,str(OUT))
from r2_geometry import MeshBatch
from r3_public_realm import build_public_realm,ROOF_PIXELS as PARK_PIXELS,ROAD_Y,ROAD_Z,GRADE,inside,deck_z,STAIR_Y_TOP,STAIR_Y_BOTTOM
from r3_reference_projection import source_to_surface,source_to_plane
from r3_restaurant import ROOF_PIXELS
from r11_circulation import regrade_restaurant,terrace_z,build_terrace_surface,rail,slab,stairs
from r12_outfield import build_lc_bank,build_rf_corner,build_river_deck,build_terrace_front,build_terrace_surface_v12,in_lc_bank,in_corner_bank
from r2_lighting import apply_lighting
scene=bpy.data.scenes['Railyards v4'];bpy.context.window.scene=scene
spec=json.loads((OUT/'scene-spec.json').read_text())
if 'bowl_front_v11_trace' not in spec:raise ValueError('V12 needs the corrected bowl_front in scene-spec.json')
skyline=json.loads((OUT/'skyline-buildings.json').read_text())
materials={m.name[3:]:m for m in bpy.data.materials if m.name.startswith('D2_') and '.' not in m.name}
for name in ['D2_Public realm','D2_Riverfront retail','D2_Left center arrival']:
    col=bpy.data.collections.get(name)
    if col:
        for obj in list(col.objects):bpy.data.objects.remove(obj,do_unlink=True)
        bpy.data.collections.remove(col)
batch=MeshBatch(scene,materials)
build_public_realm(scene,spec,batch,materials,circulation=True)
cam=bpy.data.objects['R2_north']
roof=[source_to_plane(scene,cam,p,(1944,1294),22)[:2] for p in ROOF_PIXELS]
entrance=[source_to_surface(scene,cam,p,(1944,1294),deck_z)[:2] for p in [(695,736),(808,668),(1050,689),(810,790)]]
from r9_arrival import SOURCE_POLYGON
front_terrace=[source_to_surface(scene,cam,p,(1944,1294),deck_z)[:2] for p in SOURCE_POLYGON]
regrade_restaurant(scene,batch,roof,entrance,front_terrace)


def connect_outfield_v12(batch,front_terrace):
    """V11 connect_outfield without the LF stair, field-edge rail and plaza
    columns: the left-center bank now carries the plaza edge down to the field."""
    polygons=[front_terrace]
    # V12: the V11 elevated path over the outfield void is gone (the left-center
    # bank now fills that void); the RF stair keeps a small landing on the
    # restaurant roof edge instead.
    landing=[(106.5,85.5),(113.5,85.5),(113.5,96.5),(106.5,96.5)]
    polygons.append(landing)
    for aa,bb in [((106.5,85.5),(113.5,85.5)),((113.5,85.5),(113.5,96.5))]:
        rail(batch,'V11 Outfield upper concourse',(aa[0],aa[1],terrace_z(aa[1])),(bb[0],bb[1],terrace_z(bb[1])))
    for x,y in [(107.2,86.2),(112.8,86.2)]:
        z=terrace_z(y);batch.box('V11 Concourse supports','brick_dark',(x,y,(13.4+z)/2),(.55,.65,z-13.4))
    stairs(batch,'V11 RF concourse stair',(110,89,terrace_z(89)),(112,65,13.4),4.2,1)
    c=Vector(front_terrace[0]).lerp(Vector(front_terrace[2]),.54);z=terrace_z(c.y)
    for dx in (-3,3):
        for dy in (-2,2):batch.box('V11 LF pergola','metal',(c.x+dx,c.y+dy,z+1.5),(.14,.14,3))
    for i in range(15):batch.box('V11 LF pergola','metal',(c.x-3+i*6/14,c.y,z+3.05),(.16,4.5,.16))
    return polygons


def open_lower_landings_v12(scene,batch,spec,front_terrace):
    import bmesh
    for suffix,lo,hi in [('metal',13.3,14.8),('stone',13.3,13.7)]:
        obj=bpy.data.objects.get('D2_RF structure '+suffix)
        if not obj:continue
        mesh=bmesh.new();mesh.from_mesh(obj.data);seen=set();remove=[]
        for vertex in mesh.verts:
            if vertex in seen:continue
            stack=[vertex];component=[];seen.add(vertex)
            while stack:
                v=stack.pop();component.append(v)
                for edge in v.link_edges:
                    other=edge.other_vert(v)
                    if other not in seen:seen.add(other);stack.append(other)
            if all(lo<=v.co.z<=hi for v in component):remove.extend(component)
        bmesh.ops.delete(mesh,geom=remove,context='VERTS');mesh.to_mesh(obj.data);mesh.free()
    field=[Vector(p[:2]) for p in spec['field_boundary']]
    outer=[Vector(spec['bowl_front'][0][:2])]+[p+p.normalized()*10 for p in field]+[Vector(spec['bowl_front'][-1][:2])]
    portals=[Vector((110,65))]
    for a,b in zip(outer,outer[1:]):
        count=max(1,math.ceil((b-a).length/1.7))
        for i in range(count):
            p,q=a.lerp(b,i/count),a.lerp(b,(i+1)/count);c=(p+q)/2
            if any((c-portal).length<3.2 for portal in portals):continue
            if in_lc_bank(c,front_terrace) or in_corner_bank(c,spec):continue
            rail(batch,'V11 Lower concourse guardrail',(p.x,p.y,13.4),(q.x,q.y,13.4))
    batch.box('V11 Lower concourse landings','stone',(110.5,65,13.25),(6.5,6,.30))


polygons=connect_outfield_v12(batch,front_terrace)
park=[source_to_surface(scene,cam,p,(1944,1294),deck_z)[:2] for p in PARK_PIXELS]
build_terrace_surface_v12(batch,polygons+[roof,entrance,park],[STAIR_Y_TOP,STAIR_Y_BOTTOM])
front=build_terrace_front(scene,batch,spec,materials,park,roof)
open_lower_landings_v12(scene,batch,spec,front_terrace)
rng=random.Random(1212)
lc=build_lc_bank(scene,batch,spec,front_terrace,roof,rng)
corner=build_rf_corner(scene,batch,spec,materials,rng)
gallery=build_river_deck(scene,batch,spec,materials,rng)
batch.flush()
scene['seat_count']=int(scene['seat_count'])+lc['seats']+corner['seats']
scene['spectator_count']=int(scene['spectator_count'])+lc['spectators']+corner['spectators']
# CF board sits above, and is supported by, the public terrace (unchanged from V11).
board_base=terrace_z(126);screen_bottom=board_base+3.8;delta=screen_bottom-18
for obj in bpy.data.collections['D2_Scoreboards'].objects:
    if obj.type=='MESH':
        for v in obj.data.vertices:
            if v.co.y<80:continue
            if v.co.z<18:v.co.z=board_base+(v.co.z-13)/5*(screen_bottom-board_base)
            else:v.co.z+=delta
    elif obj.name.startswith('D2_cf_scoreboard_top'):obj.location.z+=delta
scene['v11_circulation']='Public deck continues onto graded restaurant terrace; source-led riverfront arcade, stepped quay and corner stair.'
scene['v11_cf_board_bottom']=screen_bottom
scene['v12_proportions']=json.dumps({'bowl_front':spec['bowl_front_basis'],'left_center_bank':lc,'rf_corner':corner,'river_gallery':gallery,'terrace_front':front,
 'dugouts':'both 20 m, 12.8 m off the foul lines','flag':'mast on the tower roof cap','rf_board':'brick board house on the podium ring'})
scene['v12_source_boundaries']='Source establishes plaza-to-bleacher continuity, a solid RF corner under the board and a roof mast; foul clearances, rakes, row counts, cut lines and understructure are inferred.'
scene['stage']='V12: stadium proportions (bowl front, left-center bank, RF corner, flag)'
apply_lighting(scene,'south')
scene.camera=bpy.data.objects['R2_north']
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'railyards-v12-static.blend'),compress=True)
print('V12_BUILD',json.dumps({'scene':bpy.data.filepath,'terrace_at_entry':terrace_z(161.8),'cf_board_bottom':screen_bottom,'objects':len(scene.objects),'lc':lc,'corner':corner,'seat_count':scene['seat_count']}))
