# Independent phase 1 review: A01 and preliminary A02/A07

## Disposition

**A01: accept narrowly for the missing-bank-floor/support defect on this frozen scene.** The hanging-bank condition is repaired and the sampled park passage remains open. This does not sign off every seat, guard, accessibility route, or engineering property. Carry the small seat/rail edge cases below into A09.

**A02/A07: do not accept the perimeter-frame experiment as the final correction.** It connects the roofs but preserves an unsupported architectural interpretation of the source and introduces substantial field-view obstruction. Replace it with a connected pavilion, field-facing galleries and rooftop shelter/roof composition, retaining the user's required three LF seating tiers.

## Audited identity and evidence

- Frozen authority: `work/audit-fixes-v14/phase1-review.blend`.
- SHA256 verified before inspection: `ec879a0037a90cd2abc6e372161ce84ace48a7c957610c9b9b12abcca0ef91ec`.
- Read-only: no model, generator, source, or baseline edits. Scripts/renders/results are under `work/audit-fixes-v14/independent-phase1/`. A copy of the generator read for this phase is `r14_audit-reviewed.py`; the parent may continue changing its working generator.
- Independently reopened the frozen scene in Blender CLI, rendered fixed north/south/bridge and five detail cameras, reran original audit floor/headroom probes, and added independent foot/body/route/solid checks.
- MCP port9878 still reported V13, so that live scene was explicitly **not** used as V14 authority. Computer Use inspected the local live LF roof-support review, then fresh frozen-file renders supplied authoritative evidence.
- The changing `railyards-v14-static.blend`, new A03 work, and supplemental unofficial home-plate image were not used to sign off this phase.

## A01 results

| Check | Independent result | Scope |
|---|---|---|
| Original all-seat downward-floor diagnostic | All 932 prior left-center-bank failures eliminated; 17 separate legacy outfield failures remain | Same original script, same 33,805 active point-based seat placements; center-point ray starts z+0.05, distance2m, failure threshold0.5m |
| Retained bank active seat count | 971 | Zero-scale removed instances excluded |
| Expanded bank foot samples | 4,854/4,855 rays find floor within0.35m from placement z+0.05 | Center plus four world-axis offsets of0.15m; one border miss described below; these offsets are a diagnostic envelope, not exact seat-leg geometry |
| Bank center upward check including rails | 2 rail hits; no new bank soffit or roof intrusion | Hits are existing vomitory rail crossing seat envelopes, not restored slab headroom failure |
| Bank horizontal body envelope | 8 ray hits at7 distinct seat positions, all against retained rails | Radii0.24m, heights0.75/1.25m, eight horizontal directions; diagnostic envelope, not anatomical certification |
| Independent passage sweep | 565 positions: no missing floor, no sampled headroom/body obstruction | x49.2/50.1/51/51.9/52.8; y105 through161 in0.5m steps; floor z13.4–15.38; 2m upward sweep and0.23m horizontal radius at heights0.6/1.3/1.7m |
| New bank support mesh topology | 0 non-manifold edges in either concrete or paving mesh | Checks closure of explicitly split components; not a global union or engineering load-path calculation |
| Native visible evidence | Hanging rows are replaced by continuous bank solids and a bounded passage/soffit | `bank-front.png`, `bank-underneath.png`, `park-underpass.png` |

The new explicit left/right solid domains extend to the modeled foundation datum z7.9; central caps above the passage have a soffit at z18.9. Fresh front and underneath views support the intended visible connection. The passage stays open rather than being concealed by a new wall across its route.

Raw results and reusable scripts: `floor.json`, `headroom.json`, `bank-verification.json`, `floor.py`, `headroom.py`, `verify_bank.py`. The original broad headroom diagnostic still finds the other V13 issues in this frozen scene; A03 improvements being developed separately are outside this signoff.

### A09 residuals carried forward explicitly

