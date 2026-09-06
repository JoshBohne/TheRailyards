"""Sightline-ranked V4 skyline additions: the near-South-Loop lakefront cluster
and the three downtown towers that read largest from the bowl.

Ranking (see skyline-v4-additions.json for bearings, distances and projected
pixel heights): NEMA, One Museum Park, The Grant and 1000M sit at local
azimuth 10-33 deg, 1.1-1.3 km from the bowl, and project 150-290 px tall in the
third-base and upper-deck views.  They were absent from every V3 dataset.
311 South Wacker, Chicago Board of Trade and Franklin Center replace generic
prisms in the north-west view.  Placement uses the shared r4_geo registration;
buildings are never moved to make them photogenic.
"""
import json,math
from pathlib import Path
import r4_geo

OUT=Path(__file__).resolve().parent
GROUP='Skyline landmarks V4'
Z=r4_geo.GROUND_Z


def _rect(cx,cy,w,d,angle=0.0):
    c,s=math.cos(angle),math.sin(angle)
    return [(cx+a*w/2*c-b*d/2*s,cy+a*w/2*s+b*d/2*c) for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]]


def _frustum(batch,cx,cy,z0,z1,w0,d0,w1,d1,material,angle=0.0):
    bottom=_rect(cx,cy,w0,d0,angle);top=_rect(cx,cy,w1,d1,angle)
    verts=[(x,y,z0) for x,y in bottom]+[(x,y,z1) for x,y in top]
    faces=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    batch.add(GROUP,material,verts,faces)


def _bands(batch,cx,cy,z0,z1,w,d,spacing,material='aluminum',angle=0.0,thickness=.22):
    z=z0+spacing
    while z<z1-1:
        batch.box(GROUP,material,(cx,cy,z),(w+.5,d+.5,thickness),angle);z+=spacing


def _glazing_strips(batch,cx,cy,z0,z1,w,d,pitch,angle=0.0,material='glass'):
    """Vertical dark glazing strips on all faces (reads at 1-2 km)."""
    c,s=math.cos(angle),math.sin(angle)
    def place(u,v,size_u,size_v):
        x=cx+u*c-v*s;y=cy+u*s+v*c
        batch.box(GROUP,material,(x,y,(z0+z1)/2),(size_u,size_v,z1-z0-1.0),angle)
    n=max(1,round(w/pitch))
    for i in range(n):
        u=-w/2+w*(i+.5)/n
        for v in (-d/2-.12,d/2+.12):place(u,v,min(2.6,w/n*.62),.14)
    n=max(1,round(d/pitch))
    for i in range(n):
        v=-d/2+d*(i+.5)/n
        for u in (-w/2-.12,w/2+.12):place(u,v,.14,min(2.6,d/n*.62))


def _nema(batch,rec):
    cx,cy=rec['scene_xy'];h=rec['architectural_height_m']
    # Vinoly's three-part bundled-tube composition: site podium, square middle
    # with a stair-stepped southern extension, indented upper section.
    _frustum(batch,cx,cy+8,Z,Z+48,62,70,62,70,'precast')
    _bands(batch,cx,cy+8,Z,Z+48,62,70,4.0,'metal')
    mid_top=Z+178
    _frustum(batch,cx,cy+8,Z+48,mid_top,44,44,44,44,'glass_grey')
    _glazing_strips(batch,cx,cy+8,Z+48,mid_top,44,44,7.5)
    _bands(batch,cx,cy+8,Z+48,mid_top,44,44,12.0)
    # Southern "staircase" of stacked bays stepping down away from the shaft.
    for k,(top,depth) in enumerate([(Z+150,14),(Z+118,14),(Z+86,14)]):
        y=cy+8-22-depth/2-k*depth
        _frustum(batch,cx,y,Z+48,top,44,depth,44,depth,'glass')
        _glazing_strips(batch,cx,y,Z+48,top,44,depth,7.5)
    # Upper section with two indents, then the crown.
    _frustum(batch,cx,cy+8,mid_top,Z+h-14,36,36,36,36,'glass_grey')
    _glazing_strips(batch,cx,cy+8,mid_top,Z+h-14,36,36,7.5)
    for dx,dy in [(-1,1),(1,-1)]:
        batch.box(GROUP,'metal',(cx+dx*13,cy+8+dy*13,(mid_top+Z+h-14)/2),(10.5,10.5,Z+h-14-mid_top+.6))
    _frustum(batch,cx,cy+8,Z+h-14,Z+h,28,28,28,28,'glass_grey')
    batch.box(GROUP,'metal',(cx,cy+8,Z+h+.3),(30,30,.6))


def _one_museum_park(batch,rec):
    cx,cy=rec['scene_xy'];h=rec['architectural_height_m']
    # Rounded lakeward face on a rectangular core; light blue-green glass.
    pts=[]
    for i in range(25):
        a=-math.pi/2+math.pi*i/24;pts.append((cx+22*math.cos(a),cy+22*math.sin(a)))
    pts+= [(cx-16,cy+22),(cx-16,cy-22)]
    batch.prism(GROUP,'glass_blue',pts,Z,Z+h-6)
    for z in range(int(Z+12),int(Z+h-6),12):batch.prism(GROUP,'aluminum',[(x*1.0,y*1.0) for x,y in pts],z,z+.3)
    batch.prism(GROUP,'crown_white',[(cx+.9*(x-cx),cy+.9*(y-cy)) for x,y in pts],Z+h-6,Z+h)
    # Museum Tower: the shorter twin immediately south (1235 S Prairie, 124 m).
    mx,my=rec['museum_tower_scene_xy']
    _frustum(batch,mx,my,Z,Z+124,34,30,34,30,'glass')
    _bands(batch,mx,my,Z,Z+124,34,30,12.0)


