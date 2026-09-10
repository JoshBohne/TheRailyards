"""Draw the decorative footer skyline and inline it into the public pages.

The composition follows the user's ballpark-view reference (Willis at the left,
a layered Loop roofline, two tall near-lake towers at the right). It is built the
way the footer that inspired it was built: a wireframe first (heights, three
overlapping rows, one oblique camera), then per-building facade instructions,
then details (a clock that tells Chicago time, windows that light on their own),
then motion (a left-to-right wave whose taller buildings settle later).

Run from any directory. Rewrites the `<div class="footer-skyline">` block in each
public page listed in PAGES, and writes public/skyline.svg for standalone review.
"""
import random
import re
from pathlib import Path

PUBLIC = Path(__file__).resolve().parent / 'public'
PAGES = ['index.html', 'gallery.html', '3d.html', 'build.html']
W, H = 1200, 380            # viewBox; the ground line is y=H
GROUND = H

# One camera for everything: slightly above and to the right, so every roof
# reads as a parallelogram and the right face of every block is visible.
DX, DY = 9, 5

WARMTH = ['#f5dfa0', '#f8d78c', '#f1e2b4', '#f9cf7c', '#f0dea8', '#ffd98a', '#f7e6bf']
GLASS = '#c9d6cf'
rng = random.Random(20260908)

out: list[str] = []


def shade(hex_color: str, k: float) -> str:
    """Scale an RGB hex color; k<1 darkens, k>1 lightens toward white."""
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    if k >= 1:
        r, g, b = (round(c + (255 - c) * (k - 1)) for c in (r, g, b))
    else:
        r, g, b = (round(c * k) for c in (r, g, b))
    return f'#{r:02x}{g:02x}{b:02x}'


def n(v: float) -> str:
    return f'{v:.1f}'.rstrip('0').rstrip('.')


def box(x, y, w, h, color, dx=DX, dy=DY, roof=None, side=None):
    """An oblique block: roof parallelogram, right side face, front face."""
    roof = roof or shade(color, 1.22)
    side = side or shade(color, 0.72)
    return (f'<path d="M{n(x)} {n(y)}l{dx} -{dy}h{n(w)}l-{dx} {dy}Z" fill="{roof}"/>'
            f'<path d="M{n(x + w)} {n(y)}l{dx} -{dy}v{n(h)}l-{dx} {dy}Z" fill="{side}"/>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="{color}"/>')


PATTERNS: list[str] = []


