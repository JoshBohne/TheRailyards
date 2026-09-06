"""Linked seating and crowd geometry, with a regulation-scaled infield."""
import math,random
import bpy
from mathutils import Vector
from r2_geometry import MeshBatch,resample,instances

def prototype(scene,materials,name,build):
    batch=MeshBatch(scene,materials,prefix='D2_Proto_');build(batch)
    objects=batch.flush()
    # Join mesh datablocks without operators, keeping prototype coordinates local.
    vertices=[];faces=[];indices=[];mats=[]
    for obj in objects:
        start=len(vertices);vertices.extend([tuple(v.co)for v in obj.data.vertices])
        faces.extend([tuple(start+i for i in p.vertices)for p in obj.data.polygons])
        indices.extend([len(mats)]*len(obj.data.polygons));mats.append(obj.data.materials[0])
        bpy.data.objects.remove(obj,do_unlink=True)
    mesh=bpy.data.meshes.new('D2_'+name);mesh.from_pydata(vertices,[],faces)
    for material in mats:mesh.materials.append(material)
    for face,index in zip(mesh.polygons,indices):face.material_index=index
    obj=bpy.data.objects.new('D2_'+name,mesh)
    # An unlinked source remains in the blend via its Geometry Nodes reference.
    obj.use_fake_user=True
    return obj

def build_seating(scene,spec,batch,materials):
    rng=random.Random(1948)
    def seat(b):
        b.box('Seat','seat',(0,0,.43),(.43,.40,.085))
        b.box('Seat','seat',(0,.18,.69),(.44,.07,.44))
        for x in [-.23,.23]:
            b.box('Seat','metal',(x,0,.23),(.035,.30,.46))
            b.box('Seat','metal',(x,0,.61),(.035,.35,.035))
    source=prototype(scene,materials,'Seat source',seat)
    people=[]
    for color in ['cloth_black','cloth_white','cloth_gray','navy','cloth_blue','cloth_red']:
        def person(b,color=color):
            b.ellipsoid('Person',color,(0,.04,.78),(.20,.13,.28),8,5)
            b.ellipsoid('Person','skin',(0,.03,1.16),(.105,.095,.125),8,5)
            for x in [-.10,.10]:
                b.cylinder('Person','navy',(x,.02,.50),(x,-.32,.48),.075,sides=6)
                b.cylinder('Person','navy',(x,-.32,.48),(x,-.34,.10),.06,sides=6)
                b.cylinder('Person',color,(x*1.8,0,.91),(x*2,-.18,.62),.055,sides=6)
            b.ellipsoid('Person',color,(0,.03,1.24),(.11,.105,.045),8,4)
        people.append(prototype(scene,materials,'Seated fan '+color,person))
    positions=[];rotations=[];fanpos=[[]for _ in people];fanrot=[[]for _ in people]
    front=[Vector(p)for p in spec['bowl_front']];back=[Vector(p)for p in spec['bowl_back']]
    tiers=[(0,.34,14,24,24),(.40,.49,27,30,8),(.55,.65,33,36,9),(.70,.93,39,47,18)]
    for tier,(ta,tb,za,zb,rows)in enumerate(tiers):
        for row in range(rows):
            t=ta+(tb-ta)*(row+.48)/rows;z=za+(zb-za)*row/rows
            path=resample([(a.x*(1-t)+b.x*t,a.y*(1-t)+b.y*t,z)for a,b in zip(front,back)],.54)
            for i,p in enumerate(path[1:-1],1):
                # Radial aisles stay aligned as each concentric row grows.
                section=(i/(len(path)-1)*27)%1
                if section<.10:continue
                tangent=(path[i+1]-path[i-1]).normalized();angle=math.atan2(tangent.y,tangent.x)
                positions.append(tuple(p));rotations.append((0,0,angle))
                if rng.random()<(.83 if tier<2 else .75):
                    k=rng.choices(range(6),[32,27,18,15,5,3])[0]
                    fanpos[k].append(tuple(p));fanrot[k].append((0,0,angle+rng.uniform(-.07,.07)))
        for i in range(0,len(front),6):
            a,b=front[i],back[i]
            p=a.lerp(b,ta);q=a.lerp(b,tb);p.z=za+1.0;q.z=zb+1.0
            batch.line('Bowl railings','metal',[p,q],.026)
    col=batch.collection('Seating and spectators')
    instances(scene,col,'Individual seats',source,positions,rotations)
    for k,person in enumerate(people):instances(scene,col,'Spectators '+str(k),person,fanpos[k],fanrot[k])
    scene['seat_count']=len(positions);scene['spectator_count']=sum(map(len,fanpos))

