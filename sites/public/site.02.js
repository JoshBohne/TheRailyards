    nav.classList.toggle('is-open', open);
    document.body.classList.toggle('menu-open', open);
  });
  nav?.querySelectorAll('a').forEach((link) => link.addEventListener('click', closeMenu));
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeMenu();
  });

  const progress = document.querySelector('#scroll-progress');
  let scrollFrame = 0;
  function updateScrollUi() {
    scrollFrame = 0;
    const y = window.scrollY;
    header?.classList.toggle('is-scrolled', y > 16);
    if (progress) {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      progress.style.transform = `scaleX(${max > 0 ? Math.min(1, Math.max(0, y / max)) : 0})`;
    }
  }
  window.addEventListener('scroll', () => {
    if (!scrollFrame) scrollFrame = window.requestAnimationFrame(updateScrollUi);
  }, { passive: true });
  updateScrollUi();

  document.querySelectorAll('[data-back-top]').forEach((button) => {
    button.addEventListener('click', () => window.scrollTo({ top: 0, behavior: reducedMotion ? 'auto' : 'smooth' }));
  });

  // Fan-facing guided tour
  const scenes = {
    arrival: {
      index: '01',
      location: 'Roosevelt Road · North approach',
      title: 'Off Roosevelt, into the park.',
      description: 'Follow the raised public park toward the outfield as the pavilion, clock tower, and seating bowl come into view.',
      basis: 'The park elevation is visible in the concept artwork. The route, grading transitions, and camera travel connect gaps the still images do not resolve.',
      evidence: 'Reconstructed',
      evidenceClass: 'evidence-reconstructed',
      poster: 'arrival',
      video: 'arrival',
      aria: 'The approach from Roosevelt Road',
      mapTitle: 'Roosevelt arrival',
      mapCopy: 'Enter from the city at the raised public park.'
    },
    left_center: {
      index: '02',
      location: 'Left-center · Arrival terrace',
      title: 'The field opens all at once.',
      description: 'Move through the terrace and around the restaurant edge until the full bowl, diamond, and skyline reveal themselves.',
