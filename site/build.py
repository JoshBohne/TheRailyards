"""Build the Railyards site.

    python3 site/build.py            # writes site/*.html (multi-page, img/ paths)
    python3 site/build.py --single   # also writes site/dist/railyards-rebuilt.html
                                     # (one file, images embedded, for claude.ai artifacts)

Images live in site/img/ (JPEG, made by site/make_images.sh from the renders).
Page content lives in this file so the multi-page site and the single-page
artifact never drift apart.
"""
import base64,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
FONTS='<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;700;800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">'
PAGES=[('index','Overview'),('sources','Sources vs model'),('views','New views'),('process','Process'),('roadmap','Roadmap')]

def nav(current,single=False):
    items=''.join(f'<li><a class="l" href="{"#"+k if single else k+".html"}"{" aria-current=\"page\"" if (k==current and not single) else ""}>{t}</a></li>' for k,t in PAGES)
    return f'<nav class="top"><div class="wrap"><a class="brand" href="{"#index" if single else "index.html"}">Railyards, Rebuilt</a><ul>{items}</ul></div></nav>'

FOOT='<footer><div class="wrap"><p>Reference artwork © AECOM for the Chicago White Sox; used here for comparison only. Map data © OpenStreetMap contributors (ODbL). Shoreline: USGS National Hydrography Dataset. Token accounting: Tokscale on local session logs, Railyards sessions only. Model, renders and page: Josh Bohne, September 2026. This is a fan reconstruction of published concept art, not an official or surveyed design.</p></div></footer>'

def fig(img,cap,alt=''):
    return f'<figure><img src="img/{img}.jpg" alt="{alt or cap}" loading="lazy"><figcaption>{cap}</figcaption></figure>'

def pair(a,b):return f'<div class="pair">{a}{b}</div>'

def cmp(source,models,cap,start=50):
    """Drag slider: AECOM artwork on the left of the handle, the model on the right.
    ``models`` is an ordered dict of label -> image stem; the first is shown."""
    first=next(iter(models.values()))
    picks=''.join(f'<button type="button" data-src="img/{v}.jpg" aria-pressed="{"true" if v==first else "false"}">{k}</button>' for k,v in models.items())
    return f'''<div class="cmp" style="--x:{start}%"><div class="frame"><img src="img/{source}.jpg" alt="AECOM concept rendering" loading="lazy"><img class="over" src="img/{first}.jpg" alt="Blender model through the same camera" loading="lazy"><div class="bar"></div><div class="knob">&lt;&gt;</div><span class="lab l">AECOM</span><span class="lab r">Model</span><div class="pick">{picks}</div><input type="range" min="0" max="100" value="{start}" aria-label="Reveal the model"></div><figcaption>{cap}</figcaption></div>'''

CMP_JS='''<script>
document.querySelectorAll('.cmp').forEach(c=>{const r=c.querySelector('input[type=range]');const set=v=>c.style.setProperty('--x',v+'%');r.addEventListener('input',()=>set(r.value));
c.querySelectorAll('.pick button').forEach(b=>b.addEventListener('click',()=>{c.querySelector('.over').src=b.dataset.src;c.querySelectorAll('.pick button').forEach(o=>o.setAttribute('aria-pressed',o===b));}));});
</script>'''

