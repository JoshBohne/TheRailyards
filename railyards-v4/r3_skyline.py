"""Real Chicago skyline silhouettes for the Railyards interior views.

The proposed stadium and its future district are schematic.  This module owns
only a short, source-backed landmark layer beyond the outfield.  Coordinates
come from ``reference-audit/skyline-buildings.json`` in the shared metric
frame; no camera-based hiding is performed, so a wider or panned interior
camera can reveal Willis Tower and the left-field landmarks naturally.
"""

import json
import math
from pathlib import Path

from mathutils import Vector

from r2_geometry import MeshBatch
import r4_geo


OUT = Path(__file__).resolve().parent
with (OUT / 'skyline-buildings.json').open(encoding='utf-8') as _handle:
    SKYLINE_SPEC = json.load(_handle)

GROUP = 'Skyline landmarks'
GROUND_Z = 8.0


def _landmark(identifier):
    for building in SKYLINE_SPEC['buildings']:
        if building['id'] == identifier:
            return building
    raise KeyError(f'Missing skyline landmark: {identifier}')


def _center(identifier):
    point = _landmark(identifier)['local_xy_m']
    # V4: the JSON values are raw-formula coordinates; apply the audited
    # site registration exactly once (see r4_geo).
    return r4_geo.register((point['x'], point['y']))


def _rect(cx, cy, width, depth):
    half_w, half_d = width * 0.5, depth * 0.5
    return [(cx - half_w, cy - half_d),
            (cx + half_w, cy - half_d),
            (cx + half_w, cy + half_d),
            (cx - half_w, cy + half_d)]


def _ellipse(cx, cy, width, depth, segments=18):
    return [(cx + width * 0.5 * math.cos(math.tau * i / segments),
             cy + depth * 0.5 * math.sin(math.tau * i / segments))
            for i in range(segments)]


def _tapered_prism(batch, name, cx, cy, z0, z1, w0, d0, w1, d1,
                   material='glass'):
    """Add a closed four-sided tower section with independently tapered ends."""
    bottom = _rect(cx, cy, w0, d0)
    top = _rect(cx, cy, w1, d1)
    vertices = [(x, y, z0) for x, y in bottom]
    vertices.extend((x, y, z1) for x, y in top)
    faces = [(3, 2, 1, 0), (4, 5, 6, 7),
             (0, 1, 5, 4), (1, 2, 6, 5),
             (2, 3, 7, 6), (3, 0, 4, 7)]
    batch.add(GROUP, material, vertices, faces)


def _horizontal_bands(batch, cx, cy, z0, z1, width, depth,
                      material='aluminum', spacing=12.0):
    """Keep distant tower floors legible without tiling every window."""
    z = z0 + spacing
    while z < z1 - 1.0:
        batch.box(GROUP, material, (cx, cy - depth * 0.5 - 0.10, z),
                  (width, 0.16, 0.20))
        batch.box(GROUP, material, (cx, cy + depth * 0.5 + 0.10, z),
                  (width, 0.16, 0.20))
        batch.box(GROUP, material, (cx - width * 0.5 - 0.10, cy, z),
                  (0.16, depth, 0.20))
        batch.box(GROUP, material, (cx + width * 0.5 + 0.10, cy, z),
                  (0.16, depth, 0.20))
        z += spacing


def _vertical_bays(batch, cx, cy, z0, z1, width, depth, spacing=10.0,
                   material='aluminum', bar_width=0.18):
    for x in [cx - width * 0.5 + spacing * i
              for i in range(1, max(1, round(width / spacing)))] :
        batch.box(GROUP, material, (x, cy - depth * 0.5 - 0.11,
                                    (z0 + z1) * 0.5),
                  (bar_width, 0.18, z1 - z0))
        batch.box(GROUP, material, (x, cy + depth * 0.5 + 0.11,
                                    (z0 + z1) * 0.5),
                  (bar_width, 0.18, z1 - z0))


