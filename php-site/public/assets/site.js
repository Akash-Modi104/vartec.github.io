(() => {
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.primary-nav');
  const mobileLayout = window.matchMedia('(max-width: 1000px)');
  const syncNavFocus = () => { if (nav) nav.inert = mobileLayout.matches && !nav.classList.contains('open'); };
  syncNavFocus();
  mobileLayout.addEventListener('change', () => { closeMenu(); syncNavFocus(); });
  const closeDropdowns = () => document.querySelectorAll('.nav-group').forEach((group) => {
    group.classList.remove('open');
    group.querySelector('button')?.setAttribute('aria-expanded', 'false');
  });
  const closeMenu = () => {
    closeDropdowns();
    if (!toggle || !nav) return;
    toggle.setAttribute('aria-expanded', 'false');
    nav.classList.remove('open');
    document.body.classList.remove('menu-open');
    syncNavFocus();
  };
  toggle?.addEventListener('click', () => {
    const open = toggle.getAttribute('aria-expanded') !== 'true';
    toggle.setAttribute('aria-expanded', String(open));
    nav.classList.toggle('open', open);
    document.body.classList.toggle('menu-open', open);
    syncNavFocus();
  });
  document.querySelectorAll('.nav-group > button').forEach((button) => {
    button.addEventListener('click', () => {
      const group = button.closest('.nav-group');
      const open = !group.classList.contains('open');
      closeDropdowns();
      group.classList.toggle('open', open);
      button.setAttribute('aria-expanded', String(open));
    });
  });
  nav?.querySelectorAll('a').forEach((link) => link.addEventListener('click', closeMenu));
  document.addEventListener('click', (event) => {
    if (!event.target.closest('.nav-group')) closeDropdowns();
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      const wasOpen = nav?.classList.contains('open');
      closeMenu();
      if (wasOpen) toggle?.focus();
    }
  });

  const header = document.querySelector('[data-header]');
  const banner = document.querySelector('[data-hero]');
  const onScroll = () => {
    header?.classList.toggle('scrolled', window.scrollY > 8);
    // Over the banner the help button shrinks to its icon so it never covers the banner text.
    document.querySelector('[data-chatbot]')?.classList.toggle('compact', !!banner && window.scrollY < banner.offsetHeight - 160);
  };
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  const calm = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Full-width banner: cross-fades through the chosen photos; arrows and dots let visitors choose.
  const hero = document.querySelector('[data-hero]');
  const stage = hero?.querySelector('[data-hero-stage]');
  const list = [...(hero?.querySelectorAll('[data-hero-list] [data-src]') || [])];
  const controls = hero?.querySelector('[data-hero-controls]');
  if (stage && controls && list.length > 1) {
    const images = [stage.querySelector('.hero-img')];
    const dots = controls.querySelector('[data-hero-dots]');
    let index = 0;
    let timer = null;
    const imageFor = (n) => {
      if (!images[n]) {
        const image = document.createElement('img');
        image.className = 'hero-img';
        image.alt = list[n].dataset.alt || '';
        image.decoding = 'async';
        image.src = list[n].dataset.src;
        stage.appendChild(image);
        images[n] = image;
      }
      return images[n];
    };
    const show = (n) => {
      index = (n + list.length) % list.length;
      const next = imageFor(index);
      const reveal = () => {
        images.forEach((image, i) => image?.classList.toggle('is-active', i === index));
        [...dots.children].forEach((dot, i) => dot.setAttribute('aria-current', String(i === index)));
      };
      if (next.complete) reveal(); else next.addEventListener('load', reveal, { once: true });
      imageFor((index + 1) % list.length); // have the following photo ready
    };
    const stop = () => { window.clearInterval(timer); timer = null; };
    const start = () => { if (!calm && !timer) timer = window.setInterval(() => show(index + 1), 6500); };
    list.forEach((item, n) => {
      const dot = document.createElement('button');
      dot.type = 'button';
      dot.setAttribute('aria-label', 'Photo ' + (n + 1) + ' of ' + list.length + (item.dataset.alt ? ': ' + item.dataset.alt : ''));
      dot.setAttribute('aria-current', String(n === 0));
      dot.addEventListener('click', () => { stop(); show(n); start(); });
      dots.appendChild(dot);
    });
    controls.querySelector('[data-hero-prev]').addEventListener('click', () => { stop(); show(index - 1); start(); });
    controls.querySelector('[data-hero-next]').addEventListener('click', () => { stop(); show(index + 1); start(); });
    controls.addEventListener('focusin', stop);
    controls.addEventListener('focusout', start);
    document.addEventListener('visibilitychange', () => (document.hidden ? stop() : start()));
    controls.hidden = false;
    window.setTimeout(() => imageFor(1), 2500);
    start();
  }

  // The video only loads and plays once it is on screen, so it does not slow the first view.
  const video = document.querySelector('[data-inview-video]');
  if (video && 'IntersectionObserver' in window) {
    let visible = false;
    let userPaused = false;
    video.addEventListener('pause', () => { if (visible && !video.ended) userPaused = true; });
    video.addEventListener('play', () => { userPaused = false; });
    new IntersectionObserver((entries) => entries.forEach((entry) => {
      visible = entry.isIntersecting;
      if (visible && !userPaused && !calm) video.play().catch(() => {});
      else if (!visible) video.pause();
    }), { threshold: 0.35 }).observe(video);
  }

  // Sections below the first screen ease in as they are scrolled to.
  if (!calm && 'IntersectionObserver' in window) {
    const watcher = new IntersectionObserver((entries) => entries.forEach((entry) => {
      if (entry.isIntersecting) { entry.target.classList.add('in'); watcher.unobserve(entry.target); }
    }), { rootMargin: '0px 0px -8% 0px' });
    document.querySelectorAll('[data-reveal]').forEach((element) => {
      if (element.getBoundingClientRect().top > window.innerHeight) { element.classList.add('reveal'); watcher.observe(element); }
    });
  }

  const chatbot = document.querySelector('[data-chatbot]');
  if (chatbot) {
    const panel = chatbot.querySelector('.chatbot-panel');
    const launcher = chatbot.querySelector('[data-chat-open]');
    const close = chatbot.querySelector('[data-chat-close]');
    const messages = chatbot.querySelector('[data-chat-messages]');
    const form = chatbot.querySelector('[data-chat-form]');
    const input = chatbot.querySelector('[data-chat-input]');
    const contactLink = '<a href="#contact">contact our team</a>';
    const replyFor = (question) => {
      const text = question.toLowerCase();
      if (/battery|storage|bess/.test(text)) return 'VARTEC supports battery energy storage projects alongside solar PV, from engineering and procurement to construction support.';
      if (/maintenance|operation|o&m|clean|testing|monitor/.test(text)) return 'Our operations and maintenance support includes monitoring, diagnostics, electrical testing, panel cleaning and planned site maintenance.';
      if (/epc|engineering|design|procurement|construction|service/.test(text)) return 'We provide engineering, detailed design, procurement, construction, commissioning and ongoing maintenance for solar and energy-storage projects.';
      if (/project|experience|carport|floating|solar park|ev/.test(text)) return 'Our project experience covers solar parks, floating solar, solar carports, EV charging, battery storage and site security systems.';
      if (/quote|price|cost|contact|phone|email|speak/.test(text)) return 'For a project discussion or quotation, please ' + contactLink + '. We will connect you with the right specialist.';
      if (/hello|hi|hey/.test(text)) return 'Hello. I can help with VARTEC services, projects, operations and maintenance, battery storage, or contacting our team.';
      return 'I can provide general information about VARTEC services and projects. For a detailed answer, please ' + contactLink + '.';
    };
    const addMessage = (content, type, allowLink = false) => {
      const message = document.createElement('p');
      message.className = 'chatbot-message ' + type;
      if (allowLink) message.innerHTML = content;
      else message.textContent = content;
      messages.appendChild(message);
      messages.scrollTop = messages.scrollHeight;
    };
    const answer = (question) => {
      const clean = question.trim();
      if (!clean) return;
      addMessage(clean, 'user');
      input.value = '';
      window.setTimeout(() => addMessage(replyFor(clean), 'bot', true), 180);
    };
    const setOpen = (open) => {
      chatbot.classList.toggle('open', open);
      panel.setAttribute('aria-hidden', String(!open));
      panel.inert = !open;
      launcher.setAttribute('aria-expanded', String(open));
      if (open) window.setTimeout(() => input.focus(), 50);
      else launcher.focus();
    };
    launcher.addEventListener('click', () => setOpen(!chatbot.classList.contains('open')));
    close.addEventListener('click', () => setOpen(false));
    form.addEventListener('submit', (event) => { event.preventDefault(); answer(input.value); });
    chatbot.querySelectorAll('[data-chat-question]').forEach((button) => button.addEventListener('click', () => answer(button.dataset.chatQuestion || '')));
    document.addEventListener('keydown', (event) => { if (event.key === 'Escape' && chatbot.classList.contains('open')) setOpen(false); });
  }
})();
