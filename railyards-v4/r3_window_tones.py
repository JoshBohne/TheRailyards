"""Sample source pane brightness into native materials, without photo projection.

Only six restrained pane tones are recovered. Geometry, lighting, signs and
occlusion remain native Blender elements; the photograph is never rendered
onto the building. Hidden window patterns remain reconstructed.
"""
from pathlib import Path
import bisect
import bpy
import numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view


def apply_window_tones(scene):
    source=Path(__file__).parent.parent/'reconstruction-references/aecom-north-aerial.png'
    image=bpy.data.images.load(str(source),check_existing=True)
    pixels=np.empty(len(image.pixels),dtype=np.float32);image.pixels.foreach_get(pixels)
    pixels=pixels.reshape(image.size[1],image.size[0],4)
    palette=[(.035,.047,.056),(.075,.09,.09),(.14,.14,.11),(.26,.22,.15),(.43,.34,.21),(.66,.52,.34)]
    materials=[]
    for i,color in enumerate(palette):
        name='D2_Source pane tone '+str(i)
        m=bpy.data.materials.get(name)or bpy.data.materials.new(name);m.use_nodes=True
        m.diffuse_color=(*color,1)
        p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1)
        p.inputs['Roughness'].default_value=.32;p.inputs['Metallic'].default_value=.22
        p.inputs['Emission Color'].default_value=(*color,1)
        p.inputs['Emission Strength'].default_value=[.02,.05,.12,.24,.4,.65][i]
        materials.append(m)
    camera=bpy.data.objects['R2_north'];old_size=(scene.render.resolution_x,scene.render.resolution_y)
    scene.render.resolution_x,scene.render.resolution_y=1944,1294
    targets=['Medical replacement','Medical wing','North entertainment hall','Left field pavilion','Pavilion hall connector','Centerfield restaurant replacement']
    count=0
    for obj in scene.objects:
        if obj.type!='MESH'or 'glass'not in obj.name or not any(obj.name.startswith('D2_'+name+' ')for name in targets):continue
        # These owning modules emit facade panes as independent eight-vertex,
        # six-face boxes. Do not apply this contract to mixed primitive meshes.
        mesh=obj.data
        if len(mesh.vertices)%8 or len(mesh.polygons)!=len(mesh.vertices)//8*6:continue
        start=len(mesh.materials)
        for material in materials:mesh.materials.append(material)
        for k in range(len(mesh.vertices)//8):
            center=sum((mesh.vertices[k*8+j].co for j in range(8)),Vector())/8
            uv=world_to_camera_view(scene,camera,obj.matrix_world@center)
            x,y=int(uv.x*image.size[0]),int(uv.y*image.size[1])
            if not 1<=x<image.size[0]-1 or not 1<=y<image.size[1]-1:continue
            brightness=float(np.median(pixels[y-1:y+2,x-1:x+2,:3]))
            tone=bisect.bisect([.17,.26,.38,.52,.70],brightness)
            for face in mesh.polygons[k*6:k*6+6]:face.material_index=start+tone
            count+=1
    scene.render.resolution_x,scene.render.resolution_y=old_size
    scene['source_sampled_window_panes']=count
    scene['facade_material_note']='Native window meshes use six tones sampled from source-image brightness; no photograph is projected onto final geometry. Hidden pane patterns remain inferred.'
    if image.users==0:bpy.data.images.remove(image)
    return count
