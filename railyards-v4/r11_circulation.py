"""V11 source-led plaza/terrace continuity and riverfront circulation.

Applied to preserved V9 by build_circulation_v11.py. Existing calibrated XY
traces stay fixed. Grades, stair dimensions, unseen connections and structure
are inferred; the north and bridge artwork establish the spatial relationships.
"""
import math
import bpy
from mathutils import Vector
from r2_geometry import text
from r3_public_realm import deck_z, quay_z, LOWER_Z, inside


ARRIVAL_XY=[(50,294),(48,220),(52,185),(66.9,161.8),(66.9,136)]


def clear_arrival(x,y):
    p=Vector((x,y))
    for aa,bb in zip(ARRIVAL_XY,ARRIVAL_XY[1:]):
        a,b=Vector(aa),Vector(bb);d=b-a;u=max(0,min(1,(p-a).dot(d)/d.length_squared))
        if (p-a-d*u).length<5.0:return True
    return False


def terrace_z(y):
    # One planar grade preserves the source-projected plaza/roof continuity.
    return deck_z(y) + .055


def slab(batch, group, material, polygon, top, bottom):
    n=len(polygon)
    vertices=[(x,y,bottom(y)) for x,y in polygon]+[(x,y,top(y)) for x,y in polygon]
    batch.add(group,material,vertices,[tuple(reversed(range(n))),tuple(range(n,2*n))]+
              [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)])


def rail(batch, group, a, b, height=1.1):
    a,b=Vector(a),Vector(b);count=max(1,math.ceil((b-a).length/2.0))
    for i in range(count+1):
        p=a.lerp(b,i/count)
        batch.cylinder(group,'metal',p,p+Vector((0,0,height)),.035,sides=6)
    for z in (.42,height):
        batch.cylinder(group,'metal',a+Vector((0,0,z)),b+Vector((0,0,z)),.04,sides=6)


def build_quay(batch):
    group='Public realm'
    # Carve the north frontage down to the lower walk; the former z8 land mass
    # buried the lower shop windows and made the arcade read as another wall.
    polygons=[ [(-94,-1200),(6,-1200),(6,1800),(-94,1800)],
               [(6,-1200),(124,-1200),(124,-135),(6,-135)],
               [(6,310),(124,310),(124,1800),(6,1800)],
               [(6,-135),(124,-135),(124,-79),(6,-79)],
               [(6,-79),(100,-79),(100,170),(6,170)],
               [(6,170),(80,170),(80,310),(6,310)] ]
    for poly in polygons:batch.prism(group,'paving',poly,-2,8)
    batch.prism(group,'paving',[(100,-79),(124,-79),(124,170),(100,170)],-2,LOWER_Z-1.3)
    batch.prism(group,'paving',[(80,170),(124,170),(124,310),(80,310)],-2,LOWER_Z-1.3)
    for ya,yb,x0 in [(-135,-79,112),(-79,170,100),(170,310,80)]:
        slab(batch,'V11 Riverwalk','paving',[(x0,ya),(118,ya),(118,yb),(x0,yb)],quay_z,lambda y:LOWER_Z-1.3)
        for step in range(3):
            left=118+2*step;drop=.35*(step+1)
            slab(batch,'V11 Riverwalk steps','stone',[(left,ya),(left+2,ya),(left+2,yb),(left,yb)],
                 lambda y,d=drop:quay_z(y)-d,lambda y:LOWER_Z-1.3)
    # Planting interrupts long seating steps without blocking the continuous
    # upper promenade. Short stair-sized gaps remain between the planted bays.
    for y in range(-65,290,22):
        batch.box('V11 Riverwalk planting','brick_dark',(119,y,quay_z(y)-.04),(1.6,12,.62))
        batch.box('V11 Riverwalk planting','lawn',(119,y,quay_z(y)+.30),(1.44,11.8,.12))
        for k in range(6):
            batch.box('V11 Riverwalk benches','wood' if 'wood' in batch.materials else 'bark',
                      (117.4,y-4.8+k*.12,quay_z(y)+.48),(.52,.065,.07))
        rail(batch,'V11 River edge',(124,y-6,quay_z(y)-1.05),(124,y+6,quay_z(y)-1.05),.95)


