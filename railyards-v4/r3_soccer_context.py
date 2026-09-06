"""Source-led context model for the proposed Chicago Fire soccer venue.

The venue is an explicitly inferred future phase visible in the south AECOM
artwork.  Its registration is inherited from the v2 context layer: the field
center is ``(424, 51)`` in the shared local frame, with the long field axis on
Y.  This module owns only the venue and its river-facing public edge.  It does
not change ``r2_context.py`` or the shared scene.

The source resolves the venue as a dark rectangular roof with red seating,
green pitch, and a low warm frontage.  Exact structure, facade program, and
dimensions are not published in the supplied artwork; the dimensions below
therefore preserve the existing registration and are marked as inferred in
``soccer-context-spec.json``.
"""

import math
from pathlib import Path

import bpy
from mathutils import Vector

from r2_geometry import MeshBatch, text


OUT = Path(__file__).resolve().parent
GROUP = 'Proposed soccer stadium'

SOCCER_SPEC = {
    'center': (424.0, 51.0),
    'field_width': 74.0,
    'field_length': 112.0,
    'field_z': 16.05,
    'base_z': 12.0,
    'seat_rows': 12,
    'roof_inner_x': 49.0,
    'roof_outer_x': 82.0,
    'roof_inner_y': 67.0,
    'roof_outer_y': 104.0,
    'roof_inner_z': 38.6,
    'roof_outer_z': 34.3,
}


def _p(center, x, y, z):
    return (center[0] + float(x), center[1] + float(y), float(z))


def _roof_panel(batch, center, x0, x1, y0, y1, z0, z1, axis='x'):
    # ``center`` is added by the caller after the local panel is built.  The
    # helper uses the shared scene's world coordinates directly for clarity.
    if axis == 'x':
        heights = (z0, z1, z1, z0)
    else:
        heights = (z0, z0, z1, z1)
    top = [_p(center, x, y, z) for (x, y), z in zip(
        ((x0, y0), (x1, y0), (x1, y1), (x0, y1)), heights)]
    bottom = [(x, y, z - 1.2) for x, y, z in top]
    batch.add(GROUP, 'roof', bottom + top,
              [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4),
               (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)])


def _outline(batch, center, points, z, radius=0.09):
    batch.line(GROUP, 'white', [_p(center, x, y, z) for x, y in points],
               radius, sides=6)


def _field(batch, center):
    width = SOCCER_SPEC['field_width']
    length = SOCCER_SPEC['field_length']
    z = SOCCER_SPEC['field_z']
    batch.box(GROUP, 'field', _p(center, 0, 0, z),
              (width, length, 0.16))

    # Regulation-style markings are scaled to the image-derived pitch rather
    # than asserted as a surveyed venue plan.
    half_w, half_l = width * 0.5, length * 0.5
    _outline(batch, center,
             [(-half_w, -half_l), (half_w, -half_l),
              (half_w, half_l), (-half_w, half_l), (-half_w, -half_l)],
             z + 0.10)
    _outline(batch, center, [(-half_w, 0), (half_w, 0)], z + 0.10)
    circle = [(9.15 * math.cos(i * math.tau / 64.0),
               9.15 * math.sin(i * math.tau / 64.0)) for i in range(65)]
    _outline(batch, center, circle, z + 0.10)
    for y in (-half_l, half_l):
        sign = 1.0 if y < 0 else -1.0
        box_depth = 16.5
        box_half_w = 20.5
        y0 = y if sign > 0 else y - box_depth
        y1 = y + box_depth if sign > 0 else y
        _outline(batch, center,
                 [(-box_half_w, y0), (box_half_w, y0),
                  (box_half_w, y1), (-box_half_w, y1),
                  (-box_half_w, y0)], z + 0.11)
        six_depth = 5.5
        six_half_w = 9.0
        y0 = y if sign > 0 else y - six_depth
        y1 = y + six_depth if sign > 0 else y
        _outline(batch, center,
                 [(-six_half_w, y0), (six_half_w, y0),
                  (six_half_w, y1), (-six_half_w, y1),
                  (-six_half_w, y0)], z + 0.11)

        # Minimal white goal frame and a fine net plane keep the end condition
        # legible from the aerial camera without pretending to model mesh net.
        goal_y = y + (1.0 if y < 0 else -1.0)
        post_z = z + 1.75
        for x in (-3.66, 3.66):
            batch.cylinder(GROUP, 'white', _p(center, x, goal_y, z + .1),
                           _p(center, x, goal_y, post_z), .11, sides=8)
        batch.line(GROUP, 'white',
                   [_p(center, -3.66, goal_y, post_z),
                    _p(center, 3.66, goal_y, post_z)], .11, sides=8)
        batch.line(GROUP, 'cloth_white',
                   [_p(center, -3.66, goal_y, z + .15),
                    _p(center, -3.66, goal_y + sign * 2.2, z + .15),
                    _p(center, 3.66, goal_y + sign * 2.2, z + .15),
                    _p(center, 3.66, goal_y, z + .15)], .035, sides=5)


