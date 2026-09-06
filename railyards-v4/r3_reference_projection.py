"""Recover points on a documented height plane from a calibrated source view."""
from mathutils import Vector


def source_to_plane(scene, camera, pixel, image_size, elevation):
    """Intersect a source-pixel camera ray with world Z=elevation.

    This reproduces source XY at the chosen height. It does not establish that
    height or recover hidden depth: each caller must document its plane prior.
    """
    old_x, old_y = scene.render.resolution_x, scene.render.resolution_y
    try:
        scene.render.resolution_x, scene.render.resolution_y = image_size
        frame = camera.data.view_frame(scene=scene)
    finally:
        scene.render.resolution_x, scene.render.resolution_y = old_x, old_y
    xmax = max(v.x for v in frame)
    ymax = max(v.y for v in frame)
    local = Vector(((2 * pixel[0] / image_size[0] - 1) * xmax,
                    (1 - 2 * pixel[1] / image_size[1]) * ymax, frame[0].z))
    direction = camera.matrix_world.to_3x3() @ local
    origin = camera.matrix_world.translation
    if abs(direction.z) < 1e-8:
        raise ValueError(f'Camera ray parallel to plane for pixel {pixel}')
    distance = (elevation - origin.z) / direction.z
    if distance <= 0:
        raise ValueError(f'Plane intersection behind camera for pixel {pixel}')
    result = origin + direction * distance
    return tuple(result)


def source_polygon(scene, camera, pixels, image_size, elevation):
    result = [source_to_plane(scene, camera, pixel, image_size, elevation) for pixel in pixels]
    area = sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(result,result[1:]+result[:1]))
    if area < 0:
        result.reverse()
    return result


def source_to_grade(scene,camera,pixel,image_size,road_y=300.0,road_z=14.1,slope=.045):
    """Intersect a source ray with z = road_z + slope*(road_y-y)."""
    origin=camera.matrix_world.translation
    on_zero=Vector(source_to_plane(scene,camera,pixel,image_size,0.0))
    direction=on_zero-origin
    distance=(road_z+slope*road_y-origin.z-slope*origin.y)/(direction.z+slope*direction.y)
    return tuple(origin+direction*distance)
