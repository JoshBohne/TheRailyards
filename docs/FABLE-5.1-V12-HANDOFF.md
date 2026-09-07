# Fresh Fable 5.1 session — V12 stadium proportions

Josh explicitly requests a fresh chat and a complete implementation pass, not another review-only report. This document is the current brief; the older V4 handoff provides history, not the current baseline.

## User's concerns and scope

The stadium interior and outfield still look awkward and disproportionate. Audit and fix the whole connected stadium composition, especially:

1. Third-base foul line, dugout and adjacent seating: the line appears too close to the dugout. Measure the actual plan geometry, identify both foul lines from home plate, inspect dugout placement/length/depth, foul territory, warning-track/boundary transitions, field level and front rows. Preserve regulation infield geometry; do not stretch the diamond to conceal an incorrect bowl or dugout.
2. Entire outfield: reconcile wall, batter's eye, warning track, seating banks, boards, restaurant, concourses, stair runs, rails, supports and gaps. Avoid oversized blank masses, arbitrary narrow bridges, implausible slopes, floating ends and mismatched heights. Reconsider V11's inferred architecture when the renderings disagree.
3. North aerial deck, raised Roosevelt approach and left-center: compare source north aerial, bridge rendering and actual pedestrian views. Make the plaza/restaurant roof/bleacher/pavilion transition read convincingly at aerial and human scale. Continuous floor probes alone do not establish good proportions.
4. Right-field corner: check the foul pole, board, wall, bleachers, tower end, concourse and river edge together. Resolve the entire footprint and section, rather than moving one component until one camera looks acceptable.
5. Clock/watchtower flag: inspect its actual flag, pole, roof mounting, offsets/orientation and support. Josh says it does not sit correctly on the tower. Correct the generator and saved scene; show a close-up and wider context.
6. Catch other visibly wonky interior proportions while doing this pass. The outcome is a coherent stadium, with honest remaining uncertainty, not a checklist of instantiated objects.

## Central repository and starting point

- Repository: https://github.com/JoshBohne/TheRailyards (private).
- Root checkout: /Users/joshbohne/Developer/TheRailyards.
- Latest model/code baseline: branch `feat/v11-outfield-circulation`, model implementation commit `ee3ddd9f7ce51baba84a421f576f8b53586ae381`, PR #1. This handoff is committed on that branch after the implementation. Fetch origin before choosing the new branch; DO NOT start from stale main (V10) or the old Claude V4 worktree.
- Create a fresh feature branch/worktree from the current remote V11 branch. Preserve all existing worktrees and uncommitted work; do not reset or clean the old Claude worktree.
- V11 backup: https://github.com/JoshBohne/TheRailyards/releases/tag/v11-circulation. Includes public site, review site, separate static/animated scenes, native and browser evidence, SHA-256 sums.
- Saved scenes locally: `railyards-v4/railyards-v11-static.blend` and `railyards-v4/railyards-v11.blend`. Make separate V12 output names before building. Keep V3/V9/V10/V11 intact. Generators stay in `railyards-v4/`; R2/D2/R10 object names are functional.

## Read and inspect first

Read AGENTS.md, `docs/V11-CIRCULATION.md`, `docs/FABLE-5.1-HANDOFF.md`, the relevant current generators and `railyards-v4/ISSUE-LEDGER.md`. Use current geometry and renders as authority over old completion labels. Inspect `scene-spec.json` and `skyline-buildings.json` together if geography/registration changes.

References are in `reconstruction-references/`: AECOM north and south aerials, user bridge view and the site plan. Compare their original full-resolution files; projected traces can use different source sizes. V11 native source comparisons are `railyards-v4/v11-{north,south,bridge}.png`. Pedestrian/stair images and the previous Fable reviews are in `railyards-v4/review/v11/`, including `FABLE-REVIEW.md` and `FABLE-CIRCULATION-REVIEW.md`.

Relevant owners include `build_blockout.py`, `r2_seating.py`, `r3_bowl_details.py`, `r3_outfield.py`, `r3_scoreboards.py`, tower/envelope generators, `r3_public_realm.py`, `r11_circulation.py` and `build_circulation_v11.py`. Search for the actual field/dugout/flag builders rather than assuming historical names remain accurate. Objects are batched by material, so one mesh may contain unrelated pieces.

V11 improved entrance continuity, added arches and stairs and lowered the replay's illustrative flight. It passed 163 arrival floor/body samples, exported collision checks and browser tests. Josh has now explicitly rejected the overall proportions as sufficiently convincing: these checks are regression evidence, NOT architectural acceptance.

## Working method and acceptance

Use Blender CLI for reproducible saved builds and renders; use Blender MCP for live scene inspection. Port 9877 last held clean V11. Port 9876 held unsaved V3 work: do not replace it. Inspect current dirty/file state before touching either instance. Reflect all geometry changes in generators.

First establish a dimensioned overhead plan and relevant sections covering field/dugouts, the full outfield, Roosevelt/left-center and the RF/tower corner. State known baseball geometry separately from inferred architectural dimensions. Cross-check source proportions with fixed calibrated cameras and actual stadium-level views. Fix geometry, not just camera framing or overlays. Keep source/model and before/after evidence available early while working.

Then implement and iterate through the entire scope. Reopen the saved V12 scene and inspect every affected view. Show: three fixed source comparisons; home/third-base/upper-deck interior views; left-center and RF close-ups from both levels; Roosevelt approach; clock-tower flag close-up and context. Check plausible clearances and connected supports without claiming engineering certification. Preserve live-edit changes in the build chain.

The main deliverable is the website, not a request for Josh to navigate Blender. Current main site is http://127.0.0.1:8854/, review is http://127.0.0.1:8853/, and replay is /replay/ on the main site. Refresh model export, replay cameras/flight collision checks if geometry affects them, native films/stills, and source/before-after comparisons. Keep the shared timeline and all modeled seat IDs valid. Use isolated preview outputs/ports while working; only replace shared artifacts in a serialized final build.

Run relevant saved-scene, geometry and browser checks. `pnpm --dir sites/replay test`, production build, and the repeatable browser capture command are documented in `docs/V11-CIRCULATION.md`. Blender commands must use `--python-exit-code 1`. Inspect captured images; successful rendering is not proof the stadium looks right.

Push source/spec/docs/evidence summaries to this same Railyards repository, open/update a PR, and upload generated scenes and visual evidence as a private versioned release with checksums. Generated scenes, frames, caches and node_modules stay outside Git. Keep changes centrally recoverable throughout substantial phases. Deliver direct links to the updated main/review sites, PR and backup, and state any unresolved proportions honestly. Continue through implementation and verification without stopping at a review or asking whether to continue.
