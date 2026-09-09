"""V15 seating correction for the two exposed return-bank pairs.

The V14 LF and RF returns used quadratic station curves.  That made adjacent
rows change direction as they approached the pavilions and left the chairs,
aisle cuts and support lines difficult to read as one structure.  V15 keeps
the V14 two-bank/two-box interpretation on both sides, but makes each exposed
row a straight ruled line with a constant row pitch.  The RF bank junction is
also given a bounded concourse transition so its source-visible tier ends do
not float over an empty triangular void.

This module only contributes seating and immediately supporting return-bank
access geometry.  It does not change the park/left-center circulation, field,
scoreboards, tower or roof.  Dimensions remain reconstruction inferences; the
returned receipt identifies the views that still require inspection.
"""

import json
import math
import random

import bpy
from mathutils import Matrix, Vector

from r11_circulation import rail
from r13_outfield import remove_collection
from r2_geometry import instances


# These are the two exposed LF banks already established by the V14 source
# comparison.  The gaps at t=.34-.40 and the two box floors behind them are
# intentional; they are not a request to add a third exposed seating tier.
LF_BANKS = (
    {
        "name": "lower",
        "inner": "radial",
        "parallel": (41.1, 6.8),
        "end_x": 24.0,
        "depth_scale": 62.0,
        "t0": 0.00,
        "t1": 0.34,
        "z0": 14.0,
        "z1": 24.0,
        "rows": 24,
        "end0": (24.0, 110.85),
        "end1": (24.0, 137.00),
    },
    # 2026-09-08 user correction: drop the rearmost row that sat under the box
    # floors. Seven rows keep the original 8-row pitch and rise (t1, z1 and
    # end1 are scaled by 7/8), so the bank shortens at the rear only.
    {
        "name": "upper",
        "inner": "back",
        "parallel": (41.1, 6.8),
        "end_x": 24.0,
        "depth_scale": 62.0,
        "t0": 0.40,
        "t1": 0.47875,
        "z0": 27.0,
        "z1": 29.625,
        "rows": 7,
        "end0": (24.0, 134.80),
        "end1": (24.0, 141.3625),
    },
)

# RF retains the two source-derived exposed bank counts and the authored V13 /
# V14 endpoints.  Unlike the LF pair, the source upper bank starts towerward
# of the lower bank's rear cap.  The explicit junction transition below fills
# that offset as a concourse landing with visible guards and supports; it does
# not turn the offset into an extra seating tier.
RF_BANKS = (
    {
        "name": "lower",
        "t0": 0.00,
        "t1": 0.34,
        "z0": 14.0,
        "z1": 24.0,
        "rows": 24,
        # 2026-09-09 (Josh, rf thumbs-down "wonky like the angled seating"):
        # rows parallel to the first row's line to the RF wall corner, ending
        # on one straight line through (102, 2), inner ends on the bowl radial.
        "inner": "radial",
        "parallel": (26.8, 22.9),
        "end_line": (102.0, 2.0),
        "depth_scale": 62.0,
        "end0": (102.0, 2.0),
        "end1": (111.0, -35.0),
    },
    {
        "name": "upper",
        "t0": 0.40,
        "t1": 0.49,
        "z0": 27.0,
        "z1": 30.0,
        "rows": 8,
        "inner": "radial",
        "parallel": (26.8, 22.9),
        "end_line": (102.0, 2.0),
        "depth_scale": 62.0,
        "end0": (101.2, -37.0),
        "end1": (101.2, -47.0),
    },
)

SEAT_PITCH = 0.56
# Keep the chair feet and backs clear of the open bank ends.  The V14
# endpoint landed on the shared lower-concourse guard and upper terrace edge;
# this source-guided two-and-a-half metre buffer is the smallest regular
# setback that leaves a readable row while preserving the bank shape.
SEAT_INSET = 2.50
AISLE_CENTERS = (0.34, 0.68)
AISLE_WIDTH = 1.20
# Leave room for a chair envelope beside the aisle rail.  This is applied in
# metres around the aisle center, so it follows changing row lengths without
# hiding seats by object index.
AISLE_SEAT_CLEARANCE = 0.30
FOUNDATION_Z = 8.0


