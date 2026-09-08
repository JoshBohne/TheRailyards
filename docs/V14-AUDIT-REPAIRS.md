# V14 stadium audit repairs — work in progress

V14 applies the [23-finding V13 audit](audits/V13-INDEPENDENT-AUDIT.md) to the preserved V13 static scene. The [closure ledger](STADIUM-AUDIT-CLOSURE.md) separates implemented repairs, local diagnostics and independent acceptance. This revision is not a complete resolution of the audit and has no new interactive export or public deployment.

## Reproduce

Use Blender 5.2.1 LTS. Run from the repository root with the preserved `railyards-v4/railyards-v13-static.blend` available. Its expected SHA256 is `22b7801e6d0bfab64c73d82e2e18efe8dc64aea0fba1e6b5db00dbadd17cbb95`.

```sh
blender -b railyards-v4/railyards-v13-static.blend --python railyards-v4/build_audit_v14.py
blender -b railyards-v4/railyards-v14-static.blend --python railyards-v4/verify_audit_v14.py
blender -b railyards-v4/railyards-v14-static.blend --python railyards-v4/verify_tower_v14.py
blender -b railyards-v4/railyards-v14-static.blend --python railyards-v4/verify_seat_pairs_v14.py
VIEWS=tower-corner,tower-plan,frontage,lf-roof-field,lf-roof-rear blender -b railyards-v4/railyards-v14-static.blend --python railyards-v4/render_audit_v14.py
blender -b railyards-v4/railyards-v14-static.blend --python railyards-v4/render_tower_section_v14.py
```

The builder refuses a different input filename or hash and records the verified input hash. Generated scenes, receipts and renders stay outside Git. Current local evidence is under `railyards-v4/review/v14/`; frozen independent review scenes and evidence packages are under `work/audit-fixes-v14/`. Never build into a preserved baseline.

## Implemented geometry

- Rebuild retained left-center seat support as closed solids around the park passage; replace incompatible bowl rails with stairs and rails aligned to the actual section gaps.
- Rebuild low outfield banks with inset seat placement and replace the rounded RF return with straight diagonal rows tapering to the low river bank. Omit a chair and matching occupant when its feet overhang a clipped row cap.
- Shorten the west lantern's lower enclosure while preserving its roof anchor and height.
- Move the tower's near outer-stone face to the retained RF foul-pole x datum. Rebuild its west seating/roof extension, actual facade, hollow interior, floor openings, stairs and doorways.
- Connect the lower balconies to bowl concourse gaps and the upper balcony by stairs; add a shared terrace support frame and a graded arrival onto the existing riverwalk.
- Replace covered bridge endpoints with receiving stairs and actual facade openings. Full ground destinations and a coherent long-span structure remain open.

## Evidence boundaries

The seat diagnostic checks all active seat placements against raw authored mesh: center and four rotated foot samples, low contacts, headroom and a sampled body envelope. It includes retained components and guards. It also checks the specified park passage. The tower diagnostic adds explicit tread centers, doorways, terrace connections and the arrival onto the sloping riverwalk. Neither diagnostic proves every possible walking route, structural adequacy, accessibility, capacity or surveyed dimensional fidelity.

The tower section removes part of the outer shell **only in an unsaved render session** to expose the interior route. It is a cutaway, not an opening in the delivered model.

The independent [phase-3](audits/V14-PHASE3-REVIEW.md) report found actual chair-to-chair penetrations omitted by the architectural mesh test, and unprotected lift-well edges. The [phase-4 follow-up](audits/V14-PHASE4-REVIEW.md) independently accepts the subsequent shaft-edge protection while preserving the chair-collision finding. A passing centerline route alone does not prove edge protection.

The independent [phase-1](audits/V14-PHASE1-REVIEW.md) and [phase-2](audits/V14-PHASE2-REVIEW.md) reports identify their frozen scene hashes. They do not automatically accept later geometry. In particular, the LF pavilion roof study remains source-inconsistent, and bridge ground continuations remain unresolved. Keep these findings open even if seat diagnostics pass.
