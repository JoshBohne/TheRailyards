# The Railyards

Editable Blender reconstruction of the AECOM White Sox Railyards concept in Chicago.

**Start here: [Fable 5.1 handoff](docs/FABLE-5.1-HANDOFF.md).** V3 is the preserved baseline. The next milestone is V4: correct spatial relationships, structure and geographic context before further surface detail.

## Contents

- `railyards-v3/`: delivered scene, 35 reproducible Python modules, specifications, gallery and eight native renders.
- `reconstruction-references/`: original artwork, working images and additional references.
- `reference-audit/`: source inventories and research evidence, including historical findings that may have been superseded.
- `railyards-v2/`: three earlier renders for comparison; the full earlier study remains in the original workspace.
- `docs/FABLE-5.1-HANDOFF.md`: prioritized brief, concrete defects, evidence, constraints and acceptance criteria.
- `docs/START-FABLE.txt`: short prompt to paste into the receiving agent.

## Review locally

From the project root:

```sh
python3 -m http.server 8850 --bind 127.0.0.1
```

Open http://127.0.0.1:8850/railyards-v3/ in a browser. Open `railyards-v3/railyards-v3.blend` in Blender. The scene uses no externally linked images. Rebuild commands are in `railyards-v3/README.md`; use them on a V4 copy when beginning changes.

## Versioning

Git tracks source modules, specifications, reference assets and project documentation. Generated `.blend` files, model renders, logs and archives stay on disk and in the transfer ZIP, outside Git. A Git clone alone therefore requires rebuilding the scene or obtaining the transfer ZIP. The `v3-baseline` tag preserves the starting source tree. This is a local repository; no remote has been created or files published.

The project was copied from the verified V3 delivery on 2026-09-06. Original V1/V2/V3 deliveries remain in `/Users/joshbohne/Documents/Codex/2026-09-05/i-h/outputs`. The copy's 65 manifest-listed baseline files and images matched their recorded SHA-256 hashes. The historical receipts retain their original absolute paths as provenance.

Reference artwork remains attributed to its creators; inclusion as reference is not a claim of ownership or a redistribution license.
