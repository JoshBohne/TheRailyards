  const playButton = document.querySelector('[data-scene-play]');
  const sceneEvidence = document.querySelector('#scene-evidence');
  const mapOpenButton = document.querySelector('[data-map-open]');
  let currentScene = 'arrival';

  function sceneFromUrl() {
    const key = new URL(window.location.href).searchParams.get('view');
    return key && scenes[key] ? key : 'arrival';
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
