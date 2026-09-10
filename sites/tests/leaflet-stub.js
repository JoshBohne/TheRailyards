/* Offline adapter for navigation tests, NOT a cartographic renderer. */
(function () {
  const groups = [];
  class Layer {
    constructor(kind, value, options) { this.kind = kind; this.value = value; this.options = options || {}; this.events = {}; }
    addTo(target) { target.addLayer(this); return this; }
    on(names, fn) { names.split(' ').forEach(name => { (this.events[name] ||= []).push(fn); }); return this; }
    getLatLng() { return this.value; }
  }
  class Group extends Layer {
    constructor(layers) { super('group'); this.layers = layers || []; this.testIndex = groups.length; groups.push(this); }
    getLayers() { return this.layers.slice(); }
    addLayer(layer) { if (!this.layers.includes(layer)) this.layers.push(layer); return this; }
    eachLayer(fn) { this.layers.forEach(fn); }
  }
  class Bounds {
    constructor(points) { this.points = []; this.extend(points); }
    extend(value) {
      if (value instanceof Bounds) this.points.push(...value.points);
      else if (Array.isArray(value) && typeof value[0] === 'number') this.points.push(value);
      else if (Array.isArray(value)) value.forEach(point => this.extend(point));
      return this;
    }
    getCenter() { return [0, 1].map(i => (Math.min(...this.points.map(p => p[i])) + Math.max(...this.points.map(p => p[i]))) / 2); }
    getNorth() { return Math.max(...this.points.map(p => p[0])); }
    getSouth() { return Math.min(...this.points.map(p => p[0])); }
  }
  function handler() { return { value: true, enable() { this.value = true; }, disable() { this.value = false; }, enabled() { return this.value; } }; }
  class Map extends Layer {
    constructor(root, options) {
      super('map'); this.root = root; this.layers = new Set(); this.calls = []; this.zoom = options.zoom; this.center = options.center;
      ['dragging','touchZoom','doubleClickZoom','boxZoom','keyboard','tapHold','scrollWheelZoom'].forEach(name => { this[name] = handler(); });
      this.attributionControl = { setPrefix() {} };
      root.classList.add('leaflet-container');
      window.__map = this; window.__groups = groups;
    }
    addLayer(layer) { this.layers.add(layer); return this; }
    removeLayer(layer) { this.layers.delete(layer); return this; }
    hasLayer(layer) { return this.layers.has(layer); }
    stop() { this.calls.push({ method: 'stop' }); return this; }
    getZoom() { return this.zoom; }
    getCenter() { return this.center; }
    fitBounds(bounds, options) { this.center = bounds.getCenter(); this.zoom = options.maxZoom || 15; this.calls.push({ method: 'fitBounds', options }); this.fire('zoomend'); return this; }
    setView(center, zoom, options) { this.center = center; this.zoom = zoom; this.calls.push({ method: 'setView', options }); this.fire('zoomend'); return this; }
    invalidateSize(options) { this.calls.push({ method: 'invalidateSize', options }); return this; }
    panBy(offset, options) { this.calls.push({ method: 'panBy', options }); return this; }
    closePopup() { this.popup = null; return this; }
    fire(name) { (this.events[name] || []).forEach(fn => fn()); }
  }
  window.L = {
    map: (root, opts) => new Map(root, opts),
    layerGroup: layers => new Group(layers), LayerGroup: Group,
    latLngBounds: points => new Bounds(points),
    tileLayer: (url, opts) => new Layer('tile', url, opts),
    svg: opts => new Layer('svg', null, opts),
    polygon: (points, opts) => new Layer('polygon', points, opts),
    polyline: (points, opts) => new Layer('polyline', points, opts),
    circle: (point, opts) => new Layer('circle', point, opts),
    marker: (point, opts) => new Layer('marker', point, opts),
    divIcon: options => options,
    geoJSON: (data, opts) => new Layer('geoJSON', data, opts),
    extend: (target, ...sources) => Object.assign(target, ...sources),
    popup: () => ({ setLatLng() { return this; }, setContent(html) { this.html = html; return this; }, openOn(map) { map.popup = this; return this; } })
  };
})();
