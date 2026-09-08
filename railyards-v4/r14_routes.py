"""Explicit conceptual pedestrian bridge receiving landings and vertical routes."""
import math
import bpy
from mathutils import Vector
from r13_outfield import remove_collection
from r11_circulation import rail
from r3_south_rail_context import LINKS
from r3_reference_projection import source_to_plane


def stair_tower(batch,group,anchor,direction):
    """Eight alternating flights, shared end landings and an adjacent lift shaft.

    Dimensions are inferred for coherent geometry; lift equipment and capacity
    are not simulated. Doors are open model apertures, not decals on a solid box.
    """
    u=Vector((direction.x,direction.y,0)).normalized();v=Vector((-u.y,u.x,0))
    a=Vector(anchor);angle=math.atan2(u.y,u.x)
    def point(x,y,z):
        p=a+u*x+v*y;p.z=z;return p
    def box(mat,x,y,z,w,d,h):batch.box(group,mat,point(x,y,z),(w,d,h),angle)
    # Clear stairwell occupies u[-9,0], v[-2.4,2.4]. Upper landing
    # shares the existing bridge floor; the descent stays outside its span.
    for x in [-8.5,-.5]:
        for y in [-2.45,2.45]:box('metal',x,y,17.0,.22,.22,18)
    for level in range(9):
        z=22-level*1.75
        landing_x=-1 if level%2==0 else -8
        box('concrete',landing_x,0,z-.15,2,5,.3)

        for side in ([-2.4] if level in [0,8] else [-2.4,2.4]):rail(batch,group,point(landing_x-1,side,z),point(landing_x+1,side,z),1.05)
        if level%2:rail(batch,group,point(-9,-2.4,z),point(-9,2.4,z),1.05)
        if level==8:continue
        # Every flight has11 risers of0.159m and0.455m treads.
        start=-2 if level%2==0 else -7;end=-7 if level%2==0 else -2
        side=-1.2 if level%2==0 else 1.2
        for step in range(11):
            x=start+(end-start)*(step+.5)/11;top=z-(step+1)*1.75/11
            box('stone',x,side,top-.10,5/11+.015,2.1,.20)
        corners=[point(start,side-1.05,z-.25),point(start,side+1.05,z-.25),
                 point(end,side+1.05,z-2),point(end,side-1.05,z-2)]
        batch.add(group,'concrete',[tuple(p)for p in corners]+[tuple(p-Vector((0,0,.18)))for p in corners],
                  [(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)])
        for edge in [-1.05,1.05]:
            rail(batch,group,point(start,side+edge,z),point(end,side+edge,z-1.75),1.05)
    box('roof',-4.5,0,26.25,9.5,5.6,.25)
    box('paving',-1,0,7.9,3,5.6,.2)
    # Lift beside the top/ground landing, three solid shaft sides and open
    # doorway at y2.4 on each served landing. Floors stop at the clear well.
    for y in [5.65]:box('glass',-1,y,17,3,.14,18)
    for x in [-2.5,.5]:box('metal',x,4.1,17,.16,3.2,18)
    # Front remains open at served landings; paired piers and lintels frame it.
    for x in [-2.35,.35]:box('metal',x,2.5,17,.3,.22,18)
    for z in [8,22]:
        box('metal',-1,4.1,z-.12,2.6,3,.24)
        box('metal',-1,2.5,z+2.6,2.5,.25,.22)
    return {'anchor':list(a),'direction':list(u),'top':22,'ground':8,
            'flights':8,'risers_per_flight':11,'rise':1.75/11,'tread':5/11,
            'lift':'Conceptual shaft and landing apertures; no mechanical simulation'}


