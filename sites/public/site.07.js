
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
      caption: '<strong>North aerial.</strong> This is the broadest source view and the main test for the bowl, park, river edge, and surrounding district.'
    },
    south: {
      source: 'source-south', model: 'model-south',
      sourceAlt: 'The published south aerial concept rendering',
      modelAlt: 'The reconstruction through the matched south aerial camera',
      caption: '<strong>South aerial.</strong> This angle tests the open outfield, tower relationship, rail corridor, and the district extending beyond the stadium.'
    },
    bridge: {
      source: 'source-bridge', model: 'model-bridge',
      sourceAlt: 'The published concept view from Roosevelt Road bridge',
      modelAlt: 'The reconstruction through the matched Roosevelt Road bridge camera',
      caption: '<strong>Roosevelt bridge.</strong> This street-level source is the strongest check on arrival scale, the clock tower, and the park-to-ballpark connection.'
    }
  };
  const compareFrame = document.querySelector('[data-compare-frame]');
