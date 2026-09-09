"""Replace the V3/V14 straight river staging slab with mapped V15 geometry.

The City of Chicago Hydro export is kept as WGS84 source geometry in
``reference-audit/v15/chicago-hydro-south-branch.geojson``.  This module applies
the shared tangent projection once, hides only the named straight staging
objects, and adds a water surface, bank walls and land infill for the part of
the old channel that the mapped river no longer occupies.  Buildings are
never moved to make the river fit; only confirmed generic context components
that fall inside the downloaded water polygon are clipped.
"""
import json
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

import r4_geo


WATER_GROUP = 'V15 River water'
BANK_GROUP = 'V15 River banks'
INFILL_GROUP = 'V15 River land infill'
WATER_Z = r4_geo.WATER_Z
LAND_TOP_Z = r4_geo.GROUND_Z
OLD_CHANNEL = (124.0, 196.0, -1000.0, 1200.0)
SOURCE_FILE = 'reference-audit/v15/chicago-hydro-south-branch.geojson'
LEGACY_STAGING_OBJECTS = ('R2_River channel', 'R2_River west quay', 'R2_River east quay')


def _project_ring(ring):
    return [r4_geo.local_xy(lat, lon) for lon, lat in ring]


def _source_path(root):
    """Resolve from either the repository root or the railyards-v4 module root."""
    candidates = [root / SOURCE_FILE, root.parent / SOURCE_FILE]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f'Unable to find {SOURCE_FILE} from {root}')


def _load_rings(root):
    source = _source_path(root)
    data = json.loads(source.read_text(encoding='utf-8'))
    rings = []
    feature_count = 0
    for feature in data.get('features', []):
        geometry = feature.get('geometry') or {}
        if geometry.get('type') != 'MultiPolygon':
            continue
        feature_count += 1
        for polygon in geometry.get('coordinates', []):
            if not polygon:
                continue
            # The downloaded Hydro features have no holes. Do not silently
            # fill a future island or hole into the water surface.
            if len(polygon) != 1:
                raise ValueError(f'Unsupported river polygon hole in {source}')
            ring = _project_ring(polygon[0])
            if len(ring) >= 3:
                rings.append(ring)
    if not rings:
        raise ValueError(f'No usable river rings in {source}')
    return rings, feature_count


def _bbox(ring):
    return (min(p[0] for p in ring), max(p[0] for p in ring),
            min(p[1] for p in ring), max(p[1] for p in ring))


def _in_ring(point, ring):
    x, y = point
    inside = False
    for a, b in zip(ring, ring[1:] + ring[:1]):
        if (a[1] > y) != (b[1] > y):
            crossing = (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]) + a[0]
            if x < crossing:
                inside = not inside
    return inside


def _water_intervals(rings, y):
    """Return merged x intervals crossed by a horizontal scanline."""
    intervals = []
    for ring in rings:
        xs = []
        for a, b in zip(ring, ring[1:] + ring[:1]):
            ay, by = a[1], b[1]
            if (ay <= y < by) or (by <= y < ay):
                t = (y - ay) / (by - ay)
                xs.append(a[0] + t * (b[0] - a[0]))
        xs.sort()
        intervals.extend((xs[i], xs[i + 1]) for i in range(0, len(xs) - 1, 2))
    intervals.sort()
    merged = []
    for left, right in intervals:
        if right <= left:
            continue
        if merged and left <= merged[-1][1] + 0.01:
            merged[-1] = (merged[-1][0], max(merged[-1][1], right))
        else:
            merged.append((left, right))
    return merged


def _segment_intersection_fraction(a, b, c, d):
    """Return the segment parameter where AB meets CD, or None."""
    ab_x, ab_y = b[0] - a[0], b[1] - a[1]
    cd_x, cd_y = d[0] - c[0], d[1] - c[1]
    denominator = ab_x * cd_y - ab_y * cd_x
    if abs(denominator) < 1e-9:
        return None
    ac_x, ac_y = c[0] - a[0], c[1] - a[1]
    t = (ac_x * cd_y - ac_y * cd_x) / denominator
    u = (ac_x * ab_y - ac_y * ab_x) / denominator
    if -1e-8 <= t <= 1.00000001 and -1e-8 <= u <= 1.00000001:
        return max(0.0, min(1.0, t))
    return None


