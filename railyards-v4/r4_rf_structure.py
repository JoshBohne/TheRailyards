"""Continuous support beneath the right-field / clock-tower end of the bowl.

V3 left the bowl's first-base end face, the outfield bleachers and the field
platform hovering over a riverwalk cut at z4.83.  This module adds, in one
footprint, the podium that carries the field and the outfield banks down to
the site ground datum, a brick end wall following the tier profile at the
bowl's RF termination, a link block closing the gap to the clock tower base,
a river-facing arcade under the RF board, and the corner terrace with
railings that the north aerial shows between the bowl end and the board.

Everything here is inferred understructure consistent with the visible
concept artwork; it is not an engineering design.  Datums: ground z8,
lower riverwalk z4.95, podium ring (bleacher base / corner terrace) z13.4,
field z12 (podium top under the field is 11.9 to avoid coplanar faces).
"""
import math
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
from r3_envelope import _arch_bay

GROUP='RF structure'
PODIUM_BOTTOM=4.95
PODIUM_TOP=11.9
RING_TOP=13.4
RING_OFFSET=10.0  # bleacher zone depth behind the outfield wall (m); terraces end at 9.4
END_WALL_THICKNESS=1.0
TIERS=[(0.0,.34,14,24),(.40,.49,27,30),(.55,.65,33,36),(.70,.93,39,47)]


def _unit(p):
    v=Vector((p[0],p[1]));return v.normalized() if v.length>1e-6 else Vector((1,0))


def _offset(p,d):
    return tuple(Vector((p[0],p[1]))+_unit(p)*d)


def _prism_cdt(batch,material,footprint,z0,z1):
    """Prism whose caps are triangulated so concave footprints render cleanly."""
    pts=[Vector(p) for p in footprint];n=len(pts)
    verts,_e,faces,*_=delaunay_2d_cdt(pts,[(i,(i+1)%n) for i in range(n)],[],1,0.01)
    coords=[(v.x,v.y) for v in verts]
    batch.add(GROUP,material,[(x,y,z1) for x,y in coords],[tuple(f) for f in faces])
    batch.add(GROUP,material,[(x,y,z0) for x,y in coords],[tuple(reversed(f)) for f in faces])
    for a,b in zip(footprint,footprint[1:]+footprint[:1]):
        batch.quad(GROUP,material,[(a[0],a[1],z0),(b[0],b[1],z0),(b[0],b[1],z1),(a[0],a[1],z1)])


def tier_top(t):
    """Top of seating/concourse at normalized bowl depth t (front 0, back 1)."""
    previous=14.0
    for ta,tb,za,zb in TIERS:
        if t<ta:return previous+2.5
        if t<=tb:return za+(zb-za)*(t-ta)/(tb-ta)
        previous=zb
    return 47.6


