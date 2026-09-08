# Independent phase-4 shaft-protection follow-up

Frozen authority: `phase4-review.blend`, SHA-256 `5a738d598569600a73bdab790536f5077f02cd2acff1c23e42da4651b413165c`.

**The previously confirmed 18 unprotected lift-well edge locations now have barriers, and all 3,583 expanded tower route probes remain clear. Accept this bounded correction.** This does not close all A05 architecture/source findings or A09 chair collisions.

## Independent results

| Check | Phase 3 | Phase 4 |
| --- | --- | --- |
| North/south/east lift-well edge at six upper levels | 18 locations without barriers | 18 locations protected |
| Horizontal barrier rays at 0.6 and 1.0 m | 36 missing barrier hits | 36 barrier hits |
| Expanded tower route floor/head/body probes | 3,583 points, zero failures | 3,583 points, zero failures |

North-facing landing doors are hit as `D2_V14 Tower lift enclosure metal` (12 rays). South/east enclosure surfaces are hit as `D2_V14 Tower lift enclosure glass_mid` (24 rays). The z47.6 top-floor checks pass as well, so the new protection extends above that landing at the tested heights.

The route test is the same independent phase-3 extension: submitted paths plus north-entry/stair joins, west portals around the core, intermediate stair turns, and ±0.4 m lateral offsets on selected treads, entries, terraces, upper stair/approach and quay arrival. It preserves the 0.3 m body-ray envelope. The new enclosure has not obstructed those sampled circulation paths.

Evidence is in `independent-phase4/`: `shaft-edge-diagnostics.json`, `dense-tower-routes.json`, the two reproducible scripts and their logs. The scripts operate on the frozen scene and do not save it. The shaft diagnostic retains the vertical drop measurement behind each enclosure; those drops are now separated from the adjacent floor by the confirmed barriers.

## Acceptance boundary

This closes the specific modeled open-well fall paths demonstrated in phase 3. It does not certify glass/door strength, operation, lift equipment, fire strategy, capacity or accessibility. Closed static doors depict a protected unused shaft; they are not proof of a functioning elevator.

The follow-up did not rerun seat collision checks or the complete source comparison. The documented chair-pair collisions, terrace/source fidelity caveats, LF pavilion, bridges and other unresolved audit findings remain open. No full A05 or A09 acceptance is implied. The frozen scene was left unchanged; only this report and `independent-phase4/` were written.