def water_crossing(start_xy, end_xy, root):
    """Return the first fraction where a segment enters the mapped river.

    ``start_xy`` and ``end_xy`` are scene-frame XY points.  A value of ``0``
    means the start is already over water; ``1`` is returned only when the end
    point is inside water but a source edge could not be intersected due to a
    degenerate source vertex.  ``None`` means the segment does not cross the
    downloaded river polygon.
    """
    rings, _feature_count = _load_rings(root)
    start = (float(start_xy[0]), float(start_xy[1]))
    end = (float(end_xy[0]), float(end_xy[1]))
    if any(_in_ring(start, ring) for ring in rings):
        return 0.0
    fractions = []
    for ring in rings:
        for a, b in zip(ring, ring[1:] + ring[:1]):
            fraction = _segment_intersection_fraction(start, end, a, b)
            if fraction is not None:
                fractions.append(fraction)
    if fractions:
        return min(fractions)
    if any(_in_ring(end, ring) for ring in rings):
        return 1.0
    return None


def _hide_legacy_staging():
    hidden = []
    for name in LEGACY_STAGING_OBJECTS:
        obj = bpy.data.objects.get(name)
        if not obj:
            continue
        obj.hide_render = True
        obj.hide_set(True)
        hidden.append(name)
    return hidden


def _build_water_and_banks(batch, rings):
    triangles = 0
    wall_segments = 0
    min_x, max_x, min_y, max_y = -250.0, 300.0, -1250.0, 1800.0
    for ring in rings:
        bx0, bx1, by0, by1 = _bbox(ring)
        if bx1 < min_x or bx0 > max_x or by1 < min_y or by0 > max_y:
            continue
        clipped = [(x, y) for x, y in ring]
        points = [Vector((x, y, WATER_Z)) for x, y in clipped]
        for triangle in tessellate_polygon([points]):
            # Hydro rings arrive with mixed winding.  ``tessellate_polygon``
            # preserves that winding, so explicitly orient every water face
            # toward +Z; otherwise the same D2_water material reads differently
            # in reflected/rendered views despite the correct XY footprint.
            vertices = [points[index] for index in triangle]
            edge_a = vertices[1] - vertices[0]
            edge_b = vertices[2] - vertices[0]
            if edge_a.cross(edge_b).z < 0.0:
                vertices[1], vertices[2] = vertices[2], vertices[1]
            batch.add(WATER_GROUP, 'water', [tuple(point) for point in vertices], [(0, 1, 2)])
            triangles += 1
        for a, b in zip(clipped, clipped[1:] + clipped[:1]):
            if max(a[1], b[1]) < min_y or min(a[1], b[1]) > max_y:
                continue
            batch.quad(BANK_GROUP, 'stone', [
                (a[0], a[1], WATER_Z), (b[0], b[1], WATER_Z),
                (b[0], b[1], LAND_TOP_Z), (a[0], a[1], LAND_TOP_Z)])
            wall_segments += 1
    return triangles, wall_segments


def _build_land_infill(batch, rings):
    """Fill only the old river rectangle outside the mapped water intervals."""
    x0, x1, y0, y1 = OLD_CHANNEL
    step = 10.0
    sections = 0
    y = y0
    while y < y1:
        ya, yb = y, min(y + step, y1)
        intervals = _water_intervals(rings, (ya + yb) / 2)
        cursor = x0
        for water_left, water_right in intervals:
            left = max(x0, min(x1, water_left))
            right = max(x0, min(x1, water_right))
            if left > cursor + 0.05:
                batch.prism(INFILL_GROUP, 'paving',
                            [(cursor, ya), (left, ya), (left, yb), (cursor, yb)],
                            -2.0, LAND_TOP_Z)
                sections += 1
            cursor = max(cursor, right)
        if cursor < x1 - 0.05:
            batch.prism(INFILL_GROUP, 'paving',
                        [(cursor, ya), (x1, ya), (x1, yb), (cursor, yb)],
                        -2.0, LAND_TOP_Z)
            sections += 1
        y = yb
    return sections


