"""High fidelity stadium envelope, canopy, and clock tower for Railyards v3.

The builder owns only the stadium's exterior envelope: the river-facing brick
arcade, the continuous upper louver band, the barrel canopy and its roof
structure, floodlight gantries, and the signature clock tower/lantern.  Field,
seating, scoreboards, bridges, landscape, and adjacent buildings stay in their
own modules.

All dimensions are in metres.  The traced ``bowl_back`` and ``canopy_inner``
curves remain the attachment datum from ``scene-spec.json``; the section
parameters live in ``envelope-spec.json`` so future visual passes can adjust
the profile without rewriting the geometry.
"""

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector
from r3_reference_projection import source_to_plane

from r2_geometry import MeshBatch, resample, text


OUT = Path(__file__).resolve().parent
with (OUT / 'envelope-spec.json').open(encoding='utf-8') as _handle:
    ENVELOPE_SPEC = json.load(_handle)


ENVELOPE_GROUP = 'Stadium envelope'
CANOPY_GROUP = 'Canopy'
TOWER_GROUP = 'Clock tower'
GANTRY_GROUP = 'Floodlight gantries'


def _v(point):
    return Vector((float(point[0]), float(point[1]), float(point[2])))


def _frame(center, tangent):
    """Return tangent, outward normal, point helper, and local angle.

    The traced bowl path runs around the outside of the seating bowl.  Its
    left normal is the street/river-facing side used for the facade depth.
    """
    tangent_vector = Vector((float(tangent[0]), float(tangent[1]), 0.0))
    tangent_vector.normalize()
    outward = Vector((-tangent_vector.y, tangent_vector.x, 0.0))
    origin = Vector((float(center[0]), float(center[1]), 0.0))

    def point(u, z, depth=0.0):
        return tuple(origin + tangent_vector * float(u) +
                     outward * float(depth) + Vector((0.0, 0.0, float(z))))

    return tangent_vector, outward, point, math.atan2(tangent_vector.y,
                                                       tangent_vector.x)


def _edge_path(spec, spacing):
    return resample(spec['bowl_back'], float(spacing))


def _arch_points(point, radius, bottom, height, depth, segments=18):
    """Opening polygon with vertical jambs and a true semicircular head."""
    spring = bottom + height - radius
    points = [point(-radius, bottom, depth),
              point(radius, bottom, depth),
              point(radius, spring, depth)]
    points.extend(point(radius * math.cos(math.pi * index / segments),
                        spring + radius * math.sin(math.pi * index / segments),
                        depth) for index in range(1, segments + 1))
    points.append(point(-radius, bottom, depth))
    return points


def _arch_ring(batch, group, point, width, bottom, height, depth,
               ring_width, material='stone', segments=18):
    """Stone voussoirs following the arch without horizontal shortcut bands."""
    radius = width * 0.5
    spring = bottom + height - radius
    outer_radius = radius + ring_width
    # Left-to-right semicircle, with each segment as an individually readable
    # stone wedge.  Short vertical jambs complete the ring down to the plinth.
    for index in range(segments):
        a = math.pi * index / segments
        b = math.pi * (index + 1) / segments
        batch.quad(group, material,
                   [point(radius * math.cos(a), spring + radius * math.sin(a), depth),
                    point(outer_radius * math.cos(a), spring + outer_radius * math.sin(a), depth),
                    point(outer_radius * math.cos(b), spring + outer_radius * math.sin(b), depth),
                    point(radius * math.cos(b), spring + radius * math.sin(b), depth)])
    for u in (-radius - ring_width * 0.5, radius + ring_width * 0.5):
        batch.box(group, material,
                  point(u, bottom + (spring - bottom) * 0.5, depth),
                  (ring_width, 0.30, spring - bottom),
                  angle=math.atan2((point(1.0, bottom, 0.0)[1] -
                                    point(0.0, bottom, 0.0)[1]),
                                   (point(1.0, bottom, 0.0)[0] -
                                    point(0.0, bottom, 0.0)[0])))


