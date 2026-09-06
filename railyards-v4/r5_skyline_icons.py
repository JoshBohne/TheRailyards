"""V5 skyline icons ranked by projected size from the bowl (skyline-v5-icons.json).

Chase Tower, 333 South Wabash (the red one), Kluczynski, Crain Communications,
Blue Cross Blue Shield, Legacy, One Chicago, Water Tower Place and the Hilton.
Footprints from OSM where Nominatim returned a polygon, otherwise published
dimensions; heights from Wikipedia infoboxes.  Colours are the real facades so
the skyline stops reading as one tan material.  Placement through r4_geo.
"""
import json,math
from pathlib import Path
from mathutils import Vector
import r4_geo
from r4_skyline_south import _frustum,_bands,_glazing_strips,_rect

OUT=Path(__file__).resolve().parent
GROUP='Skyline landmarks V5'
Z=r4_geo.GROUND_Z


def _foot(rec):
    fp=rec.get('footprint_formula')
    if not fp:return None
    pts=[r4_geo.register(p) for p in fp];out=[];last=None
    for p in pts:
        if last is None or math.dist(p,last)>2.5:out.append(p);last=p
    if len(out)>2 and math.dist(out[0],out[-1])<2.5:out.pop()
    return out if len(out)>=3 else None


def _bbox(pts):
    xs=[p[0] for p in pts];ys=[p[1] for p in pts]
    return (min(xs)+max(xs))/2,(min(ys)+max(ys))/2,max(xs)-min(xs),max(ys)-min(ys)


def _slab(batch,rec,wall,window,pitch=4.0,band=14.0):
    """Footprint prism with vertical glazing strips on the bounding faces and floor bands."""
    h=rec['architectural_height_m'];pts=_foot(rec);cx,cy=rec['scene_xy']
    if pts:
        batch.prism(GROUP,wall,pts,Z,Z+h);bx,by,w,d=_bbox(pts)
    else:
        w,d=rec.get('size_m',(40,40));bx,by=cx,cy;batch.box(GROUP,wall,(bx,by,Z+h/2),(w,d,h))
    _glazing_strips(batch,bx,by,Z+2,Z+h-2,w*.98,d*.98,pitch,material=window)
    _bands(batch,bx,by,Z,Z+h,w*.98,d*.98,band,'metal')
    return bx,by,w,d


def chase(batch,rec):
    cx,cy=rec['scene_xy'];h=rec['architectural_height_m']
    # The long east/west faces sweep inward from a wide base to a narrow top.
    steps=12
    for k in range(steps):
        f0=1-.42*(k/steps)**1.6;f1=1-.42*((k+1)/steps)**1.6
        _frustum(batch,cx,cy,Z+h*k/steps,Z+h*(k+1)/steps,88*f0,58,88*f1,58,'granite_grey')
    _glazing_strips(batch,cx,cy,Z+3,Z+h-3,50,57,4.5,material='glass_grey')
    _bands(batch,cx,cy,Z,Z+h,50,57,12.0,'metal')
    batch.box(GROUP,'metal',(cx,cy,Z+h+1),(44,20,2))


def red(batch,rec):
    bx,by,w,d=_slab(batch,rec,'paint_red','glass_dark',3.2,8.0)
    batch.box(GROUP,'paint_red',(bx,by,Z+rec['architectural_height_m']+1.5),(w*.5,d*.5,3))


def kluczynski(batch,rec):
    _slab(batch,rec,'black_steel','glass_bronze',2.8,10.0)


