'use strict';

// Utilitaire API partagé entre toutes les pages
async function api(path, options = {}) {
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.detail || err.error || res.statusText);
  }
  return res.json();
}

// Toast notification
function toast(msg, duration = 3000) {
  const el = document.createElement('div');
  el.style.cssText = 'position:fixed;bottom:2rem;right:1rem;background:#1B2A4A;color:white;padding:1rem 1.5rem;border-radius:12px;font-weight:600;z-index:300;animation:slideIn .3s ease;';
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), duration);
}