def _arch_bay(batch, group, center, tangent, width, bottom, height,
              wall_top, depth, materials):
    """One tall glazed arch bay with brick spandrel and restrained mullions."""
    tangent_vector, _outward, point, angle = _frame(center, tangent)
    radius = width * 0.5
    # Glazing is kept just ahead of the brick wall.  The wall remains a real
    # solid behind it, which gives the opening depth in the night render.
    opening = _arch_points(point, radius, bottom, height, depth + 0.055)
    batch.add(group, 'glass', opening, [tuple(range(len(opening)))])
    _arch_ring(batch, group, point, width, bottom, height, depth + 0.14,
               0.32, 'stone', segments=18)
    spring = bottom + height - radius
    crown = spring + radius
    # A central mullion and two low transoms are visible in the source arches.
    batch.cylinder(group, 'metal', point(0.0, bottom + 0.08, depth + 0.21),
                   point(0.0, crown - 0.13, depth + 0.21), 0.065, sides=6)
    for z in (bottom + 6.0, bottom + 12.0, bottom + 17.5):
        if z < spring - 0.15:
            batch.cylinder(group, 'metal', point(-radius + 0.12, z, depth + 0.21),
                           point(radius - 0.12, z, depth + 0.21), 0.045, sides=6)
    # Small warm entry/room lights establish the occupied brick hall behind
    # the lower arcade without adding people or unrelated program.
    if materials.get('lamp') is not None:
        batch.box(group, 'lamp', point(0.0, bottom + 1.1, depth + 0.23),
                  (width * 0.30, 0.06, 0.16), angle=angle)


def _fascia_bay(batch, center, tangent, width, z0, z1, depth):
    """Dark continuous louver band below the source barrel canopy."""
    _tangent,_outward,point,angle=_frame(center,tangent)
    batch.box(ENVELOPE_GROUP,'glass',point(0,(z0+z1)/2,depth),
              (width+.18,.18,z1-z0),angle=angle)
    count=max(1,round(width/2.2))
    for index in range(count+1):
        u=width*index/count-width/2
        batch.box(ENVELOPE_GROUP,'brick_light',point(u,(z0+z1)/2,depth+.19),
                  (.13,.30,z1-z0+.12),angle=angle)
    rows=max(2,round((z1-z0)/.65))
    for index in range(rows):
        z=z0+(index+.5)*(z1-z0)/rows
        batch.box(ENVELOPE_GROUP,'metal',point(0,z,depth+.15),
                  (width+.24,.26,.21),angle=angle)


