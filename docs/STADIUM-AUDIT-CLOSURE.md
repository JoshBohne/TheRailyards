# Stadium audit closure ledger

**Current user priority:** correct seating alignment and stadium proportions. Interior tower/stadium detail is not the focus. Further work and review should prioritize the visible seating bands, corner angles, terrace/roof massing and source compositions; interior-only refinements will not drive the next passes.

## South extension correction from September 8 references

The user clarified that the south arcade/glazed wing behind the clock tower must project from the taller stadium facade, as shown in the newly supplied closeup. This supersedes the earlier completely flush interpretation of A08. `flush_frontage` retains the upper facade datum and restores an inferred 8.5 m outward projection, with a continuous roof ledge, joined corner geometry, arched ground level, gridded glazing and narrow upper-wall windows. Source files and the inference boundary are preserved in `reconstruction-references/user-corrections-2026-09-08/`.

The existing seating correction is retained. Before/after comparisons use the same `frontage` and `south-extension` cameras. This is an exterior geometry correction; no tower-interior work is part of this pass.

The follow-up instruction fixes the river alignment and corner explicitly: the outer arcade pier face and tower exterior finish face both lie at x117.94999695 in the saved model (measured difference 0). The actual roof polygon has perpendicular adjacent edges, measuring 90.0000025 degrees within floating-point precision. The [independent south-extension review](audits/V14-SOUTH-EXTENSION-REVIEW.md) accepts this requested alignment and square corner from the plan and oblique views. Saved scene SHA256: `21fa7f2ff90f97c7680bf17f93b5707987fa8533b714521fa1da543eb8787567`. All 34,591 active seating placements continue to pass the sampled architectural clearance checks. Five final views are in `railyards-v4/review/v14/south-square/`; this pass does not claim a new interactive export or deployment.

## Exterior seating and proportion pass

The current generator lowers the rear LF roof to the common z33.4 pavilion terrace and adds closed gable ends, retaining the three LF seating tiers. RF corner rows now keep a constant elevation across their length; their endpoints recede toward the tower instead of squeezing the rake into a narrow strip at the river. The middle seating band extends into the corner, and the third-tier ends turn toward the north tower terraces while the covered top tier stays in place. Coordinates remain inferred source fits.

The independent [exterior proportions review](audits/V14-EXTERIOR-PROPORTIONS-REVIEW.md) recommends keeping these three visible improvements. Remaining priorities are the relative LF roof hierarchy, terrace projections and edge continuity, and the RF bank's sparse appearance compared with the main bowl. This review does not close the entire corner or the 23-item ledger. Earlier route and chair-pair results below belong to their stated frozen scenes.

Fixed-camera studies: `review/v14/exterior-roofs/`, `review/v14/level-rf/`, and `review/v14/upper-junction/` under `railyards-v4`. The corresponding prior scenes remain preserved in `work/audit-fixes-v14/`.

Final saved exterior scene SHA256: `8d02f77f311c769bdc7ea75dccc3d00835cb6d6e0bc08c2258f787e378f17392`. All 34591 active placements pass the sampled architectural floor/foot/body/head checks. The transformed-chair diagnostic finds 2400 intersection/contact pairs, all in the retained main-bowl seats; none involve the revised RF returns or tower-end rows. Main-bowl alignment remains open. Seven final exterior views are preserved in `railyards-v4/review/v14/exterior-final/`. These are native local Blender results, not a new interactive export or public deployment.

## Original audit and historical evidence

Baseline: V13 at `c305dd9a510ff1d7a66864b02480fc36bcb07935`.
Original independent audit: [V13 audit](audits/V13-INDEPENDENT-AUDIT.md), preserved from `work/independent-v13-audit/AUDIT.md`.
Preserved scene SHA256: `22b7801e6d0bfab64c73d82e2e18efe8dc64aea0fba1e6b5db00dbadd17cbb95`.

An item closes only with corrected saved geometry, source comparison, a view that exposes the defect, applicable whole-component checks, and independent verification. Numeric checks alone are insufficient. Hidden details and conflicting source variants must remain explicitly identified.

