# Independent V13 stadium audit

**Disposition: V13 is not ready for a 1:1 fidelity or architectural-coherence claim.** The saved scene contains directly visible disconnected seating and roofs. Fix those before presentation polish. This is a visual/model audit, not engineering certification. It does not establish that every possible inconsistency has been found.

## Identity and method

- Audited repository head: `c305dd9a510ff1d7a66864b02480fc36bcb07935`, branch `fix/outfield-seating-continuity`.
- Source of truth: `railyards-v4/railyards-v13-static.blend`, SHA256 `22b7801e6d0bfab64c73d82e2e18efe8dc64aea0fba1e6b5db00dbadd17cbb95` (baseline record supplied by coordinating agent).
- Fresh Blender CLI renders reopen that file; `render_audit.py`, `details.py`, `extra.py`, `one_detail.py`, `dugout.py` write only this audit directory. Neither saved model nor generators were changed. The failed all-black `upper-seat-headroom.png` is a camera occlusion and is superseded by `upper-seat-headroom-visible.png`; it is not architectural evidence.
- Read-only Blender MCP inspection through dedicated port 9878 reported V13 filepath and 1,873 objects. Unrelated original Blender window was preserved. Computer Use inspected the local V13 review at port 8863. Public V12 site was not used as current-model evidence.
- Fixed `R2_north`, `R2_south`, `R2_bridge` cameras remain unchanged. Source-view lighting presets were applied only in unsaved render processes. Those presets also select **different geometry collections**, so this is explicitly recorded below.
- Generated `scene-inventory.json`, `headroom.json`, `floor.json`, source hashes/dimensions, fresh renders, and reusable scripts are included. Custom cameras illustrate model relationships; they are not calibrated source matches.
- Priority P1 = fix before credible model delivery; P2 = material fidelity/usability issue after P1; P3 = detail/presentation. Evidence class **D** = directly visible model defect; **S** = demonstrated source mismatch; **I** = plausible concern requiring more investigation. Confidence is confidence in the finding, not engineering adequacy.

## Source coverage and deduplication

**15 supplied files represent 3 unique perspective compositions and 1 site-plan composition.** Two pixel-identical pairs were found. Other files are crops, resizes, recompressions, or publisher/footer variants; there is no evidence that their raw file count represents 15 distinct camera views. `reference-inventory.json` retains every file and hash; `reference-contact.jpg` makes the grouping inspectable.

| Group | Files (relative to reconstruction-references unless stated) | Regions covered | Coverage/limits |
|---|---|---|---|
| B4 north aerial | `aecom-north-aerial.png`; `additional/soxon35th-2026-09-05-10-37-43.png` (pixel-identical pair); `additional/fox32-aecom-chicago-v-b4-aerial.jpg`; `additional/cbs-aecom-chicago-v-b4-aerial-final-v7-footer-joe-smith.jpg`; `v12-user-north-transition.png`; `work/outfield-v13/deliverable/tower-reference.png` | Entire visible bowl, tower/RF return, both boards, LF pavilion/canopies, CF terrace, event hall, medical building, park/arches/stairs, west rail crossings, riverwalk/boats | Inspected full view and detail regions. The tower crop adds emphasis, not a fourth perspective. Source does not reveal hidden connections or detailed service rooms. |
| B6 south/day aerial | `aecom-south-aerial.jpg`; `additional/fox32-aecom-chicago-v-b6-south-day.jpg`; `additional/soxon35th-2026-09-05-10-31-43.png` | South/west envelope, bowl/canopy silhouette, outfield backs, three rail links, medical/landing buildings, adjacent development, river crossings, skyline/lake | Inspected full view and south bridge detail. Cropped Soxon35th variant excludes some context. Development phase and bridge alignment differ from north-derived model fit. |
| A3 bridge panorama | `user-bridge-view.png`; `additional/fox32-aecom-chicago-v-a3-north.jpg`; `additional/cbs-aecom-chicago-v-a3-north-final-v5-footer-joe-smith.jpg` | Roosevelt bridge/approach park, tower/boards/bowl silhouette, hall, north park arrival, both riverbanks, skyline/background | Inspected full view. Aerial detail remains too small for row counts, doorway dimensions, or hidden supports. |
| Site plan | `railyards-site-plan.png`; `additional/soxon35th-2026-09-05-10-37-58.png` (pixel-identical pair); `additional/fox32-railyard-site-map.png` | Coarse stadium/river/rail/streets and surrounding district orientation | Compared against fresh saved-scene overhead views and scene/skyline coordinate metadata. Coarse orientation is consistent. Exact survey registration, individual parcel boundaries, and phased development cannot be certified from this diagram. |

