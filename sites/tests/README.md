# Hybrid homepage navigation

The document's reading position is the sole chapter authority. Previous/Next
request native smooth scrolling; they do not render a chapter directly. A single
requestAnimationFrame tracker reads stable date/title anchors with 12px of
hysteresis. It can skip any number of chapters on a fast scroll. Only the current
chapter controls site layers, auxiliary overlays, the map view, and the count.

The pending button destination exists solely for rapid-click arithmetic and
completion announcements. Wheel, touch, pointer, and navigation-key input cancels
it without preventing normal browser scrolling. The controller does not require
scrollend, scroll promises, IntersectionObserver, or an animation dependency.
All programmatic map changes explicitly disable animation.

## Integration

Only `public/map.js` and the new `public/map-story.css` affect production. The map
entrypoint loads its scoped stylesheet relative to its own URL. It also accepts
an already-loaded element with ID `railyards-story-styles`, for a future static
stylesheet link. This avoids rewriting the generated inline skyline or changing
the shared stylesheet's behavior on other pages. The original HTML, seven beats,
copy, geographic payload, image credits, and footer are retained.

At enhancement time, the existing nav is moved below the map canvas. Explore's
tools/detail panel move into the final chapter so revealing them cannot resize
the map. Failed chapter images retain their aspect-ratio frames. The compact
phone map is 30svh, clamped to 160–260px, plus a 64px navigation strip; short
landscape screens use normal flow. The wide layout remains text-left/map-right.

## Browser tests

These are optional developer tools, not production dependencies:

```sh
python -m pip install playwright
python -m playwright install chromium
python sites/tests/test_story_navigation.py
```

By default the suite replaces Leaflet with a small explicit adapter to test
navigation and layer orchestration without tile/network noise. To run against
the repository's actual vendored Leaflet:

```sh
LEAFLET_STUB=0 python sites/tests/test_story_navigation.py
python -m playwright install webkit
BROWSER=webkit LEAFLET_STUB=0 python sites/tests/test_story_navigation.py
```

`OFFLINE_DOM=1` loads the HTML/CSS/scripts directly into Chromium without browser
navigation. URL queries and pageshow are simulated in that mode. This is useful
in restricted environments, but it does not verify the asset-loading path,
real map rendering, browser history restoration, or real touch gestures.

Coverage includes full forward/back traversal, fast free scrolling, rapid Next
clicks and reversal, input interruption, phone/tablet landing offsets, Explore
layer cleanup and view preservation, viewport changes, reduced motion, keyboard
focus, deep-link state, and failed-image geometry.

## Manual release gate

Before merging/deploying, check the actual page in iPhone Safari and a desktop
browser with real tiles, at 375x667 and 390x844 portrait, short landscape, and
with enlarged text. Check a swipe starting on the map/nav, interruption of Next
with a real touch gesture, CSS first-load/cached-load, ?place=upCanalYard, browser
Back/Forward, and reduced-motion changes while navigation is in progress.

Test record for this change: offline Chromium checks used the implementation
with a reconstructed homepage markup/style fixture and the explicit Leaflet
adapter. Full deployed-site rendering, real Leaflet, and real Safari were not
executable in the authoring environment. The fixtures replacing local index,
shared CSS, and geographic data are NOT repository changes.
