document.addEventListener('DOMContentLoaded', () => {
    // NAVBAR TOGGLE
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', () => {
            navMenu.classList.toggle('open');
            navToggle.classList.toggle('active');
            navToggle.setAttribute('aria-expanded', navMenu.classList.contains('open'));
        });
        navMenu.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                navMenu.classList.remove('open');
                navToggle.classList.remove('active');
            });
        });
    }

    // SCROLL EFFECT
    const navbar = document.getElementById('navbar');
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 60) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
        const btn = document.getElementById('backToTop');
        if (btn) btn.classList.toggle('visible', window.pageYOffset > 400);
    });

    // SMOOTH SCROLL
    document.querySelectorAll('a[href^="#"]').forEach(a => {
        a.addEventListener('click', e => {
            const t = document.querySelector(a.getAttribute('href'));
            if (t) { e.preventDefault(); t.scrollIntoView({behavior:'smooth', block:'start'}); }
        });
    });

    // ATIVO NA NAV
    const sections = document.querySelectorAll('section[id]');
    window.addEventListener('scroll', () => {
        sections.forEach(s => {
            const id = s.getAttribute('id');
            const link = document.querySelector(`.nav-link[href="#${id}"]`);
            if (link) {
                const top = s.offsetTop, bottom = top + s.offsetHeight;
                link.classList.toggle('active', window.pageYOffset + 150 >= top && window.pageYOffset + 150 < bottom);
            }
        });
    });

    // BACK TO TOP
    const btt = document.createElement('button');
    btt.id = 'backToTop'; btt.className = 'back-to-top';
    btt.setAttribute('aria-label', 'Voltar ao topo');
    btt.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="18 15 12 9 6 15"/></svg>';
    btt.addEventListener('click', () => window.scrollTo({top:0, behavior:'smooth'}));
    document.body.appendChild(btt);

    // SCROLL REVEAL
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('visible'); observer.unobserve(e.target); } });
    }, {threshold: 0.1, rootMargin: '0px 0px -50px 0px'});
    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

    // FORM CONTATO
    const form = document.getElementById('contactForm');
    if (form) {
        form.addEventListener('submit', e => {
            e.preventDefault();
            const nome = document.getElementById('nome').value.trim();
            const email = document.getElementById('email').value.trim();
            const msg = document.getElementById('mensagem').value.trim();
            if (!nome || !email || !msg) { alert('Preencha todos os campos.'); return; }
            if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { alert('E-mail inválido.'); return; }
            const btn = form.querySelector('button[type="submit"]');
            btn.innerHTML = '<span class="spinner"></span>Enviando...'; btn.disabled = true;
            setTimeout(() => { alert('Mensagem enviada!'); form.reset(); btn.innerHTML = '<svg viewBox="0 0 24 24" class="send-icon" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>Enviar Mensagem'; btn.disabled = false; }, 1200);
        });
    }
});
