---
name: blender-workflow
description: How agents work on the Railyards Blender model — which tool tier to use (Blender CLI, Blender MCP, computer use), the exact commands, and how to publish progress to the live dashboard Josh watches. Use for any task that builds, edits, renders, inspects or reviews the scene.
---

# Blender workflow for The Railyards

Three tiers. Pick the cheapest one that can do the job; escalate only when it cannot.

| Need | Use | Why |
|---|---|---|
| Rebuild from generators, batch renders, exports, anything reproducible | **Blender CLI** (`/Applications/Blender.app/Contents/MacOS/Blender -b …`) | Deterministic, logged, re-runnable; never touches the GUI scene |
| Inspect the live scene, measure, small in-place edits, viewport screenshot | **Blender MCP** (`mcp__blender__*`) | Live state without a full rebuild; `execute_blender_code` for bpy |
| Something only the GUI exposes (modal operators, viewport shading, add-on panels, visual sanity of the UI itself) | **Computer use** (`mcp__computer-use__*` on Blender.app) | Last resort; slow and non-reproducible |

Rules that follow from `AGENTS.md`:

1. **Confirm the scene before touching it.** Two GUI instances are often open on different ports. `mcp__blender__get_scene_info` must report the scene you intend (`Railyards v4` family). The MCP session uses `BLENDER_PORT` from `.mcp.json`; the SessionStart hook prints which port holds which scene. Do not edit through MCP if the name is wrong.
2. **Live edits go back into generators.** Anything changed through MCP must be reflected in the `railyards-v4/r*_*.py` / `build_*.py` generator so a clean CLI rebuild reproduces it.
3. **Fixed cameras for every comparison.** Use the persisted review cameras (`railyards-v4/review-cameras.json`, `render_review.py`) so before/after images differ only by geometry.
4. **One writer per scene file.** Serialise renders and saves; do not run two CLI renders against the same `.blend` at once.
5. **Publish as you go.** Every bounded edit ends with a `dash.py` update (below). Josh watches the dashboard, not the transcript.

## Commands

Rebuild the current chain (writes stage files under `railyards-v4/work/`, never overwrites preserved scenes):

```sh
cd railyards-v4 && ./build_v12.sh
```

Render the fixed review cameras with dashboard progress. The dashboard advances one view per `Saved:` line, so `RAILYARDS_REVIEW_VIEWS` and `--views` must be the same list in the same order:

```sh
RAILYARDS_REVIEW_VIEWS=north_park_entry,roosevelt_bridge_west \
python3 tools/live-review/dash.py run --views north_park_entry,roosevelt_bridge_west --blend railyards-v12.blend -- \
  /Applications/Blender.app/Contents/MacOS/Blender -b railyards-v4/railyards-v12.blend --python-exit-code 1 \
  --python railyards-v4/render_review.py
```

Environment knobs for `render_review.py`: `RAILYARDS_REVIEW_VIEWS`, `RAILYARDS_LABEL`, `RAILYARDS_OUTDIR`, `RAILYARDS_WIDTH`, `RAILYARDS_SAMPLES`, `RAILYARDS_PRESET`.

Talk to the add-on socket directly when the MCP server is not registered:

```sh
BMCP_PORT=9877 python3 railyards-v4/tools/blender_mcp_client.py get_scene_info
```

Start a GUI instance on the scene with its MCP socket on 9877:

```sh
/Applications/Blender.app/Contents/MacOS/Blender railyards-v4/railyards-v12.blend --python railyards-v4/tools/start_live_mcp.py
```

Before any computer-use action, take `mcp__blender__get_viewport_screenshot` first; it is cheaper and usually enough.

## Dashboard publish sequence

The dashboard is `tools/live-review/serve.py` (open it with `preview_start` name `live-dashboard`, http://127.0.0.1:8863/). State lives in `work/live/state.json`, gitignored. Drive it only through `tools/live-review/dash.py`:

```sh
D="python3 tools/live-review/dash.py"
$D reset                                                             # new session: clears everything except per-view timings
$D note "What this session is doing, one sentence"
$D task add "Each acceptance item from the brief" --id short-id      # once, at the start
$D view set rf-corner --label "RF corner" --before path/before.png --source path/source.jpg
$D queue add rf-corner lf-terrace                                    # what will render, in order
$D run --views rf-corner,lf-terrace -- <blender command>             # progress + ETA come from Cycles stats
$D task done short-id --evidence railyards-v4/review/v15/rf-corner.png
$D version snapshot "V15 draft 2" --blend railyards-v15.blend --note "what changed"
```

`view set --current` is only needed when a render was produced outside `dash.py run`. `view expect <key>` marks a view stale while you re-render it by hand. `dash.py show` prints the state for your own check.

Snapshot a version after every bounded edit that Josh should be able to compare later; snapshots copy the current images under `work/live/versions/` and record the git commit.

## Delivery

Completion means the requested visible problems are resolved in the fixed-camera renders, the checklist is fully `done` with evidence, a final version snapshot exists, and generators reproduce the scene from a clean CLI build. State remaining uncertainty in the dashboard note.