| ID | Finding | Status | Implementation / evidence | Independent verification |
| --- | --- | --- | --- | --- |
| V13-A01 | Left-center seating has lost its supporting bank (P1, D, high) | Implemented; bounded verification | V14 closed bank solids; evidence below | Independent center-floor, passage and manifold checks pass; A09 edge/rail residuals remain |
| V13-A02 | Two upper LF canopy plates float (P1, D, high) | In progress | V14 implementation; evidence below | Pending |
| V13-A03 | West roof lantern intrudes into occupied upper rows (P1, D, high) | Implemented; verification in progress | Lower enclosure shortened, roof anchor retained; all 30 original seat-center hits removed | Pending expanded body/roof checks |
| V13-A04 | South covered rail-link end is stranded (P1, D/S, high) | Open | Not yet corrected | Pending |
| V13-A05 | Tower balconies lack a demonstrated usable bowl/tower entry (P1, I with visible edge discontinuities, medium-high) | In progress | Bowl links, tower stairs and doors, graded riverwalk arrival; route audit below | Pending current revision |
| V13-A06 | Tower platforms dominate the source silhouette (P1, S, high) | Open | Not yet corrected | Pending |
| V13-A07 | LF pavilion/upper-bowl junction remains an abrupt cut (P1, S/D, high) | Open | Not yet corrected | Pending |
| V13-A08 | South frontage has decorative glazing over solid entry walls (P1, D/I, high for geometry, medium for intended entrances) | Open | Not yet corrected | Pending |
| V13-A09 | Retained outfield seat floors and RF return treads need cleanup (P2, D, medium-high) | Open: independent collision findings | Architectural-mesh probes pass, but transformed chair instances overlap | Phase 3 confirms representative penetrations; 2,914 intersection/contact pairs |
| V13-A10 | Tower architecture is simplified beyond source fidelity (P2, S, high) | Open | Not yet corrected | Pending |
| V13-A11 | Bowl tier/aisle pattern is only an approximation (P2, S, medium-high) | Open | Not yet corrected | Pending |
| V13-A12 | Roof and light gantries lack source construction/detail (P2, S/I, high for appearance) | Open | Not yet corrected | Pending |
| V13-A13 | Boards, backs/supports and content remain approximate (P2, S, high) | Open | Not yet corrected | Pending |
| V13-A14 | CF scoreboard plaza is over-solid and under-detailed (P2, S, high) | Open | Not yet corrected | Pending |
| V13-A15 | Park layout, retaining frontage and grand-stair composition differ (P2, S, high) | Open | Not yet corrected | Pending |
| V13-A16 | Continuous accessible vertical routes remain unproven (P2, I, high as limitation) | Open | Not yet corrected | Pending |
| V13-A17 | River edge does not resolve boat access and edge safety (P2, S/I, medium-high) | Open | Not yet corrected | Pending |
| V13-A18 | River-gallery vegetation intersects its structure (P2, D, high) | Open | Not yet corrected | Pending |
| V13-A19 | Hall and medical building massing/facades miss source character (P2, S, high) | Open | Not yet corrected | Pending |
| V13-A20 | South urban context is massing, not 1:1 reconstruction (P2, S, high) | Open | Not yet corrected | Pending |
| V13-A21 | A3 background and immediate riverbanks are incomplete (P2, S, high) | Open | Not yet corrected | Pending |
| V13-A22 | Rail/road/bridge geometry and variants are unresolved (P2, S/I, high) | Open | Not yet corrected | Pending |
| V13-A23 | Lighting/material scale prevents visual equivalence (P3, S, high) | Open | Not yet corrected | Pending |

## Current correction evidence

### A01: retained left-center bank

`r14_audit.py:restore_bank` rebuilds the original V12 row-cap footprints as closed solids, split around the V13 passage. It preserves active seat instances and a soffit at z18.90 over the entrance. Recalculating normals alone did not fix the batched-solid boolean failure; the implementation no longer relies on that boolean.

The all-active-seat center-floor probe found zero missing floors in the retained left-center bank (932 flagged in the audit). Seventeen separate legacy outfield seats remain flagged under A09. All 417 park-passage samples still pass floor, obstacle and headroom checks. Fresh views: `railyards-v4/review/v14/bank-front.png`, `bank-underneath.png`, and `park-underpass.png`. Independent verification of frozen phase-1 scene confirms 971 active bank seats supported, 565 passage samples clear, and zero non-manifold edges in the rebuilt solids. Expanded probes found one peripheral foot sample and seven distinct seats near the old vomitory rails; these remain open under A09. Evidence: `work/audit-fixes-v14/independent-phase1/bank-verification.json`.

### A02/A07: LF pavilion and roofs

