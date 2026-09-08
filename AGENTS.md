# The Railyards agent instructions

Before continuing the model, read `docs/FABLE-5.1-HANDOFF.md`. It contains the user's V4 priorities, verified defects and visual acceptance criteria.

Preserve `railyards-v3/` as the baseline. Start changes in a separate `railyards-v4/` copy on a feature branch. Update the copied generators' scene/output names before executing builds; several legacy R2/D2 object names are functional and should remain stable unless deliberately migrated.

Keep source-backed geometry, geographic data and inferred architecture distinguishable. When changing geography, inspect `scene-spec.json` and `skyline-buildings.json` together: coordinate registration is approximate and legacy metadata can be stale. When changing a component, inspect its current generator and actual saved render; old inventory completion labels are not visual approval.

Required tool setup for every task in this repository:

- Blender CLI for scripts, batch renders, and exports.
- Blender MCP for live scene inspection and edits inside Blender.
- Computer use for visual review and UI actions that CLI or MCP do not expose.

Keep a visible live review surface open while changing geometry. Publish small fixed-camera previews as each bounded edit is ready, so Josh can watch and correct the work before a full render/export pass. Show source/current and before/after views; label stale frames while a new render is running. Use actual rendered comparisons for acceptance. Reflect live edits in generators so a clean rebuild preserves them. Keep camera settings fixed during geometry comparisons. Serialize writes to shared scenes and render files if delegating.

Generated scenes, renders and caches belong outside Git. Include the scene and visual evidence in each deliverable package. Completion means the requested visible problems are resolved across the relevant views, with remaining uncertainty stated.
