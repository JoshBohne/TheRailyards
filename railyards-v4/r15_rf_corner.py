"""V15 right-field corner rebuilt to the released AECOM views (2026-09-09).

Native crops of B4 (north aerial), A3 (bridge view) and B6 (south aerial) in
reference-audit/crops/rf-corner-*.jpg show the right-field seating as a
straight stack along the EAST river arcade, running north from the clock
tower to the foul pole and scoreboard, rows parallel to the river and facing
west: a lower tier at field level, a two-storey glazed suite band, and an
upper tier cantilevered over the arcade roof whose top row meets a terrace on
the tower's north face.  The tower itself is slender (about two arcade bays).

Everything V12-V15 had put in the triangle south of the bowl (two angled
banks, the "tower end" tier facing north, three stepped terraces, and the
2026-09-09 wedge) is removed; that triangle becomes a lower-tier corner wrap
with a concourse behind it.
"""
import json
import math
import random

import bpy
from mathutils import Matrix, Vector

from r11_circulation import rail
from r2_geometry import instances

REMOVE_PREFIXES = (
    "D2_V15 RF straight seating", "D2_RF lower straight", "D2_RF upper straight",
    "D2_V15 RF return junction", "D2_V15 RF terrace connector", "D2_V15 RF seating structure",
    "D2_V15 RF corner bank", "D2_RF corner",
    "D2_V14 Tower terrace", "D2_Tower end", "D2_V12 Tower end", "D2_RF structure paving",
)
TOWER_PREFIXES = ("D2_Clock tower", "D2_V14 Tower interior", "D2_V14 Tower lift", "D2_V14 Tower stairs", "D2_V14 Tower foundation", "R2_Clock tower")
TOWER_CENTER = Vector((110.0, -76.4, 0.0))
TOWER_SCALE = 0.6                       # 20 m square -> 12 m square
TOWER_NORTH_FACE = -76.4 + 10.0 * TOWER_SCALE   # y of the slimmed tower's north face

# east-river stack (rows parallel to the river, facing west / -x)
Y_N, Y_S = -6.0, -64.0                  # north end (scoreboard truss beyond) .. south end (terrace)
LOWER = dict(x0=101.5, z0=14.0, rows=12, pitch=0.85, rise=0.43)
SUITE = dict(x0=104.0, x1=112.0, z0=19.6, z1=25.6, floors=(19.6, 22.6, 25.6))
UPPER = dict(x0=103.5, z0=26.0, rows=16, pitch=0.85, rise=0.55)
GALLERY_X, GALLERY_ROOF = 112.0, 21.0
TERRACE_Z = UPPER["z0"] + UPPER["rows"] * UPPER["rise"]   # 34.8
SEAT_PITCH, SEAT_INSET, AISLE_W = 0.56, 2.5, 1.2
AISLES = (-25.0, -45.0)

# corner wrap: rows parallel to the field's RF corner edge (75,-21)->(100.5,-6)
WRAP_A, WRAP_B = Vector((75.2, -20.9, 0.0)), Vector((100.5, -6.0, 0.0))
WRAP = dict(rows=12, pitch=0.85, rise=0.43, z0=14.0)
CONCOURSE_Z = WRAP["z0"] + WRAP["rows"] * WRAP["rise"]     # 19.16
BOWL_BACK = Vector((60.5, -105.7, 0.0))

FACES = [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]


def _box(batch, group, mat, x0, x1, y0, y1, z0, z1):
    c = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    batch.add(group, mat, [(x, y, z0) for x, y in c] + [(x, y, z1) for x, y in c], FACES)


def _prism(batch, group, mat, corners, z0, z1):
    """Vertical prism over a convex CCW polygon of (x, y)."""
    n = len(corners)
    verts = [(x, y, z0) for x, y in corners] + [(x, y, z1) for x, y in corners]
    faces = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    batch.add(group, mat, verts, faces)


