"""Source-led pedestrian rail bridges, southern rail bascules, and Roosevelt details.

The three pedestrian crossings are the only rail crossings resolved by the
September 2026 proposal views. Their locations stay in the existing scene
frame (X east, Y north, Z up); the spec records which parts are inferred.
"""

import json
import math
from pathlib import Path


OUT = Path(__file__).resolve().parent
with (OUT / 'bridge-spec.json').open(encoding='utf-8') as _handle:
    BRIDGE_SPEC = json.load(_handle)


GROUP = 'Bridges'
PED_GROUP = 'Pedestrian rail bridges'
ROOSEVELT_GROUP = 'Roosevelt bridge detail'
SOUTHERN_RAIL_GROUP = 'Southern rail bascules'


def _hide_legacy_rail_bridges(scene):
    """Prevent the old four-copy baseline from showing through the replacement."""
    for obj in scene.objects:
        name = obj.name.lower()
        if name.startswith('r2_rail footbridge'):
            obj.hide_render = True


def _build_pedestrian_bridge(batch, crossing):
    y = float(crossing['y'])
    x0 = float(crossing['x_start'])
    x1 = float(crossing['x_end'])
    width = float(crossing['width'])
    deck_z = float(crossing['deck_z'])
    length = x1 - x0
    center_x = (x0 + x1) * 0.5
    side = width * 0.5 - 0.18

    # The source shows enclosed pedestrian links: solid walking deck, glazed
    # sidewalls, repeated aluminum mullions, and a light roof frame.
    batch.box(PED_GROUP, 'concrete', (center_x, y, deck_z - 0.18),
              (length, width, 0.36))
    batch.box(PED_GROUP, 'roof', (center_x, y, deck_z + 4.18),
              (length + 0.6, width + 0.25, 0.30))
    for side_sign in (-1, 1):
        wall_y = y + side_sign * side
        batch.box(PED_GROUP, 'glass', (center_x, wall_y, deck_z + 1.88),
                  (length, 0.14, 3.55))
        batch.line(PED_GROUP, 'aluminum',
                   [(x0, wall_y, deck_z + 0.22),
                    (x1, wall_y, deck_z + 0.22)], 0.09)
        batch.line(PED_GROUP, 'aluminum',
                   [(x0, wall_y, deck_z + 3.66),
                    (x1, wall_y, deck_z + 3.66)], 0.09)
        count = max(2, round(length / 8.0))
        for index in range(count + 1):
            x = x0 + length * index / count
            batch.box(PED_GROUP, 'aluminum',
                      (x, wall_y, deck_z + 1.9), (0.14, 0.16, 3.75))
            if index < count:
                nx = x0 + length * (index + 1) / count
                batch.line(PED_GROUP, 'aluminum',
                           [(x, wall_y, deck_z + 0.34),
                            (nx, wall_y, deck_z + 3.54)], 0.055)
                batch.line(PED_GROUP, 'aluminum',
                           [(x, wall_y, deck_z + 3.54),
                            (nx, wall_y, deck_z + 0.34)], 0.055)

    # Roof cross-members and a restrained ridge are visible in the brighter
    # north view; they also keep the glazing from reading as an empty box.
    batch.line(PED_GROUP, 'aluminum',
               [(x0, y, deck_z + 4.26), (x1, y, deck_z + 4.26)], 0.08)
    count = max(2, round(length / 12.0))
    for index in range(count + 1):
        x = x0 + length * index / count
        batch.line(PED_GROUP, 'aluminum',
                   [(x, y - width * 0.5, deck_z + 4.10),
                    (x, y + width * 0.5, deck_z + 4.10)], 0.07)

    # Each end is buried into a solid concourse/landing so the bridge cannot
    # float beside the known medical and stadium footprints.
    for end_x in (x0 + 1.8, x1 - 1.8):
        batch.box(PED_GROUP, 'concrete', (end_x, y, deck_z - 0.55),
                  (12.0, width + 2.0, 0.75))
        batch.box(PED_GROUP, 'concrete', (end_x, y, deck_z - 2.1),
                  (2.0, width + 1.2, 3.0))