def _line_xy(front, back, bank, t, station):
    """Return a planar point on a straight return-bank row.

    The inner endpoint follows the registered bowl depth line and the outer
    endpoint follows the source-guided faceted return edge.  Interpolating
    those endpoints directly is the important V15 change: for fixed ``t``,
    the row is affine in ``station`` and cannot bow through neighboring rows.
    """
    depth_point = front.lerp(back, t)
    if "parallel" in bank:
        # 2026-09-09 (Josh): LF rows run parallel to the left-field wall and
        # end on one straight line (the right-hand wall at x = end_x), so the
        # bank is a parallelogram instead of a fan.
        # Depth is measured perpendicular to the rows (t * depth_scale metres
        # back from the foul-pole corner), so the row pitch is uniform instead
        # of inheriting the fan's converging spacing along the bowl radial.
        w = Vector((bank["parallel"][0], bank["parallel"][1], 0.0)).normalized()
        n = Vector((-w.y, w.x, 0.0))
        f = Vector((front.x, front.y, 0.0))
        b = Vector((back.x, back.y, 0.0))
        if n.dot(b - f) < 0.0:
            n = -n  # depth always runs from the field toward the bowl back
        depth = t * bank["depth_scale"]
        if bank.get("inner") == "radial":
            # 2026-09-09 (Josh): lower rows run on to the bowl's end radial,
            # so each row starts where its line meets the radial.
            d = (b - f).normalized()
            depth_point = f + d * (depth / d.dot(n))
        elif bank.get("inner") == "back":
            # Upper rows start on a line straight back from the bowl's rear corner.
            depth_point = b + n * (depth - (b - f).dot(n))
        else:
            depth_point = f + n * depth
        if "end_line" in bank:
            # Rows end on the straight line through end_line, perpendicular to the rows.
            p0 = Vector((bank["end_line"][0], bank["end_line"][1], 0.0))
            outer = p0 + n * (depth_point - p0).dot(n)
            return depth_point.lerp(outer, station)
        return depth_point + w * ((bank["end_x"] - depth_point.x) / w.x * station)
    fraction = (t - bank["t0"]) / (bank["t1"] - bank["t0"])
    outer = Vector((
        bank["end0"][0] + (bank["end1"][0] - bank["end0"][0]) * fraction,
        bank["end0"][1] + (bank["end1"][1] - bank["end0"][1]) * fraction,
        0.0,
    ))
    depth_point.z = 0.0
    return depth_point.lerp(outer, station)


def _line(front, back, bank, t, station, z):
    point = _line_xy(front, back, bank, t, station)
    point.z = z
    return point


def _solid_quad(batch, group, material, points, bottom):
    """Add a thin solid under a horizontal four-point tread."""
    top = [Vector(point) for point in points]
    area = sum(a.x * b.y - b.x * a.y for a, b in zip(top, top[1:] + top[:1]))
    if area < 0.0:
        top.reverse()
    lower = [Vector((point.x, point.y, bottom)) for point in top]
    vertices = [tuple(point) for point in lower + top]
    batch.add(
        group,
        material,
        vertices,
        [
            (3, 2, 1, 0),
            (4, 5, 6, 7),
            (0, 1, 5, 4),
            (1, 2, 6, 5),
            (2, 3, 7, 6),
            (3, 0, 4, 7),
        ],
    )


def _vertical_quad(batch, group, material, points):
    """Add the four-point vertical face at a row riser.

    ``points`` is ordered as lower edge start/end followed by upper edge
    end/start.  Keeping the face in one list avoids a misleading two-list
    API: the lower and upper edges meet at the same row boundary and the
    riser is intentionally a single thin surface.
    """
    vertices = [tuple(Vector(point)) for point in points]
    batch.add(group, material, vertices, [(0, 1, 2, 3)])


def _station_segments(length):
    """Return straight row intervals split at the two common aisle cuts."""
    cuts = [0.0, 1.0]
    for center in AISLE_CENTERS:
        half = AISLE_WIDTH / max(2.0 * length, 1e-6)
        cuts.extend((max(0.0, center - half), min(1.0, center + half)))
    cuts = sorted(set(round(value, 8) for value in cuts))
    result = []
    for start, end in zip(cuts, cuts[1:]):
        if end - start < 1e-5:
            continue
        middle = (start + end) * 0.5
        aisle = any(abs(middle - center) < 0.02 for center in AISLE_CENTERS)
        result.append((start, end, aisle))
    return result


def _add_bank_edge_continuum(batch, front, back, bank, group, edge):
    """Close one bank edge with a shallow landing, coping and guard.

    A bank's first row datum is a foul-pole-side termination on the LF and a
    lower return termination on the RF.  Giving both datums the same small
    perimeter treatment keeps the row field from ending at a bare vertical
    cut.  The landing is outside the seat centers and follows the authored
    straight edge, so it does not add a hidden seating tier.
    """
    if edge == "front":
        edge_t = bank["t0"]
        landing_t = edge_t - 0.022
        level = bank["z0"]
    elif edge == "rear":
        edge_t = bank["t1"]
        landing_t = edge_t + 0.022
        level = bank["z1"]
    else:
        raise ValueError("return-bank edge must be 'front' or 'rear'")

    top = [
        _line(front, back, bank, landing_t, 0.02, level),
        _line(front, back, bank, landing_t, 0.98, level),
        _line(front, back, bank, edge_t, 0.98, level),
        _line(front, back, bank, edge_t, 0.02, level),
    ]
    _solid_quad(batch, group, "stone", top, level - 0.30)

    # The low stone beam is the coping.  The metal rail is set on its outer
    # edge and returns at both ends so the landing reads as a usable perimeter
    # route from either adjacent bank/cross-aisle.
    coping_start = top[0] + Vector((0.0, 0.0, 0.12))
    coping_end = top[1] + Vector((0.0, 0.0, 0.12))
    batch.cylinder(group, "stone", coping_start, coping_end, 0.14, sides=8)
    rail(batch, group, top[0], top[1], 1.05)
    for station in (0.02, 0.98):
        rail(
            batch,
            group,
            _line(front, back, bank, landing_t, station, level),
            _line(front, back, bank, edge_t, station, level),
            0.95,
        )
    return {
        "edge": edge,
        "edge_t": edge_t,
        "landing_t": landing_t,
        "level": level,
        "station_range": [0.02, 0.98],
        "coping": True,
        "guard": True,
    }


