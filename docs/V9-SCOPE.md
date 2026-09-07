# V9: rendered experiences and two web surfaces

The user wants browser-delivered scenes that add insight beyond the three published renderings. Blender is an authoring tool, not the viewing interface.

## Web destinations

- `sites/review/`: working model versions, source comparisons, issue status, fixed-camera evidence and the latest rendered scenes.
- `sites/public/`: fan-facing preview, organized around arrival from Roosevelt, entering at left-center, the river from a boat, a river home-run distance study, and recognizable Chicago landmarks. Native video controls and still views, with no need to navigate a 3D model.
- Preserve Fable’s `site/` as the earlier draft and source/process archive. The new public draft does not publish old token costs or uncertain completion claims.

Visual direction: preserve the draft’s charcoal, white and amber identity and condensed sports typography; put actual rendered scenes first. Public design variance 6, motion intensity 4, visual density 3. The review surface prioritizes comparisons and readable status over marketing layout.

## Model scope

V8 baseline: `e187b58`. Preserve its saved file. V9 saves as `railyards-v4/railyards-v9.blend`.

- Left-center: fill the source-visible front arrival terrace missing from the rear-landing-only implementation. Retain the park grade. The connection, retaining edges, pergola and stairs require rendered acceptance; details remain inferred.
- Bowl concourses: replace solid boxes at vomitory entrances with open-front tunnel geometry.
- Skyline: Willis becomes nine square tubes with staggered heights and twin antennae; St. Regis gains alternating frustums; Two Prudential gains a pyramid and spire within its existing total height. Individual proportions remain simplified. Geographic coordinates are unchanged.

## Primary skyline references

- [SOM: Willis Tower](https://www.som.com/projects/willis-tower-formerly-sears-tower/): nine 75-foot square tubes and staggered terminations; black aluminum and bronze-tinted glass.
- [Studio Gang: St. Regis Chicago](https://studiogang.com/projects/vista-tower/): three interconnected volumes composed of alternating 12-story frustums.
- [CTBUH: Two Prudential Plaza](https://www.skyscrapercenter.com/building/two-prudential-plaza/489): overall height and reference imagery for crown and spire.

- [MKA: St. Regis](https://www.mka.com/projects/st-regis-chicago/): 100/75/50-story interconnected volumes. Their shorter modeled heights use proportional estimates.
- [CTBUH case study by the project team](https://global.ctbuh.org/resources/papers/4218-Gang_VistaTower.pdf): floor-plate width revised to 24.7 m at the narrow end, 27.4 m at the wide end. This corrects the first V9 trial’s exaggerated taper.

## River distance study

Use the actual modeled river edge and field datum, show horizontal distance from home plate, and distinguish the illustrated trajectory from an aerodynamic prediction. No claim of an official future fence or river distance. Keep the path visible over the stadium and inspect it against the modeled board and structures.

## Rebuild and delivery

The verified V9 build reran the complete architectural detail generator on the preserved V8 scene, then saved V9 separately. The base blockout generator was not rerun. From `railyards-v4/`, using Blender 5.2.1 LTS:

```sh
blender -b railyards-v8.blend --python build_detail.py --python finalize_v9.py
blender -b railyards-v9.blend --python verify_scene.py
RAILYARDS_LABEL=v9 RAILYARDS_WIDTH=1400 RAILYARDS_SAMPLES=32 blender -b railyards-v9.blend --python render_scene.py
RAILYARDS_SAMPLES=48 blender -b railyards-v9.blend --python render_experiences.py
RAILYARDS_ENGINE=BLENDER_EEVEE RAILYARDS_MOTION=motion RAILYARDS_FRAMES=192 RAILYARDS_VIEWS=arrival,left_center,boat blender -b railyards-v9.blend --python render_experiences.py
blender -b railyards-v9.blend --python render_river_study.py
```

Build and serve the sites using `sites/README.md`. Films are 1600×900 at 24 fps: three eight-second route previews and one seven-second river illustration. The movies use Eevee; still comparisons use Cycles. The release contains the saved scene, rendered evidence, both self-contained websites and verification receipts. Raw frame caches are excluded from the package.

## Verification

- Reopened saved V9: required collections present, no missing external images, finite mesh coordinates, regulation infield dimensions, 40 cameras. Live Blender MCP confirmed V9 and all six new experience cameras with no unsaved changes.
- Both walking paths were sampled at 101 positions against actual deck surfaces; camera height stayed between 1.5 and 1.9 m. The left-center route curves around the restaurant floor.
- The illustrated river trajectory was checked over 198 segments against static modeled structures. No collisions remained. Along this chosen line, water begins about 429 ft from home plate; the illustrated splash is 476 ft away. Neither number is an official dimension or flight prediction.
- Browser checks passed at desktop and 390 px mobile widths: all four movies play, version/camera selection and comparison controls work, units and theme switch, review images load, and no page/network errors or horizontal overflow were observed.
- Local mobile Lighthouse: performance 78, accessibility 100, best practices 100, SEO 100. Largest contentful paint 6.4 s under its throttling; total blocking time and layout shift both zero. This is a local audit, not hosted performance evidence.
- Python compilation and Git whitespace checks passed. These checks establish functioning artifacts; they do not establish visual approval.

## Still open

The restaurant/terrace junction, source-inferred levels, close-up people, materials and some structural details still need refinement. Skyline forms are simplified; isolated building comparisons deliberately remove occluders and are not seat sightlines. The public site is a preview of the experience format, not a final photoreal or publicly deployed release. V3 and V8 remain preserved.
