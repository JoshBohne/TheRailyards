"""User-directed tower face registration and connected west-side bowl extension."""
import bpy,json,math,random,copy
from mathutils import Vector
from r13_outfield import remove_collection
from r11_circulation import rail


def cut_box(scene,objects,low,high,name):
    # Material batches contain intersecting masonry primitives; self-aware
    # exact booleans are required to preserve the wall shell around openings.
    bpy.ops.mesh.primitive_cube_add(size=1,location=tuple((a+b)/2 for a,b in zip(low,high)))
    cutter=bpy.context.object;cutter.name=name;cutter.dimensions=tuple(b-a for a,b in zip(low,high))
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    import bmesh
    for obj in objects:
        if obj.type!='MESH' or not obj.data.polygons:continue
        points=[obj.matrix_world@Vector(p)for p in obj.bound_box]
        if any(max(p[i]for p in points)<low[i] or min(p[i]for p in points)>high[i]for i in range(3)):continue
        bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
        modifier=obj.modifiers.new(name,'BOOLEAN');modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.use_self=True;modifier.object=cutter
        bpy.context.view_layer.objects.active=obj;bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(cutter,do_unlink=True)


def tower_registration(scene,batch,root):
    spec=json.loads((root/'scene-spec.json').read_text());old=spec['anchors']['tower_roof'][:]
    tower=bpy.data.collections['D2_Clock tower']
    stone=bpy.data.objects['D2_Clock tower stone']
    old_face=min((stone.matrix_world@v.co).x for v in stone.data.vertices)
    pole_x=100.0;shift=pole_x-old_face
    for obj in tower.objects:obj.location.x+=shift
    flags=bpy.data.collections.get('D2_Clock tower flags')
    if flags:
        for obj in flags.objects:obj.location.x+=shift
    bpy.context.view_layer.update()
    new=old[:];new[0]+=shift;spec['anchors']['tower_roof']=new
    cx,cy,_=new;shaft_west=cx-7.5
    remove_collection('D2_V12 Tower end')
    for number in range(1,4):remove_collection(f'D2_V13 Tower platform {number}')
    # Rebuild uniformly spaced rows; stretching the former instances would
    # produce implausible seat spacing across the expanded west-side reach.
    import r4_rf_structure
    from r12_outfield import build_tower_end
    original_clearance=r4_rf_structure.LINK_EAST_CLEAR
    original_base=r4_rf_structure.END_WALL_BASE
    try:
        r4_rf_structure.LINK_EAST_CLEAR=8.3
        r4_rf_structure.END_WALL_BASE=28.6
        extension=build_tower_end(scene,batch,spec,batch.materials,random.Random(1414))
    finally:
        r4_rf_structure.LINK_EAST_CLEAR=original_clearance
        r4_rf_structure.END_WALL_BASE=original_base
    for obj in list(scene.objects):
        if obj.name.startswith('D2_Tower platform visitors '):bpy.data.objects.remove(obj,do_unlink=True)
    seats=bpy.data.objects.get('D2_Tower end seats')
    if seats:seats.name='D2_Tower end individual seats'
    # Extend the same barrel section to the new tower-side termination.
    # Fixed bowl/canopy source paths remain unchanged behind this junction.
    from r3_envelope import _canopy_rows
    rows=_canopy_rows(spec);end_x=shaft_west-.7;roof_group='V14 RF roof extension'
    ends=[]
    for row in rows:
        a,b=Vector(row[0]),Vector(row[1]);d=(a-b).normalized()
        e=a+d*((end_x-a.x)/d.x);ends.append((a,e))
    for (a,e),(b,f) in zip(ends,ends[1:]):
        batch.quad(roof_group,'canopy',[tuple(a),tuple(b),tuple(f),tuple(e)])
        batch.quad(roof_group,'interior',[tuple(p-Vector((0,0,.22)))for p in [a,e,f,b]])
    for fraction in [0,.25,.5,.75,1]:
        arc=[tuple(a.lerp(e,fraction))for a,e in ends]
        batch.line(roof_group,'aluminum',arc,.065,sides=6)
        batch.line(roof_group,'metal',[(x,y,z-.22)for x,y,z in arc],.14,sides=8)
    for a,e in [ends[0],ends[-1]]:batch.line(roof_group,'metal',[tuple(a),tuple(e)],.24,sides=8)
    # Rear columns carry the new canopy/rake from outside the occupied rows.
    a,e=ends[0]
    for fraction in [.25,.5,.75,1]:
        p=a.lerp(e,fraction)
        batch.box(roof_group,'brick',(p.x,p.y,(8+p.z)/2),(.6,.65,p.z-8))
    from r3_envelope import _fascia_bay,ENVELOPE_SPEC
    facade=ENVELOPE_SPEC['facade'];a,e=ends[0];count=max(1,round((e-a).length/6))
    for i in range(count):
        left=a.lerp(e,i/count);right=a.lerp(e,(i+1)/count);center=(left+right)/2
        _fascia_bay(batch,center,left-right,(right-left).length,
                    facade['fascia_bottom_z'],facade['fascia_top_z'],.45)
    north=cy+7.5
    front,back=Vector(spec['bowl_front'][0]),Vector(spec['bowl_back'][0])
    def bowl(t):return tuple(front.lerp(back,t)[:2])
    # Lower two terraces reach the real concourse gaps. Their rear edges
    # stay in front of the adjacent seating rake rather than underneath it.
    levels=[(39,[(78,-78.5),(shaft_west,-78.5),(shaft_west,north),(119,north),(119,-59),(112,-53),(95,-56),(78,-68)]),
            (32.6,[bowl(.53),(shaft_west,-67.25),(shaft_west,north),(119.5,north),(119.5,-51),(113,-47),(99,-49),(83,-62),bowl(.495)]),
            (26.4,[bowl(.38),(shaft_west,-58),(shaft_west,north),(120,north),(120,-45),(114,-40),(101,-43),(90,-50),bowl(.345)])]
    for number,(z,polygon) in enumerate(levels,1):
        group=f'V14 Tower terrace {number}'
        batch.prism(group,'concrete',polygon,z-.4,z-.07);batch.prism(group,'paving',polygon,z-.07,z)
        # Guards only on exposed north/east edges; west edge meets bowl rows.
        for a,b in zip(polygon[3:-1],polygon[4:]):rail(batch,group,(*a,z),(*b,z),1.05)
        for x,y in polygon[3:6]:
            batch.cylinder(group,'metal',(x,y,8),(x,y,z-.4),.20,sides=8)
            batch.box(group,'stone',(x,y,8.1),(.85,.85,.5))
    # A common frame carries all three slabs; offset decorative edge posts
    # alone did not explain the long terrace projections after registration.
    for x in [100,115]:
        batch.box('V14 Tower terrace frame','metal',(x,-61,23.3),(.65,.65,30.6))
        batch.box('V14 Tower terrace frame','stone',(x,-61,7.8),(1.6,1.6,.6))
    for z in [26.4,32.6,39]:
        batch.box('V14 Tower terrace frame','metal',(107.5,-61,z-.7),(15.65,.5,.6))
    batch.cylinder('V14 Tower terrace frame','metal',(100,-61,8.2),(115,-61,25.7),.14,sides=8)
    batch.cylinder('V14 Tower terrace frame','metal',(115,-61,8.2),(100,-61,25.7),.14,sides=8)
    # Upper balcony connects to the existing z36 cross aisle by a real
    # transverse stair in its clear gap, north of the z39 first seating row.
    from r11_circulation import stairs
    stairs(batch,'V14 Tower bowl connections',(78,-77.35,39),(72,-77.35,36),1.8,0)
    batch.box('V14 Tower bowl connections','concrete',(71,-77.35,35.85),(4,1.8,.3))
    # Short graded threshold strips absorb the existing 0.1 m differences
    # between the reconstructed main concourses and the tower balconies.
    for ta,tb,z0,z1 in [(.345,.38,26.5,26.4),(.495,.53,32.5,32.6)]:
        a,b=front.lerp(back,ta),front.lerp(back,tb)
        cap=[(a.x-.5,a.y,z0),(b.x-.5,b.y,z0),(b.x+1,b.y,z1),(a.x+1,a.y,z1)]
        batch.add('V14 Tower bowl connections','concrete',cap+[(x,y,z-.25)for x,y,z in cap],
                  [(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)])
    # An actual hollow interior and north-facing doorways replace the solid
    # shaft behind decorative windows. The internal vertical system remains
    # a conceptual lift/stair core until the full route audit is complete.
    cut_box(scene,list(tower.objects),(cx-6,cy-6,8.05),(cx+6,cy+6,47.5),'V14 tower interior')
    served=[8,20,26.4,28.6,32.6,39,47.6]
    for z in served:
        if z not in [20,28.6]:
            cut_box(scene,list(tower.objects),(cx-1.5,cy+5.7,z-.02),(cx+1.5,cy+10,z+2.5),'V14 tower north doorway')
        else:
            cut_box(scene,list(tower.objects),(cx-10,cy-5,z-.02),(cx-5.7,cy-2,z+2.5),'V14 tower west doorway')
            batch.box('V14 Tower interior','stone',(cx-7.7,cy-3.5,z-.15),(4.6,3,.3))
            batch.box('V14 Tower interior','stone',(cx-3.75,cy-3.5,z-.15),(4.5,3,.3))
        group='V14 Tower interior'
        # Four floor strips leave an open3m-square central lift well.
        for x0,x1,y0,y1 in [(-6,-1.5,4,6),(1.5,6,-6,6),(-1.5,1.5,-6,-1.5),(-1.5,1.5,1.5,6)]:
            batch.box(group,'stone',(cx+(x0+x1)/2,cy+(y0+y1)/2,z-.07),(x1-x0,y1-y0,.14))
        if z not in [20,28.6]:batch.box(group,'stone',(cx,cy+7.2,z-.15),(3,3.4,.3))
        for side in [-1,1]:batch.box(group,'stone',(cx+side*1.55,cy+7.55,z+1.25),(.16,.25,2.5))
        batch.box(group,'stone',(cx,cy+7.55,z+2.6),(3.3,.25,.2))
        # Lift portal is a real opening in the framed shaft, facing the door.
        for side in [-1,1]:batch.box(group,'metal',(cx+side*1.48,cy+1.5,z+1.2),(.12,.12,2.4))
        batch.box(group,'metal',(cx,cy+1.5,z+2.45),(3,.14,.12))
    for x in [-1.5,1.5]:
        for y in [-1.5,1.5]:batch.box('V14 Tower interior','metal',(cx+x,cy+y,28),(.12,.12,40))
    batch.box('V14 Tower interior','metal',(cx,cy,7.92),(2.8,2.8,.16))
    # Enclose the inferred lift well; the earlier bare frame left the upper
    # landings open to a drop. Static doors are shown closed on every floor.
    for x in [-1.5,1.5]:
        batch.box('V14 Tower lift enclosure','glass_mid',(cx+x,cy,29.05),(.08,3,42.1))
    for y in [-1.5,1.5]:
        batch.box('V14 Tower lift enclosure','glass_mid',(cx,cy+y,29.05),(3,.08,42.1))
    for z in served:
        batch.box('V14 Tower lift enclosure','metal',(cx,cy+1.56,z+1.2),(.04,.07,2.4))
        batch.box('V14 Tower lift enclosure','metal',(cx,cy+1.56,z+2.45),(3,.07,.1))
    stair_receipt=internal_tower_stairs(batch,cx,cy,served)
    batch.box('V14 Tower foundation','stone',(cx,cy,6.425),(19.7,20.2,3.15))
    batch.box('V14 Tower foundation','stone',(cx,cy+9.1,7.85),(3.2,2,.3))
    from r11_circulation import stairs
    # Meet the existing sloping riverwalk at its actual local grade. The
    # old fixed4.95 destination sent the stair below the paved promenade.
    from r3_public_realm import quay_z
    arrival_y=cy+17.1;arrival_z=quay_z(arrival_y)
    cap=[(cx-1.4,cy+10.1,8),(cx+1.4,cy+10.1,8),
         (cx+1.4,arrival_y,arrival_z),(cx-1.4,arrival_y,arrival_z)]
    batch.add('V14 Tower quay arrival','paving',cap+[(x,y,z-.25)for x,y,z in cap],
              [(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)])
    scene['v14_tower_anchor']=json.dumps(new)
    return {'old_anchor':old,'new_anchor':new,'shift_x':shift,'old_near_face_x':old_face,
            'new_near_face_x':100,'rf_foul_pole_x':pole_x,'shaft_west_x':shaft_west,
            'extension':extension,'terraces':[{'z':z,'footprint':p}for z,p in levels],
            'served_levels':served,'internal_stairs':stair_receipt,'status':'Registration and geometry study; internal stairs and full route validation pending'}