The perimeter-frame study is rejected: 248 LF seats have at least one sampled field sightline blocked by its added columns. B4 shows a masonry pavilion, rooftop dining shelter, a taller pitched roof mass and rear clerestory; B6 shows two open field-facing galleries. The replacement must resolve this connected composition while retaining the three requested seating tiers. Frozen experiment and evidence remain in `work/audit-fixes-v14/phase1-review.blend` and `independent-phase1/roof-sightlines.json`; they are not acceptance evidence.

### A03: west roof lantern

The roof anchor, top z56 and 11 by 9 m enclosure footprint are preserved. The lower enclosure now starts at z49.1, with floor soffit z48.85. A fresh whole-model seat-center upward probe removes all 30 original west-lantern hits. The remaining 34 hits comprise 33 low RF tread contacts and one tower contact, under A09/A05. `railyards-v4/review/v14/lantern-clearance.png` exposes the underside above the crowd; standing-body and roof-support validation remains pending.

## Additional explicit tower/frontage acceptance criteria

The user's September 7 corrections extend A05/A06/A10 and exterior-frontage work. Reference images and original wording are retained under `reconstruction-references/user-corrections-2026-09-07/`.

- Reconstruct the low arched/glazed RF frontage flush with the intended main-building face and roof/deck edge. Verify actual wall geometry, not only a shortened roof.
- Shift the clock tower toward the river so the face nearest home plate aligns with the RF foul pole; verify the footprint/face, not the center.
- Deliver an overhead face/pole alignment view and a fixed source/current frontage comparison. Reconcile attached bowl, decks, galleries, roofs and access routes after the shift.
- Public site/footer edits remain owned by the coordinating task. This repair branch delivers model/generator/export evidence and does not compete with that task's site edits.

## Subsequent local correction studies

- A02/A07: replaced the rejected frame with two open pavilion galleries and three pitched roof volumes. The LF-only 14,180-ray sightline sample has zero hits against the new pavilion. Source fit and level connections remain open.
- A04: rebuilt three B6-based crossings with open ends, receiving landings, stairs and conceptual lift shafts. After opening the actual facade/medical corridors, all 993 sampled span/stair/landing positions pass floor, headroom and body checks (`receiver-check-self.log`). Fresh source comparison and independent review are still required.
- A05/A06/A08: the tower footprint near face moves to model x100, aligned to the retained RF foul-pole datum; flags move with it. West-side rows and barrel canopy are rebuilt at uniform spacing. Compact north terraces, a hollow shaft, actual doorways, internal stairs and a quay foundation/arrival are in progress. The lower RF frontage is rebuilt on the main facade datum, including its wall, floor, arch openings and roof edge.
- A09/A11: old bowl rails used two incompatible point-index grids, while the seat gaps use normalized arc length. Both old rail sets are replaced with the actual gap alignment and three stair risers per seat row. All 1,078 originally flagged main-bowl seats are retained. The legacy outfield rows use supported caps and inset interpolated seat positions. Return rakers follow the actual row curves, instead of chords that emerged through low RF seats.
- Full-model diagnostics now include guards, rotated seat feet, low concrete contacts and body envelopes. The initial rail-inclusive pass found 1,051 body rays and 353 head rays; the aisle pass reduced this to 14 body rays and 2 head rays, before the small bank/backstop cleanup. These counts are diagnostic hits, not certified usability/capacity figures. No item closes from counts alone.


## Phase-2 independent review and angular RF correction

Independent review of the preserved phase-2 scene accepts only the tower's outer-stone x100 registration and the flush placement of the frontage. It rejects the LF pavilion's detached roof composition. The original 993 receiver probes pass, but expanded 2,715-point testing finds three western ground continuations blocked or unsupported; the 69–98 m bridge spans also need a coherent modeled structural system. A04 remains open. See `work/audit-fixes-v14/phase2-independent-review.md` and its frozen evidence folder.

At 11:10 PM the user clarified that RF seating must have straight angled faces and no elevated seating along the river-facing wall; only the low bank below the outfield concourse remains there. The source crop is preserved as `reconstruction-references/user-corrections-2026-09-07/source-angular-rf-seating.png`.

`r14_seating.py:angular_rf_return` replaces the curved RF return with straight diagonal rows and tapers the river endpoint's rear floor to the retained bank datum of 17.01. Supporting caps, fascia, rails, stair aisles and rakers use the same point function. Chairs with feet beyond the clipped row caps are omitted together with their occupants. These are reconstruction coordinates, not surveyed source dimensions. The V13 generator keeps its original default behavior; V14 supplies the optional straight-point mapping.

