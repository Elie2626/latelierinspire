(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const mobile = () => innerWidth < 768;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  document.documentElement.classList.add('js');

  // Menu mobile
  const burger = $('#burger'), menu = $('#menu');
  burger?.addEventListener('click', () => {
    const open = menu.classList.toggle('open');
    burger.setAttribute('aria-expanded', open);
    burger.setAttribute('aria-label', open ? 'Fermer le menu' : 'Ouvrir le menu');
  });
  addEventListener('keydown', e => { if (e.key === 'Escape' && menu?.classList.contains('open')) burger.click(); });

  // Titres découpés mot par mot (masque + montée)
  $$('.split').forEach(el => {
    const label = el.textContent.trim();
    el.setAttribute('aria-label', label);
    el.innerHTML = label.split(/\s+/).map((w, i) =>
      `<span class="w" aria-hidden="true"><span style="--i:${i}">${w}</span></span>`).join(' ');
  });

  // Mots qui s'illuminent
  const wordBlocks = $$('[data-words]').map(el => {
    el.innerHTML = el.textContent.trim().split(/\s+/).map(w => `<span>${w}</span>`).join(' ');
    return { el, spans: [...el.children] };
  });

  // Apparitions
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
  }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
  $$('.reveal').forEach(el => {
    const sibs = [...el.parentElement.children].filter(c => c.classList.contains('reveal'));
    if (sibs.length > 1) el.style.transitionDelay = (sibs.indexOf(el) % 4) * 90 + 'ms';
    io.observe(el);
  });
  $$('.split, .clip, .timeline, .gal__item').forEach(el => io.observe(el));

  // Compteurs
  const counters = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      const el = e.target, end = +el.dataset.count, t0 = performance.now(), d = 1600;
      counters.unobserve(el);
      if (reduce) return;
      const step = t => {
        const p = clamp((t - t0) / d);
        el.textContent = Math.round(end * (1 - Math.pow(1 - p, 4))).toLocaleString('fr-FR');
        if (p < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    });
  }, { threshold: 0.6 });
  $$('[data-count]').forEach(el => counters.observe(el));

  // Galerie : lightbox
  const lb = $('#lightbox');
  if (lb) {
    const img = $('img', lb);
    $$('.gal__btn').forEach(b => b.addEventListener('click', () => {
      img.src = b.dataset.full; img.alt = $('img', b).alt; lb.showModal();
    }));
    $('.lightbox__close', lb).addEventListener('click', () => lb.close());
    lb.addEventListener('click', e => { if (e.target === lb) lb.close(); });
  }

  // Galerie : afficher toutes les créations
  const galToggle = $('#galToggle');
  galToggle?.addEventListener('click', () => {
    const all = $('#galAll'), open = all.hidden;
    all.hidden = !open;
    galToggle.setAttribute('aria-expanded', open);
    galToggle.textContent = open ? 'Masquer les créations' : galToggle.dataset.label;
    if (open) { $$('.gal__item', all).forEach(el => el.classList.add('in')); all.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
  });
  if (galToggle) galToggle.dataset.label = galToggle.textContent;

  // Histoire : vidéo YouTube chargée au clic seulement
  $('#vidPlay')?.addEventListener('click', e => {
    const f = document.createElement('iframe');
    f.src = 'https://www.youtube-nocookie.com/embed/H6FOJ6nBqi0?autoplay=1&rel=0';
    f.title = "L'histoire de L'Atelier Inspiré";
    f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
    f.allowFullscreen = true;
    e.currentTarget.replaceWith(f);
  });

  // Contact : validation au blur, envoi via la messagerie
  const form = $('#contactForm');
  if (form) {
    const rules = {
      'f-name': i => i.value.trim() !== '',
      'f-email': i => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(i.value.trim()),
      'f-ok': i => i.checked,
    };
    const check = id => {
      const i = $('#' + id), ok = rules[id](i);
      i.closest('.field').classList.toggle('has-error', !ok);
      i.setAttribute('aria-invalid', !ok);
      i.setAttribute('aria-describedby', 'e-' + id.slice(2));
      return ok;
    };
    Object.keys(rules).forEach(id => $('#' + id).addEventListener(id === 'f-ok' ? 'change' : 'blur', () => check(id)));
    form.addEventListener('submit', e => {
      e.preventDefault();
      const bad = Object.keys(rules).filter(id => !check(id));
      if (bad.length) { $('#' + bad[0]).focus(); return; }
      const d = new FormData(form);
      const body = `${d.get('message') || ''}\n\n— ${d.get('name')} (${d.get('email')})`;
      location.href = `mailto:laetitia@latelierinspire.fr?subject=${encodeURIComponent('Demande de contact — ' + d.get('name'))}&body=${encodeURIComponent(body)}`;
      $('.form__status', form).textContent = 'Votre messagerie s’ouvre avec le message prêt à envoyer. Merci !';
    });
  }

  // Boutique : retire le chargeur quand Ecwid est prêt
  if (window.Ecwid) Ecwid.OnAPILoaded?.add(() => $('.shop__loading')?.remove());
  else addEventListener('load', () => window.Ecwid?.OnAPILoaded?.add(() => $('.shop__loading')?.remove()));

  if (reduce) { const hv = $('#heroVideo'); if (hv) hv.src = innerWidth < 768 ? hv.dataset.srcMobile : hv.dataset.src; wordBlocks.forEach(b => b.spans.forEach(s => s.classList.add('on'))); return; }

  // ---------- Animations liées au scroll ----------
  const nav = $('#nav');
  const bar = $('.scrollbar span');
  const readbar = $('.readbar span');
  const prose = $('.prose');
  const hero = $('#hero'), heroMedia = $('#heroMedia'), heroVideo = $('#heroVideo');
  if (heroVideo) {
    heroVideo.addEventListener('loadedmetadata', () => onScroll());
    // Chargée en mémoire pour un défilement image par image fiable, quel que soit l'hébergeur
    // Vidéo verticale sur mobile, horizontale sinon
    const portrait = matchMedia('(max-width: 767px), (orientation: portrait) and (max-width: 1023px)').matches;
    if (portrait) heroVideo.poster = heroVideo.dataset.posterMobile;
    const url = portrait ? heroVideo.dataset.srcMobile : heroVideo.dataset.src;
    fetch(url).then(r => r.ok ? r.blob() : Promise.reject())
      .then(b => { heroVideo.src = URL.createObjectURL(b); })
      .catch(() => { heroVideo.src = url; });
  }
  const heroText = hero && $('.hero__text', hero), heroScroll = hero && $('.hero__scroll', hero);
  const products = $('#products'), track = $('#track'), prog = $('#progress');
  const parallax = $$('[data-parallax]');
  const lifts = $$('[data-lift]');
  const marquees = $$('[data-marquee]');
  const galCols = $$('.gal__col');
  const vid = $('#vid'), vidFrame = $('#vidFrame');
  const tline = $('.timeline__line span'), tl = $('.timeline');
  const cover = $('.article__cover img');
  const stack = $('#stack');
  const cards = stack ? $$('.stack__card', stack) : [];
  const stackNum = $('#stackNum');
  const floaties = $$('.floaty');

  const sizeProducts = () => {
    if (!products) return;
    if (mobile()) { products.style.removeProperty('--h'); return; }
    products.style.setProperty('--h', `${innerHeight + track.scrollWidth - innerWidth}px`);
  };

  // Lissage : la vidéo rattrape doucement la position du scroll
  let heroTarget = 0, heroCur = 0, heroRaf = 0;
  const smoothVideo = () => {
    heroCur += (heroTarget - heroCur) * 0.12;
    if (Math.abs(heroTarget - heroCur) < 0.01) heroCur = heroTarget;
    if (!heroVideo.seeking) heroVideo.currentTime = heroCur;
    heroRaf = heroCur === heroTarget ? 0 : requestAnimationFrame(smoothVideo);
  };
  let lastY = scrollY, ticking = false;
  const frame = () => {
    ticking = false;
    const y = scrollY, vh = innerHeight, docH = document.documentElement.scrollHeight - vh;

    nav.classList.toggle('is-scrolled', y > 10);
    nav.classList.toggle('is-hidden', y > lastY && y > vh && !menu.classList.contains('open'));
    lastY = y;
    bar?.style.setProperty('--p', clamp(y / docH).toFixed(4));

    if (hero) {
      const total = clamp((y - hero.offsetTop) / (hero.offsetHeight - vh));
      const hp = clamp(total / 0.15);
      // Après le zoom, la vidéo avance image par image avec le scroll
      if (heroVideo && heroVideo.duration) {
        heroTarget = clamp((total - 0.08) / 0.9) * (heroVideo.duration - 0.05);
        if (!heroRaf) heroRaf = requestAnimationFrame(smoothVideo);
      }
      const e = 1 - Math.pow(1 - hp, 3);
      heroMedia.style.setProperty('--s', (0.62 + 0.38 * e).toFixed(4));
      heroMedia.style.setProperty('--y', `${(34 * (1 - e)).toFixed(2)}%`);
      heroText.style.transform = `translateY(${-hp * 80}px) scale(${1 - hp * 0.08})`;
      heroText.style.opacity = clamp(1 - hp * 1.8);
      heroScroll.style.setProperty('--o', clamp(1 - hp * 6));
    }

    wordBlocks.forEach(({ el, spans }) => {
      const r = el.getBoundingClientRect();
      const n = Math.round(clamp((vh * 0.85 - r.top) / (r.height + vh * 0.35)) * spans.length);
      spans.forEach((w, i) => w.classList.toggle('on', i < n));
    });

    if (products && !mobile()) {
      const pr = products.getBoundingClientRect();
      const pp = clamp(-pr.top / (products.offsetHeight - vh));
      track.style.transform = `translate3d(${-pp * (track.scrollWidth - innerWidth)}px,0,0)`;
      prog.style.setProperty('--p', pp.toFixed(4));
    }

    const rel = el => { const b = el.getBoundingClientRect(); return (b.top + b.height / 2 - vh / 2) / vh; };
    parallax.forEach(el => { el.style.transform = `translate3d(0,${rel(el.parentElement) * el.dataset.parallax * -100}%,0)`; });
    lifts.forEach(el => { el.style.translate = `0 ${(rel(el) * +el.dataset.lift).toFixed(1)}px`; });

    // Bandeaux de texte qui glissent selon le scroll
    marquees.forEach((m, i) => {
      const r = m.getBoundingClientRect();
      if (r.bottom < 0 || r.top > vh) return;
      const half = m.scrollWidth / 2;
      const x = ((y * 0.35) % half);
      m.style.transform = `translate3d(${i % 2 ? x - half : -x}px,0,0)`;
    });

    // Galerie : colonnes à vitesses différentes
    if (galCols.length && !mobile()) {
      const g = galCols[0].parentElement.getBoundingClientRect();
      galCols.forEach(c => { c.style.transform = `translate3d(0,${(g.top - vh) * +c.dataset.speed}px,0)`; });
    }

    // Histoire : la vidéo s'élargit
    if (vid) {
      const p = clamp((vh - vid.getBoundingClientRect().top) / (vid.offsetHeight));
      const e = 1 - Math.pow(1 - clamp(p * 1.4), 3);
      vidFrame.style.setProperty('--s', (0.72 + 0.28 * e).toFixed(4));
      vidFrame.style.setProperty('--r', `${(1 - e) * 28 + 12}px`);
    }
    if (tline) {
      const r = tl.getBoundingClientRect();
      tline.style.setProperty('--p', clamp((vh * 0.7 - r.top) / r.height).toFixed(4));
    }

    // Galerie : la carte du dessus s'envole en tournant et révèle la suivante
    if (stack) {
      const n = cards.length;
      const p = clamp(-stack.getBoundingClientRect().top / (stack.offsetHeight - vh)) * (n - 1);
      cards.forEach((c, i) => {
        const t = clamp(p - i);               // 0 = en place, 1 = partie
        const e = t * t * (3 - 2 * t);
        const depth = Math.max(0, i - p);     // cartes en attente derrière
        const dir = i % 2 ? 1 : -1;
        if (t > 0) {
          c.style.transform = `translate3d(${dir * e * 120}vw, ${-e * 30}vh, 0) rotate(${dir * e * 35}deg)`;
          c.style.opacity = 1 - e * 0.6;
        } else {
          const s = 1 - Math.min(depth, 4) * 0.045;
          c.style.transform = `translate3d(0, ${Math.min(depth, 4) * 14}px, 0) scale(${s}) rotate(var(--tilt))`;
          c.style.opacity = depth > 4 ? 0 : 1;
        }
        c.style.visibility = t >= 1 ? 'hidden' : 'visible';
      });
      const sp = p / (n - 1) - 0.5;
      floaties.forEach((f, i) => {
        f.style.transform = `translate3d(0, ${(sp * +f.dataset.speed).toFixed(1)}px, 0) rotate(calc(var(--rot) + ${(sp * (i % 2 ? 24 : -24)).toFixed(1)}deg))`;
      });
      stackNum.textContent = String(Math.min(n, Math.round(p) + 1)).padStart(2, '0');
    }

    // Article : barre de lecture + zoom de la couverture
    if (readbar && prose) {
      const r = prose.getBoundingClientRect();
      readbar.style.setProperty('--p', clamp(-r.top / (r.height - vh * 0.6)).toFixed(4));
    }
    if (cover) cover.style.transform = `scale(${1 + clamp(y / vh) * 0.12}) translateY(${clamp(y / vh) * 6}%)`;
  };
  const onScroll = () => { if (!ticking) { ticking = true; requestAnimationFrame(frame); } };

  addEventListener('scroll', onScroll, { passive: true });
  let rt;
  addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(() => { sizeProducts(); frame(); }, 120); });
  addEventListener('load', () => { sizeProducts(); frame(); });
  sizeProducts(); frame();
})();
