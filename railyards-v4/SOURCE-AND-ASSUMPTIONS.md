# Railyards v3 — sources and reconstruction limits

This is an editable reconstruction of AECOM's September 2026 White Sox Railyards concept artwork. It is not a surveyed design, an approved building plan, or a claim of an exact photographic match. Earlier v1 and v2 files remain separate.

## Primary visual evidence

The three published views are B4 (north aerial), B6 (south aerial), and A3 (Roosevelt bridge). The preferred north and bridge originals are the 5000×3333 CBS copies; the south original is also 5000×3333. The smaller north and bridge derivatives retain the image coordinates used in the original camera fit. Source polygons always state their image size; coordinates from different derivatives must not be mixed.

The [source provenance](../reference-audit/additional-sources.md), [stadium inventory](../reference-audit/stadium-inventory.md), and [immediate-area inventory](../reference-audit/immediate-area.md) retain publication links, visible regions, and the original discrepancy audit. Those audits describe earlier passes; they are evidence inventories, not declarations that their old discrepancy descriptions remain current.

## How the geometry was recovered

The stadium uses a shared metric coordinate frame, north-traced bowl and canopy outlines, and three calibrated perspective cameras. A 90-foot baseball base square supplies a scale prior. Visible vertical building corners help constrain building heights; roof corners are back-projected to those height planes. Where a height is not constrained by a clear vertical edge, it is an inference. Back-projecting a roof outline establishes its appearance in one camera; it does not prove the hidden footprint or its height.

Four seating strata, separate outfield banks, a barrel canopy, three prominent roof floodlight gantries, two scoreboard-top light banks, the clock tower, arched stadium envelope, outfield pavilions, adjacent buildings, rail links and raised park are represented as native geometry. The field includes the base square, pitcher plate, continuous mound, clay boundaries, warning track, foul lines, poles and native players. Seat and crowd instances describe visible scale and density; their generated counts are not published venue capacity.

The Northwestern Medicine bar and wing, left-field pavilion, entertainment hall, rounded centerfield restaurant, rooftop shades and public deck retain source-pixel observations in their owning modules. Native facade panes use a small palette sampled from the north image. No source photograph is projected onto the final buildings. Fine mullions, furniture, interiors, structural member sizes, planting species and individual people are inferred representations of visible features.

## Public levels and access

Roosevelt's public road/sidewalk is the entrance datum. The park rises toward an outfield entry above the bleachers; the lower riverwalk connects beneath it, with a broad corner stair and separate lower promenade. The grade is an interpretation of the renderings and the user's supplied observation about the viaduct-level entrance. It is not an engineered accessibility or drainage design. Private covered rail bridges have their own deck elevations and do not establish the public plaza level.

## Existing city versus proposed development

Existing background footprints come from OpenStreetMap. The finite outfield corridor was expanded only to establish the buildings visible from inside the stadium; it is not an entire-city model. [Outfield context](outfield-context.json) records each footprint and height basis. River City's courtyard is open. [Skyline landmarks](skyline-buildings.json) retain identified buildings, actual geographic placement, and documented height priors, including Willis Tower. Landmarks have not been resized or hidden by camera to make the skyline look convenient.

OSM data is © OpenStreetMap contributors and available under the [Open Database License](https://www.openstreetmap.org/copyright). Tagged heights, level-derived heights and supplemental published heights are distinguished per building. Repeated facade windows on mapped context are schematic; the building footprints do not establish their facade designs.

The soccer stadium and unbuilt towers/blocks are separate future-development layers interpreted from the artwork. They should not be read as existing buildings or confirmed future plans. North, south and bridge artwork represent different visible context, so view presets control the explicitly labeled future layers. Fireworks are native event staging for the bridge artwork only.

## Verification boundary

The saved-file check verifies the native scene, camera records, finite geometry, valid instance sources, field dimensions and external asset availability. Actual renders from reopened Blender files are reviewed in the browser. These checks prove that the editable model renders and preserves its recorded construction; they do not establish whole-scene visual accuracy. The gallery's pixel residuals apply to selected frozen camera controls, not all newly built architecture.

Remaining uncertainty includes hidden building sections, exact seating counts, facade materials under daylight, construction phases, engineering details, landscaping layouts, and inconsistencies among the concept renderings. The model is a source-driven architectural interpretation, not a one-to-one digital twin.

### Covered-link source variants

The north-derived three crossing positions and the three B6 roof traces do not reconcile under the fitted cameras. `r3_south_rail_context.py` retains the refined B6 roof polygons and west-side landing blocks. `D2_Pedestrian rail bridges` is the north/bridge reading; `D2_South source rail links` and the south landing/branding collections are the B6 reading. These are documented interpretation variants, not an assertion that bridges physically move or that both sets are simultaneously proposed.

### Southern rail bridges

The far-right raised rail structure in B6 is best identified as the B&OCT bascule, immediately north of St. Charles Air Line. OSM geographic placement and Library of Congress HAER records support that identity: [B&OCT IL-67](https://www.loc.gov/item/il0633/) and [St. Charles IL-157](https://www.loc.gov/item/il0837/). The source-visible raised leaf is schematic; mechanism details and the partly off-frame second bridge remain uncertain. A separate narrow proposed public river crossing south of the stadium is represented as an artwork-derived future element.

## V4 addendum (2026-09-06)

- **Registration audit.** The tangent-plane formula in `skyline-buildings.json` omits the +33 m X site adjustment that `site-context.json`, `outfield-context.json`, `site-roads.json` and the modelled river carry. `r4_geo.py` is now the only place the adjustment lives; it is applied once to the lake, the near-South-Loop context, the V4 silhouettes and the 14 legacy landmarks. Residuals against the recorded anchors: river centre 4.8 m, Canal Street 1 m.
- **Lake Michigan.** USGS NHD large-scale waterbody polygon (WGS84), cross-checked against the City of Chicago Hydro portal export (~10 m). The City ArcGIS layer named in the handoff was unreachable (HTTP 503) when accessed. Water datum z0.5 above the river datum. Grant Park / Museum Campus lawns and the Field Museum, Shedd, Soldier Field and Adler masses are inferred approximations.
- **RF scoreboard.** Anchor from three-camera triangulation (see `scene-spec.json` `rf_scoreboard.basis`); size 36×18.5 m inferred from north-image corner rays; the placement is 4.3 m east of the triangulated centre to clear the traced wall with its supports. Board graphics remain illustrative placeholders.
- **RF / tower structure.** Podium, end wall, link block, arcade and terraces are inferred understructure consistent with the artwork; hidden structure is not certified.
- **Skyline additions.** Heights from Wikipedia/CTBUH/OSM tags as recorded per building in `skyline-v4-additions.json`; footprints from OSM (ODbL). Silhouettes are massing-level.
- **Near-South-Loop context.** OSM buildings with `height` or `building:levels` (×3.4 m) only; repeated windows are schematic.
