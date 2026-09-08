"""Corrections tied to the independent V13 audit issue ledger."""
import bpy,math
from mathutils import Vector
from mathutils.kdtree import KDTree
from r13_outfield import remove_components


def clip_x(points,bound,keep_greater):
    """Clip a convex row cap, interpolating its original surface heights."""
    result=[]
    for a,b in zip(points,points[1:]+points[:1]):
        ina=a[0]>=bound if keep_greater else a[0]<=bound
        inb=b[0]>=bound if keep_greater else b[0]<=bound
        if ina:result.append(a)
        if ina!=inb:
            t=(bound-a[0])/(b[0]-a[0])
            result.append(tuple(a[i]+t*(b[i]-a[i]) for i in range(3)))
    return result


def solid_cap(batch,group,material,points,bottom):
    if len(points)<3:return False
    area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points,points[1:]+points[:1]))/2
    if abs(area)<.00001:return False
    if area<0:points=list(reversed(points))
    n=len(points)
    vertices=[(p[0],p[1],bottom) for p in points]+points
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    batch.add(group,material,vertices,faces)
    return True


def restore_bank(scene,batch,root):
    names=['D2_V12 Left-center bank concrete','D2_V12 Left-center bank paving']
    with bpy.data.libraries.load(str(root/'railyards-v12-static.blend'),link=False) as (source,loaded):
        loaded.objects=list(names)
    count=0
    for name,original in zip(names,loaded.objects):
        if original is None:raise ValueError(f'Missing original bank geometry: {name}')
        material=name.rsplit(' ',1)[1]
        for face in original.data.polygons:
            points=[tuple(original.matrix_world@original.data.vertices[i].co) for i in face.vertices]
            if abs(face.normal.z)<.90 or min(p[2] for p in points)<13:continue
            points=clip_x(points,25.6,True)
            if len(points)<3:continue
            # Explicit solid domains avoid booleaning a batch of touching,
            # inconsistently wound row primitives. Each floor cap remains
            # at its authored elevation, with a genuine supported tunnel.
            left=clip_x(points,48,False)
            right=clip_x(points,54,True)
            middle=clip_x(clip_x(points,48,True),54,False)
            count+=solid_cap(batch,'V14 Left-center bank support',material,left,7.9)
            count+=solid_cap(batch,'V14 Left-center bank support',material,right,7.9)
            if middle and min(p[2] for p in middle)>=19.25:
                count+=solid_cap(batch,'V14 Left-center bank support',material,middle,18.90)
        bpy.data.objects.remove(original,do_unlink=True)
        old=bpy.data.objects.get(name)
        if old:bpy.data.objects.remove(old,do_unlink=True)
    return {'closed_row_solids':count,'passage_x':[48,54],'soffit':18.90,
            'foundation':7.9,'method':'Original V12 cap footprints split into explicit supported solids; V13 seat and passage domain preserved.'}