def build_arcade(scene,batch,materials,edge):
    group='V11 Riverfront arcade'
    for segment,(aa,bb) in enumerate(zip(edge,edge[1:])):
        a,b=Vector(aa),Vector(bb);t=(b-a).normalized();n=Vector((t.y,-t.x))
        if n.x<0:n=-n
        length=(b-a).length;count=max(2,round(length/7.4));bay=length/count
        for i in range(count):
            c=a.lerp(b,(i+.5)/count);angle=math.atan2(t.y,t.x)
            floor=LOWER_Z+.07;top=deck_z(c.y)-.55
            width=bay*.76;radius=width/2;height=min(7.2,top-floor-.9);spring=floor+height-radius
            def p(u,z,d=0):
                q=c+t*u+n*d;return(q.x,q.y,z)
            # Genuine recessed bays: piers and arch spandrels, no full wall
            # covering the aperture. Shop glazing and room fittings sit inside.
            for sign in (-1,1):
                batch.box(group,'brick',p(sign*(bay+width)/4,(floor+top)/2,-.4),
                          ((bay-width)/2,.85,top-floor),angle)
            for k in range(20):
                x0=-radius+width*k/20;x1=-radius+width*(k+1)/20
                z0=spring+math.sqrt(max(0,radius*radius-x0*x0))
                z1=spring+math.sqrt(max(0,radius*radius-x1*x1))
                front=[p(x0,z0,.03),p(x1,z1,.03),p(x1,top,.03),p(x0,top,.03)]
                back=[p(x0,z0,-.85),p(x1,z1,-.85),p(x1,top,-.85),p(x0,top,-.85)]
                batch.add(group,'brick',front+back,[(0,1,2,3),(7,6,5,4),(0,4,5,1)])
            # Radial brick voussoirs give the opening depth in native and GLB.
            for k in range(20):
                a0=math.pi*k/20;a1=math.pi*(k+1)/20
                pts=[p(r*math.cos(a),spring+r*math.sin(a),.12)
                     for r,a in [(radius,a0),(radius+.26,a0),(radius+.26,a1),(radius,a1)]]
                batch.add(group,'brick_light' if k%3 else 'brick_dark',pts,[(0,1,2,3)])
            batch.box(group,'interior',p(0,(floor+top)/2,-4),(bay-.3,.25,top-floor),angle)
            batch.box(group,'stone',p(0,floor-.08,-2),(bay,4,.16),angle)
            batch.box(group,'roof',p(0,top-.08,-2),(bay,4,.16),angle)
            # Inset transomed storefront; cool glazing above the warm interior.
            batch.box(group,'glass_mid',p(0,floor+height*.48,-1.25),(width-.12,.08,height*.93),angle)
            for u in (-width*.24,0,width*.24):
                batch.cylinder(group,'metal',p(u,floor,-1.12),p(u,floor+height*.83,-1.12),.045,sides=6)
            batch.cylinder(group,'metal',p(-radius,floor+2.6,-1.12),p(radius,floor+2.6,-1.12),.05,sides=6)
            batch.box(group,'lamp',p(0,floor+3.1,-1.06),(width*.32,.07,.1),angle)
            batch.box(group,'stone',p(0,top+.14,.10),(bay+.10,.48,.28),angle)
            # Parapet belongs at the exposed edge, not across the public entry.
            batch.box(group,'brick_dark',p(0,deck_z(c.y)+.38,-.05),(bay+.08,.45,.75),angle)
            batch.box(group,'stone',p(0,deck_z(c.y)+.78,-.05),(bay+.13,.57,.13),angle)
    # Screen on the inset return, facing the lower café square, as in the north
    # source. The lettering is illustrative rather than an advertisement.
    a,b=Vector(edge[1]),Vector(edge[2]);t=(b-a).normalized();n=Vector((t.y,-t.x))
    if n.y<0:n=-n
    c=a.lerp(b,.48);angle=math.atan2(t.y,t.x);z=deck_z(c.y)-3.35
    batch.box('V11 Riverfront screen','metal',(c.x+n.x*.55,c.y+n.y*.55,z),(17,.4,5.1),angle)
    batch.box('V11 Riverfront screen','screen',(c.x+n.x*.79,c.y+n.y*.79,z),(16.5,.05,4.65),angle)
    # Text local -Y faces the chosen normal.
    text(scene,batch.collection('V11 Riverfront screen'),'Riverfront welcome','THE RAILYARDS',
         (c.x+n.x*.84,c.y+n.y*.84,z-.25),1.05,materials['screen_ink'],(math.pi/2,0,angle))


