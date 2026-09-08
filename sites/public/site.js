(() => {
  'use strict';
  document.querySelectorAll('[data-compare-section]').forEach(section => {
    const comparison = section.querySelector('[data-comparison]');
    const opacityControl = section.querySelector('.opacity-control');
    const swipe = section.querySelector('.swipe-input');
    const handle = section.querySelector('.swipe-handle');
    section.querySelectorAll('[data-mode]').forEach(button => {
      button.addEventListener('click', () => {
        const mode = button.dataset.mode;
        comparison.dataset.layout = mode;
        opacityControl.hidden = mode !== 'overlay';
        swipe.hidden = handle.hidden = mode !== 'swipe';
        section.querySelectorAll('[data-mode]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
      });
    });
    section.querySelector('[data-opacity]').addEventListener('input', event => {
      comparison.style.setProperty('--source-opacity', String(Number(event.target.value) / 100));
      section.querySelector('output').value = `${event.target.value}%`;
    });
    swipe.addEventListener('input', () => comparison.style.setProperty('--swipe-position', `${swipe.value}%`));
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
  const skyline = document.querySelector('.footer-skyline');
  if (skyline && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      if (entries.some(entry => entry.isIntersecting)) {
        skyline.classList.add('skyline-arriving');
        observer.disconnect();
      }
    }, { threshold: 0.2 });
    observer.observe(skyline);
  }
  const film = document.querySelector('#overview-film');
  if (film && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    film.play().catch(() => { film.controls = true; });
  }
})();
