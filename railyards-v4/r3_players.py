"""Small native baseball figures for the source-visible field positions."""

import math

from mathutils import Vector


GROUP = 'Players'


def _basis(angle):
    forward = Vector((math.cos(angle), math.sin(angle)))
    side = Vector((-forward.y, forward.x))
    return forward, side


def _player(batch, center, angle, uniform='cloth_white', crouch=0.0):
    """Build one standing, ready-position figure at a field coordinate."""
    center = Vector((center[0], center[1], center[2]))
    center_xy = Vector((center.x, center.y))
    forward, side = _basis(angle)
    z = center.z
    hip_z = z + 0.88 - crouch * 0.12
    shoulder_z = z + 1.35 - crouch * 0.10
    head_z = z + 1.73 - crouch * 0.06
    # Slightly separated legs keep the stance readable at aerial scale.
    for sign in (-1.0, 1.0):
        hip = center_xy + side * (sign * 0.085)
        foot = center_xy + side * (sign * 0.12) - forward * 0.08
        batch.cylinder(GROUP, 'navy', tuple((*foot, z + 0.05)),
                       tuple((*hip, hip_z)), 0.065, r1=0.045, sides=6)
    batch.ellipsoid(GROUP, uniform, (center.x, center.y, shoulder_z),
                    (0.19, 0.13, 0.30), segments=8, rings=5)
    batch.ellipsoid(GROUP, 'skin', (center.x, center.y, head_z),
                    (0.105, 0.095, 0.12), segments=8, rings=5)
    # Cap brim and torso-facing arms form the source's tiny, upright silhouettes.
    batch.ellipsoid(GROUP, 'navy', (center.x, center.y, head_z + 0.12),
                    (0.12, 0.105, 0.045), segments=8, rings=4)
    for sign in (-1.0, 1.0):
        shoulder = center_xy + side * (sign * 0.15) + forward * 0.01
        hand = center_xy + side * (sign * 0.23) + forward * 0.15
        batch.cylinder(GROUP, uniform, tuple((*shoulder, shoulder_z)),
                       tuple((*hand, z + 0.98)), 0.045, r1=0.032, sides=6)


def build_players(scene, spec, batch, materials):
    """Add nine fielders plus a batter and plate umpire."""
    z = float(spec.get('field_z', 12.0)) + 0.06
    axis = Vector((1.0, 1.0)).normalized()
    facing_home = math.atan2(-axis.y, -axis.x)

    # Positions are standard defensive spots mapped into the existing 90-foot
    # diamond and source-proportioned outfield. They are intentionally generic.
    fielders = [
        ('Pitcher', (59.0 * 0.3048 / math.sqrt(2),) * 2, facing_home),
        ('First baseman', (26.0, 1.25), math.pi),
        ('Second baseman', (21.5, 21.0), facing_home),
        ('Shortstop', (14.7, 20.1), facing_home),
        ('Third baseman', (1.25, 26.0), -math.pi * 0.5),
        ('Right fielder', (65.0, 17.0), facing_home),
        ('Center fielder', (48.0, 48.0), facing_home),
        ('Left fielder', (17.0, 65.0), facing_home),
        ('Catcher', (-0.92, -0.92), math.atan2(axis.y, axis.x)),
    ]
    for name, position, angle in fielders:
        center = Vector((position[0], position[1], z))
        _player(batch, center, angle)

    # One generic batter in the first-base-side box and the plate umpire behind
    # the catcher. Their uniforms remain role-neutral and identity-free.
    batter = -axis * 0.19 + Vector((1.0, -1.0)).normalized() * 0.60
    _player(batch, Vector((batter.x, batter.y, z)), facing_home, uniform='cloth_gray', crouch=0.08)
    umpire = -axis * 1.95
    _player(batch, Vector((umpire.x, umpire.y, z)), facing_home, uniform='cloth_black', crouch=0.18)

    scene['players_builder'] = 'r3_players'
    scene['players_group'] = GROUP
    scene['players_count'] = 11
    scene['players_position_basis'] = 'standard generic field positions; no identities inferred'
