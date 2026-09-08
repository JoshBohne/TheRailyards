# Chicago skyline footer

The shared footer adapts the user's cream-and-sage city/footer reference into a decorative miniature Chicago skyline. Muted stone, sage glass, shallow side faces, and sparse warm windows connect the illustration to the site's architectural subject without competing with the page content. The current composition follows the user-supplied ballpark-view image: Willis at the left, a dense layered Loop roofline, and two tall near-lake towers at the right. Landmark silhouettes and proportions are deliberately emphasized over literal photo matching. Generic background buildings recede at reduced opacity, and most foreground filler has been removed; this remains a decorative panorama, not surveyed reconstruction evidence.

## Implementation

- `sites/public/skyline.svg` owns the shared external SVG symbols, referenced with `<use>` from `index.html`, `gallery.html`, `3d.html`, and `build.html`.
- `sites/generate-skyline.py` regenerates the SVG. Landmark groups emphasize Willis, the 311 South Wacker crown, Board of Trade clock and stepped pyramid, CNA and Aon, Two Prudential, St. Regis, and the near-lake towers. The anonymous limestone crown and background roofline remain reference-inspired. `lights` supplies the warm windows.
- Each page has one footer with eleven building groups. The illustration is decorative (`aria-hidden="true"`, SVG `focusable="false"`); disclosure and source links remain ordinary accessible content.
- `site.js` starts the arrival once the skyline reaches a 20% intersection threshold, then disconnects the observer. `site.css` staggers a 1.4-second rise by 55 milliseconds per group and adds a delayed, brief window-light sequence.
- Buildings are visible by default, so missing JavaScript or IntersectionObserver leaves a complete static skyline. The optional warm lights remain off in that fallback.
- Reduced motion disables both animations and shows the lights statically.
- The SVG scales to the full available width on phones, preserving both ends of the reference panorama.

## Validation at delivery

The implementation pass reported a successful 76-file build, no desktop/mobile horizontal overflow or browser errors, and one footer with eleven building groups on all four routes. Reduced-motion checks reported no animation. Desktop and mobile screenshots were visually inspected for composition, disclosure wrapping, and the complete skyline.

`/tmp/chicago-icons-desktop.png` and `/tmp/chicago-icons-mobile.png` are ephemeral local review captures, not durable deliverable assets or proof of hosted deployment. Re-run browser checks and capture fresh evidence after changing the SVG, footer markup, motion, or responsive rules.

Landmark detail references: [Studio Gang: St. Regis](https://studiogang.com/projects/vista-tower/) describes three volumes with alternating frustums; [311 South Wacker tenant handbook](https://zeller.us/311southwacker/wp-content/uploads/sites/14/2023/01/02.-311-S.-Wacker-Tenant-Handbook-Update-2022.pdf) documents its illuminated crown.
