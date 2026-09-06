"""Source-projected centerfield restaurant and occupied terrace."""

import math,random

import bpy
from mathutils import Vector

from r3_reference_projection import source_to_plane
from r2_geometry import instances
from r3_public_realm import inside


GROUP = 'Centerfield restaurant replacement'
SOURCE_IMAGE_SIZE = (1944, 1294)
BASE_Z = 8.0
ROOF_Z = 22.0
TERRACE_Z = 22.22

# Native north image trace.  The board occludes the back roof edge; the two
# upper points are therefore a documented interpolation between visible roof
# corners, while the lower sequence follows the curved river frontage.
ROOF_PIXELS = [(420,700),(565,799),(590,809),(620,812),(645,808),
               (675,795),(910,659),(892,630),(756,630),(700,655),
               (510,680),(425,688)]


def _area(points):
    return sum(a[0] * b[1] - b[0] * a[1]
               for a, b in zip(points, points[1:] + points[:1])) * 0.5


def _edge(points, index):
    a = Vector((*points[index], 0.0))
    b = Vector((*points[(index + 1) % len(points)], 0.0))
    tangent = (b - a).normalized()
    outward = Vector((tangent.y, -tangent.x, 0.0))
    if _area(points) < 0:
        outward.negate()
    return (a, b, tangent, outward, (b - a).length,
            math.atan2(tangent.y, tangent.x))


def _inset(points, fraction):
    cx = sum(point[0] for point in points) / len(points)
    cy = sum(point[1] for point in points) / len(points)
    return [(cx + (x - cx) * fraction, cy + (y - cy) * fraction)
            for x, y in points]


def _facade(batch, footprint):
    batch.prism(GROUP, 'brick_dark', footprint, BASE_Z, ROOF_Z)
    floors = 3
    floor_height = (ROOF_Z - BASE_Z) / floors
    for edge_index in range(len(footprint)):
        a, b, _tangent, outward, length, angle = _edge(footprint,
                                                         edge_index)
        count = max(1, round(length / 2.8))
        bay = length / count
        for floor in range(floors):
            center_z = BASE_Z + floor * floor_height + floor_height * 0.52
            for bay_index in range(count):
                center = a.lerp(b, (bay_index + 0.5) / count)
                center += outward * 0.16
                center.z = center_z
                material = ['glass_dim', 'glass_mid', 'glass_lit',
                            'glass_mid'][(bay_index + floor + edge_index) % 4]
                batch.box(GROUP, material, tuple(center),
                          (bay * 0.85, 0.14, floor_height * 0.83), angle)
                pier = a.lerp(b, bay_index / count) + outward * 0.22
                pier.z = center_z
                batch.box(GROUP, 'brick_light', tuple(pier),
                          (0.20, 0.28, floor_height * 0.90), angle)


def _cornice(batch, footprint):
    batch.prism(GROUP, 'roof', footprint, ROOF_Z, ROOF_Z + 0.20)
    for index in range(len(footprint)):
        a, b, _tangent, outward, length, angle = _edge(footprint, index)
        center = (a + b) * 0.5 + outward * 0.11
        center.z = ROOF_Z + 0.36
        batch.box(GROUP, 'stone', tuple(center),
                  (length + 0.18, 0.28, 0.52), angle)


def _terrace(batch, footprint):
    terrace = _inset(footprint, 0.95)
    batch.prism(GROUP, 'paving', terrace, TERRACE_Z, TERRACE_Z + 0.16)
    for index in range(len(terrace)):
        a, b, _tangent, outward, length, angle = _edge(terrace, index)
        center = (a + b) * 0.5 + outward * 0.10
        center.z = TERRACE_Z + 0.50
        batch.box(GROUP, 'metal', tuple(center),
                  (length, 0.10, 0.85), angle)
    # The source terrace is shared with the field-side deck.  This short,
    # broad landing gives the restaurant a readable connection to that deck.
    a, b, _tangent, outward, length, angle = _edge(terrace, 0)
    landing = a.lerp(b, 0.48) + outward * 3.2
    landing.z = TERRACE_Z + 0.08
    batch.box('Centerfield terrace connection', 'stone', tuple(landing),
              (min(length * 0.62, 30.0), 6.0, 0.16), angle)
    return terrace


def _dining(batch, terrace):
    center = Vector((sum(point[0] for point in terrace) / len(terrace),
                     sum(point[1] for point in terrace) / len(terrace),
                     TERRACE_Z + 0.18))
    tangent = _edge(terrace, 0)[2]
    outward = _edge(terrace, 0)[3]
    for along, across in ((-12, -3), (-4, 2), (5, -2), (13, 3),
                          (20, -1)):
        point = center + tangent * along + outward * across
        batch.cylinder('Centerfield terrace dining', 'metal', tuple(point),
                       (point.x, point.y, point.z + 0.68), 0.08, sides=8)
        batch.cylinder('Centerfield terrace dining', 'white',
                       (point.x, point.y, point.z + 0.68),
                       (point.x, point.y, point.z + 0.76), 0.68, sides=12)
        for side in (-1, 1):
            chair = point + tangent * (side * 1.05)
            batch.box('Centerfield terrace dining', 'metal',
                      (chair.x, chair.y, point.z + 0.34),
                      (0.42, 0.42, 0.10), math.atan2(tangent.y,
                                                     tangent.x))


def build_restaurant(batch, scene, spec, materials):
    """Build the source-projected CF restaurant and return serializable data."""
    camera = bpy.data.objects.get('R2_north')
    if camera is None:
        raise KeyError('Missing calibrated R2_north camera for restaurant')
    footprint = [source_to_plane(scene, camera, pixel, SOURCE_IMAGE_SIZE,
                                 ROOF_Z)[:2] for pixel in ROOF_PIXELS]
    if _area(footprint) < 0:
        footprint.reverse()
    _facade(batch, footprint)
    _cornice(batch, footprint)
    terrace = _terrace(batch, footprint)
    _dining(batch, terrace)
    def point(pixel,z):return source_to_plane(scene,camera,pixel,SOURCE_IMAGE_SIZE,z)
    shade=[point(p,25.4)for p in [(565,725),(720,710),(711,735),(688,760),(655,772),(620,774),(586,760),(570,742)]]
    batch.add('Centerfield board canopy','roof',shade,[tuple(range(len(shade)))])
    bench=[point(p,22.7)for p in [(550,759),(565,776),(590,789),(620,792),(653,785),(670,773)]]
    batch.line('Centerfield curved terrace bench','white',bench,.38,sides=8)
    walker=bpy.data.objects.get('D2_Walking visitor')
    if walker:
        rng=random.Random(6601);positions=[]
        for i in range(700):
            px=rng.uniform(430,910);py=rng.uniform(640,802)
            # Leave board and its small canopy clear, as in the reference.
            if 548<px<722 and py<773:continue
            q=point((px,py),TERRACE_Z+.18)
            if inside(q[:2],terrace):positions.append(q)
        instances(scene,batch.collection(GROUP),'Centerfield terrace visitors',walker,positions,
                  [(0,0,rng.random()*math.tau)for _ in positions])

    return {
        'group': GROUP,
        'source_pixels': ROOF_PIXELS,
        'source_image_size': SOURCE_IMAGE_SIZE,
        'base_z': BASE_Z,
        'roof_z': ROOF_Z,
        'terrace_z': TERRACE_Z,
        'footprint': footprint,
    }