def _make_water_cutter(rings, top_z=LAND_TOP_Z + 1.0):
    """Create a temporary closed cutter for terrain below the mapped water."""
    vertices = []
    faces = []
    min_x, max_x, min_y, max_y = -250.0, 300.0, -1250.0, 1800.0
    for ring in rings:
        bx0, bx1, by0, by1 = _bbox(ring)
        if bx1 < min_x or bx0 > max_x or by1 < min_y or by0 > max_y:
            continue
        points = [(x, y) for x, y in ring]
        start = len(vertices)
        vertices.extend([(x, y, -3.0) for x, y in points])
        vertices.extend([(x, y, top_z) for x, y in points])
        n = len(points)
        faces.append(tuple(reversed(range(start, start + n))))
        faces.append(tuple(range(start + n, start + 2 * n)))
        faces.extend((start + i, start + (i + 1) % n,
                      start + n + (i + 1) % n, start + n + i)
                     for i in range(n))
    mesh = bpy.data.meshes.new('V15 river terrain cutter mesh')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    # Source rings arrive in mixed winding directions; recalculate normals so
    # the Boolean sees every closed prism as a valid solid.
    normalizer = bmesh.new()
    normalizer.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(normalizer, faces=list(normalizer.faces))
    normalizer.to_mesh(mesh)
    normalizer.free()
    cutter = bpy.data.objects.new('V15 river terrain cutter', mesh)
    bpy.context.scene.collection.objects.link(cutter)
    return cutter


def _split_islands(obj):
    """Return temporary objects, one per connected mesh island of ``obj``."""
    source = bmesh.new()
    source.from_mesh(obj.data)
    source.verts.ensure_lookup_table()
    seen = set()
    islands = []
    for seed in source.verts:
        if seed.index in seen:
            continue
        stack = [seed]
        members = []
        while stack:
            vertex = stack.pop()
            if vertex.index in seen:
                continue
            seen.add(vertex.index)
            members.append(vertex)
            for edge in vertex.link_edges:
                other = edge.other_vert(vertex)
                if other.index not in seen:
                    stack.append(other)
        islands.append(members)
    result = []
    for number, members in enumerate(islands):
        keep = set(v.index for v in members)
        part = source.copy()
        part.verts.ensure_lookup_table()
        bmesh.ops.delete(part, geom=[v for v in part.verts if v.index not in keep], context='VERTS')
        mesh = bpy.data.meshes.new(f'{obj.name} island {number}')
        part.to_mesh(mesh)
        part.free()
        for slot in obj.material_slots:
            mesh.materials.append(slot.material)
        island = bpy.data.objects.new(mesh.name, mesh)
        island.matrix_world = obj.matrix_world.copy()
        bpy.context.scene.collection.objects.link(island)
        result.append(island)
    source.free()
    return result


def _rejoin_islands(obj, islands):
    merged = bmesh.new()
    for island in islands:
        merged.from_mesh(island.data)
    merged.to_mesh(obj.data)
    merged.free()
    obj.data.update()
    for island in islands:
        mesh = island.data
        bpy.data.objects.remove(island, do_unlink=True)
        bpy.data.meshes.remove(mesh)


def _solidify(island):
    modifier = island.modifiers.new('V15 slab thickness', 'SOLIDIFY')
    modifier.thickness = 1.0
    modifier.offset = -1.0
    bpy.context.view_layer.objects.active = island
    island.select_set(True)
    try:
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    finally:
        island.select_set(False)


def _bbox_overlaps(island, ring):
    xs = [v.co.x for v in island.data.vertices]
    ys = [v.co.y for v in island.data.vertices]
    if not xs:
        return False
    bx0, bx1, by0, by1 = _bbox(ring)
    return not (bx1 < min(xs) or bx0 > max(xs) or by1 < min(ys) or by0 > max(ys))


def _is_closed(obj):
    counts = {}
    for polygon in obj.data.polygons:
        for key in polygon.edge_keys:
            counts[key] = counts.get(key, 0) + 1
    return bool(counts) and all(count == 2 for count in counts.values())


def _mesh_area(obj):
    return sum(polygon.area for polygon in obj.data.polygons)


def _ring_area(ring):
    return abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(ring, ring[1:] + ring[:1]))) / 2.0