Copies within each composition show no confidently identified architectural design change beyond crop/resolution/footer differences. **Across B4, B6, and A3, retain phase/camera/rail alignment conflicts; do not silently collapse them.** `reference-audit/crops/` was used only as discovery context; stale `current-*` files were excluded as model evidence.

## Prioritized issue ledger

### V13-A01 — Left-center seating has lost its supporting bank (P1, D, high)

**Location:** left-center bank, x approximately 26–67, y102–127, behind the outfield wall and around the new park passage. **Evidence:** `left-center-front.png`, `left-center-underseats.png`, `park-underpass.png`; `floor.json`. Large groups of seated people and chairs hang in open space, visible from both front and back. This is not an inference about a hidden foundation.

**Source:** B4, lower-right seating beside CF plaza, roughly source pixels x690–895/y530–650; source shows a coherent raked bank. **Owner:** `D2_V12 Left-center bank concrete` / `D2_Left-center bank individual seats`; `r13_outfield.py:294` (`carve_bank_passage`), `trim_lf_overlap`, underlying `r12_outfield.py:136` (`build_lc_bank`). The audit does not claim a proven boolean root cause, but saved geometry and retained instances disagree.

**Correction:** rebuild the retained bank as sound solids with a bounded passage void and retained soffit; apply the same occupied-domain rule to seats, floors, risers, rails and people. **Accept:** front, undercroft and passage views plus every active retained-bank seat has an actual floor and continuous support. Do not close the pedestrian opening merely to hide the defect.

### V13-A02 — Two upper LF canopy plates float (P1, D, high)

**Evidence:** `lf-roof-field.png`, `lf-roof-rear.png`, `R3_v4_lf_gatehouse.png`. Upper roofs are visibly separated from supporting geometry. Roof plates are at z39.5 and z44; V13 rear-club posts stop at z36.5. **Source:** B4 LF pavilion roof region x890–1190/y375–535; artwork shows occupied building/roof masses, not unattached flat sheets.

**Owner:** `D2_Left field roof canopies roof`, `D2_Left field roof fascia metal`, `D2_V13 Pavilion rear club concrete`; `r13_outfield.py:101` removes the old canopy-support collection, replacement posts near line415 stop too low; `r3_adjacent_buildings.py:217–226` generates roof levels.

**Correction:** decide the actual source-backed roof/terrace mass and give each plate a connected support/roof system; preserve clear headroom. **Accept:** both field-side and rear-side detail views and a section showing continuous connection. Beam/column sizing remains inferred.

### V13-A03 — West roof lantern intrudes into occupied upper rows (P1, D, high)

**Evidence:** `upper-seat-headroom-visible.png`, `headroom.json`: 30 main-bowl seat points have lantern glazing/frame 0.97–1.49m above their placement floor. Representative point (-64.154,-10.393,46.111), obstruction `D2_Canopy glass_lit` at ~1.489m. The render shows the low mass over seated heads. **Source:** B4 upper bowl/roof lantern, x~560–680/y185–300; reference establishes a roof feature but not permission to occupy its solid underside.

