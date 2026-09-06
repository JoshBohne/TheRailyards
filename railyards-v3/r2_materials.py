"""Physically scaled procedural surfaces; no external asset dependency."""
import bpy

def create_materials():
    result={}
    def make(name,color,rough=.7,metal=0,emission=0):
        m=bpy.data.materials.get('D2_'+name) or bpy.data.materials.new('D2_'+name);m.use_nodes=True;m.diffuse_color=(*color,1)
        n=m.node_tree.nodes;n.clear();p=n.new('ShaderNodeBsdfPrincipled');out=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(p.outputs['BSDF'],out.inputs['Surface'])
        p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
        if emission:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
        result[name]=m;return m,p
    palette={
        'brick':((.33,.105,.048),.79,0),'brick_light':((.43,.17,.075),.75,0),'brick_dark':((.205,.07,.034),.8,0),
        'stone':((.62,.55,.42),.76,0),'paving':((.43,.44,.40),.86,0),'concrete':((.49,.51,.48),.78,0),'asphalt':((.047,.057,.057),.94,0),
        'rust_steel':((.18,.085,.037),.60,.65),'canopy':((.035,.047,.057),.78,.12),'roof':((.075,.11,.115),.43,.7),'metal':((.027,.044,.044),.38,.7),'aluminum':((.54,.58,.57),.37,.8),'rail':((.16,.19,.19),.31,.75),
        'glass':((.075,.13,.15),.18,.08),'glass_lit':((.51,.32,.14),.24,.05),'interior':((.05,.043,.03),.9,0),
        'seat':((.022,.061,.047),.56,.05),'field':((.025,.115,.009),.92,0),'field_light':((.047,.153,.013),.88,0),'lawn':((.11,.21,.035),.95,0),'soil':((.43,.235,.10),.95,0),'warning':((.28,.17,.075),.93,0),
        'white':((.86,.87,.79),.52,0),'yellow':((.97,.69,.075),.43,.1),'screen':((.008,.015,.019),.54,0),
        'bark':((.17,.13,.085),.97,0),'foliage':((.10,.205,.028),.75,0),'leaf_light':((.17,.29,.046),.74,0),'leaf_dark':((.052,.12,.026),.83,0),
        'water':((.018,.065,.075),.16,.1),'skin':((.57,.36,.21),.72,0),'navy':((.012,.02,.037),.75,0),'cloth_gray':((.25,.28,.28),.85,0),'cloth_white':((.77,.78,.73),.85,0),'cloth_black':((.024,.029,.028),.85,0),'cloth_red':((.41,.06,.034),.8,0),'cloth_blue':((.045,.115,.24),.8,0),'purple':((.44,.14,.41),.6,0),
    }
    for name,(color,rough,metal)in palette.items():make(name,color,rough,metal)
    make('lamp',(1,.72,.34),.3,0,5);make('stadium_lamp',(1,.93,.77),.3,0,12);make('screen_ink',(.86,.89,.82),.5,0,.7)
    make('purple_sign',(.59,.09,.48),.5,0,2.0)
    make('glass_dim',(.12,.105,.072),.26,.10,.10)
    make('glass_mid',(.36,.25,.12),.25,.06,.45)
    result['glass'].node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=.35
    result['glass'].node_tree.nodes.get('Principled BSDF').inputs['IOR'].default_value=1.46
    p=result['glass_lit'].node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(1,.57,.21,1);p.inputs['Emission Strength'].default_value=.45
    for name in ['brick','brick_light','brick_dark']:
        m=result[name];n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');base=m.diffuse_color[:3]
        uv=n.new('ShaderNodeTexCoord');brick=n.new('ShaderNodeTexBrick');brick.inputs['Scale'].default_value=1;brick.inputs['Mortar Size'].default_value=.011;brick.inputs['Mortar Smooth'].default_value=.006;brick.inputs['Brick Width'].default_value=.23;brick.inputs['Row Height'].default_value=.076
        brick.inputs['Color1'].default_value=(*[c*.73 for c in base],1);brick.inputs['Color2'].default_value=(*[min(c*1.24,1)for c in base],1);brick.inputs['Mortar'].default_value=(.26,.23,.175,1)
        l.new(uv.outputs['UV'],brick.inputs['Vector']);l.new(brick.outputs['Color'],p.inputs['Base Color'])
        bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.3;bump.inputs['Distance'].default_value=.022;l.new(brick.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],p.inputs['Normal'])
    for name,scale,strength,distance in [('concrete',3,.18,.018),('paving',4,.16,.018),('asphalt',15,.28,.025),('stone',4,.11,.012),('field',18,.14,.012),('field_light',18,.14,.012),('lawn',10,.45,.055),('bark',7,.6,.06),('water',.65,.2,.22)]:
        m=result[name];n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=3
        coord=n.new('ShaderNodeTexCoord');l.new(coord.outputs['Object'],noise.inputs['Vector']);bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=strength;bump.inputs['Distance'].default_value=distance;l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],p.inputs['Normal'])
    for name in ['foliage','leaf_light','leaf_dark']:
        m=result[name];n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');p.inputs['Subsurface Weight'].default_value=.06
        translucent=n.new('ShaderNodeBsdfTranslucent');translucent.inputs[0].default_value=m.diffuse_color;mix=n.new('ShaderNodeMixShader');mix.inputs[0].default_value=.18;l.new(p.outputs[0],mix.inputs[1]);l.new(translucent.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],n.get('Material Output').inputs['Surface'])
    return result
