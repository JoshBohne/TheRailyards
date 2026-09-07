#!/bin/zsh
# Rebuild the V12 static scene from the generators. Intermediate stage files
# (gray, detail, v4, v8, v9 equivalents) go to work/v12-chain so the preserved
# V3-V11 scenes are never overwritten. Then the replay export and V12 save.
set -e
cd "$(dirname "$0")"
B=/Applications/Blender.app/Contents/MacOS/Blender
export RAILYARDS_STAGE_DIR="$PWD/work/v12-chain"; mkdir -p "$RAILYARDS_STAGE_DIR"
$B -b --python-exit-code 1 --python build_blockout.py --python build_detail.py --python add_interior_cameras.py --python add_review_cameras.py --python finalize_scene.py --python finalize_v8.py --python finalize_v9.py --python build_circulation_v12.py
$B -b railyards-v12-static.blend --python-exit-code 1 --python build_replay_v10.py -- --version 12
