"""Native riverfront practical lights and restrained distance atmosphere."""
import bpy,math,random
from mathutils import Vector
from r3_public_realm import deck_z,quay_z,LOWER_Z
from r3_reference_projection import source_to_plane


def build_environment(scene,spec,batch,materials):
    # The conspicuous yellow passenger boat in the north source anchors
    # river scale; deck arrangement is a visible-detail reconstruction.
    x,y,_=source_to_plane(scene,bpy.data.objects['R2_north'],(478,1032),(1944,1294),.4)
    hull=[(x-3,y-11),(x+3,y-11),(x+3.6,y+7),(x+2,y+11),(x,y+12),(x-2,y+11),(x-3.6,y+7)]
    batch.prism('Yellow river cruise boat','yellow',hull,.3,1.8)
    batch.box('Yellow river cruise boat','glass',(x,y,2.6),(5.6,16,1.6))
    batch.box('Yellow river cruise boat','white',(x,y,3.45),(6.1,17.0,.18))
    batch.box('Yellow river cruise boat','yellow',(x,y-4,4.1),(4.0,5.0,1.3))
    for side in [-1,1]:
        batch.line('Yellow river cruise boat','metal',[(x+side*2.9,y-8,4.3),(x+side*2.9,y+8,4.3)],.035)
        for dy in range(-7,9,2):
            batch.cylinder('Yellow river cruise boat','white',(x+side*2.9,y+dy,3.5),(x+side*2.9,y+dy,4.3),.035,sides=6)
    for dx in [-1.7,1.7]:
        for dy in range(0,8,2):batch.box('Yellow river cruise boat','white',(x+dx,y+dy,3.9),(.7,.6,.6))
    # Vehicle sizes and lane spacing follow the foreground bridge source;
    # exact individual positions and paint colors are reconstructed.
    rng=random.Random(2026)
    for lane,y in enumerate([308.3,311.4,314.5,317.6,320.7,323.8]):
        for i in range(9):
            x=-245+i*62+rng.uniform(-13,13);z=14.35
            body=['white','metal','aluminum','navy'][(i+lane)%4]
            batch.box('Roosevelt traffic',body,(x,y,z+.65),(4.5,1.82,.75))
            batch.box('Roosevelt traffic','glass',(x-.10,y,z+1.20),(2.4,1.64,.63))
            batch.box('Roosevelt traffic',body,(x-.10,y,z+1.53),(2.35,1.67,.12))
            for dx in [-1.4,1.4]:
                for dy in [-.90,.90]:
                    batch.cylinder('Roosevelt traffic','metal',(x+dx,y+dy-.09,z+.38),(x+dx,y+dy+.09,z+.38),.34,sides=12)
            for dy in [-.64,.64]:
                direction=1 if lane<3 else -1
                batch.box('Roosevelt traffic','lamp',(x+direction*2.26,y+dy,z+.68),(.03,.36,.17))
    col=batch.collection('Public lighting')
    positions=[(119,y,quay_z(y))for y in range(-120,301,22)]
    positions += [(x,y,deck_z(y))for x,y in [(35,188),(65,218),(37,239),(67,270),(42,295)]]
    for k,(x,y,z)in enumerate(positions):
        batch.cylinder('Riverfront lamps','metal',(x,y,z),(x,y,z+4.5),.065,.04,sides=7)
        batch.box('Riverfront lamps','lamp',(x,y,z+4.5),(.48,.48,.16))
        data=bpy.data.lights.new('D2_Public light '+str(k),'POINT');data.energy=160;data.color=(1,.68,.34);data.shadow_soft_size=.25
        obj=bpy.data.objects.new(data.name,data);col.objects.link(obj);obj.location=(x,y,z+4.3)
    # Source festoon strands parallel the active river-facing stadium arcade.
    for y in range(-120,125,18):
        a=Vector((116,y,9.4));b=Vector((116,y+18,9.4))
        chain=[]
        for i in range(25):
            t=i/24;p=a.lerp(b,t);p.z-=.55*math.sin(math.pi*t);chain.append(tuple(p))
            if i%2==0:batch.ellipsoid('Riverfront festoons','lamp',p,(.07,.07,.09),6,4)
        batch.line('Riverfront festoons','metal',chain,.012,sides=4)
    # Broad arch illumination visible in the twilight reference; fixture
    # mounting is unresolved, so only the architectural light is inferred.
    data=bpy.data.lights.new('D2_District wash Roosevelt arch','AREA')
    data.shape='RECTANGLE';data.size=28;data.size_y=4;data.energy=3000;data.color=(.8,.9,1)
    light=bpy.data.objects.new(data.name,data);col.objects.link(light);light.location=(160,341,12)
    light.rotation_euler=(Vector((160,331,7))-light.location).to_track_quat('-Z','Y').to_euler()
    material=bpy.data.materials.get('D2_Atmosphere')or bpy.data.materials.new('D2_Atmosphere')
    material.use_nodes=True;nodes=material.node_tree.nodes;nodes.clear()
    out=nodes.new('ShaderNodeOutputMaterial');scatter=nodes.new('ShaderNodeVolumeScatter')
    scatter.inputs['Color'].default_value=(.53,.64,.78,1)
    scatter.inputs['Density'].default_value=.000035
    scatter.inputs['Anisotropy'].default_value=.2
    material.node_tree.links.new(scatter.outputs['Volume'],out.inputs['Volume'])
    materials['atmosphere']=material
    batch.box('Distance atmosphere','atmosphere',(0,1500,500),(16000,16000,1000))
    scene['atmosphere_note']='Native finite volume: density0.000035/m; geographically distant landmark contrast reduces naturally.'