def _build_main_facade(scene, spec, batch, materials):
    path = _edge_path(spec, ENVELOPE_SPEC['facade']['bay_spacing'])
    base = float(ENVELOPE_SPEC['facade']['base_z'])
    plinth_top = float(ENVELOPE_SPEC['facade']['plinth_top_z'])
    wall_top = float(ENVELOPE_SPEC['facade']['wall_top_z'])
    arch_bottom = float(ENVELOPE_SPEC['facade']['arch_bottom_z'])
    arch_height = float(ENVELOPE_SPEC['facade']['arch_height'])
    fascia_bottom = float(ENVELOPE_SPEC['facade']['fascia_bottom_z'])
    fascia_top = float(ENVELOPE_SPEC['facade']['fascia_top_z'])
    wall_depth = float(ENVELOPE_SPEC['facade']['wall_depth'])
    sign_index = min(len(path) - 1,
                     int(ENVELOPE_SPEC['facade']['sign_bay_index']))

    for index, (a, b) in enumerate(zip(path, path[1:])):
        center = (Vector(a) + Vector(b)) * 0.5
        tangent = Vector(b) - Vector(a)
        width = tangent.length
        _tangent, _outward, point, angle = _frame(center, tangent)
        # Continuous brick mass; arches/glazing are surfaced on its outward
        # face, leaving honest brick spandrels between crown and fascia.
        batch.box(ENVELOPE_GROUP, 'brick', point(0.0, (plinth_top + wall_top) * 0.5, 0.0),
                  (width + 0.16, wall_depth, wall_top - plinth_top), angle=angle)
        batch.box(ENVELOPE_GROUP, 'stone', point(0.0, (base + plinth_top) * 0.5, 0.12),
                  (width + 0.25, wall_depth + 0.45, plinth_top - base), angle=angle)
        batch.box(ENVELOPE_GROUP, 'stone', point(0.0, plinth_top - 0.12, 0.40),
                  (width + 0.38, wall_depth + 0.65, 0.26), angle=angle)
        # A cap course under the dark upper fascia gives the source's strong
        # horizontal datum without cutting the lower arches short.
        batch.box(ENVELOPE_GROUP, 'stone', point(0.0, wall_top - 0.24, 0.48),
                  (width + 0.26, wall_depth + 0.42, 0.32), angle=angle)

        bay_width = min(width * 0.72, float(ENVELOPE_SPEC['facade']['arch_width']))
        _arch_bay(batch, ENVELOPE_GROUP, center, tangent, bay_width,
                  arch_bottom, arch_height, wall_top, wall_depth * 0.5 + 0.01,
                  materials)
        _fascia_bay(batch, center, tangent, width, fascia_bottom, fascia_top,
                    wall_depth * 0.5 + 0.04)
        if index == sign_index:
            # Keep the lettering in the upper fascia, where it is visible in
            # the south crop and does not compete with the scoreboards.
            t = _tangent
            normal = _outward
            sign_z = fascia_bottom + 1.65
            batch.box(ENVELOPE_GROUP, 'screen',
                      point(0.0, sign_z, wall_depth * 0.5 + 0.21),
                      (min(width * 2.80, 48.0), 0.16, 3.35), angle=angle)
            label = Vector(center) + normal * (wall_depth * 0.5 + 0.37)
            label.z = sign_z - 0.12
            text(scene, batch.collection(ENVELOPE_GROUP), 'Main sign',
                 'THE RAILYARDS', tuple(label),
                 float(ENVELOPE_SPEC['facade']['sign_size']),
                 materials['screen_ink'],
                 (math.pi / 2.0, 0.0, math.atan2(t.y, t.x) + math.pi))

    # Vertical pilasters at the path joints are deliberately wider than the
    # individual mullions and carry the source's strong repeated cadence.
    for index, point_xy in enumerate(path):
        if index % 2:
            continue
        prev_point = Vector(path[max(0, index - 1)])
        next_point = Vector(path[min(len(path) - 1, index + 1)])
        tangent = next_point - prev_point
        center = Vector(point_xy)
        _tangent, _outward, point, angle = _frame(center, tangent)
        batch.box(ENVELOPE_GROUP, 'brick_light', point(0.0, (plinth_top + wall_top) * 0.5, 0.56),
                  (0.55, wall_depth + 0.25, wall_top - plinth_top + 0.28), angle=angle)
        batch.box(ENVELOPE_GROUP, 'stone', point(0.0, (base + plinth_top) * 0.5, 0.64),
                  (0.68, wall_depth + 0.38, plinth_top - base + 0.15), angle=angle)

    # The north/left-field termination descends into the pavilion roof.
    # A full-height end cap at the last bowl point protruded through the
    # source-visible rooftop shades as an unsupported tall brick triangle.
    for (group,material),vertices in batch.vertices.items():
        if group!=ENVELOPE_GROUP:continue
        for index,p in enumerate(vertices):
            x,y,z=p
            if x < -25 and y>108:
                cap=47.6-(47.6-33.1)*min(1,(y-108)/(126.2-108))
                if z>cap:vertices[index]=(x,y,cap)