def _build_roosevelt_bridge(batch):
    river_west = float(BRIDGE_SPEC['roosevelt']['river_west_x'])
    river_east = float(BRIDGE_SPEC['roosevelt']['river_east_x'])
    river_center = (river_west + river_east) * 0.5
    deck_z = float(BRIDGE_SPEC['roosevelt']['deck_z'])
    spring_z = float(BRIDGE_SPEC['roosevelt']['underarch_spring_z'])
    crown_z = float(BRIDGE_SPEC['roosevelt']['underarch_crown_z'])

    # The roadway is a dark, closed deck. The source silhouette is carried by
    # a pale arch below it, rather than by an arching truss above the deck.
    batch.box(ROOSEVELT_GROUP, 'asphalt',
              (river_center, 316.0, deck_z + 0.02),
              (river_east - river_west, 18.5, 0.18))
    for y in BRIDGE_SPEC['roosevelt']['side_y']:
        y = float(y)
        # Large pale spring arch below the deck. Its ends fall toward the
        # water-side bank and its crown meets the deck underside.
        arch = []
        for index in range(25):
            t = index / 24
            x = river_west + (river_east - river_west) * t
            z = spring_z + (crown_z - spring_z) * math.sin(math.pi * t)
            arch.append((x, y, z))
        # Deep vertical arch web, rather than a round wire silhouette.
        for a,b in zip(arch,arch[1:]):
            vertices=[(p[0],p[1]+dy,p[2]+dz)for p in [a,b]for dy,dz in [(-.24,-.65),(.24,-.65),(.24,.65),(-.24,.65)]]
            batch.add(ROOSEVELT_GROUP,'white',vertices,[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)])
        inner_arch = []
        for index in range(25):
            t = index / 24
            x = river_west + (river_east - river_west) * t
            z = spring_z + 0.9 + (crown_z - spring_z - 0.9) * math.sin(math.pi * t)
            inner_arch.append((x, y, z))
        batch.line(ROOSEVELT_GROUP, 'aluminum', inner_arch, 0.08)

        # Thin upper rail is the only prominent frame above the roadway.
        batch.line(ROOSEVELT_GROUP, 'aluminum',
                   [(river_west, y, deck_z + 1.1),
                    (river_east, y, deck_z + 1.1)], 0.10)
        for x in range(round(river_west), round(river_east) + 1, 6):
            t = (x - river_west) / (river_east - river_west)
            arch_z = spring_z + (crown_z - spring_z) * math.sin(math.pi * t)
            batch.line(ROOSEVELT_GROUP, 'aluminum',
                       [(x, y, arch_z), (x, y, deck_z + 1.1)], 0.065)

        # Two closed bascule leaves meet at a center seam. A narrow underside
        # beam and hinge plates keep the split legible without open-state cues.
        batch.line(ROOSEVELT_GROUP, 'metal',
                   [(river_west, y, deck_z - 0.12),
                    (river_east, y, deck_z - 0.12)], 0.15)
        batch.line(ROOSEVELT_GROUP, 'aluminum',
                   [(river_center, y - 0.55, deck_z - 0.25),
                    (river_center, y + 0.55, deck_z - 0.25)], 0.12)

        # Arch spandrel ties are sparse and pale, matching the source's open
        # under-bridge reading while leaving the water visible below.
        for x in range(round(river_west) + 4, round(river_east), 8):
            t = (x - river_west) / (river_east - river_west)
            arch_z = spring_z + (crown_z - spring_z) * math.sin(math.pi * t)
            if arch_z < deck_z - 0.35:
                batch.line(ROOSEVELT_GROUP, 'aluminum',
                           [(x, y, arch_z), (x, y, deck_z - 0.22)], 0.055)

    # Viaduct-level walks connect the bridge edges to the riverbank plazas.
    for y in (300.6, 331.4):
        batch.box(ROOSEVELT_GROUP, 'paving',
                  (river_center, y, deck_z + 0.03),
                  (river_east - river_west, 3.2, 0.16))
        batch.line(ROOSEVELT_GROUP, 'aluminum',
                   [(river_west, y, deck_z + 0.38),
                    (river_east, y, deck_z + 0.38)], 0.055)

    # The center joint, bank hinges, and machinery housings are the resolved
    # bascule cues. Existing blockout abutments/tender houses remain owners
    # of the full road and bank masses.
    batch.line(ROOSEVELT_GROUP, 'aluminum',
               [(river_center, 301.2, deck_z - 0.05),
                (river_center, 330.8, deck_z - 0.05)], 0.16)
    for x in (river_west, river_east):
        for y in (301.5, 330.5):
            batch.cylinder(ROOSEVELT_GROUP, 'metal',
                           (x, y, deck_z - 0.15), (x, y, deck_z + 1.85),
                           0.34, sides=10)
            if not ((x==river_west and y==301.5) or (x==river_east and y==330.5)):continue
            hx,hy=(187.7,335.4) if x==river_east else (x,y)
            # Octagonal tender houses with a stepped masonry base and
            # shallow domed copper cap, visible in the bridge reference.
            batch.cylinder(ROOSEVELT_GROUP,'stone',(hx,hy,10.0),(hx,hy,17.2),2.9,sides=8)
            batch.cylinder(ROOSEVELT_GROUP,'stone',(hx,hy,17.0),(hx,hy,21.1),2.2,sides=8)
            for theta in [i*math.tau/8 for i in range(8)]:
                px=hx+2.05*math.cos(theta);py=hy+2.05*math.sin(theta)
                batch.box(ROOSEVELT_GROUP,'glass',(px,py,19.2),(1.05,.10,2.1),theta+math.pi/2)
            batch.cylinder(ROOSEVELT_GROUP,'stone',(hx,hy,20.9),(hx,hy,21.35),2.65,sides=16)
            batch.cylinder(ROOSEVELT_GROUP,'roof',(hx,hy,21.35),(hx,hy,22.8),2.6,.5,sides=16)
            batch.cylinder(ROOSEVELT_GROUP,'metal',(hx,hy,22.8),(hx,hy,23.6),.20,.08,sides=8)



