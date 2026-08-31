(() => {
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.primary-nav');
  const closeMenu = () => {
    if (!toggle || !nav) return;
    toggle.setAttribute('aria-expanded', 'false');
    nav.classList.remove('open');
    document.body.classList.remove('menu-open');
  };
  toggle?.addEventListener('click', () => {
    const open = toggle.getAttribute('aria-expanded') !== 'true';
    toggle.setAttribute('aria-expanded', String(open));
    nav.classList.toggle('open', open);
    document.body.classList.toggle('menu-open', open);
  });
  document.querySelectorAll('.nav-group > button').forEach((button) => {
    button.addEventListener('click', () => {
      const group = button.closest('.nav-group');
      const open = !group.classList.contains('open');
      document.querySelectorAll('.nav-group.open').forEach((item) => item.classList.remove('open'));
      group.classList.toggle('open', open);
      button.setAttribute('aria-expanded', String(open));
    });
  });
  nav?.querySelectorAll('a').forEach((link) => link.addEventListener('click', closeMenu));
  document.addEventListener('click', (event) => {
    if (!event.target.closest('.nav-group')) document.querySelectorAll('.nav-group.open').forEach((item) => item.classList.remove('open'));
  });
  document.addEventListener('keydown', (event) => { if (event.key === 'Escape') closeMenu(); });

  const hero = document.querySelector('[data-hero]');
  const media = hero?.querySelector('.hero-media');
  const slides = [...(hero?.querySelectorAll('.hero-slides [data-src]') || [])];
  if (media && slides.length > 1 && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    let index = 0;
    const preload = (next) => { const image = new Image(); image.src = slides[next].dataset.src; };
    preload(1);
    window.setInterval(() => {
      index = (index + 1) % slides.length;
      media.style.opacity = '0.55';
      window.setTimeout(() => {
        const safeUrl = slides[index].dataset.src.replace(/"/g, '%22');
        media.style.backgroundImage = 'url("' + safeUrl + '")';
        media.style.opacity = '1';
        preload((index + 1) % slides.length);
      }, 300);
    }, 6500);
  }
})();