def stairs(batch,group,start,end,width,landings=2):
    a,b=Vector(start),Vector(end);flat=Vector((b.x-a.x,b.y-a.y,0));length=flat.length;t=flat.normalized();n=Vector((-t.y,t.x,0))
    rise=a.z-b.z;count=max(2,math.ceil(rise/.17));landing_length=1.5
    tread=(length-landings*landing_length)/count
    if tread<.25:raise ValueError(f'{group}: stair run too short ({tread:.3f} m tread)')
    cursor=0;railpoints=[a.copy()];breaks={round(count*(k+1)/(landings+1)) for k in range(landings)}
    for i in range(count):
        z=a.z-rise*(i+1)/count
        p=a+t*(cursor+tread/2);p.z=z-.12
        batch.box(group,'stone',p,(tread,width,.24),math.atan2(t.y,t.x))
        cursor+=tread;railpoints.append(Vector((a.x+t.x*cursor,a.y+t.y*cursor,z)))
        if i+1 in breaks:
            p=a+t*(cursor+landing_length/2);p.z=z-.14
            batch.box(group,'concrete',p,(landing_length,width,.28),math.atan2(t.y,t.x))
            cursor+=landing_length;railpoints.append(Vector((a.x+t.x*cursor,a.y+t.y*cursor,z)))
    for side in (-1,1):
        shifted=[p+n*(side*width/2) for p in railpoints]
        for p,q in zip(shifted,shifted[1:]):
            batch.cylinder(group,'metal',p+Vector((0,0,1.05)),q+Vector((0,0,1.05)),.045,sides=6)
        for i in range(0,len(shifted),7):
            p=shifted[i];batch.cylinder(group,'metal',p,p+Vector((0,0,1.05)),.035,sides=6)
    # A structural inclined slab, with supports clear of the walking line.
    corners=[a+n*width/2,a-n*width/2,b-n*width/2,b+n*width/2]
    batch.add(group,'concrete',[tuple(p-Vector((0,0,.85))) for p in corners]+[tuple(p-Vector((0,0,1.15))) for p in corners],
              [(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)])
    for u in (.15,.5,.85):
        p=a.lerp(b,u)
        for side in (-1,1):
            q=p+n*(side*(width/2-.4));bottom=quay_z(q.y)
            if q.z-bottom>.7:batch.box(group,'brick_dark',(q.x,q.y,(q.z+bottom)/2-.3),(.45,.45,q.z-bottom-.3))


def build_corner_stair(batch,edge):
    top=deck_z(298)+.055
    batch.box('V11 Corner stair','stone',(92,298,top-.16),(8,11,.32))
    stairs(batch,'V11 Corner stair',(96,298,top),(119,298,LOWER_Z),11)
    batch.box('V11 Corner stair','stone',(120.5,298,LOWER_Z-.12),(3,11,.24))


