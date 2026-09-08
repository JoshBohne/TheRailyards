# Independent phase-2 review

Authority: `phase2-review.blend`, SHA-256 `f110c5c13e1515e1b78a8c522a88f787c6b6e9c15276d65b98540ee9b623492e`. Rechecked after review. This report does not describe subsequent edits to the mutable V14 scene.

Evidence: `independent-phase2/` contains nine fresh saved-scene renders, copied generator inputs, two receiver diagnostics, scripts and logs. The north/south/bridge renders use saved source cameras; closeups use the explicit fixed cameras in `render.py`. All were rendered from the frozen file without saving changes. Source references are A3, B4 and B6 plus the user's tower/frontage corrections. These are conceptual perspective renderings, not construction documentation; conflicting source views cannot establish a single surveyed geometry.

## Decision

Accept the narrowly measured tower-face registration and actual flush-frontage direction. Accept the new receiver stairs' sampled tread/turn/top-join clearance. Do **not** close A04 as a complete ground-to-ground route, or A02/A07 as a matched pavilion. Do not interpret these limited passes as complete A05/A06/A08 acceptance or engineering certification.

| Item | Finding | Decision |
| --- | --- | --- |
| A04 crossings | One physical set of three B6 crossings is used in all presets; real end openings and receiving stairs replace sealed boxes. | Accept this improvement, retaining the documented source-view conflict. |
| A04 receiver stairs | Original 993 center probes reproduce zero floor/headroom/body failures. Dense sweep adds turns/top joins, which also pass. | Narrow pass. |
| A04 ground exits | The straight ground continuation of crossing 1 west intersects the medical facade; crossing 2/3 west continues beyond its paving with no nearby floor at z8. | Open: specify and test actual destination paths, which may use side exits. |
| A04 span structure | Approximate clear bridge lengths are 98.24, 71.62 and 69.48 m, with a 0.4 m slab and thin framing but no legible deep primary spanning system. | Open conceptual structure. Endpoint stair cores alone do not explain these spans. |
| A05 tower registration | Saved clock-tower stone minimum x is exactly 100.0; saved tower anchor is x109.85. Flags retain the same +28.3122 m translation. | Pass the user-directed near-face datum; the tower center was not used as the aligned datum. |
| A05/A06 west extension | Tower-plan/corner frames show rebuilt rows and extended barrel terminating toward the moved tower. No simple stretched seat instances or old overlapping triple platform slabs remain visible. | Improved; full local route/guard/support acceptance remains open. |
| A06 terraces | Three stacked terraces now meet tower apertures, but still create a large projecting slab cluster on tall thin posts. | Open source fidelity/support articulation. This cannot yet be called the source's compact resolved tower junction. |
| A08 actual frontage | The low arcade/glazed frontage follows the stadium and reaches the tower without the former standalone projecting box. | Narrow flush-placement pass. |
| A08 exterior match | B6 shows a shallower, visually recessive long glazed arcade and relatively modest upper stadium band. Current glazing/framing is tall, regular and heavy; arches/windows lack the source's proportions and articulation. | Full façade fidelity remains open. |
| A02/A07 pavilion | Current roof cluster is three detached raised pavilion/canopy volumes. B4 shows connected masonry, lower dining shelter, central pitched roof and taller rear clerestory; B6 shows compact roof volumes over two open galleries. | Reject 1:1 closure; preserve three LF seat tiers while correcting the roof architecture. |

## Route evidence and precise limitations

`receiver-diagnostics.json`: 993 samples, zero failures. Reproduces the submitted centerline test, including 303 bridge-span samples and every receiver tread/landing center. This is useful, but it omits the surrounding destination routes.

`receiver-dense-diagnostics.json`: 2,715 total probes. Adds landing turns and straight centerline joins at z8 and z22 from local u=-1 through +2 in 0.1 m increments. No new top-join or stair-turn failures. Ground continuation produces 42 body-hit records at crossing 1 west and 30 missing-floor positions across crossing 2/3 west. The 42 records include repeated body-height/direction hits, not 42 distinct blocked locations.

- Crossing 1 west: `D2_Medical replacement brick_dark` intersects/approaches the tested body envelope around x=-155.88 to -155.38, y=138.35, z=8.
- Crossing 2 west: 15 missing-floor positions approximately x=-143.16 to -141.76, y=-30.36 to -30.26, z=8.
- Crossing 3 west: 15 missing-floor positions approximately x=-133.69 to -132.29, y=-125.69 to -125.72, z=8.

These show that the simple straight continuation is unsuitable. They **do not prove that every alternate side exit is blocked**. Next acceptance evidence should trace each receiver from bridge to stair, through its ground aperture, and onto an identified public walk or building circulation floor. Include the transition beyond the small paving pad. Lifts remain conceptual shafts, with no equipment, accessibility or capacity validation.

The bridges' visible structural system should be reconciled with B6, whose glazed links imply a more substantial supporting frame. A 98 m crossing cannot be signed off merely because sampled pedestrians have a surface below them. This is a modeling-plausibility concern, not a structural calculation or code-compliance judgment.

## Tower/frontage evidence

`snapshot.log` verifies the saved x100 outer stone datum, x109.85 tower anchor and translated flag objects. `tower-plan.png` is the clearest datum/seat arrangement view; `tower-corner.png` shows the rebuilt bowl termination and remaining broad terrace projections. The stone datum includes the tower's outer trim; do not silently relabel it as the narrower shaft wall face.

`frontage.png` demonstrates the actual frontage/roof alignment, not a billboard standing in front of the old projection. This resolves the user's central placement complaint in the frozen scene. The source correction `source-flush-frontage.png` remains visibly different in arcade height, glazing lightness, upper-window cadence and roof relationships. Exact 1:1 facade acceptance needs a registered crop comparison and another bounded geometry pass, not just the removal of the projecting footprint.

The frozen tower's full internal circulation was not independently route-certified here; the main agent was already revising that system. Keep its pending status explicit. Similarly, visual vertical posts are not evidence of adequate foundations, bracing or capacity for terrace loads.

## Left-field pavilion next correction

Compare `lf-roof-field.png` and `lf-roof-rear.png` with `independent-phase1/source-b4-lf.png` and `source-b6-lf.png`. The new field view shows an oversized open upper canopy elevated behind a separate central gable, while the rear view reveals disconnected steps and large bare slabs. B4's roof elements read as a single masonry rooftop complex with an occupied dining terrace; B6's roof complex stays compact above the open galleries.

Retain the user's three LF seating tiers. Correct the roof massing and connected walls around them: lower dining shelter, central pitched body, taller rear clerestory, shared plausible terrace and explicit gallery routes. The source does not support solving the roof mismatch by deleting a seating tier. Route links remain an acknowledged work in progress and need their own frozen-scene check once complete.

## Scope

This is a bounded phase-2 review of A04/A05/A06/A08 plus pavilion feedback. It is not a repeat of the complete V13 inconsistency audit, not a hosted-site verification, and not acceptance of unrelated outstanding findings. No models, live scenes, production generators or site files were edited by this review; only review scripts, renders and this report were written.