def crain(batch,rec):
    cx,cy=rec['scene_xy'];h=rec['architectural_height_m'];pts=_foot(rec)
    body=h-34
    if pts:batch.prism(GROUP,'glass_grey',pts,Z,Z+body);bx,by,w,d=_bbox(pts)
    else:bx,by,w,d=cx,cy,46,46;batch.box(GROUP,'glass_grey',(bx,by,Z+body/2),(w,d,body))
    _bands(batch,bx,by,Z,Z+body,w,d,12.0,'aluminum')
    # Slanted "cut" roof, split down the middle with a narrow gap.
    for side in (-1,1):
        x0=bx+side*1.2;x1=bx+side*w/2
        lo=[(x0,by-d/2),(x1,by-d/2),(x1,by+d/2),(x0,by+d/2)]
        verts=[(x,y,Z+body) for x,y in lo]+[(x0,by-d/2,Z+h),(x1,by-d/2,Z+body+4),(x1,by+d/2,Z+body+4),(x0,by+d/2,Z+h)]
        batch.add(GROUP,'glass_white',verts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])


def bcbs(batch,rec):
    bx,by,w,d=_slab(batch,rec,'glass_blue','glass_blue',5.0,14.0)
    h=rec['architectural_height_m']
    batch.box(GROUP,'crown_white',(bx,by,Z+h+3),(w*.42,d*.9,6))


def legacy(batch,rec):
    cx,cy=rec['scene_xy'];h=rec['architectural_height_m']
    _frustum(batch,cx,cy,Z,Z+h-6,60,32,58,30,'glass_white')
    _glazing_strips(batch,cx,cy,Z+2,Z+h-8,58,30,4.0,material='glass_blue')
    _bands(batch,cx,cy,Z,Z+h-6,58,30,10.0,'aluminum')
    batch.box(GROUP,'crown_white',(cx,cy,Z+h-3),(56,28,6))


def one_chicago(batch,rec):
    cx,cy=rec['scene_xy'];h=rec['architectural_height_m']
    for dx,height,w in ((22,h,38),(-24,175,36)):
        _frustum(batch,cx+dx,cy,Z,Z+height*.55,w+8,w+4,w+8,w+4,'glass_white')
        _frustum(batch,cx+dx,cy,Z+height*.55,Z+height,w,w-4,w,w-4,'glass_white')
        _glazing_strips(batch,cx+dx,cy,Z+2,Z+height-2,w,w-4,4.5,material='glass_grey')
        _bands(batch,cx+dx,cy,Z,Z+height,w,w-4,12.0,'aluminum')
    batch.box(GROUP,'precast',(cx,cy,Z+16),(90,60,32))


def water_tower_place(batch,rec):
    cx,cy=rec['scene_xy'];h=rec['architectural_height_m'];pts=_foot(rec)
    if pts:batch.prism(GROUP,'granite_grey',pts,Z,Z+34);bx,by,w,d=_bbox(pts)
    else:bx,by,w,d=cx,cy,90,70;batch.box(GROUP,'granite_grey',(bx,by,Z+17),(w,d,34))
    batch.box(GROUP,'granite_grey',(bx,by+d*.15,Z+34+(h-34)/2),(52,30,h-34))
    _glazing_strips(batch,bx,by+d*.15,Z+36,Z+h-2,52,30,4.0,material='glass_grey')
    _bands(batch,bx,by+d*.15,Z+34,Z+h,52,30,10.0,'metal')


def hilton(batch,rec):
    bx,by,w,d=_slab(batch,rec,'limestone','glass_grey',3.6,14.0)
    batch.box(GROUP,'roof',(bx,by,Z+rec['architectural_height_m']+.4),(w*.98,d*.98,.8))


BUILDERS={'chase-tower':chase,'333-south-wabash':red,'kluczynski':kluczynski,'crain':crain,'bcbs':bcbs,'legacy':legacy,'one-chicago':one_chicago,'water-tower-place':water_tower_place,'hilton-chicago':hilton}


def build_skyline_icons(scene,spec,batch,materials):
    data=json.loads((OUT/'skyline-v5-icons.json').read_text());built=[]
    for rec in data['buildings']:
        rec['scene_xy']=r4_geo.local_xy(rec['latlon']['latitude'],rec['latlon']['longitude'])
        BUILDERS[rec['id']](batch,rec);built.append(rec['id'])
    scene['skyline_v5_icons']=','.join(built)
    return built
