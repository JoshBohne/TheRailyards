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
  /* Map-only display offset: keeps the illustrative footprint inside the Amtrak parcel and level with McDonald's Park across the river, as the renderings show. */
  var displayOffset = [-0.0018, 0.0005];
  var stadiumCenter = [
    origin.latitude_reference - homeOffset[1] * latScale + displayOffset[0],
    origin.longitude_reference - (homeOffset[0] + 33) * lonScale + displayOffset[1]
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
    maxZoom: 17, maxNativeZoom: 16,
    attribution: 'Basemap &copy; <a href="https://www.esri.com/en-us/legal/terms/services">Esri</a> · Footprints &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors · CTA lines: City of Chicago'
  }).addTo(map);
  var streetLabels = L.tileLayer(esri + 'World_Light_Gray_Reference/MapServer/tile/{z}/{y}/{x}', { maxZoom: 17, maxNativeZoom: 16, pane: 'shadowPane', opacity: 0.9 }).addTo(map);
  var imagery = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 17,
    attribution: 'Imagery &copy; <a href="https://www.esri.com/en-us/legal/terms/services">Esri</a>, Maxar, Earthstar Geographics'
  });
  var basemap = 'map';
  function setBasemap(name) {
    basemap = name;
    var satellite = name === 'satellite';
    if (satellite) { map.removeLayer(streetLabels); imagery.addTo(map); }
    else { map.removeLayer(imagery); streetLabels.addTo(map); }
    root.classList.toggle('is-satellite', satellite);
    document.querySelectorAll('[data-map-basemap]').forEach(function (button) {
      button.setAttribute('aria-pressed', button.getAttribute('data-map-basemap') === name ? 'true' : 'false');
    });
  }
  document.querySelectorAll('[data-map-basemap]').forEach(function (button) {
    button.addEventListener('click', function () { setBasemap(button.getAttribute('data-map-basemap')); });
  });

  var renderer = L.svg({ padding: 0.6 }).addTo(map);
  function addPatterns() {
    var container = renderer._container;
    if (!container || container.querySelector('defs.map-patterns')) return;
    var defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    defs.setAttribute('class', 'map-patterns');
    defs.innerHTML =
      '<pattern id="hatch-facility" patternUnits="userSpaceOnUse" width="8" height="8" patternTransform="rotate(45)"><rect width="8" height="8" fill="#f7dad8"/><line x1="0" y1="0" x2="0" y2="8" stroke="#c94a45" stroke-width="3"/></pattern>' +
      '<pattern id="hatch-facility-sat" patternUnits="userSpaceOnUse" width="10" height="10" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="10" stroke="#ff5a4f" stroke-width="2"/></pattern>' +
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
  function convexHull(points) {
    var sorted = points.slice().sort(function (a, b) { return a[0] - b[0] || a[1] - b[1]; });
    function cross(o, a, b) { return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]); }
    var lower = [], upper = [];
    sorted.forEach(function (point) {
      while (lower.length >= 2 && cross(lower[lower.length - 2], lower[lower.length - 1], point) <= 0) lower.pop();
      lower.push(point);
    });
    sorted.slice().reverse().forEach(function (point) {
      while (upper.length >= 2 && cross(upper[upper.length - 2], upper[upper.length - 1], point) <= 0) upper.pop();
      upper.push(point);
    });
    return lower.slice(0, -1).concat(upper.slice(0, -1));
  }
  /* Field fan: home plate at the model origin, foul lines along the local axes, outfield arc through the boundary points. */
  function fieldOutline() {
    var arc = data.fieldBoundary;
    var out = [[0, 0]];
    for (var i = 0; i < arc.length - 1; i++) {
      var a = arc[i], b = arc[i + 1];
      for (var t = 0; t < 1; t += 0.25) out.push([a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]);
    }
    out.push(arc[arc.length - 1]);
    return out;
  }
  function pointsFromLocal(points) {
    return points.map(function (point) {
      return [
        origin.latitude_reference + (point[1] - homeOffset[1]) * latScale + displayOffset[0],
        origin.longitude_reference + (point[0] - homeOffset[0] - 33) * lonScale + displayOffset[1]
      ];
    });
  }

  var statusLabels = { existing: 'Existing', underConstruction: 'Under construction', proposed: 'Proposed', concept: 'Concept · unfunded', rendering: 'Published rendering' };

  var detailNodes = {
    status: document.querySelector('[data-map-detail-status]'),
    title: document.querySelector('[data-map-detail-title]'),
    copy: document.querySelector('[data-map-detail-copy]'),
    link: document.querySelector('[data-map-detail-link]'),
    figure: document.querySelector('[data-map-detail-figure]'),
    image: document.querySelector('[data-map-detail-image]')
  };
  function showDetail(feature) {
    if (detailNodes.status) {
      detailNodes.status.textContent = statusLabels[feature.status];
      detailNodes.status.setAttribute('data-status', feature.status);
    }
    if (detailNodes.title) detailNodes.title.textContent = feature.title;
    if (detailNodes.figure && detailNodes.image) {
      detailNodes.figure.hidden = !feature.image;
      if (feature.image) { detailNodes.image.src = feature.image; detailNodes.image.alt = feature.imageAlt || feature.title; }
      else detailNodes.image.removeAttribute('src');
    }
    if (detailNodes.copy) detailNodes.copy.textContent = feature.copy;
    var panel = detailNodes.figure && detailNodes.figure.closest('.map-detail');
    if (panel && window.innerWidth <= 900 && panel.offsetParent && (feature.image || feature.userSelected)) panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    if (detailNodes.link) {
      detailNodes.link.textContent = feature.sourceLabel;
      detailNodes.link.href = feature.source;
    }
  }

  var places = {};
  function register(feature) {
    var layers = feature.layer instanceof L.LayerGroup ? feature.layer.getLayers() : [feature.layer];
    layers.forEach(function (layer) {
      layer.on('click', function () { feature.userSelected = true; showDetail(feature); feature.userSelected = false; });
    });
    feature.layer.addTo(feature.group || map);
    places[feature.id] = feature;
  }

  function label(kind, text, minZoom, position) {
    var glyphs = {
      station: '<svg viewBox="0 0 20 20" aria-hidden="true"><rect x="4" y="2.5" width="12" height="12.5" rx="2.5" fill="#fff"/><rect x="6" y="4.5" width="8" height="4.5" rx="1" fill="currentColor"/><circle cx="7.4" cy="11.8" r="1.2" fill="currentColor"/><circle cx="12.6" cy="11.8" r="1.2" fill="currentColor"/><path d="M6 15.5l-1.6 2.5M14 15.5l1.6 2.5" stroke="#fff" stroke-width="1.6" stroke-linecap="round"/></svg>',
      parking: '<svg viewBox="0 0 20 20" aria-hidden="true"><rect x="2" y="2" width="16" height="16" rx="3"/><text x="10" y="14.6" text-anchor="middle" font-size="12" font-weight="700" fill="#fff" font-family="system-ui,sans-serif">P</text></svg>',
      ballpark: '<svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="7.5"/><path d="M5.2 5.4c2.4 1 3.6 2.9 3.6 4.6s-1.2 3.6-3.6 4.6M14.8 5.4c-2.4 1-3.6 2.9-3.6 4.6s1.2 3.6 3.6 4.6" stroke="#fff" stroke-width="1.4" fill="none" stroke-linecap="round"/></svg>',
      boat: '<svg viewBox="0 0 20 20" aria-hidden="true"><rect x="2" y="2" width="16" height="16" rx="3"/><path d="M5 12.5h10l-1.6 3H6.6z" fill="#fff"/><path d="M9.2 5v6.5M9.2 5l4 4.5h-4" stroke="#fff" stroke-width="1.4" fill="none" stroke-linejoin="round"/></svg>',
      soccer: '<svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="7.5"/><path d="M10 5.2l3.2 2.3-1.2 3.8H8l-1.2-3.8z" fill="#fff"/><path d="M10 5.2V2.8M13.2 7.5l2.6-.9M12 11.3l1.6 2.2M8 11.3l-1.6 2.2M6.8 7.5l-2.6-.9" stroke="#fff" stroke-width="1.2"/></svg>',
      camera: '<svg viewBox="0 0 20 20" aria-hidden="true"><rect x="2" y="2" width="16" height="16" rx="3"/><path d="M5.5 7.5h2.2l1-1.5h2.6l1 1.5h2.2a1 1 0 0 1 1 1V14a1 1 0 0 1-1 1h-9a1 1 0 0 1-1-1V8.5a1 1 0 0 1 1-1z" fill="#fff"/><circle cx="10" cy="11.2" r="2" fill="currentColor"/></svg>',
      concept: '<svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="6.5" fill="#fff" stroke="currentColor" stroke-width="2.5" stroke-dasharray="3 2.2"/></svg>',
      area: '',
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
    copy: '47 acres on the river where Amtrak services its Midwest fleet. Ishbia’s Shore Capital is under contract to buy it once Amtrak leaves.',
    source: 'sources.html#suntimes-2026-08-14', sourceLabel: 'Sun-Times · Aug 14, 2026',
    position: [41.8625, -87.6362], zoom: 15,
    layer: L.layerGroup([
      L.polygon(sites.amtrakYard, { renderer: renderer, color: '#6b7f63', weight: 2, dashArray: '6 5', fillColor: 'url(#hatch-site)', fillOpacity: 1, className: 'map-site-fill' }),
      label('text', 'Amtrak yard today', 14, [41.8598, -87.6362])
    ])
  });

  register({
    id: 'stadium', status: 'proposed',
    title: 'The Railyards',
    copy: 'Canal Edge’s proposed White Sox ballpark, unveiled September 5, 2026. Under study; no architect, financing or date yet.',
    source: 'sources.html#blockclub-2026-09-06', sourceLabel: 'Block Club · Sept 6, 2026',
    position: stadiumCenter, zoom: 15,
    layer: L.layerGroup([
      L.polygon(pointsFromLocal(convexHull(data.bowlBack.concat(data.fieldBoundary))), { renderer: renderer, color: '#294638', weight: 2, fillColor: '#5f7a66', fillOpacity: 0.85, className: 'map-site-fill' }),
      L.polygon(pointsFromLocal(fieldOutline()), { renderer: renderer, stroke: false, fillColor: '#8fbf84', fillOpacity: 1, interactive: false }),
      L.polygon(pointsFromLocal([[0, 0], [27.43, 0], [27.43, 27.43], [0, 27.43]]), { renderer: renderer, stroke: false, fillColor: '#c9a978', fillOpacity: 1, interactive: false }),
      L.polygon(pointsFromLocal([[5, 5], [23, 5], [23, 23], [5, 23]]), { renderer: renderer, stroke: false, fillColor: '#8fbf84', fillOpacity: 1, interactive: false }),
      L.circle([0, 0].length ? pointsFromLocal([[0, 0]])[0] : stadiumCenter, { renderer: renderer, radius: 4, stroke: false, fillColor: '#c9a978', fillOpacity: 1, interactive: false }),
      label('ballpark', 'The Railyards', 11, [stadiumCenter[0] + 0.0011, stadiumCenter[1] - 0.0004])
    ])
  });

  register({
    id: 'upCanalYard', status: 'proposed',
    title: 'Amtrak’s new facility · Bridgeport',
    copy: 'Union Pacific’s existing Canal Street rail yard, idle since 2019. Amtrak would rebuild the tracks and add a maintenance building between 33rd and 35th, with $572M federal and $125M from Canal Edge. Residents oppose it.',
    source: 'sources.html#blockclub-2026-09-09', sourceLabel: 'Block Club · Sept 9, 2026',
    position: [41.834, -87.6373], zoom: 15, basemap: 'satellite',
    layer: L.layerGroup([
      L.polygon(sites.upCanalYard, { renderer: renderer, color: '#c94a45', weight: 2, fillColor: 'url(#hatch-facility)', fillOpacity: 1, className: 'map-facility' }),
      label('text', 'Amtrak’s new facility', 12, [41.8335, -87.6373])
    ])
  });

  register({
    id: 'the78', status: 'underConstruction',
    title: 'McDonald’s Park · The 78',
    copy: 'The Chicago Fire’s 22,000-seat stadium across the river. Broke ground March 2026, opens 2028.',
    source: 'sources.html#chicagofire-2026-03-03', sourceLabel: 'Chicago Fire · Mar 3, 2026',
    position: [41.8637, -87.6325], zoom: 15,
    layer: L.layerGroup([
      L.polygon(sites.the78, { renderer: renderer, color: '#c48a1a', weight: 2, fillColor: 'url(#hatch-construction)', fillOpacity: 1, className: 'map-site-fill' }),
      label('soccer', 'McDonald’s Park', 13, [41.8622, -87.6322])
    ])
  });

  register({
    id: 'rateField', status: 'existing',
    title: 'Rate Field',
    copy: 'The White Sox’s current home. Lease and state bonds run through 2029.',
    source: 'sources.html#suntimes-2024-02-08', sourceLabel: 'Sun-Times · Feb 8, 2024',
    position: [41.8299, -87.6338], zoom: 15,
    layer: L.layerGroup([
      L.polygon(sites.rateField, { renderer: renderer, color: '#4a5a4f', weight: 1.5, fillColor: '#c9cfc6', fillOpacity: 0.8 }),
      label('ballpark', 'Rate Field', 11, [41.8299, -87.6338])
    ])
  });

  /* Transit near the ballpark site. */
  var ctaColors = [
    [/^Blue/, '#347ab4'], [/^Red/, '#c94a45'], [/^Orange/, '#d47c35'], [/^Green/, '#4b8b62'],
    [/^Pink/, '#d98cb0'], [/^Brown/, '#7a4b2a'], [/^Purple/, '#6b4f9e'], [/^Yellow/, '#d9c33b']
  ];
  function ctaColor(lines) {
    if (/,/.test(lines) && !/^Red, Purple|^Green, /.test(lines)) return '#6d6d6d';
    for (var i = 0; i < ctaColors.length; i++) if (ctaColors[i][0].test(lines)) return ctaColors[i][1];
    return '#8a8f86';
  }
  var transitLayer = L.layerGroup().addTo(map);
  var parkingLayer = L.layerGroup();
  var conceptLayer = L.layerGroup();
  var renderLayer = L.layerGroup();
  L.geoJSON(data.cta, {
    style: function (feature) {
      var lines = feature && feature.properties ? feature.properties.lines : '';
      return { renderer: renderer, color: ctaColor(lines), weight: 3.5, opacity: 0.85, lineCap: 'round', lineJoin: 'round', interactive: false };
    }
  }).addTo(transitLayer);

  [
    ['ctaRoosevelt', 'Roosevelt', 'Red, Orange and Green lines. About a 15 minute walk to the site.', 13],
    ['ctaClintonBlue', 'Clinton', 'Blue Line. About a 20 minute walk to the site.', 14],
  ].forEach(function (station) {
    var position = data.stations[station[0]];
    register({
      id: station[0], status: 'existing',
      title: 'CTA · ' + station[1],
      copy: station[2],
      source: 'https://www.transitchicago.com/', sourceLabel: 'CTA ↗',
      position: position, zoom: 15, group: transitLayer,
      layer: label('station', station[1], station[3], position)
    });
  });
  register({
    id: 'unionStation', status: 'existing',
    title: 'Union Station',
    copy: 'Amtrak and Metra terminal, about a mile north. The nearest Metra stop.',
    source: 'sources.html#metra', sourceLabel: 'Metra',
    position: data.stations.unionStation, zoom: 15, group: transitLayer,
    layer: label('station', 'Union Station', 14, data.stations.unionStation)
  });
  register({
    id: 'ogilvie', status: 'existing',
    title: 'Ogilvie Transportation Center',
    copy: 'Metra terminal for the Union Pacific lines, about a mile and a half north.',
    source: 'sources.html#metra', sourceLabel: 'Metra',
    position: data.stations.ogilvie, zoom: 15, group: transitLayer,
    layer: label('station', 'Ogilvie', 14, data.stations.ogilvie)
  });
  register({
    id: 'metraLaSalle', status: 'existing',
    title: 'LaSalle Street Station',
    copy: 'Metra Rock Island terminal, about a mile north-east.',
    source: 'sources.html#metra', sourceLabel: 'Metra',
    position: data.stations.metraLaSalle, zoom: 15, group: transitLayer,
    layer: label('station', 'LaSalle St', 14, data.stations.metraLaSalle)
  });
  register({
    id: 'pingTomDock', status: 'existing',
    title: 'Water taxi · Ping Tom Park',
    copy: 'Chicago Water Taxi’s Chinatown stop, across the river from the site. Position approximate.',
    source: 'https://www.chicagowatertaxi.com/', sourceLabel: 'Chicago Water Taxi ↗',
    position: data.stations.pingTomDock, zoom: 15, group: transitLayer,
    layer: label('boat', 'Water taxi', 14, data.stations.pingTomDock)
  });

  /* Parking near the ballpark site. Nothing has been announced. */
  register({
    id: 'grantParkSouth', status: 'existing',
    title: 'Grant Park South Garage',
    copy: 'Closest large garage, about a mile away. No ballpark parking has been announced.',
    source: 'sources.html#fieldofschemes-2026-09-08', sourceLabel: 'Field of Schemes · Sept 8, 2026',
    position: data.parking.grantParkSouth, zoom: 15, group: parkingLayer,
    layer: label('parking', 'Grant Park South', 14, data.parking.grantParkSouth)
  });
  [['grantParkNorth', 'Grant Park North Garage', 'Grant Park North'], ['millenniumPark', 'Millennium Park Garage', 'Millennium Park'], ['millenniumLakeside', 'Millennium Lakeside Garage', 'Millennium Lakeside']].forEach(function (garage) {
    register({
      id: garage[0], status: 'existing',
      title: garage[1],
      copy: 'Existing downtown garage, about a mile and a half from the site.',
      source: 'sources.html#parking', sourceLabel: 'Millennium Garages',
      position: data.parking[garage[0]], zoom: 15, group: parkingLayer,
      layer: label('parking', garage[2], 15, data.parking[garage[0]])
    });
  });

  /* Neighborhood names, for orientation. */
  [['The Loop', [41.8805, -87.6295]], ['West Loop', [41.8825, -87.6475]], ['South Loop', [41.8665, -87.6255]], ['Pilsen', [41.8545, -87.6605]], ['Chinatown', [41.8518, -87.6335]], ['Bridgeport', [41.8378, -87.6475]], ['Near South Side', [41.8555, -87.6215]]].forEach(function (hood) {
    L.marker(hood[1], { icon: L.divIcon({ className: 'map-marker map-marker-area label-min-12', html: '<span class="map-marker-label">' + escapeHtml(hood[0]) + '</span>', iconSize: [0, 0] }), interactive: false, keyboard: false }).addTo(map);
  });

  /* Where the published renderings were drawn from. */
  [
    ['renderNorth', 'North aerial', [41.8695, -87.6362], 'index.html#compare-north', 'media/source-north.jpg', 'Looking south over Roosevelt Road toward the ballpark and The 78.'],
    ['renderSouth', 'South aerial', [41.8575, -87.6335], 'index.html#compare-south', 'media/source-south.jpg', 'Looking north up the river from about 18th Street.'],
    ['renderBridge', 'Roosevelt bridge', [41.8673, -87.6338], 'index.html#compare-bridge', 'media/source-bridge.jpg', 'Street level on the Roosevelt Road bridge, looking south-west.']
  ].forEach(function (view) {
    register({
      id: view[0], status: 'rendering',
      title: view[1],
      image: view[4], imageAlt: 'Published ' + view[1].toLowerCase() + ' concept by AECOM / Canal Edge',
      copy: view[5] + ' Camera position is approximate.',
      source: view[3], sourceLabel: 'Compare it with our model ↗',
      position: view[2], zoom: 16, group: renderLayer,
      layer: label('camera', view[1], 15, view[2])
    });
  });

  /* Clinton Street subway: a city concept from the Central Area Plan, never funded or studied by CTA. */
  var clintonRoute = [
    [41.9107, -87.6487], [41.9035, -87.6435], [41.8965, -87.6432], [41.8905, -87.6432], [41.8895, -87.6412],
    [41.8825, -87.6410], [41.8786, -87.6410], [41.8755, -87.6410], [41.8673, -87.6410], [41.8600, -87.6410],
    [41.8598, -87.6360], [41.8590, -87.6320], [41.8560, -87.6310], [41.8535, -87.6310]
  ];
  var clintonLine = L.polyline(clintonRoute, { renderer: renderer, color: '#7a4f6d', weight: 3.5, opacity: 0.9, dashArray: '8 7', lineCap: 'round', lineJoin: 'round', className: 'map-concept-line' });
  var clintonFeature = {
    id: 'clintonSubway', status: 'concept',
    title: 'Clinton Street subway',
    copy: 'A city concept from the Central Area Plan: a new Red Line subway from North/Clybourn under Clinton Street to Chinatown, with a stop at Roosevelt a few blocks from the ballpark site. Estimated at $3 billion with no funding identified; CTA has not studied it.',
    source: 'sources.html#central-area-plan', sourceLabel: 'Chicago Central Area Action Plan',
    position: [41.8673, -87.6410], zoom: 15, group: conceptLayer,
    layer: clintonLine
  };
  register(clintonFeature);
  [['North/Clybourn', [41.9107, -87.6487], 15], ['Chicago', [41.8965, -87.6432], 15], ['Grand', [41.8915, -87.6432], 15], ['Union Station', [41.8786, -87.6410], 16], ['Clinton', [41.8755, -87.6410], 16], ['Roosevelt · Clinton', [41.8673, -87.6410], 13], ['Chinatown', [41.8535, -87.6310], 15]].forEach(function (stop) {
    var marker = label('concept', stop[0], stop[2], stop[1]);
    marker.on('click', function () { showDetail(clintonFeature); });
    marker.addTo(conceptLayer);
  });

  var groups = { transit: transitLayer, parking: parkingLayer, concept: conceptLayer, renderings: renderLayer };
  document.querySelectorAll('[data-map-layer]').forEach(function (button) {
    button.addEventListener('click', function () {
      var layer = groups[button.getAttribute('data-map-layer')];
      if (!layer) return;
      var on = !map.hasLayer(layer);
      if (on) layer.addTo(map); else map.removeLayer(layer);
      button.setAttribute('aria-pressed', on ? 'true' : 'false');
      if (on && layer === parkingLayer) {
        var bounds = L.latLngBounds([stadiumCenter]);
        layer.eachLayer(function (item) { if (item.getLatLng) bounds.extend(item.getLatLng()); });
        map.flyToBounds(bounds, { padding: [40, 40], duration: 0.8 });
      }
      if (on && layer === renderLayer) {
        showDetail(places.renderNorth);
        map.flyToBounds(L.latLngBounds([places.renderNorth.position, places.renderSouth.position, places.renderBridge.position]), { padding: [40, 40], duration: 0.8 });
      }
      if (on && layer === conceptLayer) {
        showDetail(clintonFeature);
        map.flyToBounds(L.latLngBounds([stadiumCenter, [41.8765, -87.6425], [41.8600, -87.6300]]), { padding: [30, 30], duration: 0.8 });
      }
    });
  });
  var overview = L.latLngBounds([[41.8555, -87.6435], [41.8705, -87.6265]]);
  function focusPlace(id, button, instant, keepBasemap) {
    var place = places[id];
    if (!place) return;
    showDetail(place);
    if (!keepBasemap) setBasemap(place.basemap || 'map');
    if (instant || (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches)) map.setView(place.position, place.zoom);
    else map.flyTo(place.position, place.zoom, { duration: 0.9, easeLinearity: 0.35 });
    document.querySelectorAll('[data-map-focus]').forEach(function (item) {
      item.setAttribute('aria-pressed', item === button || item.getAttribute('data-map-focus') === id ? 'true' : 'false');
    });
  }
  document.querySelectorAll('[data-map-focus]').forEach(function (button) {
    button.addEventListener('click', function () {
      focusPlace(button.getAttribute('data-map-focus'), button);
    });
  });

  function updateZoomClasses() {
    var zoom = map.getZoom();
    [12, 13, 14, 15].forEach(function (level) { root.classList.toggle('zoom-lt-' + level, zoom < level); });
  }
  map.on('zoomend', updateZoomClasses);
  updateZoomClasses();

  /* Scroll-driven story: each step pins the map to a place; the last step opens the controls. */
  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var bothYards = L.latLngBounds(sites.amtrakYard.concat(sites.upCanalYard));
  var flight = { duration: reduceMotion ? 0 : 0.9, easeLinearity: 0.35 };
  function fly(bounds, pad) { map.flyToBounds(bounds, { padding: [pad, pad], duration: flight.duration, easeLinearity: flight.easeLinearity }); }
  var cover = document.querySelector('.story-cover');
  function setCover(open) { if (cover) cover.setAttribute('data-open', open ? 'true' : 'false'); }
  var yardNotes = L.layerGroup([
    label('text', 'North end · train storage', 12, [41.8447, -87.6373]),
    label('text', 'South end · shop building, 33rd–35th', 12, [41.8292, -87.6373])
  ]);
  var storyViews = {
    intro: function () { setCover(true); setBasemap('satellite'); fly(L.latLngBounds(sites.the78[0][0]).extend(sites.the78[1][0]).extend(sites.amtrakYard), 30); showDetail(places.stadium); },
    the78first: function () { setCover(false); setBasemap('satellite'); showDetail(places.the78); fly(L.latLngBounds(sites.the78[0][0]).extend(sites.the78[1][0]), 40); },
    fire: function () { setBasemap('satellite'); showDetail(places.the78); map.flyTo([41.8625, -87.6325], 16, flight); },
    amtrakYard: function () { setBasemap('satellite'); focusPlace('amtrakYard', null, false, true); },
    swap: function () { showDetail(places.upCanalYard); setBasemap('satellite'); var yard = L.latLngBounds(sites.upCanalYard); map.flyTo(yard.getCenter(), map.getBoundsZoom(yard, false, [20, 20]) + 1, flight); },
    stadium: function () { setBasemap('map'); focusPlace('stadium'); },
    explore: function () { setBasemap('map'); fly(overview, 12); showDetail(places.stadium); }
  };
  var progress = document.querySelector('.story-progress');
  var stepNames = [];
  document.querySelectorAll('.story-step').forEach(function (step) {
    var name = step.getAttribute('data-story');
    if (name === 'intro' || name === 'explore') return;
    stepNames.push(name);
    if (progress) {
      var item = document.createElement('li');
      item.setAttribute('data-step', name);
      item.textContent = (step.querySelector('time') || {}).textContent || '';
      progress.appendChild(item);
    }
  });
  var section = root.closest('.story');
  document.documentElement.classList.add('story-snap');
  var currentStep = '';
  /* What each chapter shows. Everything else on the map is hidden until Explore. */
  var siteIds = ['amtrakYard', 'stadium', 'upCanalYard', 'the78', 'rateField'];
  var chapterSites = {
    intro: ['amtrakYard', 'the78'],
    the78first: ['the78'],
    fire: ['the78'],
    amtrakYard: ['amtrakYard', 'the78'],
    swap: ['upCanalYard'],
    stadium: ['stadium', 'amtrakYard', 'the78'],
    explore: siteIds
  };
  function setChapterLayers(name) {
    var show = chapterSites[name] || siteIds;
    siteIds.forEach(function (id) {
      var layer = places[id].layer;
      var on = show.indexOf(id) >= 0;
      if (on && !map.hasLayer(layer)) layer.addTo(map);
      if (!on && map.hasLayer(layer)) map.removeLayer(layer);
    });
    if (name === 'swap' && !map.hasLayer(yardNotes)) yardNotes.addTo(map);
    if (name !== 'swap' && map.hasLayer(yardNotes)) map.removeLayer(yardNotes);
    var transitOn = name === 'explore' || name === 'intro';
    if (transitOn && !map.hasLayer(transitLayer)) transitLayer.addTo(map);
    if (!transitOn && map.hasLayer(transitLayer)) map.removeLayer(transitLayer);
    var transitButton = document.querySelector('[data-map-layer="transit"]');
    if (transitButton) transitButton.setAttribute('aria-pressed', map.hasLayer(transitLayer) ? 'true' : 'false');
  }
  function runStep(name) {
    if (name === currentStep || !storyViews[name]) return;
    currentStep = name;
    setChapterLayers(name);
    if (section) section.classList.toggle('is-explore', name === 'explore');
    root.classList.toggle('is-focused', name !== 'explore');
    if (name !== 'intro') setCover(false);
    document.querySelectorAll('.story-step').forEach(function (step) { step.classList.toggle('is-active', step.getAttribute('data-story') === name); });
    if (progress) {
      var index = stepNames.indexOf(name);
      progress.hidden = index < 0;
      progress.querySelectorAll('li').forEach(function (item, i) { item.classList.toggle('is-done', i < index); item.classList.toggle('is-current', i === index); });
    }
    storyViews[name]();
    updateNav();
  }
  var steps = Array.prototype.slice.call(document.querySelectorAll('.story-step'));
  var navPrev = document.querySelector('[data-story-prev]'), navNext = document.querySelector('[data-story-next]'), navCount = document.querySelector('[data-story-count]');
  function stepIndex() { return steps.findIndex(function (step) { return step.getAttribute('data-story') === currentStep; }); }
  function goTo(index) {
    var step = steps[Math.max(0, Math.min(steps.length - 1, index))];
    if (step) step.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: window.innerWidth <= 900 ? 'start' : 'center' });
  }
  if (navPrev) navPrev.addEventListener('click', function () { goTo(stepIndex() - 1); });
  if (navNext) navNext.addEventListener('click', function () { goTo(stepIndex() + 1); });
  function updateNav() {
    var index = stepIndex();
    if (navCount) navCount.textContent = index <= 0 ? '' : (index) + ' / ' + (steps.length - 1);
    if (navPrev) navPrev.disabled = index <= 0;
    if (navNext) navNext.disabled = index >= steps.length - 1;
  }
  if ('IntersectionObserver' in window) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) { if (entry.isIntersecting) runStep(entry.target.getAttribute('data-story')); });
    }, { rootMargin: window.innerWidth <= 900 ? '-52% 0px -22% 0px' : '-45% 0px -45% 0px', threshold: 0 });
    document.querySelectorAll('.story-step').forEach(function (step) { observer.observe(step); });
    /* The last card is short and ends the page, so it opens as soon as it scrolls into the lower half. */
    var exploreStep = document.querySelector('.story-explore');
    function checkExplore() {
      if (!exploreStep) return;
      var top = exploreStep.getBoundingClientRect().top;
      if (top < window.innerHeight * 0.8 && top > 0) runStep('explore');
    }
    window.addEventListener('scroll', checkExplore, { passive: true });
    checkExplore();
  } else if (section) section.classList.add('is-explore');

  var requested = new URLSearchParams(window.location.search).get('place');
  map.fitBounds(L.latLngBounds(sites.the78[0][0]).extend(sites.the78[1][0]).extend(sites.amtrakYard), { padding: [30, 30] });
  setBasemap('satellite');
  setChapterLayers('intro');
  if (places[requested]) { setCover(false); if (section) section.classList.add('is-explore'); currentStep = 'explore'; setChapterLayers('explore'); focusPlace(requested, null, true); document.querySelector('.story-explore').scrollIntoView(); }
  else showDetail(places.stadium);
  window.setTimeout(function () { map.invalidateSize(); }, 0);
})();