def _add_row_surfaces(scene, batch, front, back, bank, group, side):
    """Build level treads, visible risers, seats and the two aisle rails."""
    rng = random.Random(1515 + (0 if bank["name"] == "lower" else 1))
    seats = []
    rotations = []
    row_levels = []
    fans = [[] for _ in range(6)]
    fan_rotations = [[] for _ in range(6)]
    rows = bank["rows"]
    dt = (bank["t1"] - bank["t0"]) / rows
    rise = (bank["z1"] - bank["z0"]) / rows
    row_pitch = (
        _line_xy(front, back, bank, bank["t1"], 0.5)
        - _line_xy(front, back, bank, bank["t0"], 0.5)
    ).length / rows

    for row in range(rows):
        t0 = bank["t0"] + dt * row
        t1 = bank["t0"] + dt * (row + 1)
        level = bank["z0"] + rise * row
        previous_level = level - rise if row else level - 0.35
        # Seat positions must use this row's depth station.  Reusing one
        # bank-wide midpoint would stack every row at the same XY location
        # while leaving their level metadata apparently correct.
        row_center_t = (t0 + t1) * 0.5
        inner = _line_xy(front, back, bank, row_center_t, 0.0)
        outer = _line_xy(front, back, bank, row_center_t, 1.0)
        length = (outer - inner).length
        intervals = _station_segments(length)

        # Every tread is its own small, level solid.  Segments at the two
        # aisle cuts deliberately keep the same level and material so the
        # stairs are visibly walkable instead of being black holes in the
        # row field.
        for start, end, aisle in intervals:
            top = [
                _line(front, back, bank, t0, start, level),
                _line(front, back, bank, t0, end, level),
                _line(front, back, bank, t1, end, level),
                _line(front, back, bank, t1, start, level),
            ]
            _solid_quad(batch, group, "stone" if aisle else "concrete", top, level - 0.32)

            # The short vertical edge at each row boundary makes the pitch
            # legible from the field and keeps the stepped rake watertight.
            if row:
                low = [
                    _line(front, back, bank, t0, start, previous_level),
                    _line(front, back, bank, t0, end, previous_level),
                ]
                high = [
                    _line(front, back, bank, t0, end, level),
                    _line(front, back, bank, t0, start, level),
                ]
                _vertical_quad(batch, group, "stone", low + high)

        # Seats follow the same straight row centerline as the treads.  A
        # world-distance cursor keeps pitch uniform even as the return edge
        # changes angle from one facet to the next.
        tangent = outer - inner
        tangent.normalize()
        toward = _line_xy(front, back, bank, t0, 0.5) - _line_xy(front, back, bank, t1, 0.5)
        left = Vector((-tangent.y, tangent.x, 0.0))
        if left.dot(toward) < 0.0:
            tangent = -tangent
        angle = math.atan2(tangent.y, tangent.x)
        first = SEAT_INSET
        last = length - SEAT_INSET
        distance = first
        while distance <= last + 1e-6:
            station = distance / max(length, 1e-6)
            seat_clear = 0.245
            blocked = any(
                abs(distance - center * length)
                < AISLE_WIDTH * 0.5 + seat_clear + AISLE_SEAT_CLEARANCE
                for center in AISLE_CENTERS
            )
            if not blocked:
                point = _line(front, back, bank, row_center_t, station, level)
                position = tuple(point)
                seats.append(position)
                rotations.append((0.0, 0.0, angle))
                row_levels.append(level)
                if rng.random() < 0.80:
                    color = rng.choices(range(6), [32, 27, 18, 15, 5, 3])[0]
                    fans[color].append(position)
                    fan_rotations[color].append((0.0, 0.0, angle))
            distance += SEAT_PITCH

        # Handrails run down both sides of each straight aisle.  Split at
        # every row so each rail follows the actual rake instead of becoming
        # a curved chord through the seats.
        for center in AISLE_CENTERS:
            half = AISLE_WIDTH / max(2.0 * length, 1e-6)
            for station in (center - half, center + half):
                if station <= 0.0 or station >= 1.0:
                    continue
                start = _line(front, back, bank, t0, station, level)
                end = _line(front, back, bank, t1, station, level)
                rail(batch, group, start, end, 0.92)

    # Both ends receive a shallow perimeter route.  The front treatment is
    # the visible LF foul-pole-side fix; keeping the same datum on RF and on
    # the upper banks makes the two-bank read consistent at every turn.
    edge_continuum = {
        edge: _add_bank_edge_continuum(front=front, back=back, bank=bank, group=group, batch=batch, edge=edge)
        for edge in ("front", "rear")
    }

    source = bpy.data.objects.get("D2_Seat source")
    seat_object = None
    collection = batch.collection(group)
    if source is not None and seats:
        # The replay/export pipeline groups every modeled chair by the
        # literal "individual seats" marker, so keep that contract while
        # retaining the bank label for inspection and seat-map metadata.
        seat_object = instances(
            scene,
            collection,
            side + " " + bank["name"] + " straight individual seats",
            source,
            seats,
            rotations,
        )
        row_attribute = seat_object.data.attributes.new("row_elevation", "FLOAT", "POINT")
        row_attribute.data.foreach_set("value", row_levels)
    for index, color in enumerate(
        ["cloth_black", "cloth_white", "cloth_gray", "navy", "cloth_blue", "cloth_red"]
    ):
        person = bpy.data.objects.get("D2_Seated fan " + color)
        if person is not None and fans[index]:
            instances(
                scene,
                collection,
                side + " " + bank["name"] + " straight spectators " + color,
                person,
                fans[index],
                fan_rotations[index],
            )

    return {
        "name": bank["name"],
        "rows": rows,
        "seats": len(seats),
        "spectators": sum(len(bucket) for bucket in fans),
        "t_range": [bank["t0"], bank["t1"]],
        "levels": [bank["z0"], bank["z1"]],
        "row_pitch_m": round(row_pitch, 4),
        "row_rise_m": round(rise, 4),
        "seat_pitch_m": SEAT_PITCH,
        "seat_end_clearance_m": SEAT_INSET,
        "aisle_centers": list(AISLE_CENTERS),
        "aisle_width_m": AISLE_WIDTH,
        "aisle_seat_clearance_m": AISLE_SEAT_CLEARANCE,
        "edge_continuum": edge_continuum,
        "endpoint_rule": "Linear interpolation between bowl depth line and faceted return edge",
    }


