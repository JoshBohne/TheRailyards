# V15 seating, arrival and Chicago map

V15 applies reproducible corrections to a preserved copy of the consolidated V14 public-site scene. The V3 baseline and the original V14 scene are retained. Generated Blender scenes, renders and browser evidence remain outside Git in `work/v15/`.

## Changes and interpretation

- Left-field return seats use straight rows, aligned aisles and field-facing chairs. The two exposed banks and two existing box floors remain the reconstruction's interpretation of the renderings. On 2026-09-08 the rearmost upper-bank row, which sat under the box floors, was removed; the upper bank is seven rows at the original pitch (`r15_seating.py` `LF_BANKS`). Right field also uses straight banks with a supported connection to the main bowl.
- Nine freestanding arches open directly onto a level, open-air concourse at 13.4 m. The scoreboard terrace is a separate 22.055 m destination with its own eastern stair. Any approach grade change is north of the arches. The left-center seating banks and their walls are removed entirely, leaving a broad flat field overlook. Geometry and elevations remain inferred reconstruction choices.
- Seven LED pinwheels sit on a chevron above the center-field board (blue, red, green, yellow, green, red, blue candy discs on lit posts, after the 2026-09-08 references; four before that). The discs are keyframed to spin at half a turn per second over the scene frame range, with static spark strands above the caps. The board itself is centred on the measured 22.06 m terrace run under its own line (shifted 12.5 m along the board axis on 2026-09-08) so both legs land on the terrace instead of one hanging over the 13.4 m court. The right-field board rises two metres to clear the retained canopy; its geometry is deliberately adjusted from the earlier model.
- The river follows preserved Chicago Hydro geometry using the shared geographic registration. The terrain carve runs per mesh island with a revert guard (2026-09-08); the earlier single Boolean silently deleted the west district ground and most public-realm paving, which rendered as black ground in every daylight aerial. Willis remains at its mapped location, east of the river at its latitude. See [geography evidence](V15-GEOGRAPHY-AUDIT.md).
- The Roosevelt comparison camera includes the mapped Union Station Powerhouse. Camera fitting improves the composition; it does not establish a surveyed match for the inferred building height or every source anchor.
- The map uses a label-free Esri basemap, captured CTA rail geometry, simplified Metra corridors, station and garage markers, and separate conceptual station/parking overlays. Stadium coordinates use the inverse of the Blender registration. Parking markers do not report live availability.

## Rebuild

Run from the repository root, with `BLENDER` pointing to a Blender executable and a preserved consolidated V14 input. Do not use an already corrected V15 scene as input.

```sh
"$BLENDER" -b work/v15/baseline.blend --python-exit-code 1 --python railyards-v4/build_v15.py
"$BLENDER" -b work/v15/railyards-v15-static.blend --python-exit-code 1 --python railyards-v4/verify_audit_v14.py
"$BLENDER" -b work/v15/railyards-v15-static.blend --python-exit-code 1 --python railyards-v4/verify_seat_pairs_v14.py
V15_VIEWS=lf,rf,north,south,bridge,geography,home,concourse "$BLENDER" -b work/v15/railyards-v15-static.blend --python-exit-code 1 --python railyards-v4/render_v15.py
"$BLENDER" -b work/v15/railyards-v15-static.blend --python-exit-code 1 --python railyards-v4/build_replay_v10.py -- --version 15
```

The dedicated `verify_v15_arrival.py` samples the level floor and casts upward to check the open sky above the route, excluding only the arch wall itself. The legacy-named diagnostic scripts read the actual saved input scene and write its SHA-256 into their reports. Their route check covers the park arcade through the field landing; it does not certify every route through the stadium.

## Current delivery state

The saved static scene has SHA-256 `34dc91d5a32f6f2198f721ea4eca5de1f572794e794cab5aedca39a1fe9b8e51` and 32,372 active chairs (32,444 before the LF upper-bank row removal). Its scene-to-replay provenance matches.