# ---------------------------------------------------------------- pages
INDEX=f'''
<header class="page"><div class="wrap"><div class="grid">
<div><div class="eyebrow">The Railyards · Chicago White Sox · AECOM concept, Sept 2026</div><h1 style="margin-top:14px">Railyards,<br>Rebuilt</h1></div>
<div><p class="lede">The three renderings AECOM released on Saturday, turned into an editable 3-D model of the proposed White Sox ballpark on the South Branch, with the real Chicago skyline and Lake Michigan where they actually are, so you can look at it from anywhere.</p>
<p class="note" style="margin-top:14px">Built over one weekend by Josh Bohne with OpenAI Codex (GPT-6 Astra) and Claude Code (Claude Fable 5.1). Every image on this site is a native Blender render of the model unless it is labelled as AECOM artwork.</p></div>
</div>
<div class="hero">{cmp('aecom-south',{'V4':'final-south','V3':'v3-south','V2':'v2-south'},'Drag the handle: AECOM\'s south aerial on the left, the model through the same camera on the right. Buttons swap in the earlier V3 and V2 stages.',62)}</div>
</div></header>
<section><div class="wrap">
<div class="bigstats">
<div><b>3</b><span>AECOM renderings fitted</span></div>
<div><b>26,950</b><span>seats, individually placed</span></div>
<div><b>291 M</b><span>tokens across two agents</span></div>
<div><b>V4</b><span>current version · Sunday</span></div>
</div>
<div class="cards">
<div class="card"><h3>Sources vs model</h3><p>Each AECOM picture beside the model rendered through the same camera, plus the site plan against the model's map.</p><a href="sources.html">See the comparisons</a></div>
<div class="card"><h3>New views</h3><p>Angles the release didn't show: behind home plate with the skyline, the press box, Roosevelt Road, the park, the riverwalk, the east bank.</p><a href="views.html">Look around</a></div>
<div class="card"><h3>Process</h3><p>How V1 to V4 happened, what each agent did, what it cost in tokens and hours, and how every fix was checked.</p><a href="process.html">Read the process</a></div>
</div>
</div></section>
<section><div class="wrap"><div class="sec-head"><div class="eyebrow">Why bother</div><div><h2>A picture you can walk around</h2>
<p style="margin-top:12px">A rendering shows one angle from one height on one evening. A model answers the questions fans actually ask: what do you see from the upper deck, does the scoreboard block the skyline, where does the riverwalk go, how does the park meet Roosevelt, is the lake visible. The model is fitted to the artwork wherever the artwork shows something, honest about where it is guessing, and rebuilt from scripts so every improvement is repeatable.</p>
<p>It is not the building. AECOM's own caption applies: design, uses, building locations and public-realm elements remain subject to diligence, engineering and approvals. Treat this as an informed sketch that keeps getting better.</p></div></div>
<div class="gal">{fig('press_box','From the press-box level behind home plate. The Loop is straight ahead beyond the boards; the Museum Park towers are in right-centre.')}{fig('aerial_west','From the west over the rail yards: stadium, park, river, the near South Loop, and Lake Michigan beyond.')}</div>
</div></section>
'''

SOURCES=f'''
<header class="page"><div class="wrap"><div class="grid">
<div><div class="eyebrow">Sources vs model</div><h1 style="margin-top:14px">Same<br>camera</h1></div>
<div><p class="lede">For each released picture the model has a camera solved to the artwork's own perspective. Left is AECOM; right is Blender through that camera. Differences are where the model is wrong or unfinished, and they are meant to be visible.</p></div>
</div></div></header>
<section><div class="wrap">
<p class="note" style="margin-bottom:28px">Drag the handle. Left of it is AECOM's picture; right of it is the model through the same solved camera. The buttons swap the model between the current V4 and the earlier V3 and V2 stages, so you can see the reconstruction converge.</p>
<h3 style="margin-bottom:14px">South aerial, afternoon</h3>
{cmp('aecom-south',{'V4':'final-south','V3':'v3-south','V2':'v2-south'},'<b>Slider.</b> Same camera; AECOM at left of the handle, model at right. The lake, the board at the river edge and the tower junction are V4 changes; the future towers across the river are AECOM\'s own illustration kept as a separate layer.')}
{pair(fig('aecom-south','<b>AECOM.</b> The south aerial: the arched brick river face, clock tower, right-field board at the river, the soccer stadium and towers across the river, the Loop and lake beyond.'),fig('final-south','<b>Model.</b> Camera fitted to the same picture. The lake now sits top right where AECOM has it; the board is at the river edge beside the tower; the towers across the river are a labelled future-development layer.'))}
<h3 style="margin-bottom:14px">North aerial, dusk</h3>
{cmp('aecom-north',{'V4':'final-north','V3':'v3-north','V2':'v2-north'},'<b>Slider.</b> The first picture most people saw. The park grade, outfield entry above the bleachers and the lower riverwalk follow the artwork; the field, seats and boards are native geometry.')}
{pair(fig('aecom-north','<b>AECOM.</b> The north aerial, the view most people saw first: bowl, raised park, Northwestern Medicine building, riverwalk and the board over the bleachers.'),fig('final-north','<b>Model.</b> Same camera. The park grade, the outfield entry above the bleachers and the lower riverwalk follow the picture; the field, seats and boards are native geometry.'))}
<h3 style="margin-bottom:14px">From the Roosevelt Road bridge</h3>
{cmp('aecom-bridge',{'V4':'final-bridge','V3':'v3-bridge','V2':'v2-bridge'},'<b>Slider.</b> Twilight from the bridge; fireworks are staged for this view only, as in the artwork.')}
{pair(fig('aecom-bridge','<b>AECOM.</b> Looking south from the bridge at twilight, fireworks over the bowl.'),fig('final-bridge','<b>Model.</b> Same camera. Bridge deck, tender houses, the park and its lawn, the retail under the deck, the tower and board beyond.'))}
<h3 style="margin-bottom:14px">Site plan vs the model's map</h3>
{pair(fig('site-plan','<b>AECOM site plan.</b> Roosevelt to 18th, Canal Street to the river, Soldier Field and the lake at right.'),fig('v4-geo_map','<b>Model, orthographic, north up, 5.2 km.</b> Mapped streets and buildings, the river, the stadium, Grant Park and Museum Campus lawns, and the USGS shoreline with Northerly Island and the harbours.'))}
<div class="limits"><h3>Reading the differences</h3><p style="margin-top:8px">The bowl outline, canopy, tower position, board positions and the park edge are traced from these pictures. Materials, crowd, planting and the boards' graphics are approximations. Buildings across the river and the soccer stadium are AECOM's own future-phase illustration and are kept as a separate layer that the north view hides, exactly as the north artwork does.</p></div>
</div></section>
'''

