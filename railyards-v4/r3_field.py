"""Reference-led, regulation-scaled playing field for Railyards v3.

The stadium footprint is inferred from ``scene-spec.json`` and the supplied
AECOM north aerial.  The diamond itself follows current MLB dimensions where
the rules provide dimensions; the skinned infield, warning track width, and
mowing pattern remain visual reconstruction choices.

The module deliberately owns only ``build_field``.  It adds all geometry to a
single ``Field`` MeshBatch group so a caller can replace the old field objects
and flush this builder as one editable collection.
"""

import math

import bpy
from mathutils import Vector

from r2_geometry import MeshBatch


GROUP = 'Field'
FT = 0.3048
IN = 0.0254


def _xy(point):
    return (float(point[0]), float(point[1]))


def _v(point, z):
    return (float(point[0]), float(point[1]), float(z))


def _rounded_rect(x0, y0, x1, y1, radius, segments=8):
    """Counter-clockwise rounded rectangle footprint in the XY plane."""
    radius = min(radius, (x1 - x0) * 0.5, (y1 - y0) * 0.5)
    centers = [(x1 - radius, y0 + radius),
               (x1 - radius, y1 - radius),
               (x0 + radius, y1 - radius),
               (x0 + radius, y0 + radius)]
    result = []
    for corner, (cx, cy) in enumerate(centers):
        # The first center is bottom-right, so its arc runs from bottom to
        # right.  Advancing counter-clockwise then visits the other corners.
        start = -math.pi * 0.5 + corner * math.pi * 0.5
        for i in range(segments + 1):
            angle = start + math.pi * 0.5 * i / segments
            result.append((cx + radius * math.cos(angle),
                           cy + radius * math.sin(angle)))
    return result


def _disk(center, radius, z0, z1, sides=64):
    return [(center[0] + radius * math.cos(math.tau * i / sides),
             center[1] + radius * math.sin(math.tau * i / sides))
            for i in range(sides)]


def _clip_half_plane(polygon, normal, limit, keep_greater):
    """Clip a polygon against dot(point, normal) >= or <= limit."""
    if not polygon:
        return []

    def value(point):
        return point[0] * normal[0] + point[1] * normal[1]

    def inside(point):
        return value(point) >= limit - 1e-8 if keep_greater else value(point) <= limit + 1e-8

    result = []
    for a, b in zip(polygon, polygon[1:] + polygon[:1]):
        ina, inb = inside(a), inside(b)
        if ina:
            result.append(a)
        if ina != inb:
            va, vb = value(a), value(b)
            t = (limit - va) / (vb - va)
            result.append((a[0] + t * (b[0] - a[0]),
                           a[1] + t * (b[1] - a[1])))
    return result


def _strip_polygon(polygon, normal, low, high):
    result = _clip_half_plane(polygon, normal, low, True)
    return _clip_half_plane(result, normal, high, False)


def _inset_vertices(polygon, distance):
    """Return a joined inward offset with a bounded miter at each vertex."""
    result = []
    count = len(polygon)
    for index, point in enumerate(polygon):
        previous = Vector(polygon[(index - 1) % count])
        current = Vector(point)
        following = Vector(polygon[(index + 1) % count])
        incoming = current - previous
        outgoing = following - current
        if incoming.length < 1e-6 or outgoing.length < 1e-6:
            result.append(tuple(current))
            continue
        incoming.normalize()
        outgoing.normalize()
        normal_a = Vector((-incoming.y, incoming.x))
        normal_b = Vector((-outgoing.y, outgoing.x))
        line_a = current + normal_a * distance
        line_b = current + normal_b * distance
        cross = incoming.x * outgoing.y - incoming.y * outgoing.x
        if abs(cross) < 1e-6:
            joined = current + (normal_a + normal_b).normalized() * distance
        else:
            delta = line_b - line_a
            amount = (delta.x * outgoing.y - delta.y * outgoing.x) / cross
            joined = line_a + incoming * amount
        # A sharp traced corner can create a very long miter.  Clamping to a
        # short bevel keeps adjacent strips joined without a spike across the
        # grass while retaining the nominal width along each edge.
        offset = joined - current
        if offset.length > distance * 1.35:
            offset.normalize()
            joined = current + offset * distance * 1.35
        result.append(tuple(joined))
    return result