class _Seats:
    def __init__(self, seed):
        self.rng = random.Random(seed)
        self.pos, self.rot, self.lvl = [], [], []
        self.fans = [[] for _ in range(6)]
        self.fan_rot = [[] for _ in range(6)]

    def add(self, p, yaw):
        self.pos.append(p); self.rot.append((0.0, 0.0, yaw)); self.lvl.append(p[2])
        if self.rng.random() < 0.8:
            c = self.rng.choices(range(6), [32, 27, 18, 15, 5, 3])[0]
            self.fans[c].append(p); self.fan_rot[c].append((0.0, 0.0, yaw))

    def emit(self, scene, collection, name):
        source = bpy.data.objects.get("D2_Seat source")
        if source is not None and self.pos:
            obj = instances(scene, collection, name + " individual seats", source, self.pos, self.rot)
            obj.data.attributes.new("row_elevation", "FLOAT", "POINT").data.foreach_set("value", self.lvl)
        for i, color in enumerate(["cloth_black", "cloth_white", "cloth_gray", "navy", "cloth_blue", "cloth_red"]):
            person = bpy.data.objects.get("D2_Seated fan " + color)
            if person is not None and self.fans[i]:
                instances(scene, collection, name + " spectators " + color, person, self.fans[i], self.fan_rot[i])
        return {"seats": len(self.pos), "spectators": sum(len(f) for f in self.fans)}


def _tier(batch, group, seats, spec, z_floor):
    """Rows parallel to the river (constant x per row), facing -x."""
    for k in range(spec["rows"]):
        x0 = spec["x0"] + k * spec["pitch"]
        x1 = x0 + spec["pitch"]
        z = spec["z0"] + k * spec["rise"]
        bottom = z_floor if x1 <= GALLERY_X else min(z_floor, GALLERY_ROOF)
        _box(batch, group, "concrete", x0, x1, Y_S, Y_N, bottom, z)
        xc = (x0 + x1) * 0.5
        y = Y_S + SEAT_INSET
        while y <= Y_N - SEAT_INSET:
            if not any(abs(y - a) < AISLE_W * 0.5 + 0.55 for a in AISLES):
                seats.add((xc, y, z), math.pi / 2)
            y += SEAT_PITCH
        for a in AISLES:
            for side in (-1, 1):
                rail(batch, group, Vector((x0, a + side * AISLE_W * 0.5, z)), Vector((x1, a + side * AISLE_W * 0.5, z)), 0.92)
    top_x = spec["x0"] + spec["rows"] * spec["pitch"]
    top_z = spec["z0"] + spec["rows"] * spec["rise"]
    return top_x, top_z