def build_rf_structure(scene,spec,batch,materials):
    front=[Vector(p) for p in spec['bowl_front']];back=[Vector(p) for p in spec['bowl_back']]
    field=[(float(p[0]),float(p[1])) for p in spec['field_boundary']]
    ring=[_offset(p,RING_OFFSET) for p in field]
    # 1. Podium: bowl end (RF) -> outfield ring -> bowl end (LF) -> back along
    #    the traced bowl_back.  One prism from the riverwalk datum to just
    #    below the field plane.
    podium=[(back[0].x,back[0].y),(front[0].x,front[0].y)]+ring+[(front[-1].x,front[-1].y)]
    podium+=[(p.x,p.y) for p in reversed(back)]
    _prism_cdt(batch,'concrete',podium,PODIUM_BOTTOM,PODIUM_TOP)
    # 2. Ring step carrying the outfield banks and the two corner terraces.
    step=[(front[0].x,front[0].y)]+ring+[(front[-1].x,front[-1].y)]+list(reversed(field))
    _prism_cdt(batch,'concrete',step,PODIUM_TOP,RING_TOP)
    # Stone coping and railing along the outer ring edge (terrace parapet).
    outer=[(front[0].x,front[0].y)]+ring+[(front[-1].x,front[-1].y)]
    for a,b in zip(outer,outer[1:]):
        a,b=Vector(a),Vector(b);t=(b-a).normalized();angle=math.atan2(t.y,t.x);length=(b-a).length
        c=(a+b)/2
        batch.box(GROUP,'stone',(c.x,c.y,RING_TOP+.12),(length+.2,.9,.24),angle)
        for k in range(int(length/2.2)+1):
            p=a.lerp(b,min(1,k*2.2/length))
            batch.cylinder(GROUP,'metal',(p.x,p.y,RING_TOP+.2),(p.x,p.y,RING_TOP+1.25),.03,sides=6)
        batch.cylinder(GROUP,'metal',(a.x,a.y,RING_TOP+1.25),(b.x,b.y,RING_TOP+1.25),.035,sides=6)
    # 3. Arcade on the exposed podium faces (river side of the RF ring and the
    #    corner return), matching the envelope's brick/stone language.
    exposed=[(front[0].x,front[0].y)]+ring[:3]
    for a,b in zip(exposed,exposed[1:]):
        a,b=Vector(a),Vector(b);edge=b-a;length=edge.length
        if length<4:continue
        # Outward normal points away from home plate; _arch_bay's outward is the
        # left normal of its tangent, so feed it the reversed tangent.
        outward=_unit(((a+b)/2))
        tangent=Vector((outward.y,-outward.x,0))
        count=max(1,round(length/6.4));bay=length/count
        batch.box(GROUP,'brick',((a.x+b.x)/2,(a.y+b.y)/2,(PODIUM_BOTTOM+RING_TOP)/2+.02),(length+.3,1.1,RING_TOP-PODIUM_BOTTOM-.04),math.atan2(edge.y,edge.x))
        for k in range(count):
            c=a.lerp(b,(k+.5)/count);c=Vector((c.x,c.y,0))
            _arch_bay(batch,GROUP,c,tangent,min(4.2,bay*.7),PODIUM_BOTTOM+.3,5.6,RING_TOP,.60,materials)
        batch.box(GROUP,'stone',((a.x+b.x)/2,(a.y+b.y)/2,RING_TOP-.35),(length+.4,1.5,.3),math.atan2(edge.y,edge.x))
    # 4. RF end wall along the bowl termination line, top following the tiers.
    a,b=front[0],back[0];line=b-a;east=Vector((-line.y,line.x,0)).normalized()
    if east.x<0:east=-east
    samples=[k/40 for k in range(41)];prev=None
    for t in samples:
        p=a.lerp(b,t);top=tier_top(t)+1.1
        p0=p+east*.15;p1=p0+east*END_WALL_THICKNESS
        cur=(p0,p1,top)
        if prev:
            q0,q1,ptop=prev
            verts=[(q0.x,q0.y,PODIUM_TOP),(p0.x,p0.y,PODIUM_TOP),(p1.x,p1.y,PODIUM_TOP),(q1.x,q1.y,PODIUM_TOP),
                   (q0.x,q0.y,ptop),(p0.x,p0.y,top),(p1.x,p1.y,top),(q1.x,q1.y,ptop)]
            batch.add(GROUP,'brick',verts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
            # Stone coping along the stepped top.
            batch.add(GROUP,'stone',[(q0.x-east.x*.08,q0.y-east.y*.08,ptop),(p0.x-east.x*.08,p0.y-east.y*.08,top),(p1.x+east.x*.08,p1.y+east.y*.08,top),(q1.x+east.x*.08,q1.y+east.y*.08,ptop),
                                     (q0.x-east.x*.08,q0.y-east.y*.08,ptop+.3),(p0.x-east.x*.08,p0.y-east.y*.08,top+.3),(p1.x+east.x*.08,p1.y+east.y*.08,top+.3),(q1.x+east.x*.08,q1.y+east.y*.08,ptop+.3)],
                      [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
        prev=cur
    # Pilasters and stone plinth on the east face of the end wall, plus tall
    # arched openings at concourse levels so the wall reads as the bowl's
    # brick envelope rather than a blank slab.
    length=line.length;tangent=Vector((line.x,line.y,0)).normalized()
    for k in range(1,int(length/9)):
        p=a+line*(k*9/length);top=tier_top(k*9/length)+1.1
        c=p+east*(.15+END_WALL_THICKNESS+.28)
        batch.box(GROUP,'brick_light',(c.x,c.y,(PODIUM_TOP+top)/2),(.55,.62,top-PODIUM_TOP),math.atan2(line.y,line.x))
    c=a.lerp(b,.5)+east*(.15+END_WALL_THICKNESS/2)
    batch.box(GROUP,'stone',(c.x,c.y,PODIUM_TOP+1.7),(length+.3,END_WALL_THICKNESS+.5,3.4),math.atan2(line.y,line.x))
    for k in range(int(length/9)):
        t=(k+.5)*9/length
        if tier_top(t)<20:continue
        p=a.lerp(b,t);c=Vector((p.x,p.y,0))+Vector((east.x,east.y,0))*(.15+END_WALL_THICKNESS)
        # _arch_bay treats the left normal of its tangent as outward.
        _arch_bay(batch,GROUP,c,Vector((east.y,-east.x,0)),5.0,PODIUM_TOP+3.6,min(9.0,tier_top(t)-PODIUM_TOP-6),tier_top(t),.06,materials)
    # 5. Link block between the end wall and the clock-tower base.
    tx,ty,_=spec['anchors']['tower_roof']
    def x_on_line(y):return a.x+(b.x-a.x)*(y-a.y)/(b.y-a.y)
    y_north,y_south=ty+10.2,ty-10.2
    link=[(x_on_line(y_north)+.9,y_north),(tx-7.4,y_north),(tx-7.4,y_south),(x_on_line(y_south)+.9,y_south)]
    _prism_cdt(batch,'brick',link,8.0,33.0)
    batch.prism(GROUP,'stone',[(x-.3 if i in (1,2) else x,y) for i,(x,y) in enumerate(link)],32.6,33.4)
    batch.prism(GROUP,'roof',link,33.4,33.8)
    for z in (13.2,20.4,27.2):
        batch.prism(GROUP,'stone',[(x+(.25 if i in (1,2) else 0),y) for i,(x,y) in enumerate(link)],z,z+.45)
        for y in (y_north-.02,y_south+.02):
            for u in (.25,.5,.75):
                xx=link[0][0]+(link[1][0]-link[0][0])*u
                batch.box(GROUP,'glass_lit',(xx,y,z+3.4),(2.2,.12,4.2))
    # 6. Column line beneath the RF bank front (visible inside the arcade
    #    openings) and rakers under the bowl end so the underside is not empty.
    for k in range(6):
        t=.12+k*.16;p=a.lerp(b,t)+east*.6
        batch.cylinder(GROUP,'concrete',(p.x,p.y,PODIUM_BOTTOM),(p.x,p.y,PODIUM_TOP),.45,sides=10)
    scene['rf_structure_datums']='podium %.2f-%.2f, ring %.1f, ground 8, riverwalk 4.95'%(PODIUM_BOTTOM,PODIUM_TOP,RING_TOP)
    scene['rf_structure_note']='Inferred understructure: podium, tier-profile end wall, tower link block, river arcade; not an engineering certification.'
    return {'podium_vertices':len(podium),'ring_offset_m':RING_OFFSET}