def _build_river_arcade(batch, spec):
    """Long glazed public arcade attached to the river side of the bowl."""
    arcade = ENVELOPE_SPEC['river_arcade']
    footprint = [tuple(point) for point in arcade['footprint']]
    base = float(arcade['base_z'])
    lower_top = float(arcade['lower_wall_top_z'])
    upper_top = float(arcade['upper_glass_top_z'])
    roof_top = float(arcade['roof_top_z'])
    # The footprint is intentionally explicit: it is the river-side volume
    # visible in the south and B4 sources, not a generic stadium extrusion.
    batch.prism('River-side arcade', 'brick_dark', footprint, base, lower_top)
    batch.prism('River-side arcade', 'stone', footprint,
                lower_top - 0.35, lower_top + 0.08)
    for edge_index, (a_xy, b_xy) in enumerate(zip(footprint,
                                                   footprint[1:] + footprint[:1])):
        a = Vector((*a_xy, 0.0))
        b = Vector((*b_xy, 0.0))
        tangent = b - a
        length = tangent.length
        if length < 1.0:
            continue
        count = max(1, round(length / float(arcade['bay_spacing'])))
        bay = length / count
        # The explicit arcade footprint is counter-clockwise, so the normal
        # produced by its forward edge points into the volume.  Reverse the
        # local tangent for facade details to put glazing and arch rings on
        # the river/street-facing side of the wall.
        facade_tangent = -tangent
        for bay_index in range(count):
            center = a.lerp(b, (bay_index + 0.5) / count)
            width = min(bay * 0.74, float(arcade['arch_width']))
            _arch_bay(batch, 'River-side arcade', center, facade_tangent, width,
                      float(arcade['arch_bottom_z']),
                      float(arcade['arch_height']), lower_top,
                      float(arcade['face_depth']) * 0.5 + 0.04, {})
            _tangent, _outward, point, angle = _frame(center, facade_tangent)
            batch.box('River-side arcade', 'glass',
                      point(0.0, (lower_top + upper_top) * 0.5,
                            float(arcade['face_depth']) * 0.5 + 0.12),
                      (bay * 0.82, 0.14, upper_top - lower_top), angle=angle)
            for u in (-bay * 0.30, 0.0, bay * 0.30):
                batch.box('River-side arcade', 'metal',
                          point(u, (lower_top + upper_top) * 0.5,
                                float(arcade['face_depth']) * 0.5 + 0.22),
                          (0.075, 0.20, upper_top - lower_top + 0.18), angle=angle)
        batch.box('River-side arcade', 'metal',
                  ((a + b) * 0.5 + Vector((0.0, 0.0, roof_top - 0.25))),
                  (length + 0.35, 0.34, 0.50),
                  angle=math.atan2(tangent.y, tangent.x))
    batch.prism('River-side arcade', 'roof', footprint, roof_top - 0.18,
                roof_top + 0.18)


def _canopy_rows(spec):
    outer = [_v(point) for point in spec['bowl_back']]
    inner = [_v(point) for point in spec['canopy_inner']]
    count = int(ENVELOPE_SPEC['canopy']['cross_section_rows'])
    lift = float(ENVELOPE_SPEC['canopy']['crown_lift'])
    rows = []
    for row_index in range(count):
        fraction = row_index / (count - 1)
        row = []
        for outside, inside in zip(outer, inner):
            base = outside.lerp(inside, fraction)
            crown = lift * math.sin(math.pi * fraction)
            row.append(tuple(base + Vector((0.0, 0.0, crown))))
        rows.append(row)
    return rows


