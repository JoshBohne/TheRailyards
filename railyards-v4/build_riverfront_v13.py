"""Apply the supplied McDonald's Park reference to a preserved V12 scene.

Run with Blender -b INPUT.blend --python-exit-code 1 --python this_file.
All dimensions are image-derived; mapped landmark footprints retain their frame.
"""
import json
import math
import os
import random
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT))
from r2_geometry import MeshBatch, text, instances
from r3_soccer_context import SOCCER_SPEC, _field, _seating, _roof_panel


def remove_collection(name):
    col = bpy.data.collections.get(name)
    if col:
        for obj in list(col.all_objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(col)


def build(scene):
    for name in ['D2_Proposed soccer stadium', 'D2_Southern rail bascules',
                 'R13_McDonalds Park', 'R13_Union Station powerhouse', 'R13_Rail bascules']:
        remove_collection(name)
    # Remove the speculative layer so lighting presets cannot bring it back.
    remove_collection('D2_Future development')
    mats = {m.name.removeprefix('D2_'): m for m in bpy.data.materials if m.name.startswith('D2_')}
    batch = MeshBatch(scene, mats, prefix='R13_')
    g = 'McDonalds Park'
    # Keep the old pitch/bowl helpers but register the new public west frontage.
    SOCCER_SPEC.update(center=(382., 100.), base_z=8., field_z=8.6)
    center = SOCCER_SPEC['center']
    import r3_soccer_context
    r3_soccer_context.GROUP = g
    _field(batch, center)
    _seating(batch, center)
    # Dark roof ring: level outer cornice and exposed triangular eave structure.
    for x0, x1, z0, z1 in [(-86,-49,39,41),(49,86,41,39)]:
        _roof_panel(batch, center, x0,x1,-108,108,z0,z1)
    for y0,y1,z0,z1 in [(-108,-67,39,41),(67,108,41,39)]:
        _roof_panel(batch, center,-49,49,y0,y1,z0,z1,axis='y')
    # West and south elevations: deep brick piers, tall glazed bays, dark entries.
    def facade(origin, tangent, normal, length):
        def p(u, v, z):
            return (origin[0]+tangent[0]*u+normal[0]*v,
                    origin[1]+tangent[1]*u+normal[1]*v,z)
        angle=math.atan2(tangent[1],tangent[0])
        def box(mat,u,v,z,w,d,h):batch.box(g,mat,p(u,v,z),(w,d,h),angle)
        box('brick',0,0,20,length,2,24)
        box('black_steel',0,1.05,11.5,length-2,.12,6.5)
        count=round(length/18)
        for i in range(count):
            u=-length/2+(i+.5)*length/count
            box('glass_bronze',u,1.08,23,14,.16,16)
            for dx in [-7,-4.7,-2.35,0,2.35,4.7,7]:box('black_steel',u+dx,1.25,23,.15,.2,16)
            for z in [16,20,24,28,31]:box('black_steel',u,1.25,z,14,.2,.13)
            box('brick_light',u+8,1.4,20,2.1,2,24)
            if i%2==0:
                box('paint_red',u+7.8,2.48,27,1.4,.12,6)
            # Eave triangles run from facade head to cantilever edge.
            for du in [-8,0,8]:
                batch.line(g,'black_steel',[p(u+du,0,32),p(u+du,5,38.5),p(u+du+5,0,32)],.23)
        box('black_steel',0,2,38.5,length+8,7,.55)
    facade((300,100),(0,1),(-1,0),204)
    facade((382,-2),(1,0),(0,-1),164)
    text(scene,batch.collection(g),'McDonalds Park facade sign',
         'CHICAGO FIRE', (297.5,102,32.6),2.4,mats['white'],
         rotation=(math.pi/2,0,-math.pi/2))
    # East bank is X=191. Public realm occupies the whole intervening strip.
    batch.box(g,'lawn',(244,50,8.12),(100,318,.24))
    batch.box(g,'bark',(199,50,8.3),(12,340,.25))
    batch.box(g,'paving',(289,100,8.32),(14,234,.25))
    for y in [-14,65,210]:batch.box(g,'paving',(246,y,8.36),(88,5,.2))
    for y in range(-118,220,3):
        batch.line(g,'black_steel',[(192.8,y,8.4),(192.8,y,9.5)],.045)
    batch.line(g,'black_steel',[(192.8,-120,9.5),(192.8,220,9.5)],.055)
    # Two lawn activity fields, with removable event tents and paths.
    for cy in [24,144]:
        x0,x1,y0,y1=214,276,cy-32,cy+32
        batch.line(g,'white',[(x0,y0,8.3),(x1,y0,8.3),(x1,y1,8.3),(x0,y1,8.3),(x0,y0,8.3)],.07)
        batch.line(g,'white',[(x0,cy,8.3),(x1,cy,8.3)],.07)
    rng=random.Random(13)
    tree = bpy.data.objects['D2_Broadleaf tree 0']
    positions = [(280,y,8.4) for y in range(-4,207,18)]
    instances(scene,batch.collection(g),'R13 frontage trees',tree,positions,
              scales=[(1.05,1.05,1.2)]*len(positions))
    for y in [85,107,169,191]:
        for x in [227,251]:
            for dx in [-3,3]:
                for dy in [-3,3]:batch.line(g,'white',[(x+dx,y+dy,8.3),(x+dx,y+dy,11)],.045)
            batch.add(g,'cloth_red',[(x-3,y-3,11),(x+3,y-3,11),(x+3,y+3,11),(x-3,y+3,11),(x,y,12.5)],[(0,1,4),(1,2,4),(2,3,4),(3,0,4)])
    positions=[]
    for _ in range(340):
        x=rng.choice([rng.uniform(194,203),rng.uniform(284,295),rng.uniform(216,274)])
        positions.append((x,rng.uniform(-8,205),8.4))
    for k,name in enumerate(['D2_Walking visitor cloth_red','D2_Walking visitor cloth_white','D2_Walking visitor']):
        points=positions[k::3]
        instances(scene,batch.collection(g),'R13 fans '+str(k),bpy.data.objects[name],points,
                  rotations=[(0,0,rng.random()*math.tau) for _ in points])
    powerhouse(scene,batch)
    bridges(batch)
    batch.flush()
    scene['riverfront_v13']='Reference 4 target: open riverfront and brick/glass McDonalds Park. Inferred dimensions; existing geographic registration retained for landmarks.'


def powerhouse(scene,batch):
    g='Union Station powerhouse'
    data=json.loads((OUT/'site-context.json').read_text())
    source=next(b for b in data['buildings'] if b['osm_way']==155559109)
    foot=source['footprint']
    # Remove the generic footprint and its batched windows/roof furniture.
    obj=bpy.data.objects.get('R2_OSM 155559109')
    if obj:obj.hide_render=True;obj.hide_set(True)
    for name in ['D2_Existing city facades','D2_Existing city roofs']:
        col=bpy.data.collections.get(name)
        if not col:continue
        for obj in col.objects:
            if obj.type!='MESH':continue
            bm=bmesh.new();bm.from_mesh(obj.data)
            faces=[f for f in bm.faces if 75<f.calc_center_median().x<112 and 430<f.calc_center_median().y<473]
            bmesh.ops.delete(bm,geom=faces,context='FACES');bm.to_mesh(obj.data);bm.free()
    batch.prism(g,'limestone',foot,8,31.8)
    batch.prism(g,'black_steel',foot,31.8,32.2)
    for a,b in zip(foot,foot[1:]+foot[:1]):
        a,b=Vector((*a,0)),Vector((*b,0));t=(b-a).normalized();n=Vector((t.y,-t.x,0))
        # OSM footprint is counterclockwise; normal points outward.
        for i in range(1,6):
            p=a.lerp(b,i/6)+n*.2;p.z=21
            batch.box(g,'glass_dark',p,(1.65,.18,16),math.atan2(t.y,t.x))
            for z in [15,19,23,27]:
                q=p.copy();q.z=z
                batch.box(g,'black_steel',q,(1.7,.24,.15),math.atan2(t.y,t.x))
    for y in [444,460]:
        batch.cylinder(g,'black_steel',(91,y,32),(91,y,54),1.15,r1=.85,sides=20)
        for z in range(34,54,3):batch.cylinder(g,'metal',(91,y,z),(91,y,z+.13),1.18-(z-32)*.013,sides=20)


def bridges(batch):
    g='Rail bascules'
    spec=json.loads((OUT/'bridge-spec.json').read_text())['southern_rail_bridges']
    # Both leaves raised to match attachment 2; this is a captured pose.
    for key,angle in [('primary',72),('secondary',64)]:
        entry=spec[key];y=entry['y'];pivot=entry['x_end']-5
        length=entry['x_end']-entry['x_start'];a=math.radians(angle)
        def p(s,side,z):return (pivot-s*math.cos(a)+z*math.sin(a),y+side,14+s*math.sin(a)+z*math.cos(a))
        batch.box(g,'stone',(pivot,y,5),(9,13,14))
        for side in [-4,4]:
            for z in [0,7]:batch.line(g,'black_steel',[p(0,side,z),p(length,side,z)],.32)
            for i in range(8):
                s0,s1=length*i/8,length*(i+1)/8
                batch.line(g,'black_steel',[p(s0,side,0),p(s0,side,7),p(s1,side,0)],.20)
        for i in range(9):
            s=length*i/8
            batch.line(g,'black_steel',[p(s,-4,0),p(s,4,0)],.24)
            batch.line(g,'black_steel',[p(s,-4,7),p(s,4,7)],.20)
        for side in [-2.7,-1.3,1.3,2.7]:
            batch.line(g,'rail',[p(0,side,.3),p(length,side,.3)],.10)
        for start,end in [(entry['x_start']-85,entry['x_start']),
                          (pivot+24,entry['x_end']+80)]:
            batch.box(g,'black_steel',((start+end)/2,y,13.6),(end-start,8,.8))
            for x in range(round(start),round(end),2):
                batch.box(g,'bark',(x,y,14.1),(.22,7,.2))
            for side in [-2.7,-1.3,1.3,2.7]:
                batch.line(g,'rail',[(start,y+side,14.3),(end,y+side,14.3)],.10)
            for x in range(round(start)+5,round(end),18):
                batch.box(g,'stone',(x,y,7),(2.5,8,13))
        # Open bracing rather than the former opaque raised slab.
        for x in [pivot+10,pivot+24]:
            for side in [-5,5]:batch.line(g,'black_steel',[(x,y+side,10),(x,y+side,41)],.45)
        batch.box(g,'concrete',(pivot+17,y,35),(12,10,5))
        batch.box(g,'metal',(pivot+37,y,13.7),(26,8,.6))


if __name__=='__main__':
    build(bpy.context.scene)
    dest=Path(os.environ.get('RAILYARDS_V13_OUTPUT',str(OUT/'railyards-v13-static.blend')))
    bpy.ops.wm.save_as_mainfile(filepath=str(dest))