def regrade_restaurant(scene,batch,roof,entrance,front_terrace):
    collection=bpy.data.collections['D2_Centerfield restaurant replacement']
    for obj in list(collection.objects):
        if obj.type!='MESH':continue
        if any(obj.name.endswith(' '+suffix) for suffix in ['metal','stone','paving']):
            bpy.data.objects.remove(obj,do_unlink=True);continue
        points_only=not len(obj.data.polygons)
        for v in obj.data.vertices:
            y=v.co.y;target=terrace_z(y)
            if points_only:v.co.z+=target-22.4
            elif obj.name.endswith(' roof'):v.co.z=target-.28+(v.co.z-22.0)
            elif obj.name.endswith(' paving'):v.co.z=target+(v.co.z-22.38)
            else:
                base=quay_z(y)
                v.co.z=base+(v.co.z-8.0)*(target-.30-base)/14.0
    obsolete=bpy.data.collections.get('D2_Centerfield terrace connection')
    if obsolete:
        for obj in list(obsolete.objects):bpy.data.objects.remove(obj,do_unlink=True)
    for name in ['D2_Centerfield terrace dining','D2_Centerfield board canopy','D2_Centerfield curved terrace bench']:
        col=bpy.data.collections.get(name)
        if not col:continue
        for obj in col.objects:
            if obj.type=='MESH':
                for v in obj.data.vertices:v.co.z+=terrace_z(v.co.y)-22.38
    # Reuse the exact V9 XY perimeter, with a roof surface that reaches the
    # public deck. The legacy inset terrace left a gap at the entry.
    for aa,bb in zip(roof,roof[1:]+roof[:1]):
        a,b=Vector(aa),Vector(bb);count=max(1,math.ceil((b-a).length/2))
        t=(b-a).normalized();angle=math.atan2(t.y,t.x)
        for i in range(count):
            p=a.lerp(b,i/count);q=a.lerp(b,(i+1)/count);c=(p+q)/2
            # Coping stays below the walking surface, including at the join.
            batch.box('V11 Terrace cornice','stone',(c.x,c.y,terrace_z(c.y)-.24),((q-p).length+.02,.32,.25),angle)
            if inside(tuple(c),entrance) or inside(tuple(c),front_terrace) or (c.y>154 and 40<c.x<108):continue
            # Keep access openings for the two inferred outfield-bank links.
            if 102<c.x<116 and c.y<110:continue
            if c.x<56 and 127<c.y<146:continue
            rail(batch,'V11 Terrace railing',(p.x,p.y,terrace_z(p.y)),(q.x,q.y,terrace_z(q.y)))
    # Decongest the entry; the existing crowd point is retained elsewhere.
    obj=bpy.data.objects.get('D2_Centerfield terrace visitors')
    if obj:
        scales=obj.data.attributes.get('scale')
        for i,v in enumerate(obj.data.vertices):
            if clear_arrival(v.co.x,v.co.y):scales.data[i].vector=(0,0,0)


def connect_outfield(batch,front_terrace):
    # Preserve V9's source-traced broad left-center plaza. It shares the same
    # plane with the restaurant roof; narrow bridges are only needed at RF.
    polygons=[front_terrace]
    a,b=Vector(front_terrace[0]),Vector(front_terrace[1])
    count=max(1,math.ceil((b-a).length/1.5))
    for i in range(count):
        p,q=a.lerp(b,i/count),a.lerp(b,(i+1)/count);c=(p+q)/2
        if (c-Vector((50,121.7))).length<3.0:continue
        rail(batch,'V11 LF field edge',(p.x,p.y,terrace_z(p.y)),(q.x,q.y,terrace_z(q.y)))
    # The broad plaza has understructure down to the retained z8 site datum.
    # Keep its front undercroft open rather than adding another blank wall.
    normal=Vector(((b-a).y,-(b-a).x)).normalized()
    for i in range(7):
        p=a.lerp(b,i/6)+normal*1.2;z=terrace_z(p.y)
        batch.box('V11 Plaza supports','brick_dark',(p.x,p.y,(8+z-.5)/2),(.8,.8,z-.5-8))
    beam_a=a+normal*1.2;beam_b=b+normal*1.2
    slab(batch,'V11 Plaza supports','concrete',[tuple(beam_a-normal*.5),tuple(beam_b-normal*.5),tuple(beam_b+normal*.5),tuple(beam_a+normal*.5)],lambda y:terrace_z(y)-.5,lambda y:terrace_z(y)-1.0)
    path=[(110,89),(83,117),(53,135)]
    for aa,bb in zip(path,path[1:]):
        a,b=Vector(aa),Vector(bb);t=(b-a).normalized();n=Vector((-t.y,t.x))*2.8
        poly=[tuple(a+n),tuple(a-n),tuple(b-n),tuple(b+n)]
        polygons.append(poly)
        p,q=a+n,b+n
        count=max(1,math.ceil((q-p).length/2))
        for i in range(count):
            r,s=p.lerp(q,i/count),p.lerp(q,(i+1)/count)
            if not inside(tuple((r+s)/2),front_terrace):rail(batch,'V11 Outfield upper concourse',(r.x,r.y,terrace_z(r.y)),(s.x,s.y,terrace_z(s.y)))
        for u in (.15,.65):
            p=a.lerp(b,u);z=terrace_z(p.y)
            batch.box('V11 Concourse supports','brick_dark',(p.x,p.y,(13.4+z)/2),(.55,.65,z-13.4))
    stairs(batch,'V11 LF concourse stair',(50,121.7,terrace_z(121.7)),(28,116.8,13.4),4.2,1)
    stairs(batch,'V11 RF concourse stair',(110,89,terrace_z(89)),(112,65,13.4),4.2,1)
    c=Vector(front_terrace[0]).lerp(Vector(front_terrace[2]),.54);z=terrace_z(c.y)
    for dx in (-3,3):
        for dy in (-2,2):batch.box('V11 LF pergola','metal',(c.x+dx,c.y+dy,z+1.5),(.14,.14,3))
    for i in range(15):batch.box('V11 LF pergola','metal',(c.x-3+i*6/14,c.y,z+3.05),(.16,4.5,.16))
    return polygons


