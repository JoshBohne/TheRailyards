"""Source-calibrated Northwestern Medicine replacement mass.

The north reference gives the medical building's visible roof corners more
reliably than the earlier small scene-spec footprint.  This module keeps
those image-space observations beside the inverse projection, so the medical
mass can be replaced without changing the shared adjacent-building module.
"""

import math

import bpy
from mathutils import Vector

from r2_geometry import text
from r3_reference_projection import source_to_plane


GROUP = 'Medical replacement'
SOURCE_IMAGE_SIZE = (1944, 1294)
ROOF_Z = 36.0
BASE_Z = 8.0

# Native north-image coordinates, origin top-left.  The trace follows the
# visible roof/cornice perimeter; the east corner glazing is represented by
# the last two points rather than a second guessed world footprint.
ROOF_PIXELS = [(1040,246),(1390,330),(1455,295),(1120,217)]


def _area(footprint):
    return sum(a[0] * b[1] - b[0] * a[1]
               for a, b in zip(footprint, footprint[1:] + footprint[:1])) * 0.5


def _edge(footprint, index):
    a = Vector((*footprint[index], 0.0))
    b = Vector((*footprint[(index + 1) % len(footprint)], 0.0))
    tangent = (b - a).normalized()
    outward = Vector((tangent.y, -tangent.x, 0.0))
    if _area(footprint) < 0:
        outward.negate()
    return (a, b, tangent, outward, (b - a).length,
            math.atan2(tangent.y, tangent.x))


def _inset(footprint, fraction):
    cx = sum(point[0] for point in footprint) / len(footprint)
    cy = sum(point[1] for point in footprint) / len(footprint)
    return [(cx + (x - cx) * fraction, cy + (y - cy) * fraction)
            for x, y in footprint]


def _facade(batch, footprint, roof_z):
    """Build a continuous brick mass and exterior curtain-wall bays."""
    batch.prism(GROUP, 'brick_dark', footprint, BASE_Z, roof_z)
    floor_height = 4.3
    floors = max(1, round((roof_z - BASE_Z) / floor_height))
    floor_height = (roof_z - BASE_Z) / floors
    for edge_index in range(len(footprint)):
        a, b, _tangent, outward, length, angle = _edge(footprint,
                                                         edge_index)
        count = max(1, round(length / 3.2))
        bay = length / count
        for floor in range(floors):
            center_z = BASE_Z + floor * floor_height + floor_height * 0.53
            for bay_index in range(count):
                center = a.lerp(b, (bay_index + 0.5) / count)
                center += outward * 0.16
                center.z = center_z
                material = 'glass_mid'
                batch.box(GROUP, material, tuple(center),
                          (bay * 0.91, 0.14, floor_height * 0.90), angle)
                q=center+outward*.10
                batch.box(GROUP+' glazing frames','aluminum',q,(bay*.91,.10,.07),angle)
                batch.box(GROUP+' glazing frames','aluminum',q,(.07,.10,floor_height*.90),angle)
                pier = a.lerp(b, bay_index / count) + outward * 0.22
                pier.z = center_z
                batch.box(GROUP, 'aluminum', tuple(pier),
                          (0.20, 0.28, floor_height * 0.90), angle)
            sill = (a + b) * 0.5 + outward * 0.23
            sill.z = BASE_Z + floor * floor_height + 0.34
            batch.box(GROUP, 'stone', tuple(sill),
                      (length + 0.18, 0.18, 0.16), angle)


def _roof(batch, footprint, roof_z):
    batch.prism(GROUP, 'roof', footprint, roof_z, roof_z + 0.22)
    for index in range(len(footprint)):
        a, b, _tangent, outward, length, angle = _edge(footprint, index)
        center = (a + b) * 0.5 + outward * 0.12
        center.z = roof_z + 0.42
        batch.box(GROUP, 'stone', tuple(center),
                  (length + 0.24, 0.28, 0.58), angle)


