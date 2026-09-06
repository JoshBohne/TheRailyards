"""V7: concourses between the seating tiers, visible from inside the bowl.

V3 closed each tier gap with a flat glass ribbon and stuck flat "entry" boxes
on it.  This module builds, for each of the three concourse levels: a walkway
slab, a front rail, a back wall in segments with real vomitory openings
(dark tunnels recessed behind the wall), suite/club glazing between the
openings, and lamp strips under the overhang so the walkways read at night.
Dimensions follow the tier datums in build_blockout (gap = 0.06 of the bowl
depth, next tier 3 m higher); the arrangement is inferred, not surveyed.
"""
import math
from mathutils import Vector

GROUP='Concourses'
TIERS=[(0.0,.34,14,24),(.40,.49,27,30),(.55,.65,33,36),(.70,.93,39,47)]


def build_concourses(scene,spec,batch,materials):
    front=[Vector(p) for p in spec['bowl_front']];back=[Vector(p) for p in spec['bowl_back']]
    n=len(front)
    def at(i,t,z):
        p=front[i].lerp(back[i],t);return Vector((p.x,p.y,z))
    openings=0
    for k in range(3):
        _ta,tb,_za,zb=TIERS[k];ta_next,_tb2,za_next,_zb2=TIERS[k+1]
        floor=zb;wall_top=za_next-.9  # the next tier's fascia hangs 0.9 m below its first row
        t_front=tb+.012;t_wall=ta_next-.008
        # Walkway slab across the whole gap and a low front wall with a rail.
        for i in range(n-1):
            a0,a1=at(i,t_front,floor-.35),at(i+1,t_front,floor-.35)
            b0,b1=at(i,t_wall,floor-.35),at(i+1,t_wall,floor-.35)
            batch.add(GROUP,'concrete',[tuple(a0),tuple(a1),tuple(b1),tuple(b0),(a0.x,a0.y,floor),(a1.x,a1.y,floor),(b1.x,b1.y,floor),(b0.x,b0.y,floor)],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
            f0,f1=at(i,t_front,floor),at(i+1,t_front,floor)
            batch.add(GROUP,'precast',[tuple(f0),tuple(f1),(f1.x,f1.y,floor+.9),(f0.x,f0.y,floor+.9)],[(0,1,2,3)])
            batch.add(GROUP,'precast',[(f0.x,f0.y,floor+.9),(f1.x,f1.y,floor+.9),tuple(f1),tuple(f0)],[(0,1,2,3)])
            if i%2==0:batch.cylinder(GROUP,'metal',(f0.x,f0.y,floor+.9),(f0.x,f0.y,floor+1.15),.03,sides=6)
            batch.cylinder(GROUP,'metal',(f0.x,f0.y,floor+1.15),(f1.x,f1.y,floor+1.15),.035,sides=6)
        # Back wall in segments; every 12th index a 3-index vomitory opening.
        i=0
        while i<n-1:
            is_open=(i%12) in (5,6,7)
            w0,w1=at(i,t_wall,floor),at(i+1,t_wall,floor)
            if is_open:
                # Tunnel: dark box recessed 5 m behind the wall line, with a lit soffit.
                if i%12==5:
                    c0=at(i,t_wall,floor);c1=at(min(n-1,i+3),t_wall,floor);mid=(c0+c1)/2
                    tangent=(c1-c0);width=tangent.length;tangent.normalize();inward=Vector((-tangent.y,tangent.x,0))
                    back_dir=(at(i,t_wall+.02,floor)-at(i,t_wall,floor)).normalized()
                    centre=mid+back_dir*2.6;centre.z=floor+1.4
                    angle=math.atan2(tangent.y,tangent.x)
                    batch.box(GROUP,'interior',(centre.x,centre.y,centre.z),(width-.4,5.2,2.8),angle)
                    lamp=mid+back_dir*1.2;batch.box(GROUP,'lamp',(lamp.x,lamp.y,floor+2.55),(width*.5,.18,.08),angle)
                    for u in (-width/2+.1,width/2-.1):
                        q=mid+tangent*u;batch.box(GROUP,'stone',(q.x,q.y,floor+1.4),(.35,.4,2.8),angle)
                    batch.box(GROUP,'stone',(mid.x,mid.y,floor+2.95),(width+.2,.45,.35),angle)
                    openings+=1
            else:
                # Wall panel: precast base, then suite glazing on the upper part.
                batch.add(GROUP,'precast',[tuple(w0),tuple(w1),(w1.x,w1.y,floor+1.1),(w0.x,w0.y,floor+1.1)],[(0,1,2,3)])
                batch.add(GROUP,'precast',[(w0.x,w0.y,floor+1.1),(w1.x,w1.y,floor+1.1),tuple(w1),tuple(w0)],[(0,1,2,3)])
                glass='glass_lit' if (i//12)%2==0 else 'glass_grey'
                batch.add(GROUP,glass,[(w0.x,w0.y,floor+1.1),(w1.x,w1.y,floor+1.1),(w1.x,w1.y,wall_top),(w0.x,w0.y,wall_top)],[(0,1,2,3)])
                batch.add(GROUP,glass,[(w0.x,w0.y,wall_top),(w1.x,w1.y,wall_top),(w1.x,w1.y,floor+1.1),(w0.x,w0.y,floor+1.1)],[(0,1,2,3)])
                if i%2==0:batch.box(GROUP,'aluminum',(w0.x,w0.y,(floor+1.1+wall_top)/2),(.12,.16,wall_top-floor-1.1),0)
            # Soffit lamp strip under the next tier, lighting the walkway.
            if i%4==0:
                s=at(i,(t_front+t_wall)/2,za_next-.95)
                batch.box(GROUP,'lamp',(s.x,s.y,s.z),(1.2,.35,.06))
            i+=1
    scene['concourse_openings']=openings
    scene['concourse_note']='V7 inferred concourses: walkway, front rail, segmented back wall with recessed vomitories, suite glazing, soffit lamps.'
    return openings
