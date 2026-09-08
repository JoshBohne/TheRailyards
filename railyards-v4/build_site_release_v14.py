"""Consolidate the final saved V14 stadium and reference-backed riverfront pass.

Input is the preserved final V14 static scene. Output is a separate site release;
the V3 baseline and all prior saved scenes remain unchanged.
"""
import bpy
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from build_riverfront_v13 import build

source = Path(bpy.data.filepath)
scene = bpy.data.scenes['Railyards v4']
bpy.context.window.scene = scene
if scene.get('seat_count') != 33997 or not bpy.data.collections.get('D2_V14 Flush RF frontage'):
    raise ValueError('Expected the final two-bank V14 stadium input')
receipt = {'sourceScene': str(source), 'sourceSha256': hashlib.sha256(source.read_bytes()).hexdigest(),
           'generators': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                          [ROOT / 'r14_audit.py', ROOT / 'r14_tower.py', ROOT / 'build_riverfront_v13.py']}}
build(scene)
scene['site_release'] = 'V14 stadium plus merged McDonalds Park riverfront'
scene['site_release_provenance'] = json.dumps(receipt)
destination = Path(os.environ['RAILYARDS_RELEASE_SCENE'])
destination.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(destination), compress=True)
receipt['releaseScene'] = str(destination)
receipt['releaseSha256'] = hashlib.sha256(destination.read_bytes()).hexdigest()
destination.with_suffix('.json').write_text(json.dumps(receipt, indent=2) + '\n')
print('SITE_RELEASE', json.dumps(receipt))
