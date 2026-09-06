"""Visible near-bank planting and lit paths in the bridge-view foreground."""
import math,random
import bpy
from r2_geometry import instances


def build_bridge_approach_park(scene,spec,batch,materials):
    group='Bridge approach park';rng=random.Random(3906)
    # Existing north-bank lawn parcels are retained. Source A3 resolves a
    # dense eastern tree canopy and a more open, lit western path garden.
    points=[(rng.uniform(207,259),rng.uniform(352,476),8.5) for _ in range(70)]
    tree=bpy.data.objects.get('D2_Broadleaf tree 1')
    if tree:
        scales=[(s,s,s*1.15)for s in [rng.uniform(1.25,1.8)for _ in points]]
        instances(scene,batch.collection(group),'Mature approach trees',tree,points,
                  [(0,0,rng.random()*math.tau)for _ in points],scales)
    for offset in [-20,16]:
        path=[(86+offset+9*math.sin(i/24*math.pi*2),344+i*4.9,8.48)for i in range(25)]
        batch.line(group,'paving',path,1.1,sides=8)
    ring=[(84+11*math.cos(i*math.tau/64),380+15*math.sin(i*math.tau/64),8.48)for i in range(65)]
    batch.line(group,'paving',ring,1.2,sides=8)
    for y in [351,374,397,420]:
        for x in [60,84,108]:
            batch.cylinder(group,'metal',(x,y,8.5),(x,y,13),.055,sides=6)
        for x in [60,84]:
            chain=[]
            for i in range(25):
                t=i/24;p=(x+24*t,y,13-.85*math.sin(math.pi*t));chain.append(p)
                if i%2==0:batch.ellipsoid(group,'lamp',p,(.075,.075,.10),6,4)
            batch.line(group,'metal',chain,.012,sides=4)
        data=bpy.data.lights.new('D2_Public light approach '+str(y),'AREA');data.energy=160;data.shape='DISK';data.size=9;data.color=(1,.69,.35)
        obj=bpy.data.objects.new(data.name,data);batch.collection('Lighting').objects.link(obj);obj.location=(84,y,12.8)
    scene['bridge_approach_park_note']='A3 resolves dense foreground bank trees, looping garden paths and festoon lights. Parcel bounds retained; individual trees, path radii and strand locations inferred.'