def _the_grant(batch,rec):
    cx,cy=rec['scene_xy'];h=rec['architectural_height_m']
    _frustum(batch,cx,cy,Z,Z+h-4,40,40,36,36,'glass_grey')
    _glazing_strips(batch,cx,cy,Z,Z+h-4,38,38,6.5)
    _bands(batch,cx,cy,Z,Z+h-4,38,38,14.0,'metal')
    batch.box(GROUP,'metal',(cx,cy,Z+h-2),(30,30,4))


def _1000m(batch,rec):
    cx,cy=rec['scene_xy'];h=rec['architectural_height_m']
    # Jahn's slender curved slab: tapers as it rises, horizontal spandrels.
    steps=10
    for k in range(steps):
        z0=Z+h*k/steps;z1=Z+h*(k+1)/steps
        f0=1-.22*(k/steps)**1.4;f1=1-.22*((k+1)/steps)**1.4
        pts0=[];pts1=[]
        for f,pts in ((f0,pts0),(f1,pts1)):
            w=44*f;d=22+6*f
            for i in range(13):
                a=-math.pi/2+math.pi*i/12;pts.append((cx+w/2*math.cos(a)*.55+w/2*.45,cy+d/2*math.sin(a)))
            pts+=[(cx-w/2,cy+d/2),(cx-w/2,cy-d/2)]
        verts=[(x,y,z0) for x,y in pts0]+[(x,y,z1) for x,y in pts1];n=len(pts0)
        faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
        batch.add(GROUP,'glass_white',verts,faces)
        for z in (z0+h/steps*.5,):batch.prism(GROUP,'aluminum',[(cx+(x-cx)*1.02,cy+(y-cy)*1.02) for x,y in pts0],z,z+.3)
    batch.box(GROUP,'glass_white',(cx+4,cy,Z+h+3),(18,14,6))


def _311_south_wacker(batch,rec):
    cx,cy=rec['scene_xy'];h=rec['architectural_height_m']
    body=h-32
    _frustum(batch,cx,cy,Z,Z+body,58,58,52,52,'granite_pink')
    _glazing_strips(batch,cx,cy,Z,Z+body,55,55,6.0)
    _bands(batch,cx,cy,Z,Z+body,55,55,16.0,'metal')
    # Glass "crown": tall translucent cylinder ringed by four smaller cylinders.
    batch.cylinder(GROUP,'crown_white',(cx,cy,Z+body),(cx,cy,Z+h),13.5,sides=24)
    for dx,dy in [(-17,-17),(17,-17),(17,17),(-17,17)]:
        batch.cylinder(GROUP,'crown_white',(cx+dx,cy+dy,Z+body),(cx+dx,cy+dy,Z+body+18),6.0,sides=16)
    batch.cylinder(GROUP,'lamp',(cx,cy,Z+h),(cx,cy,Z+h+3),1.2,sides=8)


def _cbot(batch,rec):
    cx,cy=rec['scene_xy'];h=rec['architectural_height_m']
    # Art-deco setbacks and the pyramidal copper roof with the Ceres figure.
    for z0,z1,w,d in [(Z,Z+34,76,58),(Z+34,Z+92,58,50),(Z+92,Z+142,40,42),(Z+142,Z+162,28,30)]:
        _frustum(batch,cx,cy,z0,z1,w,d,w,d,'limestone')
        _glazing_strips(batch,cx,cy,z0,z1,w,d,4.5)
    _frustum(batch,cx,cy,Z+162,Z+h-9,26,26,6,6,'copper_green')
    batch.cylinder(GROUP,'aluminum',(cx,cy,Z+h-9),(cx,cy,Z+h),1.4,.6,sides=8)


def _franklin_center(batch,rec):
    cx,cy=rec['scene_xy'];h=rec['architectural_height_m']
    # Setbacks at floors 15/30/45, granite deepening at the base, spiked pinnacles.
    for z0,z1,w,d,mat in [(Z,Z+62,64,52,'granite_pink'),(Z+62,Z+124,54,44,'granite_pink'),(Z+124,Z+186,46,38,'granite_pink'),(Z+186,Z+h-16,38,32,'granite_pink')]:
        _frustum(batch,cx,cy,z0,z1,w,d,w,d,mat)
        _glazing_strips(batch,cx,cy,z0,z1,w,d,5.0)
    _frustum(batch,cx,cy,Z+h-16,Z+h-4,38,32,26,22,'granite_pink')
    for dx,dy in [(-14,-11),(14,-11),(14,11),(-14,11),(0,0)]:
        batch.cylinder(GROUP,'metal',(cx+dx,cy+dy,Z+h-6),(cx+dx,cy+dy,Z+h+(6 if dx==0 else 0)),.7,.2,sides=6)


BUILDERS={'nema':_nema,'one-museum-park':_one_museum_park,'the-grant':_the_grant,'1000m':_1000m,
          '311-south-wacker':_311_south_wacker,'chicago-board-of-trade':_cbot,'franklin-center':_franklin_center}


def build_skyline_south(scene,spec,batch,materials):
    data=json.loads((OUT/'skyline-v4-additions.json').read_text())
    built=[]
    for rec in data['buildings']:
        rec['scene_xy']=r4_geo.local_xy(rec['latlon']['latitude'],rec['latlon']['longitude'])
        if rec.get('museum_tower_latlon'):
            rec['museum_tower_scene_xy']=r4_geo.local_xy(*rec['museum_tower_latlon'])
        BUILDERS[rec['id']](batch,rec);built.append(rec['id'])
    scene['skyline_v4_additions']=','.join(built)
    scene['skyline_v4_registration']='r4_geo.local_xy (formula + 33 m X)'
    return built
