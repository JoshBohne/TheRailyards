# White Sox Railyards — reconstruction v4

Editable, source-driven Blender reconstruction of the September 2026 AECOM concept. V4 starts from the preserved V3 generators (`../railyards-v3/`) and corrects spatial relationships, structure and geography before further surface detail. Read `ISSUE-LEDGER.md` for the before/after record and `../docs/FABLE-5.1-HANDOFF.md` for the brief.

What V4 and V5 change (V5 = skyline pass, see ISSUE-LEDGER.md):

- **RF scoreboard** re-anchored from a three-camera triangulation, rotated 92°, 36×18.5 m, on lattice pylons behind the outfield wall (`scene-spec.json` `rf_scoreboard`, `r3_scoreboards.py`, `r3_outfield.py`).
- **RF / clock-tower structure**: podium, tier-profile end wall, tower link block, river arcade, corner terraces (`r4_rf_structure.py`); ground datum fix in `r3_public_realm.py`.
- **Lake Michigan and lakefront**: USGS NHD shoreline clipped into the scene, water at z0.5, Grant Park / Museum Campus, 238 OSM near-South-Loop buildings (`r4_geography.py`, `lake-michigan-local.json`, `near-south-loop-context.json`); the east background box in `r2_context.py` is gone.
- **Skyline**: NEMA, One Museum Park (+ Museum Tower), The Grant, 1000M, 311 South Wacker, Chicago Board of Trade, Franklin Center as silhouettes (`r4_skyline_south.py`, `skyline-v4-additions.json`); legacy landmarks shifted by the audited registration (`r4_geo.py`).
- **Review cameras** persisted in the scene (`add_review_cameras.py`, `review-cameras.json`, `render_review.py`) and plan evidence (`make_plan_evidence.py`).

Legacy `R2_` / `D2_` object prefixes are functional and unchanged. The scene is named `Railyards v4`.

## Rebuild

Tested with Blender 5.2.1 LTS (`/Applications/Blender.app/Contents/MacOS/Blender`). From this folder:

```sh
blender -b --python build_blockout.py --python build_detail.py --python add_interior_cameras.py --python add_review_cameras.py --python finalize_scene.py
./run_v4_renders.sh
```

`run_v4_renders.sh` verifies the saved file (`verify_scene.py`), writes the RF plan evidence, then renders the eight review cameras (`review/v4-*.png`), the four interior views, the three fixed source comparisons (`final-*.png`) and the southern rail close-up. `RAILYARDS_WIDTH` / `RAILYARDS_SAMPLES` scale the final passes.

Control run (unchanged V3 generators through the V4 chain) is in `review/control-*.png` and `review/control-interior/`; copied V3 and V2 deliverables are in `baseline-v3/` and `baseline-v2/`. Generated `.blend` files, renders, logs and `work/` stay outside Git.

Keep `../reconstruction-references/` adjacent: the north image is read for window tones and the source overlays reference the three artworks.

## Files

- `r4_geo.py` — single geographic registration (formula + 33 m X), datums, lake loader, clipping helpers.
- `r4_geography.py`, `r4_skyline_south.py`, `r4_rf_structure.py` — new V4 builders, called from `build_detail.py`.
- `review/rf-plan.svg`, `review/rf-plan-evidence.json`, `review/rf-source-overlays.html` — labelled plan and clearance proof.
- `review/index.html` — before/after gallery (open through a local HTTP server from the project root).
- `SOURCE-AND-ASSUMPTIONS.md`, `ELEMENT-REVIEW.md` — V3 records, with a V4 addendum in the former.
