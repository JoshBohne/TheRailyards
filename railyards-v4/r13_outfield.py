"""Outfield seating returns and a genuine park-to-bleachers entrance.

V13 is applied to the preserved V12 static scene. The source artwork establishes
stacked curved seating, an open park arcade and the pavilion behind the seats.
Curves, rows, structure and passage dimensions are reconstruction assumptions.
"""
import math
import random

import bpy
import bmesh
from mathutils import Vector

from r2_geometry import instances
from r11_circulation import rail, stairs
from r12_outfield import footprint, _clear_of_field

TIERS = [(0, .34, 14, 24, 24), (.40, .49, 27, 30, 8),
         (.55, .65, 33, 36, 9), (.70, .93, 39, 47, 18)]
PASSAGE_X = (48.0, 54.0)
PASSAGE_FLOOR = 15.38
PASSAGE_CEILING = 18.90


def remove_collection(name):
    collection = bpy.data.collections.get(name)
    if collection:
        for obj in list(collection.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(collection)


def remove_components(obj, predicate):
    """Remove complete primitives from a material-batched mesh."""
    mesh = bmesh.new()
    mesh.from_mesh(obj.data)
    seen = set()
    removed = []
    for vertex in mesh.verts:
        if vertex in seen:
            continue
        component = []
        stack = [vertex]
        seen.add(vertex)
        while stack:
            current = stack.pop()
            component.append(current)
            for edge in current.link_edges:
                other = edge.other_vert(current)
                if other not in seen:
                    seen.add(other)
                    stack.append(other)
        if predicate([v.co for v in component]):
            removed.extend(component)
    bmesh.ops.delete(mesh, geom=removed, context='VERTS')
    mesh.to_mesh(obj.data)
    mesh.free()


def cut_box(scene, objects, low, high, name):
    """Cut real architectural voids, including their soffits and reveals."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=tuple((a+b)/2 for a,b in zip(low,high)))
    cutter = bpy.context.object
    cutter.name = name
    cutter.dimensions = tuple(b-a for a,b in zip(low,high))
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for obj in objects:
        if obj.type != 'MESH' or not obj.data.polygons:
            continue
        modifier = obj.modifiers.new(name, 'BOOLEAN')
        modifier.operation = 'DIFFERENCE'
        modifier.solver = 'EXACT'
        modifier.object = cutter
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def trim_pavilion(scene):
    # Preserve the source-visible rear club. Its former solid field-side bays
    # occupy the missing grandstand. Recess those bays, including their cap.
    names = ['D2_Left field pavilion', 'D2_Left field pavilion glazing frames',
             'D2_Left field terrace dining']
    for name in names:
        collection = bpy.data.collections.get(name)
        if not collection:
            continue
        for obj in collection.objects:
            if obj.type != 'MESH':
                continue
            mesh = bmesh.new()
            mesh.from_mesh(obj.data)
            bmesh.ops.bisect_plane(mesh, geom=list(mesh.verts)+list(mesh.edges)+list(mesh.faces),
                                  plane_co=(0,145,0), plane_no=(0,1,0),
                                  clear_inner=True, clear_outer=False, dist=.0001)
            mesh.to_mesh(obj.data)
            mesh.free()
    remove_collection('D2_LF end')
    # Low decorative canopy posts formerly ended at a solid roof which has
    # just been opened; new grandstand rakers and rear columns replace them.
    remove_collection('D2_Left field canopy supports')
    # Lift the lowest canopy one metre to clear the newly restored rear rows.
    for name in ['D2_Left field roof canopies','D2_Left field roof fascia']:
        collection=bpy.data.collections.get(name)
        if collection:
            for obj in collection.objects:
                if obj.type=='MESH':
                    for vertex in obj.data.vertices:
                        if vertex.co.z<35.6:vertex.co.z+=1.0
    remove_collection('D2_Left field terrace dining')


def curved_returns(scene, batch, spec, side, rng, point_mapper=None):
    group = 'V13 '+side+' seating return'
    is_rf = side == 'RF'
    front = [Vector(p) for p in spec['bowl_front']]
    back = [Vector(p) for p in spec['bowl_back']]
    index, neighbor = (0,1) if is_rf else (-1,-2)
    f,b = front[index],back[index]
    fn,bn = front[neighbor],back[neighbor]
    field = footprint(spec)
    tower = Vector(spec['anchors']['tower_roof'][:2])
    seats, rotations, row_levels = [], [], []
    fans, fanrot = [[] for _ in range(6)], [[] for _ in range(6)]
    # User correction: no new upper seating on the river/east side of the
    # tower. Retain V12's upper west-side termination; the new north return
    # carries the lower seating to the RF foul-pole/board corner.
    tiers = TIERS[:1] if is_rf else TIERS[:3]
    # Endpoints follow the diminishing banks seen between tower and RF board,
    # and the three exposed tiers in front of the LF pavilion respectively.
    ends = [((102,2),(111,2))] if is_rf else [
            ((24,110.85),(24,127.34)),((24,130),(24,136)),((24,139),(24,144))]
    end_z = [(14,24)] if is_rf else [(13.65,22.055),(25.2,28),(29.6,32)]

    def allowed(p):
        if not _clear_of_field(Vector(p[:2]),field):
            return False
        return not (is_rf and abs(p.x-tower.x)<8.8 and abs(p.y-tower.y)<9.7)

    receipts=[]
    for tier,(ta,tb,za,zb,rows) in enumerate(tiers):
        ea,eb = [Vector((*p,0)) for p in ends[tier]]
        def at(t, z, s):
            if point_mapper is not None:
                return point_mapper(f, b, t, z, s)
            fraction=(t-ta)/(tb-ta)
            start=f.lerp(b,t)
            direction=(start-fn.lerp(bn,t)).normalized()
            end=ea.lerp(eb,fraction)
            distance=(end-start).length
            control=start+direction*distance*(.62 if is_rf else .38)
            p=start*(1-s)**2+control*(2*s*(1-s))+end*s*s
            target=end_z[tier][0]+(end_z[tier][1]-end_z[tier][0])*(z-za)/(zb-za)
            p.z=z+(target-z)*s
            return p
        cells=72
        tier_seats=0
        for row in range(rows):
            t0=ta+(tb-ta)*row/rows
            t1=ta+(tb-ta)*(row+1)/rows
            z=za+(zb-za)*row/rows
            rise=(zb-za)/rows
            midt=(t0+t1)/2
            curve=[at(midt,z,k/cells) for k in range(cells+1)]
            lengths=[0]
            for a,c in zip(curve,curve[1:]):
                lengths.append(lengths[-1]+(c-a).length)
            total=lengths[-1]
            aisle_centers=[total*.32,total*.68]
            for k in range(cells):
                s0,s1=k/cells,(k+1)/cells
                points=[at(t0,z,s0),at(t0,z,s1),at(t1,z,s1),at(t1,z,s0)]
                if not all(allowed(p) for p in points):
                    continue
                center=sum(points,Vector())/4
                aisle=any(abs((lengths[k]+lengths[k+1])/2-a)<.85 for a in aisle_centers)
                bottom=[p-Vector((0,0,.32)) for p in points]
                batch.add(group,'concrete',[tuple(p) for p in points+bottom],
                          [(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)])
                p,q=points[3],points[2]
                # Two half-risers in every aisle; the seating rake itself is
                # deliberately steeper than a pedestrian stair.
                batch.quad(group,'concrete',[tuple(p),tuple(q),tuple(at(t1,z+rise,s1)),tuple(at(t1,z+rise,s0))])
                if aisle and point_mapper is None:
                    a=at(midt,z+rise/2,s0);c=at(midt,z+rise/2,s1)
                    batch.quad(group,'stone',[tuple(a),tuple(c),tuple(at(t1,z+rise/2,s1)),tuple(at(t1,z+rise/2,s0))])
            # Uniform seat spacing, with the same radial aisle stations on each row.
            cursor=.55
            k=0
            while cursor<total-(.65 if is_rf else 1.6):
                while k<cells-1 and lengths[k+1]<cursor:
                    k+=1
                u=(cursor-lengths[k])/max(.00001,lengths[k+1]-lengths[k])
                s=(k+u)/cells
                p=at(t0+(t1-t0)*.48,z,s)
                tangent=at(midt,z,min(1,s+.001))-at(midt,z,max(0,s-.001))
                toward=at(t0,z,s)-at(t1,z,s)
                left=Vector((-tangent.y,tangent.x,0))
                if left.dot(toward)<0:
                    tangent=-tangent
                angle=math.atan2(tangent.y,tangent.x)
                cell_points=[at(t,z,k/cells) for t in (t0,t1) for k in (int(s*cells),int(s*cells)+1)]
                if all(allowed(q) for q in cell_points) and not any(abs(cursor-a)<1.05 for a in aisle_centers):
                    seats.append(tuple(p));rotations.append((0,0,angle));row_levels.append(z);tier_seats+=1
                    if rng.random()<.80:
                        color=rng.choices(range(6),[32,27,18,15,5,3])[0]
                        fans[color].append(tuple(p));fanrot[color].append((0,0,angle))
                cursor+=.56
        # Continuous rear cross aisle and edge guard, on its own tier datum.
        for k in range(cells):
            p,q=at(tb,zb,k/cells),at(tb,zb,(k+1)/cells)
            p2,q2=at(tb+.018,zb,k/cells),at(tb+.018,zb,(k+1)/cells)
            if all(allowed(v) for v in [p,q,p2,q2]):
                batch.add(group,'concrete',[tuple(v) for v in [p,q,q2,p2]],[(0,1,2,3)])
                rail(batch,group,tuple(p2),tuple(q2),1.05)
        # Rakers connect tread undersides, and columns connect those rakers to
        # the z8 foundation datum. Avoid both field and tower shaft.
        for s in ([] if point_mapper is not None else [.04,.18,.34,.50,.66,.82,.98]):
            a,c=at(ta,za-.4,s),at(tb,zb-.4,s)
            if allowed(a) and allowed(c):
                batch.cylinder(group,'concrete',a,c,.26,sides=8)
                for p in [a,c]:
                    batch.cylinder(group,'concrete',(p.x,p.y,8),p,.30,sides=8)
        # Front fascia and end edge remain visibly connected to the rakers.
        for k in range(cells):
            p,q=at(ta,za,k/cells),at(ta,za,(k+1)/cells)
            if allowed(p) and allowed(q):
                batch.quad(group,'stone',[tuple(p-Vector((0,0,.7))),tuple(q-Vector((0,0,.7))),tuple(q),tuple(p)])
        for row in range(rows):
            t=ta+(tb-ta)*row/rows;t1=ta+(tb-ta)*(row+1)/rows
            p=at(t,za+(zb-za)*row/rows,1)
            q=at(t1,za+(zb-za)*(row+1)/rows,1)
            rail(batch,group,tuple(p),tuple(q))
        receipts.append({'tier':tier+1,'rows':rows,'seats':tier_seats,
                         'front_end':list(at(ta,za,1)), 'rear_end':list(at(tb,zb,1))})
    source=bpy.data.objects['D2_Seat source']
    seat_object=instances(scene,batch.collection(group),side+' return individual seats',source,seats,rotations)
    row_attribute=seat_object.data.attributes.new('row_elevation','FLOAT','POINT')
    row_attribute.data.foreach_set('value',row_levels)
    for k,color in enumerate(['cloth_black','cloth_white','cloth_gray','navy','cloth_blue','cloth_red']):
        if fans[k]:
            instances(scene,batch.collection(group),side+' return spectators '+color,
                      bpy.data.objects['D2_Seated fan '+color],fans[k],fanrot[k])
    return {'seats':len(seats),'spectators':sum(map(len,fans)),'tiers':receipts}


def open_park_arcade(scene,batch):
    """Six real arch apertures share the park floor; one leads into the bank."""
    from r3_public_realm import TERRACE_Z
    group='V13 Park arcade'
    restaurant=bpy.data.collections.get('D2_Centerfield restaurant replacement')
    if restaurant:
        cut_box(scene,list(restaurant.objects),(31,129,PASSAGE_FLOOR-.01),
                (80,162,21.0),'V13 open restaurant undercroft')
    old=bpy.data.collections.get('D2_V12 Terrace front')
    # Keep the eastern grand stair; replace only the continuous facade and
    # its cosmetic arch panes. Cheek walls have their centroid north of 160.8.
    if old:
        for obj in list(old.objects):
            if obj.type=='MESH' and not obj.name.endswith(('paving','concrete','brick_dark')):
                remove_components(obj,lambda ps: max(p.y for p in ps)<161.65 and
                    not all(79.7<p.x<100.3 for p in ps))
    x0,x1=33.5,75.5
    bays=6;bay=(x1-x0)/bays;width=4.8
    floor=PASSAGE_FLOOR
    top=TERRACE_Z-.35
    for i in range(bays):
        center=x0+(i+.5)*bay
        radius=width/2;spring=floor+2.75
        for sign in [-1,1]:
            batch.box(group,'brick',(center+sign*(width+bay)/4,160.2,(floor+top)/2),
                      ((bay-width)/2,1.2,top-floor))
        for k in range(32):
            a=-radius+width*k/32;b=-radius+width*(k+1)/32
            za=spring+math.sqrt(max(0,radius*radius-a*a))
            zb=spring+math.sqrt(max(0,radius*radius-b*b))
            vertices=[(center+a,159.6,za),(center+b,159.6,zb),(center+b,159.6,top),(center+a,159.6,top),
                      (center+a,160.8,za),(center+b,160.8,zb),(center+b,160.8,top),(center+a,160.8,top)]
            batch.add(group,'brick',vertices,[(0,1,2,3),(7,6,5,4),(0,4,5,1)])
            angle0=math.pi*k/32;angle1=math.pi*(k+1)/32
            ring=[(center+r*math.cos(a),160.84,spring+r*math.sin(a))
                  for r,a in [(radius,angle0),(radius+.22,angle0),(radius+.22,angle1),(radius,angle1)]]
            batch.quad(group,'stone',ring)
        batch.box(group,'stone',(center,160.2,TERRACE_Z-.14),(bay+.02,1.45,.28))
        # Warm soffit illumination makes the depth legible without glazing.
        batch.box(group,'lamp',(center,156.8,21.2),(1.6,.20,.10))
    # Shared concourse and passage. The slabs meet the park to the millimetre.
    batch.box(group,'paving',(55.7,145.05,floor-.15),(47.2,31.5,.3))
    batch.box(group,'paving',(51,119.5,floor-.15),(6,20,.3))
    # Broad final descent terminates behind the outfield wall on its podium.
    stairs(batch,'V13 Passage field stair',(51,109.5,floor),(51,105.0,13.4),6,0)
    return {'floor':floor,'ceiling':PASSAGE_CEILING,'width':6,
            'arcade_y':160.2,'arcade_openings':bays,'field_landing':[51,105,13.4]}


def carve_bank_passage(scene,batch):
    collection=bpy.data.collections['D2_V12 Left-center bank']
    cut_box(scene,list(collection.objects),(48,104.5,13.39),
            (54,150,PASSAGE_CEILING),'V13 seating passage void')
    # Remove seats and people only where the passage opens through the rake.
    # Rows with a full structural soffit above the tunnel remain occupied.
    removed_seats=removed_fans=0
    for obj in collection.objects:
        if obj.type!='MESH' or obj.data.polygons:
            continue
        attr=obj.data.attributes.get('scale')
        if attr is None:
            continue
        for i,v in enumerate(obj.data.vertices):
            if 47.7<v.co.x<54.3 and 104.5<v.co.y<150 and v.co.z<PASSAGE_CEILING+.35:
                attr.data[i].vector=(0,0,0)
                if 'seats' in obj.name:removed_seats+=1
                else:removed_fans+=1
    # Guard the sides of the opening, rising with the adjacent seating rake.
    for x in [47.85,54.15]:
        for y in range(106,119):
            def adjacent_level(y):
                off=(x-60.201126)*(-.2154)+(y-119.357338)*(-.9765)
                row=max(0,min(18,math.ceil((off-2.4)/.78)))
                return 22.055-row*.467
            rail(batch,'V13 Vomitory rails',(x,y,adjacent_level(y)),(x,y+1,adjacent_level(y+1)))
    return {'removed_seats':removed_seats,'removed_spectators':removed_fans}



def trim_lf_overlap(scene,batch):
    counts={'seats':0,'spectators':0}
    collection=bpy.data.collections['D2_V12 Left-center bank']
    for obj in collection.objects:
        if obj.type!='MESH':continue
        if obj.data.polygons:
            mesh=bmesh.new();mesh.from_mesh(obj.data)
            bmesh.ops.bisect_plane(mesh,geom=list(mesh.verts)+list(mesh.edges)+list(mesh.faces),
                plane_co=(25.6,0,0),plane_no=(1,0,0),clear_inner=True,clear_outer=False,dist=.0001)
            mesh.to_mesh(obj.data);mesh.free()
        else:
            scale=obj.data.attributes.get('scale')
            if scale:
                for i,v in enumerate(obj.data.vertices):
                    if v.co.x<25.6 and scale.data[i].vector.length>0:
                        scale.data[i].vector=(0,0,0)
                        counts['seats' if 'seats' in obj.name else 'spectators']+=1
    old=bpy.data.collections['D2_Outfield']
    for obj in old.objects:
        if obj.type!='MESH':continue
        if obj.data.polygons and obj.name.endswith('concrete'):
            remove_components(obj,lambda ps: max(p.x for p in ps)<25.6)
        elif not obj.data.polygons:
            scale=obj.data.attributes.get('scale')
            if scale:
                for i,v in enumerate(obj.data.vertices):
                    if v.co.x<25.6 and scale.data[i].vector.length>0:
                        scale.data[i].vector=(0,0,0)
                        counts['seats' if 'seats' in obj.name else 'spectators']+=1
    # The junction is a full pedestrian stair, not mismatched row edges.
    stairs(batch,'V13 LF bank junction',(24.5,127.34,22.055),(24.5,110.7,13.65),2.2,1)
    return counts


def tower_platforms(batch):
    """Angular north balconies observed in the user's tower close-up.

    The artwork fixes the stacked/open relationship. Levels and footprints
    remain inferred, aligned here to the existing tower and bowl datums.
    """
    levels = [
        (39.0, [(70,-85),(93,-85),(93,-66),(88,-60),(73,-60),(70,-66)]),
        (32.6, [(70,-78),(94,-78),(100,-47),(94,-40),(77,-43),(70,-57)]),
        (26.4, [(73,-69),(96,-69),(107,-30),(102,-23),(87,-29),(76,-47)]),
    ]
    for index,(z,polygon) in enumerate(levels):
        group=f'V13 Tower platform {index+1}'
        batch.prism(group,'concrete',polygon,z-.48,z-.08)
        batch.prism(group,'paving',polygon,z-.08,z)
        # The west edge opens into the grandstand; exposed river/north edges
        # have thin guards, not a solid masonry infill.
        for a,b in zip(polygon[:4],polygon[1:5]):
            rail(batch,group,(*a,z),(*b,z),1.05)
        for x,y in polygon[1:4]:
            batch.cylinder(group,'stone',(x,y,8),(x,y,z-.48),.38,sides=8)
            batch.box(group,'stone',(x,y,8.2),(1.05,1.05,.4))
    return [{'elevation':z,'footprint':p} for z,p in levels]


def build(scene,batch,spec):
    if not scene.get('v12_proportions'):
        raise ValueError('V13 requires a completed V12 static input')
    import json
    old=json.loads(scene['v12_proportions'])
    tower_seats=bpy.data.objects.get('D2_Tower end seats')
    if tower_seats:tower_seats.name='D2_Tower end individual seats'
    remove_collection('D2_V12 Right-field corner')
    collection=bpy.data.collections['D2_RF structure']
    for obj in collection.objects:
        if obj.type=='MESH' and not obj.name.endswith('paving'):
            remove_components(obj,lambda ps: max(p.x for p in ps)<100 and max(p.z for p in ps)>13.4 and min(p.z for p in ps)>=7.9)
    trim_pavilion(scene)
    rng=random.Random(1313)
    rf=curved_returns(scene,batch,spec,'RF',rng)
    lf=curved_returns(scene,batch,spec,'LF',rng)
    platforms=tower_platforms(batch)
    # The exposed club face now sits behind the upper seats, with an open
    # lower undercroft rather than a multi-storey wall against the foul pole.
    for x in range(-50,25,6):
        batch.box('V13 Pavilion rear club','glass_mid',(x,145.1,32.1),(5.5,.15,1.8))
        batch.box('V13 Pavilion rear club','metal',(x+2.9,145.1,31.7),(.12,.3,2.7))
        batch.cylinder('V13 Pavilion rear club','concrete',(x,145.5,8),(x,145.5,36.5),.23,sides=8)
    passage=open_park_arcade(scene,batch)
    carved=carve_bank_passage(scene,batch)
    overlap=trim_lf_overlap(scene,batch)
    carved['removed_seats']+=overlap['seats']
    carved['removed_spectators']+=overlap['spectators']
    scene['seat_count']=int(scene['seat_count'])-old['rf_corner']['seats']+rf['seats']+lf['seats']-carved['removed_seats']
    scene['spectator_count']=int(scene['spectator_count'])-old['rf_corner']['spectators']+rf['spectators']+lf['spectators']-carved['removed_spectators']
    return {'rf':rf,'lf':lf,'passage':passage,'carved':carved,'tower_platforms':platforms,
            'source_basis':'North and south AECOM artwork plus user outfield crops; dimensions and hidden structure inferred.'}
