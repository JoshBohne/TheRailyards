"""V6: the left-field end of the bowl.

The north aerial shows the upper decks terminating against a brick gatehouse
with a tall arched opening toward the park, with the left-field pavilion
behind it.  V3-V5 ended the bowl with the envelope's dark louver band running
over the pavilion as a flat slab.  This module gives the LF termination line
(bowl_front[-1] -> bowl_back[-1]) the same tier-profile brick end wall as the
right-field end (r4_rf_structure), and adds the gatehouse block that bridges
the gap between the bowl end and the pavilion footprint, with an arch on its
park face.  Inferred geometry consistent with the artwork, not a design.
"""
import math
from mathutils import Vector
from r3_envelope import _arch_bay,_arch_ring
from r4_rf_structure import tier_top,_prism_cdt,PODIUM_TOP,END_WALL_THICKNESS

GROUP='LF end'
BASE_Z=8.0


def build_lf_end(scene,spec,batch,materials):
    front=[Vector(p) for p in spec['bowl_front']];back=[Vector(p) for p in spec['bowl_back']]
    a,b=front[-1],back[-1];line=b-a
    # Outward normal points away from the field (north / west side of the line).
    out=Vector((-line.y,line.x,0)).normalized()
    if out.y<0:out=-out
    pav=[p for p in spec['buildings'] if p['name']=='Left field pavilion'][0]
    pav_roof=float(pav['roof']);pav_y=min(p[1] for p in pav['footprint'])
    # 1. Tier-profile brick end wall, capped so it never rises above the
    #    pavilion junction line the envelope already slopes to (47.6 -> 33.1).
    def cap(y):return 47.6-(47.6-33.1)*min(1,max(0,(y-108)/(126.2-108)))
    prev=None
    for k in range(41):
        t=k/40;p=a.lerp(b,t);top=min(tier_top(t)+1.1,cap(p.y)+1.1)
        p0=p+out*.15;p1=p0+out*END_WALL_THICKNESS;cur=(p0,p1,top)
        if prev:
            q0,q1,ptop=prev
            batch.add(GROUP,'brick',[(q0.x,q0.y,BASE_Z),(p0.x,p0.y,BASE_Z),(p1.x,p1.y,BASE_Z),(q1.x,q1.y,BASE_Z),(q0.x,q0.y,ptop),(p0.x,p0.y,top),(p1.x,p1.y,top),(q1.x,q1.y,ptop)],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
            batch.add(GROUP,'stone',[(q0.x,q0.y,ptop),(p0.x,p0.y,top),(p1.x,p1.y,top),(q1.x,q1.y,ptop),(q0.x,q0.y,ptop+.3),(p0.x,p0.y,top+.3),(p1.x,p1.y,top+.3),(q1.x,q1.y,ptop+.3)],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
        prev=cur
    length=line.length
    for k in range(1,int(length/9)):
        p=a+line*(k*9/length);top=min(tier_top(k*9/length),cap(p.y))+1.1;c=p+out*(.15+END_WALL_THICKNESS+.28)
        batch.box(GROUP,'brick_light',(c.x,c.y,(BASE_Z+top)/2),(.55,.62,top-BASE_Z),math.atan2(line.y,line.x))
    c=a.lerp(b,.5)+out*(.15+END_WALL_THICKNESS/2)
    batch.box(GROUP,'stone',(c.x,c.y,BASE_Z+1.7),(length+.3,END_WALL_THICKNESS+.5,3.4),math.atan2(line.y,line.x))
    # V9: the former full-depth block extended to the first row and created
    # an unsupported 34 m blank wall beside left field. The source arch is
    # above the rear pavilion, so leave the front 40% to the tier end wall.
    # 2. Gatehouse: brick block between the bowl end line and the pavilion,
    #    full canopy-junction height, with a tall arch on the park face and
    #    a stone belt at the pavilion roof line.
    x_left=min(p[0] for p in pav['footprint'])+.5;x_right=a.lerp(b,.40).x
    def y_on_line(x):return a.y+(b.y-a.y)*(x-a.x)/(b.x-a.x)
    gate=[(x_right,y_on_line(x_right)+.2),(x_right,pav_y-.4),(x_left,pav_y-.4),(x_left,y_on_line(x_left)+.2)]
    gate_top=44.0  # V9: confine the inferred gatehouse to the rear tier, below the 44 m roof trace
    batch.prism(GROUP,'brick',gate,BASE_Z,gate_top)
    batch.prism(GROUP,'stone',[(x-.2 if i in (2,3) else x+.2,y) for i,(x,y) in enumerate(gate)],gate_top,gate_top+.35)
    batch.prism(GROUP,'roof',gate,gate_top+.35,gate_top+.8)
    for z in (pav_roof-.4,20.4):
        batch.prism(GROUP,'stone',[(x-.25 if i in (2,3) else x+.25,y) for i,(x,y) in enumerate(gate)],z,z+.45)
    # Arched opening on the north (park) face: _arch_bay's outward is the left
    # normal of its tangent, so a tangent pointing +X puts the opening on +Y (the park side).
    cx=(x_left+x_right)/2;face=Vector((cx,pav_y-.4,0))
    width=min(14.0,(x_right-x_left)*.55)
    # The arch sits above the pavilion roof, where the artwork shows it.
    _arch_bay(batch,GROUP,face,Vector((1,0,0)),width,pav_roof+1.2,gate_top-pav_roof-4.0,gate_top,.06,materials)
    # Small square windows in the brick above the arch, like the pavilion.
    for u in (-width*.62,width*.62):
        for z in (pav_roof+5.0,pav_roof+9.5):
            batch.box(GROUP,'glass_grey',(cx-u,pav_y-.4+.12,z),(2.2,.12,3.0))
    scene['lf_end_note']='V6 inferred: tier-profile brick end wall on the LF termination and a gatehouse block with a park-facing arch bridging to the pavilion; matches the north aerial gatehouse reading.'
    return {'gate':gate,'gate_top':gate_top}
