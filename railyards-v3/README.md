# White Sox Railyards — reconstruction v3

An editable, source-driven Blender reconstruction of the September 2026 AECOM concept. V1 and v2 remain preserved in their original locations.

Open `railyards-v3.blend` in Blender, or open `index.html` through a local HTTP server for the three reference comparisons and interior views. All displayed model images are actual Blender renders.

The scene includes the stadium bowl and four seating levels, separate outfield banks, canopy and light gantries, clock tower, arched exterior and river arcade, two constructed video boards, regulation-scale field details, pavilions and rooftop activity, medical and entertainment buildings, raised outfield park, lower riverwalk, rail links, Roosevelt bridge, boats and road activity. Source-visible future buildings, the soccer stadium, southern rail bridges and the finite outfield skyline are separate native layers.

Read [SOURCE-AND-ASSUMPTIONS.md](SOURCE-AND-ASSUMPTIONS.md) before using this as a design reference. Concept artwork does not establish surveyed dimensions, hidden structure, approved construction phases, or an exact digital twin. North and south covered-link alignments remain inconsistent under the shared camera fit; explicitly named source-view collections preserve those interpretations. The render presets select those collections. Interior views use the north-link configuration and hide inferred future development.

## Rebuild

Tested with Blender 5.2.1 LTS. Run these from this folder, replacing `blender` with the path to your Blender executable if needed:

```sh
blender -b --python build_blockout.py --python build_detail.py --python add_interior_cameras.py --python finalize_scene.py
blender -b railyards-v3.blend --python verify_scene.py
RAILYARDS_LABEL=final RAILYARDS_WIDTH=1800 RAILYARDS_SAMPLES=64 blender -b railyards-v3.blend --python render_scene.py
RAILYARDS_WIDTH=1800 RAILYARDS_SAMPLES=64 blender -b railyards-v3.blend --python render_interior.py
blender -b railyards-v3.blend --python render_southern_rail.py
```

Keep the adjacent `reconstruction-references` folder with the three canonical working images. The build reads the north image only to assign native window-tone materials; it does not project photography onto the model. All rendered surfaces, logos, crowds and plants are native meshes, curves, procedural materials or instances. The final saved scene requires no externally linked source images.

`scene-spec.json` preserves the calibrated coordinate frame and cameras. The `r3_*.py` modules own the revised components. Per-component JSON files preserve source points and uncertainty; some small source traces are kept directly beside their generator code. `saved-scene-verification.json` records the reopened file checks. Render receipts identify the saved scene used for each image.

CLI scripts handle repeatable builds, renders and packaging. The live scene is inspected through Blender MCP; browser comparison is used for visual review. Successful file checks do not constitute whole-scene visual accuracy.
