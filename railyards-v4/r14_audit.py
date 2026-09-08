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
    for z in [24.4,28.8,33.4]:
        batch.box(group,'stone',(3.5,148.5,z-.2),(41,7,.4))
        batch.box(group,'concrete',(3.5,145.35,z-.5),(41,.5,.6))
        if z<33:
            rail(batch,group,(-17,145.3,z),(24,145.3,z),1.05)
            # Rear glazing has open door bays at x0 and x16.
            for x in [-13,-5,7,19]:
                batch.box(group,'glass_mid',(x,150.8,z+1.8),(5.6,.16,3.3))
        else:
            rail(batch,group,(-17,145.3,z),(24,145.3,z),1.05)
    for x in [-16,-8,0,8,16,24]:
        batch.box(group,'brick_light',(x,145.8,20.7),(.45,.65,25.4))
        batch.box(group,'concrete',(x,145.8,8),(1.2,1.3,.5))
    # Terraces remain behind the restored seats. The old flat roof traces
    # projected in front of this datum and could not support a dining floor.
    roofs=[('Dining',(-5,18,146,161),33.4,36.5,38.0),
           ('Middle',(-25,-5,144,160),33.4,37.0,40.0),
           ('Rear',(-46,-25,136,165),38.8,41.0,44.0)]
    result=[]
    for label,(x0,x1,y0,y1),floor,eave,ridge in roofs:
        roofgroup='V14 LF '+label+' roof'
        mid=(y0+y1)/2
        # Two pitched planes, each with real thickness and joined eave beams.
        for ya,yb,za,zb in [(y0,mid,eave,ridge),(mid,y1,ridge,eave)]:
            cap=[(x0,ya,za),(x1,ya,za),(x1,yb,zb),(x0,yb,zb)]
            verts=cap+[(x,y,z-.18) for x,y,z in cap]
            batch.add(roofgroup,'roof',verts,[(0,1,2,3),(7,6,5,4),
                (0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)])
        batch.box(roofgroup,'stone',((x0+x1)/2,(y0+y1)/2,floor-.2),
                  (x1-x0,y1-y0,.4))
        for y in [y0,y1]:
            batch.box(roofgroup,'metal',((x0+x1)/2,y,eave-.3),(x1-x0,.25,.45))
        # Dining shelter posts terminate on the pavilion terrace. Taller
        # enclosed roof masses have masonry end piers and clerestory bands.
        for x in [x0+.35,x1-.35]:
            for y in [y0+.35,y1-.35]:
                batch.box(roofgroup,'metal' if label=='Dining' else 'brick_light',
                    (x,y,(floor+eave)/2),(.25 if label=='Dining' else .75,.35,eave-floor))
                if floor>33.4:
                    batch.box(roofgroup,'brick_light',(x,y,(8+floor)/2),(.65,.65,floor-8))
        if label!='Dining':
            for y in [y0+.15,y1-.15]:
                batch.box(roofgroup,'glass_mid',((x0+x1)/2,y,(floor+eave)/2),
                          (x1-x0-.8,.16,eave-floor-.3))
                for x in range(math.ceil(x0+1),math.floor(x1),2):
                    batch.box(roofgroup,'metal',(x,y,(floor+eave)/2),(.10,.22,eave-floor))
        result.append({'name':label,'footprint':[x0,x1,y0,y1],
                       'floor':floor,'eave':eave,'ridge':ridge})
    return {'roofs':result,'gallery_levels':[24.4,28.8],
            'terrace':33.4,'status':'Source composition study awaiting saved-render and whole-seat validation'}


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
    from r14_seating import angular_rf_return,main_aisles,legacy_outfield,return_aisles_and_rakers,bank_guards_and_backstop
    return {'A01_bank':restore_bank(scene,batch,root),'A02_roofs':pavilion_roofs(scene,batch),
            'A03_lantern':lantern_clearance(scene,batch,root),
            'A04_receivers':bridge_receivers(scene,batch),
            'A05_tower':tower_registration(scene,batch,root),
            'A08_frontage':flush_frontage(scene,batch,root),
            'A09_main_aisles':main_aisles(scene,batch,root),
            'A09_retained_banks':legacy_outfield(scene,batch,root),
            'A09_angular_RF':angular_rf_return(scene,batch,root),
            'A09_returns':return_aisles_and_rakers(scene,batch,root),
            'A09_edge_guards':bank_guards_and_backstop(scene,batch,root),
            'status':'A01/A03 corrections awaiting whole-model verification; A02/A07 connected pavilion study awaits source and circulation validation'}