def windows(x, y, w, h, ww, wh, px, py, lit=0.32, glass_color=GLASS, reveal='#3d4a45',
            sill='#f2ecdc', top=6, side_margin=None):
    """Recessed windows with projecting sills on the front face.

    The unlit grid (reveal, sill, glass) is one pattern tile per facade, so a
    tower costs a few hundred bytes. Only windows that will light up are their
    own element, each carrying its own phase, period and warmth.
    """
    side_margin = (px - ww) / 2 if side_margin is None else side_margin
    cols = int((w - 2 * side_margin + (px - ww)) // px)
    rows = int((h - top - 2) // py)
    if cols < 1 or rows < 1:
        return '', ''
    offset = (w - (cols * px - (px - ww))) / 2
    gx, gy = x + offset, y + top
    pid = f'w{len(PATTERNS)}'
    PATTERNS.append(f'<pattern id="{pid}" x="{n(gx)}" y="{n(gy)}" width="{n(px)}" height="{n(py)}" patternUnits="userSpaceOnUse">'
                    f'<rect x="-.7" y="-.7" width="{n(ww + 1.4)}" height="{n(wh + 1.4)}" fill="{reveal}" fill-opacity=".55"/>'
                    f'<rect x="-1.3" y="{n(wh + .5)}" width="{n(ww + 2.6)}" height="1" fill="{sill}"/>'
                    f'<rect width="{n(ww)}" height="{n(wh)}" fill="{glass_color}"/></pattern>')
    static = (f'<rect x="{n(gx - 1.3)}" y="{n(gy - .7)}" width="{n(cols * px - (px - ww) + 2.6)}" '
              f'height="{n(rows * py - (py - wh) + 2.4)}" fill="url(#{pid})"/>')
    lit_rects = []
    for r in range(rows):
        for c in range(cols):
            if rng.random() < lit:
                style = f'--d:{rng.uniform(0, 5):.1f}s;--t:{rng.uniform(7, 16):.1f}s;--c:{rng.choice(WARMTH)}'
                lit_rects.append(f'<rect class="win" style="{style}" x="{n(gx + c * px)}" y="{n(gy + r * py)}" '
                                 f'width="{n(ww)}" height="{n(wh)}"/>')
    return static, f'<g fill="{glass_color}" style="--glass:{glass_color}">{"".join(lit_rects)}</g>'


def building(name, x, height, parts, row):
    """Wrap one building for the rise animation.

    The wave runs left to right, so the delay follows the x position; taller
    buildings take longer to settle.
    """
    delay = round(60 + 900 * x / W)
    duration = round(950 + 1000 * height / H)
    out.append(f'<g class="bldg {row}" data-b="{name}" style="--rd:{delay}ms;--rt:{duration}ms">'
               + ''.join(parts) + '</g>')


# --------------------------------------------------------------------------
# Row 1: distant roofline. Hazed, static window texture, no per-window elements.
# --------------------------------------------------------------------------
out.append('<defs><pattern id="haze-win" width="7" height="9" patternUnits="userSpaceOnUse">'
           '<rect x="2" y="2" width="3" height="4.5" fill="#ffffff" fill-opacity=".28"/></pattern></defs>')
back_row = [(0, 238, 46, '#b7bcb0'), (52, 226, 26, '#a4b6ac'), (84, 214, 30, '#8b9f96'), (120, 199, 24, '#74877f'),
            (150, 244, 22, '#a8bbb0'), (232, 196, 28, '#b9baa8'), (268, 220, 22, '#9fb0a5'), (300, 212, 32, '#8ea79c'),
            (340, 224, 26, '#7c9189'), (376, 204, 36, '#b9bda9'), (418, 198, 20, '#aeb59f'), (446, 226, 32, '#9db0a2'),
            (484, 232, 40, '#84998f'), (528, 214, 20, '#a3b7a9'), (556, 206, 26, '#7e968f'), (592, 190, 26, '#c3c4b1'),
            (628, 222, 18, '#a9bcb0'), (652, 210, 40, '#b09b8c'), (700, 200, 14, '#829891'), (722, 250, 18, '#a3bcae'),
            (746, 236, 28, '#b0b5a2'), (812, 228, 40, '#a7b4a6'), (866, 216, 24, '#93ada2'), (900, 192, 30, '#7d9a8f'),
            (940, 224, 22, '#b3a48d'), (970, 230, 24, '#b1bdab'), (1000, 216, 20, '#9fb2a7'), (1064, 236, 28, '#adb8a9')]
for i, (x, y, w, c) in enumerate(back_row):
    parts = [box(x, y, w, GROUND - y, c, dx=5, dy=3),
             f'<rect x="{x}" y="{y}" width="{w}" height="{GROUND - y}" fill="url(#haze-win)"/>']
    building(f'back-{i}', x, GROUND - y, parts, 'back')

# --------------------------------------------------------------------------
# Row 2: the landmarks. Each one carries its own facade instructions.
# --------------------------------------------------------------------------

# Willis: nine bundled dark tubes stepping down; only the bands and small
# windows read, plus the twin white antennae. Keep it the tallest thing here.
parts = []
for x, y, w in [(151, 172, 15), (166, 92, 15), (181, 66, 24), (205, 128, 12)]:
    parts.append(box(x, y, w, GROUND - y, '#2c3f3c', roof='#4a5e59', side='#1d2b29'))
    static, glass = windows(x, y, w, GROUND - y, 3, 4.6, 6.6, 10, lit=.2, glass_color='#3f5450',
                            reveal='#0f1715', sill='#4b5f5a', top=8)
    parts += [static, glass]
parts.append('<path d="M186 66V22M200 66V28" stroke="#c8d4c7" stroke-width="1.8"/>'
             '<path d="M184 34h4M198 40h4" stroke="#e6e9db" stroke-width="1"/>')
# Belt bands where the tubes step.
parts.append('<path d="M151 172h15M166 92h15M181 66h24M205 128h12M166 232h51M166 302h51" '
             'stroke="#182421" stroke-width="1.4"/>')
building('willis', 151, GROUND - 22, parts, 'mid')

# Limestone tower beside Willis: narrow shaft, ornate crown, keep the proportions.
parts = [box(213, 162, 23, GROUND - 162, '#c6bfa5'), box(217, 146, 15, 16, '#d2caae')]
static, glass = windows(213, 162, 23, GROUND - 162, 4.5, 7.4, 10.5, 14.0, lit=.3, top=5)
parts += [static, glass]
parts.append('<path d="M213 162v-11l3 4 3-14 3 12 4-12 4 13 4-4 2 12" fill="#d5ccad" stroke="#a8a08a" stroke-width=".9"/>')
building('limestone', 213, GROUND - 146, parts, 'mid')

# 311 South Wacker: rose-stone octagonal shaft, five-part illuminated crown.
parts = [box(280, 196, 54, GROUND - 196, '#b9a28c'),
         '<path d="M280 196l8-12h38l8 12v184h-8V197h-38v183h-8Z" fill="#a68e79"/>']
static, glass = windows(288, 197, 38, GROUND - 197, 5, 8, 10.5, 13, lit=.28, glass_color='#d3cbb5', top=4)
parts += [static, glass]
parts.append('<path d="M291 184v-26q16-8 32 0v26" fill="#e2e1c8" stroke="#a9b6a1" stroke-width="1.3"/>'
             '<ellipse cx="307" cy="158" rx="16" ry="6" fill="#efe9cf"/>')
for cx in [279, 287, 322, 330]:
    parts.append(f'<path d="M{cx} 191v-16q4-5 8 0v16" fill="#d8dcc1" stroke="#9fae96" stroke-width="1"/>')
parts.append('<rect class="win lit" style="--d:1s;--t:9s;--c:#fbe7b0;--glass:#e6e3c6" x="297" y="160" width="20" height="20" '
             'rx="9" fill="#e6e3c6" fill-opacity=".7"/>')
building('wacker', 280, GROUND - 158, parts, 'mid')

# Board of Trade: stepped limestone tiers, pyramidal roof, working clock, Ceres.
parts = [box(414, 276, 82, GROUND - 276, '#c9c1a5'), box(427, 244, 56, 32, '#d3c8aa'), box(440, 208, 30, 36, '#d9ceb1')]
for x, y, w, h in [(414, 276, 82, GROUND - 276), (427, 244, 56, 32), (440, 208, 30, 36)]:
    static, glass = windows(x, y, w, h, 4.2, 8, 9.1, 13, lit=.3, glass_color='#a9b8ac', top=5)
    parts += [static, glass]
# Pilasters on the base tier read as the Art Deco verticals.
parts.append('<path d="M424 276v104M444 276v104M466 276v104M486 276v104" stroke="#b7ad90" stroke-width="1.6"/>')
parts.append('<path d="M440 208l15-28 15 28Z" fill="#6c9384"/>'
             '<path d="M455 180v-14m-4 5h8" stroke="#b1b9a2" stroke-width="3"/><circle cx="455" cy="164" r="2.6" fill="#b1b9a2"/>')
CLOCK = (455, 228)
parts.append(f'<circle cx="{CLOCK[0]}" cy="{CLOCK[1]}" r="9" fill="#f2e8c8" stroke="#6b7466" stroke-width="1"/>'
             + ''.join(f'<circle cx="{CLOCK[0] + 6.6 * dx:.1f}" cy="{CLOCK[1] + 6.6 * dy:.1f}" r=".6" fill="#6b7466"/>'
                       for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)])
             + f'<line class="clock-hour" x1="{CLOCK[0]}" y1="{CLOCK[1]}" x2="{CLOCK[0]}" y2="{CLOCK[1] - 4.6}" '
               'stroke="#3b4239" stroke-width="1.5" stroke-linecap="round"/>'
             + f'<line class="clock-minute" x1="{CLOCK[0]}" y1="{CLOCK[1]}" x2="{CLOCK[0]}" y2="{CLOCK[1] - 7}" '
               'stroke="#3b4239" stroke-width="1" stroke-linecap="round"/>'
             + f'<circle cx="{CLOCK[0]}" cy="{CLOCK[1]}" r=".9" fill="#3b4239"/>')
