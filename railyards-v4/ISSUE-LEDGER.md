# V4 issue ledger

Before/after evidence for the V4 priorities in `docs/FABLE-5.1-HANDOFF.md`. All "before" images are pipeline-identical control renders of the unchanged V3 generators rebuilt as V4 (`review/control-*.png`, `review/control-interior/`), plus the delivered V3 renders in `baseline-v3/`. All "after" images come from the saved `railyards-v4.blend`. Cameras are identical between before and after.

Status codes: **resolved** (visible problem gone in every relevant view), **improved / uncertain** (better, with stated remaining doubt), **deferred** (deliberately not changed).

## P0-1 Right-field scoreboard inside the field polygon — resolved

| Evidence | Before | After |
| --- | --- | --- |
| Labelled plan | V3 anchor `[96.87, 25.39, 38]` is 5.2 m inside the playable polygon | `review/rf-plan.svg`, `review/rf-plan-evidence.json` |
| Orthographic plan render | `review/control-rf_plan_ortho.png` | `review/v4-rf_plan_ortho.png` |
| Section through board / bleachers / podium / riverwalk | `review/control-rf_section.png` | `review/v4-rf_section.png` |
| Field-eye, third-base, upper-deck | `baseline-v3/interior-*.png`, `review/control-interior/` | `interior-home_plate.png`, `interior-third_base_seats.png`, `interior-home_upper_deck.png` |
| Three exterior source comparisons | `baseline-v3/final-*.png` | `final-north.png`, `final-south.png`, `final-bridge.png` |
| Source-image overlays | — | `review/rf-overlay-north.png`, `review/rf-overlay-south.png`, `review/rf-overlay-bridge.png` (playable polygon green, board frame black/white, pylon bases red, V3 anchor orange, burned into crops of the three artworks with `world_to_camera_view`); full-frame HTML version `review/rf-source-overlays.html` |

What was wrong: the V3 anchor was a single-height back-projection. Triangulating the board top-centre from three calibrated fits (north pixel 279,514 of 1944×1294; the south and bridge control pixels) gives `[101.7, 36.9, 37.8]` with 0.4 / 2.0 / 2.1 m ray misses, i.e. the board face sits on the outfield wall line, 13.5 m further north than V3 assumed. The north-image corner rays also indicate a board nearer 36×18.5 m than 39×20 m and a slight cant toward home.

What changed (`scene-spec.json` → `rf_scoreboard`, `r3_scoreboards.py`, `r3_outfield.py`): anchor `[106.0, 37.0, 37.8]`, angle 92°, 36×18.5 m, bottom z19.3, two lattice pylons at ±0.30 W landing on the podium ring (z13.4) behind the wall, service platform and light banks retained. The board sits 4.3 m east of the triangulated centre so that the whole frame, service platform and both pylon footprints clear the wall; the first V4 pass (x 104.6) left the north pylon 0.5–0.9 m inside at the wall bend and was corrected. Clearance figures are in `review/rf-plan-evidence.json` (`all_outside_playable` must be `true`). The warning track is inset inside the traced boundary (`r3_field.py`), so anything outside the polygon clears it by construction. The RF bleacher gap was recomputed from path lengths (board span y 18.5–55.5 plus 1.5 m).

Calibration check: `saved-scene-verification.json` `rf_scoreboard_top` control error fell from 31.9 px to 16.1 px in the south fit (5000 px image) and rose from 5.7 px to 12.8 px in the bridge fit (1440 px image); the V3 value was low in the bridge fit because the old anchor sat on that camera's ray at the wrong depth. Final clearance: every board, service-platform and pylon corner is outside the playable polygon, minimum 0.39 m at the north pylon's field-side corner, 2.2–6.2 m elsewhere. Regulation infield dimensions are untouched; outfield distances remain artwork-derived (RF pole 100 m).

Residual uncertainty: ±4 m along the wall from the camera fits; the board size is inferred from corner rays.

## P0-2 Unsupported right-field / clock-tower end — resolved

| Evidence | Before | After |
| --- | --- | --- |
| Low exterior (east bank) | `review/control-rf_corner_exterior.png` | `review/v4-rf_corner_exterior.png` |
| Riverwalk level toward tower | `review/control-rf_corner_low_river.png` | `review/v4-rf_corner_low_river.png` |
| Close-up beneath bleachers | `review/control-rf_underside.png` | `review/v4-rf_underside.png` |
| Section | `review/control-rf_section.png` | `review/v4-rf_section.png` |
| Tower junction (south-east, compare the south source crop) | — | `review/v4-rf_tower_junction.png` |

