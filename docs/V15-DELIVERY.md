# V15 seating, arrival and Chicago map

V15 applies reproducible corrections to a preserved copy of the consolidated V14 public-site scene. The V3 baseline and the original V14 scene are retained. Generated Blender scenes, renders and browser evidence remain outside Git in `work/v15/`.

## Changes and interpretation

- Left-field return seats use straight rows, aligned aisles and field-facing chairs. The two exposed banks and two existing box floors remain the reconstruction's interpretation of the renderings. Right field also uses straight banks with a supported connection to the main bowl.
- Nine freestanding arches open directly onto a level, open-air concourse at 13.4 m. The scoreboard terrace is a separate 22.055 m destination with its own eastern stair. Any approach grade change is north of the arches. The left-center seating banks and their walls are removed entirely, leaving a broad flat field overlook. Geometry and elevations remain inferred reconstruction choices.
- Four colored pinwheels sit above the center-field board. The right-field board rises two metres to clear the retained canopy; its geometry is deliberately adjusted from the earlier model.
- The river follows preserved Chicago Hydro geometry using the shared geographic registration. Willis remains at its mapped location, east of the river at its latitude. See [geography evidence](V15-GEOGRAPHY-AUDIT.md).
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

The saved static scene has SHA-256 `5c909c6b1903aecb6cd4a271951762979b66548b4b3b758c343f52e75aba41ea` and 32,444 active chairs. Its scene-to-replay provenance matches.

- Whole-scene chair-to-architecture probes: zero failures. Park-to-field route: 515 samples, zero failures.
- Dedicated arrival floor/open-sky probes: 105 samples, zero failures.
- Chair mesh pairs: 2,400 contacts, all in the retained main bowl; none in the rebuilt LF/RF returns.
- Replay: six tests pass and TypeScript/Vite build succeeds. Feedback runtime: two tests pass. Local map has been visually inspected.
- Browser screenshot verification timed out; it is not a passing browser suite.
- Native preview views are saved in `work/v15/review/`. A dark near-field paving patch in the overlook view remains unresolved. Replacing its material did not fix it.
- New gallery stills and social card were rendered. The 288-frame film remains incomplete. The V15 hosted release has not been packaged or published. HTML now targets V15 media and must be built with a complete matching release before deployment.

The local live review is at port 8875, the map at port 8874, and the replay at port 8876. Generated artifacts are outside Git. Work stopped for the user's weekly usage reserve; this is a draft checkpoint, not visual acceptance.

## Acceptance boundary

This delivery does not close the earlier 23-finding V14 audit. The retained main bowl has known chair-mesh contacts that prevent a whole-model collision-free claim. Source renderings remain the architectural reference; geographic data establishes plan positions, while unseen circulation, structural details, vertical datums and future developments remain illustrative.

Local build, saved-scene verification, a pushed PR, and public deployment are separate delivery states. The final release receipt and browser evidence identify the tested scene and deployment state.