def flush_frontage(scene,batch,root):
    """Align actual arcade wall and roof edges with the stadium facade datum."""
    spec=json.loads((root/'scene-spec.json').read_text())
    remove_collection('D2_River-side arcade')
    back=[Vector(p) for p in spec['bowl_back']]
    # Follow the curved main facade, then the same terminal tangent used by
    # the new bowl/canopy extension. No independent cosmetic roof offset.
    path=list(reversed([p for p in back if p.x>=18 and p.y<-100]))
    direction=(back[0]-back[1]).normalized()
    end=back[0]+direction*((100-back[0].x)/direction.x);path.append(end)
    path.append(Vector((100,spec['anchors']['tower_roof'][1]-3,48)))
    from r2_geometry import resample
    path=resample(path,7.4)
    group='V14 Flush RF frontage';segments=[]
    envelope=[o for o in scene.objects if o.type=='MESH' and o.data.polygons and
              (o.name.startswith('D2_Stadium envelope ') or o.name.startswith('D2_RF structure '))]
    # A single continuous corridor cutter avoids booleaning every overlapping
    # facade primitive once per bay. It follows the same curved frontage.
    normals=[]
    for i,a in enumerate(path):
        tangent=path[min(i+1,len(path)-1)]-path[max(0,i-1)];tangent.z=0;tangent.normalize()
        normals.append(Vector((tangent.y,-tangent.x,0)))
    footprint=[p+n*1.1 for p,n in zip(path,normals)]+list(reversed([p-n*6.6 for p,n in zip(path,normals)]))
    verts=[(p.x,p.y,z) for z in [7.975,28.625] for p in footprint];count=len(footprint)
    faces=[tuple(reversed(range(count))),tuple(range(count,2*count))]+[(i,(i+1)%count,(i+1)%count+count,i+count)for i in range(count)]
    mesh=bpy.data.meshes.new('V14 continuous frontage void');mesh.from_pydata(verts,[],faces);mesh.update()
    cutter=bpy.data.objects.new(mesh.name,mesh);scene.collection.objects.link(cutter)
    import bmesh
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
    for obj in envelope:
        modifier=obj.modifiers.new(cutter.name,'BOOLEAN');modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.use_self=True;modifier.object=cutter
        bpy.context.view_layer.objects.active=obj;bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(cutter,do_unlink=True)
    for a,b in zip(path,path[1:]):
        u=(b-a).normalized();u.z=0;u.normalize();n=Vector((u.y,-u.x,0))
        center=(a+b)/2+n*.85;length=(b-a).length;angle=math.atan2(u.y,u.x)
        def p(x,y,z):
            q=center+u*x-n*y;q.z=z;return q
        for z in [8,20,28.6]:batch.box(group,'stone',p(0,3.4,z-.15),(length+.03,6.8,.3),angle)
        # Each generator segment is a narrow masonry bay. Cluster visual
        # details continuously along the same field-independent datum.
        batch.box(group,'brick',p(-length/2,0,18.3),(.28,.65,20.6),angle)
        batch.box(group,'metal',p(-length/2,6.6,18.3),(.25,.35,20.6),angle)
        batch.box(group,'glass',p(0,.12,24.15),(max(.1,length-.28),.12,7.9),angle)
        batch.box(group,'metal',p(0,0,20.15),(length+.1,.3,.3),angle)
        batch.box(group,'stone',p(0,0,28.6),(length+.08,.45,.3),angle)
        # Lower openings are real voids; segmented arch ring above open bays.
        radius=max(.25,(length-.28)/2);spring=15.5
        for k in range(12):
            t0=math.pi*k/12;t1=math.pi*(k+1)/12
            points=[tuple(p(r*math.cos(t),0,spring+r*math.sin(t)))for r,t in [(radius,t0),(radius+.2,t0),(radius+.2,t1),(radius,t1)]]
            batch.quad(group,'brick_light',points)
        for k in range(16):
            xa=-radius+2*radius*k/16;xb=-radius+2*radius*(k+1)/16
            za=spring+math.sqrt(max(0,radius*radius-xa*xa));zb=spring+math.sqrt(max(0,radius*radius-xb*xb))
            front=[p(xa,0,za),p(xb,0,zb),p(xb,0,20),p(xa,0,20)]
            rear=[q-n*.6 for q in front]
            batch.add(group,'brick',[tuple(q)for q in front+rear],[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)])
        segments.append({'front_start':list(p(-length/2,0,0)[:2]),'front_end':list(p(length/2,0,0)[:2]),'depth':6.8})
    return {'segments':segments,'floor_levels':[8,20],'roof':28.6,
            'rule':'Wall plane and roof edge share the main facade datum; old projecting volume removed',
            'status':'Generator study awaiting fixed source/current frontage and clearance checks'}


