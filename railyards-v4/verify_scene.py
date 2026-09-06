"""Inspect the reopened saved scene and write a bounded verification receipt."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
OUT=Path(__file__).resolve().parent;scene=bpy.data.scenes['Railyards v4'];spec=json.loads((OUT/'scene-spec.json').read_text())
required=['R2_Cameras','R2_Site','R2_Bowl','D2_Stadium envelope','D2_Canopy','D2_Clock tower','D2_Scoreboards','D2_Seating and spectators','D2_Landscape','D2_Adjacent buildings','D2_Public realm','D2_Field','D2_Players','D2_Outfield','D2_Skyline landmarks','D2_Riverfront retail','D2_Future development','D2_South source rail links','D2_South source landing buildings','D2_Proposed soccer stadium','D2_Southern rail bascules']
missing=[name for name in required if bpy.data.collections.get(name)is None]
assets=[]
for image in bpy.data.images:
    if image.source=='FILE'and image.filepath and not image.packed_file and not Path(bpy.path.abspath(image.filepath)).exists():assets.append(image.filepath)
projections={}
for name,c in spec['cameras'].items():
    camera=bpy.data.objects['R2_'+name];assert abs(camera.data.lens-c['lens_mm'])<.0001
    scene.render.resolution_x=c['size'][0];scene.render.resolution_y=c['size'][1];rows=[]
    for control in c['controls']:
        p=world_to_camera_view(scene,camera,Vector(control['world']));pixel=[p.x*c['size'][0],(1-p.y)*c['size'][1]]
        rows.append({'name':control['name'],'reference_pixel':control['pixel'],'projected_pixel':pixel,'error_px':math.dist(pixel,control['pixel'])})
    projections[name]=rows
assert not missing,missing
assert not assets,assets
assert scene.get('seat_count',0)>20000
assert math.isclose(scene['field_base_path_m'],27.432,abs_tol=1e-6)
assert math.isclose(scene['field_pitcher_plate_front_distance_m'],18.4404,abs_tol=1e-6)
assert scene['players_count']==11
for obj in scene.objects:
    if obj.type=='MESH':
        assert all(math.isfinite(v)for vertex in obj.data.vertices for v in vertex.co),obj.name

instances=[]
for obj in scene.objects:
    if obj.get('instance_count'):
        source=[n.inputs['Object'].default_value for m in obj.modifiers if m.type=='NODES'for n in m.node_group.nodes if n.bl_idname=='GeometryNodeObjectInfo']
        assert source and all(s and len(s.data.vertices)>0 for s in source)
        instances.append({'name':obj.name,'count':obj['instance_count'],'source_meshes':[s.name for s in source]})
result={'file':bpy.data.filepath,'blender_version':bpy.app.version_string,'scene':scene.name,'required_collections_present':not missing,'missing_external_images':assets,'camera_count':sum(o.type=='CAMERA'for o in scene.objects),'objects':len(scene.objects),'mesh_vertices_excluding_instances':sum(len(o.data.vertices)for o in scene.objects if o.type=='MESH'),'seats':scene['seat_count'],'spectators':scene['spectator_count'],'trees':sum(i['count']for i in instances if any('Broadleaf tree'in n for n in i['source_meshes'])),'pedestrians':sum(i['count']for i in instances if any('Walking visitor'in n for n in i['source_meshes'])),'outfield_context_buildings':scene.get('outfield_context_count'),'source_variant_note':scene.get('south_rail_variant_note'),'instances':instances,'projections':projections,'public_deck_grade':scene.get('public_deck_grade'),'field_base_path_m':scene['field_base_path_m'],'pitcher_plate_front_m':scene['field_pitcher_plate_front_distance_m'],'players':scene['players_count'],'limitations':'Frozen reference controls check camera calibration, not the final rebuilt architecture. Public deck grade, hidden roof profiles and context heights remain inferred. Structural verification does not establish visual fidelity.'}
(OUT/'saved-scene-verification.json').write_text(json.dumps(result,indent=2)+'\n')
scene.camera=bpy.data.objects['R2_north'];scene.render.resolution_x=1800;scene.render.resolution_y=1198
print(json.dumps({k:v for k,v in result.items()if k not in ['projections','instances']}))
