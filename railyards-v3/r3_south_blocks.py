"""Native-pixel traced southern future-development masses.

The south AECOM artwork shows discrete brick buildings with individual dark
green roofs, bright parapets, and stepped heights. This module owns only that
foreground future phase and replaces the four generic boxes in ``r2_context``.
Each mass is an independent prism whose roof polygon is traced in the native
5000 x 3333 source image and projected through ``R2_south``. Heights are
inferred from the visible facade-to-roof relationships.
"""

import math,json
from pathlib import Path

import bpy
from mathutils import Vector

from r2_geometry import MeshBatch
from r3_reference_projection import source_to_plane


GROUP = 'Future development'
SOURCE_IMAGE_SIZE = (5000, 3333)
GRADE_Z = 8.0

# Coordinates are native source pixels. The first two outlines are the
# source-resolved west pair called out in review; the remaining outlines trace
# the connected middle, eastern stepped, and standalone tower masses.
MASS_SPECS=json.loads((Path(__file__).parent/'south-blocks-spec.json').read_text())['masses']


def _project_polygon(scene, camera, pixels, elevation):
    return [Vector(source_to_plane(scene, camera, pixel, SOURCE_IMAGE_SIZE,
                                   elevation)) for pixel in pixels]


def _facade_windows(batch, outer, roof_z):
    """Place source-scale warm window rhythm on each exposed prism face."""
    centroid = sum(outer, Vector((0.0, 0.0, 0.0))) / len(outer)
    floors = max(1, int((roof_z - GRADE_Z - 0.8) / 3.6))
    for index, start in enumerate(outer):
        end = outer[(index + 1) % len(outer)]
        edge = end - start
        length = edge.length
        if length < 4.0:
            continue
        tangent = edge.normalized()
        normal = Vector((edge.y, -edge.x, 0.0)).normalized()
        midpoint = (start + end) * 0.5
        if (midpoint - centroid).dot(normal) < 0.0:
            normal = -normal
        count = max(2, int(length / 3.6))
        angle = math.atan2(tangent.y, tangent.x)
        for floor in range(floors):
            z = GRADE_Z + 1.75 + floor * 3.6
            for window in range(count):
                along = (window + .5) / count - .5
                point = midpoint + tangent * (along * length) + normal * .16
                material=['glass','glass','glass_dim','glass','glass_lit'][(window+floor*2+index)%5]
                batch.box(GROUP, material, (point.x, point.y, z),
                          (length / count * .76, .10, 2.6),
                          angle=angle)
                pier=point+tangent*(length/count*.5)+normal*.06
                batch.box(GROUP,'stone',(pier.x,pier.y,z),(.13,.16,3.6),angle)
            band=midpoint+normal*.22
            batch.box(GROUP,'stone',(band.x,band.y,z+1.78),(length+.25,.30,.15),angle)


def _mass(batch, scene, camera, spec):
    roof_z = float(spec['roof_z'])
    outer = _project_polygon(scene, camera, spec['roof_pixels'], roof_z)
    footprint = [(point.x, point.y) for point in outer]
    batch.prism(GROUP, 'brick', footprint, GRADE_Z, roof_z)
    batch.prism(GROUP, 'roof', footprint, roof_z, roof_z + .28)
    # Bright parapet follows the actual roof outline rather than a generated
    # rectangle, retaining the source's crisp roof setbacks and corners.
    for index, point in enumerate(outer):
        next_point = outer[(index + 1) % len(outer)]
        delta=next_point-point;mid=(next_point+point)/2
        batch.box(GROUP,'stone',(mid.x,mid.y,roof_z+.30),(delta.length,.85,.6),math.atan2(delta.y,delta.x))
    _facade_windows(batch, outer, roof_z)


def build_south_blocks(scene, spec, batch, materials):
    """Add independent source-traced low-rise masses to an existing batch."""
    del spec
    for key in ('brick', 'roof', 'stone', 'glass_lit'):
        if key not in materials:
            raise KeyError(f"South blocks require material {key!r}")
    camera = bpy.data.objects.get('R2_south')
    if camera is None:
        raise RuntimeError('South source projection requires the R2_south camera')
    for mass in MASS_SPECS:
        _mass(batch, scene, camera, mass)
    scene['south_blocks_note'] = (
        'Independent southern future-development roof prisms projected from '
        'native AECOM south outlines; mass heights remain inferred.'
    )


__all__ = ['MASS_SPECS', 'build_south_blocks']