def _build_roosevelt_approach(batch):
    # Source views resolve the bridge deck's lane scale and repeated lighting,
    # while approach road placement is already owned by the blockout.
    for x in range(-250, 351, 24):
        for y in (301, 331):
            batch.cylinder(ROOSEVELT_GROUP, 'metal',
                           (x, y, 14.0), (x, y, 20.0), 0.08, 0.04,
                           sides=7)
            batch.box(ROOSEVELT_GROUP, 'lamp', (x, y, 20.0),
                      (0.65, 0.65, 0.30))
    for x in range(-250, 351, 10):
        for y in (309.85,312.95,319.15,322.25):
            batch.box(ROOSEVELT_GROUP, 'white', (x, y, 14.40),
                      (4.0, 0.12, 0.025))


def _build_southern_rail_bridges(batch):
    """Add the two historic rail bascules resolved at the south edge.

    The AECOM south aerial shows a raised steel silhouette in the lower-right
    foreground.  The live OSM frame and HAER photos place the nearer B&OCT
    bridge just north of the parallel St. Charles Air Line bridge.  This is a
    restrained silhouette study: the bridge status is abandoned/disused and
    the source does not justify operational details or a surveyed mechanism.
    """
    bridges = BRIDGE_SPEC['southern_rail_bridges']
    entries = [
        (bridges['primary'], True),
        (bridges['secondary'], False),
    ]
    for entry, raised in entries:
        y = float(entry['y'])
        x0 = float(entry['x_start'])
        x1 = float(entry['x_end'])
        width = 8.0
        deck_z = 14.0
        # Rail approach and a low west half keep the crossing legible at a
        # distance without competing with the much larger Roosevelt bridge.
        if not raised:
            batch.box(SOUTHERN_RAIL_GROUP,'metal',((x0+x1)*.5,y,deck_z),(x1-x0,width,.55))
        ranges=[(x0-98,x0),(x1,x1+55)] if raised else [(x0-98,x1+55)]
        for start,end in ranges:
            batch.box(SOUTHERN_RAIL_GROUP,'metal',((start+end)/2,y,deck_z-.15),(end-start,width,.45))
            for rail_y in (y-2.1,y+2.1):
                for offset in [-.72,.72]:
                    batch.line(SOUTHERN_RAIL_GROUP,'metal',[(start,rail_y+offset,deck_z+.42),(end,rail_y+offset,deck_z+.42)],.075)
        for start,end in ranges:
            for x in range(round(start)+5,round(end)-3,18):
                for yy in [y-2.9,y+2.9]:
                    batch.box(SOUTHERN_RAIL_GROUP,'stone',(x,yy,9.6),(1.2,1.2,8.4))
            for x in range(round(start),round(end)):
                batch.box(SOUTHERN_RAIL_GROUP,'bark',(x,y,deck_z+.12),(.22,6.8,.20))
        # Steel bank towers / machinery houses are visible as the paired
        # vertical masses framing the source's raised foreground leaf.
        for bank_x in (x0 - 2.0, x1 + 2.0):
            for bank_y in (y - 4.1, y + 4.1):
                batch.box(SOUTHERN_RAIL_GROUP, 'stone',
                          (bank_x, bank_y, 9.7), (3.2, 1.35, 8.2))
                batch.box(SOUTHERN_RAIL_GROUP, 'metal',
                          (bank_x, bank_y, 16.6), (1.0, .75, 5.0))

        if raised:
            # One upright bascule leaf at the east bank.  Two side trusses,
            # top chord, and restrained diagonals reproduce the tall open
            # silhouette visible at the image edge.
            pivot_x = x1 - 5.0
            top_x = pivot_x - 13.5
            batch.box(SOUTHERN_RAIL_GROUP,'stone',(pivot_x,y,4.5),(5.0,9.0,13.0))
            batch.box(SOUTHERN_RAIL_GROUP,'metal',(pivot_x,y,12.3),(6.0,8.4,2.6))
            batch.box(SOUTHERN_RAIL_GROUP,'rust_steel',((pivot_x+x1+3)/2,y,13.8),(x1+3-pivot_x,8.0,1.0))

            batch.quad(SOUTHERN_RAIL_GROUP,'rust_steel',[(pivot_x,y-3.7,deck_z+.25),(pivot_x,y+3.7,deck_z+.25),(top_x,y+3.7,deck_z+51),(top_x,y-3.7,deck_z+51)])
            for side_y in (y - 3.7, y + 3.7):
                bottom = (pivot_x, side_y, deck_z + .25)
                top = (top_x, side_y, deck_z + 51.0)
                batch.line(SOUTHERN_RAIL_GROUP, 'rust_steel', [bottom, top], .22)
                batch.line(SOUTHERN_RAIL_GROUP, 'rust_steel',
                           [(top_x, side_y, deck_z + 51.0),
                            (top_x - 3.8, side_y, deck_z + 45.0),
                            (pivot_x, side_y, deck_z + .25)], .18)
                for index in range(1, 5):
                    t = index / 5.0
                    p = (pivot_x + (top_x - pivot_x) * t,
                         side_y, deck_z + .25 + 51.0 * t)
                    batch.line(SOUTHERN_RAIL_GROUP, 'rust_steel',
                               [p, (top_x - 3.8 * t, side_y,
                                    deck_z + 51.0 - 6.0 * t)], .10)
            batch.line(SOUTHERN_RAIL_GROUP, 'rust_steel',
                       [(top_x, y - 3.7, deck_z + 51.0),
                        (top_x, y + 3.7, deck_z + 51.0)], .18)
        else:
            # The parallel St. Charles bridge is kept as a lower, closed
            # secondary line; its raised state is not resolved in the aerial.
            batch.line(SOUTHERN_RAIL_GROUP, 'rust_steel',
                       [(x0, y - 3.7, deck_z + .7),
                        (x1, y - 3.7, deck_z + .7)], .12)
            batch.line(SOUTHERN_RAIL_GROUP, 'rust_steel',
                       [(x0, y + 3.7, deck_z + .7),
                        (x1, y + 3.7, deck_z + .7)], .12)


def build_bridges(scene, spec, batch, materials):
    """Build the source-resolved rail links and Roosevelt bridge details."""
    del spec, materials
    _hide_legacy_rail_bridges(scene)
    for obj in scene.objects:
        if obj.name in ['R2_Roosevelt bridge','R2_OSM 1324080275'] or obj.name.startswith('R2_Bridge tender house'):
            obj.hide_render=True
    # Keep the solid approach viaducts, with a slender river-span deck so
    # the source-visible arch is exposed underneath instead of buried.
    for x0,x1 in [(-325,128),(192,355)]:
        batch.box(ROOSEVELT_GROUP,'concrete',((x0+x1)/2,316,12),(x1-x0,26,4))
    batch.box(ROOSEVELT_GROUP,'concrete',(160,316,13.8),(64,26,.65))

    for crossing in BRIDGE_SPEC['pedestrian_crossings']:
        _build_pedestrian_bridge(batch, crossing)
    _build_southern_rail_bridges(batch)
    _build_roosevelt_bridge(batch)
    _build_roosevelt_approach(batch)
