# V13 outfield correction

V13 applies to the preserved V12 static scene. It restores three seating tiers
in front of the left-field pavilion, carries lower right-field seating north
to the foul pole, and adds three angular platforms connected to the clock
tower. The new upper seating east of the tower from the rejected first pass
is absent. The park entrance now passes through real arch openings and a
continuous concourse into a stair through the left-center seating bank.

The user's north-aerial close-ups establish the terrace stack, open supports,
seating placement, and recessed pavilion. Platform footprints, floor heights,
row counts, hidden supports, and circulation dimensions are inferred. This
revision is a visual reconstruction, not measured architecture. The close-up
is the primary review view; passing geometry checks does not establish an
exact match to the artwork.

## Rebuild and inspect

From the repository root, with the preserved `railyards-v4/railyards-v12-static.blend`:

```sh
BLENDER=/Applications/Blender.app/Contents/MacOS/Blender
"$BLENDER" -b railyards-v4/railyards-v12-static.blend --python-exit-code 1 --python railyards-v4/build_outfield_v13.py
LABEL=platforms VIEWS=corner,tower,lf,entrance,north "$BLENDER" -b railyards-v4/railyards-v13-static.blend --python-exit-code 1 --python railyards-v4/render_outfield_v13.py
"$BLENDER" -b railyards-v4/railyards-v13-static.blend --python-exit-code 1 --python railyards-v4/verify_outfield_v13.py
"$BLENDER" -b railyards-v4/railyards-v13-static.blend --python-exit-code 1 --python railyards-v4/build_replay_v10.py -- --version 13
pnpm --dir sites/replay test
pnpm --dir sites/replay build
```

The static scene, animated scene, render PNGs, and detailed receipts stay
outside Git. The input checksum and generated seat counts are written to
`railyards-v4/review/v13/build-receipt.json`. Checks cover 417 passage samples,
new-seat floors and headroom, absence of rejected river-side upper seats,
stable browser seat IDs and rows, and exported ball-flight collisions.

## Watch along

`tools/live-review/serve.py` serves an operator-authored JSON state file:

```sh
python3 tools/live-review/serve.py --state work/outfield-v13/live.json --port 8863
```

Each entry under `views` supplies a `label` and `current`, optional `before`,
and optional `source` objects with local `path` and `label` fields. Set
`requested_after` to the update's Unix timestamp to mark older frames stale.
The browser automatically refreshes saved renders. HTTP clients cannot select
arbitrary workspace paths. The server binds only to localhost.

The current review uses `http://127.0.0.1:8863/`; the built interactive model
is served separately at `http://127.0.0.1:8864/`. Public-site galleries and
movies require a separate refresh and deployment before they represent V13.
