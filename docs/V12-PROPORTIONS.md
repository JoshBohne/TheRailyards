# V12 — stadium proportions

V12 answers the V12 handoff: the interior and outfield read as one coherent bowl instead of a set of instantiated parts. V11 and every older saved scene are untouched; V12 is built from the generators into `railyards-v12-static.blend` and `railyards-v12.blend`.

## What was wrong, measured

| Item | V11 geometry | Source reading |
| --- | --- | --- |
| Seating front behind home plate | 5.7 m from the plate (V2 trace) | Curved backstop, roughly 16–18 m |
| Third-base foul clearance | 5 m from the line at the dugout, 0.3 m at y 80 | Same as first base, 12–13 m |
| First-base foul clearance | 12.8 m (trace kept) | — |
| Third-base dugout | 17 m long, its front on the foul line | Mirror of the first-base dugout |
| Plaza edge above left-center | z 22.0, 17–24 m behind the wall; bleachers topped out at z 17, 9 m behind the wall; one 4 m stair bridged the 5–9 m drop | Plaza flows straight down into a bleacher bank (`reconstruction-references/v12-user-north-transition.png`) |
| Right-field corner | Bare 13.4 m terrace behind the foul-pole diagonal with a railing; board on lattice legs from the ring; nothing between tower and board along the river | Seating wrapping the pole on a solid base; a two-level lit gallery on posts along the river from the tower past the board, the board frame standing on its upper level |
| Tower flag | Pole 1.7 m outside the shaft face, from z 56 to 72, flags below the roof line | Mast on the tower roof |
| Field-edge wall | Void between the field (z 12) and the tier fascia (z 13.1) | Padded wall |

## What V12 changes

- **Bowl front** (`scene-spec.json` → `bowl_front`, written by `tools/correct_bowl_front_v12.py`): 123 of 161 traced points are pushed along their own front→back ray until they clear 12.8 m either side of the foul lines (tapering to 4 m at the poles) and a 16.5 m backstop radius. Row/tier indices stay aligned with the traced `bowl_back`, so every tier, concourse, end wall and podium follows automatically. The diamond, poles, outfield wall and traced facade do not move. The original trace is kept as `bowl_front_v11_trace`.
- **Dugouts** (`r3_bowl_details.py`): both 20 m long, backs against the 12.8 m clearance, fronts 10.1 m off their lines.
- **Field-edge wall** (`r3_bowl_details.py`): padded wall from the field to the fascia along the whole bowl front.
- **Left-center bank** (`r12_outfield.py`): 18 level rows (0.78 m tread, 0.467 m rise, about 31°) parallel to the plaza edge, from 1.6 m behind the wall up to a 2.4 m cross-aisle flush with the plaza. Aisles run straight down from the plaza. The bank extends 10 m west of the plaza and east to the batter's eye, with brick end walls following the rake and a paved landing joining the plaza corner to the restaurant roof edge. It replaces the V11 stair and the elevated path over the void.
- **Right-field corner** (`r12_outfield.py`): 12 rows (0.85 m tread, 0.40 m rise) parallel to the foul-pole diagonal, a 2.4 m rear aisle with a brick parapet, brick end walls, and an arcade on the south-east face (ground z 8) and the east face (riverwalk z 4.95). The block replaces the V4 terrace railing on that edge.
- **Right-field river gallery** (`r12_outfield.py` `build_river_deck`): the north aerial shows a two-level open gallery on slender posts along the river between the clock tower and the board, people on both levels, festoons below and the board's dark frame rising from the upper terrace. V12 builds it from y −62 to 57: decks at z 11.3 and 16.5 over the riverwalk, a canopy at 20.7, the upper deck widened over the podium ring to the outfield wall in the board zone, stairs to the quay, between levels and to the ring, festoons and crowd. The board's steel pylons now bear on that upper deck (`rf_scoreboard.support_base_z` 16.5); its anchor, size and angle are unchanged.
- **Outfield terraces** (`r3_outfield.py`): only the board-to-center-field bank and the small left-field-pole bank remain as low terraces.
- **Flag** (`r3_bowl_details.py`): a 12.8 m mast on the tower roof cap with a base sleeve and finial; the city flag and team pennant fly above the roof.

