# Chicago skyline footer

The shared footer adapts the user's cream-and-sage city/footer reference into a decorative miniature Chicago skyline. Muted stone, sage glass, shallow side faces, and sparse warm windows connect the illustration to the site's architectural subject without competing with the page content. Landmark proportions and placement are stylized; this is not a surveyed geographic panorama or reconstruction evidence.

## Implementation

- `sites/public/skyline.svg` owns the shared external SVG symbols, referenced with `<use>` from `index.html`, `gallery.html`, `3d.html`, and `build.html`.
- Landmark IDs are `franklin`, `wacker`, `willis`, `trade`, `trump`, `aon`, `prudential`, and `regis`; `neighborhood` supplies the foreground buildings and `lights` supplies the warm windows.
- Each page has one footer with nine building groups. The illustration is decorative (`aria-hidden="true"`, SVG `focusable="false"`); disclosure and source links remain ordinary accessible content.
- `site.js` starts the arrival once the skyline reaches a 20% intersection threshold, then disconnects the observer. `site.css` staggers a 1.4-second rise by 65 milliseconds per group and adds a delayed, brief window-light sequence.
- Buildings are visible by default, so missing JavaScript or IntersectionObserver leaves a complete static skyline. The optional warm lights remain off in that fallback.
- Reduced motion disables both animations and shows the lights statically.
- At widths up to 700 pixels, the SVG expands to 150% with a centered crop. This keeps the towers legible while the footer contains horizontal overflow; outer buildings are intentionally cropped.

## Validation at delivery

The implementation pass reported a successful 76-file build, no desktop/mobile horizontal overflow or browser errors, and one footer with nine building groups on all four routes. Reduced-motion checks reported no animation. Desktop and mobile screenshots were visually inspected for composition, disclosure wrapping, and the intended crop.

`/tmp/chicago-footer-desktop.png` and `/tmp/chicago-footer-mobile.png` are ephemeral local review captures, not durable deliverable assets or proof of hosted deployment. Re-run browser checks and capture fresh evidence after changing the SVG, footer markup, motion, or responsive rules.
