"""Explicit B6 source variant for covered links and west-side landing buildings."""
import math
import bpy
from mathutils import Vector
from r3_reference_projection import source_to_plane
from r3_adjacent_buildings import _facade,_roof_and_parapet
from r3_medical import ROOF_PIXELS,ROOF_Z,_edge
from r2_geometry import text

LINKS=[[(748,1683),(1450,1608),(1452,1625),(758,1705)],
       [(1108,2070),(1700,1960),(1704,1986),(1115,2092)],
       [(1420,2370),(2080,2255),(2090,2285),(1430,2400)]]


def build_south_rail_context(scene,spec,batch,materials):
    camera=bpy.data.objects['R2_south']
    def project(pixels,z):return [source_to_plane(scene,camera,p,(5000,3333),z)for p in pixels]
    for pixels in LINKS:
        roof=project(pixels,26.2);group='South source rail links'
        batch.add(group,'aluminum',roof,[(0,1,2,3)])
        batch.prism(group,'concrete',[p[:2]for p in roof],21.6,22)
        for a,b in zip(roof,roof[1:]+roof[:1]):
            batch.quad(group,'glass',[(a[0],a[1],22.1),(b[0],b[1],22.1),b,a])
            batch.line(group,'white',[(a[0],a[1],26.1),(b[0],b[1],26.1)],.16,sides=6)
            batch.line(group,'white',[(a[0],a[1],22.2),(b[0],b[1],22.2)],.14,sides=6)
            count=max(1,round((Vector(b)-Vector(a)).length/2.5))
            for i in range(count+1):
                p=Vector(a).lerp(Vector(b),i/count)
                batch.cylinder(group,'aluminum',(p.x,p.y,22),p,.13,sides=6)
        # Steel lift/stair landing towers visible at the west ends.
        p=(Vector(roof[0])+Vector(roof[-1]))/2
        for dx in [-2,2]:
            for dy in [-2,2]:batch.cylinder(group,'metal',(p.x+dx,p.y+dy,8),(p.x+dx,p.y+dy,26.2),.12,sides=6)
        for z in [9,14,19,24]:
            batch.line(group,'metal',[(p.x-2,p.y-2,z),(p.x+2,p.y-2,z+4)],.075,sides=6)
    group='South source landing buildings'
    def building(pixels,z):
        foot=[p[:2]for p in project(pixels,z)]
        _facade(batch,group,foot,8,z,3.4,window_material='glass_dim',window_fraction=.55,level_height=3.7)
        _roof_and_parapet(batch,group,foot,z,'roof',.5)
    building([(910,2040),(1070,2010),(1135,2130),(970,2165)],29)
    outer=project([(800,2380),(1250,2300),(1360,2490),(870,2580)],31)
    inner=project([(900,2400),(1180,2360),(1235,2460),(950,2515)],31)
    for i in range(4):
        foot=[outer[i][:2],outer[(i+1)%4][:2],inner[(i+1)%4][:2],inner[i][:2]]
        _facade(batch,group,foot,8,31,3.5,window_material='glass_dim',window_fraction=.52,level_height=3.8,mass_material='stone')
        _roof_and_parapet(batch,group,foot,31,'roof',.5)
    building([(900,2620),(1270,2550),(1300,2590),(920,2670)],28.5)
    building([(1290,2650),(1430,2610),(1460,2670),(1310,2700)],24.5)
    # The narrow proposed public crossing is distinct from the railway
    # bascules farther south. Its engineering and approach grade are inferred.
    group='Future development';x0,x1,y=72,218,-154
    batch.box(group,'stone',((128+192)/2,y,13.65),(64,4.8,.7))
    for a,b,z0,z1 in [(x0,128,8.5,14),(192,x1,14,8.5)]:
        batch.quad(group,'paving',[(a,y-2.4,z0),(b,y-2.4,z1),(b,y+2.4,z1),(a,y+2.4,z0)])
    for side in [-1,1]:
        batch.line(group,'metal',[(x0,y+side*2.3,9.7),(128,y+side*2.3,15.2),(192,y+side*2.3,15.2),(x1,y+side*2.3,9.7)],.055,sides=6)
        for x in range(128,193,3):batch.cylinder(group,'metal',(x,y+side*2.3,14),(x,y+side*2.3,15.2),.035,sides=6)
    # B6 resolves a large end-face medical sign and a roof monogram.
    medical=[p[:2]for p in [source_to_plane(scene,bpy.data.objects['R2_north'],q,(1944,1294),ROOF_Z)for q in ROOF_PIXELS]]
    center=sum((Vector((*p,0))for p in medical),Vector())/len(medical)
    ends=sorted(range(len(medical)),key=lambda i:_edge(medical,i)[4])[:2]
    index=max(ends,key=lambda i:_edge(medical,i)[3].dot(camera.location-center))
    a,b,t,outward,length,angle=_edge(medical,index);p=(a+b)/2+outward*.4;p.z=ROOF_Z-7
    facing=math.atan2(outward.x,-outward.y);collection=batch.collection('South source medical branding')
    batch.box('South source medical branding','stone',p,(length*.98,.15,6),angle)
    text(scene,collection,'South medical end sign','Northwestern\nMedicine',p+outward*.12,2.4,materials['purple_sign'],(math.pi/2,0,facing))
    center.z=ROOF_Z+1.12
    text(scene,collection,'Medical rooftop monogram','M',center,18,materials['purple_sign'],(0,0,angle))
    scene['south_rail_variant_note']='Three B6-covered roof traces conflict with north-derived crossings under the shared camera calibration. Separate source-view link collections preserve both readings; no surveyed common alignment is claimed. B6 landing blocks are source-traced; hidden heights/depth remain inferred.'