building('board-of-trade', 414, GROUND - 180, parts, 'mid')

# CNA: the warm red slab. Wide ribbon windows, low light density.
parts = [box(582, 244, 61, GROUND - 244, '#b97a62')]
static, glass = windows(582, 244, 61, GROUND - 244, 9.1, 4.9, 12.2, 10.8, lit=.2, glass_color='#d9b7a4', reveal='#5a3529', sill='#e8c9b5', top=4)
parts += [static, glass]
building('cna', 582, GROUND - 244, parts, 'mid')

# Aon: pale vertical fins the full height; windows are the slots between them.
parts = [box(695, 174, 47, GROUND - 174, '#d7d6bd')]
static, glass = windows(695, 174, 47, GROUND - 174, 3.9, 7.7, 10.5, 12.6, lit=.25, glass_color='#a3b5aa', reveal='#6d7f75', sill='#ebe9d6', top=5)
parts += [static, glass]
parts.append(''.join(f'<path d="M{x} 174v206" stroke="#eeeddc" stroke-width="1.4"/>' for x in range(698, 742, 6)))
building('aon', 695, GROUND - 174, parts, 'mid')

# Two Prudential: stepped shaft, diamond pyramid, thin needle.
parts = [box(785, 244, 50, GROUND - 244, '#9cb6a2'), box(795, 220, 30, 24, '#bacab0')]
for x, y, w, h in [(785, 244, 50, GROUND - 244), (795, 220, 30, 24)]:
    static, glass = windows(x, y, w, h, 4.5, 7.0, 9.8, 12.2, lit=.28, glass_color='#dce6d6', reveal='#4c6558', top=4)
    parts += [static, glass]