**Owner:** `r3_envelope.py:536` `_build_west_lantern`, `envelope-spec.json`, `D2_Individual seats`. **Correction:** reconcile lantern footprint/elevation and rear seat rows, provide a genuine transition; do not blindly lift the entire canopy. **Accept:** occupied-eye and standing-clearance views, sectional dimensions, all affected seats/aisles clear. This is a human-scale geometric collision finding, not a code-compliance ruling.

### V13-A04 — South covered rail-link end is stranded (P1, D/S, high)

**Evidence:** `south-bridges.png`; the southernmost covered bridge stops above the plaza without a receiving floor/stair or supporting landing at its stadium-side tip. Its west end has a skeletal landing tower. **Source:** B6 lower rail-link region x1400–2110/y2250–2450 in the 5000×3333 original shows an arrival structure/route, not an unsupported terminal box.

**Owner:** `D2_South source rail links`, `r3_south_rail_context.py:20–43`. Pixel-to-plane roof traces do not establish vertical access. **Correction:** reconstruct the source landing and a walkable end-to-end route at the bridge floor elevation. Do not force every crossing through a stadium wall if the reference intends a freestanding stair landing. **Accept:** north/south variants, plaza-eye view and route section with no suspended dead end.

### V13-A05 — Tower balconies lack a demonstrated usable bowl/tower entry (P1, I with visible edge discontinuities, medium-high)

**Evidence:** `tower-access.png`, `platforms-corner.png` from existing accepted-camera render, and model bounds. The older narrow z32.6 populated ledge abuts new platforms and seating edges; rails/row fronts and different tier levels do not establish a usable landing. The tower is surfaced/solid where access would be needed. One occupied tower-end seat has a cornice only 1.712m above its placement floor.

**Source:** B4 tower crop: occupied connected terraces. **Owner:** `r13_outfield.py:tower_platforms`, `r12_outfield.py` tower-end extension, `D2_RF structure paving`, `D2_V12 Tower end metal`, tower shaft. **Correction:** explicitly model one clear route to each balcony, door voids or bowl cross-aisle openings, level transitions and edge protection. **Accept:** pedestrian walk-through and plan/section at z26.4/32.6/39.0. Some connections may exist out of view; this item requires route proof, not a claim all balconies are certainly inaccessible.

### V13-A06 — Tower platforms dominate the source silhouette (P1, S, high)

**Evidence:** `north.png`, `tower-access.png`, existing `platforms-corner.png`; compare tower-reference crop. Three broad empty pale plates extend much farther into the visual bowl envelope and read as a bulky stack. Source terraces are tighter, darker, populated, and merge into the seating/brick tower composition. Exact plan depths cannot be inferred from the crop alone.

**Owner:** `r13_outfield.py:tower_platforms` polygons and materials. **Correction:** fit footprint, stepping and rail silhouette jointly with lower RF bank and tower, using B4 plus A3/B6 safeguards. **Accept:** fixed north tower crop and both exterior long views; avoid fitting only the attractive field-side angle.

### V13-A07 — LF pavilion/upper-bowl junction remains an abrupt cut (P1, S/D, high)

**Evidence:** `lf-roof-rear.png`, `lf-roof-field.png`, `north.png`: upper main grandstand ends as a thin, exposed rake with occupied rows at its terminal edge, while LF tiers/roof system step away into a separate stack. Source B4 LF corner x750–1080/y320–575 reads as a resolved pavilion/terrace composition with roof volumes and facade behind it.

**Owner:** `r13_outfield.py:trim_pavilion/curved_returns`, `r3_adjacent_buildings.py:build_left_field_pavilion`, main bowl termination. **Correction:** resolve end walls, fascia, actual rear concourse, roof attachment and openings as one corner. **Accept:** B4 crop, low field view, rear pavilion view and underside. Do not add a solid wall that again deletes the required LF seating.

### V13-A08 — South frontage has decorative glazing over solid entry walls (P1, D/I, high for geometry, medium for intended entrances)