def build(scene, batch, root):
    removed = []
    for obj in list(scene.objects):
        if obj.name.startswith(REMOVE_PREFIXES):
            removed.append(obj.name); bpy.data.objects.remove(obj, do_unlink=True)
    # slim the tower about its plan centre
    scaled = []
    m = Matrix.Translation(TOWER_CENTER) @ Matrix.Diagonal((TOWER_SCALE, TOWER_SCALE, 1.0, 1.0)) @ Matrix.Translation(-TOWER_CENTER)
    for obj in scene.objects:
        if obj.name.startswith(TOWER_PREFIXES):
            obj.matrix_world = m @ obj.matrix_world; scaled.append(obj.name)

    group = "V15 RF river stack"
    seats = _Seats(1517)
    # front wall below the lower tier, then the lower tier
    _box(batch, group, "stone", 100.5, LOWER["x0"], Y_S, Y_N, 8.0, LOWER["z0"])
    lower_top_x, lower_top_z = _tier(batch, group, seats, LOWER, 8.0)
    # suite band: floor plates, glazed front, brick rear
    for zf in SUITE["floors"]:
        _box(batch, group, "stone", SUITE["x0"] - 1.0, SUITE["x1"], Y_S, Y_N, zf - 0.4, zf)
    _box(batch, group, "glass_mid", SUITE["x0"], SUITE["x0"] + 0.3, Y_S, Y_N, SUITE["z0"], SUITE["z1"])
    _box(batch, group, "brick_light", SUITE["x1"] - 0.6, SUITE["x1"], Y_S, Y_N, SUITE["z0"], SUITE["z1"])
    _box(batch, group, "brick_light", lower_top_x, SUITE["x0"] - 1.0, Y_S, Y_N, lower_top_z, SUITE["z0"])
    rail(batch, group, Vector((SUITE["x0"] - 1.0, Y_S, SUITE["z0"])), Vector((SUITE["x0"] - 1.0, Y_N, SUITE["z0"])), 1.05)
    # upper tier over the suites and the arcade roof
    upper_top_x, upper_top_z = _tier(batch, group, seats, UPPER, SUITE["z1"])
    rail(batch, group, Vector((upper_top_x, Y_S, upper_top_z)), Vector((upper_top_x, Y_N, upper_top_z)), 1.05)
    # north end wall (scoreboard side) and south end wall, following the rake
    for y in (Y_N, Y_S):
        _box(batch, group, "stone", 100.5, upper_top_x, y - 0.3, y + 0.3, 8.0, LOWER["z0"] + 0.9)
        _box(batch, group, "stone", SUITE["x0"] - 1.0, upper_top_x, y - 0.3, y + 0.3, SUITE["z0"], UPPER["z0"] + 0.9)
    # terrace on the tower's north face, level with the upper tier's top row
    _box(batch, group, "stone", 100.5, upper_top_x, TOWER_NORTH_FACE, Y_S, 8.0, TERRACE_Z - 0.4)
    _box(batch, group, "paving", 100.5, upper_top_x + 1.0, TOWER_NORTH_FACE, Y_S, TERRACE_Z - 0.4, TERRACE_Z)
    rail(batch, group, Vector((100.5, TOWER_NORTH_FACE, TERRACE_Z)), Vector((100.5, Y_S, TERRACE_Z)), 1.05)
    rail(batch, group, Vector((upper_top_x + 1.0, TOWER_NORTH_FACE, TERRACE_Z)), Vector((upper_top_x + 1.0, Y_S, TERRACE_Z)), 1.05)
    stack = seats.emit(scene, batch.collection(group), "RF river stack")

    # corner wrap: lower-tier rows parallel to the RF corner edge, concourse behind
    wgroup = "V15 RF corner wrap"
    wseats = _Seats(1518)
    t = (WRAP_B - WRAP_A).normalized()
    n = Vector((t.y, -t.x, 0.0))        # away from the field (south-east)
    yaw = math.atan2(t.y, t.x) + math.pi  # seats face the field (left of the row direction reversed)
    length = (WRAP_B - WRAP_A).length
    for k in range(WRAP["rows"]):
        z = WRAP["z0"] + k * WRAP["rise"]
        a = WRAP_A + n * (k * WRAP["pitch"]); b = WRAP_B + n * (k * WRAP["pitch"])
        a2 = a + n * WRAP["pitch"]; b2 = b + n * WRAP["pitch"]
        _prism(batch, wgroup, "concrete", [(a.x, a.y), (b.x, b.y), (b2.x, b2.y), (a2.x, a2.y)], 8.0, z)
        c = (a + a2) * 0.5
        d = SEAT_INSET
        while d <= length - SEAT_INSET:
            p = c + t * d
            wseats.add((p.x, p.y, z), yaw)
            d += SEAT_PITCH
    depth = WRAP["rows"] * WRAP["pitch"]
    rear_a, rear_b = WRAP_A + n * depth, WRAP_B + n * depth
    # concourse slab from the wrap's rear to the bowl back and the stack front
    poly = [(rear_a.x, rear_a.y), (rear_b.x, rear_b.y), (100.5, Y_S), (BOWL_BACK.x, BOWL_BACK.y)]
    _prism(batch, wgroup, "stone", poly, 8.0, CONCOURSE_Z - 0.3)
    _prism(batch, wgroup, "paving", poly, CONCOURSE_Z - 0.3, CONCOURSE_Z)
    rail(batch, wgroup, Vector((rear_a.x, rear_a.y, CONCOURSE_Z)), Vector((rear_b.x, rear_b.y, CONCOURSE_Z)), 1.05)
    wrap = wseats.emit(scene, batch.collection(wgroup), "RF corner wrap")

    result = {
        "removed": removed, "tower_scaled": scaled, "tower_scale": TOWER_SCALE, "tower_north_face_y": TOWER_NORTH_FACE,
        "stack": {"y": [Y_S, Y_N], "lower": LOWER, "suite": SUITE, "upper": UPPER, "terrace_z": TERRACE_Z, "upper_top_x": upper_top_x, **stack},
        "wrap": {"rows": WRAP["rows"], "concourse_z": CONCOURSE_Z, **wrap},
        "source": ["reference-audit/crops/rf-corner-b4.jpg", "reference-audit/crops/rf-corner-a3.jpg", "reference-audit/crops/rf-corner-b6.jpg"],
    }
    scene["v15_rf_corner"] = json.dumps(result)
    return result