def _roof_garden(batch, footprint, roof_z):
    terrace = _inset(footprint, 0.76)
    batch.prism(GROUP, 'lawn', terrace, roof_z + 0.25, roof_z + 0.38)
    # The source shows a low perimeter garden rail and raised mechanical/
    # service bars behind the sign facade.
    for index in range(len(terrace)):
        a, b, _tangent, outward, length, angle = _edge(terrace, index)
        center = (a + b) * 0.5 + outward * 0.10
        center.z = roof_z + 0.72
        batch.box(GROUP, 'metal', tuple(center),
                  (length, 0.10, 0.85), angle)
    rear = _inset(footprint, 0.52)
    batch.prism(GROUP, 'roof', rear, roof_z + 0.42, roof_z + 1.05)
    for x, y in ((0.22, 0.30), (0.47, 0.30), (0.72, 0.30)):
        edge = _edge(terrace, 1)
        a, b = edge[0], edge[1]
        point = a.lerp(b, x)
        point += edge[3] * (2.0 + y * 2.0)
        point.z = roof_z + 0.40
        batch.box(GROUP, 'lawn', tuple(point), (3.2, 1.8, 0.25), edge[5])


def _corner_glazing(batch, footprint, roof_z):
    """Add the transparent stepped volume visible at the east corner."""
    index = max(range(len(footprint)), key=lambda i: footprint[i][0])
    a, b, tangent, outward, length, angle = _edge(footprint, index - 1)
    corner = Vector((*footprint[index], 0.0)) + outward * 0.35
    corner.z = (BASE_Z + min(roof_z - 1.0, 29.5)) * 0.5
    batch.box(GROUP, 'glass_lit', tuple(corner),
              (min(length * 0.42, 16.0), .25,
               min(roof_z - BASE_Z - 2.0, 20.0)), angle)


def _sign(batch, scene, footprint, materials, roof_z):
    camera = bpy.data.objects.get('R2_north')
    if camera is None:
        raise KeyError('Missing calibrated R2_north camera for medical sign')
    center = Vector((sum(point[0] for point in footprint) / len(footprint),
                     sum(point[1] for point in footprint) / len(footprint),
                     0.0))
    edge_index = max(
        range(len(footprint)),
        key=lambda i: (_edge(footprint, i)[3].x *
                       (camera.location.x - center.x) +
                       _edge(footprint, i)[3].y *
                       (camera.location.y - center.y)))
    a, b, _tangent, outward, length, angle = _edge(footprint, edge_index)
    sign_center = a.lerp(b, 0.40) + outward * 0.38
    sign_center.z = roof_z - 7.0
    sign_width = min(length * 0.66, 46.0)
    batch.box(GROUP, 'glass_mid', tuple(sign_center),
              (sign_width, 0.10, 4.0), angle)
    face_angle = math.atan2(outward.x, -outward.y)
    sign_center += outward * .12
    sign_material = materials['purple_sign']
    text(scene, batch.collection(GROUP), 'Northwestern Medicine sign',
         'Northwestern\nMedicine', tuple(sign_center), 4.7,
         sign_material, (math.pi / 2, 0.0, face_angle))
    # Keep the monogram on the same narrow sign band rather than building a
    # large glowing panel that occludes the facade.
    horizontal = Vector((math.cos(face_angle), math.sin(face_angle), 0.0))
    monogram = sign_center - horizontal * (sign_width * 0.36)
    monogram.z += 0.05
    text(scene, batch.collection(GROUP), 'Northwestern Medicine monogram',
         'M', tuple(monogram), 8.0, sign_material,
         (math.pi / 2, 0.0, face_angle))
    return {'edge': edge_index, 'center': tuple(sign_center),
            'width': sign_width}


def build_medical(batch, scene, spec, materials):
    """Build the camera-calibrated medical replacement and return metadata."""
    camera = bpy.data.objects.get('R2_north')
    if camera is None:
        raise KeyError('Missing calibrated R2_north camera for medical mass')
    footprint = [source_to_plane(scene, camera, pixel, SOURCE_IMAGE_SIZE,
                                 ROOF_Z)[:2] for pixel in ROOF_PIXELS]
    if _area(footprint) < 0:
        footprint.reverse()
    _facade(batch, footprint, ROOF_Z)
    _roof(batch, footprint, ROOF_Z)
    _roof_garden(batch, footprint, ROOF_Z)
    _corner_glazing(batch, footprint, ROOF_Z)
    sign = _sign(batch, scene, footprint, materials, ROOF_Z)
    return {
        'group': GROUP,
        'source_pixels': ROOF_PIXELS,
        'source_image_size': SOURCE_IMAGE_SIZE,
        'base_z': BASE_Z,
        'roof_z': ROOF_Z,
        'footprint': footprint,
        'sign': sign,
    }
