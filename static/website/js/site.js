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

  const autoplayVideo = document.querySelector('[data-autoplay-video]');
  if (autoplayVideo) {
    autoplayVideo.muted = true;
    autoplayVideo.playsInline = true;
    const startVideo = () => autoplayVideo.play().catch(() => {});
    if (autoplayVideo.readyState >= 2) startVideo();
    else autoplayVideo.addEventListener('canplay', startVideo, { once: true });
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
      launcher.setAttribute('aria-expanded', String(open));
      if (open) window.setTimeout(() => input.focus(), 50);
    };
    launcher.addEventListener('click', () => setOpen(!chatbot.classList.contains('open')));
    close.addEventListener('click', () => setOpen(false));
    form.addEventListener('submit', (event) => { event.preventDefault(); answer(input.value); });
    chatbot.querySelectorAll('[data-chat-question]').forEach((button) => button.addEventListener('click', () => answer(button.dataset.chatQuestion || '')));
    document.addEventListener('keydown', (event) => { if (event.key === 'Escape' && chatbot.classList.contains('open')) setOpen(false); });
  }
})();