def _seating(batch, center):
    width = SOCCER_SPEC['field_width']
    length = SOCCER_SPEC['field_length']
    rows = SOCCER_SPEC['seat_rows']
    # Each row has four connected sides and four corner blocks.  The corner
    # blocks close the bowl visually from oblique aerial views.
    for row in range(rows):
        z = SOCCER_SPEC['field_z'] + 1.05 + row * 0.82
        depth = 0.92
        offset = 5.0 + row * depth
        side_x = width * 0.5 + offset
        side_y = length * 0.5 + offset
        seat_z = z + 0.24
        batch.box(GROUP, 'cloth_red', _p(center, -side_x, 0, seat_z),
                  (depth, length + 2 * offset, 0.48))
        batch.box(GROUP, 'cloth_red', _p(center, side_x, 0, seat_z),
                  (depth, length + 2 * offset, 0.48))
        batch.box(GROUP, 'cloth_red', _p(center, 0, -side_y, seat_z),
                  (width + 2 * offset, depth, 0.48))
        batch.box(GROUP, 'cloth_red', _p(center, 0, side_y, seat_z),
                  (width + 2 * offset, depth, 0.48))
        corner = 7.0 + row * 0.12
        for sx in (-1, 1):
            for sy in (-1, 1):
                batch.box(GROUP, 'cloth_red',
                          _p(center, sx * side_x, sy * side_y, seat_z),
                          (corner, corner, 0.48))

    # Dark fascia below the roof gives the red bowl a readable outer edge.
    outer_x = width * 0.5 + 5.0 + rows * 0.92
    outer_y = length * 0.5 + 5.0 + rows * 0.92
    z = SOCCER_SPEC['field_z'] + 1.05 + rows * 0.82
    batch.box(GROUP, 'metal', _p(center, -outer_x - 0.7, 0, z),
              (1.0, 2 * outer_y, 1.2))
    batch.box(GROUP, 'metal', _p(center, outer_x + 0.7, 0, z),
              (1.0, 2 * outer_y, 1.2))
    batch.box(GROUP, 'metal', _p(center, 0, -outer_y - 0.7, z),
              (2 * outer_x, 1.0, 1.2))
    batch.box(GROUP, 'metal', _p(center, 0, outer_y + 0.7, z),
              (2 * outer_x, 1.0, 1.2))


def _roof_and_structure(batch, center):
    ix = SOCCER_SPEC['roof_inner_x']
    ox = SOCCER_SPEC['roof_outer_x']
    iy = SOCCER_SPEC['roof_inner_y']
    oy = SOCCER_SPEC['roof_outer_y']
    iz = SOCCER_SPEC['roof_inner_z']
    oz = SOCCER_SPEC['roof_outer_z']
    # Four overlapping sloped panels read as one continuous dark roof ring.
    _roof_panel(batch, center, -ox, -ix, -oy, oy, oz, iz)
    _roof_panel(batch, center, ix, ox, -oy, oy, iz, oz)
    _roof_panel(batch, center, -ix, ix, -oy, -iy, oz, iz, axis='y')
    _roof_panel(batch, center, -ix, ix, iy, oy, iz, oz, axis='y')
    for sx in (-1, 1):
        for sy in (-1, 1):
            batch.box(GROUP, 'roof', _p(center, sx * (ix + ox) * .5,
                                        sy * (iy + oy) * .5, oz - .35),
                      (ox - ix, oy - iy, 1.25))

    # Eave beams and repeated angled columns expose the scale of the roof.
    for x in (-ox, ox):
        batch.line(GROUP, 'metal', [_p(center, x, -oy, oz - .65),
                                    _p(center, x, oy, oz - .65)], .28, sides=8)
    for y in (-oy, oy):
        batch.line(GROUP, 'metal', [_p(center, -ox, y, oz - .65),
                                    _p(center, ox, y, oz - .65)], .28, sides=8)
    for x in (-ox + 8, -ox + 42, ox - 42, ox - 8):
        for y in range(-90, 91, 30):
            batch.cylinder(GROUP, 'aluminum', _p(center, x, y, 12.4),
                           _p(center, x + (-7 if x < 0 else 7), y, oz - .55),
                           .24, sides=8)

    # Source-visible roof branding on the near (south) edge.
    col = batch.collection(GROUP)
    lettering_y = -oy + 5.0
    # Keep the curve clearly above the roof surface.  The venue sits hundreds
    # of metres from the world origin, so a small offset can still z-fight in
    # the aerial render.
    lettering_z = oz + (5.0 / (oy - iy)) * (iz - oz) + .60
    text(scene=None, group=col, name='Chicago Fire roof lettering',
         body='CHICAGO FIRE',
         position=_p(center, 0, lettering_y, lettering_z), size=4.15,
         material=batch.materials['screen_ink'], rotation=(0.0, 0.0, 0.0))


