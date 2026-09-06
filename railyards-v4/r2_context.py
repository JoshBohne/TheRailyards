"""Geographic background envelopes and explicitly inferred future-phase masses."""
import math,random,json
from pathlib import Path
from mathutils import Vector

def build_context(scene,spec,batch,materials):
    rng=random.Random(1201)
    # Extend ground beyond the geographic query so the horizon is continuous.
    # V4: the east box (x 1000-20000) is owned by r4_geography (land clipped
    # to the USGS NHD Lake Michigan shoreline); the other three stay.
    for center,size in [((-10750,0,3),(18500,40000,10)),((-250,10900,3),(2500,18200,10)),((-250,-10600,3),(2500,18800,10))]:
        batch.box('Background terrain','paving',center,size)
    roads=json.loads((Path(__file__).parent/'site-roads.json').read_text())['roads']
    for road in roads:
        for a,b in zip(road['points'],road['points'][1:]):
            a,b=Vector((*a,8.23)),Vector((*b,8.23));center=(a+b)/2
            if -225<center.x<200 and -770<center.y<340:continue
            if abs(center.x)>1490 or not -1150<center.y<1750:continue
            delta=b-a
            if delta.length<.1:continue
            n=Vector((-delta.y,delta.x,0)).normalized()*road['width_m']/2
            batch.quad('Mapped street network','asphalt',[a-n,b-n,b+n,a+n])
            if road['width_m']>=10:batch.line('Mapped street network','white',[a,b],.055,sides=4)
    def windows(group,foot,z0,z1,spacing=3.1):
        signed=sum(a[0]*b[1]-b[0]*a[1]for a,b in zip(foot,foot[1:]+foot[:1]))
        for a,b in zip(foot,foot[1:]+foot[:1]):
            a,b=Vector((*a,0)),Vector((*b,0));length=(b-a).length
            if length<1:continue
            t=(b-a).normalized();n=Vector((t.y,-t.x,0))*(1 if signed>0 else -1);angle=math.atan2(t.y,t.x)
            count=max(1,int(length/spacing));floors=max(1,int((z1-z0)/3.6))
            for j in range(floors):
                z=z0+(j+.55)*(z1-z0)/floors
                for i in range(count):
                    p=a.lerp(b,(i+.5)/count)+n*.10;p.z=z
                    batch.box(group,'glass_lit'if rng.random()<.17 else 'glass',p,(length/count*.67,.08,(z1-z0)/floors*.64),angle)
            p=(a+b)/2;p.z=z1+.15
            batch.box(group,'stone',p,(length,.4,.3),angle)
    context=json.loads((Path(__file__).parent/'site-context.json').read_text())
    for building in context['buildings']:
        if building['osm_way']==1324080275:continue  # Dedicated source-led bridgehouse owns this footprint.
        foot=building['footprint'];cx=sum(p[0]for p in foot)/len(foot);cy=sum(p[1]for p in foot)/len(foot)
        if abs(cx)>1100 or abs(cy)>1700 or building['height_m']<7:continue
        windows('Existing city facades',foot,building['base_z'],building['base_z']+building['height_m'],4.4)
    group='Future development'
    # Heights and footprints below are image-derived massing, not published plans.
    towers=[(-159,238,55,40,84),(226,-28,19,26,105),(256,294,12,16,80),(241,213,42,40,27),(263,-161,34,36,76),(85,427,49,46,48)]
    for k,(x,y,w,d,h)in enumerate(towers):
        foot=[(x-w/2,y-d/2),(x+w/2,y-d/2),(x+w/2,y+d/2),(x-w/2,y+d/2)]
        batch.prism(group,'aluminum'if k==0 else 'stone'if k==5 else 'brick_light',foot,8,h);windows(group,foot,8,h,2.7)
        for z in range(12,int(h),4):batch.box(group,'metal'if k==0 else 'stone',(x,y,z),(w+.4,d+.4,.22 if k==0 else .32))
        batch.box(group,'roof',(x,y,h+.25),(w,d,.4))
        batch.box(group,'metal',(x,y,h+1.6),(w*.45,d*.4,2.7))
    scene['future_phase_note']='South and bridge source artwork shows additional towers absent from the north source; Future development is an explicitly inferred long-term context layer.'