Fixed overhead and corner studies are in `railyards-v4/review/v14/angular/`, published to the local live review with the preceding V14 render and the user's source. This visibly removes the rounded return. Terrace-to-bowl connections and complete tower routes remain open, and the angular study has not received independent acceptance.

Angular saved-scene diagnostics (`2e11aa5cd95c390d00d117243d5881acd584deca071b760cc723b92265288e6d`): 1,697 active RF-return chairs after omitting ten edge placements; zero RF seat floor/foot/headroom/low-contact/body hits. The 34,392-seat whole-scene diagnostic retains three foot misses (two LF-return samples, one main-bowl sample); 565 park-passage probes pass. This is not a full route or structural acceptance.

Clean V13-to-V14 rebuild supersedes the incremental study diagnostic: saved scene `0857c96ba9d3c271d2ea198edb4b30d0b4c038df8220019afe433dc08f517da4` contains 34,390 active seat placements with zero sampled center-floor, foot-floor, low-contact, headroom or body failures; all 565 park-passage samples pass. The clean generator also reapplies the bank/backstop edge omissions that the incremental study lacked. Tower/bridge destination routes, pavilion source fit and structural continuity remain open.


## Tower connection revision (phase 3)

Saved scene SHA256 `d9cf903626d58aa2b14bdc4838d68c83f5a422bc45e92d991eeca938ea212a5d` is frozen as `work/audit-fixes-v14/phase3-review.blend`. The lower two terrace floors now join the real bowl concourse gaps; an upper stair reaches the existing cross aisle. A shared column/beam/braced frame carries the three terraces. The tower has actual west portals through the completed frontage/end-wall batches. Interior slabs and stair landings clear the closely spaced 26.4/28.6 levels. The ground arrival follows the actual sloping riverwalk, replacing the fixed 4.95 stair that descended underneath it.

`verify_tower_v14.py` tests 1,285 explicit route samples with zero floor/headroom/body hits: internal treads, doorways, terrace links, upper stair and graded quay arrival/destination. `verify_audit_v14.py` independently checks all 34,390 active seat placements and 565 park-passage samples, with zero sampled failures. These are geometric diagnostics with documented envelopes, not structural/accessibility/capacity certification or proof of every possible route.

Fresh fixed plan/corner renders and an unsaved east-shell cutaway are in `railyards-v4/review/v14/terrace-links/` and the live review. The source scene retains its complete outer shell. Independent phase-3 review reproduced the route passes but found unprotected lift-well edges and chair-to-chair penetrations; see the findings below. A05/A06 remain open to source silhouette, route coverage and support findings; no unrelated audit item is closed by these passes.


### Phase-3 independent findings supersede broad seat-clearance interpretations

The [phase-3 report](audits/V14-PHASE3-REVIEW.md) reproduces 34,390 architectural seat-envelope checks and expands the tested tower routes to 3,583 positions without a floor/head/body failure. However, the architectural BVH omits Geometry Nodes chair instances. A separate transformed-chair mesh check reports 2,914 intersection/contact pairs (2,400 main bowl; 514 RF return), and isolated representative renders confirm actual chair penetration. **A09 remains open.** Correct the actual row/instance arrangement and add chair-pair coverage; do not equate floor clearance with collision-free seating.

The same frozen scene has 18 tested upper lift-well edges with no guard or enclosure. A subsequent generator revision encloses the shaft, shows closed static landing doors and adds protection to exposed stair turns. That revision is separate from the reviewed hash and requires its own verification. The lift is conceptual; machinery, operation and capacity are not modeled or certified.


### Shaft protection follow-up (phase 4)

The saved revision `5a738d598569600a73bdab790536f5077f02cd2acff1c23e42da4651b413165c` adds a continuous glazed lift enclosure, closed landing-door panels, a flush ground cab floor and guards around exposed south stair turns. The enclosure continues above the highest landing. The final top extension was applied through the live Blender MCP scene and reflected in `r14_tower.py`; subsequent checks read the saved file.

All 1,285 explicit tower route samples still pass, and all 18 upper shaft-edge locations have barriers at both tested heights. The architectural seat-envelope and 565 park-passage checks also pass. This does not resolve the 2,914 reported chair-pair contacts/intersections or the wider source-fidelity findings. The [independent phase-4 follow-up](audits/V14-PHASE4-REVIEW.md) accepts the specific shaft-edge correction: all 18 tested edges are protected and all 3,583 expanded route points remain clear. It does not grant full A05/source-fidelity acceptance.
