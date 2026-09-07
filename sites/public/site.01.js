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
