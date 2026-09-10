"""Requested pinwheel addition; ornamental departure from the concept artwork."""
import json
import math
import bpy
from mathutils import Vector


ORDER = ['blue', 'red', 'green', 'yellow', 'green', 'red', 'blue']
COLORS = {'red': (0.9, 0.03, 0.05, 1), 'yellow': (1, 0.8, 0.05, 1),
          'green': (0.05, 0.75, 0.2, 1), 'blue': (0.05, 0.28, 1.0, 1)}
SPACING = 4.9
RADIUS = 1.9


def _axes(spec):
    top = Vector(spec['anchors']['cf_scoreboard_top'])
    tangent = Vector((math.cos(math.radians(135)), math.sin(math.radians(135)), 0))
    normal = Vector((tangent.y, -tangent.x, 0))
    return top, tangent, normal


def build(scene, batch, spec):
    """Seven LED pinwheels on a chevron above the center-field board, after the
    2026-09-08 references: blue, red, green, yellow, green, red, blue candy
    discs on lit posts of the same colour, centre highest, with spark strands.
    Discs are built one group per wheel so ``animate`` can spin them."""
    import random
    rng = random.Random(1508)
    top, tangent, normal = _axes(spec)
    for name, color in COLORS.items():
        for key, strength, metallic in [('pinwheel_' + name, 2.5, 0.0), ('pinlight_' + name, 5.0, 0.0)]:
            material = bpy.data.materials.new('D2_' + key)
            material.diffuse_color = color
            material.use_nodes = True
            shader = material.node_tree.nodes.get('Principled BSDF')
            shader.inputs['Base Color'].default_value = color
            shader.inputs['Metallic'].default_value = metallic
            shader.inputs['Roughness'].default_value = .4
            shader.inputs['Emission Color'].default_value = color
            shader.inputs['Emission Strength'].default_value = strength
            batch.materials[key] = material
    for key, color, strength in [('pinled_white', (1, 1, 1, 1), 2.0), ('pinspark', (1, .85, .55, 1), 6.0)]:
        material = bpy.data.materials.new('D2_' + key)
        material.diffuse_color = color
        material.use_nodes = True
        shader = material.node_tree.nodes.get('Principled BSDF')
        shader.inputs['Base Color'].default_value = color
        shader.inputs['Emission Color'].default_value = color
        shader.inputs['Emission Strength'].default_value = strength
        batch.materials[key] = material
    frame = 'V15 Scoreboard pinwheel posts'
    sparks = 'V15 Scoreboard pinwheel fireworks'
    centers = []
    for index, name in enumerate(ORDER):
        u = (index - 3) * SPACING
        lift = 3.4 - abs(index - 3) * 0.8  # chevron: centre highest
        base = top + tangent * u + Vector((0, 0, 0.6))
        center = base + Vector((0, 0, lift + RADIUS + 0.7))
        centers.append([center.x, center.y, center.z])
        post_h = center.z - base.z
        # Lit post: translucent colour housing between two dark rails, a dark
        # cap above the disc, like the LED posts at the ballpark.
        batch.box(frame, 'pinlight_' + name, (base.x, base.y, base.z + post_h / 2), (.62, .34, post_h), math.radians(135))
        for side in (-1, 1):
            rail = base + tangent * (side * .42)
            batch.box(frame, 'cloth_black', (rail.x, rail.y, base.z + post_h / 2), (.22, .42, post_h), math.radians(135))
        cap = center + Vector((0, 0, RADIUS + .35))
        batch.box(frame, 'cloth_black', (cap.x, cap.y, cap.z), (1.0, .5, .5), math.radians(135))
        batch.cylinder(frame, 'cloth_black', center - normal * .3, center + normal * .3, .2, sides=12)
        # LED candy disc: sixteen swirled wedges alternating colour and white,
        # inside a dark rim; one group per wheel so it can be animated.
        group = f'V15 Pinwheel {index} disc'
        for i in range(16):
            a0 = math.tau * i / 16
            def point(r, offset):
                a = a0 + offset + (r / RADIUS) * .55  # swirl grows with radius
                return center + tangent * (r * math.cos(a)) + Vector((0, 0, r * math.sin(a)))
            face = [point(.22, 0), point(RADIUS, 0), point(RADIUS, math.tau / 16), point(.22, math.tau / 16)]
            verts = [tuple(p + normal * d) for d in (-.10, .10) for p in face]
            batch.add(group, 'pinwheel_' + name if i % 2 == 0 else 'pinled_white', verts,
                      [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)])
        for i in range(24):
            a0 = math.tau * i / 24; a1 = math.tau * (i + 1) / 24
            ring = [center + tangent * (r * math.cos(a)) + Vector((0, 0, r * math.sin(a))) for a in (a0, a1) for r in (RADIUS, RADIUS + .28)]
            verts = [tuple(p + normal * d) for d in (-.14, .14) for p in [ring[0], ring[1], ring[3], ring[2]]]
            batch.add(group, 'cloth_black', verts, [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)])
        # Spark strands rising from the cap, the way the board fires on a
        # home run; static strands, event staging only.
        for _ in range(14):
            spread = Vector((rng.uniform(-.35, .35), rng.uniform(-.35, .35), 1)).normalized()
            height = rng.uniform(4.5, 9.5)
            points = []
            for k in range(8):
                s = k / 7
                p = cap + spread * height * s + tangent * (rng.uniform(-.08, .08))
                p.z -= 1.2 * s * s
                points.append(tuple(p))
            batch.line(sparks, 'pinspark', points, rng.uniform(.03, .06), sides=4)
    scene['v15_pinwheel_centers'] = json.dumps(centers)
    scene['v15_pinwheel_normal'] = json.dumps([normal.x, normal.y, normal.z])
    return {'count': 7, 'order': ORDER, 'centers': centers, 'radius_m': RADIUS, 'spacing_m': SPACING,
            'basis': 'Seven-pinwheel references supplied 2026-09-08; LED discs, lit posts, chevron heights and spark strands inferred. Discs spin via animate().'}


