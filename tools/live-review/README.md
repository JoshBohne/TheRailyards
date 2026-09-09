# Live agent dashboard

A local site Josh keeps open while an agent works on the Blender model. Four tabs: **Agent** (what is rendering now with an ETA, the queue, checklist, fixed-camera views with before/after and source comparison, version snapshots, activity, commits), **Review** (every finished render waits here for a thumbs up or down with feedback; the agent reads it with `dash.py review list`), **Gallery** (every current render with one-click Copy for pasting into chat) and **Sources** (references, maps, mockups and data we did not create, with credits).

```sh
python3 tools/live-review/serve.py            # http://127.0.0.1:8863/, state work/live/state.json
python3 tools/live-review/dash.py --help      # agent CLI that mutates the state
```

- `serve.py` only reads the state file and the image paths recorded in it; HTTP clients never supply paths.
- `dash.py` is the only writer. Mutations are serialised through a lock file and saved atomically; each one appends to the activity feed.
- `dash.py run -- <blender command>` wraps a CLI render and streams Cycles `Sample x/y` / `Remaining` stats into the progress bar. Without live stats the ETA falls back to the average of the last three renders of that view.
- Older V13/V14 `live.json` files (`note` + `views` only) still load: `serve.py --state work/outfield-v13/live.json`.
- `dash.py gallery add <dir> [--glob] [--prefix] [--label]` registers every image in a directory as a view, so the All current renders grid holds everything Josh might copy into chat. Files named `before-*` register as the before image.
- `POST /review` is the only write the page makes; the server appends to `work/live/reviews.json` and logs an activity event. `dash.py review list --pending` shows verdicts the agent has not acted on and views still waiting for Josh.
- `dash.py source scan <dir> --kind render --credit "…"` registers reference material for the Sources tab (served at `/source/<id>`).
- Snapshots (`dash.py version snapshot`) copy the current view images into `work/live/versions/<id>/` and record the short git hash.

Agents get the publish sequence from `.claude/skills/blender-workflow/SKILL.md`.
