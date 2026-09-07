# Into the River

A browser replay built from the saved Railyards model. One 10.5-second clock drives the authored players, ball, trail, splash and moving cameras. Switching cameras never resets time. Every modeled seat position is selectable, including the outfield terraces, the V12 left-center bank and the right-field corner; the exact count is in the export receipt.

The application uses TypeScript, Three.js and Vite. Blender exports the venue as Draco-compressed GLB and the generic players as glTF transform animation. Seats and spectators are lightweight instances at the original positions. Browser materials approximate procedural Blender shaders; the original scene remains intact.

## Rebuild

From the repository root, follow [the V12 rebuild](../../docs/V12-PROPORTIONS.md) (the V11 commands remain in [V11-CIRCULATION.md](../../docs/V11-CIRCULATION.md)):

```sh
pnpm --dir sites/replay install --frozen-lockfile
railyards-v4/build_v12.sh
pnpm --dir sites/replay test
uv run --with imageio-ffmpeg==0.6.0 python sites/build.py --replay --scene-version 12
```

Serve `work/web-dist/public` on port 8854, then open `/replay/`. This integrated build includes the V12 rendered films (render them using the linked instructions first). `pnpm --dir sites/replay dev` serves development on 8855; its parent link is intended for the integrated site.

Generated GLBs, JSON point data, decoder copies, scene files and `dist/` are excluded from Git. The private release contains self-contained sites and the saved V12 scenes. Rebuild the assets before running the tests, which validate actual export data.

## Honest boundaries

This is an imagined future play, not an event reconstruction or an aerodynamic simulation. Distances and seats come from an inferred architectural model, not official field dimensions or a ticket plan. Camera views can be obstructed. The optional locator shows the ball through obstructions and can be disabled. No reference-site assets or broadcast audio were copied.