VIEWS=f'''
<header class="page"><div class="wrap"><div class="grid">
<div><div class="eyebrow">New views</div><h1 style="margin-top:14px">Angles the<br>release skipped</h1></div>
<div><p class="lede">The point of a model. These cameras are not fitted to any artwork; they are placed where a person would stand. Lighting is the same late-afternoon sun as the south aerial.</p></div>
</div></div></header>
<section><div class="wrap">
<div class="full">{fig('home_plate_skyline','<b>Behind home plate, field level.</b> A batter’s view: the boards, the outfield banks, and above them the near South Loop towers with the Loop to the left. The lake is behind those towers and cannot be seen from here.')}</div>
<div class="full">{fig('press_box','<b>Press-box level.</b> The whole bowl and the skyline in one frame: Willis and 311 South Wacker over left-centre, NEMA, The Grant and One Museum Park over right-centre, 1000M between them.')}</div>
{pair(fig('roosevelt_bridge_west','<b>Roosevelt Road, west end of the bridge.</b> Looking south over the raised park toward the outfield entrance, with the Northwestern Medicine building on the right.'),fig('north_park_entry','<b>On the park deck.</b> Approaching the outfield entry above the bleachers; the bowl and the centre-field board ahead, the riverwalk below to the left.'))}
{pair(fig('riverwalk_north','<b>Lower riverwalk, walking north.</b> The brick arcade under the right-field seats on the left, the river on the right, the Roosevelt bridge ahead.'),fig('east_bank','<b>From the east bank.</b> Across the river: the clock tower, the river arcade, the right-field board and the bleachers behind it.'))}
<div class="full">{fig('aerial_west','<b>From the west, 270 m up.</b> The whole district at once: rail yards and the covered links, the park meeting Roosevelt, the river, the near South Loop, Lake Michigan.')}</div>
{pair(fig('interior-third_base_seats','<b>Third-base seats.</b> The right-field board set back behind the wall on its pylons; the Museum Park cluster in right-centre.'),fig('interior-left_field_skyline','<b>Left-field upper deck.</b> Willis Tower, the lit crown of 311 South Wacker, the Board of Trade.'))}
<p class="note">Coming next: short camera moves through these same spots (a walk down the riverwalk, a slow turn from the press box) once materials and crowd variation are further along.</p>
</div></section>
'''

