# Immediate-area audit

The v2 stadium has a usable north-facing bowl and field anchor, but the immediate district still reads as a blockout. The next modeling pass should spend its budget on the four named adjacent buildings, the riverwalk and park levels, the rail crossings, and Roosevelt bridge structure. The skyline can stay a low-confidence framing layer until those elements hold together.

## What the references establish

The north aerial is the best geometric anchor: the asymmetric bowl, left-field tower, dark canopy, centerfield rounded frontage, rail corridor, medical sign building, pavilion roof corners, and long hall are all visible in one frame. The newly available full-resolution north source keeps that framing at 5000 x 3333 and makes the rooftop terraces, under-lawn glazed pavilions, formal lawn paths, lower promenade, and Roosevelt-corner stairs readable. The south aerial supplies the clearest facade and rail-yard rhythm at a larger native size. The bridge view supplies the structure and public-realm relationship at Roosevelt bridge. The site plan confirms orientation, the west rail corridor, Roosevelt Road north of the stadium, the Chicago River edge, and the river bend toward 18th Street. It is schematic and does not dimension the stadium glyph.

The four source-visible buildings have distinct jobs in the composition:

* The medical main and wing are a long institutional bar with a purple Northwestern Medicine sign, finer curtain-wall rhythm, and stepped roof/wing massing.
* The left-field pavilion is an elongated dark-roof volume that mediates the bowl, rail crossing and hall. It is not a freestanding cube.
* The north entertainment hall is a long brick/glass block with strong vertical bays, a deep rooftop terrace, and an active edge to the park.
* The centerfield restaurant is a broad curved/glazed frontage below the centerfield screen. Its dark rounded canopy and upper terrace make it a public-front anchor on the riverwalk.

## Current v2 read

The north overlay shows that the field and broad bowl placement are close on selected controls (2.9 px RMS per coordinate, 5.6 px maximum). That result should be preserved. The render still loses source identity in the canopy ribs, tower-to-roof junction, facade bay hierarchy, and river-facing cornice. The facade detail render makes the issue clear: the current shell has clean repeated windows and arches, but it lacks the source's stronger layered cornice, varied bay groups, and active curved frontage.

The four adjacent masses technically exist in `scene-spec.json`, but they read as generic gridded envelopes. The medical sign is not a strong visual anchor, the left-field pavilion is too boxy, the entertainment hall has no convincing roof terrace, and the rounded restaurant is too small and detached. South fitting exposes the problem: RMS is 34.2 px per coordinate and the selected left-field pavilion roof control is 111.2 px off. That number is a selected-control diagnostic, not a whole-scene score, but it identifies the pavilion/camera relationship as a practical next check.

The park and river edge are the largest near-field gap. The full-resolution source shows an elevated lawn held by formal segmented paths and lawn steps, a broad lower waterside promenade, loose tree and furniture clusters, several low glazed pavilions tucked under the lawn edge, and a grand stair sequence at the Roosevelt corner. The current scene has a blank rectangular lawn, grid-planted trees, narrow straight quays and stairs that are too subtle to establish levels. Keep the current simplified river as a staging device, but introduce visible upper, intermediate and lower public levels and vary the river edge south of Roosevelt where the plan/source bends. The standalone `r3_public_realm.py` module and `public-realm-spec.json` record this bounded replacement without taking ownership of roads, rail, bridge or skyline geometry.

The rail corridor is present but too diagrammatic. The code retains four pedestrian crossings, which is a useful count prior, yet the renders show thin repetitive bars. In the references, the crossings have substantial covered decks, side/roof edges, landings and layered relationships to parallel tracks, roads and concourses. Give those existing crossings depth and public connections before adding more city blocks.

Roosevelt bridge is also under-modeled. The bridge source has a broad multi-lane deck, paired bank/road-edge tower or tender-house forms with ornamental tops, a visible under-span arch/steel assembly, traffic/lane rhythm, and a lit park/lower walk on the near bank. The current render has a narrow deck, simple truss lines, box piers and one small striped house. Match deck width and the paired silhouettes first, then add the under-span and connect the riverwalk below.

## Correction sequence

1. Preserve the north bowl/field anchor. Correct facade/cornice, canopy ribs and tower junction; enlarge and integrate the centerfield curved frontage.
2. Rebuild the medical, left-field pavilion, north hall and rounded restaurant as distinct masses with source-facing roof and facade rhythms. Use the recorded footprints as visual plan priors only; elevations remain inferred.
3. Replace the blank park with a connected upper plaza, lawn rooms, diagonal/river-parallel paths, irregular planting groups, visible furniture and legible stairs/landings.
4. Give the four existing rail crossings covered depth, guard/roof edges and concourse landings; enrich the track/road hierarchy.
5. Correct Roosevelt bridge deck width, paired tower/pylon silhouettes and under-span structure; tie the lower riverwalk and near-bank park into it.
6. Warm the public realm and adjacent facades to match source value structure after geometry is stable. Revisit skyline density only after near-field checks pass.

The detailed element inventory, approximate source pixel boxes and per-element correction specs are in [immediate-elements.json](/Users/joshbohne/Documents/Codex/2026-09-05/i-h/outputs/reference-audit/immediate-elements.json). The model's own source/assumption limits remain in [SOURCE-AND-ASSUMPTIONS.md](/Users/joshbohne/Documents/Codex/2026-09-05/i-h/outputs/railyards-v2/SOURCE-AND-ASSUMPTIONS.md).