def open_lower_landings(scene,batch,spec):
    """Replace the old ring guardrail with explicit openings at the new stairs."""
    import bmesh
    for suffix,lo,hi in [('metal',13.3,14.8),('stone',13.3,13.7)]:
        obj=bpy.data.objects.get('D2_RF structure '+suffix)
        if not obj:continue
        mesh=bmesh.new();mesh.from_mesh(obj.data);seen=set();remove=[]
        for vertex in mesh.verts:
            if vertex in seen:continue
            stack=[vertex];component=[];seen.add(vertex)
            while stack:
                v=stack.pop();component.append(v)
                for edge in v.link_edges:
                    other=edge.other_vert(v)
                    if other not in seen:seen.add(other);stack.append(other)
            if all(lo<=v.co.z<=hi for v in component):remove.extend(component)
        bmesh.ops.delete(mesh,geom=remove,context='VERTS');mesh.to_mesh(obj.data);mesh.free()
    field=[Vector(p[:2]) for p in spec['field_boundary']]
    outer=[Vector(spec['bowl_front'][0][:2])]+[p+p.normalized()*10 for p in field]+[Vector(spec['bowl_front'][-1][:2])]
    portals=[Vector((28,115)),Vector((110,65))]
    for a,b in zip(outer,outer[1:]):
        count=max(1,math.ceil((b-a).length/1.7))
        for i in range(count):
            p,q=a.lerp(b,i/count),a.lerp(b,(i+1)/count);c=(p+q)/2
            if any((c-portal).length<3.2 for portal in portals):continue
            rail(batch,'V11 Lower concourse guardrail',(p.x,p.y,13.4),(q.x,q.y,13.4))
    batch.box('V11 Lower concourse landings','stone',(28,115,13.25),(8,7,.30))
    batch.box('V11 Lower concourse landings','stone',(110.5,65,13.25),(6.5,6,.30))


def build_terrace_surface(batch,polygons):
    """Triangulate the union, so overlapping source traces cannot z-fight."""
    from mathutils.geometry import delaunay_2d_cdt
    from collections import Counter
    points=[];edges=[]
    for poly in polygons:
        start=len(points);points.extend(Vector(p) for p in poly)
        edges.extend((start+i,start+(i+1)%len(poly)) for i in range(len(poly)))
    vertices,_,faces,*_=delaunay_2d_cdt(points,edges,[],0,.0001)
    selected=[]
    for face in faces:
        center=sum((vertices[i] for i in face),Vector((0,0)))/len(face)
        if any(inside(tuple(center),poly) for poly in polygons):selected.append(tuple(face))
    top=[(p.x,p.y,terrace_z(p.y)) for p in vertices]
    bottom=[(p.x,p.y,terrace_z(p.y)-.5) for p in vertices]
    batch.add('V11 Continuous terrace','paving',top,selected)
    batch.add('V11 Continuous terrace','concrete',bottom,[tuple(reversed(face)) for face in selected])
    counts=Counter(tuple(sorted((a,b))) for face in selected for a,b in zip(face,face[1:]+face[:1]))
    for (a,b),count in counts.items():
        if count==1:batch.quad('V11 Continuous terrace','stone',[bottom[a],bottom[b],top[b],top[a]])
