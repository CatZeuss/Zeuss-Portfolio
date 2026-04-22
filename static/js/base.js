/* ═══════════════════════════════════════════════
   ZEUSS PORTFOLIO — base.js
   ═══════════════════════════════════════════════ */

/* ── Star Canvas ──────────────────────────────────────────────── */
(function () {
    const canvas = document.getElementById('starsCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    let W, H, stars = [], dpr = window.devicePixelRatio || 1;

    function resize() {
        W = canvas.width  = window.innerWidth  * dpr;
        H = canvas.height = window.innerHeight * dpr;
        canvas.style.width  = window.innerWidth  + 'px';
        canvas.style.height = window.innerHeight + 'px';
        ctx.scale(dpr, dpr);
        init();
    }

    function rand(min, max) { return Math.random() * (max - min) + min; }

    function init() {
        stars = [];
        const count = Math.floor((window.innerWidth * window.innerHeight) / 5000);
        for (let i = 0; i < count; i++) {
            stars.push({
                x:       rand(0, window.innerWidth),
                y:       rand(0, window.innerHeight),
                size:    rand(1, 3.5),
                opacity: rand(0.1, 0.9),
                speed:   rand(0.002, 0.008),        // twinkle speed
                phase:   rand(0, Math.PI * 2),       // twinkle phase offset
                drift:   rand(-0.04, 0.04),          // slow x drift
                color:   pickColor(),
            });
        }
    }

    function pickColor() {
        const palette = [
            '#ffffff',
            '#c4b5fd',  // violet tint
            '#a78bfa',  // purple
            '#f9a8d4',  // pink tint
        ];
        return palette[Math.floor(Math.random() * palette.length)];
    }

    /* Draw a 4-pointed star (diamond cross) */
    function drawStar(cx, cy, size, alpha, color) {
        ctx.save();
        ctx.globalAlpha = alpha;
        ctx.fillStyle = color;

        // Outer spikes
        const outer = size;
        const inner = size * 0.22;

        ctx.beginPath();
        // top
        ctx.moveTo(cx, cy - outer);
        ctx.lineTo(cx + inner, cy - inner);
        // right
        ctx.lineTo(cx + outer, cy);
        ctx.lineTo(cx + inner, cy + inner);
        // bottom
        ctx.lineTo(cx, cy + outer);
        ctx.lineTo(cx - inner, cy + inner);
        // left
        ctx.lineTo(cx - outer, cy);
        ctx.lineTo(cx - inner, cy - inner);
        ctx.closePath();
        ctx.fill();

        // Soft glow
        if (size > 2) {
            ctx.globalAlpha = alpha * 0.18;
            const glow = ctx.createRadialGradient(cx, cy, 0, cx, cy, size * 3);
            glow.addColorStop(0, color);
            glow.addColorStop(1, 'transparent');
            ctx.fillStyle = glow;
            ctx.beginPath();
            ctx.arc(cx, cy, size * 3, 0, Math.PI * 2);
            ctx.fill();
        }
        ctx.restore();
    }

    let raf, t = 0;

    function draw() {
        ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
        t += 0.016;

        stars.forEach(s => {
            // Sinusoidal twinkle
            const alpha = s.opacity * (0.45 + 0.55 * Math.abs(Math.sin(t * s.speed * 60 + s.phase)));
            // Slow drift
            s.x += s.drift;
            if (s.x < -10) s.x = window.innerWidth + 10;
            if (s.x > window.innerWidth + 10) s.x = -10;

            drawStar(s.x, s.y, s.size, alpha, s.color);
        });

        raf = requestAnimationFrame(draw);
    }

    window.addEventListener('resize', () => {
        cancelAnimationFrame(raf);
        resize();
        raf = requestAnimationFrame(draw);
    });

    resize();
    draw();
})();


/* ── Page Loader ─────────────────────────────────────────────── */
(function () {
    const loader = document.getElementById('pageLoader');
    if (!loader) return;

    function hide() {
        loader.classList.add('hidden');
    }

    if (document.readyState === 'complete') {
        setTimeout(hide, 400);
    } else {
        window.addEventListener('load', () => setTimeout(hide, 400));
    }

    // Show loader on navigation
    window.addEventListener('beforeunload', () => {
        loader.classList.remove('hidden');
    });
})();


/* ── Navbar: scroll state + progress bar ────────────────────── */
(function () {
    const nav      = document.getElementById('mainNav');
    const progress = document.getElementById('navProgress');
    if (!nav) return;

    function onScroll() {
        // Scrolled class
        if (window.scrollY > 20) {
            nav.classList.add('scrolled');
        } else {
            nav.classList.remove('scrolled');
        }

        // Read progress
        if (progress) {
            const docH   = document.documentElement.scrollHeight - window.innerHeight;
            const pct    = docH > 0 ? (window.scrollY / docH) * 100 : 0;
            progress.style.width = pct + '%';
        }
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
})();


/* ── Mobile Sidebar ──────────────────────────────────────────── */
(function () {
    const sidebar  = document.getElementById('mobileSidebar');
    const overlay  = document.getElementById('sidebarOverlay');
    const openBtn  = document.getElementById('openSidebar');
    const closeBtn = document.getElementById('closeSidebar');
    if (!sidebar) return;

    function open() {
        sidebar.classList.remove('translate-x-full');
        overlay.classList.remove('hidden');
        requestAnimationFrame(() => overlay.classList.add('opacity-100'));
        document.body.style.overflow = 'hidden';
    }

    function close() {
        sidebar.classList.add('translate-x-full');
        overlay.classList.remove('opacity-100');
        setTimeout(() => overlay.classList.add('hidden'), 300);
        document.body.style.overflow = '';
    }

    openBtn?.addEventListener('click', open);
    closeBtn?.addEventListener('click', close);
    overlay?.addEventListener('click', close);

    // Close on nav link click
    sidebar.querySelectorAll('a').forEach(a => a.addEventListener('click', close));
})();


/* ── Flash toast auto-dismiss ────────────────────────────────── */
(function () {
    document.querySelectorAll('.flash-toast').forEach(toast => {
        setTimeout(() => {
            toast.classList.add('animate__fadeOutRight');
            setTimeout(() => toast.remove(), 500);
        }, 5000);
    });
})();


/* ── Scroll animations (IntersectionObserver) ────────────────── */
(function () {
    const els = document.querySelectorAll('.animate-on-scroll');
    if (!els.length) return;

    const obs = new IntersectionObserver((entries) => {
        entries.forEach((entry, i) => {
            if (entry.isIntersecting) {
                // Stagger by DOM index
                const delay = (parseInt(entry.target.dataset.delay) || 0);
                entry.target.style.transitionDelay = delay + 'ms';
                entry.target.classList.add('visible');
                obs.unobserve(entry.target);
            }
        });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

    els.forEach(el => obs.observe(el));
})();