parts.append('<path d="M795 220l15-27 15 27Z" fill="#749b86"/><path d="M810 193V154" stroke="#7a9784" stroke-width="2"/>')
building('prudential', 785, GROUND - 154, parts, 'mid')

# St. Regis: three interlocking volumes; alternating inward and outward frustums.
parts = []
for x, start, w in [(868, 236, 24), (892, 178, 28), (920, 268, 23)]:
    for k, y in enumerate(range(start, GROUND, 32)):
        h = min(32, GROUND - y)
        inset = 4 if k % 2 else 0
        end = 4 - inset
        fill = ['#5f9a8a', '#8dbaa3'][k % 2]
        parts.append(f'<path d="M{x + inset} {y}h{w - 2 * inset}L{x + w - end} {y + h}H{x + end}Z" fill="{fill}" stroke="#c4d6bc" stroke-width=".7"/>')
        static, glass = windows(x + 3, y + 2, w - 6, h - 4, 3.1, 6.0, 7.7, 10.8, lit=.24, glass_color=shade(fill, 1.25), reveal=shade(fill, .6), sill=shade(fill, 1.4), top=3)
        parts += [static, glass]
    parts.append(f'<path d="M{x + w} {start}l{DX} -{DY}v{GROUND - start}l-{DX} {DY}Z" fill="#4f7a6c"/>')
building('st-regis', 868, GROUND - 178, parts, 'mid')

# The two tall near-lake towers at the right edge anchor this particular view.
parts = [box(1017, 136, 29, GROUND - 136, '#6f9a91'), box(1022, 118, 20, 18, '#8dafa2'),
         '<path d="M1022 118v-14M1038 118v-8" stroke="#8b8f7b" stroke-width="2"/>']
static, glass = windows(1017, 136, 29, GROUND - 136, 4.2, 7.4, 9.5, 12.2, lit=.3, glass_color='#c3d9d0', reveal='#365149', top=5)
parts += [static, glass]
building('lake-north', 1017, GROUND - 104, parts, 'mid')

parts = [box(1090, 248, 25, GROUND - 248, '#8eaa9c'), box(1110, 112, 67, GROUND - 112, '#7aa090')]
static, glass = windows(1110, 112, 67, GROUND - 112, 6.0, 7.7, 15.0, 12.6, lit=.3, glass_color='#cfe0d6', reveal='#3f5c52', top=6)
parts += [static, glass]
parts.append(''.join(f'<path d="M{n(x)} 113v267" stroke="#cbd9c8" stroke-width="1.2"/>' for x in [1114 + 8.6 * i for i in range(8)]))
static, glass = windows(1090, 248, 25, GROUND - 248, 4.2, 7.0, 9.8, 12.2, lit=.26, glass_color='#cfe0d6', reveal='#3f5c52', top=5)
parts += [static, glass]
building('lake-south', 1090, GROUND - 112, parts, 'mid')