def _carve_water_from_terrain(scene, rings):
    """Cut the actual water volume from only terrain/park slabs it crosses."""
    carved = []
    targets = (
        'D2_Background terrain paving',
        'D2_Public realm paving',
        'D2_Bridge approach park paving',
        'D2_Northbank garden lawn',
        'R2_West district ground',
        'R2_Stadium district ground',
        'R2_East district ground',
    )
    for name in targets:
        obj = bpy.data.objects.get(name)
        if not obj or obj.type != 'MESH' or not obj.data.polygons:
            continue
        if obj.hide_render and name != 'D2_Background terrain paving':
            continue
        world_vertices = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
        if not world_vertices:
            continue
        bounds = (min(vertex.x for vertex in world_vertices),
                  max(vertex.x for vertex in world_vertices),
                  min(vertex.y for vertex in world_vertices),
                  max(vertex.y for vertex in world_vertices))
        overlapping_rings = [ring for ring in rings
                             if not (_bbox(ring)[1] < bounds[0] or
                                     _bbox(ring)[0] > bounds[1] or
                                     _bbox(ring)[3] < bounds[2] or
                                     _bbox(ring)[2] > bounds[3])]
        if not overlapping_rings:
            continue
        # Keep each Boolean local to the target's XY bounds. A single cutter
        # containing every disconnected Hydro feature can split a thin slab at
        # a water edge yet retain the intersecting side in Blender's exact
        # solver. Per-target filtering preserves the same registered polygon
        # while producing a closed, unambiguous cutter for small lawns.
        # Terrain slabs top out at the 8 m ground datum. Keeping this cutter
        # just above that datum avoids carrying a tall Boolean cap into the
        # background mesh; the separate generic-building pass below uses a
        # 120 m cutter when a full-height clip is required.
        # 2026-09-08: one cutter holding every overlapping ring let the exact
        # solver delete whole slabs (R2_West district ground went to 0 faces,
        # D2_Public realm paving from 48 to 6), which rendered as black holes.
        # Carve one ring at a time and revert any cut that removes more of the
        # slab than the ring's own footprint could justify.
        # 2026-09-08: these slabs are unions of overlapping boxes. The exact
        # solver discards a self-intersecting target wholesale (black ground
        # in every aerial), so carve each closed island on its own and rejoin.
        islands = _split_islands(obj)
        reverted = []
        kept = []
        for island in islands:
            if not _is_closed(island):
                _solidify(island)
            area_before = _mesh_area(island)
            for ring in overlapping_rings:
                if not _bbox_overlaps(island, ring):
                    continue
                snapshot = island.data.copy()
                cutter = _make_water_cutter([ring], top_z=LAND_TOP_Z + 1.0)
                cutter_mesh = cutter.data
                try:
                    modifier = island.modifiers.new('V15 mapped river cut', 'BOOLEAN')
                    modifier.operation = 'DIFFERENCE'
                    modifier.solver = 'EXACT'
                    modifier.object = cutter
                    bpy.context.view_layer.objects.active = island
                    island.select_set(True)
                    try:
                        bpy.ops.object.modifier_apply(modifier=modifier.name)
                    except RuntimeError as error:
                        raise RuntimeError(f'Failed to carve mapped river from {name}: {error}') from error
                    finally:
                        island.select_set(False)
                finally:
                    bpy.data.objects.remove(cutter, do_unlink=True)
                    bpy.data.meshes.remove(cutter_mesh)
                area_after = _mesh_area(island)
                removed = area_before - area_after
                if not island.data.polygons or removed > _ring_area(ring) * 1.05 + 25.0:
                    broken = island.data
                    island.data = snapshot
                    bpy.data.meshes.remove(broken)
                    reverted.append(round(removed, 1))
                else:
                    bpy.data.meshes.remove(snapshot)
                    area_before = area_after
            kept.append(island)
        _rejoin_islands(obj, kept)
        solidified = False
        carved.append({'object': name, 'rings': len(overlapping_rings), 'reverted_cuts': reverted, 'solidified': solidified,
                       'faces': len(obj.data.polygons)})
    return carved


