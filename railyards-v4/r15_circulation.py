"""Freestanding park arches opening onto the level, open-air concourse.

The user's corrected spatial brief is authoritative: no roof over the arrival;
the scoreboard terrace is a separate higher destination with its own stair.
"""
import math
import bpy
from r13_outfield import remove_collection
from r11_circulation import slab, rail, stairs, terrace_z

FLOOR = 13.4
FIELD_CONCOURSE = FLOOR
TERRACE = 22.055


def passage_z(y):
    return FLOOR


def approach_z(y):
    return FLOOR + (terrace_z(220)-FLOOR)*max(0,min(1,(y-181)/39))


def open_box(objects,low,high):
    """Trim authored surfaces without Boolean solids on legacy open meshes."""
    def split(poly,axis,bound,sign):
        inside=[];outside=[]
        for a,b in zip(poly,poly[1:]+poly[:1]):
            da=(a[axis]-bound)*sign;db=(b[axis]-bound)*sign
            (inside if da>=0 else outside).append(a)
            if (da>=0)!=(db>=0):
                p=a.lerp(b,da/(da-db));inside.append(p);outside.append(p)
        return inside,outside
    for obj in objects:
        verts=[];faces=[];material_ids=[];inverse=obj.matrix_world.inverted()
        for face in obj.data.polygons:
            remainder=[obj.matrix_world@obj.data.vertices[i].co for i in face.vertices]
            fragments=[]
            for axis,bound,sign in [(i,low[i],1)for i in range(3)]+[(i,high[i],-1)for i in range(3)]:
                if len(remainder)<3:break
                remainder,outside=split(remainder,axis,bound,sign)
                if len(outside)>=3:fragments.append(outside)
            for poly in fragments:
                start=len(verts);verts.extend(inverse@v for v in poly)
                faces.append(tuple(range(start,len(verts))));material_ids.append(face.material_index)
        obj.data.clear_geometry();obj.data.from_pydata(verts,[],faces)
        for face,index in zip(obj.data.polygons,material_ids):face.material_index=index
        obj.data.update()