Diagnosis: the field is a z12 plane, the outfield terraces started at z13.5, and `r3_public_realm.py` cut the ground to z4.83 for all of x 6–124 / y −135–310, so the bowl's first-base end face, the outfield banks, the tower base (z8) and the river arcade all hovered 3–8 m above the riverwalk pit. The bowl end line (75.2,−20.9)→(60.5,−105.7) had no end wall at all; dark facade materials made the hole read as shadow in aerial views.

What changed: `r4_rf_structure.py` adds one podium footprint (bowl end line → 10 m outfield ring → LF end line → traced `bowl_back`) from z4.95 to z11.9, a ring step to z13.4 under the banks and the two corner terraces with coping and railings, a river-facing brick arcade on the exposed podium faces, a brick end wall on the RF termination standing on the z8 ground (no lip over the podium edge) whose top follows the four tier heights (stone plinth, pilasters, arched openings at concourse levels), a two-storey link block closing the 4–8 m gap to the clock-tower base, and a column line beneath the RF bank. `r3_public_realm.py` now cuts only the riverwalk strip (x 100–124, y −79–310) to the lower level; the stadium, tower and arcade land sit on the z8 datum. `r3_outfield.py` terraces end at 9.4 m so nothing overhangs the lower riverwalk (quay slab starts at x 112; festoons at x 116 and quay tables at x 115 are unaffected).

Datums: ground 8, lower riverwalk 4.95, podium ring 13.4, field 12. This is inferred understructure, not an engineering design.

Residual: the LF end of the bowl was given the podium but not an end wall (it meets the LF pavilion, outside the identified area).

## P0-3 Lake Michigan absent, terrain across the lake — resolved

| Evidence | Before | After |
| --- | --- | --- |
| Orthographic geographic map (5.2 km, +Y north) | `review/control-geo_map.png` | `review/v4-geo_map.png` |
| Elevated east camera | `review/control-east_lake_high.png`, `review/control-east_lake.png` | `review/v4-east_lake_high.png`, `review/v4-east_lake.png` |
| South source comparison (lake at top right in the AECOM image) | `baseline-v3/final-south.png` | `final-south.png` |

Source: the City of Chicago ArcGIS Lake Michigan layer (Basemap_BlackWhite/22) returned HTTP 503 "wait timeout" on every attempt on 2026-09-06 (full query, envelope query, single-object query). The shoreline was taken instead from the USGS National Hydrography Dataset (`hydro.nationalmap.gov …/nhd/MapServer/12`, GNIS "Lake Michigan", FType 390, requested in WGS84) and cross-checked against the City of Chicago data-portal Hydro export (dataset knfe-65pw, feature "LAKE MICHIGAN"): shoreline x agrees within ~10 m at y = 0, 300 and 1000. Stored as `lake-michigan-local.json`.

Registration: one audit, recorded in `r4_geo.py`. The 14 legacy landmarks used the raw tangent-plane formula; site/outfield context, roads and the modelled river carry the +33 m X adjustment. Formula + 33 m matches the river centre within 4.8 m and Canal Street within 1 m, so V4 applies +33 m exactly once (`r4_geo.local_xy` / `register`) for the lake, the near-South-Loop context, the new silhouettes and, now, the legacy landmarks (`r3_skyline.py` shift). Shoreline at the stadium latitude: x ≈ 1915 (mainland), Northerly Island 2173–2388; Grant Park shore x ≈ 1650 at y 1000.

Datum: lake surface z0.5 (river held slightly below lake), not the field's +12.

Field-level visibility: from the seats the lake is behind the near-South-Loop blocks and the Museum Campus; only the elevated east cameras (z60 / z140) see water, as expected for a site 1.9 km inland. The V4 renders do not force a lake view from any seat.

Residual: Grant Park / Museum Campus lawns and the four museum masses are inferred approximations; no terrain grading.

## P1 Recognizable skyline by sightline — improved

| Evidence | Before | After |
| --- | --- | --- |
| Third-base (RF/RCF window) | `baseline-v3/interior-third_base_seats.png` | `interior-third_base_seats.png` |
| Home upper deck | `baseline-v3/interior-home_upper_deck.png` | `interior-home_upper_deck.png` |
| LF skyline | `baseline-v3/interior-left_field_skyline.png` | `interior-left_field_skyline.png` |
| East cameras | — | `review/v4-east_lake*.png` |

