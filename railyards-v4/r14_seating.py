"""Shared physical aisle geometry for the existing normalized seat sections."""
import bpy,json,math
from mathutils import Vector
from r13_outfield import remove_collection

TIERS=[(0,.34,14,24,24),(.40,.49,27,30,8),(.55,.65,33,36,9),(.70,.93,39,47,18)]


def angular_rf_point(front, back, t, z, station):
    """Straight diagonal rows terminate below the river outfield concourse.

    The reference establishes straight angled faces, not an exact surveyed
    rake. The main-bowl join retains its existing row elevations; the river
    endpoint tapers to the retained low bank's 17.01 m rear datum.
    """
    fraction=t/.34
    end=Vector((102+9*fraction,2,0))
    point=front.lerp(back,t).lerp(end,station)
    point.z=z+((14+(17.01-14)*(z-14)/10)-z)*station
    return point


def angular_rf_return(scene,batch,root):
    import random
    from r13_outfield import curved_returns
    spec=json.loads((root/'scene-spec.json').read_text())
    spec['anchors']['tower_roof']=json.loads(scene['v14_tower_anchor'])
    remove_collection('D2_V13 RF seating return')
    result=curved_returns(scene,batch,spec,'RF',random.Random(1415),angular_rf_point)
    # The diagonal wedge narrows at the river; omit a chair when any of its
    # feet would overhang a clipped cap instead of leaving partial support.
    from mathutils.bvhtree import BVHTree
    vertices=[];faces=[]
    for (group,material),points in batch.vertices.items():
        if group!='V13 RF seating return':continue
        offset=len(vertices);vertices.extend(points)
        faces.extend(tuple(offset+i for i in face)for face in batch.faces[(group,material)])
    tree=BVHTree.FromPolygons(vertices,faces);omitted=[]
    obj=bpy.data.objects['D2_RF return individual seats'];rot=obj.data.attributes['rotation'];scale=obj.data.attributes['scale']
    for i,v in enumerate(obj.data.vertices):
        angle=rot.data[i].vector.z
        for dx,dy in [(-.2475,-.15),(.2475,-.15),(.2475,.15),(-.2475,.15)]:
            point=v.co+Vector((dx*math.cos(angle)-dy*math.sin(angle),dx*math.sin(angle)+dy*math.cos(angle),.05))
            hit=tree.ray_cast(point,Vector((0,0,-1)),.35)[0]
            if hit is None:
                scale.data[i].vector=(0,0,0);omitted.append(tuple(round(c,4)for c in v.co));break
    omitted_fans=0
    for obj in batch.collection('V13 RF seating return').objects:
        if 'spectators' not in obj.name:continue
        scale=obj.data.attributes.get('scale')
        for i,v in enumerate(obj.data.vertices):
            if tuple(round(c,4)for c in v.co)in omitted:
                scale.data[i].vector=(0,0,0);omitted_fans+=1
    result['omitted_at_tapered_edges']=len(omitted);result['seats']-=len(omitted)
    result['tiers'][0]['seats']=result['seats'];result['spectators']-=omitted_fans
    result['geometry']='Straight diagonal rows; river endpoint rear floor 17.01 below outfield concourse'
    return result