def _facade_rhythm(batch, cx, cy, z0, z1, width, depth, spacing=8.0,
                   band_spacing=12.0, glass_width=2.8):
    """Add broad glazing strips and floor lines that survive long views.

    A single dark prism reads as an untextured block at the 1.5 km Willis
    distance.  These restrained strips are intentionally much wider than a
    modeled mullion: they establish the real tower's continuous dark-window
    rhythm without pretending to resolve individual windows.
    """
    bay_count = max(1, round(width / spacing))
    bay_pitch = width / bay_count
    strip_width = min(glass_width, bay_pitch * 0.68)
    mid_z = (z0 + z1) * 0.5
    strip_height = max(1.0, z1 - z0 - 2.0)
    for index in range(bay_count):
        x = cx - width * 0.5 + bay_pitch * (index + 0.5)
        for y in (cy - depth * 0.5 - 0.13, cy + depth * 0.5 + 0.13):
            batch.box(GROUP, 'glass', (x, y, mid_z),
                      (strip_width, 0.16, strip_height))
    side_count = max(1, round(depth / spacing))
    side_pitch = depth / side_count
    side_strip = min(glass_width, side_pitch * 0.68)
    for index in range(side_count):
        y = cy - depth * 0.5 + side_pitch * (index + 0.5)
        for x in (cx - width * 0.5 - 0.13, cx + width * 0.5 + 0.13):
            batch.box(GROUP, 'glass', (x, y, mid_z),
                      (0.16, side_strip, strip_height))
    z = z0 + band_spacing
    while z < z1 - 1.0:
        for y in (cy - depth * 0.5 - 0.23, cy + depth * 0.5 + 0.23):
            batch.box(GROUP, 'aluminum', (cx, y, z),
                      (width + 0.8, 0.18, 0.20))
        for x in (cx - width * 0.5 - 0.23, cx + width * 0.5 + 0.23):
            batch.box(GROUP, 'aluminum', (x, cy, z),
                      (0.18, depth + 0.8, 0.20))
        z += band_spacing


def _st_regis(batch):
    """Alternating 12-story frustums, following Studio Gang's stated geometry.

    Floor-plate widths follow the CTBUH case study (24.7-27.4 m); the
    shorter heights approximate MKA's 100/75/50-story volumes. The wind
    opening height is inferred. Geographic registration is unchanged.
    """
    cx, cy = _center('st-regis-chicago')
    for index, (offset, height) in enumerate([(-26.5,362.9),(0,272.2),(26.5,181.5)]):
        step = 43.5
        z0 = 0.0
        while z0 < height:
            z1 = min(height,z0+step)
            module = int(round(z0/step))
            w0,w1 = ((24.7,27.4) if (module+index)%2==0 else (27.4,24.7))
            # Leave an actual wind opening near the top of the tallest stem.
            pieces=[(z0,z1)]
            if index==0 and z0<310 and z1>304:
                pieces=[(z0,304),(310,z1)]
            for low,high in pieces:
                if high<=low:continue
                f0=(low-z0)/step;f1=(high-z0)/step
                wa=w0+(w1-w0)*f0;wb=w0+(w1-w0)*f1
                _tapered_prism(batch,'St Regis frustum',cx+offset,cy,
                    GROUND_Z+low,GROUND_Z+high,wa,wa*.86,wb,wb*.86,
                    'glass_blue' if module%2 else 'glass_green')
            z0=z1
        if index==0:
            for dx in (-8,8):
                batch.cylinder(GROUP,'metal',(cx+offset+dx,cy,GROUND_Z+304),
                    (cx+offset+dx,cy,GROUND_Z+310),.65,sides=8)


def _aqua(batch):
    """Irregular balcony plates around a compact tower core."""
    cx, cy = _center('aqua')
    top = GROUND_Z + 261.8
    _tapered_prism(batch, 'Aqua core', cx, cy, GROUND_Z, top,
                   25.0, 21.0, 31.0, 25.0, 'glass_blue')
    for z in range(20, 255, 13):
        phase = math.sin(z * 0.17)
        width = 51.0 + phase * 13.0
        depth = 42.0 + math.cos(z * 0.13) * 11.0
        batch.prism(GROUP, 'crown_white', _ellipse(cx, cy, width, depth),
                    GROUND_Z + z, GROUND_Z + z + 0.30)


def _aon(batch):
    cx, cy = _center('aon-center')
    top = GROUND_Z + 346.3
    _tapered_prism(batch, 'Aon Center monolith', cx, cy, GROUND_Z, top,
                   65.0, 48.0, 61.0, 45.0, 'white_marble')
    _vertical_bays(batch, cx, cy, GROUND_Z + 2, top - 2, 61.0, 45.0,
                   spacing=9.0, material='metal', bar_width=0.45)
    for dx in (-13.0, 13.0):
        batch.cylinder(GROUP, 'metal', (cx + dx, cy, top),
                       (cx + dx, cy, GROUND_Z + 362.5), 0.42, sides=8)


