"""Apply reproducible architectural detail to the calibrated gray scene via CLI."""
import bpy,json,sys
from pathlib import Path
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT))
from r2_materials import create_materials
from r2_geometry import MeshBatch
from r3_envelope import build_envelope
from r3_scoreboards import build_scoreboards
from r3_public_realm import build_public_realm
from r3_outfield import build_outfield
from r3_skyline import build_skyline
from r2_seating import build_seating
from r3_bowl_details import build_bowl_details
from r2_landscape import build_landscape
from r3_bridges import build_bridges
from r3_field import build_field
from r3_players import build_players
from r3_adjacent_buildings import build_adjacent_buildings
from r2_context import build_context
from r3_soccer_context import build_soccer_context
from r3_south_blocks import build_south_blocks
from r3_outfield_context import build_outfield_context
from r3_environment import build_environment
from r3_fireworks import build_fireworks
from r3_bridge_approach_park import build_bridge_approach_park
from r3_south_rail_context import build_south_rail_context
from r3_window_tones import apply_window_tones
from r4_rf_structure import build_rf_structure
from r4_geography import build_geography
from r4_skyline_south import build_skyline_south
scene=bpy.data.scenes['Railyards v4'];bpy.context.window_manager.windows[0].scene=scene
for obj in list(bpy.data.objects):
    if obj.name.startswith('D2_'):bpy.data.objects.remove(obj,do_unlink=True)
for col in list(bpy.data.collections):
    if col.name.startswith('D2_'):bpy.data.collections.remove(col)
materials=create_materials();spec=json.loads((OUT/'scene-spec.json').read_text())
replace=['Outer stadium facade','Canopy','Roof seam','Clock tower shaft','Clock tower cap','West canopy lantern','Center field screen','River field screen','Playing platform','Outfield fence','Infield clay','Infield grass','Base ','First base foul line','Third base foul line','Left field pavilion','North entertainment hall','Medical main','Medical wing','Center field pavilion','Stadium district ground','North lawn','North riverwalk','Park walk']
for obj in scene.objects:
    if not obj.name.startswith('R2_'):continue
    obj.hide_render=any(obj.name.startswith('R2_'+prefix)for prefix in replace)
    if obj.name=='R2_Rail'or obj.name.startswith('R2_Rail.'):obj.hide_render=True
    if obj.type not in ['MESH','CURVE']:continue
    name=obj.name.lower();mat='concrete'
    if 'river channel'in name:mat='water'
    elif 'ground'in name:mat='paving'
    elif 'rail cutting'in name or 'street'in name or 'roosevelt road'in name:mat='asphalt'
    elif 'rail'in name:mat='rail'
    elif 'playing platform'in name or 'infield grass'in name:mat='field'
    elif 'infield clay'in name:mat='soil'
    elif 'north lawn'in name:mat='lawn'
    elif 'foul pole'in name:mat='yellow'
    elif 'foul line'in name or 'base 'in name:mat='white'
    elif 'glass'in name:mat='glass'
    elif 'pavilion'in name or 'medical'in name or 'entertainment'in name:mat='brick'
    elif 'osm'in name:mat='stone'
    elif 'roof'in name:mat='roof'
    obj.data.materials.clear();obj.data.materials.append(materials[mat])
    if obj.type=='MESH' and obj.name.startswith('R2_OSM'):
        obj.data.materials.append(materials['roof'])
        for face in obj.data.polygons:
            if face.normal.z>.8:face.material_index=1
    if obj.type=='MESH' and not obj.data.uv_layers:
        uv=obj.data.uv_layers.new(name='Physical meters')
        for face in obj.data.polygons:
            n=face.normal
            for i in face.loop_indices:
                p=obj.data.vertices[obj.data.loops[i].vertex_index].co
                uv.data[i].uv=(p.x,p.y)if abs(n.z)>.8 else ((p.y,p.z)if abs(n.x)>abs(n.y)else(p.x,p.z))
batch=MeshBatch(scene,materials);build_envelope(scene,spec,batch,materials)
build_scoreboards(scene,spec,batch,materials)
build_seating(scene,spec,batch,materials)
build_bowl_details(scene,spec,batch,materials)
build_landscape(scene,spec,batch,materials)
build_bridges(scene,spec,batch,materials)
build_field(scene,spec,batch,materials)
build_players(scene,spec,batch,materials)
build_adjacent_buildings(scene,spec,batch,materials)
build_public_realm(scene,spec,batch,materials)
build_outfield(scene,spec,batch,materials)
build_rf_structure(scene,spec,batch,materials)
build_skyline(scene,spec,batch,materials)
build_context(scene,spec,batch,materials)
build_geography(scene,spec,batch,materials)
build_skyline_south(scene,spec,batch,materials)
build_soccer_context(scene,spec,batch,materials)
build_south_blocks(scene,spec,batch,materials)
build_outfield_context(scene,spec,batch,materials)
build_environment(scene,spec,batch,materials)
build_fireworks(scene,spec,batch,materials)
build_bridge_approach_park(scene,spec,batch,materials)
build_south_rail_context(scene,spec,batch,materials)
objects=batch.flush()
apply_window_tones(scene)
scene.world.node_tree.nodes.get('Background').inputs[0].default_value=(.24,.34,.48,1);scene.world.node_tree.nodes.get('Background').inputs[1].default_value=.55
bpy.data.objects['R2_Sun'].data.energy=1.5;bpy.data.objects['R2_Sun'].data.color=(1,.78,.54)
scene['stage']='V4 in progress: source-backed stadium and immediate-area reconstruction; not visually accepted'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'railyards-v4-detail.blend'))
print(json.dumps({'stage':scene['stage'],'objects':len(scene.objects),'new_meshes':len(objects),'vertices':sum(len(o.data.vertices)for o in scene.objects if o.type=='MESH')}))
