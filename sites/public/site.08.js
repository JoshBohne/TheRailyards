  const compareRange = document.querySelector('#compare-range');
  const compareOutput = document.querySelector('#compare-output');
  function setComparePosition(value) {
    const safe = Math.max(0, Math.min(100, Number(value)));
    compareFrame?.style.setProperty('--compare-position', `${safe}%`);
    if (compareOutput) compareOutput.textContent = `${safe}% source`;
  }
  compareRange?.addEventListener('input', () => setComparePosition(compareRange.value));
  setComparePosition(compareRange?.value || 50);

  document.querySelectorAll('[data-compare]').forEach((button) => {
    button.addEventListener('click', () => {
      const comparison = comparisons[button.dataset.compare];
      if (!comparison) return;
      document.querySelectorAll('[data-compare]').forEach((item) => item.setAttribute('aria-selected', String(item === button)));
      const source = document.querySelector('#compare-source');
      const model = document.querySelector('#compare-model');
      if (source) { source.src = `media/${comparison.source}.jpg`; source.alt = comparison.sourceAlt; }
      if (model) { model.src = `media/${comparison.model}.jpg`; model.alt = comparison.modelAlt; }
      const caption = document.querySelector('#compare-caption');
      if (caption) caption.innerHTML = comparison.caption;
    });
  });

  // Header section awareness on the long landing page.
  const sectionLinks = [...document.querySelectorAll('.site-nav a[href^="#"]')];
  const observed = sectionLinks.map((link) => document.querySelector(link.getAttribute('href'))).filter(Boolean);
  if ('IntersectionObserver' in window && observed.length) {
    const observer = new IntersectionObserver((entries) => {
      const visible = entries.filter((entry) => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (!visible) return;
      sectionLinks.forEach((link) => {
        if (link.getAttribute('href') === `#${visible.target.id}`) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
    }, { rootMargin: '-25% 0px -60% 0px', threshold: [0.05, 0.25, 0.5] });
    observed.forEach((section) => observer.observe(section));
  }
})();