PROCESS=f'''
<header class="page"><div class="wrap"><div class="grid">
<div><div class="eyebrow">Process</div><h1 style="margin-top:14px">How we<br>got to V4</h1></div>
<div><p class="lede">Two coding agents, one weekend, four versions. Codex did the long build on Saturday; Claude Code did the corrections on Sunday. Everything is scripts, so every version can be rebuilt and compared.</p></div>
</div></div></header>
<section><div class="wrap">
<div class="sec-head"><div class="eyebrow">Innings</div><div><h2>Four versions</h2></div></div>
<div class="innings">
<div class="inning"><div class="n">V1</div><div class="who">Astra · Sat evening</div><h3>Read the pictures</h3><p>Inventory the three AECOM views and the site plan, register the site to OpenStreetMap, block out a grey massing model with cameras fitted to each artwork.</p></div>
<div class="inning"><div class="n">V2</div><div class="who">Astra · Sat night</div><h3>Calibrate</h3><p>Solve the three camera fits (2.9 px error on the north aerial), trace bowl, canopy and field from pixels, build the district: river, bridges, rail links, Roosevelt Road.</p></div>
<div class="inning"><div class="n">V3</div><div class="who">Astra + Luna · overnight</div><h3>Dress it</h3><p>Thirty-five Python generators: arched brick envelope, clock tower, four tiers with 27,000 seats, video boards, riverwalk, park, Northwestern Medicine, Willis and 13 more landmarks. Eight native renders and a written handoff of known problems.</p></div>
<div class="inning"><div class="n">V4</div><div class="who">Fable 5.1 · Sun, 2½ h</div><h3>Make it true</h3><p>Fix what a fan would notice: a scoreboard on the grass, a bowl end floating over the river, no lake, the wrong towers in right field. Every fix checked with same-camera before/after renders.</p></div>
</div>
</div></section>
<section><div class="wrap">
<div class="sec-head"><div class="eyebrow">Box score</div><div><h2>What it took</h2><p style="margin-top:12px">Railyards sessions only (Playi work on the same machine that weekend is excluded), as recorded locally by Tokscale from the Codex and Claude Code session logs. Cost is an API-equivalent estimate at list prices, not what a subscription charged.</p></div></div>
<div class="bigstats">
<div><b>~20 h</b><span>Sat 7 pm → Sun 3:30 pm CDT</span></div>
<div><b>291 M</b><span>tokens, three models</span></div>
<div><b>2,217</b><span>model responses</span></div>
<div><b>$103</b><span>API-equivalent estimate</span></div>
</div>
<div class="scroll"><table class="box">
<thead><tr><th>Model</th><th>Responses</th><th>Input</th><th>Output</th><th>Cache read</th><th>Cache write</th><th>Model time</th><th>Est. cost</th></tr></thead>
<tbody>
<tr><td>GPT-6 Astra<span class="role">Codex · V1, V2, V3 lead: calibration, bowl, district, handoff</span></td><td>922</td><td>2.18 M</td><td>248 K</td><td>112.3 M</td><td>0</td><td>6.1 h</td><td>$77.01</td></tr>
<tr><td>GPT-5.6 Luna<span class="role">Codex · six parallel V3 build workers overnight</span></td><td>1,218</td><td>4.77 M</td><td>369 K</td><td>143.6 M</td><td>0</td><td>4.7 h</td><td>$4.60</td></tr>
<tr><td>Claude Fable 5.1<span class="role">Claude Code · V4: scoreboard, structure, lake, skyline, this site</span></td><td>77</td><td>19 K</td><td>161 K</td><td>27.0 M</td><td>0.49 M</td><td>0.7 h</td><td>$21.17</td></tr>
<tr class="total"><td>Total</td><td>2,217</td><td>6.97 M</td><td>778 K</td><td>282.9 M</td><td>0.49 M</td><td>11.5 h</td><td>$102.78</td></tr>
</tbody></table></div>
<p class="note">"Model time" is the summed duration of model responses; Luna's six workers ran in parallel, so it exceeds their wall clock. Codex logs did not record cache writes. The Fable numbers are the V4 session through the building of this site.</p>
</div></section>
<section><div class="wrap">
<div class="sec-head"><div class="eyebrow">Method</div><div><h2>How it was made</h2></div></div>
<div class="method">
<div>
<h3>Sources, not vibes</h3>
<p>The model is fitted to three published AECOM images and the site plan. A 90-foot base path is the scale prior. Three perspective cameras were solved against pixel controls; everything traced from a picture records which image and which pixels it came from.</p>
<p>Geography is real: OpenStreetMap footprints for 780 existing buildings plus 238 in the near South Loop, the USGS shoreline for the lake, published heights for the landmarks. Buildings are never moved to look better from a seat; the cameras go to the buildings.</p>
<h3 style="margin-top:28px">Everything is a script</h3>
<p>About forty Python modules run through the Blender command line generate the scene: bowl, envelope, seats, boards, park, bridges, skyline, lake. Live edits in Blender were pushed back into the generators, so a clean rebuild reproduces the file. A rebuild takes about a minute; the render pass about ten.</p>
<ul><li><code>build_blockout.py → build_detail.py → finalize_scene.py</code>, then <code>run_v4_renders.sh</code></li><li>1,582 objects, 1.79 M mesh vertices, 26,950 instanced seats, 21,282 spectators, 290 trees</li><li>Blender 5.2.1 LTS, Cycles on Apple Metal</li></ul>
</div>
<div>
<h3>Two agents, two jobs</h3>
<p><b style="color:var(--white)">Astra (Codex)</b> ran Saturday: source inventories, camera calibration, the bowl and the district, thirty-five generators, six Luna workers building components in parallel overnight, and a written handoff that listed what it believed was still wrong. That handoff was honest; it flagged the scoreboard and the missing lake itself.</p>
<p><b style="color:var(--white)">Fable 5.1 (Claude Code)</b> took the handoff on Sunday. It rendered diagnostic cameras before touching anything, triangulated the board from all three source views instead of guessing, found that the skyline data and the city data disagreed by 33 m and fixed the registration once, fetched the lake from USGS when the city's GIS server timed out, and ranked candidate towers by how many pixels they would occupy from the seats. A reviewer model checked the plan before the build and the result before sign-off.</p>
<h3 style="margin-top:28px">Verification</h3>
<p>Every V4 fix has a before/after from the same camera, an orthographic plan with clearances in metres, and the model's own geometry projected back into the AECOM photos. The V3 baseline is preserved and hash-checked. A ledger records what is resolved, what is uncertain and what was deliberately left.</p>
</div></div>
</div></section>
<section><div class="wrap">
<div class="sec-head"><div class="eyebrow">V4 before / after</div><div><h2>What Sunday fixed</h2><p style="margin-top:12px">Same cameras, same lighting, same pipeline. Left: the V3 model rebuilt through the V4 chain. Right: V4.</p></div></div>
<h3 style="margin-bottom:14px">The right-field board was 5 m inside the field</h3>
{pair(fig('control-rf_plan_ortho','<b>Before.</b> The V3 anchor came from a single-height back-projection and landed inside the playable polygon.'),fig('v4-rf_plan_ortho','<b>After.</b> Triangulated from all three source cameras; on pylons behind the wall, every footprint clears the field (min 0.39 m).'))}
{pair(fig('v3-third_base','<b>Before.</b> From third base the board reads as standing on the grass; the right-field towers are missing.'),fig('interior-third_base_seats','<b>After.</b> Board set back; NEMA, One Museum Park, The Grant and 1000M in right-centre.'))}
<h3 style="margin-bottom:14px">The bowl end was held up by nothing</h3>
{pair(fig('control-rf_section','<b>Before.</b> Section through the right-field corner: field, bleachers and board over an 8 m void down to the riverwalk.'),fig('v4-rf_section','<b>After.</b> A podium from the riverwalk to the bleacher base, a brick arcade on the river face, pylons landing on the podium.'))}
{pair(fig('control-rf_corner_exterior','<b>Before.</b> From the east bank the decks end in mid-air beside the tower.'),fig('v4-rf_corner_exterior','<b>After.</b> A brick end wall following the four tiers, an arcade at the riverwalk, a link block to the tower.'))}
<h3 style="margin-bottom:14px">Lake Michigan did not exist</h3>
{pair(fig('control-geo_map','<b>Before.</b> The background terrain paved straight across the lake.'),fig('v4-geo_map','<b>After.</b> USGS shoreline in the scene’s frame: Grant Park, Museum Campus, Northerly Island, Burnham Harbor, Navy Pier.'))}
{pair(fig('rf-overlay-south','<b>Proof against the artwork.</b> The modelled field (green), board frame (black/white) and pylon bases (red) projected into the AECOM south aerial with the calibrated camera. Orange: where V3 had the board.'),fig('v4-rf_tower_junction','<b>Tower junction.</b> Clock tower, river arcade and bowl end now meet, matching the crop of the south aerial.'))}
</div></section>
'''

