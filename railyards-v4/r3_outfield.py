"""Source-supported outfield banks, terraces, batter's eye, and fence posts.

The field builder owns the playing surface. This module adds only the
outfield elements visible beyond the traced ``field_boundary``. Banks are
split around the visible right-field board, center-field board/batter's-eye
void, and left-field pavilion approach; scoreboards and buildings remain in
their own modules.
"""

import math,random
import bpy
from r2_geometry import instances

from mathutils import Vector


GROUP = 'Outfield'


def _xy(point):
    return Vector((float(point[0]), float(point[1])))


def _unit(point):
    result = Vector((point[0], point[1]))
    return result.normalized() if result.length > 1e-6 else Vector((1.0, 0.0))


def _sample_segment(a, b, spacing):
    length = (b - a).length
    count = max(1, int(math.ceil(length / spacing)))
    return [a.lerp(b, index / count) for index in range(count + 1)]


def _path_pieces(path, ranges):
    """Yield subsegments whose normalized path distance is in ``ranges``."""
    lengths = [(b - a).length for a, b in zip(path, path[1:])]
    total = sum(lengths)
    if total < 1e-6:
        return
    cursor = 0.0
    for a, b, length in zip(path, path[1:], lengths):
        start, end = cursor / total, (cursor + length) / total
        for low, high in ranges:
            overlap_low, overlap_high = max(start, low), min(end, high)
            if overlap_high - overlap_low > 1e-5:
                ta = (overlap_low - start) / (end - start)
                tb = (overlap_high - start) / (end - start)
                yield a.lerp(b, ta), a.lerp(b, tb)
        cursor += length


def _offset_segment(a, b, distance):
    return a + _unit(a) * distance, b + _unit(b) * distance


def _open_sections(a, b, period=17.0, aisle_width=1.55):
    """Yield open seating sections and aisle sections along one path piece."""
    length = (b - a).length
    tangent = (b - a).normalized()
    cursor = 0.0
    while cursor < length - 1e-5:
        cell_end = min(length, cursor + period)
        gap_start = max(cursor, cell_end - aisle_width)
        if gap_start - cursor > 1e-5:
            yield 'seat', a + tangent * cursor, a + tangent * gap_start
        if cell_end - gap_start > 1e-5:
            yield 'aisle', a + tangent * gap_start, a + tangent * cell_end
        cursor = cell_end