# --------------------------------------------------------------------------
# Row 3: South Loop foreground. Low brick and stone volumes that overlap the
# landmark bases so the street line is continuous. Cornices, water tanks,
# rooftop stairs and chimneys are the details that make them read as Chicago.
# --------------------------------------------------------------------------
def brick(name, x, y, w, color, cornice=True, tank=None, penthouse=None, chimney=None, arches=False, stories=None):
    h = GROUND - y
    parts = [box(x, y, w, h, color, dx=12, dy=7)]
    if cornice:
        parts.append(f'<path d="M{n(x - 1.5)} {n(y)}h{n(w + 3)}v2.6h-{n(w + 3)}Z" fill="{shade(color, 1.35)}"/>'
                     f'<path d="M{n(x)} {n(y + 2.6)}h{n(w)}v1.4h-{n(w)}Z" fill="{shade(color, .8)}"/>')
    py = 15 if stories is None else (h - 8) / stories
    static, glass = windows(x, y + 3, w, h - 3, 5.2, 7, 11, py, lit=.34, glass_color='#b9c9bf', reveal=shade(color, .45), sill=shade(color, 1.45), top=6)
    parts += [static, glass]
    # Storefront line at the street.
    parts.append(f'<rect x="{n(x)}" y="{GROUND - 5}" width="{n(w)}" height="5" fill="{shade(color, .82)}"/>')
    if tank:
        tx = x + tank
        parts.append(f'<path d="M{tx} {y - 1}v-10h9v10Z" fill="#8d7a66"/>'
                     f'<path d="M{tx - 1} {y - 11}l5.5-4 5.5 4Z" fill="#6f5f4f"/>'
                     f'<path d="M{tx + 1} {y - 1}v-3M{tx + 8} {y - 1}v-3" stroke="#5a4c3f" stroke-width="1.4"/>')
    if penthouse:
        px, pw = penthouse
        parts.append(box(x + px, y - 7, pw, 7, shade(color, .92), dx=12, dy=7))
    if chimney:
        parts.append(f'<rect x="{x + chimney}" y="{y - 8}" width="3" height="8" fill="{shade(color, .7)}"/>'
                     f'<rect x="{x + chimney - .6}" y="{y - 9}" width="4.2" height="1.4" fill="{shade(color, .55)}"/>')
    building(name, x, h + 12, parts, 'front')


brick('sl-1', 0, 318, 54, '#c5b39a', tank=34)
brick('sl-2', 56, 326, 44, '#b3b8a2', penthouse=(6, 14))
brick('sl-3', 102, 340, 52, '#bb9f82', chimney=42)
brick('sl-4', 156, 304, 78, '#c0ab8d', tank=10, penthouse=(48, 16))
brick('sl-5', 238, 330, 60, '#c3ae8e', chimney=8)
brick('sl-6', 302, 312, 48, '#b89b7e', tank=30)
brick('sl-7', 352, 336, 60, '#c8bda2', penthouse=(6, 18))
brick('sl-8', 416, 346, 56, '#b6bea9', chimney=46)
brick('sl-9', 474, 322, 70, '#b7a68c', tank=52)
brick('sl-10', 548, 338, 44, '#c7bda1')
brick('sl-11', 596, 348, 64, '#bac3ad', penthouse=(40, 16))
brick('sl-12', 664, 316, 44, '#b3977f', tank=6)
brick('sl-13', 712, 340, 58, '#c6bba0', chimney=50)
brick('sl-14', 772, 350, 54, '#b7bea7', penthouse=(4, 14))
brick('sl-15', 830, 326, 44, '#b4bda7', tank=30)
brick('sl-16', 878, 342, 56, '#b7a288', chimney=8)
brick('sl-17', 936, 350, 60, '#a8b9a6', penthouse=(38, 18))
brick('sl-18', 1000, 332, 52, '#b6a48a', tank=38)
brick('sl-19', 1056, 348, 58, '#c4b69b', chimney=48)
brick('sl-20', 1118, 338, 46, '#bcc3ae', tank=12)
brick('sl-21', 1168, 344, 40, '#c1ad91')

# Street line under everything, so the wave has a floor to land on.
out.append(f'<rect class="street" x="0" y="{GROUND - 1}" width="{W}" height="1" fill="#8f8f82" fill-opacity=".45"/>')

BODY = '<defs>' + ''.join(PATTERNS) + '</defs>\n' + '\n'.join(out)
INLINE = (f'<div class="footer-skyline" aria-hidden="true"><svg viewBox="0 0 {W} {H}" '
          f'preserveAspectRatio="xMidYMax slice" focusable="false">\n{BODY}\n</svg></div>')
STANDALONE = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">\n'
              f'<rect width="{W}" height="{H}" fill="#f0efe8"/>\n{BODY}\n</svg>\n')

(PUBLIC / 'skyline.svg').write_text(STANDALONE)
BLOCK = re.compile(r'<div class="footer-skyline" aria-hidden="true">.*?</svg></div>', re.S)
for page in PAGES:
    path = PUBLIC / page
    text = path.read_text()
    updated, count = BLOCK.subn(lambda _: INLINE, text)
    if count != 1:
        raise SystemExit(f'{page}: expected one footer skyline block, found {count}')
    path.write_text(updated)
lit = BODY.count('class="win"')
print(f'skyline: {len(out)} groups, {lit} lit windows, {len(INLINE) / 1024:.1f} KB inline')
for g in out:
    if len(g) > 6000:
        print('  heavy:', g[g.index('data-b="') + 8:g.index('"', g.index('data-b="') + 8)], len(g) // 1024, 'KB')
