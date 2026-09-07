"""Left-center arrival terrace recovered from the visible north source.

The source shows a broad open connection; V8 had only the rear landing.
Its grade follows the existing park datum. Rails, stairs and canopy details
are inferred and are not an accessibility or engineering assessment.
"""
from mathutils import Vector
from r3_reference_projection import source_to_grade
from r3_public_realm import deck_z,ROAD_Y,ROAD_Z,GRADE,_slab

GROUP='Left center arrival'
SOURCE_POLYGON=[(707,626),(854,567),(896,637),(1050,689),(810,790),(695,736)]


def build_arrival(scene,spec,batch,materials):
    import bpy
    cam=bpy.data.objects['R2_north']
    points=[source_to_grade(scene,cam,p,(1944,1294),ROAD_Y,ROAD_Z,GRADE)[:2] for p in SOURCE_POLYGON]
    # Same top surface as the park and existing entrance: no invented flat
    # platform at an unrelated height. The overlap joins the existing slab.
    _slab(batch,'stone',points,lambda y:deck_z(y)+.06,lambda y:deck_z(y)-.55)
    a,b=Vector(points[0]),Vector(points[1]);direction=(b-a).normalized()
    # Retaining face on the field edge. Open stairs connect down to the banks.
    span=(b-a).length
    for low,high in [(0,.40),(.56,1)]:
        q,r=a.lerp(b,low),a.lerp(b,high)
        normal=Vector((-direction.y,direction.x))*.25
        poly=[q-normal,r-normal,r+normal,q+normal]
        _slab(batch,'brick_light',poly,deck_z,lambda y:16.5)
        for f in range(14):
            p=q.lerp(r,f/13);z=deck_z(p.y)
            batch.cylinder(GROUP,'metal',(p.x,p.y,z+.1),(p.x,p.y,z+1.10),.035,sides=6)
        batch.line(GROUP,'metal',[(q.x,q.y,deck_z(q.y)+1.1),(r.x,r.y,deck_z(r.y)+1.1)],.045,sides=6)
    # Broad access stair in the center of this boundary, descending toward
    # the field and ending at the existing upper bank elevation.
    mid=a.lerp(b,.48);toward=(-mid).normalized();width=span*.16
    top=deck_z(mid.y);steps=24;run=10.0;bottom=17.05
    for i in range(steps):
        q=mid+toward*((i+.5)*run/steps);z=top-(top-bottom)*(i+1)/steps
        import math
        batch.box(GROUP,'stone',(q.x,q.y,z-.14),(width,run/steps,.28),math.atan2(direction.y,direction.x))
    # Source-visible lightweight pergola near the left-center approach.
    c=Vector(points[0]).lerp(Vector(points[2]),.54);z=deck_z(c.y)
    for dx in (-3,3):
        for dy in (-2,2):batch.box(GROUP,'metal',(c.x+dx,c.y+dy,z+1.5),(.14,.14,3))
    for i in range(15):batch.box(GROUP,'metal',(c.x-3+i*6/14,c.y,z+3.05),(.16,4.5,.16))
    scene['left_center_arrival_note']='V9 north-source polygon connects the missing front terrace to the existing graded park; stair and support detail inferred.'
    return points
