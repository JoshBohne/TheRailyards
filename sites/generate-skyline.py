"""Draw the decorative footer using the user's ballpark-view skyline reference.

The supplied image anchors the panorama; landmark silhouettes are emphasized for recognition.
Run from any directory to regenerate public/skyline.svg.
"""
from pathlib import Path

OUTPUT = Path(__file__).resolve().parent / 'public' / 'skyline.svg'
parts = ['''<svg xmlns="http://www.w3.org/2000/svg"><defs>
<pattern id="glass" width="6" height="8" patternUnits="userSpaceOnUse"><path d="M0 0V8M0 0H6" fill="none" stroke="#d1ded5" stroke-opacity=".45" stroke-width=".65"/></pattern>
<pattern id="stone" width="9" height="12" patternUnits="userSpaceOnUse"><rect x="3" y="3" width="3" height="6" fill="#61736d"/><path d="M3 9h4" stroke="#e4dcc7" stroke-width=".8"/></pattern>
<pattern id="dark" width="5" height="8" patternUnits="userSpaceOnUse"><path d="M0 0V8M0 0H5" fill="none" stroke="#8b9b91" stroke-opacity=".3" stroke-width=".5"/></pattern>
</defs>''']

def block(x, y, w, color, windows='glass', bottom=370, depth=6):
    h = bottom-y
    return f'<path d="M{x} {y}l{depth} -4h{w}l-{depth} 4Z" fill="#b3bca9"/><path d="M{x+w} {y}l{depth} -4v{h}l-{depth} 4Z" fill="#627b73"/><path d="M{x} {y}h{w}v{h}h-{w}Z" fill="{color}"/><path d="M{x} {y}h{w}v{h}h-{w}Z" fill="url(#{windows})"/>'

def symbol(name, body):
    parts.append(f'<symbol id="{name}" viewBox="0 0 1200 370">{body}</symbol>')

# Continuous distant roofline. The ordering follows the photo, not a landmark catalog.
back = ''
for x,y,w,c in [(0,245,45,'#b4baaa'),(47,239,24,'#a0b6a8'),(75,233,27,'#80988c'),(107,218,22,'#647d77'),(144,246,18,'#9eb6aa'),(227,200,25,'#b5b7a3'),(305,226,31,'#8da99e'),(337,231,24,'#657e79'),(383,212,35,'#b9bda9'),(420,207,19,'#adb59e'),(446,235,31,'#9aaea0'),(474,242,39,'#748e83'),(521,223,18,'#9bb3a5'),(561,215,22,'#718f89'),(601,194,23,'#c5c6b2'),(635,232,16,'#a5b9ad'),(655,220,36,'#ad9180'),(677,203,12,'#768e87'),(718,267,15,'#9cbaab'),(733,252,25,'#adb4a1'),(870,225,23,'#8daba1'),(903,198,28,'#75958a'),(950,231,18,'#b0a18a'),(989,234,18,'#aebcab')]:
    back += block(x,y,w,c)
symbol('distant-roofline', '<g opacity=".32">'+back+'</g>')

# Willis: narrow dark bundled tubes and twin white antennae, dominant at the left.
willis = ''
for x,y,w in [(151,176,15),(167,92,15),(181,63,24),(205,131,12)]:
    willis += block(x,y,w,'#293b38','dark')
willis += '<path d="M186 63V7M200 63V13" stroke="#b5c5b6" stroke-width="1.8"/><path d="M186 32h3M200 38h3" stroke="#dae0cf"/>'
symbol('willis',willis)

# The narrow, ornate limestone tower immediately beside Willis in the reference.
limestone = block(213,163,23,'#c5bea4','stone') + block(217,148,15,'#d1c9ad','stone',163)
limestone += '<path d="M213 163v-13l3 5 3 -16 4 14 4 -13 4 15 5 -5v13" fill="#d0c7a9" stroke="#afa68f" stroke-width="1"/>'
symbol('limestone-crown',limestone)

# 311 South Wacker: octagonal rose-stone shaft and its five-part illuminated crown.
west = block(280,196,54,'#b8a18b','stone')
west += '<path d="M280 196l8 -12h38l8 12v174h-8V197h-38v173h-8Z" fill="#a68e79"/>'
west += '<path d="M291 184v-26q16 -8 32 0v26" fill="#dcdcc4" stroke="#abb8a3" stroke-width="1.4"/><ellipse cx="307" cy="158" rx="16" ry="6" fill="#ece6cb"/>'
for x in [279,287,322,330]:
    west += f'<path d="M{x} 191v-16q4 -5 8 0v16" fill="#d3d7bc" stroke="#9fae96" stroke-width="1"/>'
west += '<path d="M297 159v23m7 -26v26m7 -26v26m7 -23v23" stroke="#b2bca7"/>'
symbol('wacker-crown',west)