def _build_bank_support(scene, batch, front, back, bank, side):
    """Carry one bank's rake to the existing conceptual z8 foundation."""
    group = "V15 " + side + " seating structure"
    t0, t1 = bank["t0"], bank["t1"]
    # Carry the rakers below the two open aisle cuts.  The earlier five-line
    # fan crossed chair feet near the inner end; aisle-aligned supports keep
    # the visible structure load-bearing while retaining clear seats.
    support_stations = AISLE_CENTERS
    for station in support_stations:
        low = _line(front, back, bank, t0, station, bank["z0"] - 0.42)
        high = _line(front, back, bank, t1, station, bank["z1"] - 0.42)
        batch.cylinder(group, "concrete", low, high, 0.23, sides=8)

        # The return edge is outside the bowl and is the least speculative
        # place for visible columns.  Keep the bowl edge open to the existing
        # main seating and its concourse.
        column_top = _line(front, back, bank, t1 + 0.004, station, bank["z1"] - 0.52)
        batch.cylinder(
            group,
            "concrete",
            (column_top.x, column_top.y, FOUNDATION_Z),
            column_top,
            0.27,
            sides=8,
        )
        batch.box(group, "stone", (column_top.x, column_top.y, FOUNDATION_Z - 0.10), (0.95, 0.95, 0.20))
    # A rear beam makes the two columns at each station read as one supported
    # return rather than isolated posts.
    beam_start = _line(front, back, bank, t1 + 0.004, 0.03, bank["z1"] - 0.48)
    beam_end = _line(front, back, bank, t1 + 0.004, 0.97, bank["z1"] - 0.48)
    batch.cylinder(group, "concrete", beam_start, beam_end, 0.20, sides=8)


def _gap_point(front, back, lower, upper, station, fraction, z):
    """Interpolate between the two authored bank edges across their gap."""
    lower_edge = _line_xy(front, back, lower, lower["t1"], station)
    upper_edge = _line_xy(front, back, upper, upper["t0"], station)
    point = lower_edge.lerp(upper_edge, fraction)
    point.z = z
    return point


