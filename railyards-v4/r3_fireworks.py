"""Native event staging visible only in the published bridge artwork."""
import math,random
import bpy
from mathutils import Vector
from r3_reference_projection import source_to_plane


def build_fireworks(scene,spec,batch,materials):
    rng=random.Random(9206);camera=bpy.data.objects['R2_bridge']
    for name,color in [('pearl',(.85,.91,1)),('gold',(1,.66,.30)),('rose',(1,.44,.33))]:
        mat=bpy.data.materials.new('D2_Firework '+name);mat.use_nodes=True
        shader=mat.node_tree.nodes.get('Principled BSDF')
        shader.inputs['Base Color'].default_value=(*color,1)
        shader.inputs['Emission Color'].default_value=(*color,1);shader.inputs['Emission Strength'].default_value=3.5
        materials['firework_'+name]=mat
    for pixel,height,pixel_radius in [((495,300),150,68),((561,329),132,59),((524,395),98,32)]:
        center=Vector(source_to_plane(scene,camera,pixel,(1440,959),height))
        distance=(camera.location-center).length
        radius=pixel_radius*distance*36/(camera.data.lens*1440)
        for i in range(70):
            direction=Vector((rng.uniform(-1,1),rng.uniform(-1,1),rng.uniform(-1,1)))
            if direction.length<.05:continue
            direction.normalize();length=radius*rng.uniform(.6,1.05)
            points=[]
            for k in range(9):
                t=.28+k*.09
                p=center+direction*length*t;p.z-=radius*.32*t*t
                points.append(tuple(p))
            material='firework_'+rng.choices(['pearl','gold','rose'],[.65,.22,.13])[0]
            batch.line('Bridge-view fireworks',material,points,rng.uniform(.045,.095),sides=4)
    scene['fireworks_note']='Three native strand bursts registered to bridge source at pixels495,300 /561,329 /524,395. Event staging only; depths, trajectories and sizes are inferred. Hidden in other views.'
