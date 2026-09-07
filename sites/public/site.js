(() => {
  const parts = Array.from({ length: 8 }, (_, index) => `site.${String(index + 1).padStart(2, '0')}.js`);
  Promise.all(parts.map(async (path) => {
    const response = await fetch(path);
    if (!response.ok) throw new Error(`Failed to load ${path} (${response.status})`);
    return response.text();
  })).then((source) => (0, eval)(source.join(''))).catch((error) => {
    console.error('The Railyards interface failed to load.', error);
  });
})();
