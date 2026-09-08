#!/bin/zsh
# Apply the reproducible context pass to an explicitly supplied V12 baseline.
set -eu
cd "$(dirname "$0")"
BLENDER=/Applications/Blender.app/Contents/MacOS/Blender
BASELINE=${1:?Usage: build_v13.sh /absolute/path/to/railyards-v12-static.blend}
$BLENDER -b "$BASELINE" --python-exit-code 1 --python build_riverfront_v13.py
$BLENDER -b railyards-v13-static.blend --python-exit-code 1 --python verify_riverfront_v13.py
$BLENDER -b railyards-v13-static.blend --python-exit-code 1 --python render_riverfront_v13.py