def internal_tower_stairs(batch,cx,cy,served):
    """Stack paired flights inside the west shaft, leaving the lift well clear."""
    group='V14 Tower stairs';routes=[]
    for low,high in zip(served,served[1:]):
        flights=max(2,2*math.ceil((high-low)/6.4));rise=(high-low)/flights
        steps=math.ceil(rise/.17);run=steps*.31;far=4-run
        for flight in range(flights):
            top=high-flight*rise;x=cx-4.95 if flight%2==0 else cx-3.2
            start,end=(4,far)if flight%2==0 else(far,4)
            for step in range(steps):
                y=cy+start+(end-start)*(step+.5)/steps;z=top-(step+1)*rise/steps
                batch.box(group,'stone',(x,y,z-.1),(1.45,.32,.2))
                routes.append([x,y,z])
            landing_y=far-1 if flight%2==0 else 5
            batch.box(group,'stone',(cx-4.1,cy+landing_y,top-rise-.07),(3.4,2,.14))
            if flight%2==0:
                # The south turn projects into the open stair well. Protect
                # its three exposed edges while leaving both flights open.
                points=[(cx-5.8,cy+far,top-rise),(cx-5.8,cy+far-2,top-rise),
                        (cx-2.4,cy+far-2,top-rise),(cx-2.4,cy+far,top-rise)]
                for a,b in zip(points,points[1:]):rail(batch,group,a,b,.95)

            for edge in [-.75,.75]:
                a=(x+edge,cy+start,top);b=(x+edge,cy+end,top-rise)
                rail(batch,group,a,b,.95)
            # Stringers connect every flight to the masonry-side landings.
            for dx in [-.56,.56]:
                batch.cylinder(group,'metal',(x+dx,cy+start,top-.3),(x+dx,cy+end,top-rise-.3),.10,sides=8)
        routes.extend([[cx-4.1,cy+5,low],[cx-4.1,cy+5,high]])
    return {'levels':served,'sampled_tread_centers':routes,'going':.31,'riser_max':.17,
            'inference':'Internal stair/lift arrangement is not visible in the artwork.'}


def finalize_tower(scene,receipt):
    """Open the west portals after the new facade material batches exist."""
    cx,cy,_=receipt['A05_tower']['new_anchor']
    candidates=[obj for obj in scene.objects if obj.name in [
        'D2_V12 Tower end brick','D2_V12 Tower end stone',
        'D2_V14 Flush RF frontage glass','D2_V14 Flush RF frontage metal',
        'D2_V14 Flush RF frontage brick','D2_V14 Flush RF frontage brick_light']]
    for z in [20,28.6]:
        cut_box(scene,candidates,(cx-10,cy-5,z+.01),(cx-5.7,cy-2,z+2.5),'V14 completed west portal')
    return {'opened_levels':[20,28.6],'opening_width':3,'opening_height':2.49}
