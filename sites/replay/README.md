# Into the River

A browser replay built from the saved Railyards model. One 10.5-second clock drives the authored players, ball, trail, splash and moving cameras. Switching cameras never resets time. All 26,950 modeled seat positions are selectable, including 1,221 outfield seats.

The application uses TypeScript, Three.js and Vite. Blender exports the venue as Draco-compressed GLB and the generic players as glTF transform animation. Seats and spectators are lightweight instances at the original positions. Browser materials approximate procedural Blender shaders; the original scene remains intact.

## Rebuild

From the repository root, restore the saved V9 model if needed, then follow [the V11 rebuild](../../docs/V11-CIRCULATION.md):

```sh
pnpm --dir sites/replay install --frozen-lockfile
/Applications/Blender.app/Contents/MacOS/Blender -b railyards-v4/railyards-v9.blend --python-exit-code 1 --python railyards-v4/build_circulation_v11.py
/Applications/Blender.app/Contents/MacOS/Blender -b railyards-v4/railyards-v11-static.blend --python-exit-code 1 --python railyards-v4/build_replay_v10.py -- --version 11
pnpm --dir sites/replay test
uv run --with imageio-ffmpeg==0.6.0 python sites/build.py --replay
```

Serve `work/web-dist/public` on port 8854, then open `/replay/`. This integrated build includes the V11 rendered films (render them using the linked instructions first). `pnpm --dir sites/replay dev` serves development on 8855; its parent link is intended for the integrated site.

Generated GLBs, JSON point data, decoder copies, scene files and `dist/` are excluded from Git. The private release contains self-contained sites and the saved V11 scenes. Rebuild the assets before running the tests, which validate actual export data.

## Honest boundaries

This is an imagined future play, not an event reconstruction or an aerodynamic simulation. Distances and seats come from an inferred architectural model, not official field dimensions or a ticket plan. Camera views can be obstructed. The optional locator shows the ball through obstructions and can be disabled. No reference-site assets or broadcast audio were copied.
