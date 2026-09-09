"""Requested pinwheel addition; ornamental departure from the concept artwork."""
import math
import bpy
from mathutils import Vector


def build(scene, batch, spec):
    top = Vector(spec['anchors']['cf_scoreboard_top'])
    tangent = Vector((math.cos(math.radians(135)), math.sin(math.radians(135)), 0))
    normal = Vector((tangent.y, -tangent.x, 0))
    colors = [('red', (0.8, 0.025, 0.035, 1)), ('gold', (1, 0.53, 0.045, 1)),
              ('green', (0.06, 0.48, 0.19, 1)), ('blue', (0.035, 0.24, 0.85, 1))]
    for name, color in colors:
        key = 'pinwheel_' + name
        material = bpy.data.materials.new('D2_' + key)
        material.diffuse_color = color
        material.use_nodes = True
        shader = material.node_tree.nodes.get('Principled BSDF')
        shader.inputs['Base Color'].default_value = color
        shader.inputs['Metallic'].default_value = .25
        shader.inputs['Roughness'].default_value = .3
        shader.inputs['Emission Color'].default_value = color
        shader.inputs['Emission Strength'].default_value = .35
        batch.materials[key] = material
    group = 'V15 Scoreboard pinwheels'
    centers = []
    for u in [-10.5, -3.5, 3.5, 10.5]:
        center = top + tangent * u + Vector((0, 0, 5.8))
        centers.append(list(center))
        batch.cylinder(group, 'metal', center - Vector((0, 0, 3.0)), center, .13, sides=12)
        for i in range(8):
            angle = math.tau * i / 8
            def point(radius, offset):
                a = angle + offset
                return center + tangent * (radius * math.cos(a)) + Vector((0, 0, radius * math.sin(a)))
            face = [point(.35, 0), point(2.55, .05), point(2.1, .57), point(.8, .8)]
            # Real shallow solid blades show the motif from both board faces.
            verts = [tuple(p + normal * d) for d in [-.09, .09] for p in face]
            batch.add(group, 'pinwheel_' + colors[i % 4][0], verts,
                      [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)])
        batch.cylinder(group, 'white', center - normal * .15, center + normal * .15, .4, sides=20)
    return {'count': 4, 'centers': centers, 'radius_m': 2.55,
            'basis': 'User-requested decorative departure; positions and size inferred. Static pinwheels.'}


def align_scoreboards(scene, batch, spec):
    """Use actual saved-screen datums; old scene-spec heights are stale."""
    screen = bpy.data.objects['D2_Scoreboards screen']
    cf_vertices = [screen.matrix_world @ v.co for v in screen.data.vertices if v.co.y > 100]
    actual_top = max(p.z for p in cf_vertices)
    spec['anchors']['cf_scoreboard_top'][2] = actual_top
    # RF gallery canopy (20.7) intersects the low edge (19.3) of the RF
    # display. Lift its separate board assembly two metres; CF stays fixed.
    from mathutils import Vector
    import bmesh
    changed = []
    for obj in bpy.data.collections['D2_Scoreboards'].objects:
        if obj.type == 'MESH':
            bm = bmesh.new();bm.from_mesh(obj.data)
            seen = set();count = 0
            for vertex in bm.verts:
                if vertex in seen:continue
                stack = [vertex];seen.add(vertex);component = []
                while stack:
                    v = stack.pop();component.append(v)
                    for edge in v.link_edges:
                        other = edge.other_vert(v)
                        if other not in seen:seen.add(other);stack.append(other)
                center = sum((v.co for v in component), Vector()) / len(component)
                if center.x > 95 and 10 < center.y < 70:
                    minimum = min(v.co.z for v in component)
                    for v in component:
                        if minimum > 17 or v.co.z > 18:v.co.z += 2.0
                    count += 1
            bm.to_mesh(obj.data);bm.free()
            if count:changed.append({'object':obj.name,'components':count})
        elif obj.name.startswith('D2_rf_scoreboard_top'):
            obj.location.z += 2.0
    for obj in scene.objects:
        if obj.type == 'LIGHT' and obj.name.startswith('D2_Field light RF'):
            obj.location.z += 2.0
    return {'centerfield_screen_top_m':actual_top, 'centerfield_screen_bottom_m':min(p.z for p in cf_vertices),
            'centerfield_height_unchanged':True, 'rightfield_lift_m':2.0,
            'rightfield_screen_bottom_m':21.3, 'rightfield_canopy_m':20.7,
            'basis':'Measured saved scene supersedes stale scene-spec board Z; gallery roof must clear active screen.',
            'changed':changed}
