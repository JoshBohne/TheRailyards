"""Source-projected north public deck, riverfront retail and stadium approach.

The deck meets the Roosevelt sidewalk datum and rises gently toward the broad
outfield entry. Its grade is a reconstruction hypothesis, checked in the north
and bridge views, not a published engineering dimension.
"""
import bpy,math,random,json
from pathlib import Path
from mathutils import Vector
from r2_geometry import instances
from r2_seating import prototype
from r3_reference_projection import source_to_grade

GROUP='Public realm'
_SPEC=json.loads((Path(__file__).parent/'public-realm-spec.json').read_text())
_PARAMETERS=_SPEC['parameters']
ROAD_Y=_PARAMETERS['ROAD_Y'];ROAD_Z=_PARAMETERS['ROAD_Z'];GRADE=_PARAMETERS['GRADE'];LOWER_Z=_PARAMETERS['LOWER_Z']
SOURCE_SIZE=tuple(_SPEC['source_size_px'])
ROOF_PIXELS=_PARAMETERS['ROOF_PIXELS'];LAWN_PIXELS=_PARAMETERS['LAWN_PIXELS'];RETAIL_EDGE=_PARAMETERS['RETAIL_EDGE']


def deck_z(y):return ROAD_Z+GRADE*(ROAD_Y-y)

def quay_z(y):
    # Inferred continuous lower walk joining the stadium arcade and park quay.
    return LOWER_Z+(8.0-LOWER_Z)*max(0.0,min(1.0,(170.0-y)/250.0))

def inside(point,polygon):
    x,y=point;value=False
    for a,b in zip(polygon,polygon[1:]+polygon[:1]):
        if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:value=not value
    return value

def _slab(batch,material,polygon,top,bottom):
    points=list(polygon)
    if sum(a[0]*b[1]-b[0]*a[1]for a,b in zip(points,points[1:]+points[:1]))<0:points.reverse()
    n=len(points);verts=[(x,y,bottom(y))for x,y in points]+[(x,y,top(y))for x,y in points]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)]
    batch.add(GROUP,material,verts,faces)

def _path(batch,a,b,width,zoffset=.08):
    a,b=Vector(a),Vector(b);d=b-a
    if d.length<.01:return
    n=Vector((-d.y,d.x)).normalized()*width/2
    poly=[a-n,b-n,b+n,a+n]
    _slab(batch,'stone',poly,lambda y:deck_z(y)+zoffset,lambda y:deck_z(y)+zoffset-.10)

def _table(batch,x,y,z,scale=1):
    batch.cylinder(GROUP,'metal',(x,y,z),(x,y,z+.75),.045,sides=6)
    batch.cylinder(GROUP,'white',(x,y,z+.75),(x,y,z+.81),.53*scale,sides=12)
    for a in [0,math.pi/2,math.pi,3*math.pi/2]:
        cx,cy=x+.85*math.cos(a),y+.85*math.sin(a)
        batch.box(GROUP,'seat',(cx,cy,z+.44),(.38,.38,.08),a)
        batch.box(GROUP,'metal',(cx,cy,z+.20),(.06,.06,.40))

