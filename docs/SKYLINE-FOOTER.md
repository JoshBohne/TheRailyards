# Chicago skyline footer

The shared footer is a decorative miniature Chicago skyline in the site's cream-and-sage palette. It follows the user-supplied ballpark-view reference: Willis at the left, a dense layered Loop roofline, and two tall near-lake towers at the right. Landmark silhouettes are emphasized over literal photo matching; this remains a decorative panorama, not surveyed reconstruction evidence.

The current version was rebuilt the way the footer that inspired it was built (Emil Hovv's thread, September 8, 2026): wireframe first, then per-building facade instructions, then details, then motion.

1. **Wireframe.** One oblique camera for every block, slightly above and to the right, so each roof is a parallelogram and each right face is visible. Three overlapping rows: a hazed distant roofline, the landmark row, and a continuous South Loop foreground so the street line has no gaps.
2. **Facades.** Every window is recessed (dark reveal) with a projecting sill. Each landmark keeps its proportions and gets its own rule: Willis's dark bundled tubes and belt bands, the 311 South Wacker octagonal shaft and lit crown, Board of Trade limestone tiers with pilasters and pyramid, CNA's red ribbon windows, Aon's full-height fins, Two Prudential's diamond and needle, St. Regis's alternating frustums, and the near-lake glass towers. Foreground brick carries cornices, water tanks, rooftop stairs and chimneys.
3. **Details.** The Board of Trade clock tells the current time in Chicago (`America/Chicago` via `Intl`, refreshed every 30 seconds). Roughly a third of the windows light on their own: each has its own phase, period and warmth, and fades slowly on and off.
4. **Motion.** When the footer scrolls into view the buildings rise in a wave from left to right; the delay follows the x position and taller buildings take longer to settle, with a slight overshoot. The window lights begin only after the wave ends.

## Implementation

- `sites/generate-skyline.py` builds the SVG and inlines it into `index.html`, `gallery.html`, `3d.html`, and `build.html`, replacing the `<div class="footer-skyline">` block. Run it after any change; the four pages must stay identical. It also writes `sites/public/skyline.svg` as a standalone review copy (nothing references it).
- The SVG is inline rather than `<use>`d from an external file because per-window animation and the clock need the page's CSS and JS to reach individual elements, which an external `<use>` shadow tree does not allow.
- Unlit window grids are one `<pattern>` tile per facade; only windows that light up are their own `<rect class="win">` with inline `--d`, `--t` and `--c` custom properties. The window selection is seeded, so the output is reproducible. The inline block is about 70 KB per page.
- `site.js` adds `skyline-arriving` at a 20% intersection threshold, then disconnects the observer, and drives the two clock hands with `--angle` and `--clock-origin`.
- `site.css` owns the rise (`--rd` delay, `--rt` duration per building), the `win-glow` cycle, and the clock transforms. The SVG uses `preserveAspectRatio="xMidYMax slice"` inside a 1600px-wide, 480px-tall cap, so the widest viewports crop a little empty sky rather than letterboxing the sides.
- Buildings are visible by default, so missing JavaScript or IntersectionObserver leaves a complete static skyline with unlit windows and a clock at twelve. The illustration is `aria-hidden="true"`; disclosure and source links remain ordinary accessible content.
- Reduced motion disables the rise and the glow and shows the lit windows statically.

## Validation at delivery

Playwright checks on the local template directory (September 9, 2026): all four routes carry one footer with 59 building groups and 243 lit windows; no horizontal overflow at 1440 or 390 wide; no console errors beyond the pre-existing 404s for media that only exists in a hosted release; clock hand angles matched Chicago time; reduced motion reported no animation and static warm windows. A mid-wave capture confirmed the left-to-right order.

Screenshots taken during development are ephemeral. Re-run browser checks and capture fresh evidence after changing the generator, footer markup, motion, or responsive rules.

Landmark detail references: [Studio Gang: St. Regis](https://studiogang.com/projects/vista-tower/) describes three volumes with alternating frustums; [311 South Wacker tenant handbook](https://zeller.us/311southwacker/wp-content/uploads/sites/14/2023/01/02.-311-S.-Wacker-Tenant-Handbook-Update-2022.pdf) documents its illuminated crown.
