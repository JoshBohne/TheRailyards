# The Railyards site

The current public site and database-backed feedback runtime follow [the V14 site release instructions](../docs/V14-SITE-RELEASE.md). Build with `sites/build-hosted.py --release-root work/night-game/release`; the current builder does not fall back to archived model media.

The instructions below describe the preserved earlier experience/review builds.

# Browser-first Railyards experiences

The public experience is deliberately split from the model-review surface. Both are static builds that consume rendered artifacts rather than exposing Blender as the viewing interface.

- `public/`: the fan-facing launch site. It leads with a guided four-scene tour, an interactive orientation map, three source/model comparisons, skyline context, a clear uncertainty legend, and a secondary build log at `/process.html`.
- `replay/`: the larger real-time Three.js experience at `/replay/`, with eight synchronized perspectives and a picker for all modeled seats.
- `review/`: working version comparisons, unresolved issues, form studies, and the same rendered experience films.
- Earlier `../site/` remains preserved as Fable’s draft and historical process archive.

## Build

Build the static sites after rendering the current V11 media (or pass `--scene-version 9` for the preserved V9 set):

```sh
uv run --with imageio-ffmpeg==0.6.0 python sites/build.py --encode --replay --scene-version 11 --site-url https://your-domain.example
python3 -m http.server 8853 --bind 127.0.0.1 --directory work/web-dist/review
# In another terminal:
python3 -m http.server 8854 --bind 127.0.0.1 --directory work/web-dist/public
```

Open `http://127.0.0.1:8853/` for model review and `http://127.0.0.1:8854/` for the public experience. Each output directory is self-contained and can be deployed independently. The review navigation’s local public-preview link should be changed to the deployed URL when hosted remotely.

The builder fails on missing frames or media; it never silently substitutes a still for a film. All films are H.264 MP4 with native browser controls and no autoplay. The public site preserves deep-linked views with `?view=arrival`, `left_center`, `boat`, or `river`. Theme selection, keyboard navigation, accessible comparison controls, and reduced-motion preferences are supported.

Pass `--site-url` (or set `RAILYARDS_SITE_URL`) for canonical URLs and absolute Open Graph/Twitter image metadata. Vercel production URL environment variables are detected automatically.

`--scene-version` defaults to `11`, but accepts any later rendered version that follows the existing `review/vN/` and `vN-{north,south,bridge}.png` artifact layout.

Run with `--replay` to build and copy the current replay application into the public output. Without it, the main static site still builds, but links to `/replay/` require a separately deployed replay bundle.