# Board of Trade: stepped Art Deco shoulders, pyramidal roof, clock and Ceres.
trade = block(414,278,82,'#c6bea2','stone')+block(427,246,56,'#d2c7a8','stone')+block(440,213,30,'#d8cdb0','stone')
trade += '<path d="M440 213l15 -28 15 28Z" fill="#668e7e"/><path d="M455 185v-14m-4 5h8" stroke="#b1b9a2" stroke-width="3"/><circle cx="455" cy="169" r="2.5" fill="#b1b9a2"/><circle cx="455" cy="232" r="8" fill="#ece1bf" stroke="#8c977f"/><path d="M455 226v6l4 3" fill="none" stroke="#64715d"/>'
symbol('board-of-trade',trade)

# CNA's warm red face contrasts with the cool glass and pale Aon verticals.
center = block(582,246,61,'#b87860','dark')
center += block(695,176,47,'#d5d4bb')
center += ''.join(f'<path d="M{x} 176v194" stroke="#81978a" stroke-width="2"/>' for x in range(699,741,6))
symbol('cna-aon',center)

# Two Prudential Plaza: diamond pyramid and thin needle.
prudential = block(785,246,50,'#9ab4a0','stone')+block(795,222,30,'#b8c8ad','stone')
prudential += '<path d="M795 222l15 -27 15 27Z" fill="#739984"/><path d="M810 195V156" stroke="#799681" stroke-width="2"/>'
symbol('two-prudential',prudential)

# St. Regis: three interlocking towers with alternating inward/outward tapers.
regis = ''
for x,start,w in [(868,236,24),(892,179,28),(920,270,23)]:
    for n,y in enumerate(range(start,370,32)):
        h=min(32,370-y); inset=4 if n%2 else 0; end=4-inset
        regis += f'<path d="M{x+inset} {y}h{w-2*inset}L{x+w-end} {y+h}H{x+end}Z" fill="{["#5e9989","#8bb8a1"][n%2]}" stroke="#c0d3b8" stroke-width=".7"/>'
    regis += f'<path d="M{x+w} {start}l5 -4v{370-start}l-5 4Z" fill="#527a6e"/>'
symbol('st-regis',regis)

# Foreground South Loop brick volumes, with the stepped roofline visible in the photo.
south = block(756,230,45,'#aa8d78','stone')+block(769,211,24,'#a18370','stone',230)
south += block(823,265,31,'#b08c73','stone')+block(829,252,20,'#b99e80','stone',265)
south += block(924,259,49,'#aa8d7b','stone')+block(946,232,25,'#b49a82','stone',259)+block(972,234,21,'#bbab90','stone')
symbol('south-loop','<g opacity=".48">'+south+'</g>')

# The pair of tall near-lake towers at the right edge are key to this particular view.
east = block(1017,137,29,'#6e9890')+block(1022,120,20,'#8baca0',bottom=137)
east += '<path d="M1022 120v-13M1038 120v-7" stroke="#8b8f7b" stroke-width="2"/>'
east += block(1090,249,25,'#8ca89b')+block(1110,112,67,'#779e8e')
east += ''.join(f'<path d="M{x} 113v257" stroke="#cbd5c4" stroke-width="1.4"/>' for x in range(1115,1177,9))
east += block(1094,281,88,'#9ab4a7')+block(1103,238,26,'#90ad9b')+block(1170,299,24,'#a5bba5')
symbol('lakefront-towers',east)

front = ''
for x,y,w,c in [(0,316,53,'#c4b49a'),(58,320,42,'#b0b7a1'),(101,337,49,'#b99e81'),(241,320,35,'#c1ac8c'),(308,309,37,'#b89c80'),(350,315,29,'#c7bca0'),(400,337,44,'#b5bda8'),(471,333,36,'#b5a58b'),(534,324,28,'#c6bca0'),(583,340,53,'#b8c2ac'),(645,326,29,'#b2967f'),(691,338,39,'#c6bba0'),(737,342,39,'#b6bda6'),(806,332,27,'#b3bda7'),(857,335,33,'#b6a187'),(894,337,37,'#a5b8a5'),(997,339,36,'#b5a389'),(1057,343,36,'#c3b59a'),(1180,280,20,'#8aa396')]:
    if x < 150 or x > 1100 or x in [350,534,691,997]:
        front += block(x,max(y,342),w,c,'stone')
symbol('neighborhood', '<g opacity=".8">'+front+'</g>')
symbol('lights',''.join(f'<rect x="{x}" y="{y}" width="3" height="5" fill="#e6d298"/>' for x,y in [(184,111),(191,212),(203,280),(225,223),(297,292),(449,285),(603,275),(707,294),(805,266),(904,307),(1027,210),(1140,170),(1158,240)]))
parts.append('</svg>')
OUTPUT.write_text('\n'.join(parts)+'\n')