- Whole-scene chair-to-architecture probes: zero failures. Park-to-field route: 515 samples, zero failures.
- Dedicated arrival floor/open-sky probes: 105 samples, zero failures.
- Chair mesh pairs: 2,400 contacts, all in the retained main bowl; none in the rebuilt LF/RF returns.
- Replay: six tests pass and TypeScript/Vite build succeeds. Feedback runtime: two tests pass. Local map has been visually inspected.
- Publication follow-up: all 11 replay browser states pass with no page/network errors, synchronized camera controls, and a 390 px mobile check. The earlier failure came from an obsolete view-picker button selector, now corrected.
- Native preview views are saved in `work/v15/review/`. A dark near-field paving patch in the overlook view remains unresolved. Replacing its material did not fix it.
- All 20 required gallery stills and the social card match the static scene. Film packaging requires all 288 frames and matching scene hashes; it fails closed on incomplete renders. `work/v15/release/release.json` and the hosted build manifest record the assembled publication.
- Map is temporarily omitted from public navigation and build assets at the user's request. Its source remains available for later work; old map routes redirect to the overview.

The local live review is at port 8875, the map at port 8874, and the replay at port 8876. Generated artifacts are outside Git. The user authorized publication work using part of the remaining reserve. The unresolved overlook view and retained main-bowl contacts remain outside visual acceptance.

## LF rear enclosure (2026-09-08/09 review)

Josh's thumbs-down on the LF wide view: the stands were see-through from behind. Rays cast outward behind the LF banks from the paving (z 8) up to the lower box floor (z 31.6) travelled 22–55 m before hitting the pavilion brick. A first pass filled the void with a brick block; Josh's 2026-09-09 AECOM crop of the LF corner shows a white concourse plaza with a canopy pavilion behind the stands instead. `r15_seating._close_lf_rear` now builds a 1.5 m stone wall on the upper bank's rear edge (z 8 → 31.55) and a stone deck at the existing court level (z 14.48) from the wall back to the galleries (4–21 m per station). After the rebuild the same rays stop at 2.5–5.8 m; chairs 32,372, contacts 2,400, route 515/0 and arrival 105/0 unchanged. Open items: the deck sits under the V14 box galleries, so it is not the open-sky plaza of the crop, and the canopy pavilion is not modelled.

## LF bank re-alignment (2026-09-09 review)

Josh's second LF thumbs-down: rows must run parallel to the left-field wall, press boxes forward, a right-hand wall, plus a bullpen and outfield seats below the overlook. `LF_BANKS` now carry `parallel` (the LF fence direction, 9.4°), `end_x` 24 and `depth_scale` 62, so `_line_xy` builds each row parallel to the fence at a uniform perpendicular pitch (0.88 m lower, 0.70 m upper) ending on the x = 24 line. `_build_lf_end_wall` closes that line with a stone wall (z 8 → 31.55); the lower bank's rows run on to the bowl's end radial (`inner: radial`, each row starts where its line meets the radial) and the upper bank's inner edge runs straight back from the bowl's rear corner (`inner: back`), so `_fill_lf_wedge` is only a 4 m stone sliver at the rear corner; `_bring_lf_boxes_forward` rotates the V14 box seating to the row direction and slides it to 1.2 m behind the new rear edge (the deeper bank already reaches the gallery front, so no new box slabs were needed). Chairs 32,811 (was 32,372), contacts 2,400, route 515/0, arrival 105/0. Not done: bullpen and seating below the overlook, because the arrival court behind the LF/LC fence sits only 1.4 m above the field and the crop implies about 5 m; that level change needs Josh's call.

## Not yet regenerated after the 2026-09-08 corrections

The static scene above carries the LF row removal, the river carve fix, the centred board and the LED pinwheels, but the release pipeline has not been re-run on it: the 20 gallery stills, the social card, the replay export (`build_replay_v10.py`), the film frames and the hosted build still come from the earlier 8-row scene. The provenance and "all stills match" statements above describe that earlier release, not this scene.

## Acceptance boundary

This delivery does not close the earlier 23-finding V14 audit. The retained main bowl has known chair-mesh contacts that prevent a whole-model collision-free claim. Source renderings remain the architectural reference; geographic data establishes plan positions, while unseen circulation, structural details, vertical datums and future developments remain illustrative.

Local build, saved-scene verification, a pushed PR, and public deployment are separate delivery states. The final release receipt and browser evidence identify the tested scene and deployment state.
