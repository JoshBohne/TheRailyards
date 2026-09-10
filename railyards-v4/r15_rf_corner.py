"""V15 right-field corner rebuilt to the AECOM A3 source (2026-09-09).

Josh's reading of the A3 crop (reconstruction-references/user-corrections-
2026-09-07/source-angular-rf-seating.png): one continuous wedge of seating
between the clock tower and the main bowl, rows parallel to the river
gallery, widening toward the tower, top row on the tower terrace level so
the terrace and the bank meet edge to edge.  This replaces the two V15 RF
banks, their concourse junction and terrace connector, and the three V14
stepped tower terraces.
"""
import math
import random

import bpy
from mathutils import Vector

from r11_circulation import rail
from r2_geometry import instances

X_TOP, Z_TOP = 111.5, 32.6      # top row against the river gallery, at terrace level
PITCH, RISE = 0.85, 0.43        # row pitch and rise (LF lower bank rake)
Z_FRONT = 14.0                  # lowest row level
Y_SOUTH = -60.0                 # bank ends here; terrace strip to the tower beyond
Y_TERRACE = -68.0               # tower face
SEAT_PITCH, SEAT_INSET = 0.56, 2.5
AISLES = (-20.0, -40.0)         # aisle centre lines (y), 1.2 m wide
AISLE_W = 1.2
REMOVE_PREFIXES = (
    "D2_V15 RF straight seating", "D2_RF lower straight", "D2_RF upper straight",
    "D2_V15 RF return junction", "D2_V15 RF terrace connector", "D2_V15 RF seating structure",
    "D2_V14 Tower terrace 1", "D2_V14 Tower terrace 2", "D2_V14 Tower terrace 3",
)


def _y_north(x):
    """Field-side boundary: the RF corner diagonal, then the foul-pole line."""
    if x <= 75.0:
        return -21.0
    if x <= 100.0:
        return -21.0 + 0.84 * (x - 75.0)
    return 0.0


def _box(batch, group, mat, x0, x1, y0, y1, z0, z1):
    c = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    verts = [(x, y, z0) for x, y in c] + [(x, y, z1) for x, y in c]
    batch.add(group, mat, verts, [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)])


def build(scene, batch, root):
    removed = []
    for obj in list(scene.objects):
        if obj.name.startswith(REMOVE_PREFIXES):
            removed.append(obj.name)
            bpy.data.objects.remove(obj, do_unlink=True)
    group = "V15 RF corner bank"
    rng = random.Random(1516)
    seats, rotations, levels = [], [], []
    fans = [[] for _ in range(6)]
    rows = int((Z_TOP - Z_FRONT) / RISE) + 1
    row_records = []
    for k in range(rows):
        z = Z_TOP - k * RISE
        x1 = X_TOP - k * PITCH
        x0 = x1 - PITCH
        xc = (x0 + x1) * 0.5
        yn = _y_north(xc)
        if yn < Y_SOUTH + 3.0:
            continue
        _box(batch, group, "concrete", x0, x1, Y_SOUTH, yn, 8.0, z)
        row_records.append([round(xc, 2), round(z, 2), round(yn, 2)])
        y = Y_SOUTH + SEAT_INSET
        while y <= yn - SEAT_INSET:
            if not any(abs(y - a) < AISLE_W * 0.5 + 0.55 for a in AISLES):
                p = (xc, y, z)
                seats.append(p); rotations.append((0.0, 0.0, math.pi / 2)); levels.append(z)
                if rng.random() < 0.8:
                    fans[rng.choices(range(6), [32, 27, 18, 15, 5, 3])[0]].append(p)
            y += SEAT_PITCH
        for a in AISLES:
            if Y_SOUTH + 1.0 < a < yn - 1.0:
                for side in (-1, 1):
                    ya = a + side * AISLE_W * 0.5
                    rail(batch, group, Vector((x0, ya, z)), Vector((x1, ya, z)), 0.92)
    # top-row guard along the gallery side and the north (foul-pole) edge
    rail(batch, group, Vector((X_TOP, Y_SOUTH, Z_TOP)), Vector((X_TOP, _y_north(X_TOP) - 0.3, Z_TOP)), 1.05)
    # tower terrace: one deck at the top-row level from the bank to the tower face
    _box(batch, group, "stone", 75.0, X_TOP, Y_TERRACE, Y_SOUTH, 8.0, Z_TOP - 0.4)
    _box(batch, group, "paving", 67.0, 119.0, Y_TERRACE, Y_SOUTH, Z_TOP - 0.4, Z_TOP)
    rail(batch, group, Vector((119.0, Y_TERRACE, Z_TOP)), Vector((119.0, Y_SOUTH, Z_TOP)), 1.05)
    rail(batch, group, Vector((X_TOP, Y_SOUTH, Z_TOP)), Vector((119.0, Y_SOUTH, Z_TOP)), 1.05)
    collection = batch.collection(group)
    source = bpy.data.objects.get("D2_Seat source")
    if source is not None and seats:
        obj = instances(scene, collection, "RF corner individual seats", source, seats, rotations)
        attr = obj.data.attributes.new("row_elevation", "FLOAT", "POINT")
        attr.data.foreach_set("value", levels)
    for i, color in enumerate(["cloth_black", "cloth_white", "cloth_gray", "navy", "cloth_blue", "cloth_red"]):
        person = bpy.data.objects.get("D2_Seated fan " + color)
        if person is not None and fans[i]:
            instances(scene, collection, "RF corner spectators " + color, person, fans[i], [(0.0, 0.0, math.pi / 2)] * len(fans[i]))
    result = {
        "rows": len(row_records), "seats": len(seats), "spectators": sum(len(f) for f in fans),
        "top_row": [X_TOP, Z_TOP], "pitch_m": PITCH, "rise_m": RISE, "y_south": Y_SOUTH, "terrace": [Y_TERRACE, Y_SOUTH, Z_TOP],
        "row_x_z_ynorth": row_records[::6], "removed": removed,
        "source": "reconstruction-references/user-corrections-2026-09-07/source-angular-rf-seating.png (AECOM A3 crop)",
    }
    scene["v15_rf_corner"] = __import__("json").dumps(result)
    return result
