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
      const label = filter === 'all' ? 'views' : filter;
      document.querySelector('#gallery-count').textContent = `${visible} ${visible === 1 ? label.slice(0, -1) : label}`;
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
})();

const feedbackDialog = document.querySelector('#feedback-dialog');
const feedbackForm = document.querySelector('#feedback-form');
if (feedbackDialog instanceof HTMLDialogElement && feedbackForm instanceof HTMLFormElement) {
  const status = document.querySelector('#feedback-status');
  const submit = feedbackForm.querySelector('[type="submit"]');
  let submissionId = crypto.randomUUID();
  let lastPayload = '';
  document.querySelectorAll('[data-feedback-open]').forEach(button => button.addEventListener('click', () => feedbackDialog.showModal()));
  document.querySelector('[data-feedback-close]')?.addEventListener('click', () => feedbackDialog.close());
  feedbackForm.addEventListener('submit', async event => {
    event.preventDefault();
    if (!feedbackForm.reportValidity() || submit.disabled) return;
    const fields = new FormData(feedbackForm);
    const payload = { message: String(fields.get('message') || '').trim(), category: fields.get('category'), page: location.pathname, website: fields.get('website') };
    const serialized = JSON.stringify(payload);
    if (lastPayload && serialized !== lastPayload) submissionId = crypto.randomUUID();
    lastPayload = serialized;
    submit.disabled = true;
    status.textContent = 'Sending…';
    try {
      const response = await fetch('/api/feedback', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id: submissionId, ...payload }) });
      const result = await response.json();
      if (response.status !== 201 || result.message !== 'Saved.') throw new Error('Feedback was not saved');
      status.textContent = 'Thanks — your feedback is saved for Josh.';
      feedbackForm.reset();
      submissionId = crypto.randomUUID();
      lastPayload = '';
    } catch {
      status.textContent = 'Your feedback wasn’t saved. Please try again; your message is still here.';
    } finally {
      submit.disabled = false;
    }
  });
}