def _build_canopy_surfaces(batch, spec):
    rows = _canopy_rows(spec)
    underside = float(ENVELOPE_SPEC['canopy']['underside_drop'])
    for row_index in range(len(rows) - 1):
        upper = rows[row_index]
        lower = rows[row_index + 1]
        for index in range(len(upper) - 1):
            batch.quad(CANOPY_GROUP, 'canopy',
                       [upper[index], lower[index], lower[index + 1], upper[index + 1]])
            batch.quad(CANOPY_GROUP, 'interior',
                       [(x, y, z - underside) for x, y, z in
                        (upper[index], upper[index + 1], lower[index + 1], lower[index])])

    seam_spacing = max(1, int(ENVELOPE_SPEC['canopy']['seam_spacing_points']))
    outer = rows[0]
    inner = rows[-1]
    for index in range(0, len(outer), seam_spacing):
        seam = [row[index] for row in rows]
        batch.line(CANOPY_GROUP, 'aluminum', seam,
                   float(ENVELOPE_SPEC['canopy']['seam_radius']), sides=6)
        batch.line(CANOPY_GROUP, 'metal',
                   [(x, y, z - underside * 0.65) for x, y, z in seam],
                   float(ENVELOPE_SPEC['canopy']['under_seam_radius']), sides=6)
    # Strong perimeter beams make the shell read at the south camera's long
    # focal length and provide an unambiguous attachment endpoint.
    batch.line(CANOPY_GROUP, 'metal', outer,
               float(ENVELOPE_SPEC['canopy']['edge_beam_radius']), sides=8)
    batch.line(CANOPY_GROUP, 'metal', inner,
               float(ENVELOPE_SPEC['canopy']['edge_beam_radius']), sides=8)


def _build_gantries(scene, batch, spec):
    rows = _canopy_rows(spec)
    outer = rows[0]
    gantry = ENVELOPE_SPEC['gantries']
    indices = [min(len(outer) - 1,
                   max(0, int(round(fraction * (len(outer) - 1)))))
               for fraction in gantry['path_fractions']]
    for gantry_index, path_index in enumerate(indices):
        center = Vector(outer[path_index])
        if gantry.get('source_pixels_north'):
            px=gantry['source_pixels_north'][gantry_index]
            recovered=source_to_plane(scene,bpy.data.objects['R2_north'],px,(1944,1294),55.45)
            center.x,center.y=recovered[:2]
        prior = Vector(outer[max(0, path_index - 1)])
        following = Vector(outer[min(len(outer) - 1, path_index + 1)])
        tangent, outward, point, angle = _frame(center, following - prior)
        base_z = center.z - 0.05
        top_z = base_z + float(gantry['height'])
        width = float(gantry['crossbeam_width'])
        for offset in (-width * 0.36, width * 0.36):
            foot = Vector(point(offset, base_z, 0.18))
            head = Vector(point(offset, top_z, 0.18))
            batch.cylinder(GANTRY_GROUP, 'metal', foot, head,
                           float(gantry['leg_radius']), sides=6)
            # Rear diagonal braces are kept shallow so the gantry remains on
            # the roof edge rather than becoming a free-standing tower.
            rear = Vector(point(offset, base_z + float(gantry['height']) * 0.14,
                                -0.62))
            batch.cylinder(GANTRY_GROUP, 'metal', rear, head,
                           float(gantry['brace_radius']), sides=6)
        left_foot = Vector(point(-width * 0.36, base_z, 0.18))
        right_foot = Vector(point(width * 0.36, base_z, 0.18))
        left_head = Vector(point(-width * 0.36, top_z, 0.18))
        right_head = Vector(point(width * 0.36, top_z, 0.18))
        batch.cylinder(GANTRY_GROUP, 'metal', left_foot, right_head,
                       float(gantry['brace_radius']), sides=6)
        batch.cylinder(GANTRY_GROUP, 'metal', right_foot, left_head,
                       float(gantry['brace_radius']), sides=6)
        batch.cylinder(GANTRY_GROUP, 'metal', left_foot, right_foot,
                       float(gantry['beam_radius']) * 0.70, sides=6)
        beam_a = Vector(point(-width * 0.48, top_z, 0.18))
        beam_b = Vector(point(width * 0.48, top_z, 0.18))
        batch.cylinder(GANTRY_GROUP, 'metal', beam_a, beam_b,
                       float(gantry['beam_radius']), sides=8)
        # Two staggered rows of compact luminous heads match the source's
        # horizontal banks while leaving the dark lattice visible between.
        for lamp_index in range(int(gantry['lamp_count'])):
            u = width * (lamp_index + 0.5) / float(gantry['lamp_count']) - width * 0.5
            for lamp_depth in (0.03, 0.39):
                lamp_center = Vector(point(u, top_z - 0.55, lamp_depth))
                batch.box(GANTRY_GROUP, 'stadium_lamp', tuple(lamp_center),
                          (float(gantry['lamp_width']), 0.22,
                           float(gantry['lamp_height'])), angle=angle)
        # Keep the existing lighting preset contract: r2_lighting looks up
        # these exact names to switch between day and night energies. Reuse a
        # pre-existing object when the integrating build has retained one;
        # otherwise create the area light in the module's D2_Lighting group.
        light_name = 'D2_Field light ' + str(gantry_index)
        data = bpy.data.lights.get(light_name)
        if data is None:
            data = bpy.data.lights.new(light_name, 'AREA')
        data.energy = 42000
        data.shape = 'RECTANGLE'
        data.spread = math.radians(120)
        data.size = 10.0
        data.size_y = 4.0
        data.color = (0.88, 0.93, 1.0)
        light_object = bpy.data.objects.get(light_name)
        if light_object is None:
            light_object = bpy.data.objects.new(light_name, data)
            batch.collection('Lighting').objects.link(light_object)
        # Existing objects can remain linked to the legacy D2_Lighting
        # collection; leave that ownership intact while updating their
        # transform and data in place.
        light_object.data = data
        light_location = Vector(point(0.0, top_z - 0.35, 0.35))
        light_object.location = light_location
        light_object.rotation_euler = (
            Vector((30.0, 30.0, 12.0)) - light_location
        ).to_track_quat('-Z', 'Y').to_euler()


