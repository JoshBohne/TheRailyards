"""Resolve the two parallel southern rail bridges as distinct V15 landmarks.

The V13 riverfront collection draws both parallel bridges in the same raised
pose. The Library of Congress B&O survey specifically captions the raised
span, hinge and counterweight as B&O, while its adjacent St. Charles view is a
separate bridge. V15 therefore keeps the registered east-bank hinge direction,
raises only B&OCT, and leaves St. Charles closed until a source pose resolves
it independently.
"""
import json

import bpy


def _remove_collection(name):
    collection = bpy.data.collections.get(name)
    if not collection:
        return False
    for obj in list(collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(collection)
    return True


def build(scene, batch, root):
    del root
    removed = []
    for name in ('R13_Rail bascules', 'D2_Southern rail bascules', 'Southern rail bascules'):
        if _remove_collection(name):
            removed.append(name)

    # The existing source-led implementation already owns the registered
    # spans and puts the raised primary hinge at x_end - 5 on the east bank.
    from r3_bridges import _build_southern_rail_bridges
    _build_southern_rail_bridges(batch)
    scene['v15_southern_bridge_pose'] = json.dumps({
        'primary': {'name': 'B&OCT Bridge', 'y': -374.0, 'x_start': 145.0,
                    'x_end': 198.0, 'pose': 'raised', 'east_pivot_x': 193.0},
        'secondary': {'name': 'St. Charles Air Line Bridge', 'y': -393.0,
                      'x_start': 136.0, 'x_end': 207.0, 'pose': 'closed',
                      'east_pivot_x': 202.0},
        'source_basis': [
            'LOC HAER IL-67 captions 5-7 identify the raised B&O span, counterweight and hinge.',
            'LOC HAER IL-67 caption 2 identifies St. Charles as the adjacent bridge beyond B&O.',
            'OSM/bridge-spec east-bank geometry retains the registered east pivots.'
        ],
        'inferred': ['Exact machinery, operating state and structural dimensions remain schematic.']
    })
    return {
        'removed_collections': removed,
        'primary': {'name': 'B&OCT Bridge', 'y': -374.0, 'pose': 'raised', 'east_pivot_x': 193.0},
        'secondary': {'name': 'St. Charles Air Line Bridge', 'y': -393.0, 'pose': 'closed', 'east_pivot_x': 202.0},
        'status': 'Separated parallel bridge identities; only B&O raised from LOC source pose.'
    }