def build_public_realm(scene,spec,batch,materials):
    rng=random.Random(6026);camera=bpy.data.objects['R2_north']
    def project(p):return source_to_grade(scene,camera,p,SOURCE_SIZE,ROAD_Y,ROAD_Z,GRADE)[:2]
    roof=[project(p)for p in ROOF_PIXELS]
    lawns=[[project(p)for p in polygon]for polygon in LAWN_PIXELS]
    edge=[project(p)for p in RETAIL_EDGE]
    # Cut only the immediate riverfront down to the lower quay level. The
    # stadium and street lands retain their former support slab elsewhere.
    for poly in [[(-94,-1200),(6,-1200),(6,1800),(-94,1800)],
                 [(6,-1200),(124,-1200),(124,-135),(6,-135)],
                 [(6,310),(124,310),(124,1800),(6,1800)]]:
        batch.prism(GROUP,'paving',poly,-2,8)
    batch.prism(GROUP,'paving',[(6,-135),(124,-135),(124,310),(6,310)],-2,LOWER_Z-.12)
    for ya,yb in [(-135,-80),(-80,170)]:
        _slab(batch,'paving',[(112,ya),(124,ya),(124,yb),(112,yb)],quay_z,lambda y:LOWER_Z-.1)
    for y in range(-120,170,18):
        _table(batch,115,y,quay_z(y)+.03)
        batch.line(GROUP,'metal',[(125,y,quay_z(y)+1.05),(125,y+18,quay_z(y+18)+1.05)],.04)
        for yy in range(y,y+18,3):batch.cylinder(GROUP,'metal',(125,yy,quay_z(yy)),(125,yy,quay_z(yy)+1.05),.035,sides=6)
    _slab(batch,'concrete',roof,deck_z,lambda y:deck_z(y)-.55)
    _slab(batch,'stone',roof,lambda y:deck_z(y)+.055,deck_z)
    for lawn in lawns:_slab(batch,'lawn',lawn,lambda y:deck_z(y)+.12,lambda y:deck_z(y)+.05)
    # Short transverse paths and the long hall-side walk divide the event lawn.
    for a,b in [((969,731),(907,789)),((1110,795),(1045,866)),
                ((1310,882),(1240,970)),((1510,970),(1443,1058)),
                ((974,730),(1595,1005))]:
        _path(batch,project(a),project(b),1.45,.16)
    # Broad entry landing toward the bowl, structurally supported and continuous
    # with the rising park deck. Its top remains above the modeled bleacher rows.
    entrance=[project(p)for p in [(695,736),(808,668),(1050,689),(810,790)]]
    _slab(batch,'stone',entrance,deck_z,lambda y:deck_z(y)-.60)
    for a,b in zip(entrance,entrance[1:]+entrance[:1]):
        center=(Vector(a)+Vector(b))/2
        batch.box(GROUP,'concrete',(center.x,center.y,(8+deck_z(center.y))/2),(.6,.8,deck_z(center.y)-8))
    # Continuous tall shopfronts beneath the roof's source-visible bent edge.
    for segment,(a,b) in enumerate(zip(edge,edge[1:])):
        a,b=Vector(a),Vector(b);t=(b-a).normalized();n=Vector((t.y,-t.x));length=(b-a).length
        # Face the river (+X); this also keeps storefront glazing outside mass.
        if n.x<0:n=-n
        count=max(2,round(length/6.0));bay=length/count;angle=math.atan2(t.y,t.x)
        for i in range(count):
            c=a.lerp(b,(i+.5)/count);height=deck_z(c.y)-LOWER_Z-.5
            depth=5.2;mass=c-n*depth/2
            batch.box('Riverfront retail','brick_dark',(mass.x,mass.y,LOWER_Z+height/2),(bay,depth,height),angle)
            glass=c+n*.08
            batch.box('Riverfront retail','glass_lit',(glass.x,glass.y,LOWER_Z+height*.49),(bay-.65,.14,height*.81),angle)
            for u in [-bay/2+.18,bay/2-.18]:
                q=c+t*u+n*.17
                batch.box('Riverfront retail','stone',(q.x,q.y,LOWER_Z+height/2),(.30,.32,height),angle)
            for f in [.33,.65]:
                q=c+n*.17
                batch.box('Riverfront retail','metal',(q.x,q.y,LOWER_Z+height*f),(bay,.25,.12),angle)
            q=c+n*.22
            batch.box('Riverfront retail','stone',(q.x,q.y,deck_z(c.y)-.35),(bay+.1,.55,.35),angle)
            # A projecting striped awning and a lower café table activate the quay.
            q=c+n*1.3
            batch.box('Riverfront retail','roof',(q.x,q.y,LOWER_Z+3.1),(bay*.72,2.0,.15),angle)
            if i%2==0:
                q=c+n*3.4;_table(batch,q.x,q.y,LOWER_Z+.03)
    # Small shaded shelters are above the park, separate from the lower shops.
    for pixel in [(1120,743),(1183,779),(1470,926)]:
        x,y=project(pixel);z=deck_z(y)+.15
        for dx in [-2.8,2.8]:
            for dy in [-2,2]:batch.box(GROUP,'metal',(x+dx,y+dy,z+1.6),(.14,.14,3.2))
        batch.box(GROUP,'roof',(x,y,z+3.25),(6.3,4.7,.30))
        _table(batch,x,y,z)
    # A round sculpture plinth is clearly visible at the Roosevelt lawn corner.
    x,y=project((1481,1098));z=deck_z(y)+.15
    batch.cylinder(GROUP,'stone',(x,y,z),(x,y,z+.26),2.1,sides=32)
    batch.cylinder(GROUP,'metal',(x,y,z+.26),(x,y,z+3.1),.28,.12,sides=8)
    # Broad stair descent from the corner roof to the lower waterside promenade.
    a,b=[Vector(project(p))for p in [(1392,1190),(1480,1235)]]
    t=(b-a).normalized();n=Vector((-t.y,t.x));mid=(a+b)/2
    if n.x<0:n=-n
    count=24;run=14.0;top=deck_z(mid.y)
    for i in range(count):
        c=mid+n*(i+.5)*run/count;z=top-(top-LOWER_Z)*(i+1)/count
        batch.box(GROUP,'stone',(c.x,c.y,z-.12),((b-a).length,run/count,.24),math.atan2(t.y,t.x))
    # Native linked trees use the detailed branching prototypes built earlier.
    tree=bpy.data.objects.get('D2_Broadleaf tree 0')
    if tree:
        locations=[];rotations=[];scales=[]
        for p in [(953,757),(1010,850),(1130,805),(1200,858),(1360,950),(1455,1000),(1540,995)]:
            x,y=project(p);locations.append((x,y,deck_z(y)+.15));rotations.append((0,0,rng.random()*math.tau));scales.append((.82,.82,.88))
        for y in range(-110,300,13):
            locations.append((120,y,quay_z(y)));rotations.append((0,0,rng.random()*math.tau));scales.append((.75,.75,.80))
        instances(scene,batch.collection(GROUP),'North park and quay trees',tree,locations,rotations,scales)
    # Grounded tables occupy actual lawn polygons rather than arbitrary XY rows.
    for lawn in lawns[:1]:
        xmin=min(p[0]for p in lawn);xmax=max(p[0]for p in lawn);ymin=min(p[1]for p in lawn);ymax=max(p[1]for p in lawn)
        for i in range(180):
            x,y=rng.uniform(xmin,xmax),rng.uniform(ymin,ymax)
            if inside((x,y),lawn) and i%3==0:_table(batch,x,y,deck_z(y)+.16)
    walker=bpy.data.objects.get('D2_Walking visitor')
    if walker:
        positions=[];rotations=[];scales=[]
        xmin=min(p[0]for p in roof);xmax=max(p[0]for p in roof);ymin=min(p[1]for p in roof);ymax=max(p[1]for p in roof)
        for i in range(1500):
            x,y=rng.uniform(xmin,xmax),rng.uniform(ymin,ymax)
            if not inside((x,y),roof):continue
            positions.append((x,y,deck_z(y)+.17));rotations.append((0,0,rng.random()*math.tau));scales.append((1,1,1))
        for i in range(650):
            x,y=rng.uniform(104,123),rng.uniform(165,302)
            if inside((x,y),roof):continue
            positions.append((x,y,LOWER_Z));rotations.append((0,0,rng.random()*math.tau));scales.append((1,1,1))
        for i in range(420):
            x,y=rng.uniform(116,123),rng.uniform(-125,166)
            positions.append((x,y,quay_z(y)+.04));rotations.append((0,0,rng.random()*math.tau));scales.append((1,1,1))
        instances(scene,batch.collection(GROUP),'Public deck visitors',walker,positions,rotations,scales)
    scene['public_deck_grade']='Inferred z=14.1+0.045*(300-y), meeting Roosevelt sidewalk and rising toward the outfield entry; verify in both north and bridge source views.'
    scene['public_realm_roof_xy']=str(roof)
