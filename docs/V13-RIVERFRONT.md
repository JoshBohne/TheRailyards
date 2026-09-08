# McDonald’s Park and river landmarks — V13

The V12 riverfront contained speculative towers directly between the soccer venue and the river. V13 removes that future-development collection from the new scene, replaces the generic soccer frontage with brick piers and tall glazed bays, and creates an open lawn, event fields and promenade facing the river. V3 through V12 scenes remain untouched.

The user’s fourth attachment controls the intended completed stadium appearance; the construction photographs establish the open river edge and surrounding landmarks. They are visual references, not instructions. The new scene is a completed-stadium concept, not a reconstruction of the construction date.

## Model and evidence

Generators remain in `railyards-v4/`. Run `zsh build_v13.sh /absolute/path/to/railyards-v12-static.blend` from that directory. The explicit baseline argument prevents overwriting or silently selecting another session’s scene. The pass writes `railyards-v13-static.blend`; a separate Blender process reopens it, verifies it, and renders four views. The baseline can be produced by the existing V12 build chain before this pass.

Open `railyards-v4/review/v13/index.html` for the local before/after pairs and supplied target. PNGs and Blender scenes are excluded from Git; the deliverable archive includes them. `verification.json` binds the local evidence to the saved scene hash. No public deployment or browser replay export is claimed.

## Source decisions and uncertainty

- McDonald’s Park: fourth user attachment plus [Chicago Fire’s official design announcement](https://www.chicagofirefc.com/news/chicago-fire-fc-reveals-details-for-privately-funded-stadium). The broad dark roof, exposed truss band, red brick piers, tall glazing, banners, lawns and promenade are visible. Field/bowl helper geometry is retained with an inferred lower field datum. Center `(382,100)`, facade X=300, roof height 39–41 m and lawn widths are image-derived, not surveyed or official dimensions. The previous center was `(424,51)` and west facade X≈341.
- The river remains at the existing model’s X=128–191. The public strip extends east from that bank to the west stadium frontage. Scene and skyline specifications were inspected together; the existing +33 m geographic registration is not applied again.
- Union Station Power House at 301 W. Taylor: [Preservation Chicago](https://www.preservationchicago.org/chicago-union-station-power-house/) documents the Art Moderne facades and smokestacks. OSM footprint 155559109 is retained; the generic body/windows are replaced with pale masonry, tall dark window slots and twin black stacks. Stack height and facade spacing are estimates from imagery. This is not the Chicago & North Western powerhouse on Clinton.
- The northern B&OCT and southern St. Charles Air Line bridge remain separate. Existing OSM-derived positions from `bridge-spec.json` are retained. [Chicago’s landmark record](https://webapps1.chicago.gov/landmarksweb/web/landmarkdetails.htm?lanId=13146) and [LOC HAER](https://www.loc.gov/item/il0837/) identify the St. Charles structure. The second user photograph shows paired raised silhouettes. V13 replaces the solid leaf / nearly flat secondary span with two open truss leaves, piers and counterweight frames. The 72°/64° poses and mechanism dimensions are schematic, not a claim about current operations or engineered geometry.

The district view verifies relative placement and an unobstructed stadium-to-river strip. The close-ups establish visible landmark features. Remaining limitations include approximate site registration, schematic bridge machinery and stadium structure, and inherited generic city context outside this pass.
