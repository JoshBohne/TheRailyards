#!/bin/zsh
# Downscale renders and source artwork into site/img as JPEGs.
set -e
cd "$(dirname "$0")/.."
V=railyards-v4; O=site/img; mkdir -p $O
j(){ sips -s format jpeg -s formatOptions 74 -Z ${3:-1600} "$1" --out "$O/$2.jpg" >/dev/null; }
for f in final-south final-north final-bridge interior-third_base_seats interior-home_upper_deck interior-home_plate interior-left_field_skyline; do j $V/$f.png $f; done
for f in v4-geo_map v4-rf_section v4-rf_corner_exterior v4-rf_tower_junction v4-east_lake_high control-rf_section control-rf_corner_exterior control-geo_map control-rf_plan_ortho v4-rf_plan_ortho rf-overlay-south; do j $V/review/$f.png $f 1400; done
for f in home_plate_skyline press_box roosevelt_bridge_west north_park_entry riverwalk_north east_bank aerial_west; do [ -f $V/review/v4-$f.png ] && j $V/review/v4-$f.png $f; done
j $V/baseline-v3/interior-third_base_seats.png v3-third_base 1400
for f in south north bridge; do j $V/baseline-v3/final-$f.png v3-$f; j $V/baseline-v2/final-$f.png v2-$f; done
j reconstruction-references/aecom-south-aerial.jpg aecom-south
j reconstruction-references/aecom-north-aerial.png aecom-north
j reconstruction-references/user-bridge-view.png aecom-bridge
j reconstruction-references/railyards-site-plan.png site-plan 1400
du -ch $O/*.jpg | tail -1