**Evidence:** `south-bridges.png` and `r3_envelope.py:_arch_bay/_build_main_facade`: arch panes sit ahead of continuous brick masses; the main visible frontage has no functional door voids. B6 facade shows differentiated entry bays and a pedestrian arrival frontage. Not every tall arch must be a door, but the model lacks a demonstrated entry route from this plaza.

**Correction:** identify source-supported actual entries, cut only those openings, link them to internal concourses. **Accept:** approach-eye view and continuous plaza-to-concourse route. Unseen doors elsewhere cannot be ruled out by these references.

### V13-A09 — Retained outfield seat floors and RF return treads need cleanup (P2, D, medium-high)

**Evidence:** `floor.json` flags 17 legacy `D2_Outfield individual seats` with floor >0.5m below or absent within2m, separate from A01. `rf-seat-treads.png` shows conspicuously irregular projecting aisle plates; `headroom.json` has 33 RF return seat points whose concrete crosses 0.15–0.26m above the placement level. These RF hits are **not overhead headroom failures**; they indicate potential embedding/overlap and need seat-footprint inspection.

**Owner:** retained `D2_Outfield` meshes and `r13_outfield.py:curved_returns` tread/half-riser construction. **Correction:** unify tread surface and instance placement; build aisle solids with clean shared edges. **Accept:** detailed stair/seat views, downward floor checks with actual seat feet and body envelope, no repeated coplanar/intersecting surfaces.

### V13-A10 — Tower architecture is simplified beyond source fidelity (P2, S, high)

**Evidence:** `north.png`, `bridge.png`, `tower-access.png`. Source B4/A3 tower has tall luminous vertically divided openings, a lighter clock surround, layered lower window/terrace relationships; model has large opaque golden rectangles, broad brick bands and a dark oversized-looking clock box. The silhouette/relative widths differ even allowing lighting variation.

**Owner:** `r3_envelope.py` tower builder, `envelope-spec.json`. **Correction:** fit vertical band heights, recesses/mullions and clock surround from all three sources after A05/A06. **Accept:** three fixed views and tower crop. No exact real-world tower dimensions are established.

### V13-A11 — Bowl tier/aisle pattern is only an approximation (P2, S, medium-high)

**Evidence:** north comparison and `R3_v4_tier_junction.png`: repeated regular portals, large bright concourse ribbons, faceted changes in row direction and generic uniform row banks differ from the source's more varied section/aisle rhythm and integrated concourse edges. Four represented seat bands do not prove correct section widths or row counts.

**Owner:** `r2_seating.py`, `r3_bowl_details.py`, `r7_concourses.py`, bowl curves. **Correction:** trace a small set of source-identifiable aisle/portal anchors and fit section boundaries; then join corner returns without doubled/missing rows. **Accept:** B4 full bowl/crops and field-side inspection. Exact row counts are unresolved at supplied resolution; do not invent a definitive numerical mismatch.

### V13-A12 — Roof and light gantries lack source construction/detail (P2, S/I, high for appearance)

**Evidence:** `north.png`, `R3_left_field_skyline.png`, `south.png`: smooth dark barrel surface and sparse triangular light frames read differently from fine roof ribs, gantry thickness and bright integrated light arrays in B4/B6. Local spans and brace load paths are only schematic.

**Owner:** `r3_envelope.py` canopy/gantries. **Correction:** fit profile, seam spacing, rear support/connection and gantry frame depth; preserve the source roof edge. **Accept:** north/south silhouettes and underside detail. No claim about actual structural load adequacy is possible without engineering information.

### V13-A13 — Boards, backs/supports and content remain approximate (P2, S, high)

**Evidence:** `R3_third_base_seats.png`, `north.png`, `bridge.png`. RF board has schematic columns, light panels and service structure rather than source truss/back-frame detail; source CF board/canopy proportions and terrace interface are not yet a close fit. Placeholder graphics differ. Model field-eye views show clear support setback; this audit does **not** reassert the old V3 board-center-inside-field defect.