def _outline(batch, points, z, material='white', radius=0.035):
    points3 = [(x, y, z) for x, y in points]
    batch.line(GROUP, material, points3 + [points3[0]], radius, sides=6)


def _rect_corners(center, along, across, length, width):
    """Corners for a rectangle whose long axis is ``along``."""
    c = Vector((center[0], center[1]))
    a = Vector((along[0], along[1])).normalized()
    b = Vector((across[0], across[1])).normalized()
    hl, hw = length * 0.5, width * 0.5
    return [tuple(c - a * hl - b * hw),
            tuple(c + a * hl - b * hw),
            tuple(c + a * hl + b * hw),
            tuple(c - a * hl + b * hw)]


def build_field(scene, spec, batch, materials):
    """Add the complete playing surface to ``batch``.

    Coordinates use the v3 convention: home's rear point is (0, 0), first
    base is on +X, third base is on +Y, and second base is (+X, +Y).  All
    dimensions are in metres because that is the scene specification unit.
    """
    z = float(spec.get('field_z', 12.0))
    surface_z = z + 0.002
    # Keep all chalk above the plate dirt, clay lanes, and infield grass.
    chalk_z = z + 0.074

    # Regulation diamond.  The 2023 MLB bag size is 18 inches; home plate
    # remains the 17-inch pentagon specified by the rulebook.
    base_path = 90.0 * FT
    base_side = 18.0 * IN
    base_thickness = 0.12
    home = (0.0, 0.0)
    first = (base_path, 0.0)
    second = (base_path, base_path)
    third = (0.0, base_path)
    axis = Vector((1.0, 1.0)).normalized()
    across = Vector((1.0, -1.0)).normalized()
    mound_distance = 59.0 * FT
    mound_center = axis * mound_distance

    # The combined bowl-front/field-boundary polygon is the traced playable
    # footprint.  Its z values describe the bowl, so the playing surface is
    # intentionally leveled to field_z.
    bowl_front = [_xy(point) for point in spec['bowl_front']]
    field_boundary = [_xy(point) for point in spec['field_boundary']]
    footprint = bowl_front + list(reversed(field_boundary))
    footprint_area = sum(a[0] * b[1] - b[0] * a[1]
                         for a, b in zip(footprint,
                                         footprint[1:] + footprint[:1])) * 0.5
    # MeshBatch uses the supplied top-face winding.  Keep the playing surface
    # counter-clockwise so its normals point upward even if the traced input
    # order changes in a later scene-spec revision.
    if footprint_area < 0.0:
        footprint.reverse()
        footprint_area = -footprint_area

    # Low green substrate keeps the entire irregular field footprint coherent
    # beneath the detailed infield and the visual mowing bands.
    batch.prism(GROUP, 'field', footprint, z, surface_z)

    # Source-faithful, broad skinned infield. MLB Diagram 1 uses a 95-foot
    # grass-line radius centered on the pitcher; use that native circular arc
    # for the outfield side of the clay shell instead of a small square patch.
    # The two endpoints are where that arc meets the first/third foul rays.
    grass_arc_radius = 95.0 * FT
    mx, my = mound_center.x, mound_center.y
    first_arc_x = mx + math.sqrt(grass_arc_radius * grass_arc_radius - my * my)
    third_arc_y = my + math.sqrt(grass_arc_radius * grass_arc_radius - mx * mx)
    start_angle = math.atan2(-my, first_arc_x - mx)
    end_angle = math.atan2(third_arc_y - my, -mx)
    outer_arc = [(mx + grass_arc_radius * math.cos(angle),
                  my + grass_arc_radius * math.sin(angle))
                 for angle in [start_angle + (end_angle - start_angle) * i / 64
                               for i in range(65)]]
    outer_clay = [(-4.25, -4.25), (first_arc_x, -4.25)] + outer_arc + [
        (-4.25, third_arc_y)]
    inner_grass = _rounded_rect(2.75, 2.75, base_path - 2.45,
                                base_path - 2.45, 3.7, segments=10)
    batch.prism(GROUP, 'soil', outer_clay, surface_z, surface_z + 0.020)
    batch.prism(GROUP, 'field', inner_grass, surface_z + 0.021,
                surface_z + 0.032)

    # Four compact clay lanes restore the continuous skinned-path read over
    # the grass cutout.  Width is the common 12-ft visual treatment used by
    # many professional grounds crews; the exact grass line is club-specific.
    lane_width = 12.0 * FT
    lane_z0 = surface_z + 0.034
    lane_thickness = 0.012
    # The four slabs meet at each bag. A minute grade tolerance gives the
    # overlapping slabs a deterministic draw order and prevents Cycles from
    # producing black z-fighting diamonds at their coplanar junctions.
    lane_grade_tolerance = 0.001
    lanes = [
        ((base_path * 0.5, 0.0), (base_path + 1.2, lane_width), 0.0),
        ((0.0, base_path * 0.5), (lane_width, base_path + 1.2), 0.0),
        ((base_path, base_path * 0.5), (base_path + 1.2, lane_width), math.pi * 0.5),
        ((base_path * 0.5, base_path), (base_path + 1.2, lane_width), 0.0),
    ]
    for index, (center, size, angle) in enumerate(lanes):
        level = lane_z0 + index * lane_grade_tolerance
        batch.box(GROUP, 'soil', (center[0], center[1], level + lane_thickness * 0.5),
                  (*size, lane_thickness), angle=angle)

    # Plate dirt is intentionally a clean 13-ft diameter circle in the source
    # read, with the batter and catcher markings sitting on its rear apron.
    batch.prism(GROUP, 'soil', _disk(home, 2.0, surface_z + 0.046,
                                     surface_z + 0.056, sides=72),
                surface_z + 0.046, surface_z + 0.056)

    # Outfield mowing bands are clipped against the actual irregular footprint
    # rather than ending at an invented rectangle.  Parallel diagonal bands
    # follow the visible source treatment and remain beneath the clay details.
    band_normal = (axis.x, axis.y)
    band_width = 5.4
    for index in range(-18, 28):
        low = index * band_width
        band = _strip_polygon(footprint, band_normal, low, low + band_width)
        if len(band) >= 3:
            batch.prism(GROUP, 'field_light' if index % 2 else 'field',
                        band, surface_z + 0.004, surface_z + 0.008)

    # Warning track follows every edge of the inferred field polygon and is
    # therefore clipped at both straight outfield boundary segments and the
    # curved traced bowl front.  The 15-ft width is a reconstruction estimate,
    # since MLB regulates the field boundary rather than a universal track.
    track_width = 15.0 * FT
    inner_track = _inset_vertices(footprint, track_width)
    for index, (a, b) in enumerate(zip(footprint,
                                       footprint[1:] + footprint[:1])):
        edge = Vector((b[0] - a[0], b[1] - a[1]))
        if edge.length < 1e-5:
            continue
        # Joined offset vertices eliminate gaps between adjacent strips and
        # avoid the visible overlaps produced by independent edge normals.
        ai = inner_track[index]
        bi = inner_track[(index + 1) % len(inner_track)]
        batch.prism(GROUP, 'warning', [a, b, bi, ai],
                    surface_z + 0.010, surface_z + 0.018)

    # Foul lines terminate at the two measured field-boundary endpoints, not
    # at arbitrary 100-m points.  The lines are cylinders so they remain
    # readable in both the north aerial and perspective cameras.
    batch.line(GROUP, 'white', [_v(home, chalk_z), _v(field_boundary[0], chalk_z)],
               0.045, sides=6)
    batch.line(GROUP, 'white', [_v(home, chalk_z), _v(field_boundary[-1], chalk_z)],
               0.045, sides=6)

    # Current first/second/third bags, centered at the regulation 90-ft
    # intersections and raised within the 3-5 inch rulebook thickness range.
    for name, center in [('First base', first), ('Second base', second),
                         ('Third base', third)]:
        x, y = center
        half = base_side * 0.5
        batch.prism(GROUP, 'white', [(x - half, y - half),
                                     (x + half, y - half),
                                     (x + half, y + half),
                                     (x - half, y + half)],
                    surface_z + 0.055, surface_z + 0.055 + base_thickness)

    # Home plate pentagon: the rear point is the origin, its 12-inch edges
    # coincide with the first/third lines, and the forward edge is 17 inches.
    side = 12.0 * IN
    half_top = 8.5 * IN
    top_diagonal = 17.0 * IN / math.sqrt(2.0)
    delta = top_diagonal - side
    top_offset = (-delta + math.sqrt(2.0 * half_top * half_top - delta * delta)) * 0.5
    plate = [(0.0, 0.0), (side, 0.0),
             (top_offset + top_diagonal, top_offset),
             (top_offset, top_offset + top_diagonal), (0.0, side)]
    batch.prism(GROUP, 'white', plate, surface_z + 0.057,
                surface_z + 0.057 + 0.025)

    # Pitcher's mound.  Rulebook Diagram 3 places the center of the 18-foot
    # mound circle 59 feet from home's rear point.  The rubber's front edge is
    # 18 inches behind that center, making its distance to home 60 ft 6 in.
    rubber_front_distance = 60.5 * FT
    rubber_depth = 6.0 * IN
    rubber_center = axis * (rubber_front_distance + rubber_depth * 0.5)
    mound_radius = 9.0 * FT
    mound_top = surface_z + 10.0 * IN
    mound_base = surface_z + 0.055
    mound_top_radius = 0.78
    mound_segments = 64
    mound_rings = 16
    mound_vertices = []
    for ring in range(mound_rings + 1):
        fraction = ring / mound_rings
        radius = mound_radius + (mound_top_radius - mound_radius) * fraction
        level = mound_base + (mound_top - mound_base) * fraction
        mound_vertices.extend(
            (mound_center.x + radius * math.cos(math.tau * index / mound_segments),
             mound_center.y + radius * math.sin(math.tau * index / mound_segments),
             level)
            for index in range(mound_segments)
        )
    mound_faces = [tuple(reversed(range(mound_segments)))]
    for ring in range(mound_rings):
        start = ring * mound_segments
        next_start = (ring + 1) * mound_segments
        mound_faces.extend(
            (start + index, start + (index + 1) % mound_segments,
             next_start + (index + 1) % mound_segments, next_start + index)
            for index in range(mound_segments)
        )
    mound_faces.append(tuple(range(mound_rings * mound_segments,
                                   (mound_rings + 1) * mound_segments)))
    batch.add(GROUP, 'soil', mound_vertices, mound_faces)
    # The rubber is 24 inches wide by 6 inches deep, with its top at mound
    # height.  Local box X is aligned across the mound and local Y down-axis.
    rubber_angle = math.atan2(axis.y, axis.x) + math.pi * 0.5
    batch.box(GROUP, 'white', (rubber_center.x, rubber_center.y,
                              mound_top + 0.018),
              (24.0 * IN, rubber_depth, 0.035), angle=rubber_angle)

    # Chalked batter boxes: 4 ft wide x 6 ft long, with a 6-inch inside gap
    # from the plate.  Catcher's box is 8 ft long x 43 inches wide.
    batter_length = 6.0 * FT
    batter_width = 4.0 * FT
    plate_center = Vector((0.0, 0.0)) + axis * 0.22
    lateral_center = 0.5 * (17.0 * IN) + 6.0 * IN + batter_width * 0.5
    for sign in (-1.0, 1.0):
        center = plate_center + across * (sign * lateral_center) - axis * 0.13
        corners = _rect_corners(center, axis, across, batter_length, batter_width)
        _outline(batch, corners, chalk_z)

    catcher_center = -axis * 1.36
    catcher_corners = _rect_corners(catcher_center, axis, across,
                                     8.0 * FT, 43.0 * IN)
    _outline(batch, catcher_corners, chalk_z)

    # Preserve the dimensional audit in the saved scene for later verification
    # and make the inferred-vs-regulated boundary explicit to downstream tools.
    scene['field_builder'] = 'r3_field'
    scene['field_group'] = GROUP
    scene['field_base_path_m'] = base_path
    scene['field_mound_distance_m'] = mound_distance
    scene['field_pitcher_plate_front_distance_m'] = rubber_front_distance
    scene['field_warning_track_width_m'] = track_width
    scene['field_boundary_basis'] = 'scene-spec field_boundary and bowl_front; inferred concept geometry'