def _river_frontage(batch, center):
    """Low west edge with repeated bays and one legible entry canopy."""
    west = -SOCCER_SPEC['roof_outer_x'] - 1.4
    length = 2 * SOCCER_SPEC['roof_outer_y'] - 12.0
    base = SOCCER_SPEC['base_z']
    batch.box(GROUP, 'concrete', _p(center, west, 0, base + 2.0),
              (2.8, length, 4.0))
    batch.box(GROUP, 'stone', _p(center, west - 0.2, 0, base + .45),
              (3.4, length + 3.0, .9))
    bay_spacing = 12.0
    count = max(1, int(length / bay_spacing))
    for index in range(count):
        y = -length * .5 + (index + .5) * length / count
        batch.box(GROUP, 'glass_lit', _p(center, west - 1.48, y, base + 6.6),
                  (.10, bay_spacing * .62, 7.1))
        batch.box(GROUP, 'metal', _p(center, west - 1.58, y, base + 6.6),
                  (.12, .22, 7.6))
    # A shallow canopy and paired piers identify the river-facing public edge.
    entry_y = -10.0
    batch.box(GROUP, 'canopy', _p(center, west - 4.0, entry_y, base + 10.8),
              (7.0, 28.0, .55))
    for y in (entry_y - 11.0, entry_y + 11.0):
        batch.cylinder(GROUP, 'aluminum', _p(center, west - 6.7, y, base + .7),
                       _p(center, west - 6.7, y, base + 10.5), .24, sides=8)
    text(scene=None, group=batch.collection(GROUP), name='Chicago Fire entry',
         body='FIRE', position=_p(center, west - 6.85, entry_y, base + 9.6),
         size=2.15, material=batch.materials['screen_ink'],
         rotation=(math.pi / 2.0, 0.0, math.pi / 2.0))
    batch.box(GROUP, 'paving', _p(center, west - 14.0, 0, base + .12),
              (20.0, length + 20.0, .24))
    for y in (-70.0, -35.0, 0.0, 35.0, 70.0):
        batch.box(GROUP, 'paving', _p(center, west - 12.0, y, base + .27),
                  (4.2, 1.2, .10))


def build_soccer_context(scene, spec, batch, materials):
    """Add the proposed soccer venue to an existing ``MeshBatch``.

    ``spec`` is accepted for the shared builder signature.  Registration and
    the source-backed venue dimensions remain local constants so this module
    can be added after ``r2_context`` without mutating its implementation.
    """
    del spec
    for key in ('field', 'cloth_red', 'roof', 'metal', 'aluminum',
                'concrete', 'stone', 'glass_lit', 'canopy', 'paving',
                'white', 'cloth_white', 'screen_ink'):
        if key not in materials:
            raise KeyError(f"Soccer context requires material {key!r}")
    center = SOCCER_SPEC['center']
    _field(batch, center)
    _seating(batch, center)
    _roof_and_structure(batch, center)
    _river_frontage(batch, center)
    scene['soccer_context_note'] = (
        'Proposed Chicago Fire venue: source-backed south artwork context; '
        'registration and dimensions remain explicitly inferred.'
    )


__all__ = ['build_soccer_context', 'SOCCER_SPEC']