def _build_interbank_access(scene, batch, front, back):
    """Connect the two exposed banks through their source-visible gap.

    The images establish a bright separation between the long lower bank and
    the shorter upper bank, but they do not expose a surveyed tunnel plan.  A
    shallow lower landing plus a short stair at one shared aisle station is
    therefore used as the smallest useful access interpretation.
    """
    group = "V15 LF bank access"
    lower, upper = LF_BANKS
    # Align the narrow connector with the second lower-bank aisle.  The
    # access spans a useful walking width instead of becoming a full-width
    # cross stair that reads as a hidden third seating bank.
    center = AISLE_CENTERS[1]
    lower_edge_length = (
        _line_xy(front, back, lower, lower["t1"], 1.0)
        - _line_xy(front, back, lower, lower["t1"], 0.0)
    ).length
    half_width = AISLE_WIDTH / max(2.0 * lower_edge_length, 1e-6)
    station0, station1 = center - half_width, center + half_width
    landing_fraction = 0.18
    landing_top = 24.08
    landing = [
        _gap_point(front, back, lower, upper, station0, 0.0, landing_top),
        _gap_point(front, back, lower, upper, station1, 0.0, landing_top),
        _gap_point(front, back, lower, upper, station1, landing_fraction, landing_top),
        _gap_point(front, back, lower, upper, station0, landing_fraction, landing_top),
    ]
    _solid_quad(batch, group, "paving", landing, landing_top - 0.22)

    # Six shallow steps close the 2.9 m level difference to the upper bank's
    # front edge, leaving the seating banks and the box floors untouched.
    steps = 6
    for index in range(steps):
        a = landing_fraction + (1.0 - landing_fraction) * index / steps
        b = landing_fraction + (1.0 - landing_fraction) * (index + 1) / steps
        level = landing_top + (upper["z0"] - landing_top) * (index + 1) / steps
        tread = [
            _gap_point(front, back, lower, upper, station0, a, level),
            _gap_point(front, back, lower, upper, station1, a, level),
            _gap_point(front, back, lower, upper, station1, b, level),
            _gap_point(front, back, lower, upper, station0, b, level),
        ]
        _solid_quad(batch, group, "stone", tread, level - 0.18)

    # Side guards follow the connector edges.  They are intentionally
    # compact: the source supports access between banks, not a broad new
    # enclosure across the field-facing composition.
    for station in (station0, station1):
        points = []
        for index in range(steps + 1):
            fraction = landing_fraction + (1.0 - landing_fraction) * index / steps
            z = landing_top + (upper["z0"] - landing_top) * index / steps
            points.append(_gap_point(front, back, lower, upper, station, fraction, z))
        for first, second in zip(points, points[1:]):
            rail(batch, group, first, second, 0.95)

    return {
        "levels": [landing_top, upper["z0"]],
        "gap_t": [lower["t1"], upper["t0"]],
        "landing_fraction": landing_fraction,
        "station_fraction": center,
        "stair_steps": steps,
        "width_m": round((station1 - station0) * lower_edge_length, 2),
        "basis": "Open separation between the V14 two-bank interpretation; exact tunnel plan remains inferred",
    }


def _build_rf_junction(scene, batch, front, back):
    """Join the authored RF bank ends with a compact supported concourse.

    The V13/V14 RF endpoints intentionally put the upper bank towerward of
    the lower rear cap.  That offset is useful source evidence, but the old
    curved rows left it as a dark triangular void.  This transition keeps the
    two exposed seat banks and their authored ends while making the intervening
    datum a walkable, stepped concourse with a perimeter coping, guards and
    visible columns.  It has no seat centers.
    """
    group = "V15 RF return junction"
    lower, upper = RF_BANKS
    station0, station1 = 0.04, 0.96
    lower_level = lower["z1"]
    upper_level = upper["z0"]
    steps = 5

    # A shallow five-module transition reads as the source's broad concourse
    # break instead of a single floating slab.  The first and last modules are
    # landings; the three middle modules supply the modest level change.
    for index in range(steps):
        fraction0 = index / steps
        fraction1 = (index + 1) / steps
        level0 = lower_level + (upper_level - lower_level) * fraction0
        level1 = lower_level + (upper_level - lower_level) * fraction1
        module = [
            _gap_point(front, back, lower, upper, station0, fraction0, level0),
            _gap_point(front, back, lower, upper, station1, fraction0, level0),
            _gap_point(front, back, lower, upper, station1, fraction1, level1),
            _gap_point(front, back, lower, upper, station0, fraction1, level1),
        ]
        _solid_quad(batch, group, "paving" if index in (0, steps - 1) else "stone", module, min(level0, level1) - 0.22)

    # Continuous coping at each bank datum and a guard along both side edges
    # close the junction perimeter.  The rails sit in the gap and therefore
    # remain outside every RF seat center.
    lower_start = _gap_point(front, back, lower, upper, station0, 0.0, lower_level)
    lower_end = _gap_point(front, back, lower, upper, station1, 0.0, lower_level)
    upper_start = _gap_point(front, back, lower, upper, station0, 1.0, upper_level)
    upper_end = _gap_point(front, back, lower, upper, station1, 1.0, upper_level)
    for start, end in ((lower_start, lower_end), (upper_start, upper_end)):
        batch.cylinder(group, "stone", start, end, 0.16, sides=8)
        rail(batch, group, start, end, 1.02)

    for station in (station0, station1):
        points = []
        for index in range(steps + 1):
            fraction = index / steps
            level = lower_level + (upper_level - lower_level) * fraction
            points.append(_gap_point(front, back, lower, upper, station, fraction, level))
        for start, end in zip(points, points[1:]):
            rail(batch, group, start, end, 0.95)

    # This short transition bears on the supported rear edge of the lower
    # bank and front edge of the upper bank. Additional piers through the
    # lower row would obstruct chairs, so the bank frames carry its ends.

    return {
        "banks": [lower["name"], upper["name"]],
        "gap_t": [lower["t1"], upper["t0"]],
        "station_range": [station0, station1],
        "levels": [lower_level, upper_level],
        "transition_modules": steps,
        "landings": [0, steps - 1],
        "coping": True,
        "guards": True,
        "supports": {
            "foundation_z": FOUNDATION_Z,
            "bearing": "Existing supported bank edges",
            "outside_seats": True,
        },
        "seat_centers": 0,
        "basis": "V13/V14 authored RF endpoints joined by an inferred concourse transition; no extra exposed seating tier",
    }


