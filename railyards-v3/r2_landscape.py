"""Deterministic branching trees and ground-level riverfront detail."""
import math,random
from mathutils import Vector
from r2_geometry import instances
from r2_seating import prototype

def build_landscape(scene,spec,batch,materials):
    rng=random.Random(20260905);trees=[]
    for variant in range(3):
        def tree(b,variant=variant):
            r=random.Random(132+variant)
            b.cylinder('Tree','bark',(0,0,0),(.12,-.08,5.7),.20,.08,9)
            for branch in range(18):
                theta=branch*2.399+r.uniform(-.3,.3);h=2.6+branch*.16
                root=Vector((.06,-.04,h));end=Vector((math.cos(theta)*(2.5+r.random()),math.sin(theta)*(2.5+r.random()),h+1.5+r.random()))
                mid=root.lerp(end,.6);mid.z+=.3
                b.cylinder('Tree','bark',root,mid,.085,.04,6);b.cylinder('Tree','bark',mid,end,.04,.013,5)
                for twig in range(5):
                    a=theta+twig*1.25;tip=end+Vector((math.cos(a)*.9,math.sin(a)*.9,r.uniform(-.4,.8)))
                    b.cylinder('Tree','bark',mid,tip,.018,.003,4)
                    # Leaves occupy irregular volumes around fine branch tips.
                    for leaf in range(115):
                        q=tip+Vector((r.gauss(0,.65),r.gauss(0,.65),r.gauss(0,.48)))
                        a=r.uniform(0,math.tau);e=r.uniform(-.7,.7);s=r.uniform(.08,.18)
                        u=Vector((math.cos(a),math.sin(a),e))*s;v=Vector((-math.sin(a),math.cos(a),r.uniform(-.8,.8)))*s*.48
                        mat=r.choices(['foliage','leaf_light','leaf_dark'],[5,2,3])[0]
                        b.quad('Tree',mat,[q-u,q-v+Vector((0,0,.025)),q+u,q+v])
        trees.append(prototype(scene,materials,'Broadleaf tree '+str(variant),tree))
    points=[]
    # Retain planting outside the immediate public realm.  The new public
    # realm module owns the park, lower riverwalk and their furniture.
    for y in range(-150,156,13):points.append((-88,y,8.5))
    for x in range(-85,111,12):points.append((x,-143,8.5))
    for y in range(-230,301,14):points.extend([(-205,y,8),(208,y,8)])
    for y in range(350,495,13):
        for x in [55,83,113,209,239]:points.append((x,y,8.5))
    for x in [83,229]:batch.box('Northbank garden','lawn',(x,412,8.20),(75,146,.35))
    for x,y,z in points:
        batch.box('Tree beds','soil',(x,y,z-.06),(2.4,2.4,.10))
        batch.box('Tree beds','stone',(x,y,z-.15),(2.8,2.8,.14))
    col=batch.collection('Landscape')
    for k,tree in enumerate(trees):
        positions=[];rot=[];scales=[]
        for i,(x,y,z)in enumerate(points):
            if i%3!=k:continue
            s=rng.uniform(.82,1.22);positions.append((x+rng.uniform(-.5,.5),y+rng.uniform(-.5,.5),z));rot.append((0,0,rng.random()*math.tau));scales.append((s,s,s*rng.uniform(.95,1.15)))
        instances(scene,col,'Planted broadleaf '+str(k),tree,positions,rot,scales)
    scene['tree_count']=len(points)
    def pedestrian(b):
        b.ellipsoid('Walker','cloth_gray',(0,0,1.16),(.22,.13,.31),8,5)
        b.ellipsoid('Walker','skin',(0,0,1.66),(.11,.10,.13),8,5)
        for side in [-1,1]:
            b.cylinder('Walker','navy',(side*.10,0,.95),(side*.12,side*.09,.10),.08,sides=7)
            b.cylinder('Walker','cloth_gray',(side*.22,0,1.36),(side*.28,-.09,.96),.065,sides=6)
    walker=prototype(scene,materials,'Walking visitor',pedestrian)
    positions=[];rotations=[];scales=[]
    for i in range(250):
        x,y=rng.uniform(-85,-70),rng.uniform(-135,155)
        s=rng.uniform(.90,1.08);positions.append((x,y,8.6));rotations.append((0,0,rng.random()*math.tau));scales.append((s,s,s))
    instances(scene,col,'Walking visitors',walker,positions,rotations,scales)
    scene['pedestrian_count']=len(positions)
    # Rail bed, ties and catenary-free commuter tracks.
    for x in [-139,-129,-119,-109,-99]:
        for dx in [-.72,.72]:batch.line('Rail detail','rail',[(x+dx,-350,3.65),(x+dx,365,3.65)],.075)
        for y in range(-350,366,1):batch.box('Rail detail','bark',(x,y,3.48),(2.5,.20,.12))
    # Boats establish water scale without altering the inferred site registration.
    for x,y,angle in [(155,60,.15),(174,238,-.12),(153,-98,.1)]:
        co,si=math.cos(angle),math.sin(angle)
        hull=[(-2,-7),(2,-7),(2.3,4),(0,8),(-2.3,4)]
        hull=[(x+a*co-b*si,y+a*si+b*co)for a,b in hull]
        batch.prism('River boats','white',hull,.15,1.4)
        batch.box('River boats','glass',(x,y,2.15),(3.7,7.5,1.5),angle)
        batch.box('River boats','white',(x,y,3),(4.1,8,.22),angle)
