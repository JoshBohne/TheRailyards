# The Railyards

Editable Blender reconstruction of AECOM’s White Sox Railyards concept in Chicago. This is an independent fan study with inferred architecture, not an official design or an engineering model.

## Current work

Fable’s V4–V7 work is preserved in the `v7-baseline` tag. It includes the right-field scoreboard and structure corrections, lake geography, expanded skyline, gatehouse, concourses and night views. V8 adds a separate night preset with individual landmark windows. The generators remain in `railyards-v4/` because later iterations build on that scene; legacy object names are functional.

- [Current model and rebuild commands](railyards-v4/README.md)
- [V8 scope and verification](docs/V8-HANDOFF.md)
- [Spatial issue ledger](railyards-v4/ISSUE-LEDGER.md)
- [Original V4 priorities](docs/FABLE-5.1-HANDOFF.md)
- `site/`: Fable’s fan website and build script; its historical version/cost copy has not yet been refreshed for V8.
- `railyards-v3/`: preserved baseline, also tagged `v3-baseline`.
- `reconstruction-references/`, `reference-audit/`: artwork, source data and historical research. Older completion labels are not visual acceptance.

## Review locally

From the repository root:

```sh
python3 -m http.server 8852 --bind 127.0.0.1
```

Open [the V8 comparison](http://127.0.0.1:8852/railyards-v4/review/v8.html), [Fable’s website](http://127.0.0.1:8852/site/), or [the V4–V7 review gallery](http://127.0.0.1:8852/railyards-v4/review/). Generated renders must be rebuilt or restored from a delivery archive first.

## Repository and artifacts

The private repository is [JoshBohne/TheRailyards](https://github.com/JoshBohne/TheRailyards). Git tracks generators, specifications, reference assets and documentation. Generated Blender scenes, renders, caches and host-specific MCP configuration stay outside Git. A clone therefore requires rebuilding or restoring the scene/render archive from the repository’s Releases.

The original V1–V3 deliveries remain preserved in the original workspace. V7’s saved scene is retained locally under `work/v7-baseline/`; V8 saves separately as `railyards-v4/railyards-v8.blend`.

Reference artwork remains attributed to its creators; inclusion as reference is not a claim of ownership or a redistribution license.