def _tower_face_data(anchor, angle, half_width):
    tangent = Vector((math.cos(angle), math.sin(angle), 0.0))
    normal = Vector((-tangent.y, tangent.x, 0.0))
    center = Vector((float(anchor[0]), float(anchor[1]), 0.0)) + normal * half_width
    _tangent, _outward, point, _local_angle = _frame(center, tangent)
    return tangent, normal, point, angle


def _clock_face(batch, point, radius, z, depth):
    segments = int(ENVELOPE_SPEC['tower']['clock_segments'])
    face = [point(radius * math.cos(math.tau * index / segments),
                  z + radius * math.sin(math.tau * index / segments), depth)
            for index in range(segments)]
    batch.add(TOWER_GROUP, 'screen', face, [tuple(range(len(face)))])
    batch.line(TOWER_GROUP, 'stone', face + [face[0]],
               float(ENVELOPE_SPEC['tower']['clock_ring_radius']), sides=6)
    # Hands and twelve small hour marks are enough to read as a clock at the
    # calibrated south/bridge resolutions without pretending to know a time.
    for index in range(12):
        theta = math.tau * index / 12.0
        outer = point(radius * 0.82 * math.cos(theta),
                      z + radius * 0.82 * math.sin(theta), depth + 0.05)
        inner = point(radius * 0.68 * math.cos(theta),
                      z + radius * 0.68 * math.sin(theta), depth + 0.05)
        batch.cylinder(TOWER_GROUP, 'white', inner, outer, 0.055, sides=5)
    for theta, length, radius_hand in ((math.radians(42.0), radius * 0.56, 0.12),
                                       (math.radians(252.0), radius * 0.39, 0.10)):
        batch.cylinder(TOWER_GROUP, 'white', point(0.0, z, depth + 0.10),
                       point(length * math.cos(theta), z + length * math.sin(theta),
                             depth + 0.10), radius_hand, sides=6)


