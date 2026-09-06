# Fable 5.1 handoff — The Railyards V4

Prepared 2026-09-06 for Josh. Project root on this Mac: `/Users/joshbohne/Developer/TheRailyards`.

## Objective

Improve the existing V3 reconstruction into a convincing stadium and recognizable Chicago setting. Josh likes the V3 foundation but identifies unsupported-looking right-field geometry near the clock tower, a right-field scoreboard that appears to sit on the field, insufficient attention to important skyline buildings, and uncertain Lake Michigan placement. Start with these spatial and architectural issues. Keep the raised plaza that meets Roosevelt and enters above the bleachers as an important design feature.

V3 is an extensive conceptual model, not a fidelity-complete architectural reconstruction. Earlier statements that all 28 inventory groups were covered mean components were represented; they do not establish correct geometry, supports, visibility or geography. In particular, the scoreboard and lake defects below survived the prior review. Treat the current renders critically.

## First session

1. Read this document and open the V3 gallery plus `interior-home_plate.png`, `interior-home_upper_deck.png`, `interior-third_base_seats.png` and `final-south.png`. Reopen the actual `.blend`. Identify the right-field/tower edge in 3D rather than guessing from the words “right field.”
2. Check Git status; create a feature branch and a `railyards-v4/` copy. Preserve V3. Adapt the copied build/finalize/render entrypoints from `Railyards v3` and `railyards-v3*.blend` to V4 before running them. Keep the shared reference folders adjacent. The legacy R2/D2 prefixes are still used by code.
3. Produce an annotated plan and a section through the RF board, boundary, seating and tower end. Show dimensions and object names. Establish the geographic frame and lake shoreline before selecting additional landmarks.
4. Fix the priority issues below in bounded passes. For each, save a before/after from the same camera, describe observed versus inferred details, and preserve improvements in the generator.

## P0 — Right-field scoreboard is inside the current field polygon

**Verified from the current source, not just an impression:** `scene-spec.json` has `rf_scoreboard_top = [96.869615, 25.394204, 38]`. Treating the field as home plate `[0,0]` plus the ordered `field_boundary`, the board center's XY lies inside that polygon. Its closest boundary point is approximately `[102.059660, 24.966033]`, 5.207677 m away. Its center is about 100.143 m from home. This is a horizontal centerline check; the full screen, service platform and support footprint require their own clearance checks.

`r3_scoreboards.py` builds RF width 39 m, height 20 m, angle pi/2, with its bottom at z18. The field datum is z12, so the screen bottom is roughly 6 m above the playing surface. It adds support boxes starting at z13 and a service platform. The board's apparent size is also affected by camera perspective, but the centerline intrusion is a geometry inconsistency regardless of lens.

**Work:** reconcile the board, field boundary, warning track, foul pole, bleacher gaps and river-side space against all three AECOM views and the site plan. Determine whether the board anchor, field tracing, or both need correction. Fit the entire board footprint and support system, not only its top-center pixel. Avoid prescribing an arbitrary backwards shift as the final answer.

**Accept when:** a labeled plan proves every board/support/service-platform footprint is outside the playable area and warning-track clearance is documented; field-eye, third-base and upper-deck renders show a coherent setback; all three exterior comparisons remain credible. Keep the regulation infield dimensions intact. Report inferred outfield dimensions honestly.

## P0 — Unsupported right-field / clock-tower end

**Observed concern:** Josh sees seating or platform edges near the tower apparently held up by nothing. V3 has many slabs, seats and facade surfaces, but this does not guarantee connected understructure. Diagnose which deck termination and undercroft he is seeing. Check whether dark facade materials, one-sided surfaces or hidden collections compound the gap.

**Owners:** `build_blockout.py` (tier shells and foundational masses), `r2_seating.py`, `r3_bowl_details.py`, `r3_outfield.py`, `r3_envelope.py`, `r3_scoreboards.py`. Geometry is batched by collection/material, so a single object can contain many disconnected pieces.