1. **Seat1044 at (25.6774,114.4903,15.9840):** the x−0.15m foot-envelope sample misses the restored bank at the x25.6 cut edge. Its center is supported. A neighboring stair can be lower without being a valid floor for that seat's feet. Verify the actual rotated seat footprint before trimming/moving the endpoint seat.
2. **Vomitory rail crosses seat envelopes:** seat191 at (47.8255,117.5925,20.6540) has a rail0.880m above its placement; seat436 at (47.8879,115.1825,19.2530) has a rail0.501m above placement. Fresh `bank-seat-rail.png` shows the rail running through the occupied seat edge.
3. **Seven distinct seats have a rail within the sampled horizontal body envelope:** indices273,436,845,962,1044,1090,1289. The owner objects are `D2_V13 Vomitory rails metal` and `D2_V13 LF bank junction metal`. Including the additional upward-only seat191 gives8 distinct candidate seats across both diagnostics. `bank-lf-edge.png` corroborates the LF stair/seat proximity.
4. **17 legacy outfield floor failures** remain unchanged and belong to A09, not the repaired retained left-center bank.

Suggested correction: resolve endpoint seating and guard alignment together; omit or move only the conflicting seats when necessary, maintain continuous edge protection, and retest actual seat-leg/body geometry. Do not move a guard away from a drop merely to clear an occupied seat. These residuals prevent a blanket claim that every bank seat is usable, but they do not invalidate the narrow A01 repair of the missing entire supporting bank.

## A02 preliminary frame assessment

The new perimeter beams/slabs/columns eliminate the visible free-floating-sheet condition, but geometry contact is insufficient acceptance:

- `lf-roof-field.png` shows long columns standing through the view corridors in front of the retained LF seating and galleries. The scheme locates posts by distance from seat centers; that does not test the view from those seats or the circulation aisles between them.
- An independent **frame-only sightline test** at **2,836 active LF-return seats**, using an illustrative seated eye1.15m above placement and five targets (home, mound, first, third, outfield), finds **366 blocked rays affecting248 seats**. Counts by target: home76, mound72, first59, third75, outfield84. See `roof-sightlines.json` and `roof_sightlines.py`. These counts establish demonstrable occlusion by the added frame, not a certified count of unusable seats; exact eye positions and acceptable view criteria remain to be designed.
- The broad north render still reads as three stacked horizontal plates with open air around them. Official B4 and B6 describe a more substantial connected pavilion and roof program. Adding a column to every plate corner therefore solves only the superficial floating condition.
- The new post positions avoid point-seat centers by1.05m but do not establish aisle clearance, row accessibility, gallery continuity, or suitable structural sizes. Do not retain that algorithm as the architectural authority.

## What the official sources actually support

Two native source crops are included without architectural edits:

- `source-b4-lf.png`: extracted from the5,000px CBS B4 original using the normalized1944px region x775–1210/y345–670.
- `source-b6-lf.png`: extracted from the5,000×3333 B6 original at x1400–2300/y1250–1830.

**B4 north:** substantial multi-storey masonry pavilion on the park-facing sides; a continuous occupied rooftop terrace/cornice; a lower dark pitched shelter over dining; a higher sloping/thick roof element connected to visible brick/service volumes; a broad rear roof with a dark vertical window/clerestory band; open space and people where the main bowl ends beside the terrace. Roof edges visibly belong to this building, not a forest of independent poles passing through the seating.

**B6 reverse side:** a pavilion with **two open field-facing gallery levels** above the seating, integrated floor/beam/column bands, and relatively modest rooftop shelter forms. The field-side galleries need not resemble the closed masonry park facade. Both can coexist in one building. Exact enclosure depth, roof pitch, hidden rooms, and all intermediate elevations remain inferred.

**Retain the user's required three LF seat tiers.** Gallery bands are a separate architectural element behind/above them; do not automatically convert every dark gallery opening into another seating tier or delete a requested tier to simplify the roof. The current detailed row counts and return curves remain reconstruction choices, not directly measurable facts from the source.

## Concrete architectural direction for A02/A07

Treat the area as **one pavilion with three related rooftop components**, rather than three independent horizontal canopies:

1. Keep a coherent masonry exterior toward the park and connecting hall, using source-visible facade corners, window-bay rhythm and the terrace cornice as the initial fit anchors.
2. Reconstruct two field-facing open gallery bands behind the required seat tiers. Use continuous floors and rear/side support walls or columns aligned with actual pavilion bays; keep primary sightlines in front of seated spectators clear. Tie their levels into the corresponding bowl cross-aisles with real openings/landings.
3. Put an occupied rooftop terrace over the pavilion structure. Model the **lower dining shelter** as a shallow pitched canopy supported from the terrace or building edge, with visible occupied dining space under it.
4. Model the **higher dark roof element** with actual pitch, thickness and side/rear enclosure/service volume where B4 shows them. Its visible edge should meet a support or building face; avoid an arbitrary solid box that erases the open B6 galleries.
5. Model the **broad rear roof/clerestory** as part of the pavilion rear volume. Carry its loads into that volume instead of sending isolated full-height posts down through the foreground seating.
6. Finish the main-bowl/pavilion junction with continuous slab/fascia/end support and a real gallery/terrace landing. Preserve the open, occupied corner visible in B4. Do not hide the abrupt seating termination by filling the field-facing space with masonry.

