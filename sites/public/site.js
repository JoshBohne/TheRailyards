(() => {
  'use strict';
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
      document.querySelectorAll('[data-compare]').forEach((item) => item.setAttribute('aria-pressed', String(item === button)));
      const source = document.querySelector('#compare-source');
      const model = document.querySelector('#compare-model');
      if (source) { source.src = `media/${comparison.source}.jpg`; source.alt = comparison.sourceAlt; }
      if (model) { model.src = `media/${comparison.model}.jpg`; model.alt = comparison.modelAlt; }
      const caption = document.querySelector('#compare-caption');
      if (caption) caption.textContent = comparison.caption;
    });
  });

})();