Ranking (`skyline-v4-additions.json`): NEMA (273 m), One Museum Park (221 m), The Grant (181 m) and 1000M (245 m) lie at local azimuth 10–33°, 1.1–1.3 km from the bowl, and project 150–290 px tall in the third-base and upper-deck views — larger than any downtown landmark — and were absent from every V3 dataset (context stopped at x ≈ 830). 311 South Wacker, Chicago Board of Trade and Franklin Center replace generic prisms; the duplicates are excluded by name in `r3_outfield_context.py`. 238 OSM buildings with height tags/levels were fetched for the near South Loop (`near-south-loop-context.json`); 99 of them share an `osm_way` with `outfield-context.json` or `site-context.json` and are skipped (`skip_ways`), and the four dedicated silhouettes are skipped by name, so nothing is represented twice.

Residual: silhouettes are massing-level; materials are flat glass. 875 N Michigan, Marina City, Wrigley, Tribune, Salesforce, River Point and 150 N Riverside were left as modelled (under 120 px at 2.5–4 km).

## Recorded, not fixed

- CF board: three-ray triangulation puts its top at `[93.4, 140.1, 36.3]`, 14 m north of the V3 anchor `[90.0, 126.0, 36]`; the rounded restaurant hangs off that anchor, so it was left for a later pass.
- `lf_pavilion_roof` control error (111 px south) is unchanged.
- North / B6 covered-link variants remain separate collections.
- Raised Roosevelt-level plaza entering above the bleachers is preserved unchanged.

## Baseline preservation and reproducibility

`review/baseline-preservation.json` (2026-09-06): the original `/Users/joshbohne/Developer/TheRailyards/railyards-v3/` matches all 65 `delivery-manifest.json` hashes (files and images); the worktree copy matches the 50 tracked entries, with the 15 Git-ignored generated files (blend, renders, receipts) absent as expected. `railyards-v3-baseline.blend` copied into V4 is byte-identical to the original scene. No V3 file was modified.

Render passes: pass 1 (1400 px / 24 samples) exposed the north-pylon intrusion; pass 2 (1800 px / 48) rendered the corrected anchor; pass 3 (1800 px / 48) is the delivered set after grounding the end wall at z8, adding the tower-junction camera and deduplicating the OSM context. `saved-scene-verification.json`, `review/rf-plan-evidence.json` and `delivery-manifest-v4.json` were regenerated from the pass-3 scene.

## V5 — skyline accuracy, facade variety, finished tops, lakefront references

| Evidence | Before (V4) | After (V5) |
| --- | --- | --- |
| Press box panorama | `review/v4-press_box.png` | `review/v5-press_box.png` |
| Home upper deck / LF skyline / third base | `review/pass1/`, site images `v4-*` | `interior-*.png` (V5 pass) |
| South fixed comparison (Loop core in the top band) | `review/pass1/final-south.png` | `final-south.png` |
| Elevated east / west aerial | `review/v4-east_lake_high.png`, `review/v4-aerial_west.png` | `review/v5-east_lake_high.png`, `review/v5-aerial_west.png` |
| Labelled panoramas and visibility table | — | `review/skyline-panoramas.html`, `review/skyline-v5.json` |

