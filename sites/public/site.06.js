      const nextKey = sceneKeys[nextIndex];
      updateScene(nextKey, { updateHistory: true, historyMode: 'push' });
      document.querySelector(`.scene-tab[data-scene="${nextKey}"]`)?.focus();
    });
  });

  document.querySelectorAll('.map-hotspot[data-scene]').forEach((button) => {
    button.addEventListener('click', () => updateScene(button.dataset.scene, {
      updateHistory: true,
      historyMode: 'push'
    }));
  });

  document.querySelectorAll('[data-jump-tour]').forEach((button) => {
    button.addEventListener('click', () => updateScene(button.dataset.scene, { updateHistory: true, historyMode: 'push', focusTour: true }));
  });

  document.querySelector('[data-start-tour]')?.addEventListener('click', () => {
    updateScene(currentScene, { updateHistory: true, focusTour: true });
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

  mapOpenButton?.addEventListener('click', () => updateScene(currentScene, { updateHistory: true, historyMode: 'push', focusTour: true }));