def _prudential(batch, identifier, two=False):
    cx,cy=_center(identifier)
    if not two:
        _tapered_prism(batch,'One Prudential',cx,cy,GROUND_Z,GROUND_Z+179,
                       46,36,46,36,'glass_grey')
        _horizontal_bands(batch,cx,cy,GROUND_Z+6,GROUND_Z+179,46,36,spacing=12)
        return
    # Two Pru: stepped shoulders, rotated pyramidal crown, and slender spire.
    # The total stays at 303.3 m; crown proportions are estimated from images.
    for z0,z1,w,d in [(0,230,57,43),(230,242,49,37),(242,253,40,30)]:
        _tapered_prism(batch,'Two Pru shoulder',cx,cy,GROUND_Z+z0,GROUND_Z+z1,
                       w,d,w,d,'glass_grey')
        _horizontal_bands(batch,cx,cy,GROUND_Z+z0,GROUND_Z+z1,w,d,spacing=4)
    base=[(cx,cy-20,GROUND_Z+253),(cx+20,cy,GROUND_Z+253),
          (cx,cy+20,GROUND_Z+253),(cx-20,cy,GROUND_Z+253)]
    batch.add(GROUP,'crown_white',base+[(cx,cy,GROUND_Z+279)],
              [(0,1,4),(1,2,4),(2,3,4),(3,0,4),(3,2,1,0)])
    batch.cylinder(GROUP,'aluminum',(cx,cy,GROUND_Z+279),
                   (cx,cy,GROUND_Z+303.3),.60,.10,sides=8)


def _trump(batch):
    cx, cy = _center('trump-international-chicago')
    # Tapered glass shaft, with two visible setbacks before the narrow spire.
    _tapered_prism(batch, 'Trump Tower lower shaft', cx, cy, GROUND_Z,
                   GROUND_Z + 278.0, 55.0, 44.0, 49.0, 39.0, 'glass')
    _tapered_prism(batch, 'Trump Tower upper shaft', cx, cy, GROUND_Z + 278.0,
                   GROUND_Z + 357.0, 49.0, 39.0, 31.0, 27.0, 'glass_blue')
    _horizontal_bands(batch, cx, cy, GROUND_Z + 10, GROUND_Z + 350,
                       49.0, 39.0, material='metal', spacing=16.0)
    batch.cylinder(GROUP, 'aluminum', (cx, cy, GROUND_Z + 357.0),
                   (cx, cy, GROUND_Z + 423.2), 1.25, sides=8)


def _hancock(batch):
    cx, cy = _center('875-north-michigan')
    body_top = GROUND_Z + 343.7
    _tapered_prism(batch, '875 North Michigan shaft', cx, cy, GROUND_Z,
                   body_top, 58.0, 46.0, 48.0, 40.0, 'glass')
    _horizontal_bands(batch, cx, cy, GROUND_Z + 5, body_top,
                       52.0, 42.0, material='metal', spacing=15.0)
    # External X braces on all four elevations; they are the identifier at 4 km.
    for z0 in range(30, 330, 60):
        z1 = min(z0 + 60, 343)
        for y in (cy - 23.3, cy + 23.3):
            batch.line(GROUP, 'metal',
                       [(cx - 28.0, y, GROUND_Z + z0),
                        (cx + 28.0, y, GROUND_Z + z1)], 0.72, sides=6)
            batch.line(GROUP, 'metal',
                       [(cx + 28.0, y, GROUND_Z + z0),
                        (cx - 28.0, y, GROUND_Z + z1)], 0.72, sides=6)
        for x in (cx - 29.3, cx + 29.3):
            batch.line(GROUP, 'metal',
                       [(x, cy - 22.0, GROUND_Z + z0),
                        (x, cy + 22.0, GROUND_Z + z1)], 0.72, sides=6)
            batch.line(GROUP, 'metal',
                       [(x, cy + 22.0, GROUND_Z + z0),
                        (x, cy - 22.0, GROUND_Z + z1)], 0.72, sides=6)
    for dx in (-17.0, 17.0):
        batch.cylinder(GROUP, 'metal', (cx + dx, cy, body_top),
                       (cx + dx, cy, GROUND_Z + 456.9), 0.55, sides=8)


def _willis(batch):
    """Nine 75-foot square tubes, with asymmetric terminations (SOM).

    Heights of intermediate terminations are visual estimates; the overall
    roof and antenna heights retain the existing source specification.
    """
    cx,cy=_center('willis-tower');pitch=22.86
    heights=[(205,283,342),(283,442.1,442.1),(205,283,342)]
    for row in range(3):
        for column in range(3):
            h=heights[row][column];x=cx+(column-1)*pitch;y=cy+(row-1)*pitch
            batch.box(GROUP,'black_steel',(x,y,GROUND_Z+h/2),(pitch,pitch,h))
            _facade_rhythm(batch,x,y,GROUND_Z+.5,GROUND_Z+h-.5,pitch,pitch,
                spacing=3.3,band_spacing=12,glass_width=2.0)
            batch.box(GROUP,'metal',(x,y,GROUND_Z+h+.2),(pitch,pitch,.4))
    for x in (cx,cx+pitch):
        batch.cylinder(GROUP,'white',(x,cy,GROUND_Z+442.1),
                       (x,cy,GROUND_Z+527),.70,sides=10)