**Owner:** `r3_scoreboards.py`, `r4_rf_structure.py`, CF restaurant/terrace builders. **Correction:** fit full board/frame silhouette and service supports, then graphics. **Accept:** B4 crop plus field-eye, third-base and plan clearances for screen/support/service footprints. Exact tolerances need new dedicated measurements.

### V13-A14 — CF scoreboard plaza is over-solid and under-detailed (P2, S, high)

**Evidence:** `north.png`, `R3_v4_cf_board_plan.png`, `R3_v4_north_park_entry.png`. Broad blank continuous pale deck, simple curved dark canopy and simplified building edge replace a finer differentiated terrace with dining/furniture, glazing, occupied edges and openings. Source B4 x350–920/y610–925 and A3 CF building.

**Owner:** `r3_restaurant.py`, `r12_outfield.py`, `r13_outfield.py:open_park_arcade`. **Correction:** fit the plaza/building/board ensemble without filling A01's passage. **Accept:** north plan-like view, A3 and actual park entrance.

### V13-A15 — Park layout, retaining frontage and grand-stair composition differ (P2, S, high)

**Evidence:** `north.png`, `bridge.png`, `R3_v4_north_park_entry.png`. The source has a carefully stepped sunken riverside event court, changing terrace edges, finer angled lawn boundaries and several stair/landing moments. Model collapses much of this into a continuous repetitive arched wall, broad lawn/path rectangles and schematic stairs. The source park-to-stadium arrival concept is now represented, but that is not 1:1 agreement.

**Owner:** `r3_public_realm.py`, `r11_circulation.py`, `r12_outfield.py`, `r13_outfield.py` arcade. **Correction:** fit source contours and level transitions jointly, then furniture/planting. **Accept:** B4 park crop, A3 bridge view and two pedestrian views. Perspective artwork does not determine every slope or elevation.

### V13-A16 — Continuous accessible vertical routes remain unproven (P2, I, high as limitation)

**Evidence:** visible stairs now connect several levels, but no end-to-end step-free path to each occupied bowl/platform/park/river-gallery level is demonstrated. Visible tower/bridge terminal issues worsen this. An absence of visible elevator shafts is not proof that real designs omit elevators.

**Owner:** circulation builders, hidden program still inferred. **Correction:** map a route graph for public entries, decks, tiers and riverwalk; model essential transitions and mark hidden inferred lifts/ramps honestly. **Accept:** route walkthrough with elevation and obstruction checks, while keeping architectural assumptions distinct from source evidence. This is not an egress/capacity/accessibility certification.

### V13-A17 — River edge does not resolve boat access and edge safety (P2, S/I, medium-high)

**Evidence:** `R3_v4_rf_corner_low_river.png`, `R3_v4_riverwalk_north.png`, `river-landing.png`. Tall continuous retaining walls, occasional short guard segments and floating boats have no demonstrated boarding/gangway connection. Source B4/A3 has a more articulated busy waterfront with craft close to the quay. Some moored craft need not have passenger access, and source gangways are not fully visible.

**Owner:** `r3_public_realm.py`, riverwalk/context/boat builders, `r12_outfield.py:build_river_deck`. **Correction:** choose only source-backed landing locations, connect at plausible datums, and resolve unguarded elevated pedestrian edges where present. **Accept:** low river view, quay walk and section. Model water/ground heights are conceptual, so do not present measured flood/freeboard conclusions.

### V13-A18 — River-gallery vegetation intersects its structure (P2, D, high)

**Evidence:** `R3_v4_rf_underside.png`, `R3_v4_riverwalk_north.png`: tree branches and foliage pass through slabs/soffits and rails along occupied circulation. The open gallery has a visible column/beam system, which is positive, but planting was not reconciled to its vertical envelope.

