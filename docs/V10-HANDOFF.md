# V10 — Into the River

The request was to investigate the OG Game 4 basketball replay and use the same approach for a home run into the Chicago River, with browser-delivered scenes that help people imagine the proposed ballpark.

## Reference findings

A research subagent inspected the live [Garden replay](https://the-garden-og-game-four.vercel.app/), its [interface bundle](https://the-garden-og-game-four.vercel.app/assets/index-B5HUo2ua.js) and its [arena bundle](https://the-garden-og-game-four.vercel.app/assets/arena-C6C81vWp.js).

The reference uses a React interface around Three.js, procedural arena geometry, imported player GLBs, a deterministic 12-second timeline, baked hero motion sampled with `AnimationMixer.setTime(t)`, supporting procedural poses and a separate ball trajectory. Seats are calculated along row polylines; camera changes preserve replay time. Its own provenance panel describes hand-staged motion, not optical or volumetric tracking. Public evidence does not substantiate the tweet's claim about watching thousands of clips or establish which software authored the GLBs.

No venue, player, animation or audio assets were copied. The useful pattern is a single reconstructed scene and shared clock viewed through different cameras.

## Implemented

- Full-window replay integrated into the existing public preview at `/replay/` and linked from the working review site.
- Seven curated perspectives: aerial, behind the plate, upper deck, left-center terrace, boat level, ball follow and Roosevelt approach.
- A seat map plus tier/row/seat controls for the saved model's 26,950 actual positions: 25,729 in the bowl and 1,221 outfield seats. Numbering is local to the reconstruction.
- Play/pause, restart, scrubbing, quarter/half/full speed, looping, keyboard controls, camera gaze/zoom, fullscreen, crowd toggle and links preserving camera/seat/time.
- Optional trajectory and ball locator. The locator can show the ball through real occluders; it is identified as an aid, not a clear sightline.
- Reproducible Blender-authored generic batter and pitcher motion. Contact occurs at 1.55 s and the illustrative splash at about 8.427 s. The ball samples, actors and camera paths use the same clock.
- Existing V9 geometry preserved. V10 saves separately as `railyards-v4/railyards-v10.blend`. Browser export simplification occurs in a disposable scene after saving the authoring file.

## Tool split and validation

Blender CLI builds, exports and renders. Blender MCP opens the saved V10 and inspects contact/cameras in the live scene. Computer use verifies the actual browser output and controls.

The native flight path was sampled against full-resolution static geometry; no collisions were reported. At contact the ball is at home plate `(0, 0, 13)` and the authored bat crosses that point. Three tests verify the exported contact/landing, seek-order independence and complete seat enumeration. TypeScript and the production build pass.

Independent browser review confirmed timeline/camera continuity and seat selection, and identified three corrections: expose the seat picker immediately, offset the boat camera to reveal the splash, and stop the arrival approach before the visually empty endpoint. Final visual evidence and browser checks are included with the release.

## Limits and next work

The play and player motion are illustrative. Materials, crowd geometry and some architecture remain schematic. Procedural shaders are flattened for the browser; tree detail is reduced, and static sun shadows do not follow the animated figures. There is no broadcast audio. The large venue export is about 28 MB before server compression, so slower connections and lower-end devices need further optimization before a broad public launch.

The model's 429 ft to the water and 476 ft to the illustrated splash are horizontal measurements along one chosen line. They are not official dimensions or predicted ball flight. The current delivery is a local preview and private backup, not a public deployment or a claim of final visual acceptance.

Rebuild and serve using [the replay instructions](../sites/replay/README.md).