def build(scene, batch, root):
    del root
    # Keep the new terrace paving material independently editable.
    paving = bpy.data.materials.new('D2_v15_paving')
    paving.diffuse_color = (.43, .44, .40, 1)
    paving.use_nodes = True
    shader = paving.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = paving.diffuse_color
    shader.inputs['Roughness'].default_value = .86
    batch.materials['v15_paving'] = paving
    for name in ['D2_V12 Terrace front','D2_V13 Park arcade','D2_V13 Passage field stair',
                 'D2_V11 LF pergola','D2_V13 Vomitory rails','D2_V14 Vomitory edge guards',
                 'D2_V12 Left-center bank','D2_V14 Left-center bank support']:
        remove_collection(name)
    # Open the courtyard completely to the sky. The scoreboard and its
    # restaurant terrace remain south/east of this cut, clear of the arches.
    owners=['D2_Centerfield restaurant replacement','D2_V11 Continuous terrace',
            'D2_V11 Terrace cornice','D2_V11 Terrace railing','D2_V11 Outfield upper concourse','D2_V11 LF field edge',
            'D2_V11 Plaza supports','D2_V11 Concourse supports','D2_V11 LF concourse stair',
            'D2_Centerfield terrace dining','D2_Centerfield board canopy',
            'D2_Centerfield curved terrace bench','D2_V14 Left-center bank support',
            'D2_V12 Left-center bank']
    objects=[o for name in owners if (c:=bpy.data.collections.get(name)) for o in c.objects
             if o.type=='MESH' and o.data.polygons]
    open_box(objects,(32,128,FLOOR-.01),(104,181,80))
    open_box(objects,(24,97,FLOOR-.01),(76,181,80))
    open_box(objects,(47,104.5,FLOOR-.01),(55,129.1,80))
    open_box(objects,(47,180.9,FLOOR-.01),(55,220,80))
    # A level court continues through the freestanding arches and the open
    # slot between the left-center seating banks. Grade change stays north.
    terrace=[(24,108),(42,110),(74,97.5),(76,128),(104,128),(104,181),(24,181)]
    batch.prism('V15 Open arrival court','v15_paving',terrace,FLOOR-.4,FLOOR)
    for a,b in zip(terrace[:3],terrace[1:3]):
        rail(batch,'V15 Field overlook',(*a,FLOOR),(*b,FLOOR),1.05)
    slab(batch,'V15 Park approach','v15_paving',[(47,181),(55,181),(55,220),(47,220)],
         approach_z,lambda y:approach_z(y)-.35)
    # Guards enclose the grade change without blocking the central approach.
    for a,b in [((24,128,FLOOR),(24,181,FLOOR)),((104,128,FLOOR),(104,181,FLOOR)),
                ((24,181,FLOOR),(47,181,FLOOR)),((55,181,FLOOR),(104,181,FLOOR))]:
        rail(batch,'V15 Court perimeter',a,b,1.05)
    for x in [47.15,54.85]:
        rail(batch,'V15 Park approach',(x,181,FLOOR),(x,220,approach_z(220)),1.05)
    # Nine masonry arches support only their own shallow coping.
    group='V15 Freestanding arches';width=5.1;radius=width/2
    spring=FLOOR+2.55;top=FLOOR+6.25
    bays=[(33.5+i*7,7)for i in range(6)]+[(75.5+i*8.4,8.4)for i in range(3)]
    for start,bay in bays:
        center=start+bay/2
        for sign in [-1,1]:
            batch.box(group,'brick',(center+sign*(width+bay)/4,160.2,(FLOOR+top)/2),
                      ((bay-width)/2,1.2,top-FLOOR))
        for k in range(24):
            a=-radius+width*k/24;b=-radius+width*(k+1)/24
            za=spring+math.sqrt(max(0,radius*radius-a*a));zb=spring+math.sqrt(max(0,radius*radius-b*b))
            points=[(center+a,159.6,za),(center+b,159.6,zb),(center+b,159.6,top),(center+a,159.6,top),
                    (center+a,160.8,za),(center+b,160.8,zb),(center+b,160.8,top),(center+a,160.8,top)]
            batch.add(group,'brick',points,[(0,1,2,3),(7,6,5,4),(0,4,5,1),(3,2,6,7)])
            for y in [159.55,160.85]:
                a0=math.pi*k/24;a1=math.pi*(k+1)/24
                batch.quad(group,'stone',[(center+r*math.cos(a),y,spring+r*math.sin(a))
                    for r,a in [(radius,a0),(radius+.22,a0),(radius+.22,a1),(radius,a1)]])
        batch.box(group,'stone',(center,160.2,top+.12),(bay+.02,1.4,.24))
    # Separate eastern stair reaches the scoreboard terrace, never crossing
    # over the arch arrival or the open passage into the seating bowl.
    stairs(batch,'V15 Scoreboard terrace stair',(99,126,TERRACE),(99,155,FLOOR),4,2)
    batch.box('V15 Scoreboard terrace stair','v15_paving',(99,126,TERRACE-.18),(4,4,.36))
    for a,b in [((76,128,TERRACE),(96.8,128,TERRACE)),((101.2,128,TERRACE),(104,128,TERRACE))]:
        rail(batch,'V15 Terrace courtyard edge',a,b,1.1)
    # Clear chairs from the newly open sky slot; preserve the two flanking
    # banks and regrade park/terrace visitors onto their actual new floors.
    removed_seats=regraded=0
    for obj in scene.objects:
        if obj.type!='MESH' or obj.data.polygons:continue
        scales=obj.data.attributes.get('scale')
        if not scales:continue
        is_seat='seat' in obj.name.lower() and 'source' not in obj.name.lower()
        for i,v in enumerate(obj.data.vertices):
            x,y,z=v.co
            if 46.4<x<55.6 and 104.8<y<129 and z>FLOOR:
                if scales.data[i].vector.length>.1 and is_seat:removed_seats+=1
                scales.data[i].vector=(0,0,0)
            elif not is_seat and any(w in obj.name.lower() for w in ['visitor','crowd','fan','spectator']):
                if 32<x<104 and 128<y<181 and z>13:
                    if 159.2<y<161.2:scales.data[i].vector=(0,0,0)
                    else:v.co.z=FLOOR
                    regraded+=1
                elif 47<x<55 and 181<=y<=220 and z>13:v.co.z=approach_z(y);regraded+=1
    from r2_geometry import instances
    prototype=bpy.data.objects.get('D2_Walking visitor')
    if prototype:
        points=[(x,y,FLOOR)for x,y in [(50,173),(52,166),(50,153),(52,141),(50,130),(52,119),(50,111)]]
        instances(scene,batch.collection('V15 Open arrival court'),'V15 Arcade walkers',prototype,points,
                  rotations=[(0,0,math.pi)]*len(points))
    scene['v15_arrival_route']='Freestanding arches -> broad level open-air field overlook at13.4m; separate eastern stair to22.055m scoreboard terrace.'
    return {'arch_floor_m':FLOOR,'outfield_concourse_m':FLOOR,'scoreboard_roof_m':TERRACE,
            'arcade_openings':9,'open_terrace_width_m':52,'roof_over_arrival':False,'left_center_seating_bank_removed':True,
            'removed_grand_stair':True,'separate_scoreboard_stair':True,
            'removed_open_slot_seats':removed_seats,'regraded_visitors':regraded,
            'route':[[51,220,approach_z(220)],[51,181,FLOOR],[51,161,FLOOR],[51,140,FLOOR],[51,110,FLOOR]],
            'basis':'User clarification: freestanding arches and level open-air concourse. Separate terrace stair and unseen structural details inferred.'}