### Coordinate constraints: retain versus replace

| Existing element/assumption | Direction |
|---|---|
| Fixed `R2_north`, `R2_south`, `R2_bridge` cameras and global field/river/bowl placement | **Retain.** No camera repositioning or independent geography shift to make the pavilion look correct. |
| A01 restored bank, passage x48–54, floor15.38, soffit18.9, foundation7.9 | **Retain as frozen acceptance constraints.** Roof/pavilion work should not consume the passage or remove restored row floors. |
| User-required three LF seat tiers | **Retain.** Preserve continuous floors and correspondence between rows/aisles/instances; only resolve local demonstrable collisions, with before/after evidence. |
| Original park-facing pavilion footprint/cornice derived from B4 (`r3_adjacent_buildings.py` around lines207–213; nominal terrace33.1) | **Retain as initial visual anchors, not measured dimensions.** Preserve visible north/east facade corners and hall connection while fitting the reverse face. Use the preserved earlier pavilion as reference; do not blindly restore all pre-V13 solid field-side bays. |
| Blanket y145 clipping plane introduced by `trim_pavilion` | **Replace as the architectural rule.** It was a convenient cut, not a source-backed wall/gallery boundary. Define per-level pavilion/gallery edges from both sources and local seat/aisle clearance. |
| Three horizontal roof planes at36.5/39.5/44m and their inverse-projected footprints | **Replace as fixed construction assumptions.** They can be initial silhouette bounds, but roof edge pixels and height assumptions are coupled. Refit pitched roof/eave/ridge geometry in both views; do not merely extrude the same planes downward. |
| Full-height perimeter post algorithm and1.05m distance-to-seat rule | **Reject as final arrangement.** Use actual pavilion bays/side-rear structure and explicitly test seated sightlines, foot/body envelopes and walking routes. |
| Main-bowl terminal fascia and gallery/cross-aisle interfaces | **Resolve deliberately.** Current abrupt rake end is not a source constraint. Keep source tier relationships while supplying end support and usable connections. |

Do not set one uniform roof clearance from the single tallest LF seat. Heights vary around the curved return: inspect the actual local occupied envelope beneath each roof/eave and along each gallery. Ensure the planned walking/standing space fits before fixing a ridge elevation. Conversely, do not lift the entire pavilion to avoid one localized interference.

## Cross-view acceptance safeguards

- **B4 fixed north crop:** match the masonry pavilion, terrace perimeter, relative roof/eave/ridge silhouettes, dining opening and occupied bowl-to-terrace corner; no big unsupported sheets or extraneous pole field.
- **B6 fixed south crop:** show the two open field-facing galleries and restrained rooftop shelters; retain the rail-link and hall relationships. Confirm that the B4 roof fit has not produced a tall opaque field-side wall or erased seating.
- **A3 fixed bridge view:** preserve pavilion scale relative to hall, park, boards and bowl. A locally excellent roof crop must not distort the long composition.
- **Two field-side details:** verify all three seat tiers remain legible and occupied, front views are clear of new columns/walls, and gallery routes are not blocked. Repeat frame/enclosure-only sightline diagnostics with exact planned eye locations.
- **Rear/section view:** demonstrate roof-to-pavilion support and gallery/terrace floor continuity. Connected geometry is necessary, but member capacity/lateral design remains inferred.
- **A01 regression:** repeat bank floor/route checks after pavilion replacement; the source repair must not reintroduce hanging seats or block the park passage.

If the B4 and B6 roof interpretations cannot be reconciled at fixed cameras, preserve both rendered evidence sets and identify the specific conflicting edges. Do not silently select a favorable source or claim1:1 agreement. The sources provide exterior composition and visible occupied relationships, not construction drawings.

## Handoff

A01's original defect can be marked closed with a narrow scope and A09 residuals linked. A02/A07 remain open; preserve the preliminary framing as rejected evidence, then rebuild the connected pavilion/roof arrangement. This phase is not the final independent whole-model audit.
