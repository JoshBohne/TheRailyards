# V11 — Roosevelt, outfield and riverwalk

V11 applies Fable's V10 review to the model and replay. The preserved V9 static scene is the build input; V3, V9 and V10 saved scenes remain separate.

The raised Roosevelt park now continues onto one graded restaurant/outfield terrace. The old wall across the arrival path and overlapping roof caps are removed. The riverfront has recessed brick arches, café glazing, stepped quay seating, planting and a broad corner stair. The broad source-traced left-center plaza is retained; stairs connect both outfield banks to the lower concourse, with openings in its perimeter guardrail and supporting structure below.

The artwork supports the plaza continuity, arcade and riverwalk arrangement. Dimensions, grades, structural supports, unseen stairs and exact connections remain inferred. This is a spatial reconstruction, not a construction or accessibility design. Existing approximate geographic registration and camera calibration are retained.

The replay follows the arrival route onto the terrace and adds an “Along the riverwalk” camera. Its lower illustrative flight and limited tracking pitch retain the bowl and skyline in the seat views. The contact camera shifts away from the backstop posts. Instanced seats, people and trees are grouped spatially so offscreen chunks can be culled; all 26,950 selectable seat IDs remain intact. Nearby visitors are hidden along the moving camera routes. Only people hidden for the previous view are restored on camera changes.

The main site uses V11 rendered films and stills. The review site defaults to V11 and retains the V9/V8/V3 comparisons, plus pedestrian-view before/after images. The flight stays on the fair right-field side of the board; its updated horizontal model distances round to 423 ft at the water and 469 ft at the splash. The arc is illustrative, not a physical trajectory prediction.

## Rebuild

Run from the repository root, with Blender available as `blender` (on this Mac: `/Applications/Blender.app/Contents/MacOS/Blender`). Always use `--python-exit-code 1`; Blender otherwise may return success after a script exception.

```sh
blender -b railyards-v4/railyards-v9.blend --python-exit-code 1 --python railyards-v4/build_circulation_v11.py
blender -b railyards-v4/railyards-v11-static.blend --python-exit-code 1 --python railyards-v4/build_replay_v10.py -- --version 11
blender -b railyards-v4/railyards-v11.blend --python-exit-code 1 --python railyards-v4/verify_scene.py
blender -b railyards-v4/railyards-v11-static.blend --python-exit-code 1 --python railyards-v4/verify_circulation_v11.py
```

`verify_circulation_v11.py` repeats Fable's fixed pedestrian cameras, adds stair views, records floor/body probes at roughly one-metre intervals and fails on arrival gaps or architectural obstructions. These probes establish route continuity, not full visual fidelity or code compliance.

```sh
RAILYARDS_LABEL=v11 blender -b railyards-v4/railyards-v11-static.blend --python-exit-code 1 --python railyards-v4/render_scene.py
RAILYARDS_OUTDIR=review/v11 RAILYARDS_VIEWS=arrival,left_center,boat,skyline_west,skyline_east blender -b railyards-v4/railyards-v11-static.blend --python-exit-code 1 --python railyards-v4/render_experiences.py
RAILYARDS_OUTDIR=review/v11 RAILYARDS_ENGINE=BLENDER_EEVEE RAILYARDS_WIDTH=1280 RAILYARDS_SAMPLES=16 RAILYARDS_MOTION=move RAILYARDS_VIEWS=arrival,left_center,boat RAILYARDS_FRAMES=192 blender -b railyards-v4/railyards-v11-static.blend --python-exit-code 1 --python railyards-v4/render_experiences.py
RAILYARDS_WIDTH=1280 RAILYARDS_SAMPLES=16 RAILYARDS_FRAMES=168 blender -b railyards-v4/railyards-v11.blend --python-exit-code 1 --python railyards-v4/render_river_study.py
pnpm --dir sites/replay test
uv run --with imageio-ffmpeg==0.6.0 python sites/build.py --encode --replay
```

The site outputs are `work/web-dist/public` and `work/web-dist/review`. The main site's `replay/` folder is self-contained. Each build manifest records its commit, dirty state and asset hashes.

With the site running, use `REPLAY_URL=http://127.0.0.1:8854/replay/ pnpm --dir sites/replay verify:browser`. Install Playwright's Chromium using `pnpm --dir sites/replay exec playwright install chromium`, or set `PLAYWRIGHT_CHROMIUM_EXECUTABLE` to an existing executable. The script captures eleven desktop camera/time states and two mobile layouts, checks share-link initialization, shared-clock camera switching, HTTP/page errors and horizontal overflow. Inspect the images in `work/replay-verification`; screenshot capture alone is not visual acceptance.

## Remaining limits

Real-phone GPU performance, a mid-range laptop benchmark and hosted-network loading remain unmeasured. Browser exports flatten procedural materials and simplify crowds; close views reveal those approximations. Splitting far context into a deferred GLB, binary instance data, more detailed athlete animation and a vertical splash plume are deferred. This pass prioritizes the requested circulation defects and the review's principal replay/framing fixes.
