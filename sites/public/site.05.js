    setText('#map-selection-index', scene.index);
    setText('#map-selection-title', scene.mapTitle);
    setText('#map-selection-copy', scene.mapCopy);

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
    mapOpenButton?.setAttribute('data-selected-scene', key);
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
