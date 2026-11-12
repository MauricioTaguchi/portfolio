/* Shared appearance preference for the portfolio and its reading pages. */
(() => {
  'use strict';
  const key = 'portfolio-theme-v1';
  const root = document.documentElement;
  const system = window.matchMedia('(prefers-color-scheme: dark)');
  let preference = null;
  let toggle;
  let reset;
  try {
    const saved = localStorage.getItem(key);
    if (saved === 'light' || saved === 'dark') preference = saved;
  } catch { /* The control also works when browser storage is unavailable. */ }

  function paint() {
    const dark = preference ? preference === 'dark' : system.matches;
    root.dataset.theme = dark ? 'dark' : 'light';
    root.style.colorScheme = dark ? 'dark' : 'light';
    document.querySelector('meta[name="theme-color"]')?.setAttribute('content', dark ? '#11151d' : '#f5f5f3');
    if (!toggle) return;
    const pt = root.lang.toLowerCase().startsWith('pt');
    toggle.setAttribute('aria-pressed', String(dark));
    toggle.setAttribute('aria-label', pt ? 'Modo escuro' : 'Dark mode');
    toggle.title = pt ? (dark ? 'Ativar modo claro' : 'Ativar modo escuro') : (dark ? 'Switch to light mode' : 'Switch to dark mode');
    toggle.querySelector('.theme-control-label').textContent = pt ? (dark ? 'Escuro' : 'Claro') : (dark ? 'Dark' : 'Light');
    toggle.querySelector('.theme-control-icon').textContent = dark ? '☾' : '☀';
    reset.hidden = preference === null;
    reset.setAttribute('aria-label', pt ? 'Usar o tema do dispositivo' : 'Use device theme');
    reset.title = pt ? 'Usar o tema do dispositivo' : 'Use device theme';
  }
  function choose(next) {
    preference = next;
    try { next === null ? localStorage.removeItem(key) : localStorage.setItem(key, next); } catch { /* In-memory choice remains active. */ }
    paint();
  }
  paint();
  system.addEventListener('change', () => { if (preference === null) paint(); });
  window.addEventListener('storage', event => {
    if (event.key === key || event.key === null) {
      preference = event.newValue === 'dark' || event.newValue === 'light' ? event.newValue : null;
      paint();
    }
  });
  document.addEventListener('DOMContentLoaded', () => {
    const control = document.createElement('div');
    control.className = 'theme-control';
    toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'theme-control-toggle';
    toggle.innerHTML = '<span class="theme-control-icon" aria-hidden="true"></span><span class="theme-control-label"></span>';
    toggle.addEventListener('click', () => choose(root.dataset.theme === 'dark' ? 'light' : 'dark'));
    reset = document.createElement('button');
    reset.type = 'button';
    reset.className = 'theme-control-reset';
    reset.innerHTML = '<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="3" y="4" width="18" height="13" rx="2"/><path d="M8 21h8m-4-4v4"/></svg>';
    reset.addEventListener('click', () => choose(null));
    control.append(toggle, reset);
    document.body.append(control);
    new MutationObserver(paint).observe(root, { attributes: true, attributeFilter: ['lang'] });
    paint();
  }, { once: true });
})();