## Source versus inference

The artwork establishes: balanced foul territory and a curved backstop; a plaza that continues down into left-center bleachers; a solid brick right-field corner under the board; a roof mast. Everything dimensional is inferred: the 12.8 m clearance (symmetric with the traced first-base side), the 16.5 m backstop, rakes, row counts, cut lines, the board house, the end walls and all understructure. This is a spatial reconstruction, not an engineering or accessibility design.

## Rebuild

From the repository root, Blender 5.2 as `blender` (`/Applications/Blender.app/Contents/MacOS/Blender` on this Mac). Intermediate stage files go to `railyards-v4/work/v12-chain`, so the preserved V3–V11 scenes are never overwritten.

```sh
railyards-v4/build_v12.sh
blender -b railyards-v4/railyards-v12-static.blend --python-exit-code 1 --python railyards-v4/verify_v12.py
RAILYARDS_SCENE_LABEL=v11 RAILYARDS_OUTDIR=review/v12/before blender -b railyards-v4/railyards-v11-static.blend --python-exit-code 1 --python railyards-v4/verify_v12.py
RAILYARDS_LABEL=v12 blender -b railyards-v4/railyards-v12-static.blend --python-exit-code 1 --python railyards-v4/render_scene.py
RAILYARDS_INTERIOR_PREFIX=v12-interior- blender -b railyards-v4/railyards-v12-static.blend --python-exit-code 1 --python railyards-v4/render_interior.py
RAILYARDS_OUTDIR=review/v12 RAILYARDS_VIEWS=arrival,left_center,boat,skyline_west,skyline_east blender -b railyards-v4/railyards-v12-static.blend --python-exit-code 1 --python railyards-v4/render_experiences.py
RAILYARDS_OUTDIR=review/v12 RAILYARDS_ENGINE=BLENDER_EEVEE RAILYARDS_WIDTH=1280 RAILYARDS_SAMPLES=16 RAILYARDS_MOTION=move RAILYARDS_VIEWS=arrival,left_center,boat RAILYARDS_FRAMES=192 blender -b railyards-v4/railyards-v12-static.blend --python-exit-code 1 --python railyards-v4/render_experiences.py
RAILYARDS_OUTDIR=review/v12 RAILYARDS_WIDTH=1280 RAILYARDS_SAMPLES=16 RAILYARDS_FRAMES=168 blender -b railyards-v4/railyards-v12.blend --python-exit-code 1 --python railyards-v4/render_river_study.py
pnpm --dir sites/replay test
uv run --with imageio-ffmpeg==0.6.0 python sites/build.py --encode --replay --scene-version 12
```

`build_v12.sh` runs the V4 chain (`build_blockout.py` → `build_detail.py` → cameras → `finalize_scene.py` → `finalize_v8.py` → `finalize_v9.py`) and then `build_circulation_v12.py`, which applies the V11 public realm and the V12 banks and saves `railyards-v12-static.blend`; it then exports the replay (`build_replay_v10.py -- --version 12`) and saves `railyards-v12.blend`. `verify_v12.py` repeats the V11 arrival floor probes, walks the first left-center aisle from the plaza to the wall, measures the built foul clearances, and renders the acceptance views (`review/v12/v12-*.png`; the same cameras on V11 in `review/v12/before/`).

## Acceptance views

`review/v12/`: three fixed source comparisons (`v12-{north,south,bridge}.png`), interiors (`v12-interior-*.png`), and the paired before/after cameras: left-center from the plaza, from the field, aerial and along the top aisle; the park toward the bleachers; the right-field corner from the field, the river, the air and the upper deck; the third-base line, the dugouts and the backstop from the upper deck; the flag close-up and tower context; a stadium plan and sections through left-center, the right-field corner and third base.

## Remaining limits

The seat export grew from 26,950 to the count recorded in the build receipt, so a V11 share link with `seat=N` selects a different seat in V12. The lower outfield concourse behind the right-field terraces is still a covered corridor. Crowd figures, materials and board graphics remain schematic, and the geographic registration and camera calibration are unchanged from V4.
