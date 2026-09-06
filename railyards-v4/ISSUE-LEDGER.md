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
| Source-image overlays | — | `review/rf-source-overlays.html` (playable polygon, board frame, pylon bases projected into the north, south and bridge fits) |

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

Diagnosis: the field is a z12 plane, the outfield terraces started at z13.5, and `r3_public_realm.py` cut the ground to z4.83 for all of x 6–124 / y −135–310, so the bowl's first-base end face, the outfield banks, the tower base (z8) and the river arcade all hovered 3–8 m above the riverwalk pit. The bowl end line (75.2,−20.9)→(60.5,−105.7) had no end wall at all; dark facade materials made the hole read as shadow in aerial views.

What changed: `r4_rf_structure.py` adds one podium footprint (bowl end line → 10 m outfield ring → LF end line → traced `bowl_back`) from z4.95 to z11.9, a ring step to z13.4 under the banks and the two corner terraces with coping and railings, a river-facing brick arcade on the exposed podium faces, a brick end wall on the RF termination whose top follows the four tier heights (stone plinth, pilasters, arched openings at concourse levels), a two-storey link block closing the 4–8 m gap to the clock-tower base, and a column line beneath the RF bank. `r3_public_realm.py` now cuts only the riverwalk strip (x 100–124, y −79–310) to the lower level; the stadium, tower and arcade land sit on the z8 datum. `r3_outfield.py` terraces end at 9.4 m so nothing overhangs the lower riverwalk (quay slab starts at x 112; festoons at x 116 and quay tables at x 115 are unaffected).

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

Ranking (`skyline-v4-additions.json`): NEMA (273 m), One Museum Park (221 m), The Grant (181 m) and 1000M (245 m) lie at local azimuth 10–33°, 1.1–1.3 km from the bowl, and project 150–290 px tall in the third-base and upper-deck views — larger than any downtown landmark — and were absent from every V3 dataset (context stopped at x ≈ 830). 311 South Wacker, Chicago Board of Trade and Franklin Center replace generic prisms; the duplicates are excluded by name in `r3_outfield_context.py`. 238 OSM buildings with height tags/levels fill the near South Loop between the district and the shore (`near-south-loop-context.json`).

Residual: silhouettes are massing-level; materials are flat glass. 875 N Michigan, Marina City, Wrigley, Tribune, Salesforce, River Point and 150 N Riverside were left as modelled (under 120 px at 2.5–4 km).

## Recorded, not fixed

- CF board: three-ray triangulation puts its top at `[93.4, 140.1, 36.3]`, 14 m north of the V3 anchor `[90.0, 126.0, 36]`; the rounded restaurant hangs off that anchor, so it was left for a later pass.
- `lf_pavilion_roof` control error (111 px south) is unchanged.
- North / B6 covered-link variants remain separate collections.
- Raised Roosevelt-level plaza entering above the bleachers is preserved unchanged.
