# Railyards v3 field audit

`r3_field.py` uses the v3 scene convention that home’s rear point is `(0, 0)`, first base is `(27.432, 0)`, third base is `(0, 27.432)`, and second base is `(27.432, 27.432)`. The scene is in metres.

## Controlled dimensions

- A 90-foot infield is `27.432 m` per side. Second base is placed on the diagonal at `127 ft 3 3/8 in` from home by the same geometry.
- Rulebook Diagram 3 places the mound-circle center 59 feet (`17.9832 m`) from the rear point of home plate. The rubber’s front edge is 18 inches behind that center, so its front edge is 60 ft 6 in (`18.4404 m`) from home; the six-inch slab projects three inches farther toward second base. This corrects the prior `(19.397, 19.397)` mound while preserving the official pitching distance.
- The current MLB base size is 18 by 18 inches (`0.4572 m`). Home plate remains a 17-inch pentagon with 12-inch side edges and 8.5-inch transitions.
- The mound is modeled as a nine-foot-radius (`18 ft` diameter) terraced slope with a ten-inch top elevation and a 24 by 6 inch rubber. Diagram 3 also specifies the six-inch front level area and gradual one-inch-per-foot slope; the terraced mesh is a visual approximation of that profile.
- Batter’s boxes are 4 by 6 feet, the catcher’s box is 8 feet by 43 inches. Chalk is represented as narrow raised white cylinders for aerial readability.

Primary sources:

- [MLB Official Information: Baseball field](https://www.mlb.com/official-information/basics/field) — 60 ft 6 in mound distance and the 90-foot base square / 127 ft 3 3/8 in home-to-second construction.
- [MLB Field Dimensions glossary](https://www.mlb.com/glossary/rules/field-dimensions) — mound diameter, 10-inch height, rubber dimensions, home-plate geometry, and current 18-inch bases.
- [MLB Official Baseball Rules, Rule 2.01 PDF](https://content.mlb.com/documents/2/2/4/305750224/2019_Official_Baseball_Rules_FINAL_.pdf) — field layout, fair territory, mound slope, and the requirement that the batter/catcher boxes follow the official diagrams.
- [MLB 2023 rule changes](https://www.mlb.com/rule-changes-2023) — the 18-inch base change while the 90-foot base distance remains.

## Reference-led estimates

The AECOM north aerial is a conceptual rendering, and `scene-spec.json` records an inferred, manually registered bowl rather than a survey. The broad rounded clay shell, inset rounded grass cutout, 15-foot warning track, and diagonal mowing bands are therefore visual reconstruction choices. MLB rules allow each club to determine the grassed and bare-area shape; the source image is the controlling visual reference for those surfaces. The warning-track width is a common professional treatment, not a universal MLB rule.

The warning track is generated as inward-facing strips along the complete combined `bowl_front + field_boundary` polygon. Adjacent strips share a joined inward offset vertex, with a bounded bevel at the two sharp traced joins; this avoids corner gaps and long overlapping miters while preserving the nominal width along each edge. Foul lines terminate at the two explicit field-boundary endpoints, so they do not stop at the old arbitrary 100-m extents.
