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
    zoom: 13,
    minZoom: 10,
    maxZoom: 19,
    zoomControl: true,
    scrollWheelZoom: true,
    attributionControl: true
  });

  L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 19,
    attribution: 'Tiles &copy; <a href="https://www.esri.com/en-us/legal/terms/services">Esri</a>'
  }).addTo(map);

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, function (character) {
      return {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
      }[character];
    });
  }

  function pointFromLocal(point) {
    return [
      origin.latitude_reference + (point[1] - homeOffset[1]) * latScale,
      origin.longitude_reference + (point[0] - homeOffset[0] - 33) * lonScale
    ];
  }

  function pointsFromLocal(points) {
    return points.map(pointFromLocal);
  }

  function detail(kicker, title, copy, link, href) {
    var kickerNode = document.querySelector('[data-map-detail-kicker]');
    var titleNode = document.querySelector('[data-map-detail-title]');
    var copyNode = document.querySelector('[data-map-detail-copy]');
    var linkNode = document.querySelector('[data-map-detail-link]');
    if (kickerNode) kickerNode.textContent = kicker;
    if (titleNode) titleNode.textContent = title;
    if (copyNode) copyNode.textContent = copy;
    if (linkNode) {
      linkNode.textContent = link + ' ↗';
      linkNode.href = href;
    }
  }

  function popup(title, copy) {
    return '<strong>' + escapeHtml(title) + '</strong><br><span>' + escapeHtml(copy) + '</span>';
  }

  var placeRegistry = {};
  function registerPlace(value, marker, layer, position, kicker, title, copy, link, href) {
    placeRegistry[value] = { marker: marker, layer: layer, position: position, kicker: kicker, title: title, copy: copy, link: link, href: href };
  }

  var stadiumLayer = L.layerGroup().addTo(map);
  var ctaLayer = L.layerGroup().addTo(map);
  var metraLayer = L.layerGroup().addTo(map);
  var parkingLayer = L.layerGroup().addTo(map);
  var proposedLayer = L.layerGroup().addTo(map);
  var contextLayer = L.layerGroup().addTo(map);

  var bowlFootprint = L.polygon(pointsFromLocal(data.bowlFront.concat(data.bowlBack.slice().reverse())), {
    color: '#33483b',
    weight: 2,
    fillColor: '#667969',
    fillOpacity: 0.24,
    className: 'railyards-bowl-footprint'
  }).addTo(stadiumLayer);

  var fieldBoundary = L.polygon(pointsFromLocal(data.fieldBoundary), {
    color: '#33483b',
    weight: 2,
    fillColor: '#799b73',
    fillOpacity: 0.84,
    className: 'railyards-field-boundary'
  }).addTo(stadiumLayer);

  L.polyline(pointsFromLocal(data.bowlBack), {
    color: '#3c5143',
    weight: 3,
    opacity: 0.9,
    className: 'railyards-bowl-back'
  }).addTo(stadiumLayer);
  L.polyline(pointsFromLocal(data.bowlFront), {
    color: '#506857',
    weight: 3,
    opacity: 0.95,
    className: 'railyards-bowl-front'
  }).addTo(stadiumLayer);

  var stadiumMarker = L.circleMarker(stadiumCenter, {
    radius: 8,
    color: '#25352d',
    weight: 3,
    fillColor: '#e8d19c',
    fillOpacity: 1,
    bubblingMouseEvents: false
  }).addTo(stadiumLayer);
  bowlFootprint.bindPopup(popup('The Railyards · modeled bowl footprint', 'The bowl front and back traces are geographically registered from the saved scene specification. They are traced from public imagery with inferred elevations.'));
  fieldBoundary.bindPopup(popup('Modeled field boundary', 'The field boundary is positioned from the saved scene coordinate system. Dimensions remain illustrative.'));
  stadiumMarker.bindPopup(popup('The Railyards', 'Modeled stadium center near the river rail yard, south of Roosevelt Road.'));
  registerPlace('stadium', stadiumMarker, stadiumLayer, stadiumCenter, 'Modeled place', 'The Railyards', 'A geographically registered stadium footprint in the rail yard south of Roosevelt Road. The overlay comes from the saved scene coordinate system and remains an independent reconstruction.', 'Read the source boundary', 'build.html#credits');

  function selectStadium() {
    detail('Modeled place', 'The Railyards', 'A geographically registered stadium footprint in the rail yard south of Roosevelt Road. The overlay comes from the saved scene coordinate system and remains an independent reconstruction.', 'Read the source boundary', 'build.html#credits');
  }
  bowlFootprint.on('click', selectStadium);
  fieldBoundary.on('click', selectStadium);
  stadiumMarker.on('click', selectStadium);

  var ctaColors = {
    'Blue Line': '#347ab4',
    'Red Line': '#c94a45',
    'Orange Line': '#d47c35',
    'Green Line': '#4b8b62'
  };
  var ctaGeoJson = L.geoJSON(data.cta, {
    style: function (feature) {
      var line = feature && feature.properties ? feature.properties.lines : '';
      var color = ctaColors[line] || '#bd6b59';
      return { color: color, weight: 4, opacity: 0.88, lineCap: 'round', lineJoin: 'round' };
    },
    onEachFeature: function (feature, layer) {
      var properties = feature.properties || {};
      var line = properties.lines || 'CTA rail';
      var description = properties.description || 'City of Chicago rail-line geometry.';
      layer.bindPopup(popup(line, description + '. Source: City of Chicago rail-line dataset.'));
      layer.on('click', function () {
        detail('Current transit', line, description + '. These route traces come from the City of Chicago open rail-line dataset; they do not show live service.', 'Open the CTA rail dataset', 'https://data.cityofchicago.org/d/xbyr-jnvx');
      });
    }
  }).addTo(ctaLayer);

  var ctaStations = [
    ['ctaRoosevelt', 'Roosevelt/State · Red / Orange / Green', 'CTA station at Roosevelt Road serving the Red, Orange, and Green lines', 'https://www.transitchicago.com/station/roos/'],
    ['ctaClintonBlue', 'Clinton-Congress · Blue', 'CTA Blue Line station west of the stadium district', 'https://www.transitchicago.com/'],
    ['ctaHarrison', 'Harrison · Red', 'CTA Red Line station near the southern Loop', 'https://www.transitchicago.com/'],
    ['ctaCermak', 'Cermak-Chinatown · Red', 'CTA Red Line station south of the stadium district', 'https://www.transitchicago.com/'],
    ['ctaCermakGreen', 'Cermak-McCormick Place · Green', 'CTA Green Line station by McCormick Place', 'https://www.transitchicago.com/'],
    ['ctaHalstedOrange', 'Halsted-Midway · Orange', 'CTA Orange Line station south-west of the stadium district', 'https://www.transitchicago.com/'],
    ['ctaSox35', 'Sox-35th-Dan Ryan · Red', 'CTA Red Line station near the existing ballpark', 'https://www.transitchicago.com/'],
    ['ctaStateLake', 'State/Lake · Loop', 'CTA elevated Loop station serving the Red, Brown, Green, Orange, Pink, and Purple lines', 'https://www.transitchicago.com/']
  ];
  ctaStations.forEach(function (station) {
    var position = data.stations[station[0]];
    var marker = L.circleMarker(position, {
      radius: 5,
      color: '#c94a45',
      weight: 2,
      fillColor: '#fffaf1',
      fillOpacity: 1
    }).addTo(ctaLayer);
    marker.bindPopup(popup(station[1], station[2]));
    marker.on('click', function () {
      detail('Current transit', station[1], station[2] + '. Station coordinates are fixed orientation points; check CTA for current service and access information.', 'Open CTA station information', station[3]);
    });
    registerPlace(station[0], marker, ctaLayer, position, 'Current transit', station[1], station[2] + '. Station coordinates are fixed orientation points; check CTA for current service and access information.', 'Open CTA station information', station[3]);
  });

  var metraColors = { bnsf: '#a7623b', rockIsland: '#915b37', electric: '#6e6d56' };
  var metraNames = { bnsf: 'BNSF Railway', rockIsland: 'Rock Island', electric: 'Metra Electric' };
  Object.keys(data.metra).forEach(function (key) {
    var route = L.polyline(data.metra[key], {
      color: metraColors[key] || '#9c5d35',
      weight: 4,
      opacity: 0.85,
      lineCap: 'round',
      lineJoin: 'round'
    }).addTo(metraLayer);
    route.bindPopup(popup(metraNames[key] || 'Metra corridor', 'Simplified geographic trace between mapped stations and the downtown corridor; consult Metra for the current system map and schedules.'));
    route.on('click', function () {
      detail('Current transit', metraNames[key] || 'Metra corridor', 'A simplified geographic trace between mapped stations and the downtown corridor. It is orientation context, not a track survey or live schedule.', 'Open Metra maps and schedules', 'https://metra.com/');
    });
  });

  var metraStations = [
    ['metraMuseum', 'Metra Electric · Museum Campus / 11th St', 'Metra Electric station point near Museum Campus', 'https://metra.com/'],
    ['metraLaSalle', 'Rock Island · LaSalle Street', 'Rock Island terminal point in the Loop', 'https://metra.com/'],
    ['unionStation', 'Chicago Union Station', 'Downtown terminal context for BNSF and other services', 'https://metra.com/']
  ];
  metraStations.forEach(function (station) {
    var marker = L.circleMarker(data.stations[station[0]], {
      radius: 5,
      color: '#9c5d35',
      weight: 2,
      fillColor: '#fffaf1',
      fillOpacity: 1
    }).addTo(metraLayer);
    marker.bindPopup(popup(station[1], station[2]));
    marker.on('click', function () {
      detail('Current transit', station[1], station[2] + '. The marker is an orientation point and does not represent live arrivals or platform access.', 'Open Metra maps and schedules', station[3]);
    });
    registerPlace(station[0], marker, metraLayer, data.stations[station[0]], 'Current transit', station[1], station[2] + '. The marker is an orientation point and does not represent live arrivals or platform access.', 'Open Metra maps and schedules', station[3]);
  });

  var parkingPlaces = [
    ['grantParkSouth', 'Grant Park South Garage', 'Current downtown garage location; rates and event availability change.', 'https://www.prod2.millenniumgarages.com/faqs/'],
    ['grantParkNorth', 'Grant Park North Garage', 'Current downtown garage location; rates and event availability change.', 'https://www.prod2.millenniumgarages.com/faqs/'],
    ['millenniumPark', 'Millennium Park Garage', 'Current downtown garage location; rates and event availability change.', 'https://www.prod2.millenniumgarages.com/faqs/'],
    ['millenniumLakeside', 'Millennium Lakeside Garage', 'Current downtown garage location; rates and event availability change.', 'https://www.prod2.millenniumgarages.com/faqs/']
  ];
  parkingPlaces.forEach(function (place) {
    var marker = L.circleMarker(data.parking[place[0]], {
      radius: 6,
      color: '#2e7773',
      weight: 2,
      fillColor: '#d5ebe4',
      fillOpacity: 1
    }).addTo(parkingLayer);
    marker.bindPopup(popup(place[1], place[2]));
    marker.on('click', function () {
      detail('Current parking context', place[1], place[2] + ' No event parking supply has been announced for The Railyards.', 'Open garage location information', place[3]);
    });
    registerPlace(place[0], marker, parkingLayer, data.parking[place[0]], 'Current parking context', place[1], place[2] + ' No event parking supply has been announced for The Railyards.', 'Open garage location information', place[3]);
  });

  var contextPlaces = [
    ['willis', 'Willis Tower', [41.878876, -87.635918], 'Existing landmark orientation point.'],
    ['powerhouse', 'Powerhouse', [41.8773, -87.6379], 'Existing landmark orientation point.'],
    ['rooseveltBridge', 'Roosevelt bridge', [41.867, -87.6322], 'Existing river crossing orientation point.']
  ];
  contextPlaces.forEach(function (place) {
    var marker = L.circleMarker(place[2], {
      radius: 3,
      color: '#5b6b61',
      weight: 1.5,
      fillColor: '#f8f8f3',
      fillOpacity: 1
    }).addTo(contextLayer);
    marker.bindPopup(popup(place[1], place[3]));
    registerPlace(place[0], marker, contextLayer, place[2], 'Current context', place[1], place[3], 'Open the map disclosure', 'map.html#map-title');
  });

  var underConstructionLayer = L.layerGroup().addTo(map);
  var firePlace = ['fireStadium', "McDonald's Park", [41.86472, -87.63222], 'Chicago Fire FC stadium at The 78; officially broken ground on March 3, 2026. Expected opening: Spring 2028.'];
  var fireMarker = L.circleMarker(firePlace[2], {
    radius: 6,
    color: '#2e7773',
    weight: 2,
    fillColor: '#d5ebe4',
    fillOpacity: 1
  }).addTo(underConstructionLayer);
  fireMarker.bindPopup(popup(firePlace[1], firePlace[3]));
  fireMarker.on('click', function () {
    detail('Under construction', firePlace[1], firePlace[3], 'Open Chicago Fire announcement', 'https://www.chicagofirefc.com/news/historic-day-for-the-city-chicago-fire-fc-breaks-ground-on-privately-funded-soccer-stadium-at-the-78');
  });
  registerPlace(firePlace[0], fireMarker, underConstructionLayer, firePlace[2], 'Under construction', firePlace[1], firePlace[3], 'Open Chicago Fire announcement', 'https://www.chicagofirefc.com/news/historic-day-for-the-city-chicago-fire-fc-breaks-ground-on-privately-funded-soccer-stadium-at-the-78');

  var proposedRoute = L.polyline([
    data.stations.ctaRoosevelt,
    [41.8659, -87.6301],
    stadiumCenter
  ], {
    color: '#ab6190',
    weight: 4,
    opacity: 0.9,
    dashArray: '10 8',
    lineCap: 'round'
  }).addTo(proposedLayer);
  proposedRoute.bindPopup(popup('Conceptual stadium arrival link', 'A dashed possibility connecting Roosevelt transit to the modeled footprint. No project, alignment, or delivery date has been announced.'));
  proposedRoute.on('click', function () {
    detail('Conceptual / unconfirmed', 'Stadium arrival link', 'A dashed possibility between Roosevelt transit and the modeled footprint. It is included to make future arrival ideas legible and is not a proposed CTA or Metra project.', 'Read the map disclosure', 'map.html#map-title');
  });
  var proposedStop = L.circleMarker(stadiumCenter, {
    radius: 10,
    color: '#ab6190',
    weight: 2,
    dashArray: '5 4',
    fillColor: '#f5eaf1',
    fillOpacity: 0.92
  }).addTo(proposedLayer);
  proposedStop.bindPopup(popup('Conceptual future arrival point', 'A placeholder for a future connection near the modeled stadium. No station or service has been announced.'));
  proposedStop.on('click', function () {
    detail('Conceptual / unconfirmed', 'Future arrival point', 'A placeholder near the modeled stadium for discussing arrival ideas. No station, route, or service has been announced.', 'Read the map disclosure', 'map.html#map-title');
  });

  var statusLayers = {
    existing: [ctaLayer, metraLayer, parkingLayer, contextLayer],
    proposed: [stadiumLayer, proposedLayer],
    underConstruction: [underConstructionLayer]
  };
  function setStatusVisibility(name, visible) {
    var groupedLayers = statusLayers[name] || [];
    groupedLayers.forEach(function (layer) {
      if (visible && !map.hasLayer(layer)) layer.addTo(map);
      if (!visible && map.hasLayer(layer)) map.removeLayer(layer);
    });
    var button = document.querySelector('[data-map-status="' + name + '"]');
    if (button) button.setAttribute('aria-pressed', visible ? 'true' : 'false');
  }
  document.querySelectorAll('[data-map-status]').forEach(function (button) {
    button.addEventListener('click', function () {
      var name = button.getAttribute('data-map-status');
      setStatusVisibility(name, button.getAttribute('aria-pressed') !== 'true');
    });
  });
  // Keep the modeled center selectable when the conceptual arrival layer is visible.
  stadiumMarker.bringToFront();

  var views = {
    city: L.latLngBounds([[41.82, -87.68], [41.90, -87.60]]),
    stadium: L.latLngBounds([stadiumCenter, data.stations.ctaRoosevelt, [41.858, -87.621]])
  };
  function setView(name) {
    var bounds = views[name] || views.city;
    map.fitBounds(bounds, { padding: [20, 20], maxZoom: name === 'stadium' ? 16 : 13 });
    document.querySelectorAll('[data-map-view]').forEach(function (button) {
      button.setAttribute('aria-pressed', button.getAttribute('data-map-view') === name ? 'true' : 'false');
    });
  }
  document.querySelectorAll('[data-map-view]').forEach(function (button) {
    button.addEventListener('click', function () {
      setView(button.getAttribute('data-map-view'));
    });
  });

  var layers = {
    parking: parkingLayer,
    metra: metraLayer,
    cta: ctaLayer,
    proposed: proposedLayer
  };
  function setLayerVisibility(name, visible) {
    var layer = layers[name];
    if (!layer) return;
    if (visible && !map.hasLayer(layer)) layer.addTo(map);
    if (!visible && map.hasLayer(layer)) map.removeLayer(layer);
    var button = document.querySelector('[data-map-layer="' + name + '"]');
    if (button) button.setAttribute('aria-pressed', visible ? 'true' : 'false');
  }
  document.querySelectorAll('[data-map-layer]').forEach(function (button) {
    button.addEventListener('click', function () {
      var name = button.getAttribute('data-map-layer');
      var layer = layers[name];
      if (!layer) return;
      var active = map.hasLayer(layer);
      setLayerVisibility(name, !active);
    });
  });
  var placeSelect = document.querySelector('[data-map-place]');
  if (placeSelect) {
    function handlePlaceChange() {
      var place = placeRegistry[placeSelect.value];
      if (!place) return;
      detail(place.kicker, place.title, place.copy, place.link, place.href);
      if (place.layer === ctaLayer) setLayerVisibility('cta', true);
      if (place.layer === metraLayer) setLayerVisibility('metra', true);
      if (place.layer === parkingLayer) setLayerVisibility('parking', true);
      if (Array.isArray(place.position) && place.position.length === 2) {
        map.setView(place.position, placeSelect.value === 'stadium' ? 16 : 14);
      }
    }
    placeSelect.addEventListener('change', handlePlaceChange);
    placeSelect.addEventListener('input', handlePlaceChange);
  }

  detail('Modeled place', 'The Railyards', 'A geographically registered stadium footprint in the rail yard south of Roosevelt Road. Select a marker to inspect its relationship to the district.', 'Read the source boundary', 'build.html#credits');
  setView('city');
  window.setTimeout(function () { map.invalidateSize(); }, 0);
})();
