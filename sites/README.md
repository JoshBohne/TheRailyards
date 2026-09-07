# Browser-first Railyards experiences

Two independent static sites share rendered artifacts, not a live Blender viewport.

- `public/`: fan-facing preview, experience films, river distance illustration, and source/uncertainty context.
- `review/`: working version comparisons, unresolved issues, form studies, and the same experience films.
- Earlier `../site/` remains preserved as Fable’s draft.

Build both after rendering the documented V9 artifacts:

```sh
uv run --with imageio-ffmpeg==0.6.0 python sites/build.py --encode
python3 -m http.server 8853 --bind 127.0.0.1 --directory work/web-dist/review
# In another terminal:
python3 -m http.server 8854 --bind 127.0.0.1 --directory work/web-dist/public
```

Open `http://127.0.0.1:8853/` for review and `http://127.0.0.1:8854/` for the public preview. Each output directory is self-contained and can be deployed separately. The review navigation’s local public-preview link should be changed to the deployed preview URL if hosted remotely.

Build outputs and frame caches are ignored by Git. The builder fails on missing frames or media; it never silently substitutes a still for a movie. All films are H.264 MP4 with native browser controls and no autoplay. Theme selection and reduced-motion preferences are respected by the public page.

V10 adds the [interactive replay](replay/README.md) at `/replay/`. After exporting its model, use `sites/build.py --replay` to include the application in the public build.
