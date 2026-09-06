"""Fixed source-view lighting presets; geometry and cameras stay unchanged."""
import math
import bpy

def apply_lighting(scene,name):
    night=name in ['north','bridge','night']
    enhanced=name=='night'
    future=bpy.data.collections.get('D2_Future development')
    if future:future.hide_render=name in ['north','night']
    soccer=bpy.data.collections.get('D2_Proposed soccer stadium')
    if soccer:soccer.hide_render=name in ['north','night']
    fireworks=bpy.data.collections.get('D2_Bridge-view fireworks')
    if fireworks:fireworks.hide_render=name!='bridge'
    for group in ['South source rail links','South source landing buildings','South source medical branding']:
        col=bpy.data.collections.get('D2_'+group)
        if col:col.hide_render=name!='south'
    links=bpy.data.collections.get('D2_Pedestrian rail bridges')
    if links:links.hide_render=name=='south'
    sun=bpy.data.objects['R2_Sun'];sun.data.angle=math.radians(5)
    sun.data.energy=.11 if night else 2.8
    sun.data.color=(.42,.59,1)if night else(1,.73,.43)
    sun.rotation_euler=(math.radians(71 if night else 74),math.radians(-18),math.radians(-58))
    nodes=scene.world.node_tree.nodes;links=scene.world.node_tree.links
    nodes.clear();out=nodes.new('ShaderNodeOutputWorld');background=nodes.new('ShaderNodeBackground');links.new(background.outputs[0],out.inputs['Surface'])
    sky=nodes.new('ShaderNodeTexSky');sky.sky_type='MULTIPLE_SCATTERING';sky.sun_disc=False;sky.sun_elevation=math.radians(5 if night else 12);sky.sun_rotation=math.radians(230);sky.altitude=100;sky.air_density=1.2
    if night:
        # Source views show a cool blue twilight dome, without the strong
        # orange solar lobe produced by the daytime sky model at this azimuth.
        coord=nodes.new('ShaderNodeTexCoord');separate=nodes.new('ShaderNodeSeparateXYZ')
        ramp=nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=0.0
        ramp.color_ramp.elements[0].color=(.08,.13,.23,1)
        ramp.color_ramp.elements[1].position=1.0
        ramp.color_ramp.elements[1].color=(.015,.04,.10,1)
        links.new(coord.outputs['Normal'],separate.inputs[0]);links.new(separate.outputs['Z'],ramp.inputs[0])
        links.new(ramp.outputs['Color'],background.inputs['Color'])
        background.inputs['Strength'].default_value=.55
        if enhanced:
            ramp.color_ramp.elements[0].color=(.028,.055,.115,1)
            ramp.color_ramp.elements[1].position=.45
            ramp.color_ramp.elements[1].color=(.002,.006,.025,1)
            background.inputs['Strength'].default_value=.32
        if name=='bridge':
            ramp.color_ramp.elements[0].color=(.33,.46,.70,1)
            ramp.color_ramp.elements[1].color=(.20,.36,.65,1)
            background.inputs['Strength'].default_value=.80
    else:
        links.new(sky.outputs['Color'],background.inputs['Color']);background.inputs['Strength'].default_value=.065
    for obj in scene.objects:
        if obj.type=='LIGHT'and obj.name.startswith('D2_Field light'):obj.data.energy=160000 if night else 8000
        if obj.type=='LIGHT'and obj.name.startswith('D2_District wash'):obj.data.energy=4500 if night else 0
        if obj.type=='LIGHT'and obj.name.startswith('D2_Walk light'):obj.data.energy=1800 if night else 0
        if obj.type=='LIGHT'and obj.name.startswith('D2_Public light'):obj.data.energy=160 if night else 0
    lit=bpy.data.materials.get('D2_glass_lit')
    if lit:lit.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=.9 if night else .04
    # V7 night pass: boards glow, lit crowns and a faint interior glow behind
    # ordinary glazing so the city and the bowl read after dark.
    for material_name,color,strength in [('screen',(.10,.20,.34,1),.16),('crown_white',(1,.85,.62,1),.55),('glass_grey',(1,.78,.52,1),.09),('glass_blue',(1,.80,.55,1),.07),('glass_bronze',(1,.72,.45,1),.08),('glass_dark',(1,.75,.5,1),.05),('glass_white',(1,.82,.6,1),.09),('glass_green',(1,.80,.55,1),.06),('glass',(1,.78,.52,1),.06)]:
        m=bpy.data.materials.get('D2_'+material_name)
        if m and m.node_tree.nodes.get('Principled BSDF'):
            p=m.node_tree.nodes['Principled BSDF'];p.inputs['Emission Color'].default_value=color;p.inputs['Emission Strength'].default_value=strength if night else 0.0
    for group in ['D2_Future development','D2_Proposed soccer stadium','D2_Bridge-view fireworks','D2_South source rail links','D2_South source landing buildings','D2_South source medical branding','D2_Pedestrian rail bridges']:
        col=bpy.data.collections.get(group)
        if col:col.hide_viewport=col.hide_render
    from r8_night import apply_landmark_windows
    apply_landmark_windows(scene,enhanced)
    scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.10 if night else .05
    scene.render.film_transparent=False
    scene['lighting_preset']=name