def _build_clock_tower(scene, spec, batch, materials):
    tower_spec = ENVELOPE_SPEC['tower']
    anchor = spec['anchors']['tower_roof']
    x, y, roof_z = (float(anchor[0]), float(anchor[1]),
                    float(tower_spec['roof_z']))
    shaft_width = float(tower_spec['shaft_width'])
    shaft_depth = float(tower_spec['shaft_depth'])
    center = (x, y)
    batch.box(TOWER_GROUP, 'stone', (x, y, 9.15),
              (shaft_width + 4.0, shaft_depth + 4.5, 2.3))
    batch.box(TOWER_GROUP, 'brick_light', (x, y, 15.5),
              (shaft_width + 1.2, shaft_depth + 1.4, 10.2))
    batch.box(TOWER_GROUP, 'brick', (x, y, 31.0),
              (shaft_width, shaft_depth, 20.5))
    for z, width, depth, height in ((11.0, shaft_width + 4.7, shaft_depth + 5.2, 0.50),
                                     (21.1, shaft_width + 1.5, shaft_depth + 1.8, 0.55),
                                     (42.8, shaft_width + 1.5, shaft_depth + 1.8, 0.62),
                                     (47.0, shaft_width + 2.1, shaft_depth + 2.4, 0.65),
                                     (66.3, shaft_width + 2.2, shaft_depth + 2.5, 0.65)):
        batch.box(TOWER_GROUP, 'stone', (x, y, z), (width, depth, height))

    # Close the shaft-to-lantern transition; previously the belt courses
    # at 42.8 and 47 m floated above a shaft ending at 41.25 m.
    batch.box(TOWER_GROUP,'brick',(x,y,44.35),(shaft_width,shaft_depth,6.3))
    # Tall lower shaft windows, with corner pilasters that survive at aerial
    # scale and keep the clock tower from reading as a plain brick box.
    for angle in (0.0, math.pi * 0.5, math.pi, math.pi * 1.5):
        tangent, normal, point, local_angle = _tower_face_data(
            (x, y), angle, shaft_depth * 0.5 + 0.08)
        for u in (-shaft_width * 0.28, shaft_width * 0.28):
            batch.box(TOWER_GROUP, 'glass_lit', point(u, 31.0, 0.04),
                      (shaft_width * 0.20, 0.12, 13.6), angle=local_angle)
            batch.box(TOWER_GROUP, 'stone', point(u - shaft_width * 0.14,
                                                  31.0, 0.13),
                      (0.24, 0.36, 14.4), angle=local_angle)
        for u in (-shaft_width * 0.5 + 0.36, shaft_width * 0.5 - 0.36):
            batch.box(TOWER_GROUP, 'stone', point(u, 31.0, 0.16),
                      (0.48, 0.38, 20.2), angle=local_angle)

    # Lantern: translucent lit bays behind the four dark clock faces, with an
    # open metal frame and a modest stepped cap below the roof datum.
    lantern_bottom = float(tower_spec['lantern_bottom_z'])
    lantern_top = float(tower_spec['lantern_top_z'])
    lantern_half = float(tower_spec['lantern_half_width'])
    clock_z = float(tower_spec['clock_z'])
    clock_radius = float(tower_spec['clock_radius'])
    for angle in (0.0, math.pi * 0.5, math.pi, math.pi * 1.5):
        tangent, normal, point, local_angle = _tower_face_data(
            (x, y), angle, lantern_half)
        # Dark transmissive glass keeps the clock dial dominant; narrow warm
        # practicals behind the frame supply the lantern glow seen in the
        # source without turning the tower into a solid peach cube.
        batch.box(TOWER_GROUP, 'glass',
                  point(0.0, (lantern_bottom + lantern_top) * 0.5, 0.01),
                  (lantern_half * 2.0, 0.13, lantern_top - lantern_bottom),
                  angle=local_angle)
        for lamp_u in (-lantern_half * 0.68, lantern_half * 0.68):
            batch.box(TOWER_GROUP, 'lamp',
                      point(lamp_u, (lantern_bottom + lantern_top) * 0.5, -0.02),
                      (0.20, 0.08, lantern_top - lantern_bottom - 0.8),
                      angle=local_angle)
        for u in (-lantern_half + 0.38, lantern_half - 0.38):
            batch.box(TOWER_GROUP, 'metal', point(u,
                                                  (lantern_bottom + lantern_top) * 0.5,
                                                  0.19),
                      (0.25, 0.34, lantern_top - lantern_bottom + 0.35),
                      angle=local_angle)
        batch.box(TOWER_GROUP, 'metal', point(0.0, lantern_bottom, 0.20),
                  (lantern_half * 2.10, 0.38, 0.32), angle=local_angle)
        batch.box(TOWER_GROUP, 'metal', point(0.0, lantern_top, 0.20),
                  (lantern_half * 2.10, 0.38, 0.32), angle=local_angle)
        _clock_face(batch, point, clock_radius, clock_z, 0.24)

    batch.box(TOWER_GROUP, 'roof', (x, y, roof_z - 0.35),
              (shaft_width + 3.4, shaft_depth + 3.8, 0.70))
    batch.box(TOWER_GROUP, 'stone', (x, y, roof_z - 1.0),
              (shaft_width + 2.3, shaft_depth + 2.8, 0.45))
    # A small rooftop beacon is visible in the bridge source and gives the
    # stepped cap a vertical finish without inventing a mast.
    batch.cylinder(TOWER_GROUP, 'metal', (x, y, roof_z),
                   (x, y, roof_z + 0.95), 0.10, sides=8)
    batch.ellipsoid(TOWER_GROUP, 'lamp', (x, y, roof_z + 1.05),
                    (0.28, 0.28, 0.28), segments=12, rings=6)


