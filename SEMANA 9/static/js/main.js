// Toggle rápido usando Bootstrap 5.3 (data-bs-theme)
(function () {
  const root = document.documentElement; // <html>
  const btn = document.getElementById('themeToggle');
  if (!btn) return;

  // Preferencia guardada
  const saved = localStorage.getItem('sv-theme');
  if (saved) root.setAttribute('data-bs-theme', saved);

  btn.addEventListener('click', () => {
    const current = root.getAttribute('data-bs-theme') || 'light';
    const next = current === 'light' ? 'dark' : 'light';
    root.setAttribute('data-bs-theme', next);
    localStorage.setItem('sv-theme', next);
  });
})();