**Owner:** riverfront trees/landscape versus `r12_outfield.py:build_river_deck`. **Correction:** adjust planting species/height/positions and test against slabs and paths. **Accept:** low undercroft and walkway views with connected trunks and clear walking space.

### V13-A19 — Hall and medical building massing/facades miss source character (P2, S, high)

**Evidence:** north/A3 comparisons. Hall roof enclosure/canopy, rooftop occupation, facade bay hierarchy and warm internal depth are simplified; medical building reads as a checkerboard box, with much smaller branding and weak stepped roof/landscape articulation relative to B4/B6.

**Owner:** `r3_adjacent_buildings.py`, `r3_medical.py`, `r3_south_rail_context.py`. **Correction:** fit visible roof outlines, setbacks and mullion/bay hierarchy first, then glazing/lighting. **Accept:** B4 full context/crops and B6; source-view branding variants must remain explicit.

### V13-A20 — South urban context is massing, not 1:1 reconstruction (P2, S, high)

**Evidence:** `south.png` against B6. Numerous large vacant grey blocks, generic repeated windows and simplified box silhouettes replace varied built fabric and dense streetscape. Near proposed towers, soccer-stadium perimeter/roof, west rail landing blocks and south buildings have substantial envelope and proportion differences. Far landmark refinements do not close these foreground mismatches.

**Owner:** `r3_south_blocks.py`, `r3_soccer_context.py`, `r3_outfield_context.py`, `r3_skyline.py`, context data. **Correction:** rank visible blocks by projected size; fit silhouettes/footprints before fine windows. **Accept:** B6 full view and nearer block crops. Future-phase and real geographic context must stay separately identified.

### V13-A21 — A3 background and immediate riverbanks are incomplete (P2, S, high)

**Evidence:** `bridge.png` versus A3. The model's south horizon is nearly empty/flat, with sparse blocky riverbank buildings; artwork has continuous city fabric, distinct foreground towers, detailed terraces and strongly framed river corridor. This remains a large composition difference even if stadium geometry is corrected.

**Owner:** `r2_context.py`, `r3_outfield_context.py`, adjacent/future development and bridge approach park. **Correction:** add/fix source-visible masses and corridor detail in geographically consistent positions, not camera-facing billboard substitutions. **Accept:** fixed A3 plus overhead placement check.

### V13-A22 — Rail/road/bridge geometry and variants are unresolved (P2, S/I, high)

**Evidence:** B4/B6 source comparisons, `south-bridges.png`, `R3_southern_rail_detail.png`, `bridge.png`. Rail bed/track count, curve/catenary/detail, service streets and bridge approaches are schematic. South-source covered links and north-source links occupy different alignments; `r2_lighting.py` switches entire geometry collections. Thus one render can appear locally plausible while another represents a different physical layout.

**Owner:** `r3_south_rail_context.py`, `r2_lighting.py`, rail/context/bridge generators. **Correction:** test a common geometry fit against fixed cameras; when source conflict remains, retain explicitly named alternative scenarios. **Accept:** all three source views and overhead route map of each alternative. Do not move railways independently to satisfy each image while claiming a single resolved stadium.

### V13-A23 — Lighting/material scale prevents visual equivalence (P3, S, high)

**Evidence:** all comparisons: B4 plazas/facades glow; current north public realm is much darker while bowl is harshly lit. B6 source has warm complex sunlight/reflection; current is flat/cool and uniformly gridded. River/water/vegetation and repeated stylized spectators further separate the images.

**Owner:** `r2_lighting.py`, material/palette/window/crowd builders. **Correction:** only after geometry, tune exposure, area illumination, facade depth/material roughness and varied occupancy. **Accept:** all three views without using light to hide unsupported or disconnected geometry.

## Items inspected but not closed by available evidence