def _fcurves(obj):
    """F-curves of an object's action across the legacy and slotted (5.x) APIs."""
    data = obj.animation_data
    if not data or not data.action:
        return []
    action = data.action
    if hasattr(action, 'fcurves'):
        return list(action.fcurves)
    curves = []
    for layer in action.layers:
        for strip in layer.strips:
            bag = strip.channelbag(data.action_slot) if data.action_slot else None
            if bag:
                curves.extend(bag.fcurves)
    return curves


def animate(scene):
    """Spin each disc about the board normal: one turn every two seconds,
    alternating direction, looping over the scene frame range."""
    centers = json.loads(scene['v15_pinwheel_centers'])
    normal = Vector(json.loads(scene['v15_pinwheel_normal']))
    fps = scene.render.fps or 24
    frames = max(1, scene.frame_end - scene.frame_start)
    spun = []
    for index, center in enumerate(centers):
        center = Vector(center)
        for obj in scene.objects:
            if not obj.name.startswith(f'D2_V15 Pinwheel {index} disc'):
                continue
            for vertex in obj.data.vertices:
                vertex.co -= center
            obj.location = center
            obj.rotation_mode = 'AXIS_ANGLE'
            turns = frames / fps / 2.0 * (1 if index % 2 == 0 else -1)
            obj.rotation_axis_angle = (0.0, normal.x, normal.y, normal.z)
            obj.keyframe_insert('rotation_axis_angle', frame=scene.frame_start)
            obj.rotation_axis_angle = (math.tau * turns, normal.x, normal.y, normal.z)
            obj.keyframe_insert('rotation_axis_angle', frame=scene.frame_end)
            for curve in _fcurves(obj):
                for point in curve.keyframe_points:
                    point.interpolation = 'LINEAR'
            spun.append(obj.name)
    return {'objects': spun, 'turns_per_second': 0.5, 'frames': frames}


def center_cf_on_terrace(scene, spec):
    """2026-09-08: the CF board straddled the terrace edge, so one leg hung
    over the 13.4 m court. Measure the terrace run under the board line and
    slide the whole board assembly to its centre; pinwheels follow the anchor."""
    import bmesh
    top, tangent, normal = _axes(spec)
    # Must run after r15_circulation has cut the terrace down to the 13.4 m
    # court on the +u side; the baseline terrace is continuous and misleads.
    # Hide the board assembly itself while measuring, or its legs split the
    # terrace run into fragments on either side of them.
    board_objects = [o for o in bpy.data.collections['D2_Scoreboards'].objects if not o.hide_viewport]
    for o in board_objects:
        o.hide_viewport = True
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    terrace = []
    for step in range(-70, 41):
        p = top + tangent * step
        hit, location, _, _, obj, _ = scene.ray_cast(depsgraph, Vector((p.x, p.y, 24.5)), Vector((0, 0, -1)))
        terrace.append(bool(hit) and abs(location.z - 22.06) < .3 and 'terrace' in obj.name.lower())
    for o in board_objects:
        o.hide_viewport = False
    bpy.context.view_layer.update()
    # contiguous terrace run that includes or is nearest to the board centre
    runs = []
    start = None
    for i, on in enumerate(terrace + [False]):
        if on and start is None:
            start = i
        if not on and start is not None:
            runs.append((start - 70, i - 1 - 70))
            start = None
    if not runs:
        return {'shift_m': 0.0, 'reason': 'no terrace found under the board line'}
    lo, hi = max(runs, key=lambda r: r[1] - r[0])
    shift = (lo + hi) / 2.0
    delta = tangent * shift
    moved = []
    for obj in bpy.data.collections['D2_Scoreboards'].objects:
        if obj.type == 'MESH' and obj.data.vertices:
            bm = bmesh.new(); bm.from_mesh(obj.data)
            seen = set(); count = 0
            for vertex in bm.verts:
                if vertex in seen: continue
                stack = [vertex]; seen.add(vertex); component = []
                while stack:
                    v = stack.pop(); component.append(v)
                    for edge in v.link_edges:
                        other = edge.other_vert(v)
                        if other not in seen: seen.add(other); stack.append(other)
                center = sum((v.co for v in component), Vector()) / len(component)
                if center.y > 100:
                    for v in component: v.co += delta
                    count += 1
            bm.to_mesh(obj.data); bm.free()
            if count: moved.append(obj.name)
        elif obj.name.startswith('D2_cf_scoreboard_top'):
            obj.location += delta; moved.append(obj.name)
    spec['anchors']['cf_scoreboard_top'][0] += delta.x
    spec['anchors']['cf_scoreboard_top'][1] += delta.y
    scene['v15_cf_board_shift_m'] = shift
    return {'shift_m': round(shift, 2), 'terrace_run_u': [lo, hi], 'moved': moved,
            'basis': 'Board centred on the measured 22.06 m terrace run under its own line'}


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