ROADMAP=f'''
<header class="page"><div class="wrap"><div class="grid">
<div><div class="eyebrow">Roadmap</div><h1 style="margin-top:14px">What's<br>next</h1></div>
<div><p class="lede">V4 fixed the things that were spatially wrong. The next passes are about looking right and showing more. This list is the working plan and will change as fans point things out.</p></div>
</div></div></header>
<section><div class="wrap">
<div class="road">
<div><span class="st">Next · V5</span><h3>Materials and light</h3><p>Real brick, glass and metal at the right scale, window recess depth, varied crowd colours and poses, coherent dusk lighting across all views. The city stops looking like a grey checkerboard.</p></div>
<div><span class="st">Next · V5</span><h3>Centre-field board and restaurant</h3><p>The centre-field board triangulates 14 m north of where it sits; the rounded restaurant hangs off the same anchor. Move both together and re-fit the batter's eye.</p></div>
<div><span class="st">Next · V5</span><h3>Left-field end and concourses</h3><p>Give the left-field end of the bowl the same end wall treatment as right field; open up visible concourse depth, vomitories and the tower-to-bowl junction from the inside.</p></div>
<div><span class="st">Planned</span><h3>Moving pictures</h3><p>Short clips: a walk north along the riverwalk, a slow turn from the press box, the approach from Roosevelt over the park. Same cameras as the stills.</p></div>
<div><span class="st">Planned</span><h3>Night game</h3><p>A full night lighting pass: floodlights, board glow, the lit crowns downtown, the river reflections, from every fixed camera.</p></div>
<div><span class="st">Planned</span><h3>More of the city</h3><p>Textured silhouettes for the towers that matter from the seats; the Loop core beyond the near South Loop; the Museum Campus buildings from real footprints rather than boxes.</p></div>
<div><span class="st">Open question</span><h3>The two rail-link readings</h3><p>The north and south artworks disagree on where the covered rail links cross. Both readings are kept as separate layers until a better unified fit exists.</p></div>
<div><span class="st">Open question</span><h3>Outfield dimensions</h3><p>The infield is regulation; the outfield wall is traced from the artwork (about 328 ft down the right-field line). Any published dimensions would replace the trace.</p></div>
</div>
<div class="limits" style="margin-top:40px"><h3>What this is not</h3><p style="margin-top:8px">A conceptual reconstruction of concept art, not a surveyed building. Outfield distances, hidden structure, materials and the future towers across the river are inferred. Scoreboard graphics and players are placeholders. AECOM's disclaimer applies: design, uses and locations remain subject to diligence, engineering and approvals.</p></div>
</div></section>
'''

