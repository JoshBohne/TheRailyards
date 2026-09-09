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
    minZoom: 11,
    maxZoom: 18,
    zoomControl: true,
    scrollWheelZoom: false,
    attributionControl: true
  });
  map.attributionControl.setPrefix('');
  root.addEventListener('wheel', function (event) {
    if (event.ctrlKey || event.metaKey) { map.scrollWheelZoom.enable(); }
  }, { passive: true });
  map.on('focus', function () { map.scrollWheelZoom.enable(); });
  map.on('blur', function () { map.scrollWheelZoom.disable(); });

  var esri = 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/';
  L.tileLayer(esri + 'World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 18,
    attribution: 'Basemap &copy; <a href="https://www.esri.com/en-us/legal/terms/services">Esri</a> · Footprints &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors · CTA lines: City of Chicago'
  }).addTo(map);
  L.tileLayer(esri + 'World_Light_Gray_Reference/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 18,
    pane: 'shadowPane',
    opacity: 0.9
  }).addTo(map);

  /* One SVG renderer so hatched fills can reference a shared <pattern>. */
  var renderer = L.svg({ padding: 0.6 }).addTo(map);
  function addPatterns() {
    var container = renderer._container;
    if (!container || container.querySelector('defs.map-patterns')) return;
    var ns = 'http://www.w3.org/2000/svg';
    var defs = document.createElementNS(ns, 'defs');
    defs.setAttribute('class', 'map-patterns');
    defs.innerHTML =
      '<pattern id="hatch-facility" patternUnits="userSpaceOnUse" width="8" height="8" patternTransform="rotate(45)"><rect width="8" height="8" fill="#f7dad8"/><line x1="0" y1="0" x2="0" y2="8" stroke="#c94a45" stroke-width="3"/></pattern>' +
      '<pattern id="hatch-site" patternUnits="userSpaceOnUse" width="8" height="8" patternTransform="rotate(-45)"><rect width="8" height="8" fill="#eef1e6"/><line x1="0" y1="0" x2="0" y2="8" stroke="#6b7f63" stroke-width="2"/></pattern>' +
      '<pattern id="hatch-construction" patternUnits="userSpaceOnUse" width="8" height="8" patternTransform="rotate(45)"><rect width="8" height="8" fill="#fbeed0"/><line x1="0" y1="0" x2="0" y2="8" stroke="#d29a2c" stroke-width="2"/></pattern>';
    container.insertBefore(defs, container.firstChild);
  }
  addPatterns();

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, function (character) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[character];
    });
  }
  function pointFromLocal(point) {
    return [
      origin.latitude_reference + (point[1] - homeOffset[1]) * latScale,
      origin.longitude_reference + (point[0] - homeOffset[0] - 33) * lonScale
    ];
  }
  function pointsFromLocal(points) { return points.map(pointFromLocal); }

  var statusLabels = {
    existing: 'Existing',
    underConstruction: 'Under construction',
    proposed: 'Proposed',
    concept: 'Concept · unconfirmed'
  };

  /* Detail panel */
  var detailNodes = {
    kicker: document.querySelector('[data-map-detail-kicker]'),
    title: document.querySelector('[data-map-detail-title]'),
    copy: document.querySelector('[data-map-detail-copy]'),
    link: document.querySelector('[data-map-detail-link]')
  };
  function showDetail(feature) {
    if (detailNodes.kicker) {
      detailNodes.kicker.textContent = statusLabels[feature.status] || feature.status;
      detailNodes.kicker.setAttribute('data-status', feature.status);
    }
    if (detailNodes.title) detailNodes.title.textContent = feature.title;
    if (detailNodes.copy) detailNodes.copy.textContent = feature.copy;
    if (detailNodes.link) {
      detailNodes.link.textContent = feature.sourceLabel || 'Source';
      detailNodes.link.href = feature.source;
    }
  }
  function popupHtml(feature) {
    return '<span class="map-popup-status" data-status="' + feature.status + '">' + escapeHtml(statusLabels[feature.status]) + '</span><strong>' + escapeHtml(feature.title) + '</strong><span>' + escapeHtml(feature.summary || feature.copy.split('. ')[0] + '.') + '</span>';
  }

  /* Feature registry: status + group decide visibility; places are focusable from the picker. */
  var features = [];
  var places = {};
  function register(feature) {
    feature.layer.bindPopup(popupHtml(feature), { maxWidth: 260, closeButton: false });
    feature.layer.on('click', function () { showDetail(feature); });
    features.push(feature);
    if (feature.id) places[feature.id] = feature;
    return feature;
  }

  function icon(kind, label, labelZoom) {
    var glyphs = {
      station: '<svg viewBox="0 0 20 20" aria-hidden="true"><rect x="4" y="2.5" width="12" height="12.5" rx="2.5" fill="#fff"/><rect x="6" y="4.5" width="8" height="4.5" rx="1" fill="currentColor"/><circle cx="7.4" cy="11.8" r="1.2" fill="currentColor"/><circle cx="12.6" cy="11.8" r="1.2" fill="currentColor"/><path d="M6 15.5l-1.6 2.5M14 15.5l1.6 2.5" stroke="#fff" stroke-width="1.6" stroke-linecap="round"/></svg>',
      star: '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M10 1.8l2.5 5.3 5.8.7-4.3 4 1.2 5.8L10 14.7l-5.2 2.9 1.2-5.8-4.3-4 5.8-.7z"/></svg>',
      parking: '<svg viewBox="0 0 20 20" aria-hidden="true"><rect x="2" y="2" width="16" height="16" rx="3"/><text x="10" y="14.6" text-anchor="middle" font-size="12" font-weight="700" fill="#fff" font-family="system-ui,sans-serif">P</text></svg>',
      ballpark: '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M10 2.5a7.5 7.5 0 1 1 0 15 7.5 7.5 0 0 1 0-15z"/><path d="M5.2 5.4c2.4 1 3.6 2.9 3.6 4.6s-1.2 3.6-3.6 4.6M14.8 5.4c-2.4 1-3.6 2.9-3.6 4.6s1.2 3.6 3.6 4.6" stroke="#fff" stroke-width="1.4" fill="none" stroke-linecap="round"/></svg>',
      dot: '<svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="5"/></svg>'
    };
    return L.divIcon({
      className: 'map-marker map-marker-' + kind + ' label-min-' + String(labelZoom || 15).replace('.', '-'),
      html: '<span class="map-marker-glyph">' + glyphs[kind] + '</span>' + (label ? '<span class="map-marker-label">' + escapeHtml(label) + '</span>' : ''),
      iconSize: kind === 'dot' ? [12, 12] : [24, 24],
      iconAnchor: kind === 'dot' ? [6, 6] : [12, 12],
      popupAnchor: [0, -12]
    });
  }

  /* ---------- Sites and buildings ---------- */
  var sites = data.sites || {};

  register({
    id: 'amtrakYard', status: 'existing', group: 'sites',
    title: 'Amtrak 14th Street Coach Yard · today',
    summary: 'Amtrak’s current Chicago maintenance yard, and the land The Railyards would be built on.',
    copy: 'About 47 acres between Roosevelt Road, 18th Street, Canal Street and the river, where Amtrak services its Midwest fleet today. Shore Capital Partners, Justin Ishbia’s firm, is under contract to buy the yard once Amtrak moves out. The outline is the OpenStreetMap yard footprint clipped at Roosevelt Road.',
    source: 'sources.html#suntimes-2026-08-14', sourceLabel: 'Sun-Times · Aug 14, 2026',
    position: [41.8625, -87.6362], zoom: 15,
    layer: L.polygon(sites.amtrakYard, { renderer: renderer, color: '#6b7f63', weight: 2, dashArray: '6 5', fillColor: 'url(#hatch-site)', fillOpacity: 1, className: 'map-site map-site-current' })
  });

  var bowl = L.polygon(pointsFromLocal(data.bowlFront.concat(data.bowlBack.slice().reverse())), {
    renderer: renderer, color: '#294638', weight: 2, fillColor: '#7d9a80', fillOpacity: 0.55, className: 'railyards-bowl-footprint'
  });
  var field = L.polygon(pointsFromLocal(data.fieldBoundary), {
    renderer: renderer, color: '#294638', weight: 1.5, fillColor: '#8fb28a', fillOpacity: 0.9, className: 'railyards-field-boundary'
  });
  var stadiumFeature = {
    id: 'stadium', status: 'proposed', group: 'sites',
    title: 'The Railyards · proposed ballpark',
    summary: 'Canal Edge’s proposed White Sox ballpark on the Amtrak yard, as modeled for this site.',
    copy: 'Justin Ishbia’s Canal Edge unveiled the concept on September 5, 2026, with AECOM renderings of a brick riverfront ballpark facing The 78. The White Sox say a multi-month study will decide whether the site joins the list under consideration, and Canal Edge says the architect has not been chosen. The footprint here is our reconstruction registered to the scene coordinates, not a published site plan.',
    source: 'sources.html#blockclub-2026-09-06', sourceLabel: 'Block Club · Sept 6, 2026',
    position: stadiumCenter, zoom: 16,
    layer: L.layerGroup([bowl, field, L.marker(stadiumCenter, { icon: icon('ballpark', 'The Railyards', 11), zIndexOffset: 500 })])
  };
  register(stadiumFeature);
  stadiumFeature.layer.eachLayer(function (item) {
    item.bindPopup(popupHtml(stadiumFeature), { maxWidth: 260, closeButton: false });
    item.on('click', function () { showDetail(stadiumFeature); });
  });

  register({
    id: 'upCanalYard', status: 'proposed', group: 'sites',
    title: 'Amtrak maintenance facility · Bridgeport',
    summary: 'Where Amtrak plans to move: Union Pacific’s Canal Street yard beside Rate Field.',
    copy: 'Amtrak plans a 24-hour maintenance facility on Union Pacific’s elevated Canal Street yard, which runs from Cermak Road to Pershing Road west of Rate Field. The maintenance building would sit between 33rd and 35th Streets, with train storage to the north. Federal grants cover up to $572 million, Canal Edge adds $125 million, and Amtrak targets a fall 2026 start and roughly 18 months of work. Bridgeport and Chinatown residents and their elected officials oppose the site.',
    source: 'sources.html#amtrak-2026-08-14', sourceLabel: 'Amtrak · Aug 14, 2026',
    position: [41.836, -87.6373], zoom: 14,
    layer: L.polygon(sites.upCanalYard, { renderer: renderer, color: '#c94a45', weight: 2, fillColor: 'url(#hatch-facility)', fillOpacity: 1, className: 'map-site map-site-facility' })
  });
  register({
    id: 'facilityBuilding', status: 'proposed', group: 'sites',
    title: 'Maintenance building · 33rd to 35th',
    summary: 'The four-story trainshed and shop building, about 100 feet from homes on Canal Street.',
    copy: 'Amtrak described an eight-track yard to the north and a four-story maintenance building to the south at its August 26 community meeting. Residents note the building would stand about 100 feet from houses, and Amtrak is using a federal categorical exclusion rather than a full environmental study. Position is approximate, from the reported street bounds.',
    source: 'sources.html#nbc-bridgeport-2026-08-27', sourceLabel: 'NBC Chicago · Aug 27, 2026',
    position: [41.8328, -87.6373], zoom: 16,
    layer: L.marker([41.8328, -87.6373], { icon: icon('star', 'Amtrak facility · proposed', 13) })
  });

  register({
    id: 'the78', status: 'underConstruction', group: 'sites',
    title: 'The 78 · McDonald’s Park',
    summary: 'Chicago Fire’s 22,000-seat soccer stadium, under construction across the river.',
    copy: 'Related Midwest’s 62-acre site between Roosevelt Road, 16th Street, Clark Street and the river. The Fire broke ground on a privately funded stadium on March 3, 2026, named McDonald’s Park in May, and target a 2028 opening. The Railyards renderings show the ballpark directly across the river from it.',
    source: 'sources.html#chicagofire-2026-03-03', sourceLabel: 'Chicago Fire · Mar 3, 2026',
    position: [41.8637, -87.6325], zoom: 15,
    layer: L.polygon(sites.the78, { renderer: renderer, color: '#c48a1a', weight: 2, fillColor: 'url(#hatch-construction)', fillOpacity: 1, className: 'map-site map-site-construction' })
  });
  register({
    id: 'fireStadium', status: 'underConstruction', group: 'sites',
    title: 'McDonald’s Park',
    summary: 'Stadium bowl going vertical in 2026; opening targeted for 2028.',
    copy: 'The soccer stadium occupies the south end of The 78. Construction photos in July 2026 showed the bowl rising with the first tower crane in place. Pedestrian access is planned from Wells Street, Wentworth Avenue and the new LaSalle Street extension.',
    source: 'sources.html#yimby-2026-07', sourceLabel: 'Chicago YIMBY · July 2026',
    position: [41.8622, -87.6322], zoom: 16,
    layer: L.marker([41.8622, -87.6322], { icon: icon('star', 'McDonald’s Park', 13) })
  });

  register({
    id: 'rateField', status: 'existing', group: 'sites',
    title: 'Rate Field',
    summary: 'The White Sox’s current home, state-owned, with a lease through 2029.',
    copy: 'Rate Field is owned by the Illinois Sports Facilities Authority. The White Sox lease runs through the 2029 season, and the authority’s remaining Rate Field bonds are retired in 2029. Ald. Nicole Lee argues the ballpark still has life left and that a 24-hour rail facility does not belong beside it.',
    source: 'sources.html#suntimes-2024-02-08', sourceLabel: 'Sun-Times · Feb 8, 2024',
    position: [41.8299, -87.6338], zoom: 15,
    layer: L.layerGroup([
      L.polygon(sites.rateField, { renderer: renderer, color: '#4a5a4f', weight: 1.5, fillColor: '#c9cfc6', fillOpacity: 0.8, className: 'map-site map-site-existing' }),
      L.marker([41.8299, -87.6338], { icon: icon('ballpark', 'Rate Field', 11) })
    ])
  });
  places.rateField.layer.eachLayer(function (item) {
    item.bindPopup(popupHtml(places.rateField), { maxWidth: 260, closeButton: false });
    item.on('click', function () { showDetail(places.rateField); });
  });

  register({
    id: 'bnsfYard', status: 'existing', group: 'sites',
    title: 'Metra BNSF coach yard',
    summary: 'Metra’s 14th Street coach yard, west of the Amtrak yard. Not part of the deal.',
    copy: 'Metra stores and services BNSF Line trains here. No source describes it moving, so it stays a working rail yard between the proposed ballpark and Canal Street.',
    source: 'sources.html#osm', sourceLabel: 'OpenStreetMap footprint',
    position: [41.866, -87.639], zoom: 15,
    layer: L.polygon(sites.bnsfYard, { renderer: renderer, color: '#8a8f86', weight: 1, fillColor: '#d9dbd4', fillOpacity: 0.7, className: 'map-site map-site-existing' })
  });

  register({
    id: 'powerhouse', status: 'proposed', group: 'sites',
    title: 'Union Station Powerhouse',
    summary: 'The 1930s power plant on Taylor Street at the river, shown redeveloped in the renderings.',
    copy: 'Chicago YIMBY reports the concept includes a redeveloped Powerhouse and a small park north of Roosevelt Road. No program or timeline has been announced for the building.',
    source: 'sources.html#yimby-2026-09', sourceLabel: 'Chicago YIMBY · Sept 2026',
    position: [41.8688, -87.6354], zoom: 16,
    layer: L.marker([41.8688, -87.6354], { icon: icon('star', 'Powerhouse', 15) })
  });

  /* ---------- Concept elements shown in renderings, nothing announced ---------- */
  register({
    id: 'waterTaxi', status: 'concept', group: 'sites',
    title: 'Water taxi landing',
    summary: 'Renderings show water taxis at the ballpark; no operator or service is announced.',
    copy: 'The concept imagery shows water taxi service on the South Branch and pedestrian bridges over the tracks. No operator, route or funding has been announced, and the landing position here is illustrative.',
    source: 'sources.html#soxon35th-2026-09', sourceLabel: 'Sox On 35th · Sept 2026',
    position: [41.8635, -87.6352], zoom: 16,
    layer: L.marker([41.8635, -87.6352], { icon: icon('star', 'Water taxi', 15.5) })
  });
  register({
    id: 'redLineInfill', status: 'concept', group: 'cta',
    title: 'Red Line infill station at The 78',
    summary: 'A station near 15th and Clark was in The 78’s original plan; its status is unclear.',
    copy: 'The 78’s original plan included a new Red Line station near 15th Street and Clark Street and a Metra Rock Island realignment to reopen Clark Street. Streetsblog reported in August 2025 that the Fire’s stadium plan dropped the realignment and that no station commitment is confirmed. It would be the closest rapid-transit stop to The Railyards if built.',
    source: 'sources.html#streetsblog-2025-08-27', sourceLabel: 'Streetsblog · Aug 27, 2025',
    position: [41.8613, -87.6314], zoom: 16,
    layer: L.marker([41.8613, -87.6314], { icon: icon('star', 'Red Line infill · unconfirmed', 15.5) })
  });

  /* ---------- Transit ---------- */
  var ctaColors = { 'Blue Line': '#347ab4', 'Red Line': '#c94a45', 'Orange Line': '#d47c35', 'Green Line': '#4b8b62' };
  var ctaLines = L.geoJSON(data.cta, {
    style: function (feature) {
      var line = feature && feature.properties ? feature.properties.lines : '';
      return { renderer: renderer, color: ctaColors[line] || '#8a8f86', weight: 4, opacity: 0.9, lineCap: 'round', lineJoin: 'round', className: 'map-cta-line' };
    }
  });
  register({
    id: 'ctaLines', status: 'existing', group: 'cta',
    title: 'CTA rail lines',
    summary: 'City of Chicago open-data rail geometry, captured September 8, 2026.',
    copy: 'Colored routes are the CTA Red, Orange, Green and Blue lines from the City of Chicago rail-line dataset. They show geometry, not live service. Chicago YIMBY notes the nearest L stations are a 15 to 20 minute walk from the Railyards site.',
    source: 'sources.html#cta-lines', sourceLabel: 'City of Chicago open data',
    layer: ctaLines
  });

  var ctaStations = [
    ['ctaRoosevelt', 'Roosevelt', 'Red, Orange and Green lines. About a 15 minute walk to the Railyards site across the Roosevelt Road bridge.', 'https://www.transitchicago.com/station/roos/', '#c94a45'],
    ['ctaClintonBlue', 'Clinton (Blue)', 'Blue Line station at Clinton and Congress, north-west of the site near Union Station.', 'https://www.transitchicago.com/', '#347ab4'],
    ['ctaHarrison', 'Harrison', 'Red Line station under State Street in the South Loop.', 'https://www.transitchicago.com/', '#c94a45'],
    ['ctaCermak', 'Cermak-Chinatown', 'Red Line station serving Chinatown, north of the proposed Amtrak facility.', 'https://www.transitchicago.com/', '#c94a45'],
    ['ctaCermakGreen', 'Cermak-McCormick Place', 'Green Line station by McCormick Place.', 'https://www.transitchicago.com/', '#4b8b62'],
    ['ctaHalstedOrange', 'Halsted (Orange)', 'Orange Line station west of Bridgeport.', 'https://www.transitchicago.com/', '#d47c35'],
    ['ctaSox35', 'Sox-35th', 'Red Line station serving Rate Field today, a few blocks east of the proposed Amtrak facility.', 'https://www.transitchicago.com/', '#c94a45'],
    ['ctaStateLake', 'State/Lake', 'Loop elevated station serving the Red, Brown, Green, Orange, Pink and Purple lines.', 'https://www.transitchicago.com/', '#c94a45']
  ];
  ctaStations.forEach(function (station) {
    var position = data.stations[station[0]];
    register({
      id: station[0], status: 'existing', group: 'cta',
      title: 'CTA · ' + station[1],
      summary: station[2],
      copy: station[2] + ' Station coordinates are orientation points from the City of Chicago station dataset; check CTA for service and accessibility.',
      source: station[3], sourceLabel: 'CTA station information ↗',
      position: position, zoom: 15,
      layer: L.marker(position, { icon: icon('station', station[1], station[0] === 'ctaRoosevelt' || station[0] === 'ctaSox35' ? 13 : station[0] === 'ctaCermakGreen' ? 15.5 : station[0] === 'ctaHarrison' ? 15 : 14), zIndexOffset: 200 })
    });
    places[station[0]].layer.getElement && places[station[0]].layer.on('add', function () {
      var element = places[station[0]].layer.getElement();
      if (element) element.style.color = station[4];
    });
  });

  var metraColors = { bnsf: '#a7623b', rockIsland: '#915b37', electric: '#6e6d56' };
  var metraNames = { bnsf: 'Metra BNSF Line', rockIsland: 'Metra Rock Island Line', electric: 'Metra Electric' };
  Object.keys(data.metra).forEach(function (key) {
    register({
      id: 'metra-' + key, status: 'existing', group: 'metra',
      title: metraNames[key] || 'Metra corridor',
      summary: 'Simplified corridor trace between mapped stations. Not a track survey.',
      copy: 'A simplified geographic trace of the ' + (metraNames[key] || 'Metra') + ' corridor. Metra trains do not stop beside the Railyards site today; the renderings refer to “a nearby Metra station” without naming one.',
      source: 'sources.html#metra', sourceLabel: 'Metra system map',
      layer: L.polyline(data.metra[key], { renderer: renderer, color: metraColors[key] || '#9c5d35', weight: 3, opacity: 0.8, dashArray: '1 7', lineCap: 'round', className: 'map-metra-line' })
    });
  });
  var metraStations = [
    ['metraMuseum', 'Museum Campus / 11th St', 'Metra Electric station east of the site.'],
    ['metraLaSalle', 'LaSalle Street', 'Rock Island Line terminal at LaSalle and Congress.'],
    ['unionStation', 'Union Station', 'Amtrak and Metra terminal, about a mile north of the site.']
  ];
  metraStations.forEach(function (station) {
    var position = data.stations[station[0]];
    register({
      id: station[0], status: 'existing', group: 'metra',
      title: 'Metra · ' + station[1],
      summary: station[2],
      copy: station[2] + ' The marker is an orientation point, not live arrivals or platform access.',
      source: 'sources.html#metra', sourceLabel: 'Metra maps and schedules',
      position: position, zoom: 15,
      layer: L.marker(position, { icon: icon('station', station[1], station[0] === 'unionStation' ? 13 : 14), zIndexOffset: 150 })
    });
  });

  /* ---------- Parking ---------- */
  var parkingPlaces = [
    ['grantParkSouth', 'Grant Park South Garage'],
    ['grantParkNorth', 'Grant Park North Garage'],
    ['millenniumPark', 'Millennium Park Garage'],
    ['millenniumLakeside', 'Millennium Lakeside Garage']
  ];
  parkingPlaces.forEach(function (place) {
    var position = data.parking[place[0]];
    register({
      id: place[0], status: 'existing', group: 'parking',
      title: place[1],
      summary: 'Existing downtown garage. No Railyards event parking has been announced.',
      copy: 'An existing downtown garage roughly a mile from the site. The renderings show no parking, and a Canal Edge spokesperson said parking “will be ironed out” later. Rates and event availability change.',
      source: 'sources.html#fieldofschemes-2026-09-08', sourceLabel: 'Field of Schemes · Sept 8, 2026',
      position: position, zoom: 15,
      layer: L.marker(position, { icon: icon('parking', place[1].replace(' Garage', ''), 15) })
    });
  });
  register({
    id: 'rateFieldLots', status: 'existing', group: 'parking',
    title: 'Rate Field parking lots',
    summary: 'The surface lots around Rate Field, next to the proposed Amtrak facility.',
    copy: 'Rate Field is ringed by surface lots between 35th Street and Pershing Road, on land held by the state’s Illinois Sports Facilities Authority. They serve Sox games today; nothing has been announced about them under either plan.',
    source: 'sources.html#suntimes-2024-02-08', sourceLabel: 'Sun-Times · Feb 8, 2024',
    position: [41.8265, -87.6356], zoom: 15,
    layer: L.marker([41.8265, -87.6356], { icon: icon('parking', 'Rate Field lots', 15) })
  });

  /* ---------- Visibility ---------- */
  var statusOn = { existing: true, underConstruction: true, proposed: true, concept: true };
  var groupOn = { sites: true, cta: true, metra: true, parking: true };
  function refresh() {
    features.forEach(function (feature) {
      var visible = statusOn[feature.status] && groupOn[feature.group];
      if (visible && !map.hasLayer(feature.layer)) feature.layer.addTo(map);
      if (!visible && map.hasLayer(feature.layer)) map.removeLayer(feature.layer);
    });
    document.querySelectorAll('[data-map-status]').forEach(function (button) {
      button.setAttribute('aria-pressed', statusOn[button.getAttribute('data-map-status')] ? 'true' : 'false');
    });
    document.querySelectorAll('[data-map-layer]').forEach(function (button) {
      button.setAttribute('aria-pressed', groupOn[button.getAttribute('data-map-layer')] ? 'true' : 'false');
    });
    addPatterns();
  }
  document.querySelectorAll('[data-map-status]').forEach(function (button) {
    button.addEventListener('click', function () {
      var name = button.getAttribute('data-map-status');
      statusOn[name] = !statusOn[name];
      refresh();
    });
  });
  document.querySelectorAll('[data-map-layer]').forEach(function (button) {
    button.addEventListener('click', function () {
      var name = button.getAttribute('data-map-layer');
      groupOn[name] = !groupOn[name];
      refresh();
    });
  });

  /* ---------- Extents ---------- */
  var views = {
    overview: L.latLngBounds([[41.822, -87.652], [41.887, -87.616]]),
    stadium: L.latLngBounds([[41.8555, -87.6435], [41.8705, -87.6265]]),
    bridgeport: L.latLngBounds([[41.8205, -87.6465], [41.8555, -87.6245]])
  };
  var viewPlaces = { overview: 'stadium', stadium: 'stadium', bridgeport: 'upCanalYard' };
  function setView(name) {
    var bounds = views[name] || views.overview;
    map.fitBounds(bounds, { padding: [12, 12] });
    if (places[viewPlaces[name]]) showDetail(places[viewPlaces[name]]);
    document.querySelectorAll('[data-map-focus]').forEach(function (item) { item.setAttribute('aria-current', 'false'); });
    document.querySelectorAll('[data-map-view]').forEach(function (button) {
      button.setAttribute('aria-pressed', button.getAttribute('data-map-view') === name ? 'true' : 'false');
    });
  }
  document.querySelectorAll('[data-map-view]').forEach(function (button) {
    button.addEventListener('click', function () { setView(button.getAttribute('data-map-view')); });
  });

  function focusPlace(id) {
    var place = places[id];
    if (!place) return;
    statusOn[place.status] = true;
    groupOn[place.group] = true;
    refresh();
    showDetail(place);
    if (place.position) map.flyTo(place.position, place.zoom || 15, { duration: 0.8 });
    document.querySelectorAll('[data-map-view]').forEach(function (button) { button.setAttribute('aria-pressed', 'false'); });
  }

  var placeSelect = document.querySelector('[data-map-place]');
  if (placeSelect) {
    placeSelect.addEventListener('change', function () { focusPlace(placeSelect.value); });
  }
  document.querySelectorAll('[data-map-focus]').forEach(function (button) {
    button.addEventListener('click', function () {
      focusPlace(button.getAttribute('data-map-focus'));
      document.querySelectorAll('[data-map-focus]').forEach(function (item) { item.setAttribute('aria-current', item === button ? 'step' : 'false'); });
      root.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    });
  });

  function updateZoomClasses() {
    var zoom = map.getZoom();
    [13, 14, 15, 15.5].forEach(function (level) {
      root.classList.toggle('zoom-lt-' + String(level).replace('.', '-'), zoom < level);
    });
  }
  map.on('zoomend', updateZoomClasses);

  refresh();
  updateZoomClasses();
  var requested = new URLSearchParams(window.location.search).get('place');
  if (requested && places[requested]) { setView('overview'); focusPlace(requested); }
  else setView('overview');
  window.setTimeout(function () { map.invalidateSize(); }, 0);
})();
