# Current V14 site release

The site uses one consolidated source scene: the final V14 stadium (two exposed LF seating banks and the square south arcade corner), plus the merged McDonald’s Park / powerhouse / rail-bridge pass. The former V12 hero and archived replay payload are no longer accepted as build inputs.

## Reproduce

From this repository, first open the preserved final `railyards-v14-static.blend` as the input to `railyards-v4/build_site_release_v14.py`. Set `RAILYARDS_RELEASE_SCENE` to a new `railyards-v4/railyards-v14-site-static.blend`. The input scene and V3 baseline are preserved. The builder writes input and generator hashes beside the output.

Run `railyards-v4/build_replay_v10.py -- --version 14` against that consolidated static scene. The export retains active seat scales, row elevations and the V13 park entrance. Its `sourceStaticSha256` ties the replay to the saved scene. The authored animated scene is `railyards-v4/railyards-v14.blend`.

Render these from the consolidated **static** scene:

- `railyards-v4/render_audit_v14.py`, with `REVIEW_OUT=work/night-game/stills` and `VIEWS=frontage,south-extension,south-extension-plan,tower-corner,south,north,bridge,lf-roof-field,lf-roof-rear`.
- `sites/render-current-gallery.py` for the interior, riverbank and skyline stills.
- `sites/render-social-preview.py`, with `RAILYARDS_SOCIAL_OUT=work/night-game/og-home-run.png`.
- `sites/verify-current-scene.py`, with `RAILYARDS_SCENE_CHECK=work/night-game/scene-check.json`.

Render `sites/render-night-game.py` from the **animated** scene, setting `RAILYARDS_HERO_OUT=work/night-game/frames`. It renders 288 frames at 24 fps. Use `RAILYARDS_HERO_FRAMES=36,84,138,202` and a separate output directory for camera previews. A preview receipt cannot be packaged as a complete film.

The cameras cut at 2.4, 5.0 and 6.65 seconds: home plate, above the diamond, right-field corner, river. The ball splashes at 7.65 seconds. The river camera stays fixed, retaining the low splash, two-sided HOME RUN board and fireworks above it. Ball size, player animation and celebration effects are illustrative.

Then:

```sh
pnpm --dir sites/replay install --frozen-lockfile
pnpm --dir sites/replay test
pnpm --dir sites/replay build
python3 sites/package-current-media.py --ffmpeg /absolute/path/to/ffmpeg
python3 sites/build-hosted.py --release-root work/night-game/release
pnpm --dir sites/runtime install --frozen-lockfile
pnpm --dir sites/runtime test
pnpm --dir sites/runtime exec tsc --noEmit
pnpm --dir sites/runtime build
```

`build-hosted.py` verifies every release file hash and the static scene identity before copying anything. It splits the lossless compressed venue buffer for the hosting file limit. The build manifest records all output hashes and the two source scene hashes. The current release package replaces the old archive fallback; missing current media is an error.

## Database-backed feedback

The Sites runtime is in `sites/runtime/`; its `.openai/hosting.json` is the single hosting configuration. It reuses the existing Site and adds the logical `DB` D1 binding. `drizzle/` contains the generated schema migration. The Worker exports a callable `fetch`, serves static assets, and handles only `POST /api/feedback` for submissions. Feedback has no public read endpoint.

The form accepts a category and 5–2,000 characters. The server checks origin, content type, body size, permitted pages, UUID and category, and binds the values in one prepared statement. Submission IDs prevent duplicate rows when a response is lost and retried. A save error keeps the draft and never reports success. There are no email or identity fields.

For local testing:

```sh
pnpm --dir sites/runtime exec wrangler d1 migrations apply DB --local
pnpm --dir sites/runtime dev
```

Local test entries stay in `.wrangler/`, which is excluded from the deployment archive and Git. Production migrations are applied by Sites when the saved version is deployed. Local persistence checks do not establish production persistence.

## Distance and provenance

The authored shot has horizontal landing coordinates `(142,16)` metres. The near river edge is `x=128`: 423 feet along that direction. The shown splash is 469 feet away. Both are rounded horizontal model measurements. A sampled architecture-clearance check is not a physical baseball simulation, wind analysis, or guarantee of feasibility.

The social image uses the current north camera, a projected version of that same flight and a 1200×630 layout. Its distinct image URL replaces the old OG thumbnail; individual social platforms may retain their own cached cards.

The How it was made page includes the specified model credits, with the first-person maker disclosure directly before credits and disclosures. Its usage snapshot covers locally identifiable Railyards sessions from September 5–8 through the stated cutoff, including subagents. Unrelated work is excluded. Cloud-only and missing logs remain outside the count; no model identity is guessed from an internal alias. Raw conversation logs are not published.

The wider 23-finding architectural audit remains open. The release alignment and visible square-corner correction do not close that audit.