BODIES={'index':INDEX,'sources':SOURCES,'views':VIEWS,'process':PROCESS,'roadmap':ROADMAP}
TITLES={'index':'Railyards, Rebuilt','sources':'Sources vs model · Railyards, Rebuilt','views':'New views · Railyards, Rebuilt','process':'Process · Railyards, Rebuilt','roadmap':'Roadmap · Railyards, Rebuilt'}

def page(key):
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{TITLES[key]}</title>{FONTS}<link rel="stylesheet" href="assets/site.css"></head><body>{nav(key)}{BODIES[key]}{FOOT}{CMP_JS}</body></html>'

def single():
    """One file for claude.ai artifacts: every image embedded exactly once and
    assigned by script, so repeated uses do not repeat the bytes."""
    import re,json
    css=(ROOT/'assets/site.css').read_text()
    body=''.join(f'<div id="{k}">{BODIES[k]}</div>' for k,_ in PAGES)
    html=f'<title>Railyards, Rebuilt</title>{FONTS}<style>{css}\nsection,header.page{{scroll-margin-top:60px}}</style>{nav("index",single=True)}{body}{FOOT}{CMP_JS}'
    names=sorted(set(re.findall(r'img/([a-z0-9_\-]+)\.jpg',html)))
    html=re.sub(r'src="img/([a-z0-9_\-]+)\.jpg"',r'data-img="\1"',html)
    html=re.sub(r'data-src="img/([a-z0-9_\-]+)\.jpg"',r'data-pick="\1"',html)
    table={n:'data:image/jpeg;base64,'+base64.b64encode((ROOT/'img'/(n+'.jpg')).read_bytes()).decode() for n in names}
    js='<script id="imgs" type="application/json">'+json.dumps(table)+'</script><script>(function(){const T=JSON.parse(document.getElementById("imgs").textContent);document.querySelectorAll("[data-img]").forEach(e=>{e.src=T[e.dataset.img]});document.querySelectorAll("[data-pick]").forEach(b=>{b.dataset.src=T[b.dataset.pick]});})();</script>'
    # the picker script must run before CMP_JS binds click handlers that read data-src
    return html.replace(CMP_JS,js+CMP_JS)

if __name__=='__main__':
    for k,_ in PAGES:(ROOT/f'{k}.html').write_text(page(k))
    print('wrote',[k+'.html' for k,_ in PAGES])
    if '--single' in sys.argv:
        (ROOT/'dist').mkdir(exist_ok=True);out=ROOT/'dist/railyards-rebuilt.html';out.write_text(single());print('wrote',out,round(out.stat().st_size/1e6,2),'MB')
