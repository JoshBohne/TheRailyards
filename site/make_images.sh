#!/bin/zsh
# Downscale renders and source artwork into site/img as JPEGs.
set -e
cd "$(dirname "$0")/.."
V=railyards-v4; O=${IMG_OUT:-site/img}; Q=${IMG_Q:-74}; mkdir -p $O
j(){ local z=${3:-1600}; [ -n "$IMG_MAX" ] && [ "$z" -gt "$IMG_MAX" ] && z=$IMG_MAX; sips -s format jpeg -s formatOptions $Q -Z $z "$1" --out "$O/$2.jpg" >/dev/null; }
for f in final-south final-north final-bridge interior-third_base_seats interior-home_upper_deck interior-home_plate interior-left_field_skyline; do j $V/$f.png $f; done
for f in v4-geo_map v4-rf_section v4-rf_corner_exterior v4-rf_tower_junction v4-east_lake_high control-rf_section control-rf_corner_exterior control-geo_map control-rf_plan_ortho v4-rf_plan_ortho rf-overlay-south; do j $V/review/$f.png $f 1400; done
for f in press_box riverwalk_north east_bank aerial_west home_plate_skyline roosevelt_bridge_west tier_junction north_park_entry lf_gatehouse; do [ -f $V/review/night-$f.png ] && j $V/review/night-$f.png night-$f; done
for f in home_plate home_upper_deck third_base_seats left_field_skyline; do [ -f $V/night-$f.png ] && j $V/night-$f.png night-$f; done
for f in tier_junction upper_concourse; do [ -f $V/review/v7-$f.png ] && j $V/review/v7-$f.png v7-$f; done
[ -f $V/review/v7day-tier_junction.png ] && j $V/review/v7day-tier_junction.png v7pre-tier_junction 1400
for f in lf_gatehouse; do [ -f $V/review/v6-$f.png ] && j $V/review/v6-$f.png v6-$f; done
for f in press_box east_lake_high aerial_west; do [ -f $V/review/v5-$f.png ] && j $V/review/v5-$f.png v5-$f; done
[ -f $V/review/pass1/final-south.png ] && j $V/review/pass1/final-south.png v4-south 1400
for f in home_upper_deck left_field_skyline; do [ -f $V/review/pass1/interior-$f.png ] && j $V/review/pass1/interior-$f.png v4-$f 1400; done
for f in home_plate_skyline press_box roosevelt_bridge_west north_park_entry riverwalk_north east_bank aerial_west; do if [ -f $V/review/v5-$f.png ]; then j $V/review/v5-$f.png $f; else j $V/review/v4-$f.png $f; fi; done
j $V/baseline-v3/interior-third_base_seats.png v3-third_base 1400
for f in south north bridge; do j $V/baseline-v3/final-$f.png v3-$f; j $V/baseline-v2/final-$f.png v2-$f; done
j reconstruction-references/aecom-south-aerial.jpg aecom-south
j reconstruction-references/aecom-north-aerial.png aecom-north
j reconstruction-references/user-bridge-view.png aecom-bridge
j reconstruction-references/railyards-site-plan.png site-plan 1400
for f in site wide; do [ -f $V/work/today-$f.jpg ] && j $V/work/today-$f.jpg today-$f >/dev/null; done
for f in site_today site_today_wide; do [ -f $V/review/v5-$f.png ] && j $V/review/v5-$f.png v5-$f 1600; done
du -ch $O/*.jpg | tail -1