What was wrong: every mapped building used one tan `stone` with a dark checkerboard, the V3/V4 crowns used the night-emissive `glass_lit` (0.04 emission by day, so 311's cylinder, NEMA's top and Aqua's rings read as unfinished dark caps), flat prisms had no parapets or penthouses, and Chase, CNA/333 S Wabash, Crain, BCBS, Legacy, One Chicago, Water Tower Place and the Hilton were absent while Kluczynski was a generic prism.

What changed:
- `r5_palette.py`: 16 daylight facade materials; a curated table of 50 named buildings (Kluczynski black/bronze, Old Post Office limestone per its OSM tag, Harold Washington red brick, BMO glass…) and an era/height-weighted mix for the rest (only 8 of 114 fetched ways carried OSM colour/material tags). Window glazing ratio varies per building. Every flat prism gets a parapet and, above 18 m, a mechanical penthouse; above 90 m a rooftop mast box.
- `r5_skyline_icons.py` (+`skyline-v5-icons.json`): Chase Tower (curved sweep), 333 South Wabash painted red, Kluczynski, Crain (slanted split top), BCBS, Legacy, One Chicago (both towers), Water Tower Place, Hilton Chicago. OSM footprints where Nominatim returned polygons; Wikipedia heights. Kluczynski removed from the generic set.
- Crowns re-materialled: 311 South Wacker white cylinder crown, St. Regis / Aqua / Two Prudential white bands and blue glass, Aon white marble, Trump blue glass, Franklin Center pink granite, CBOT limestone with copper pyramid, NEMA grey glass, 1000M light glass.
- `r5_lakefront.py` (+`lakefront-v5.json`): Soldier Field (OSM colonnade footprint, columns, glass bowl inside), Field Museum (marble mass, raised hall, columns), Shedd (octagon, green dome), Adler (dome), Wintrust Arena, McCormick Lakeside (inferred box). Heights inferred and labelled.
- Crowd: five walker clothing variants replace the single grey figure (`r2_landscape.py`, `r3_public_realm.py`).

Visibility (ray test from each camera to each landmark roof, stopping 70 m short of the target): upper deck sees 15 landmarks unobstructed (St. Regis, Aqua, Aon, Two Prudential, Trump, NEMA, One Museum Park, The Grant, 1000M, CBOT, Chase, 333 S Wabash, Kluczynski, Legacy, One Chicago); LF skyline adds Willis, 311, Franklin Center, Salesforce, 150 N Riverside; third base sees the Museum Park cluster and the Field Museum; the south fixed camera sees 11. Hancock, Tribune, Wrigley, Marina City, Crain, BCBS and Water Tower Place are in frame but behind nearer towers from the bowl, as they are in reality.

Residual: silhouettes are massing-level (no window textures on the dedicated towers beyond strip glazing); lakefront heights inferred; buildings west of the river and the Loop core beyond the mapped extent are still absent.

## V6 — left-field end and the centre-field board check

**Left-field end — resolved (inferred).** The north aerial shows the upper decks ending against a brick gatehouse with a tall arch toward the park, the pavilion in front of it. V3–V5 ran the envelope's dark louver band over that corner. `r6_lf_end.py` adds a tier-profile brick end wall on the LF termination line (front[-1] → back[-1]) capped to the envelope's junction slope, and a gatehouse block between the bowl end and the pavilion footprint rising to the fascia top (47.6) with an arch above the pavilion roof on its park face; `r3_envelope._fascia_bay` builds brick with stone belts instead of louvers for bays with y > 100, x < 20. Evidence: `review/v6-lf_gatehouse.png`, `review/v6-lf_corner_exterior.png` (the dark glazed box in front is the pavilion itself, as in the artwork), `final-north.png`.

**Centre-field board — checked, anchor retained.** A north-pixel trace (695,567 of 1944×1294) was added to the two-camera result recorded in V4. The three pairings disagree: south+bridge `[93.4,140.1]`, north+south `[81.2,127.7]`, north+bridge `[78.1,126.5]`; the three-ray solution `[83.0,128.2,40.7]` misses the rays by 6–11 m. The V3 anchor `[90.0,126.0,36.0]` lies inside that spread, and the restaurant footprint is traced independently from north pixels, so nothing was moved. Recorded in `scene-spec.json` → `cf_scoreboard_triangulation`. From behind the plate (`review/v5-cf_from_home.png`) the board sits on the restaurant/batter's-eye block with the terrace seats in front, matching the north crop.

## V7 — concourses and the night pass

**Concourses — resolved (inferred).** Between each pair of tiers V3 had a flat glass ribbon (`R2_Tier N concourse glass`) with flat "entry" boxes on it and no walkway. `r7_concourses.py` builds, at each of the three concourse levels: a walkway slab, a 0.9 m front wall with a rail, a segmented back wall (precast base, suite/club glazing above, alternating lit and dark bays), a 4.8 m vomitory opening every ~19 m with a dark tunnel recessed 5 m behind the wall line and a lit soffit, and lamp strips under the next tier's overhang. The V3 ribbons are hidden and the old entry boxes removed. Evidence: `review/v7-tier_junction.png` vs `review/v7day-tier_junction.png` (before, first pass of this session), `review/v7-upper_concourse.png`.

**Night pass — resolved (render interpretation).** The dusk preset fitted to the north aerial now also drives the interior and review cameras (`RAILYARDS_PRESET=north`, `night-*` outputs). `r2_lighting.py` toggles, at night only: board screens glow faintly (so the graphics keep contrast), the white crowns (311 South Wacker, St. Regis bands, Aqua rings) emit warm light, and ordinary glazing materials get a faint interior glow so the Loop reads instead of going black. Evidence: `night-*.png` interiors and `review/night-*.png`. First attempt over-lit the boards (`review/v7night-press_box.png`); emission was cut from 0.35 to 0.16.

Residual: window lighting is uniform per material (no per-window variation at night); the sky is the preset's flat gradient; canopy underside stays dark.

### Tool split (V7 onward)

- **Blender CLI** for the reproducible chain and batch renders (`build_*.py`, `render_*.py`, `run_v4_renders.sh`).
- **Blender MCP** for live inspection and edits. The `blender-mcp` server is registered in `/Users/joshbohne/Developer/TheRailyards/.mcp.json` (`uvx blender-mcp`) for future sessions; in this session it was not loaded, so the add-on socket was driven directly with `tools/blender_mcp_client.py` (same JSON protocol: `get_scene_info`, `execute_code`, `get_viewport_screenshot`). A second Blender GUI instance was started on the V7 scene with the add-on on port 9877 (`tools/start_live_mcp.py`) because the existing instance on 9876 holds unsaved Codex work on the V3 file and was left alone. Live checks: concourse objects and vertex counts, 39 vomitory openings, tunnel z-range 24.0–38.8 m below the next tiers' first rows (27/33/39), viewport set to the tier-junction camera and captured offscreen: `review/live-viewport-tier_junction.png`.
- **Computer use** for UI review: the granted Blender window reachable to the computer-use tools was the Codex instance on another Space (V3 file), so UI screenshots of the V7 instance were not possible this session; the add-on's offscreen viewport capture stands in.

## V12 — stadium proportions (2026-09-07)

Brief: `../docs/FABLE-5.1-V12-HANDOFF.md`; decisive reference `../reconstruction-references/v12-user-north-transition.png`. All "before" images are the saved V11 scene rendered through the V12 acceptance cameras (`review/v12/before/v11-*.png`); all "after" images are the saved `railyards-v12-static.blend` (`review/v12/v12-*.png`). Cameras are identical. Numbers come from `review/v12/{v11,v12}-geometry.json` (ray probes in the built scenes).

| Item | Before (V11) | After (V12) | Evidence |
| --- | --- | --- | --- |
| Third-base line to seats/dugout, y 40 | 3.2 m | 10.1 m (first base 10.1 m) | `D1_third_base_line`, `D2_dugouts_from_upper`, `D3_home_to_3b` |
| Third-base line to seats, y 20 / 60 / 80 | nothing hit within 40 m at field level (no wall) | 12.6 / 12.6 / 8.2 m | `v12-geometry.json` |
| Backstop, home plate to wall | no wall hit (trace was 5.7 m) | 17.7 m | `D4_backstop`, `P1_plan_stadium` |
| Left-center plaza to bleachers | plaza z 22 over bleachers topping at z 17; one 4 m stair | 18-row bank from the wall to a cross-aisle flush with the plaza; first aisle max step 1.38 m (the field wall), no gaps | `N1`–`N5`, `S1_section_left_center`, `H_entrance_from_field` |
| Right-field corner | railing terrace at z 13.4, board on lattice legs | 12-row corner bank on a brick block with arcades; brick board house | `R1`–`R5`, `S2_section_rf_corner` |
| Tower flag | pole at x 90.7 (shaft face 89.0), z 56–72, flags below the roof | mast on the roof cap, flags above the roof | `F1_flag_close`, `F2_tower_context` |
| Field-edge wall | void z 12–13.1 under the first row | padded wall | `D1`, `D3` |
| Arrival route probes | 163 samples, no gap | 163 samples, no gap | `v12-geometry.json` |

Status: **resolved** for the dugout/foul-line clearance, the backstop, the flag mounting and the field-edge void; **improved / inferred** for the left-center bank and right-field corner (the artwork establishes the relationships, not the dimensions). Deliberately unchanged: the traced `bowl_back`, outfield wall, board anchors, geographic registration and camera calibration.

Generator owners: `tools/correct_bowl_front_v12.py` (spec), `r3_bowl_details.py` (dugouts, front wall, flag), `r3_outfield.py` (terrace ranges), `r3_scoreboards.py` (board house), `r4_rf_structure.py` (corner rail removed), `r12_outfield.py` (banks), `build_circulation_v12.py` (stage), `verify_v12.py` (probes and cameras).

Residual: the lower outfield concourse behind the right-field terraces is still a covered corridor (`E_outfield_concourse`); the left-center bank's lowest row is clipped by the wall for about 1 m where the plaza edge is closest to the wall; crowd figures and materials remain schematic. The seat export grew from 26,950 to 29,566, so V11 `seat=N` share links select different seats.