def build_outfield(scene, spec, batch, materials):
    """Add discrete outfield banks around the source-traced field boundary."""
    z = float(spec.get('field_z', 12.0))
    rng=random.Random(1431);seats=[];seat_rot=[]
    fan_positions=[[]for _ in range(6)];fan_rotations=[[]for _ in range(6)]
    boundary = [_xy(point) for point in spec['field_boundary']]

    # The low wall and posts remain continuous because they define the field
    # edge. Seating banks are intentionally discontinuous around source-visible
    # board/building voids below.
    wall_height = 1.35
    for a, b in zip(boundary, boundary[1:]):
        edge = b - a
        if edge.length < 1e-5:
            continue
        tangent = edge.normalized()
        normal = _unit((a + b) * 0.5)
        center = (a + b) * 0.5 + normal * 0.28
        batch.box(GROUP, 'seat', (center.x, center.y, z + wall_height * 0.5),
                  (edge.length + 0.08, 0.48, wall_height),
                  angle=math.atan2(tangent.y, tangent.x))
        for point in _sample_segment(a, b, 5.0)[:-1]:
            post = point + _unit(point) * 0.54
            batch.cylinder(GROUP, 'metal', (post.x, post.y, z + 0.05),
                           (post.x, post.y, z + wall_height + 0.32),
                           0.045, sides=6)

    # Normalized locations are measured from the right-field foul endpoint to
    # the left-field foul endpoint. Gaps correspond to the RF board, the large
    # CF board/restaurant/batter's-eye void, and the LF pavilion approach seen
    # in the full-resolution north aerial and adjacent-building source regions.
    # V4: the RF gap (0.094-0.317) is the RF board footprint plus 1.5 m
    # clearance, computed from the boundary path lengths (board spans wall
    # y 18.5-55.5).  Terraces stay within the 9.5 m podium ring so nothing
    # overhangs the lower riverwalk (quay slab starts at x 112).
    # V12: the RF corner (to the board) and the left-center range are built
    # by r12_outfield as taller banks; only the RF-board-to-CF bank and the
    # small LF-pole bank remain as low terraces here.
    bank_ranges = [(0.0445, 0.094), (0.317, 0.47), (0.94, 0.985)]
    terraces = [(1.45, 4.10, 13.65),
                (4.10, 6.80, 15.05),
                (6.80, 9.40, 16.45)]
    rows_per_terrace = 3
    row_rise = 0.28
    for inner_offset, outer_offset, base_level in terraces:
        row_depth = (outer_offset - inner_offset) / rows_per_terrace
        for row in range(rows_per_terrace):
            front_offset = inner_offset + row * row_depth
            rear_offset = front_offset + row_depth
            level = base_level + row * row_rise
            previous_level = level - row_rise if row else level - 0.16
            for piece_a, piece_b in _path_pieces(boundary, bank_ranges):
                front_a, front_b = _offset_segment(piece_a, piece_b, front_offset)
                rear_a, rear_b = _offset_segment(piece_a, piece_b, rear_offset)
                for kind, a, b in _open_sections(front_a, front_b):
                    piece_length = max(1e-6, (front_b - front_a).length)
                    t0 = (a - front_a).length / piece_length
                    t1 = (b - front_a).length / piece_length
                    ra = rear_a.lerp(rear_b, t0)
                    rb = rear_a.lerp(rear_b, t1)
                    tangent = (b - a).normalized()
                    angle = math.atan2(tangent.y, tangent.x)
                    if kind == 'seat':
                        # Each row is a real horizontal tread with a front
                        # riser; seats land on that tread rather than floating
                        # above one broad terrace slab.
                        batch.prism(GROUP, 'concrete',
                                    [(a.x, a.y), (b.x, b.y),
                                     (rb.x, rb.y), (ra.x, ra.y)],
                                    level - 0.08, level)
                        batch.box(GROUP, 'concrete',
                                  ((a.x + b.x) * 0.5, (a.y + b.y) * 0.5,
                                   (level + previous_level) * 0.5),
                                  ((b - a).length + 0.04, 0.14,
                                   level - previous_level), angle=angle)
                        for seat in _sample_segment(a, b, .58)[:-1]:
                            seat = seat + _unit(seat) * (row_depth * 0.55)
                            position=(seat.x,seat.y,level)
                            seats.append(position);seat_rot.append((0,0,angle))
                            if rng.random()<.78:
                                color=rng.choices(range(6),[32,27,18,15,5,3])[0]
                                fan_positions[color].append(position);fan_rotations[color].append((0,0,angle))
                    else:
                        # Concrete aisle tread fills the intentional gap and
                        # makes a continuous radial access stair through rows.
                        aisle_center = (a + b) * 0.5 + _unit((a + b) * 0.5) * (row_depth * 0.5)
                        batch.box(GROUP, 'concrete',
                                  (aisle_center.x, aisle_center.y, level + 0.01),
                                  ((b - a).length, row_depth, 0.12), angle=angle)

    # The dark center-field batter's eye occupies the central source void. Its
    # placement follows the middle field-boundary vertex instead of a board or
    # restaurant anchor so it survives later adjacent-building revisions.
    center_index = len(boundary) // 2
    center = boundary[center_index]
    if 0 < center_index < len(boundary) - 1:
        tangent = (boundary[center_index + 1] - boundary[center_index - 1]).normalized()
    else:
        tangent = Vector((1.0, 0.0))
    radial = _unit(center)
    eye_center = center + radial * 12.0
    eye_height = 11.0
    batch.box(GROUP, 'seat', (eye_center.x, eye_center.y,
                               z + 0.55 + eye_height * 0.5),
              (26.0, 0.55, eye_height),
              angle=math.atan2(tangent.y, tangent.x))
    batch.box(GROUP, 'seat', (eye_center.x, eye_center.y, z + 0.78),
              (28.0, 1.5, 0.32), angle=math.atan2(tangent.y, tangent.x))

    source=bpy.data.objects.get('D2_Seat source')
    if source:instances(scene,batch.collection(GROUP),'Outfield individual seats',source,seats,seat_rot)
    for k,color in enumerate(['cloth_black','cloth_white','cloth_gray','navy','cloth_blue','cloth_red']):
        person=bpy.data.objects.get('D2_Seated fan '+color)
        if person and fan_positions[k]:instances(scene,batch.collection(GROUP),'Outfield spectators '+color,person,fan_positions[k],fan_rotations[k])
    scene['bowl_seat_count']=scene['seat_count'];scene['outfield_seat_count']=len(seats)
    scene['seat_count']+=len(seats);scene['spectator_count']+=sum(map(len,fan_positions))
    scene['outfield_builder'] = 'r3_outfield'
    scene['outfield_group'] = GROUP
    scene['outfield_source_basis'] = 'full-resolution north AECOM aerial and scene-spec field_boundary'
    scene['outfield_bank_ranges'] = str(bank_ranges)
    scene['outfield_terrace_basis'] = 'discrete visual estimate; gaps preserve source board/building voids'
    scene['outfield_batter_eye_basis'] = 'center-field boundary-derived inferred screen'
