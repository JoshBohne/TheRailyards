(() => {
  'use strict';

  const root = document.documentElement;
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const storage = {
    get(key) {
      try { return window.localStorage.getItem(key); } catch { return null; }
    },
    set(key, value) {
      try { window.localStorage.setItem(key, value); } catch { /* Storage can be unavailable in private contexts. */ }
    }
  };

  const toast = document.querySelector('#toast');
  let toastTimer;
  function showToast(message) {
    if (!toast) return;
    window.clearTimeout(toastTimer);
    toast.textContent = message;
    toast.classList.add('is-visible');
    toastTimer = window.setTimeout(() => toast.classList.remove('is-visible'), 2800);
  }

  // Theme
  const themeButton = document.querySelector('[data-theme-toggle]');
  const themeColor = document.querySelector('meta[name="theme-color"]');
  const savedTheme = storage.get('railyards-theme');
  const initialTheme = savedTheme || 'dark';
  root.dataset.theme = initialTheme;
  function syncThemeButton() {
    if (!themeButton) return;
    const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
    themeButton.setAttribute('aria-label', `Switch to ${next} theme`);
    themeColor?.setAttribute('content', root.dataset.theme === 'dark' ? '#0a0b0d' : '#f1eee7');
  }
  syncThemeButton();
  themeButton?.addEventListener('click', () => {
    root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    storage.set('railyards-theme', root.dataset.theme);
    syncThemeButton();
  });

  // Header, mobile navigation, and scroll progress
  const header = document.querySelector('[data-header]');
  const menuButton = document.querySelector('[data-menu-toggle]');
  const nav = document.querySelector('[data-nav]');
  function closeMenu() {
    if (!menuButton || !nav) return;
    menuButton.setAttribute('aria-expanded', 'false');
    nav.classList.remove('is-open');
    document.body.classList.remove('menu-open');
  }
  menuButton?.addEventListener('click', () => {
    if (!nav) return;
    const open = menuButton.getAttribute('aria-expanded') !== 'true';
    menuButton.setAttribute('aria-expanded', String(open));
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
      index: '04',
      location: 'Roosevelt Road · North approach',
      title: 'Park walk.',
      description: 'Walk from the raised park toward the outfield.',
      basis: 'The park elevation is visible in the concept artwork. The route, grading transitions, and camera travel connect gaps the still images do not resolve.',
      evidence: 'Reconstructed',
      evidenceClass: 'evidence-reconstructed',
      poster: 'arrival',
      video: 'arrival',
      aria: 'The approach from Roosevelt Road',
    },
    left_center: {
      index: '02',
      location: 'Left-center · Arrival terrace',
      title: 'Inside the bowl.',
      description: 'The field opens up from left-center.',
      basis: 'The source images establish the raised arrival condition and major masses. The exact path, retaining edges, stairs, and close-range details remain interpretive.',
      evidence: 'Interpretive',
      evidenceClass: 'evidence-interpretive',
      poster: 'left_center',
      video: 'left_center',
      aria: 'The field reveal from the left-center terrace',
    },
    boat: {
      index: '01',
      location: 'Chicago River · Boat level',
      title: 'From the river.',
      description: 'A boat-level view of the ballpark and waterfront.',
      basis: 'The river, stadium edge, and principal buildings are source-backed. Low-level facade detail, activity, and the continuous boat route are reconstructed between fixed views.',
      evidence: 'Reconstructed',
      evidenceClass: 'evidence-reconstructed',
      poster: 'boat',
      video: 'boat',
      aria: 'The ballpark viewed from a boat on the Chicago River',
    },
    river: {
      index: '03',
      location: 'Home plate to river · Modeled line',
      title: 'Into the river.',
      description: 'An illustrative home run. The flight is authored, not simulated.',
      basis: 'The current model measures 423 feet to the water and 469 feet to the illustrated splash along this chosen line. The arc is enlarged and authored for visibility; it is not an aerodynamic prediction or official dimension.',
      evidence: 'Illustrative',
      evidenceClass: 'evidence-illustrative',
      poster: 'river-poster',
      video: 'river',
      aria: 'An illustrated home run traveling from home plate to the Chicago River',
    }
  };
  const sceneKeys = ['boat', 'left_center', 'river', 'arrival'];
  const tour = document.querySelector('[data-tour-shell]');
  const video = document.querySelector('#scene-video');
  const videoSource = video?.querySelector('source');
  const playButton = document.querySelector('[data-scene-play]');
  const sceneEvidence = document.querySelector('#scene-evidence');
  let currentScene = 'boat';

  function sceneFromUrl() {
    const key = new URL(window.location.href).searchParams.get('view');
    return key && Object.hasOwn(scenes, key) ? key : 'boat';
  }

  function updateUrl(key, mode = 'replace') {
    const url = new URL(window.location.href);
    url.searchParams.set('view', key);
    if (!url.hash || url.hash === '#top') url.hash = 'tour';
    window.history[mode === 'push' ? 'pushState' : 'replaceState']({ scene: key }, '', url);
  }

  function setText(selector, text) {
    const element = document.querySelector(selector);
    if (element) element.textContent = text;
  }

  function updateScene(key, options = {}) {
    if (!scenes[key]) return;
    const { updateHistory = true, historyMode = 'replace', autoplay = false, focusTour = false } = options;
    const scene = scenes[key];
    const changed = key !== currentScene;
    currentScene = key;

    document.querySelectorAll('[data-scene]').forEach((button) => {
      const active = button.dataset.scene === key;
      button.classList.toggle('is-active', active);
      if (button.getAttribute('role') === 'tab') {
        button.setAttribute('aria-selected', String(active));
        button.tabIndex = active ? 0 : -1;
      } else if (button.classList.contains('map-hotspot')) {
        button.setAttribute('aria-pressed', String(active));
      }
    });

    if (video && videoSource) {
      const sourcePath = `media/${scene.video}.mp4`;
      const posterPath = `media/${scene.poster}.jpg`;
      if (!videoSource.src.endsWith(sourcePath) || changed) {
        video.pause();
        video.poster = posterPath;
        videoSource.src = sourcePath;
        video.setAttribute('aria-label', scene.aria);
        video.load();
      }
    }

    setText('#scene-count', `${scene.index} / 04`);
    setText('#scene-location', scene.location);
    setText('#scene-title', scene.title);
    setText('#scene-description', scene.description);
    setText('#scene-basis', scene.basis);

    if (sceneEvidence) {
      sceneEvidence.textContent = scene.evidence;
      sceneEvidence.className = `evidence-chip ${scene.evidenceClass}`;
    }
    const still = document.querySelector('#scene-still');
    if (still) still.href = `media/${scene.poster}.jpg`;
    if (playButton) {
      playButton.classList.remove('is-hidden');
      playButton.setAttribute('aria-label', `Play ${scene.aria.toLowerCase()}`);
      const label = playButton.querySelector('small');
      if (label) label.textContent = 'Play film';
    }
    const activeTab = document.querySelector('.scene-tab.is-active');
    const rail = activeTab?.closest('.scene-rail');
    if (activeTab && rail && rail.scrollWidth > rail.clientWidth) {
      rail.scrollTo({
        left: activeTab.offsetLeft - (rail.clientWidth - activeTab.clientWidth) / 2,
        behavior: reducedMotion ? 'auto' : 'smooth'
      });
    }

    if (updateHistory) updateUrl(key, historyMode);
    if (focusTour && tour) tour.scrollIntoView({ block: 'start', behavior: reducedMotion ? 'auto' : 'smooth' });
    if (autoplay && video) {
      video.play().catch(() => showToast('Use the video controls to start the film.'));
    }
  }

  document.querySelectorAll('.scene-tab[data-scene]').forEach((button) => {
    button.addEventListener('click', () => updateScene(button.dataset.scene, {
      updateHistory: true,
      historyMode: 'push'
    }));
    button.addEventListener('keydown', (event) => {
      const currentIndex = sceneKeys.indexOf(button.dataset.scene);
      let nextIndex = null;
      if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') nextIndex = (currentIndex - 1 + sceneKeys.length) % sceneKeys.length;
      if (event.key === 'ArrowRight' || event.key === 'ArrowDown') nextIndex = (currentIndex + 1) % sceneKeys.length;
      if (event.key === 'Home') nextIndex = 0;
      if (event.key === 'End') nextIndex = sceneKeys.length - 1;
      if (nextIndex === null) return;
      event.preventDefault();
      const nextKey = sceneKeys[nextIndex];
      updateScene(nextKey, { updateHistory: true, historyMode: 'push' });
      document.querySelector(`.scene-tab[data-scene="${nextKey}"]`)?.focus();
    });
  });




  function stepScene(direction) {
    const index = sceneKeys.indexOf(currentScene);
    const next = sceneKeys[(index + direction + sceneKeys.length) % sceneKeys.length];
    updateScene(next, { updateHistory: true, historyMode: 'push' });
  }
  document.querySelector('[data-scene-prev]')?.addEventListener('click', () => stepScene(-1));
  document.querySelector('[data-scene-next]')?.addEventListener('click', () => stepScene(1));
  tour?.addEventListener('keydown', (event) => {
    if (event.target.matches('input, select, textarea, button, a')) return;
    if (event.key === 'ArrowLeft') { event.preventDefault(); stepScene(-1); }
    if (event.key === 'ArrowRight') { event.preventDefault(); stepScene(1); }
  });

  playButton?.addEventListener('click', async () => {
    if (!video) return;
    if (!video.paused) { video.pause(); return; }
    try { await video.play(); } catch { showToast('Use the video controls to start the film.'); }
  });
  video?.addEventListener('play', () => playButton?.classList.add('is-hidden'));
  video?.addEventListener('pause', () => {
    if (video.currentTime < video.duration - 0.1) playButton?.classList.remove('is-hidden');
  });
  video?.addEventListener('ended', () => playButton?.classList.remove('is-hidden'));


  document.querySelector('[data-share-scene]')?.addEventListener('click', async () => {
    const scene = scenes[currentScene];
    const url = new URL(window.location.href);
    url.searchParams.set('view', currentScene);
    url.hash = 'tour';
    const data = { title: `The Railyards: ${scene.title}`, text: scene.description, url: url.toString() };
    try {
      if (navigator.share) {
        await navigator.share(data);
        showToast('View shared.');
      } else {
        await navigator.clipboard.writeText(url.toString());
        showToast('Link copied.');
      }
    } catch (error) {
      if (error?.name !== 'AbortError') showToast('Copy the URL from your browser to share this view.');
    }
  });

  window.addEventListener('popstate', () => updateScene(sceneFromUrl(), { updateHistory: false }));
  if (tour) updateScene(sceneFromUrl(), { updateHistory: false });

  // Source / reconstruction comparison
  const comparisons = {
    north: {
      source: 'source-north', model: 'model-north',
      sourceAlt: 'The published north aerial concept rendering',
      modelAlt: 'The reconstruction through the matched north aerial camera',
      caption: 'North aerial.'
    },
    south: {
      source: 'source-south', model: 'model-south',
      sourceAlt: 'The published south aerial concept rendering',
      modelAlt: 'The reconstruction through the matched south aerial camera',
      caption: 'South aerial.'
    },
    bridge: {
      source: 'source-bridge', model: 'model-bridge',
      sourceAlt: 'The published concept view from Roosevelt Road bridge',
      modelAlt: 'The reconstruction through the matched Roosevelt Road bridge camera',
      caption: 'Roosevelt bridge.'
    }
  };
  const compareFrame = document.querySelector('[data-compare-frame]');
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
      if (caption) caption.textContent = comparison.caption;
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
