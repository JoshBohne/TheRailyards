#!/bin/zsh
# Verify the saved V4 scene, then render review, interior and the three fixed source views.
set -e
cd "$(dirname "$0")"
B=/Applications/Blender.app/Contents/MacOS/Blender
W=${RAILYARDS_WIDTH:-1800}; S=${RAILYARDS_SAMPLES:-48}
$B -b railyards-v4.blend --python verify_scene.py
$B -b railyards-v4.blend --python make_plan_evidence.py
RAILYARDS_LABEL=v4 RAILYARDS_OUTDIR=review RAILYARDS_WIDTH=1400 RAILYARDS_SAMPLES=32 $B -b railyards-v4.blend --python render_review.py
RAILYARDS_WIDTH=$W RAILYARDS_SAMPLES=$S $B -b railyards-v4.blend --python render_interior.py
RAILYARDS_LABEL=final RAILYARDS_WIDTH=$W RAILYARDS_SAMPLES=$S $B -b railyards-v4.blend --python render_scene.py
$B -b railyards-v4.blend --python render_southern_rail.py