def _footprint_intersects_river(footprint, rings):
    if any(_in_ring(point, ring) for point in footprint for ring in rings):
        return True
    def orient(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    def crosses(a, b, c, d):
        return (orient(a, b, c) * orient(a, b, d) < 0 and
                orient(c, d, a) * orient(c, d, b) < 0)
    for a, b in zip(footprint, footprint[1:] + footprint[:1]):
        for ring in rings:
            if any(crosses(a, b, c, d) for c, d in zip(ring, ring[1:] + ring[:1])):
                return True
    return False


def _clip_confirmed_generic_context(scene, root, rings):
    context_file = root / 'site-context.json'
    if not context_file.exists():
        context_file = root.parent / 'railyards-v4' / 'site-context.json'
    records = json.loads(context_file.read_text(encoding='utf-8'))['buildings']
    confirmed = []
    for record in records:
        way = record.get('osm_way')
        # Named/source-backed landmarks have their own owners and must never be
        # auto-deleted by this generic-context cleanup.
        if record.get('name') not in (None, '', 'Context building'):
            continue
        footprint = [tuple(point) for point in record.get('footprint', [])]
        if not footprint or way == 1324080275:
            continue  # bridgehouse is a dedicated bridge object, not generic context.
        if _footprint_intersects_river(footprint, rings):
            confirmed.append((way, footprint))
    if not confirmed:
        scene['v15_overwater_generic_buildings'] = json.dumps([])
        return []
    bounds = [(way, min(x for x, _ in foot), max(x for x, _ in foot),
               min(y for _, y in foot), max(y for _, y in foot))
              for way, foot in confirmed]
    removed = {way: 0 for way, _ in confirmed}
    for collection_name in ('D2_Existing city facades', 'D2_Existing city roofs'):
        collection = bpy.data.collections.get(collection_name)
        if not collection:
            continue
        for obj in list(collection.objects):
            if obj.type != 'MESH' or not obj.data.polygons:
                continue
            mesh = bmesh.new()
            mesh.from_mesh(obj.data)
            to_delete = []
            visited = set()
            for vertex in mesh.verts:
                if vertex in visited:
                    continue
                component = []
                stack = [vertex]
                visited.add(vertex)
                while stack:
                    current = stack.pop()
                    component.append(current)
                    for edge in current.link_edges:
                        other = edge.other_vert(current)
                        if other not in visited:
                            visited.add(other)
                            stack.append(other)
                points = [(v.co.x, v.co.y) for v in component]
                cx = sum(x for x, _ in points) / len(points)
                cy = sum(y for _, y in points) / len(points)
                for way, x0, x1, y0, y1 in bounds:
                    if x0 - 1 <= cx <= x1 + 1 and y0 - 1 <= cy <= y1 + 1 and any(_in_ring(p, ring) for p in points for ring in rings):
                        to_delete.extend(component)
                        removed[way] += 1
                        break
            if to_delete:
                bmesh.ops.delete(mesh, geom=list(set(to_delete)), context='VERTS')
                mesh.to_mesh(obj.data)
            mesh.free()
    # The generic context builder also leaves an R2_OSM solid mass behind each
    # footprint. Difference the same mapped water volume from that mass so the
    # corrected bank cannot leave a building visibly embedded in the river.
    solid_mass_clipped = []
    cutter = _make_water_cutter(rings, top_z=120.0)
    cutter_mesh = cutter.data
    try:
        for way, _footprint in confirmed:
            obj = bpy.data.objects.get(f'R2_OSM {way}')
            if not obj or obj.type != 'MESH' or not obj.data.polygons:
                continue
            modifier = obj.modifiers.new('V15 mapped river cut', 'BOOLEAN')
            modifier.operation = 'DIFFERENCE'
            modifier.solver = 'EXACT'
            modifier.object = cutter
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            try:
                bpy.ops.object.modifier_apply(modifier=modifier.name)
            except RuntimeError as error:
                raise RuntimeError(f'Failed to carve mapped river from R2_OSM {way}: {error}') from error
            finally:
                obj.select_set(False)
            solid_mass_clipped.append(f'R2_OSM {way}')
    finally:
        bpy.data.objects.remove(cutter, do_unlink=True)
        bpy.data.meshes.remove(cutter_mesh)
    result = [{'osm_way': way, 'status': 'clipped water-intersecting generic components',
               'component_count': removed[way],
               'solid_mass': f'R2_OSM {way}' if f'R2_OSM {way}' in solid_mass_clipped else None}
              for way, _ in confirmed]
    scene['v15_overwater_generic_buildings'] = json.dumps(result)
    return result


def build(scene, batch, root):
    source_path = _source_path(root)
    rings, feature_count = _load_rings(root)
    hidden = _hide_legacy_staging()
    triangles, wall_segments = _build_water_and_banks(batch, rings)
    carved = _carve_water_from_terrain(scene, rings)
    infill_sections = _build_land_infill(batch, rings)
    clipped = _clip_confirmed_generic_context(scene, root, rings)
    scene['v15_river_source'] = str(source_path)
    scene['v15_river_registration'] = 'r4_geo.local_xy: raw WGS84 -> tangent projection +33m X exactly once'
    scene['v15_river_water_z'] = WATER_Z
    scene['v15_river_control_bounds'] = json.dumps(OLD_CHANNEL)
    return {
        'source': SOURCE_FILE,
        'source_features': feature_count,
        'water_triangles': triangles,
        'bank_wall_segments': wall_segments,
        'carved_terrain_objects': carved,
        'land_infill_sections': infill_sections,
        'hidden_legacy_objects': hidden,
        'clipped_generic_context': clipped,
        'registration': 'r4_geo.local_xy (+33m X once)',
        'water_z': WATER_Z,
        'land_top_z': LAND_TOP_Z,
    }
