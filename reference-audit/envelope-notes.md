# Railyards v3 envelope notes

This pass uses the 2,400 × 1,200 south closeup served at
`reference-audit/parent-stadium-closeup.html` (source crop x=1400, y=1250,
w=2000, h=1200), the south AECOM aerial, and the high resolution B4 north
aerial. The served crop was allowed to decode before inspection. The B4 image
is the most useful source for the repeated roof ribs, light gantries, and the
open clock lantern; the south crop is the most useful source for the masonry
facade and upper fascia.

## Visible composition translated to the model

The river-facing envelope reads as a continuous warm brick hall over a pale
stone plinth. The lower bays are tall, broad, and round-headed, with full
height dark glazing and stone arch rings. The south crop resolves roughly
12–15 prominent front bays; the v3 envelope uses about 19 bays around the full
traced horseshoe, with approximately 10.5 m openings and 18 m bay spacing.
The arch heads sit just below the dark glazed/louver fascia, leaving a thin
masonry spandrel rather than a blank upper grid. The sign now crosses adjacent
front bays on a projected dark panel; its target width is about 0.3 of the
visible front facade, matching the south crop.
The fascia carries the main sign. The roof is a broad shallow barrel shell,
not a flat lid: its outer traced edge is z=48 and its inner traced edge is
z=46, with a 3.25 m crown lift and 18–19 visible radial ribs. Floodlight
gantries sit on the outer roof edge as short steel lattice frames with compact
horizontal lamp banks.

The clock tower retains the calibrated XY anchor `[81.5378, -76.3826]` and
roof datum z=68. Its lower shaft is stepped brick/stone construction. Above
the shaft is a wide transparent lit lantern, approximately z=47.6–63, with a
large dark circular clock face on each visible side. The cap is stepped and
slightly wider than the lantern. The west lantern retains
`[-62.3406, -6.3273]` and roof z=56.

The river-side arcade is an explicit inferred volume at
`[(18,-135), (109,-99), (106,-79), (23,-109)]`. It is separate from the main
facade and uses a lower 8–20 m brick/arch level, upper glazed level to z=27.8,
and a shallow metal roof at z=28.6. This footprint is used because the long
arcade is visible in the south crop; its hidden back edge remains uncertain.

## Attachment and coordinate notes

`r3_envelope.build_envelope(scene, spec, batch, materials)` consumes the
existing `scene-spec.json` curves directly. Every main facade segment is
derived from `bowl_back`; canopy quads and ribs use the paired
`canopy_inner`/`bowl_back` points without rescaling. Positive local facade
depth is the path's left normal, which is the street/river-facing side for the
traced path. The main facade starts at z=8, its stone plinth finishes at z=11.3,
and the upper fascia finishes at z=47.6 beneath the z=48 canopy datum.

The new module produces these independently batched groups: `Stadium
envelope`, `River-side arcade`, `Canopy`, `Floodlight gantries`, and `Clock
tower`. It does not create field, seating, scoreboards, adjacent buildings,
park, bridges, rail, river, or other context.

## Evidence boundary

The source establishes the silhouette, cadence, materials, and relative
proportions. The reconciled main section uses arch crowns at z≈33.45, a dark
fascia beginning at z=35.2, and the full upper wall/cap at z=47.6 beneath the
z=48 roof datum. Exact structural sections, floor heights, hidden wall depth,
clock time, and the arcade's unseen faces are inferred. This pass intentionally
keeps the existing calibrated path and tower XY anchors rather than globally
inflating the stadium. The integrator should judge the saved-scene renders
against south, north, and bridge views; object existence or vertex counts do
not establish visual acceptance.
