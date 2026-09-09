# V15 geography audit

Prepared 2026-09-08 for the bounded geography pass. This document records source-backed findings for the river, riverfront buildings, southern bridges and skyline registration. It does not claim that the conceptual stadium or its inferred elevations are survey accurate.

## Findings

| Priority | Finding | Evidence | Required resolution |
| --- | --- | --- | --- |
| P0 | The modeled river is straight and cannot represent the mapped bend. | `railyards-v4/build_blockout.py:59-61` builds one 63 m-wide rectangle from y=-1050 to 1250 with fixed banks x=128/191. The Hydro and OSM control data in [`reference-audit/v15/river-control-points.json`](../reference-audit/v15/river-control-points.json) move the centerline from x≈173 at y=-504, through x≈155 at Roosevelt, to x≈-110 at the Willis latitude. | Replace the staging slab with a registered river polygon or segmented bank mesh. Keep the river water datum at z=0 and connect quays, park levels and bridges to the resulting banks. |
| P1 | Willis is on the wrong side of the straight river at its actual latitude; this is a geography defect, not a camera-framing defect. | `skyline-buildings.json` places Willis at raw local x=19, y=1574.2; `r3_skyline.py` applies `r4_geo.register()` so the scene x is about 52. The Hydro/OSM river center at y≈1574 is x≈-110, with east bank still west of Willis. The fixed x=128..191 river therefore puts Willis west of the river in the current scene. | Preserve Willis geographic XY. After curving the river, verify a north/skyline camera against the map. Do not move Willis or hide it to compensate for the old channel. |
| P1 | The Union Station Powerhouse footprint is geospatially plausible; its missing appearance is an overlay/camera ownership issue until proven otherwise. | `build_riverfront_v13.py:116-145` uses OSM way 155559109, footprint approximately x=78.4..108.6, y=433.9..469.7, with inferred top z=54. Hydro banks in that reach are approximately x=110..174, placing the footprint immediately west of the water. | Render the AECOM bridge camera with the R13 collection enabled and the curved river. Compare the building's lower-right source silhouette before changing its footprint. Treat 23.8 m body height and 54 m stacks as inferred visual dimensions. |
| P1 | St. Charles is not demonstrably on the wrong bank. | OSM ways 56179928/56179943 and `bridge-spec.json` place the east-west span at y=-393, x=136..207. The projected centerline is x≈171.3; Hydro banks there are x≈140..201. `build_riverfront_v13.py:151-170` uses the east pivot x_end-5≈202, which is consistent with the east bank. LOC's [HAER record](https://www.loc.gov/item/il0837/) documents the bridge and its eastern bearing/locking-mechanism orientation; the [Chicago landmark record](https://webapps1.chicago.gov/landmarksweb/web/landmarkdetails.htm?lanId=13146) places it north of 16th Street, east of Lumber Street. | Resolve the river banks first, then inspect the raised-leaf mechanism in a source-calibrated south/bridge view. Reconcile the duplicate `r3_bridges.py` closed secondary and R13 raised secondary owners before final export. |
| P1 | The baseline conflates the two parallel bridges into one raised pose. | `work/v15/baseline.blend` contains `R13_Rail bascules` with both registered spans combined; `build_riverfront_v13.py:151-180` raises both the B&OCT span at y=-374 and St. Charles at y=-393. LOC [HAER IL-67](https://www.loc.gov/item/il0633/) captions 2 and 5-7 identify the adjacent St. Charles bridge and the raised B&O span, hinge and counterweight separately. | `r15_landmarks.py` removes the combined R13 collection and rebuilds the source-led pair as one raised B&OCT primary and one closed St. Charles secondary. Preserve the east-bank hinge priors x≈193 and x≈202; treat the exact operating pose as source-scoped. |
| P1 | Generic context footprints need an explicit water-intersection check after the river replacement. | Existing context is built by multiple owners (`build_blockout.py`, `r3_context.py`, `r4_geography.py`, `build_riverfront_v13.py`). A straight water rectangle can conceal a building-water overlap or make a valid west-bank footprint appear submerged. | On the geographic plan, show the river polygon, every near-bank footprint, bridge spans and quays. Fail the audit if any solid building footprint intersects water except for documented piers, bridge decks or waterfront walls. |
| P1 | The registration authority is duplicated in metadata. | `r4_geo.py:1-17` declares +33 m as the one scene shift, and `r4_geo.py:42-50` applies it in `local_xy()`/`register()`. `scene-spec.json` still records the Roosevelt river anchor as x=126.77 while the scene slab is centered x=159.5 and the projected OSM point is x≈154.7. | Keep one registration table with raw projection, shift and residuals. Update dependent metadata only after the scene anchor is deliberately chosen; never add a second corrective constant in a consumer. |

## Control geometry

The companion JSON stores the transformed centerline and Hydro bank scanlines. The downloaded source geometry is preserved in [`reference-audit/v15/chicago-hydro-south-branch.geojson`](../reference-audit/v15/chicago-hydro-south-branch.geojson): 44 WGS84 `MultiPolygon` features selected by `properties.name == "SOUTH BRANCH CHICAGO RIVER"`, with no simplification or reprojection. It intentionally keeps the audit controls separate from the source vertex dump. The bank polygon is the shape authority; OSM centerline points are a cross-check for the bend and bridge relation. The scanlines are approximate intersections of the transformed polygon with constant-y lines and inherit source geometry and registration residuals.

The most useful acceptance anchors are:

- St. Charles reach: centerline x≈171.3 at y=-393; banks x≈140..201.
- Roosevelt reach: centerline x≈154.7 at y≈306; banks near x≈128..180 around y=300.
- Powerhouse reach: west-bank edge moves to about x≈110 by y=434..470; the OSM footprint remains west of it.
- Willis latitude: river centerline is about x≈-110 at y≈1574; Willis scene x≈52 should therefore be east of the river.

## Acceptance checks

1. Build a top-down geographic map with north arrow, river polygon, curved banks, Roosevelt, both southern bridge spans, powerhouse footprint, Willis and lake shoreline. Label the registration transform and source/inference boundary.
2. Render the fixed bridge, north, south and skyline cameras from the saved scene after rebuilding. The river edge, separated B&OCT/St. Charles bridge poses and powerhouse must agree in all views; stale HTML overlays do not count as evidence.
3. Run a footprint intersection report for water, buildings, quays, bridge decks and documented piers. Report any overlap with object name and local coordinates.
4. Verify the shared tangent projection and +33 m registration once against the recorded Roosevelt/Canal anchors. Keep the river file's `local_xy_m` values in scene coordinates without another shift.
5. Keep `railyards-v3/` unchanged and preserve source/current comparison frames. Remaining inferred bank widths, vertical datums, powerhouse height and bridge mechanism dimensions must be labelled in the next handoff.

## Source register

- [City of Chicago Hydro dataset](https://catalog.data.gov/dataset/hydro) and [GeoJSON export](https://data.cityofchicago.org/api/v3/views/knfe-65pw/query.geojson?accessType=DOWNLOAD), accessed 2026-09-08.
- [OpenStreetMap Overpass waterway query](https://overpass-api.de/api/interpreter?data=%5Bout:json%5D%3Bway%5Bwaterway%5D%2841.855%2C-87.645%2C41.881%2C-87.63%29%3Bout%20geom%3B), accessed 2026-09-08.
- [Library of Congress HAER St. Charles Air Line Bridge](https://www.loc.gov/item/il0837/), [HAER B&OCT bridge](https://www.loc.gov/item/il0633/) and [City of Chicago landmark record](https://webapps1.chicago.gov/landmarksweb/web/landmarkdetails.htm?lanId=13146), accessed 2026-09-08.
