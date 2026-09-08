# V14 left-field final correction

The LF return now has two exposed seating banks instead of three. The lower bank is deeper and the upper bank projects slightly over its rear. Two open box levels and a roof terrace replace the removed exposed seating tier.

The initial interpretation raised the pavilion too far and introduced a large bright glass block. That experiment was rejected after comparison with the AECOM B4/B6/A3 renderings and independent reassessment. The final correction removes that glass block, lowers and compresses the gallery stack, and replaces the repeated tall gabled volumes with a dominant sloping central roof, a lower dining shelter and a shallow rear roof. The accepted south extension and RF seating remain in place.

These are source-guided proportions, not surveyed dimensions. Gallery elevations, hidden roof slopes, supports and roof footprints remain inferred. The rounded LF seating outline and exact roof-to-pavilion fit still differ from the concept art; this delivery does not close those fidelity findings or the wider 23-item audit. Work ends here at the user's request.

The rejected experiment is preserved locally in `work/audit-fixes-v14/lf-verbal-study/`. The pre-LF baseline remains `work/audit-fixes-v14/before-lf-two-banks.blend`. Current evidence is in `railyards-v4/review/v14/lf-final/`; no new interactive export or hosted deployment is claimed.

## Validation

Saved scene SHA256: `d84d198ce70ec941929f96757f96baeefd8c5c36d07c235bdc9406aa0f4a59ee`. All 33997 active seat placements pass the sampled architectural floor, foot, body and headroom checks. All 565 samples on the park arcade-to-field route pass. This is not a chair-mesh pair test or coverage of every stadium route. The main-bowl chair-contact finding remains open.

The V13-based generator was rebuilt. Two final unsupported edge chairs were omitted in the saved scene and the same omissions were reflected in the generator, followed by reopening and rerunning the full architectural placement check. Python compilation and patch whitespace checks pass. Four final native views were rendered from the saved scene.
