(() => {
  'use strict';
  const comparison = document.querySelector('[data-comparison]');
  const opacity = document.querySelector('#compare-opacity');
  const output = document.querySelector('#compare-output');
  document.querySelectorAll('[data-compare]').forEach(button => {
    button.addEventListener('click', () => {
      const view = button.dataset.compare;
      document.querySelectorAll('[data-compare]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
      for (const kind of ['source', 'model']) {
        const image = document.querySelector(`#compare-${kind}`);
        image.src = `media/${kind}-${view}.jpg`;
        image.alt = `${button.textContent}: ${kind === 'source' ? 'published concept by AECOM / Canal Edge' : 'V12 reconstruction'}`;
      }
    });
  });
  document.querySelectorAll('[data-layout]').forEach(button => {
    if (button.tagName !== 'BUTTON') return;
    button.addEventListener('click', () => {
      comparison.dataset.layout = button.dataset.layout;
      document.querySelector('.opacity-control').hidden = button.dataset.layout !== 'overlay';
      document.querySelectorAll('button[data-layout]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
    });
  });
  opacity?.addEventListener('input', () => {
    comparison.style.setProperty('--source-opacity', String(Number(opacity.value) / 100));
    output.value = `${opacity.value}%`;
  });
  document.querySelectorAll('[data-filter]').forEach(button => {
    button.addEventListener('click', () => {
      const filter = button.dataset.filter;
      let visible = 0;
      document.querySelectorAll('[data-media]').forEach(item => {
        item.hidden = filter !== 'all' && item.dataset.media !== filter;
        if (item.hidden) item.querySelector('video')?.pause();
        else visible++;
      });
      document.querySelectorAll('[data-filter]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
      document.querySelector('#gallery-count').textContent = `${visible} ${filter === 'all' ? 'views' : filter}`;
    });
  });
  const film = document.querySelector('#overview-film');
  if (film && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    film.play().catch(() => { film.controls = true; });
  }
})();
