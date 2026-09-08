# Independent phase-3 review

Frozen authority: `phase3-review.blend`, SHA-256 `d9cf903626d58aa2b14bdc4838d68c83f5a422bc45e92d991eeca938ea212a5d`. Subsequent guard, seat or generator corrections are outside this report.

**A05 remains open for unprotected shaft edges. A09 remains open for chair-to-chair collisions omitted by the submitted architecture-only probe.** Route continuity and sampled architecture clearance improve substantially. The RF return now satisfies the narrow straight-diagonal/low-river-end direction, but visible terrace/source fidelity remains open.

## Results

| Scope | Independent result | Acceptance |
| --- | --- | --- |
| Submitted all-seat envelope | Reproduced 34,390 active seats, zero architecture-floor/head/body failures. | Valid result within its stated raw-mesh scope; not proof of clearance from adjacent instanced chairs. |
| Park route | Reproduced 565 points, zero failures. | Retains the narrow park-arcade-to-field passage pass. |
| Tower routes | 3,583 points including the submitted 1,285 plus added joins, stair turns and width offsets; zero floor/head/body failures. | Narrow usable-path clearance pass. |
| Upper shaft protection | 18 tested upper-floor edge locations have no barrier at either 0.6 or 1.0 m, with drops of 11.84–39.44 m. | A05 open: direct, unprotected fall paths into the modeled lift well. |
| Chair instances | 2,914 pairs report surface intersection/contact in transformed chair meshes: 2,400 main bowl and 514 RF return. Representative pairs visibly penetrate. | A09 open. Complete pair list supplied for correction and exact recheck. |
| RF shape | Fresh plan/corner renders show straight diagonal rows tapering toward the low retained river bank. | Pass this directional correction only. |
| Tower terraces/source fit | Broad, bare stacked terraces and the triangular upper concourse junction still differ from the source's occupied and compact tower junction. | Source fidelity remains open. |

## A05 route scope

`dense-tower-routes.json` and `verify_dense.py` document the expanded 3,583 probes. The extension adds:

- North-entry circulation to the west stair landing at every served level.
- A continuous route from both west portals around the south/east side of the lift core to the stair landing.
- Crosswise traversal of every intermediate stair landing.
- Lateral offsets of ±0.4 m on submitted stair treads, entries, terrace center paths, upper-link stair/approach, ground approach and quay ramp. Each offset retains the submitted 0.3 m body-ray envelope.

These additions find no new floor/head/body failures. They cover the closely spaced z26.4/28.6 circulation surfaces, upper stair connection and arrival beyond the ramp onto the actual quay mesh. The z26.4 floor has only about 2.06 m to the underside of the z28.6 floor; this clears the test's 2 m criterion but has little margin. The ramp test computes the retained quay grade and then tests the actual geometry below that path; it is not a nominal z4.95 destination check.

The width sampling is useful passage evidence, not an accessibility, crowd-capacity, complete edge-protection or building-code assessment. It does not establish that every point on the entire terraces is usable.

## A05 protected-edge defect

The modeled lift has corner posts, portal frames and a ground cab floor, but no continuous shaft enclosure or closed doors at upper landings. On all six upper levels (20, 26.4, 28.6, 32.6, 39, 47.6), north/south/east floor strips directly abut the open well.

`shaft-edge-diagnostics.json` tests 18 such locations. At each, two horizontal rays toward the well at heights 0.6 and 1.0 m find no barrier within 0.8 m. A downward ray just beyond the edge then reaches the ground cab floor, producing these drops:

| Floor z | Drop into well |
| --- | --- |
| 20 | 11.84 m |
| 26.4 | 18.24 m |
| 28.6 | 20.44 m |
| 32.6 | 24.44 m |
| 39 | 30.84 m |
| 47.6 | 39.44 m |

Example north edge: x109.850, y-74.583, z26.4. A clear circulation centerline alongside an open shaft does not make the floor safe. Close the shaft sides and represent closed static landing doors or equivalent protection before accepting the inferred core. Intermediate stair landings also need deliberately checked exposed-edge guards; the current generator adds flight handrails, but does not comprehensively enclose the intermediate landing perimeter. The 18 confirmed failures above are lift-well failures, not a claim that every stair landing edge was exhaustively tested.

## A09 omitted instance collisions

The submitted BVH collects only raw polygon meshes. Seats are Geometry Nodes point instances whose owner meshes have no polygons, so they are absent as obstructions. The submitted result correctly establishes sampled clearance from architectural raw meshes; it cannot establish chair-to-chair clearance.

`verify_seat_pairs.py` reads every active visible seat point, rotation and scale. It applies this transform to each local vertex of `D2_Seat source`:

`owner.matrix_world @ Translation(point.co) @ Rotation(rotation.z, Z) @ Diagonal(scale.x, scale.y, scale.z, 1)`

This reproduces the generator's Object Info → Instance on Points placement. Source chair bounds are x[-0.2475,0.2475], y[-0.20,0.215], z[0,0.91]. A KD tree selects pairs within 0.8 m, followed by `BVHTree.FromPolygons` and `overlap` on the actual transformed source surfaces. That nearby-pair bound targets local collisions; it is not a formal exhaustive arbitrary-instance collision proof.

The test reports 2,914 intersection/contact pairs. BVH overlap does not provide signed penetration volume, and touching or nearly coplanar surfaces may be included. Do not call all 2,914 deeply penetrating pairs. However, isolated renders of two actual pairs establish material penetration rather than harmless contact:

- RF return indices 408/486, center distance 0.3251 m: the red chair's arm penetrates the blue seat and their bodies overlap. `rf-seat-pair.png`.
- Main bowl indices 151/152, center distance 0.3998 m: adjacent chairs are rotated across one another with visibly intersecting seats/legs. `main-seat-pair.png`.

These diagnostic renders preserve the actual local meshes, positions, rotations and scales, translating the pair together for framing and recoloring the chairs red/blue. They isolate the pair; they are not full-scene material renders.

`seat-pair-diagnostics.json` contains the complete detected pair list with object names, indices, centers, distances and intersecting-face counts. `representative-chair-triangles.json` contains the representative transforms, transformed vertices, source polygons and intersecting polygon pairs. Both are generated by the supplied script. Main-bowl failures show that correction must extend beyond the newest RF taper. Resolve spacing/orientation at the actual intersections, then rerun architecture and chair-pair tests on a new frozen hash.

## Visual source comparison

Fresh unchanged-scene views: `tower-plan.png`, `tower-corner.png`, `frontage.png`. Relevant source: `reconstruction-references/user-corrections-2026-09-07/source-angular-rf-seating.png`.

The old curved RF return is gone. Straight diagonal rows now taper toward the river endpoint at the retained low-bank datum, leaving only a low seating bank along the wall. That is a meaningful correction to the user's requested shape. The tightly compressed chairs at the endpoint still prevent physical acceptance.

The source shows populated, relatively compact terraces integrated with the bowl end, arcade and tower. The frozen model retains large empty stacked slabs, long visible support posts and a broad triangular separation around the upper connection. It establishes a traversable conceptual connection, but does not match the source 1:1. Preserve the straight RF treatment while refining the tower/terrace composition; do not restore a curved return to fill the residual space.

No acceptance of LF roof, rail bridges, other routes or the remaining 23-item audit is implied. This review wrote only its evidence directory and report and left the frozen/live scenes and production generators untouched.