def pavilion_roofs(scene,batch):
    """Source-led connected pavilion study; hidden framing remains inferred."""
    import bmesh
    from r13_outfield import remove_collection
    from r11_circulation import rail
    for name in ['D2_Left field roof canopies','D2_Left field roof fascia',
                 'D2_V13 Pavilion rear club']:
        remove_collection(name)
    # The source's field galleries are open. Recess the formerly solid club
    # frontage so its floor plates and columns frame actual occupiable bays.
    for name in ['D2_Left field pavilion','D2_Left field pavilion glazing frames']:
        collection=bpy.data.collections.get(name)
        if not collection:continue
        for o in collection.objects:
            if o.type!='MESH':continue
            bm=bmesh.new();bm.from_mesh(o.data)
            bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),
                plane_co=(0,151,0),plane_no=(0,1,0),clear_inner=True,dist=.0001)
            bm.to_mesh(o.data);bm.free()
    group='V14 LF pavilion galleries'
    for z in [31.6,34.8,38.0]:
        terrace=z>37;front=141.5 if terrace else 143
        batch.box(group,'stone',(3.5,(front+153)/2,z-.2),(41,153-front,.4))
        batch.box(group,'concrete',(3.5,front+.35,z-.5),(41,.5,.6))
        if z<37:
            rail(batch,group,(-17,front+.3,z),(24,front+.3,z),1.05)
            # Rear glazing has open door bays at x0 and x16.
            for x in [-13,-5,7,19]:
                batch.box(group,'glass_mid',(x,150.8,z+1.8),(5.6,.16,3.3))
        else:
            rail(batch,group,(-17,143.3,z),(24,143.3,z),1.05)
    for x in [-16,-8,0,8,16,24]:
        batch.box(group,'brick_light',(x,145.8,23),(.45,.65,30))
        batch.box(group,'concrete',(x,145.8,8),(1.2,1.3,.5))
    # Terraces remain behind the restored seats. The old flat roof traces
    # projected in front of this datum and could not support a dining floor.
    # Two box floors replace the former third exposed bank. Their rear
    # enclosure carries the terrace; the central roof dominates a shallower
    # rear clerestory and lower dining shelter, as in the supplied closeup.
    # The AECOM views retain a masonry pavilion below a compact roof
    # cluster. The rejected study added an unsupported full-width glass box.
    batch.box(group,'stone',(-11,158,37.8),(70,14,.4))
    for x in [-46,24]:
        batch.box(group,'brick_light',(x,158,35.7),(.65,14,4.6))
    batch.box(group,'brick_light',(-31.5,151,35.7),(29,.45,4.6))
    # Continue the rear facade's window rhythm through the modest extension.
    for x in range(-45,25,3):
        batch.box(group,'brick_light',(x,165,35.7),(.55,.55,4.6))
        if x<23:
            batch.box(group,'glass_mid',(x+1.5,165,35.7),(2.4,.16,3.7))
    for z in [33.5,37.7]:
        batch.box(group,'stone',(-11,165,z),(70,.65,.45))
    # Visible roof-plane hierarchy from B4. Ridge positions and hidden
    # back slopes are inferred; broad upright glazed club walls are removed.
    roofs=[('Dining',(-2,15,151,162),38.0,39.8,40.5,.90,40.1),
           ('Middle',(-29,-5,148,164),38.0,38.7,42.5,.82,40.0),
           ('Rear',(-46,-29,148,165),38.0,39.1,39.6,.82,39.3)]
    result=[]
    for label,(x0,x1,y0,y1),floor,eave,ridge,ridge_fraction,rear_eave in roofs:
        roofgroup='V14 LF '+label+' roof'
        mid=y0+(y1-y0)*ridge_fraction
        # Two pitched planes, each with real thickness and joined eave beams.
        for ya,yb,za,zb in [(y0,mid,eave,ridge),(mid,y1,ridge,rear_eave)]:
            cap=[(x0,ya,za),(x1,ya,za),(x1,yb,zb),(x0,yb,zb)]
            verts=cap+[(x,y,z-.18) for x,y,z in cap]
            batch.add(roofgroup,'roof',verts,[(0,1,2,3),(7,6,5,4),
                (0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)])
        batch.box(roofgroup,'stone',((x0+x1)/2,(y0+y1)/2,floor-.2),
                  (x1-x0,y1-y0,.4))
        for y,edge_z in [(y0,eave),(y1,rear_eave)]:
            batch.box(roofgroup,'metal',((x0+x1)/2,y,edge_z-.3),(x1-x0,.25,.45))
        # Dining shelter posts terminate on the pavilion terrace. Taller
        # enclosed roof masses have masonry end piers and clerestory bands.
        for x in [x0+.35,x1-.35]:
            for y,edge_z in [(y0+.35,eave),(y1-.35,rear_eave)]:
                batch.box(roofgroup,'metal' if label=='Dining' else 'brick_light',
                    (x,y,(floor+edge_z)/2),(.25 if label=='Dining' else .75,.35,edge_z-floor))
        if label!='Dining':
            # B4 shows closed gable ends on the taller roof volumes. Keep
            # their bases on the common pavilion terrace, not on a second
            # elevated platform above it. These are exterior source fits.
            for x in [x0+.2,x1-.2]:
                end=[(x,y0,floor),(x,y1,floor),(x,y1,rear_eave),
                     (x,mid,ridge-.18),(x,y0,eave)]
                thickness=.35
                verts=end+[(px+thickness,py,pz) for px,py,pz in end]
                batch.add(roofgroup,'brick_light',verts,
                          [(4,3,2,1,0),(5,6,7,8,9)]+
                          [(i,(i+1)%5,(i+1)%5+5,i+5) for i in range(5)])
            for y,edge_z in [(y0+.15,eave),(y1-.15,rear_eave)]:
                batch.box(roofgroup,'glass_mid',((x0+x1)/2,y,(floor+edge_z)/2),
                          (x1-x0-.8,.16,edge_z-floor-.3))
                for x in range(math.ceil(x0+1),math.floor(x1),2):
                    batch.box(roofgroup,'metal',(x,y,(floor+edge_z)/2),(.10,.22,edge_z-floor))
        result.append({'name':label,'footprint':[x0,x1,y0,y1],
                       'floor':floor,'eave':eave,'ridge':ridge,'ridge_fraction':ridge_fraction,'rear_eave':rear_eave})
    from r2_geometry import instances
    seats=[];rotations=[]
    for z in [31.6,34.8]:
        for i in range(50):
            seats.append((-15+i*.75,144.7,z));rotations.append((0,0,0))
    for x in [-12,-4,4,12,20]:
        batch.cylinder(group,'metal',(x,145.6,38.0),(x,145.6,38.72),.06,sides=8)
        batch.cylinder(group,'stone',(x,145.6,38.72),(x,145.6,38.8),.55,sides=16)
        for sign in [-1,1]:
            seats.append((x+sign*.95,145.6,38.0));rotations.append((0,0,-sign*math.pi/2))
    instances(scene,batch.collection(group),'LF boxes and terrace individual seats',bpy.data.objects['D2_Seat source'],seats,rotations)
    for offset,color in enumerate(['cloth_black','cloth_white','cloth_gray']):
        selected=[i for i in range(len(seats))if i%4!=0 and i%3==offset]
        instances(scene,batch.collection(group),'LF box spectators '+color,bpy.data.objects['D2_Seated fan '+color],
                  [seats[i]for i in selected],[rotations[i]for i in selected])
    return {'roofs':result,'gallery_levels':[31.6,34.8],'box_and_terrace_seats':len(seats),
            'terrace':38.0,'status':'Compact roof-plane study after rejecting oversized LF mass; elevations and hidden roof slopes inferred, awaiting AECOM source comparison'}


