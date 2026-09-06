"""Museum Campus and lakefront reference landmarks from OSM footprints.

Soldier Field, Field Museum, Shedd Aquarium, Adler Planetarium and Wintrust
Arena use their mapped footprints (lakefront-v5.json); heights are inferred
from photographs and labelled so.  McCormick Place Lakeside Center has no
polygon in the fetch and is an inferred dark box.  These are points of
reference east of the ballpark, sized to read from the elevated cameras.
"""
import json,math
from pathlib import Path
from mathutils import Vector
import r4_geo

OUT=Path(__file__).resolve().parent
GROUP='Lakefront landmarks'
Z=r4_geo.GROUND_Z


def _centroid(pts):
    return sum((Vector(p) for p in pts),Vector((0,0)))/len(pts)


def _inset(pts,factor):
    c=_centroid(pts);return [(c.x+(p[0]-c.x)*factor,c.y+(p[1]-c.y)*factor) for p in pts]


def _simplify(pts,step=6.0):
    out=[];last=None
    for p in pts:
        if last is None or math.dist(p,last)>step:out.append(p);last=p
    if len(out)>2 and math.dist(out[0],out[-1])<step:out.pop()
    return out


def build_lakefront(scene,spec,batch,materials):
    data=json.loads((OUT/'lakefront-v5.json').read_text());items=data['items'];built=[]
    def foot(key):return _simplify([r4_geo.register(p) for p in items[key]['footprint']])
    # Soldier Field: limestone colonnade ring, the 2003 bowl rising inside it, field in the middle.
    sf=foot('soldier-field');c=_centroid(sf);it=items['soldier-field']
    batch.prism(GROUP,'limestone',sf,Z,Z+it['colonnade_top'])
    batch.prism(GROUP,'limestone',_inset(sf,1.02),Z+it['colonnade_top'],Z+it['colonnade_top']+1.2)
    bowl=_inset(sf,.86);batch.prism(GROUP,'glass_grey',bowl,Z+it['colonnade_top'],Z+it['bowl_top'])
    for z in range(int(Z+it['colonnade_top'])+4,int(Z+it['bowl_top'])-2,5):batch.prism(GROUP,'aluminum',_inset(sf,.87),z,z+.3)
    batch.prism(GROUP,'lawn',_inset(sf,.48),Z+it['colonnade_top']-2,Z+it['colonnade_top']-1.8)
    # Colonnade columns on the long sides (Doric rows), every 5 m along the ring.
    for a,b in zip(sf,sf[1:]+sf[:1]):
        a,b=Vector(a),Vector(b);n=max(1,int((b-a).length/5.2))
        for k in range(n):
            p=a.lerp(b,(k+.5)/n)+(c-a.lerp(b,(k+.5)/n)).normalized()*2.2
            batch.cylinder(GROUP,'white_marble',(p.x,p.y,Z+it['colonnade_top']-9),(p.x,p.y,Z+it['colonnade_top']+.3),.7,sides=8)
    built.append('soldier-field')
    # Field Museum: long white marble mass with the raised central hall.
    fm=foot('field-museum');c=_centroid(fm);it=items['field-museum']
    batch.prism(GROUP,'white_marble',fm,Z,Z+it['roof']);batch.prism(GROUP,'roof',fm,Z+it['roof'],Z+it['roof']+.4)
    batch.box(GROUP,'white_marble',(c.x,c.y,Z+it['roof']+(it['hall_top']-it['roof'])/2),(70,46,it['hall_top']-it['roof']))
    batch.box(GROUP,'roof',(c.x,c.y,Z+it['hall_top']+.3),(72,48,.6))
    for a,b in zip(fm,fm[1:]+fm[:1]):
        a,b=Vector(a),Vector(b);n=max(1,int((b-a).length/6.0))
        for k in range(n):
            p=a.lerp(b,(k+.5)/n)+(c-a.lerp(b,(k+.5)/n)).normalized()*.6
            batch.box(GROUP,'white_marble',(p.x,p.y,Z+it['roof']*.55),(1.3,1.3,it['roof']*.8))
    built.append('field-museum')
    # Shedd Aquarium: octagonal marble block with the dome.
    sh=foot('shedd-aquarium');c=_centroid(sh);it=items['shedd-aquarium']
    batch.prism(GROUP,'white_marble',sh,Z,Z+it['roof']);batch.prism(GROUP,'roof',sh,Z+it['roof'],Z+it['roof']+.4)
    batch.ellipsoid(GROUP,'copper_green',(c.x,c.y,Z+it['roof']),(24,24,it['dome_top']-it['roof']),24,10)
    built.append('shedd-aquarium')
    # Adler Planetarium: granite dodecagon with the dome.
    ad=foot('adler-planetarium');c=_centroid(ad);it=items['adler-planetarium']
    batch.prism(GROUP,'granite_pink',ad,Z,Z+it['roof']);batch.ellipsoid(GROUP,'aluminum',(c.x,c.y,Z+it['roof']),(19,19,it['dome_top']-it['roof']),20,8)
    built.append('adler-planetarium')
    # Wintrust Arena: precast box with a curved roof suggested by a low ridge.
    wa=foot('wintrust-arena');c=_centroid(wa);it=items['wintrust-arena']
    batch.prism(GROUP,'precast',wa,Z,Z+it['roof']-6);batch.prism(GROUP,'aluminum',_inset(wa,.9),Z+it['roof']-6,Z+it['roof'])
    built.append('wintrust-arena')
    # McCormick Place Lakeside Center: inferred dark steel box on the shore.
    mc=items['mccormick-lakeside'];x,y=r4_geo.local_xy(*mc['latlon']);w,d=mc['size_m']
    batch.box(GROUP,'black_steel',(x,y,Z+mc['roof']/2),(w,d,mc['roof']));batch.box(GROUP,'roof',(x,y,Z+mc['roof']+.4),(w+6,d+6,.8))
    for dx in range(-int(w/2)+20,int(w/2),40):
        batch.box(GROUP,'black_steel',(x+dx,y,Z+mc['roof']+2.5),(2,d+8,4))
    built.append('mccormick-lakeside')
    scene['lakefront_landmarks']=','.join(built);scene['lakefront_basis']=data['source']
    return built