def _secondary_landmarks(batch):
    # These audited landmarks occupy gaps in wider/panned outfield views.
    # They remain at their real coordinates and can be naturally occluded.
    cx,cy=_center('marina-city')
    for offset in [-28,28]:
        x=cx+offset
        batch.cylinder(GROUP,'glass',(x,cy,GROUND_Z),(x,cy,GROUND_Z+179.2),13.5,sides=32)
        for floor in range(60):
            z=GROUND_Z+floor*2.98
            ring=[]
            for i in range(96):
                a=math.tau*i/96;r=17.4+1.4*math.cos(16*a)
                ring.append((x+r*math.cos(a),cy+r*math.sin(a)))
            batch.prism(GROUP,'concrete',ring,z,z+.38)
    cx,cy=_center('tribune-tower')
    batch.box(GROUP,'stone',(cx,cy,GROUND_Z+55),(36,38,110))
    _vertical_bays(batch,cx,cy,GROUND_Z,GROUND_Z+112,36,38,spacing=4.5,material='glass')
    for dx in [-14,14]:
        for dy in [-15,15]:
            batch.cylinder(GROUP,'stone',(cx+dx,cy+dy,GROUND_Z+104),(cx+dx,cy+dy,GROUND_Z+141),2.7,.55,sides=8)
            batch.cylinder(GROUP,'stone',(cx+dx,cy+dy,GROUND_Z+112),(cx+dx*.45,cy+dy*.45,GROUND_Z+133),1.4,sides=8)
    _tapered_prism(batch,'Tribune crown',cx,cy,GROUND_Z+109,GROUND_Z+141,20,22,10,11,'stone')
    cx,cy=_center('wrigley-building')
    for dx,height in [(-20,100),(21,133)]:
        x=cx+dx
        batch.box(GROUP,'stone',(x,cy,GROUND_Z+height*.34),(32,34,height*.68))
        _vertical_bays(batch,x,cy,GROUND_Z+5,GROUND_Z+height*.68,32,34,spacing=5,material='glass')
        _tapered_prism(batch,'Wrigley crown',x,cy,GROUND_Z+height*.68,GROUND_Z+height*.94,24,26,13,14,'stone')
        batch.cylinder(GROUP,'roof',(x,cy,GROUND_Z+height*.94),(x,cy,GROUND_Z+height),7,.5,sides=12)
        for side in [-1,1]:
            batch.cylinder(GROUP,'screen',(x,cy+side*13.1,GROUND_Z+height*.81),(x,cy+side*13.3,GROUND_Z+height*.81),4.0,sides=24)
    for ident,w,d in [('salesforce-tower-chicago',49,42),('river-point',56,48),('150-north-riverside',49,27)]:
        cx,cy=_center(ident);h=_landmark(ident)['architectural_height_m']
        base_w=w*.35 if ident=='150-north-riverside' else w*.84
        _tapered_prism(batch,ident,cx,cy,GROUND_Z,GROUND_Z+35,base_w,d*.7,w,d,'glass')
        batch.box(GROUP,'glass',(cx,cy,GROUND_Z+(35+h)/2),(w,d,h-35))
        _facade_rhythm(batch,cx,cy,GROUND_Z+35,GROUND_Z+h,w,d,spacing=4.5)
        _tapered_prism(batch,ident+' crown',cx,cy,GROUND_Z+h-14,GROUND_Z+h,w,d,w*.78,d*.8,'glass')


def build_skyline(scene, spec, batch, materials):
    """Add the source-backed upper skyline layer to an existing MeshBatch.

    ``spec`` is accepted for the common builder signature.  Landmark
    placement intentionally comes from the audited local XY values rather
    than from a camera or from inferred future-development geometry.
    """
    del scene, spec, materials
    _st_regis(batch)
    _aqua(batch)
    _aon(batch)
    _prudential(batch, 'two-prudential-plaza', two=True)
    _prudential(batch, 'one-prudential-plaza', two=False)
    _trump(batch)
    _hancock(batch)
    _willis(batch)
    _secondary_landmarks(batch)
    return {
        'group': GROUP,
        'landmarks': [
            'st-regis-chicago', 'aqua', 'aon-center',
            'two-prudential-plaza', 'one-prudential-plaza',
            'trump-international-chicago', '875-north-michigan',
            'willis-tower','marina-city','tribune-tower','wrigley-building',
            'salesforce-tower-chicago','river-point','150-north-riverside'
        ],
        'source': 'skyline-buildings.json',
        'camera_visibility': 'No camera-based visibility filtering; occlusion is left to native scene geometry.'
    }
