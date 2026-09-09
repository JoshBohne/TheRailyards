"""Requested pinwheel addition; ornamental departure from the concept artwork."""
import math
import bpy
from mathutils import Vector


def build(scene, batch, spec):
    """Seven pinwheels on a chevron above the center-field board, after the
    2026-09-08 reference: blue, red, green, yellow, green, red, blue, each on a
    dark pillar with a lit stripe in its own colour, the centre wheel highest."""
    top = Vector(spec['anchors']['cf_scoreboard_top'])
    tangent = Vector((math.cos(math.radians(135)), math.sin(math.radians(135)), 0))
    normal = Vector((tangent.y, -tangent.x, 0))
    colors = {'red': (0.85, 0.03, 0.04, 1), 'yellow': (1, 0.82, 0.05, 1),
              'green': (0.05, 0.6, 0.18, 1), 'blue': (0.04, 0.3, 0.95, 1)}
    for name, color in colors.items():
        for key, strength in [('pinwheel_' + name, .25), ('pinlight_' + name, 6.0)]:
            material = bpy.data.materials.new('D2_' + key)
            material.diffuse_color = color
            material.use_nodes = True
            shader = material.node_tree.nodes.get('Principled BSDF')
            shader.inputs['Base Color'].default_value = color
            shader.inputs['Metallic'].default_value = .2 if strength < 1 else 0
            shader.inputs['Roughness'].default_value = .3
            shader.inputs['Emission Color'].default_value = color
            shader.inputs['Emission Strength'].default_value = strength
            batch.materials[key] = material
    group = 'V15 Scoreboard pinwheels'
    order = ['blue', 'red', 'green', 'yellow', 'green', 'red', 'blue']
    spacing = 4.9
    radius = 2.0
    centers = []
    for index, name in enumerate(order):
        u = (index - 3) * spacing
        lift = 3.2 - abs(index - 3) * 0.75  # chevron: centre highest
        base = top + tangent * u + Vector((0, 0, 0.6))
        center = base + Vector((0, 0, lift + radius + 0.9))
        centers.append(list(center))
        # Dark pillar with a lit stripe on both faces, like the reference posts.
        pillar_h = center.z - base.z
        batch.box(group, 'cloth_black', (base.x, base.y, base.z + pillar_h / 2), (1.5, .7, pillar_h), math.radians(135))
        for side in (-1, 1):
            stripe = base + normal * (side * .37)
            batch.box(group, 'pinlight_' + name, (stripe.x, stripe.y, base.z + pillar_h / 2 - .2), (.7, .04, pillar_h - 1.0), math.radians(135))
        batch.box(group, 'pinwheel_' + name, (base.x, base.y, base.z + pillar_h - .15), (1.3, .7, .3), math.radians(135))
        # White rim ring, eight blades alternating colour and white, white hub.
        for i in range(24):
            a0 = math.tau * i / 24; a1 = math.tau * (i + 1) / 24
            ring = [center + tangent * (r * math.cos(a)) + Vector((0, 0, r * math.sin(a))) for a in (a0, a1) for r in (radius, radius + .22)]
            verts = [tuple(p + normal * d) for d in (-.12, .12) for p in [ring[0], ring[1], ring[3], ring[2]]]
            batch.add(group, 'white', verts, [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)])
        for i in range(8):
            angle = math.tau * i / 8
            def point(r, offset):
                a = angle + offset
                return center + tangent * (r * math.cos(a)) + Vector((0, 0, r * math.sin(a)))
            face = [point(.3, 0), point(radius - .05, .06), point(radius * .86, .5), point(radius * .55, .78), point(.5, .82)]
            verts = [tuple(p + normal * d) for d in (-.08, .08) for p in face]
            batch.add(group, 'pinwheel_' + name if i % 2 == 0 else 'white', verts,
                      [(4, 3, 2, 1, 0), (5, 6, 7, 8, 9), (0, 1, 6, 5), (1, 2, 7, 6), (2, 3, 8, 7), (3, 4, 9, 8), (4, 0, 5, 9)])
        batch.cylinder(group, 'white', center - normal * .16, center + normal * .16, .34, sides=20)
    return {'count': 7, 'order': order, 'centers': centers, 'radius_m': radius, 'spacing_m': spacing,
            'basis': 'Seven-pinwheel reference supplied 2026-09-08; chevron heights, pillar stripes and size inferred. Static pinwheels.'}


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
