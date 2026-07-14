export function showToast(msg) {
  const t = document.createElement('div');
  t.textContent = msg;
  Object.assign(t.style, {
    position: 'fixed', bottom: '80px', left: '50%', transform: 'translateX(-50%)',
    background: '#0f172a', color: '#fff', padding: '0.5rem 1rem', borderRadius: '0.5rem',
    fontSize: '0.85rem', zIndex: 999, maxWidth: '80%', textAlign: 'center',
    transition: 'opacity 0.3s', opacity: '0'
  });
  document.body.appendChild(t);
  requestAnimationFrame(() => { t.style.opacity = '1'; });
  setTimeout(() => { t.style.opacity = '0'; setTimeout(() => t.remove(), 300); }, 2000);
}