- **Field/infield:** diamond, mound, foul poles, chalk, warning-track and boundary are present and broadly consistent in aerials. Exact outfield depths, track widths and regulation compliance were not re-certified. No new definitive field-polygon intrusion is alleged. Turf/soil tones and source activity remain approximate.
- **Dugouts:** generated as a dark solid box plus bench/roof, rather than a resolved occupiable recess (`r3_bowl_details.py:40–52`). Source detail is too small to establish interior geometry; treat functional dugout volume/entry as an unresolved model requirement, not a proven source dimensional error.
- **Bullpens:** no confidently identifiable complete bullpen configuration was established in the supplied images or model survey. Do not invent location/capacity or assert a source mismatch without clearer evidence.
- **Bowl rakers/columns:** new returns have visible supports, but whole-building load paths, foundations, lateral system, spans, vibration and strength are not validated. A connected pole does not establish adequate engineering.
- **Main concourses/hidden rooms:** some portals/cross-aisles exist; room layouts, toilet/concession/service access, egress capacity, accessible routes and emergency access are unobservable/incomplete. Report as unresolved rather than declaring the entire stadium unusable from exterior images.
- **Site registration/lake:** coarse river/rail/stadium orientation and lake's eastward placement are represented. `scene-spec.json` still labels initial V2 calibration; `skyline-buildings.json` explains the separately applied +33m registration. Fresh overheads were inspected, but no new survey/GIS check was undertaken. Landmark bearings/scale exactness and source future tower locations need a distinct geographic fit pass; do not fix appearance by arbitrarily relocating real landmarks.
- **Source contradictions:** roof/covered-link geometry inferred from a single source plane can fit one image and fail elsewhere. If literal artwork matching would create a disconnected structure, preserve the visual target as evidence and model a plausible clearly-labeled inference; do not claim the source supplies missing engineering.

## Probe interpretation and reproducibility

The scripts test active point-based seat instances whose scale vector has nonzero length; zeroed removed seats are excluded. Seat points are transformed to world coordinates. The 33,805 tested points are a geometric survey count, not a validated capacity or rendered audience count. Occupancy/visibility and instance transforms should be rechecked when implementing repairs.

`headroom.py`: upward ray starts placement z+0.15m and travels1.70m. Static polygonal building meshes near stadium are batched into a BVH; source prototypes, people, players, trees, lamps, rails and other named decorative objects are excluded. Hidden-render meshes and hidden collections are excluded. Results: 30 west-lantern hits, 1 tower cornice hit, 33 RF-return low concrete intersections. No person height or legal clearance threshold is being certified.

`floor.py`: downward ray starts placement z+0.05m, travels2m; reports no hit or first hit more than0.5m below origin. Results: 932 left-center-bank points (788 with no floor within2m, 144 first reaching lower RF podium concrete), plus17 retained outfield points (9 no floor within2m, 8 lower podium). Example left-center index30 at (46.4624,119.4907,21.5880) has no floor within2m. These are diagnostic counts with excluded-geometry limitations, corroborated by actual hanging-seat renders. They do not substitute for checking full foot/body envelopes or connected load paths. Mesh modifiers/instances are not globally boolean-unioned; geometry with nontrivial unapplied deformation would require a separate evaluated-mesh pass.

## Repair order

1. A01 retained-bank floors/soffit and A02 roof supports; preserve the passage and reference seating.
2. A03 lantern/headroom, A04 rail-link arrivals, A05 balcony routes, A08 actual entrances; include full active-seat and route checks, not only newly generated components.
3. A06/A07 tower/RF and LF corner silhouette/connection fit against all three source cameras.
4. A09/A11 bowl/aisle cleanup, then boards, CF plaza and park levels (A13–A16).
5. River edges/planting (A17/A18), adjacent buildings and city/transport context (A19–A22).
6. Tower/envelope detail and lighting/material/activity polish (A10/A12/A23).

Every repair should have a fixed-camera before/after and at least one view that could reveal the defect (underside, section or pedestrian view). Passing tests, object counts, a favorable aerial and prior completion labels are insufficient acceptance.