def main_aisles(scene,batch,root):
    spec=json.loads((root/'scene-spec.json').read_text());front=[Vector(p)for p in spec['bowl_front']];back=[Vector(p)for p in spec['bowl_back']]
    # These two old systems used different index grids; neither followed the
    # seat generator's arc-length section gaps, so they crossed occupied rows.
    remove_collection('D2_Bowl railings');remove_collection('D2_Aisle handrails')
    cache={}
    def curve(t):
        if t not in cache:
            points=[a.lerp(b,t)for a,b in zip(front,back)];lengths=[0]
            for a,b in zip(points,points[1:]):lengths.append(lengths[-1]+(b-a).length)
            cache[t]=(points,lengths)
        return cache[t]
    def at(t,fraction,z):
        points,lengths=curve(t);target=fraction*lengths[-1];index=0
        while index<len(points)-2 and lengths[index+1]<target:index+=1
        p=points[index].lerp(points[index+1],(target-lengths[index])/(lengths[index+1]-lengths[index]));p.z=z;return p
    result=[];group='V14 Bowl aisle stairs'
    for tier,(ta,tb,za,zb,rows) in enumerate(TIERS):
        rise=(zb-za)/rows
        for section in range(27):
            fraction=(section+.05)/27
            # Central handrail is supported from the actual aisle stairs;
            # no second incompatible grid or posts in adjacent seat bodies.
            rail_points=[]
            for row in range(rows):
                t0=ta+(tb-ta)*row/rows;t1=ta+(tb-ta)*(row+1)/rows;z=za+row*rise
                for sub in range(3):
                    a=t0+(t1-t0)*sub/3;b=t0+(t1-t0)*(sub+1)/3;top=z+rise*sub/3
                    length=curve((a+b)/2)[1][-1];half_fraction=(.05/27)-.10/length
                    cap=[at(a,fraction-half_fraction,top),at(a,fraction+half_fraction,top),
                         at(b,fraction+half_fraction,top),at(b,fraction-half_fraction,top)]
                    bottom=[Vector((p.x,p.y,z-.08))for p in cap]
                    batch.add(group,'stone',[tuple(p)for p in bottom+cap],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
                    center=at((a+b)/2,fraction,top);rail_points.append(center+Vector((0,0,.95)))
                    if sub==1 and row%2==0:batch.cylinder(group,'metal',center,center+Vector((0,0,.95)),.027,sides=6)
            batch.line(group,'metal',[tuple(p)for p in rail_points],.028,sides=6)
        result.append({'tier':tier+1,'aisles':27,'risers_per_seat_row':3,'riser':rise/3,
                       'section_rule':'Matches r2_seating normalized arc-length gap, centered at (section+.05)/27'})
    return result


def legacy_outfield(scene,batch,root):
    """Rebuild low retained rows with inset seats and continuous supported rakes."""
    import random
    from r3_outfield import _path_pieces,_offset_segment,_open_sections
    from r2_geometry import instances
    from r14_audit import clip_x,solid_cap
    spec=json.loads((root/'scene-spec.json').read_text());boundary=[Vector(p[:2])for p in spec['field_boundary']]
    for obj in list(scene.objects):
        if obj.name=='D2_Outfield concrete' or obj.name=='D2_Outfield individual seats' or obj.name.startswith('D2_Outfield spectators '):bpy.data.objects.remove(obj,do_unlink=True)
    group='V14 Retained outfield banks';seats=[];rotations=[];fans=[[]for _ in range(6)];fanrot=[[]for _ in range(6)];rng=random.Random(1431)
    depth=(9.4-1.45)/9;rise=(17.01-13.65)/8
    for row in range(9):
        offset=1.45+row*depth;z=13.65+row*rise
        for piece_a,piece_b in _path_pieces(boundary,[(.0445,.094),(.317,.47),(.94,.985)]):
            fa,fb=_offset_segment(piece_a,piece_b,offset);ra,rb=_offset_segment(piece_a,piece_b,offset+depth)
            for kind,a,b in _open_sections(fa,fb):
                length=(fb-fa).length;ta=(a-fa).length/length;tb=(b-fa).length/length
                c,d=ra.lerp(rb,ta),ra.lerp(rb,tb)
                polygon=clip_x([(a.x,a.y,z),(b.x,b.y,z),(d.x,d.y,z),(c.x,c.y,z)],25.6,True)
                if len(polygon)<3:continue
                solid_cap(batch,group,'concrete',polygon,13.35)
                if kind=='aisle':
                    for sub in [1,2]:
                        aa=a.lerp(c,sub/3);bb=b.lerp(d,sub/3);top=z+rise*sub/3
                        cap=clip_x([(aa.x,aa.y,top),(bb.x,bb.y,top),(d.x,d.y,top),(c.x,c.y,top)],25.6,True)
                        solid_cap(batch,group,'stone',cap,z-.03)
                    continue
                start=a.lerp(c,.55);end=b.lerp(d,.55);tangent=(end-start).normalized();span=(end-start).length
                if span<1:continue
                count=max(1,math.floor((span-.85)/.58)+1)
                for i in range(count):
                    t=.425+(span-.85)*(i/(count-1) if count>1 else .5);p=start+tangent*t
                    if p.x<25.95:continue
                    position=(p.x,p.y,z);angle=math.atan2(tangent.y,tangent.x)
                    seats.append(position);rotations.append((0,0,angle))
                    if rng.random()<.78:
                        color=rng.choices(range(6),[32,27,18,15,5,3])[0];fans[color].append(position);fanrot[color].append((0,0,angle))
    instances(scene,batch.collection(group),'Outfield individual seats',bpy.data.objects['D2_Seat source'],seats,rotations)
    for i,color in enumerate(['cloth_black','cloth_white','cloth_gray','navy','cloth_blue','cloth_red']):
        source=bpy.data.objects.get('D2_Seated fan '+color)
        if source and fans[i]:instances(scene,batch.collection(group),'Outfield spectators '+color,source,fans[i],fanrot[i])
    return {'seats':len(seats),'rows':9,'rise':rise,'depth':depth,'aisle_riser':rise/3,
            'seat_inset':.425,'foundation':13.35,'note':'Seat centers interpolate the authored cap edges, avoiding radial endpoint overhang.'}


def return_aisles_and_rakers(scene,batch,root):
    from r13_outfield import remove_components
    from r12_outfield import footprint,_clear_of_field
    spec=json.loads((root/'scene-spec.json').read_text());front=[Vector(p)for p in spec['bowl_front']];back=[Vector(p)for p in spec['bowl_back']]
    field=footprint(spec)
    def allowed(p):return _clear_of_field(Vector(p[:2]),field)
    records=[]
    for side in ['RF','LF']:
        rf=side=='RF';index,neighbor=(0,1)if rf else(-1,-2);f,b=front[index],back[index];fn,bn=front[neighbor],back[neighbor]
        tiers=TIERS[:1]if rf else TIERS[:3]
        ends=[((102,2),(111,2))]if rf else[((24,110.85),(24,127.34)),((24,130),(24,136)),((24,139),(24,144))]
        end_z=[(14,24)]if rf else[(13.65,22.055),(25.2,28),(29.6,32)]
        concrete=bpy.data.objects.get(f'D2_V13 {side} seating return concrete')
        if concrete:remove_components(concrete,lambda ps:len(ps)==16)
        stone=bpy.data.objects.get(f'D2_V13 {side} seating return stone')
        if stone:remove_components(stone,lambda ps:len(ps)==4 and max(p.z for p in ps)-min(p.z for p in ps)<.12)
        group=f'V14 {side} return access'
        for tier,(ta,tb,za,zb,rows)in enumerate(tiers):
            ea,eb=[Vector((*p,0))for p in ends[tier]]
            def at(t,z,s):
                if rf:return angular_rf_point(f,b,t,z,s)
                fraction=(t-ta)/(tb-ta);start=f.lerp(b,t);direction=(start-fn.lerp(bn,t)).normalized();end=ea.lerp(eb,fraction)
                control=start+direction*(end-start).length*(.62 if rf else .38)
                p=start*(1-s)**2+control*(2*s*(1-s))+end*s*s
                target=end_z[tier][0]+(end_z[tier][1]-end_z[tier][0])*(z-za)/(zb-za);p.z=z+(target-z)*s;return p
            for row in range(rows):
                t0=ta+(tb-ta)*row/rows;t1=ta+(tb-ta)*(row+1)/rows;z=za+(zb-za)*row/rows;rise=(zb-za)/rows
                points=[at((t0+t1)/2,z,k/72)for k in range(73)];lengths=[0]
                for p,q in zip(points,points[1:]):lengths.append(lengths[-1]+(q-p).length)
                def param(distance):
                    k=0
                    while k<71 and lengths[k+1]<distance:k+=1
                    return (k+(distance-lengths[k])/(lengths[k+1]-lengths[k]))/72
                for fraction in [.32,.68]:
                    sa,sb=param(lengths[-1]*fraction-.75),param(lengths[-1]*fraction+.75)
                    for sub in range(3):
                        a=t0+(t1-t0)*sub/3;b0=t0+(t1-t0)*(sub+1)/3;top=z+rise*sub/3
                        cap=[at(a,top,sa),at(a,top,sb),at(b0,top,sb),at(b0,top,sa)]
                        if not all(allowed(p)for p in cap):continue
                        bottom=[at(a,z-.06,sa),at(a,z-.06,sb),at(b0,z-.06,sb),at(b0,z-.06,sa)]
                        batch.add(group,'stone',[tuple(p)for p in bottom+cap],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
            # Piecewise rakers follow each actual row, rather than a straight
            # end-to-end chord that emerged through33 occupied RF positions.
            for s in [.04,.18,.34,.50,.66,.82,.98]:
                support=[at(ta+(tb-ta)*r/rows,za+(zb-za)*r/rows-.8,s)for r in range(rows+1)]
                for a,b0 in zip(support,support[1:]):
                    if allowed(a) and allowed(b0):batch.cylinder(group,'concrete',a,b0,.22,sides=8)
                for p in [support[0],support[-1]]:
                    if allowed(p):batch.cylinder(group,'concrete',(p.x,p.y,8),p,.24,sides=8)
            records.append({'side':side,'tier':tier+1,'rows':rows,'raker_drop':.8,'aisle_risers_per_row':3})
    return records


def bank_guards_and_backstop(scene,batch,root):
    from mathutils.bvhtree import BVHTree
    from r11_circulation import rail
    from r2_geometry import resample
    spec=json.loads((root/'scene-spec.json').read_text())
    remove_collection('D2_V13 Vomitory rails')
    vertices=[];faces=[]
    for (group,material),points in batch.vertices.items():
        if group!='V14 Left-center bank support':continue
        start=len(vertices);vertices.extend(points);faces.extend(tuple(start+i for i in f)for f in batch.faces[(group,material)])
    tree=BVHTree.FromPolygons(vertices,faces);ends=[]
    for x in [47.96,54.04]:
        end_y=114.79837036-(x-48)*(.22057088)+.01;ends.append((x,end_y,19.253))
        stations=[];y=106
        while y<end_y-.02:
            hit,normal,face,distance=tree.ray_cast(Vector((x,y,25)),Vector((0,0,-1)),14)
            if hit is not None:stations.append(tuple(hit))
            y+=.4
        stations.append((x,end_y,19.253))
        for a,b in zip(stations,stations[1:]):rail(batch,'V14 Vomitory edge guards',a,b,1.05)
    rail(batch,'V14 Vomitory edge guards',ends[0],ends[1],1.05)
    # Follow the complete front-row curve instead of long sparse chords;
    # offset toward the field so the net posts clear occupied first rows.
    remove_collection('D2_Backstop protection')
    path=[]
    for value in spec['bowl_front'][25:116]:
        p=Vector(value);toward=Vector((-p.x,-p.y,0)).normalized();p+=toward*.65;path.append(p)
    for p in path[::15]:batch.cylinder('V14 Backstop','metal',(p.x,p.y,13.5),(p.x,p.y,22),.05,sides=6)
    for z in [14,16,18,20,22]:batch.line('V14 Backstop','metal',[(p.x,p.y,z)for p in path],.009,sides=4)
    for p in resample(path,.75):batch.line('V14 Backstop','metal',[(p.x,p.y,13.5),(p.x,p.y,22)],.006,sides=4)
    # Resolve the actual cropped row ends; preserve the guard rather than
    # leaving chairs whose legs extend over the bank/junction cut.
    removed=[]
    for obj in scene.objects:
        if obj.type!='MESH' or obj.data.polygons:continue
        if obj.name=='D2_Left-center bank individual seats':indices=[i for i,v in enumerate(obj.data.vertices)if 25.6<v.co.x<25.95]
        elif obj.name=='D2_LF return individual seats':indices=[44,91,139]
        elif obj.name=='D2_Individual seats':indices=[551]
        else:continue
        scales=obj.data.attributes.get('scale')
        for i in indices:
            if scales and scales.data[i].vector.length>.1:
                removed.append({'object':obj.name,'index':i,'point':list(obj.data.vertices[i].co)})
                scales.data[i].vector=(0,0,0)
    positions={tuple(round(v,4)for v in item['point'])for item in removed};fans=0
    for obj in scene.objects:
        if obj.type!='MESH' or obj.data.polygons or 'spectator'not in obj.name.lower():continue
        scales=obj.data.attributes.get('scale')
        if scales is None:continue
        for i,v in enumerate(obj.data.vertices):
            if tuple(round(c,4)for c in v.co)in positions and scales.data[i].vector.length>.1:
                scales.data[i].vector=(0,0,0);fans+=1
    return {'guard_ends':ends,'backstop_inward_offset':.65,'omitted_edge_seats':removed,'matching_fans':fans}