def open_receiver_enclosures(scene,records):
    """Carve the new receiving cores into retained facade/landing masses."""
    candidates=[o for o in scene.objects if o.type=='MESH' and o.data.polygons and
        any(o.name.startswith(prefix) for prefix in ['D2_Stadium envelope ',
        'D2_Medical replacement ','D2_RF structure ','D2_South source landing buildings '])]
    import bmesh
    for obj in candidates:
        bm=bmesh.new();bm.from_mesh(obj.data)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
    changed=[]
    for record in records:
        a,b=[Vector(p) for p in record['ends']];u=(b-a).normalized();mid=(a+b)/2;mid.z=24.15
        bpy.ops.mesh.primitive_cube_add(size=1,location=mid)
        corridor=bpy.context.object;corridor.name='V14 real crossing hall aperture'
        corridor.dimensions=((b-a).length+1,6.2,4.4);corridor.rotation_euler.z=math.atan2(u.y,u.x)
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        for obj in candidates:
            modifier=obj.modifiers.new(corridor.name,'BOOLEAN');modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.use_self=True;modifier.object=corridor
            bpy.context.view_layer.objects.active=obj;bpy.ops.object.modifier_apply(modifier=modifier.name)
        bpy.data.objects.remove(corridor,do_unlink=True)
        for end in ['west','east']:
            receiver=record[end];a=Vector(receiver['anchor']);u=Vector(receiver['direction']);v=Vector((-u.y,u.x,0))
            center=a-u*4.5+v*1.65;center.z=17.15
            bpy.ops.mesh.primitive_cube_add(size=1,location=center)
            cutter=bpy.context.object;cutter.name=f"V14 crossing {record['crossing']} {end} receiving aperture"
            cutter.dimensions=(9.15,8.5,18.4);cutter.rotation_euler.z=math.atan2(u.y,u.x)
            bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
            bpy.context.view_layer.update()
            world=[cutter.matrix_world@Vector(p)for p in cutter.bound_box]
            low=[min(p[i]for p in world)for i in range(3)];high=[max(p[i]for p in world)for i in range(3)]
            for obj in candidates:
                points=[obj.matrix_world@Vector(p)for p in obj.bound_box]
                if any(max(p[i]for p in points)<low[i] or min(p[i]for p in points)>high[i]for i in range(3)):continue
                modifier=obj.modifiers.new(cutter.name,'BOOLEAN');modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.use_self=True;modifier.object=cutter
                bpy.context.view_layer.objects.active=obj;bpy.ops.object.modifier_apply(modifier=modifier.name)
                changed.append({'crossing':record['crossing'],'end':end,'object':obj.name})
            bpy.data.objects.remove(cutter,do_unlink=True)
    return changed


def bridge_receivers(scene,batch):
    remove_collection('D2_South source rail links')
    records=[]
    for number,pixels in enumerate(LINKS,1):
        roof=[Vector(source_to_plane(scene,bpy.data.objects['R2_south'],p,(5000,3333),26.2))for p in pixels]
        a=(roof[0]+roof[-1])/2;b=(roof[1]+roof[2])/2;u=(b-a).normalized()
        group=f'V14 Rail crossing {number}'
        batch.prism(group,'concrete',[tuple(p[:2])for p in roof],21.6,22)
        batch.prism(group,'roof',[tuple(p[:2])for p in roof],26.1,26.35)
        # Long sides only. Old full-end glazing made every link a sealed box.
        for left,right in [(roof[0],roof[1]),(roof[3],roof[2])]:
            for height in [22.1,26.05]:
                batch.line(group,'metal',[(left.x,left.y,height),(right.x,right.y,height)],.10,sides=6)
            count=math.ceil((right-left).length/2.5)
            for i in range(count+1):
                p=left.lerp(right,i/count)
                batch.cylinder(group,'metal',(p.x,p.y,22),(p.x,p.y,26.2),.10,sides=6)
            batch.quad(group,'glass',[(left.x,left.y,22.1),(right.x,right.y,22.1),tuple(right),tuple(left)])
        west=stair_tower(batch,group,a,u)
        # East receiver extends beyond the bridge end, so the bridge slab
        # does not seal the first flight beneath a low soffit.
        east=stair_tower(batch,group,b,-u)
        records.append({'crossing':number,'west':west,'east':east,'ends':[list(a),list(b)]})
    opened=open_receiver_enclosures(scene,records)
    scene['v14_receiver_apertures']=str(opened)
    scene['v14_transport_variant']='One physical B6-based set of three crossings in all camera presets. Conflicting older north traces preserved in V13 baseline, hidden in V14. Receiving stairs/lifts are inferred.'
    legacy=bpy.data.collections.get('D2_Pedestrian rail bridges')
    if legacy:legacy.hide_render=True;legacy.hide_viewport=True
    return records