def _build_west_lantern(batch, spec):
    anchor = spec['anchors']['west_roof_lantern']
    x, y, roof_z = (float(anchor[0]), float(anchor[1]),
                    float(ENVELOPE_SPEC['west_lantern']['roof_z']))
    width = float(ENVELOPE_SPEC['west_lantern']['width'])
    depth = float(ENVELOPE_SPEC['west_lantern']['depth'])
    bottom = float(ENVELOPE_SPEC['west_lantern']['bottom_z'])
    batch.box(CANOPY_GROUP, 'glass_lit', (x, y, (bottom + roof_z) * 0.5),
              (width, depth, roof_z - bottom))
    for u in (-width * 0.36, 0.0, width * 0.36):
        batch.box(CANOPY_GROUP, 'metal', (x + u, y, (bottom + roof_z) * 0.5),
                  (0.20, depth + 0.20, roof_z - bottom + 0.15))
    for v in (-depth * 0.36, 0.0, depth * 0.36):
        batch.box(CANOPY_GROUP, 'metal', (x, y + v, (bottom + roof_z) * 0.5),
                  (width + 0.20, 0.20, roof_z - bottom + 0.15))
    batch.box(CANOPY_GROUP, 'roof', (x, y, roof_z),
              (width + 1.1, depth + 1.0, 0.65))


def build_envelope(scene, spec, batch, materials):
    """Add the source-led stadium exterior and return serializable metadata."""
    _build_main_facade(scene, spec, batch, materials)
    _build_river_arcade(batch, spec)
    _build_canopy_surfaces(batch, spec)
    _build_gantries(scene, batch, spec)
    _build_clock_tower(scene, spec, batch, materials)
    _build_west_lantern(batch, spec)
    return {
        'module': 'r3_envelope',
        'groups': [ENVELOPE_GROUP, 'River-side arcade', CANOPY_GROUP,
                   GANTRY_GROUP, TOWER_GROUP],
        'source': ENVELOPE_SPEC['sources'],
        'attachments': ENVELOPE_SPEC['attachments'],
    }
