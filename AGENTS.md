# The Railyards agent instructions

Before continuing the model, read `docs/FABLE-5.1-HANDOFF.md`. It contains the user's V4 priorities, verified defects and visual acceptance criteria.

Preserve `railyards-v3/` as the baseline. Start changes in a separate `railyards-v4/` copy on a feature branch. Update the copied generators' scene/output names before executing builds; several legacy R2/D2 object names are functional and should remain stable unless deliberately migrated.

Keep source-backed geometry, geographic data and inferred architecture distinguishable. When changing geography, inspect `scene-spec.json` and `skyline-buildings.json` together: coordinate registration is approximate and legacy metadata can be stale. When changing a component, inspect its current generator and actual saved render; old inventory completion labels are not visual approval.

Use Blender CLI for repeatable builds/renders, Blender MCP for live scene inspection and edits, and actual rendered comparisons for acceptance. Reflect live edits in generators so a clean rebuild preserves them. Keep camera settings fixed during geometry comparisons. Serialize writes to shared scenes and render files if delegating.

Generated scenes, renders and caches belong outside Git. Include the scene and visual evidence in each deliverable package. Completion means the requested visible problems are resolved across the relevant views, with remaining uncertainty stated.
