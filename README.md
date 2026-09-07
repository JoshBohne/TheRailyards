# The Railyards

Editable Blender reconstruction of AECOM’s White Sox Railyards concept in Chicago. This is an independent fan study with inferred architecture, not an official design or an engineering model.

## Current work

Fable’s V4–V7 work is preserved in the `v7-baseline` tag. It includes the right-field scoreboard and structure corrections, lake geography, expanded skyline, gatehouse, concourses and night views. V8 adds a separate night preset with individual landmark windows. V9 corrects the left-center arrival terrace and landmark forms, and adds two browser sites with four rendered experience films. The generators remain in `railyards-v4/` because later iterations build on that scene; legacy object names are functional.

- [V9 scope, rebuild and verification](docs/V9-SCOPE.md)
- [Two sites: build and serve](sites/README.md)
- [Current model and rebuild commands](railyards-v4/README.md)
- [V8 scope and verification](docs/V8-HANDOFF.md)
- [Spatial issue ledger](railyards-v4/ISSUE-LEDGER.md)
- [Original V4 priorities](docs/FABLE-5.1-HANDOFF.md)
- `sites/public/` and `sites/review/`: current public preview and working review site.
- `site/`: preserved earlier Fable draft.
- `railyards-v3/`: preserved baseline, also tagged `v3-baseline`.
- `reconstruction-references/`, `reference-audit/`: artwork, source data and historical research. Older completion labels are not visual acceptance.

## Review locally

Build and serve the two independent sites using [these commands](sites/README.md). Open [the working review](http://127.0.0.1:8853/) or [the public preview](http://127.0.0.1:8854/). These are local previews, not a public deployment. Release archives contain self-contained copies with all media.

Earlier V8 and V4–V7 review pages remain under `railyards-v4/review/`.

## Repository and artifacts

The private repository is [JoshBohne/TheRailyards](https://github.com/JoshBohne/TheRailyards). Git tracks generators, specifications, reference assets and documentation. Generated Blender scenes, renders, caches and host-specific MCP configuration stay outside Git. A clone therefore requires rebuilding or restoring the scene/render archive from the repository’s Releases.

The original V1–V3 deliveries remain preserved in the original workspace. V7’s saved scene is retained locally under `work/v7-baseline/`; V8 saves separately as `railyards-v4/railyards-v8.blend`.

Reference artwork remains attributed to its creators; inclusion as reference is not a claim of ownership or a redistribution license.