def lantern_clearance(scene,batch,root):
    import json
    spec=json.loads((root/'scene-spec.json').read_text())
    x,y,_=spec['anchors']['west_roof_lantern']
    for o in bpy.data.collections['D2_Canopy'].objects:
        if o.type!='MESH':continue
        remove_components(o,lambda ps: min(p.x for p in ps)>x-6.2 and max(p.x for p in ps)<x+6.2
                          and min(p.y for p in ps)>y-5.2 and max(p.y for p in ps)<y+5.2
                          and min(p.z for p in ps)>47.4 and max(p.z for p in ps)<56.5)
    group='V14 West roof lantern';bottom=49.1;top=56.0;width=11.0;depth=9.0
    # Preserve the roof anchor and exterior footprint. Shorten the lower
    # enclosure to leave the retained upper rows below a real floor slab.
    batch.box(group,'glass_lit',(x,y,(bottom+top)/2),(width,depth,top-bottom))
    for u in [-width*.36,0,width*.36]:
        batch.box(group,'metal',(x+u,y,(bottom+top)/2),(.20,depth+.20,top-bottom+.15))
    for v in [-depth*.36,0,depth*.36]:
        batch.box(group,'metal',(x,y+v,(bottom+top)/2),(width+.20,.20,top-bottom+.15))
    batch.box(group,'roof',(x,y,top),(width+1.1,depth+1,.65))
    batch.box(group,'metal',(x,y,49.075),(width,depth,.45))
    return {'bottom':bottom,'roof':top,'floor_soffit':48.85,'footprint':[width,depth],
            'source_invariant':'Original roof anchor and plan footprint retained; lower enclosure shortened for occupied rows.'}


def build(scene,batch,root):
    if not scene.get('v13_outfield'):raise ValueError('V14 requires the audited V13 static scene')
    from r14_routes import bridge_receivers
    from r14_tower import tower_registration,flush_frontage
    from r14_seating import angular_rf_return,lf_sections,main_aisles,legacy_outfield,return_aisles_and_rakers,bank_guards_and_backstop
    return {'A01_bank':restore_bank(scene,batch,root),'A02_roofs':pavilion_roofs(scene,batch),
            'A03_lantern':lantern_clearance(scene,batch,root),
            'A04_receivers':bridge_receivers(scene,batch),
            'A05_tower':tower_registration(scene,batch,root),
            'A08_frontage':flush_frontage(scene,batch,root),
            'A09_main_aisles':main_aisles(scene,batch,root),
            'A09_retained_banks':legacy_outfield(scene,batch,root),
            'A09_angular_RF':angular_rf_return(scene,batch,root),
            'A07_LF_sections':lf_sections(scene,batch,root),
            'A09_returns':return_aisles_and_rakers(scene,batch,root),
            'A09_edge_guards':bank_guards_and_backstop(scene,batch,root),
            'status':'A01/A03 corrections awaiting whole-model verification; A02/A07 connected pavilion study awaits source and circulation validation'}
