(function () {
  'use strict';

  var root = document.getElementById('railyards-map');
  var data = window.RailyardsMapData;
  if (!root || !window.L || !data) return;

  var L = window.L;
  var origin = data.origin;
  var latScale = 1 / 110900;
  var lonScale = 1 / (111320 * Math.cos(origin.latitude_reference * Math.PI / 180));
  var homeOffset = origin.home_offset_xy_m || [0, 0];
  var stadiumCenter = [
    origin.latitude_reference - homeOffset[1] * latScale,
    origin.longitude_reference - (homeOffset[0] + 33) * lonScale
  ];

  var map = L.map(root, {
    center: stadiumCenter,
    zoom: 14,
    zoomSnap: 0.5,
    minZoom: 12,
    maxZoom: 17,
    scrollWheelZoom: false
  });
  map.attributionControl.setPrefix('');
  map.on('focus', function () { map.scrollWheelZoom.enable(); });
  map.on('blur', function () { map.scrollWheelZoom.disable(); });

  var esri = 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/';
  L.tileLayer(esri + 'World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 17,
    attribution: 'Basemap &copy; <a href="https://www.esri.com/en-us/legal/terms/services">Esri</a> · Footprints &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors · CTA lines: City of Chicago'
  }).addTo(map);
  L.tileLayer(esri + 'World_Light_Gray_Reference/MapServer/tile/{z}/{y}/{x}', { maxZoom: 17, pane: 'shadowPane', opacity: 0.9 }).addTo(map);

  var renderer = L.svg({ padding: 0.6 }).addTo(map);
  function addPatterns() {
    var container = renderer._container;
    if (!container || container.querySelector('defs.map-patterns')) return;
    var defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    defs.setAttribute('class', 'map-patterns');
    defs.innerHTML =
      '<pattern id="hatch-facility" patternUnits="userSpaceOnUse" width="8" height="8" patternTransform="rotate(45)"><rect width="8" height="8" fill="#f7dad8"/><line x1="0" y1="0" x2="0" y2="8" stroke="#c94a45" stroke-width="3"/></pattern>' +
      '<pattern id="hatch-site" patternUnits="userSpaceOnUse" width="8" height="8" patternTransform="rotate(-45)"><rect width="8" height="8" fill="#eef1e6"/><line x1="0" y1="0" x2="0" y2="8" stroke="#6b7f63" stroke-width="2"/></pattern>' +
      '<pattern id="hatch-construction" patternUnits="userSpaceOnUse" width="8" height="8" patternTransform="rotate(45)"><rect width="8" height="8" fill="#fbeed0"/><line x1="0" y1="0" x2="0" y2="8" stroke="#d29a2c" stroke-width="2"/></pattern>';
    container.insertBefore(defs, container.firstChild);
  }
  addPatterns();
  map.on('zoomend moveend', addPatterns);

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function pointsFromLocal(points) {
    return points.map(function (point) {
      return [
        origin.latitude_reference + (point[1] - homeOffset[1]) * latScale,
        origin.longitude_reference + (point[0] - homeOffset[0] - 33) * lonScale
      ];
    });
  }

  var statusLabels = { existing: 'Existing', underConstruction: 'Under construction', proposed: 'Proposed' };

  var detailNodes = {
    status: document.querySelector('[data-map-detail-status]'),
    title: document.querySelector('[data-map-detail-title]'),
    copy: document.querySelector('[data-map-detail-copy]'),
    link: document.querySelector('[data-map-detail-link]')
  };
  function showDetail(feature) {
    if (detailNodes.status) {
      detailNodes.status.textContent = statusLabels[feature.status];
      detailNodes.status.setAttribute('data-status', feature.status);
    }
    if (detailNodes.title) detailNodes.title.textContent = feature.title;
    if (detailNodes.copy) detailNodes.copy.textContent = feature.copy;
    if (detailNodes.link) {
      detailNodes.link.textContent = feature.sourceLabel;
      detailNodes.link.href = feature.source;
    }
  }

  var places = {};
  function register(feature) {
    var layers = feature.layer instanceof L.LayerGroup ? feature.layer.getLayers() : [feature.layer];
    layers.forEach(function (layer) {
      layer.bindTooltip('<span data-status="' + feature.status + '">' + escapeHtml(statusLabels[feature.status]) + '</span>' + escapeHtml(feature.title), { sticky: true, className: 'map-tip', direction: 'top', offset: [0, -8] });
      layer.on('click', function () { showDetail(feature); });
    });
    feature.layer.addTo(map);
    places[feature.id] = feature;
  }

  function label(kind, text, minZoom, position) {
    var glyphs = {
      station: '<svg viewBox="0 0 20 20" aria-hidden="true"><rect x="4" y="2.5" width="12" height="12.5" rx="2.5" fill="#fff"/><rect x="6" y="4.5" width="8" height="4.5" rx="1" fill="currentColor"/><circle cx="7.4" cy="11.8" r="1.2" fill="currentColor"/><circle cx="12.6" cy="11.8" r="1.2" fill="currentColor"/><path d="M6 15.5l-1.6 2.5M14 15.5l1.6 2.5" stroke="#fff" stroke-width="1.6" stroke-linecap="round"/></svg>',
      parking: '<svg viewBox="0 0 20 20" aria-hidden="true"><rect x="2" y="2" width="16" height="16" rx="3"/><text x="10" y="14.6" text-anchor="middle" font-size="12" font-weight="700" fill="#fff" font-family="system-ui,sans-serif">P</text></svg>',
      ballpark: '<svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="7.5"/><path d="M5.2 5.4c2.4 1 3.6 2.9 3.6 4.6s-1.2 3.6-3.6 4.6M14.8 5.4c-2.4 1-3.6 2.9-3.6 4.6s1.2 3.6 3.6 4.6" stroke="#fff" stroke-width="1.4" fill="none" stroke-linecap="round"/></svg>',
      text: ''
    };
    var icon = L.divIcon({
      className: 'map-marker map-marker-' + kind + ' label-min-' + minZoom,
      html: (glyphs[kind] ? '<span class="map-marker-glyph">' + glyphs[kind] + '</span>' : '') + '<span class="map-marker-label">' + escapeHtml(text) + '</span>',
      iconSize: kind === 'text' ? [0, 0] : [24, 24],
      iconAnchor: kind === 'text' ? [0, 0] : [12, 12]
    });
    return L.marker(position, { icon: icon, zIndexOffset: kind === 'text' ? 0 : 200, keyboard: kind !== 'text' });
  }

  var sites = data.sites || {};

  /* The three sites the story is about, plus Rate Field. */
  register({
    id: 'amtrakYard', status: 'existing',
    title: 'Amtrak yard today',
    copy: 'About 47 acres between Roosevelt Road, 18th Street, Canal Street and the river, where Amtrak services its Midwest fleet. Justin Ishbia’s Shore Capital Partners is under contract to buy it once Amtrak moves out.',
    source: 'sources.html#suntimes-2026-08-14', sourceLabel: 'Sun-Times · Aug 14, 2026',
    position: [41.8625, -87.6362], zoom: 15,
    layer: L.layerGroup([
      L.polygon(sites.amtrakYard, { renderer: renderer, color: '#6b7f63', weight: 2, dashArray: '6 5', fillColor: 'url(#hatch-site)', fillOpacity: 1 }),
      label('text', 'Amtrak yard today', 14, [41.8598, -87.6362])
    ])
  });

  register({
    id: 'stadium', status: 'proposed',
    title: 'The Railyards',
    copy: 'Canal Edge’s proposed White Sox ballpark on the Amtrak yard, unveiled September 5, 2026 with AECOM renderings. The White Sox are studying it over several months; no architect, financing or date is set. The footprint is our reconstruction, not a site plan.',
    source: 'sources.html#blockclub-2026-09-06', sourceLabel: 'Block Club · Sept 6, 2026',
    position: stadiumCenter, zoom: 16,
    layer: L.layerGroup([
      L.polygon(pointsFromLocal(data.bowlFront.concat(data.bowlBack.slice().reverse())), { renderer: renderer, color: '#294638', weight: 2, fillColor: '#7d9a80', fillOpacity: 0.55 }),
      L.polygon(pointsFromLocal(data.fieldBoundary), { renderer: renderer, color: '#294638', weight: 1.5, fillColor: '#8fb28a', fillOpacity: 0.9 }),
      label('ballpark', 'The Railyards', 11, stadiumCenter)
    ])
  });

  register({
    id: 'upCanalYard', status: 'proposed',
    title: 'Amtrak’s new facility · Bridgeport',
    copy: 'Amtrak plans a 24-hour maintenance facility on Union Pacific’s Canal Street yard, which runs from Cermak Road to Pershing Road beside Rate Field. The shop building would sit between 33rd and 35th Streets, about 100 feet from homes. Up to $572 million is federal, $125 million comes from Canal Edge. Amtrak targets a fall 2026 start and about 18 months of work. Bridgeport and Chinatown residents and their elected officials oppose it.',
    source: 'sources.html#amtrak-2026-08-14', sourceLabel: 'Amtrak · Aug 14, 2026',
    position: [41.836, -87.6373], zoom: 14,
    layer: L.layerGroup([
      L.polygon(sites.upCanalYard, { renderer: renderer, color: '#c94a45', weight: 2, fillColor: 'url(#hatch-facility)', fillOpacity: 1 }),
      label('text', 'Amtrak’s new facility', 12, [41.8335, -87.6373])
    ])
  });

  register({
    id: 'the78', status: 'underConstruction',
    title: 'McDonald’s Park · The 78',
    copy: 'The Chicago Fire’s 22,000-seat soccer stadium at The 78, across the river from the ballpark site. Ground broke March 3, 2026; the target opening is 2028.',
    source: 'sources.html#chicagofire-2026-03-03', sourceLabel: 'Chicago Fire · Mar 3, 2026',
    position: [41.8637, -87.6325], zoom: 15,
    layer: L.layerGroup([
      L.polygon(sites.the78, { renderer: renderer, color: '#c48a1a', weight: 2, fillColor: 'url(#hatch-construction)', fillOpacity: 1 }),
      label('text', 'McDonald’s Park', 14, [41.8622, -87.6322])
    ])
  });

  register({
    id: 'rateField', status: 'existing',
    title: 'Rate Field',
    copy: 'The White Sox’s current home, owned by the state. The lease and the state’s remaining stadium bonds both run through 2029. The proposed Amtrak facility would be directly west of it.',
    source: 'sources.html#suntimes-2024-02-08', sourceLabel: 'Sun-Times · Feb 8, 2024',
    position: [41.8299, -87.6338], zoom: 15,
    layer: L.layerGroup([
      L.polygon(sites.rateField, { renderer: renderer, color: '#4a5a4f', weight: 1.5, fillColor: '#c9cfc6', fillOpacity: 0.8 }),
      label('ballpark', 'Rate Field', 11, [41.8299, -87.6338])
    ])
  });

  /* Transit near the ballpark site. */
  var ctaColors = { 'Blue Line': '#347ab4', 'Red Line': '#c94a45', 'Orange Line': '#d47c35', 'Green Line': '#4b8b62' };
  L.geoJSON(data.cta, {
    style: function (feature) {
      var line = feature && feature.properties ? feature.properties.lines : '';
      return { renderer: renderer, color: ctaColors[line] || '#8a8f86', weight: 3.5, opacity: 0.85, lineCap: 'round', lineJoin: 'round', interactive: false };
    }
  }).addTo(map);

  [
    ['ctaRoosevelt', 'Roosevelt', 'Red, Orange and Green lines. About a 15 minute walk to the ballpark site over the Roosevelt Road bridge.', 13],
    ['ctaClintonBlue', 'Clinton', 'Blue Line, near Union Station. About a 20 minute walk to the site.', 14],
  ].forEach(function (station) {
    var position = data.stations[station[0]];
    register({
      id: station[0], status: 'existing',
      title: 'CTA · ' + station[1],
      copy: station[2] + ' Check CTA for service and accessibility.',
      source: 'https://www.transitchicago.com/', sourceLabel: 'CTA ↗',
      position: position, zoom: 15,
      layer: label('station', station[1], station[3], position)
    });
  });
  register({
    id: 'unionStation', status: 'existing',
    title: 'Union Station',
    copy: 'Amtrak and Metra terminal about a mile north of the site. No Metra stop exists at the site, and none has been announced.',
    source: 'sources.html#metra', sourceLabel: 'Metra',
    position: data.stations.unionStation, zoom: 15,
    layer: label('station', 'Union Station', 14, data.stations.unionStation)
  });

  /* Parking near the ballpark site. Nothing has been announced. */
  register({
    id: 'grantParkSouth', status: 'existing',
    title: 'Grant Park South Garage',
    copy: 'The closest large downtown garage, about a mile from the site. The renderings show no parking; Canal Edge says it will be worked out later.',
    source: 'sources.html#fieldofschemes-2026-09-08', sourceLabel: 'Field of Schemes · Sept 8, 2026',
    position: data.parking.grantParkSouth, zoom: 15,
    layer: label('parking', 'Grant Park garage', 15, data.parking.grantParkSouth)
  });

  /* Extents */
  var views = {
    overview: { bounds: L.latLngBounds([[41.822, -87.652], [41.887, -87.616]]), place: 'stadium' },
    stadium: { bounds: L.latLngBounds([[41.8555, -87.6435], [41.8705, -87.6265]]), place: 'stadium' },
    bridgeport: { bounds: L.latLngBounds([[41.8205, -87.6465], [41.8555, -87.6245]]), place: 'upCanalYard' }
  };
  function setPressed(selector, match) {
    document.querySelectorAll(selector).forEach(function (button) {
      button.setAttribute('aria-pressed', button === match ? 'true' : 'false');
    });
  }
  function setView(name) {
    var view = views[name] || views.overview;
    map.fitBounds(view.bounds, { padding: [12, 12] });
    showDetail(places[view.place]);
    setPressed('[data-map-view]', document.querySelector('[data-map-view="' + name + '"]'));
    setPressed('[data-map-focus]', name === 'stadium' ? document.querySelector('[data-map-focus="stadium"]') : name === 'bridgeport' ? document.querySelector('[data-map-focus="upCanalYard"]') : null);
  }
  document.querySelectorAll('[data-map-view]').forEach(function (button) {
    button.addEventListener('click', function () { setView(button.getAttribute('data-map-view')); });
  });

  function focusPlace(id, button) {
    var place = places[id];
    if (!place) return;
    showDetail(place);
    map.flyTo(place.position, place.zoom, { duration: 0.8 });
    setPressed('[data-map-view]', null);
    setPressed('[data-map-focus]', button || null);
  }
  var placeSelect = document.querySelector('[data-map-place]');
  if (placeSelect) placeSelect.addEventListener('change', function () { focusPlace(placeSelect.value); });
  document.querySelectorAll('[data-map-focus]').forEach(function (button) {
    button.addEventListener('click', function () {
      focusPlace(button.getAttribute('data-map-focus'), button);
      root.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    });
  });

  function updateZoomClasses() {
    var zoom = map.getZoom();
    [12, 13, 14, 15].forEach(function (level) { root.classList.toggle('zoom-lt-' + level, zoom < level); });
  }
  map.on('zoomend', updateZoomClasses);
  updateZoomClasses();

  var requested = new URLSearchParams(window.location.search).get('place');
  setView('stadium');
  if (requested && places[requested]) focusPlace(requested);
  window.setTimeout(function () { map.invalidateSize(); }, 0);
})();