def _close_lf_rear(scene, batch, front, back):
    """Close the open back of the LF banks with a wall and a plaza deck.

    2026-09-08 review (Josh, thumbs-down on the LF wide view): rays cast
    outward from behind the LF banks travelled 22-55 m before hitting the
    pavilion brick, from the paving at z 8 up to the lower box floor, so the
    stands read as floating.  A first pass filled the void with a brick block.
    Josh's 2026-09-09 AECOM crop of the LF corner shows something else: the
    stands back onto a white concourse plaza at deck level, with a canopy
    pavilion on it, and the rear of the stands is a solid pale wall down to
    that deck.  So this builds (a) a 1.5 m stone wall on the upper bank's rear
    edge from the paving to the underside of the lower box floor and (b) a
    stone plaza deck at the existing court level (z 14.48) running from that
    wall back to the first gallery / pavilion surface per station (4-30 m).
    Nothing existing is removed.
    """
    bank = LF_BANKS[1]
    stations = 12
    z0, z1 = 8.0, 31.55
    deck_top, deck_thick, wall_thick = 14.48, 0.5, 1.5
    depsgraph = bpy.context.evaluated_depsgraph_get()
    d = (_line_xy(front, back, bank, bank["t1"], 0.5) - _line_xy(front, back, bank, bank["t0"], 0.5)).normalized()
    depths = []
    for i in range(stations + 1):
        origin = _line_xy(front, back, bank, bank["t1"], i / stations)
        origin.z = 31.0
        hit, loc, _n, _i, obj, _m = scene.ray_cast(depsgraph, origin + d * 0.3, d, distance=40.0)
        depth = (loc - origin).length if hit and (obj.name.startswith("D2_V14 LF pavilion") or obj.name.startswith("D2_Left field pavilion")) else 10.0
        depths.append(max(4.0, min(30.0, depth)))
    group = "V15 LF rear enclosure"
    faces = [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    for i in range(stations):
        s0, s1 = i / stations, (i + 1) / stations
        f0 = _line_xy(front, back, bank, bank["t1"], s0)
        f1 = _line_xy(front, back, bank, bank["t1"], s1)
        w0, w1 = f0 + d * wall_thick, f1 + d * wall_thick
        corners = [f0, f1, w1, w0]
        batch.add(group, "stone", [(c.x, c.y, z0) for c in corners] + [(c.x, c.y, z1) for c in corners], faces)
        b0 = f0 + d * depths[i]
        b1 = f1 + d * depths[i + 1]
        corners = [w0, w1, b1, b0]
        batch.add(group, "stone", [(c.x, c.y, deck_top - deck_thick) for c in corners] + [(c.x, c.y, deck_top) for c in corners], faces)
    return {"stations": stations, "depths_m": [round(v, 2) for v in depths], "wall_z": [z0, z1], "wall_thickness_m": wall_thick, "deck_top_z": deck_top, "group": group,
            "source": "Josh 2026-09-09 AECOM LF-corner crop (plaza + canopy pavilion behind the stands)"}


def _build_lf_end_wall(batch, front, back):
    """Right-hand (pavilion-side) wall closing the LF banks at x = end_x.

    2026-09-09 (Josh): the wall follows the seats as they rise to the
    building instead of standing full height.  Its top is the rake profile
    at station 1 plus a 1.1 m parapet, stepping up to the box-floor level
    only at the rear.
    """
    lower, upper = LF_BANKS
    w = Vector((upper["parallel"][0], upper["parallel"][1], 0.0)).normalized()
    parapet, z0, z_top = 1.1, 8.0, 31.55
    profile = [
        (lower, lower["t0"], lower["z0"] + parapet),
        (lower, lower["t1"], lower["z1"] + parapet),
        (upper, upper["t0"], upper["z0"] + parapet),
        (upper, upper["t1"], upper["z1"] + parapet),
    ]
    pts = [_line_xy(front, back, bank, tt, 1.0) for bank, tt, _z in profile]
    zs = [z for _b, _t, z in profile]
    group = "V15 LF end wall"
    faces = [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    segments = []
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        za, zb = zs[i], zs[i + 1]
        a2, b2 = a + w * 1.2, b + w * 1.2
        verts = [(a.x, a.y, z0), (b.x, b.y, z0), (b2.x, b2.y, z0), (a2.x, a2.y, z0),
                 (a.x, a.y, za), (b.x, b.y, zb), (b2.x, b2.y, zb), (a2.x, a2.y, za)]
        batch.add(group, "stone", verts, faces)
        segments.append([round(a.y, 2), round(b.y, 2), round(za, 2), round(zb, 2)])
    # short vertical step from the upper bank's rear up to the box floor
    b = pts[-1]
    b2, c = b + w * 1.2, b + Vector((0.0, 1.5, 0.0))
    c2 = c + w * 1.2
    corners = [b, c, c2, b2]
    batch.add(group, "stone", [(q.x, q.y, z0) for q in corners] + [(q.x, q.y, z_top) for q in corners], faces)
    return {"x": lower["end_x"], "segments_y_z": segments, "z0": z0, "parapet": parapet, "rear_step_to": z_top}


def _bring_lf_boxes_forward(scene, batch, front, back):
    """Bring the LF press/box levels forward over the rear of the banks.

    2026-09-09 (Josh): the V14 box floors sat 20-25 m behind the re-aligned
    bank.  New stone floors at the three V14 box levels now run from just
    behind the bank's rear edge back to the gallery front (y 141.5), and the
    V14 box seat and spectator objects are rotated to the row direction and
    slid forward so their front row sits about 1.2 m behind the new edge.
    """
    upper = LF_BANKS[1]
    w = Vector((upper["parallel"][0], upper["parallel"][1], 0.0)).normalized()
    d = (_line_xy(front, back, upper, upper["t1"], 0.5) - _line_xy(front, back, upper, upper["t0"], 0.5)).normalized()
    inner = _line_xy(front, back, upper, upper["t1"], 0.0) + d * 1.5
    outer = _line_xy(front, back, upper, upper["t1"], 1.0) + d * 1.5
    gallery_y = 141.5
    group = "V15 LF box floors"
    faces = [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    levels = [31.6, 34.8, 38.0]
    if max(inner.y, outer.y) > gallery_y - 2.0:
        # The deeper rectangular bank already reaches the gallery front, so the
        # V14 box floors and seats stay where they are: moving the seats put
        # them through the gallery front rails (probe 2026-09-09).
        return {"levels": levels, "front_edge": [[round(inner.x, 2), round(inner.y, 2)], [round(outer.x, 2), round(outer.y, 2)]],
                "gallery_y": gallery_y, "moved": [], "note": "bank reaches the gallery front; boxes left in place"}
    for level in levels:
        corners = [inner, outer, Vector((outer.x, gallery_y, 0.0)), Vector((inner.x, gallery_y, 0.0))]
        batch.add(group, "stone", [(c.x, c.y, level - 0.4) for c in corners] + [(c.x, c.y, level) for c in corners], faces)
        rail(batch, group, Vector((inner.x, inner.y, level)), Vector((outer.x, outer.y, level)), 1.05)
    # slide the V14 box seating to the new front edge
    angle = math.atan2(w.y, w.x)
    pivot = Vector((24.0, 145.0, 0.0))
    target = outer + w * 0.0  # front-row line should pass ~1.2 m behind the new edge at x = 24
    shift = Vector((0.0, (outer.y + 1.2 * d.y + 1.2) - 145.0, 0.0))
    moved = []
    rot = Matrix.Rotation(angle, 4, "Z")
    for obj in list(scene.objects):
        if obj.name.startswith("D2_LF boxes and terrace") or obj.name.startswith("D2_LF box spectators"):
            obj.matrix_world = Matrix.Translation(pivot + shift) @ rot @ Matrix.Translation(-pivot) @ obj.matrix_world
            moved.append(obj.name)
    return {"levels": levels, "front_edge": [[round(inner.x, 2), round(inner.y, 2)], [round(outer.x, 2), round(outer.y, 2)]],
            "gallery_y": gallery_y, "rotated_deg": round(math.degrees(angle), 2), "shift_y": round(shift.y, 2), "moved": moved}


def _fill_lf_wedge(batch, front, back):
    """Small stone podium between the lower bank's rear, the bowl's rear corner and the upper bank.

    With rows parallel to the LF wall the bank's inner edge runs straight
    back from the foul-pole corner, leaving a wedge in front of the main
    bowl's angled end radial that the old fan used to cover.  Fill it to the
    upper bank's rear level so there is no see-through there either.
    """
    lower, upper = LF_BANKS
    a = _line_xy(front, back, lower, lower["t1"], 0.0)  # lower rear row meets the radial here
    b = Vector((back.x, back.y, 0.0))
    c = _line_xy(front, back, upper, upper["t1"], 0.0)
    # Top follows the seats: lower-bank rear level plus the parapet, not the
    # upper bank's rear (2026-09-09, Josh: "giant wall on the left").
    z0, z1 = 8.0, lower["z1"] + 1.1
    verts = [(a.x, a.y, z0), (b.x, b.y, z0), (c.x, c.y, z0), (a.x, a.y, z1), (b.x, b.y, z1), (c.x, c.y, z1)]
    faces = [(0, 2, 1), (3, 4, 5), (0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5)]
    batch.add("V15 LF wedge podium", "stone", verts, faces)
    return {"corners": [[round(v.x, 2), round(v.y, 2)] for v in (a, b, c)], "z": [z0, z1]}


def _remove_v14_returns():
    removed = []
    for name in [
        "D2_V13 LF seating return",
        "D2_V13 LF bank junction",
        "D2_V14 LF return access",
        "D2_V15 LF straight seating",
        "D2_V15 LF seating structure",
        "D2_V15 LF bank access",
        "D2_V13 RF seating return",
        "D2_V14 RF return access",
        "D2_V15 RF straight seating",
        "D2_V15 RF seating structure",
        "D2_V15 RF bank access",
        "D2_V15 RF return junction",
        "D2_V15 RF junction structure",
    ]:
        if bpy.data.collections.get(name) is not None:
            remove_collection(name)
            removed.append(name)
    return removed


def build(scene, batch, root):
    """Apply the bounded V15 return seating correction to a V14 scene."""
    if not scene.get("v14_audit"):
        raise ValueError("V15 seating requires the final V14 saved scene")

    root = root if hasattr(root, "__truediv__") else __import__("pathlib").Path(root)
    spec = json.loads((root / "scene-spec.json").read_text())
    front = Vector((spec["bowl_front"][-1][0], spec["bowl_front"][-1][1], 0.0))
    back = Vector((spec["bowl_back"][-1][0], spec["bowl_back"][-1][1], 0.0))
    removed = _remove_v14_returns()

    lf_group = "V15 LF straight seating"
    lower = _add_row_surfaces(scene, batch, front, back, LF_BANKS[0], lf_group, "LF")
    upper = _add_row_surfaces(scene, batch, front, back, LF_BANKS[1], lf_group, "LF")
    _build_bank_support(scene, batch, front, back, LF_BANKS[0], "LF")
    _build_bank_support(scene, batch, front, back, LF_BANKS[1], "LF")
    access = _build_interbank_access(scene, batch, front, back)
    rear = _close_lf_rear(scene, batch, front, back)
    end_wall = _build_lf_end_wall(batch, front, back)
    wedge = _fill_lf_wedge(batch, front, back)
    boxes = _bring_lf_boxes_forward(scene, batch, front, back)

    rf_group = "V15 RF straight seating"
    front = Vector((*spec["bowl_front"][0][:2], 0.0))
    back = Vector((*spec["bowl_back"][0][:2], 0.0))
    rf_lower = _add_row_surfaces(scene, batch, front, back, RF_BANKS[0], rf_group, "RF")
    rf_upper = _add_row_surfaces(scene, batch, front, back, RF_BANKS[1], rf_group, "RF")
    _build_bank_support(scene, batch, front, back, RF_BANKS[0], "RF")
    _build_bank_support(scene, batch, front, back, RF_BANKS[1], "RF")
    rf_junction = _build_rf_junction(scene, batch, front, back)
    result = {
        "lf": {
            "banks": [lower, upper],
            "seats": lower["seats"] + upper["seats"],
            "spectators": lower["spectators"] + upper["spectators"],
            "straight_row_rule": "P(t,s)=lerp(front[-1].lerp(back[-1],t), linear faceted return endpoint(t),s)",
            "support_foundation_z": FOUNDATION_Z,
            "box_floors_preserved": [31.6, 34.8],
            "roof_untouched": True,
        },
        "access": access,
        "lf_rear_enclosure": rear,
        "lf_end_wall": end_wall,
        "lf_wedge_podium": wedge,
        "lf_boxes_forward": boxes,
        "rf": {
            "banks": [rf_lower, rf_upper],
            "seats": rf_lower["seats"] + rf_upper["seats"],
            "spectators": rf_lower["spectators"] + rf_upper["spectators"],
            "straight_row_rule": "P(t,s)=lerp(front[0].lerp(back[0],t), linear authored RF return endpoint(t),s)",
            "support_foundation_z": FOUNDATION_Z,
            "box_floors_preserved": [31.6, 34.8],
            "roof_untouched": True,
            "junction": rf_junction,
            "source_endpoints": {
                "lower": [list(RF_BANKS[0]["end0"]), list(RF_BANKS[0]["end1"])],
                "upper": [list(RF_BANKS[1]["end0"]), list(RF_BANKS[1]["end1"])],
            },
        },
        "removed_collections": removed,
        "source_basis": [
            "reconstruction-references/user-corrections-2026-09-08/left-field-section-stack.jpg",
            "reconstruction-references/additional/cbs-aecom-chicago-v-b4-aerial-final-v7-footer-joe-smith.jpg",
            "reconstruction-references/additional/fox32-aecom-chicago-v-b6-south-day.jpg",
            "reconstruction-references/user-corrections-2026-09-07/source-angular-rf-seating.png",
        ],
        "inference_boundary": "Rows, rakes, supports and access dimensions are inferred from source silhouettes; fixed-camera saved-scene review is required before fidelity claims.",
        "status": "LF and RF exposed banks replaced with straight faceted rows; RF junction supported with inferred concourse transition",
    }
    scene["v15_seating"] = json.dumps(result)
    return result