**Work:** inspect underside views and sections; connect visible deck ends to plausible columns, beams/rakers, walls or podiums. Address slab thickness, landings and tower-to-bowl junctions. Resolve the ground/field/river datums before stretching posts to an arbitrary height. Hidden structural design is inferred, not an engineering certification.

**Accept when:** a close-up, section and low exterior view all show continuous support to a stated ground/podium datum; no floating slab ends remain in the identified area; supports respect circulation and riverwalk space. Aerial beauty renders alone do not close this issue.

## P0 — Lake Michigan is absent and terrain extends across it

**Verified source defect:** the current generator closure contains a river channel but no lake or shoreline builder. `r2_context.py` creates background terrain at center `(10500,0,3)` with dimensions `(19000,40000,10)`, covering X=1000 through 20000. In the declared X-east coordinate frame this fills a large area eastward with paving. A flat horizon in the renders is not evidence of correctly placed lake water.

**Work:** obtain the real shoreline, project it into the shared geographic frame and clip the land to it. Include the relevant Grant Park/Museum Campus/lakefront landforms at appropriate detail. Keep river and lake distinct. Check the water datum rather than copying the field's inferred +12 m height. Record the projection and registration adjustment in one place and use it consistently for terrain, roads and buildings.

**Starting authoritative source:** [City of Chicago Lake Michigan polygon layer](https://gisapps.chicago.gov/arcgis/rest/services/ExternalApps/Basemap_BlackWhite/MapServer/22). Its REST metadata identifies polygon geometry and supports JSON/GeoJSON queries. Request transformed WGS84 geometry (outSR=4326) or explicitly transform its EPSG:3435 coordinates; raw State Plane values are not local Blender metres. Accessed 2026-09-06; geometry has not yet been downloaded or incorporated.

Current frame in `scene-spec.json`: X east, Y north, Z up; latitude 41.8645, longitude -87.6362; river z0, ground z8 and field z12 are conceptual datums. `skyline-buildings.json` also records a roughly +33 m X registration adjustment. Audit this once; avoid applying it twice. Verify the actual coordinate transform against mapped Roosevelt/Canal/river anchors.

**Accept when:** an orthographic geographic map shows north, shoreline, stadium, river and selected landmarks in consistent coordinates; an east-facing elevated camera shows the lake beyond actual land; field-level visibility/occlusion is explained. Do not force a lake view from a seat that cannot physically see it. Terrain must not continue over the lake.

## P1 — Recognizable skyline, ranked by actual sightlines

The current dedicated skyline list has 14 named buildings, while `outfield-context.json` adds 73 corridor buildings with mostly generic repeated window facades. Their presence does not prove visibility or likeness. Some buildings already exist in multiple datasets; deduplicate before adding replacements.

**Candidate ranking to investigate, not a claim that all are visible:**

| Area | Candidates | Reason to inspect |
| --- | --- | --- |
| Near South Loop / lake direction | NEMA, One Museum Park, One Museum Park West, 1000M, The Grant | Nearer tall silhouettes may dominate east/northeast views more than famous distant towers. These are not in the dedicated 14-landmark list; check other datasets before calling them absent. |
| Downtown west / northwest views | Willis Tower, 311 South Wacker, Franklin Center, Chicago Board of Trade | Strong identity and/or substantial apparent size, depending on the seat and canopy occlusion. Willis is already modeled; 311 South Wacker is currently a generic context building. |
| Downtown northeast / lake-adjacent cluster | St. Regis, Aon Center, Two Prudential Plaza, Aqua, Trump Tower | Existing dedicated models need review for silhouette, crown, relative spacing, material and actual visibility. |
| Farther / conditional | 875 N Michigan (Hancock), Marina City, Wrigley, Tribune, Salesforce, River Point, 150 N Riverside | Model fine detail only where the relevant view exposes enough pixels to matter. |

For each selected building, record geographic XY, source height, bearing and distance from the actual cameras, projected pixel height, visible fraction after occlusion, and the recognizability feature to model. Prioritize apparent size and unobstructed skyline contribution, then identity. Keep geographic placements fixed; add diagnostic cameras instead of moving buildings to make them famous in the frame.

Useful source leads: [CTBUH NEMA record](https://www.skyscrapercenter.com/building/one-grant-park/21954), [1000M architectural award/project description](https://www.chi-athenaeum.org/international-architecture-award-winners-2026/2026/07/31/1000m-chicago-illinois-usa-2024/), and [Chicago Architecture Center St. Regis](https://www.architecture.org/online-resources/buildings-of-chicago/st-regis). Existing landmark JSON includes architect/developer/official links for other towers. Research exact geometry from primary sources as needed.

**Accept when:** labeled panoramas from home upper deck, LF skyline, third-base and a new east/lake camera match the map's bearings and relative heights; priority buildings are recognizable by silhouette rather than labels; generic filler no longer overwhelms them. Explain landmarks excluded by occlusion or tiny projected size.

## P1/P2 — Further high-value improvements

- **Bowl and facade coherence:** review tier spacing, visible concourse depth, canopy thickness/ribs, arch proportions and the tower connection across all cameras. Avoid a separate favorable silhouette for each view.
- **Ground and public space:** replace large featureless paved areas with sourced street/park boundaries, grading and plausible connections. Preserve the sloping Roosevelt-level entrance above the bleachers and lower riverwalk. Inspect every bridge/landing connection in section.
- **Materials and depth:** generic checkerboard windows, uniformly bright spectators, broad flat surfaces and weak material separation make the city and bowl look synthetic. Address glazing/recess depth, material scale, crowd variation and coherent lighting after spatial corrections.
- **Field and activity:** keep base paths and mound geometry; review warning-track width, turf/clay transitions, netting, dugouts, foul poles and board graphics. Current player portrait and copy are illustrative placeholders.
- **Source conflicts:** north and B6 covered rail links are currently distinct source-view collections. Documented disagreement is preferable to hiding it, but investigate a better unified fit before accepting variants permanently. Inferred future towers should remain visibly separate from existing geography.

## Navigation and traps

- `railyards-v3/README.md`: build commands; `SOURCE-AND-ASSUMPTIONS.md`: source/uncertainty record; `ELEMENT-REVIEW.md`: component mapping; `delivery-manifest.json`: baseline hashes.
- `build_blockout.py` -> `build_detail.py` -> `add_interior_cameras.py` -> `finalize_scene.py` is the rebuild chain. `render_scene.py`, `render_interior.py`, `render_southern_rail.py` write actual renders. Blender 5.2.1 LTS was used; macOS executable is `/Applications/Blender.app/Contents/MacOS/Blender`.
- `r3_skyline.py`, `r3_outfield_context.py`, their JSON files and `r2_context.py` jointly own the city. `r2_lighting.py` selects source variants and future-context visibility; interior render presets hide inferred future development. Inspect both `hide_render` and `hide_viewport` when switching presets.
- `scene-spec.json` still labels itself an early V2 calibration. `skyline-buildings.json` embeds older interior-camera coordinates. `add_interior_cameras.py` and saved cameras are the current camera authority. The fixed third-base camera is `[-25,58,31.3]`; its prior location intersected fascia.
- Source traces may be directly in generator code. Original full-resolution images and working derivatives have different pixel sizes; use the size declared beside each trace.
- `reference-audit/` contains historical worker reports; some “remaining” issues were later fixed and some draft source traces were rejected. Validate against current generators. Do not reincorporate rejected future-tower placeholders as evidence.
- Original V1/V2 and the chat workspace remain preserved. This standalone copy carries V3 plus V2 comparison renders; no previous scene was moved or overwritten.

## Delivery bar

Deliver the editable V4 scene, reproducible generators, all three fixed-camera source comparisons, all four interior views, a support close-up/section and a geographic/lake diagram. Reopen and render the saved file, verify dependencies and baseline preservation, and report which visual issues are resolved, still uncertain or deliberately deferred. Object counts, successful renders and calibration residuals do not establish fidelity. Retain a short issue ledger with before/after evidence for every P0 issue.
