/* ============================================
   ROUTHEONSKUPS — ARCHITECTURAL BACKGROUND
   Grid Lines • Travel Routes • Coordinate System
   Minimal • Geometric • Technical
   ============================================ */

(function() {
  'use strict';

  // --- Architectural Grid + Travel Routes ---
  function initParticles() {
    var canvas = document.getElementById('ks-particles-canvas');
    if (!canvas) return;
    var ctx = canvas.getContext('2d');
    var w, h, mouse = { x: -1000, y: -1000 };
    var dpr = window.devicePixelRatio || 1;

    // Travel route nodes (abstract destinations)
    var nodes = [];
    var connections = [];
    var gridLines = [];

    function resize() {
      w = window.innerWidth;
      h = window.innerHeight;
      canvas.width = w * dpr;
      canvas.height = h * dpr;
      canvas.style.width = w + 'px';
      canvas.style.height = h + 'px';
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      generateNodes();
    }

    function generateNodes() {
      nodes = [];
      connections = [];
      gridLines = [];

      // Create travel route nodes
      var nodeCount = Math.min(25, Math.floor((w * h) / 60000));
      for (var i = 0; i < nodeCount; i++) {
        nodes.push({
          x: Math.random() * w,
          y: Math.random() * h,
          vx: (Math.random() - 0.5) * 0.15,
          vy: (Math.random() - 0.5) * 0.15,
          radius: 1.5 + Math.random() * 1.5,
          opacity: 0.03 + Math.random() * 0.04,
          pulse: Math.random() * Math.PI * 2,
          pulseSpeed: 0.002 + Math.random() * 0.003
        });
      }

      // Create connections between nearby nodes
      var connectionDist = Math.min(250, w * 0.25);
      for (var i = 0; i < nodes.length; i++) {
        for (var j = i + 1; j < nodes.length; j++) {
          var dx = nodes[i].x - nodes[j].x;
          var dy = nodes[i].y - nodes[j].y;
          var dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < connectionDist) {
            connections.push({ a: i, b: j, dist: dist, maxDist: connectionDist });
          }
        }
      }

      // Create horizontal grid lines (subtle)
      var gridSpacing = 120;
      for (var y = gridSpacing; y < h; y += gridSpacing) {
        gridLines.push({ type: 'h', y: y, opacity: 0.012 + Math.random() * 0.008 });
      }
      // Create vertical grid lines (subtle)
      for (var x = gridSpacing; x < w; x += gridSpacing) {
        gridLines.push({ type: 'v', x: x, opacity: 0.012 + Math.random() * 0.008 });
      }
    }

    resize();
    window.addEventListener('resize', resize);

    document.addEventListener('mousemove', function(e) {
      mouse.x = e.clientX;
      mouse.y = e.clientY;
    });

    // Floating particles (tiny dots)
    var particles = [];
    var pCount = Math.min(35, Math.floor(w / 30));
    for (var i = 0; i < pCount; i++) {
      particles.push({
        x: Math.random() * w,
        y: Math.random() * h,
        r: 0.5 + Math.random() * 1,
        dx: (Math.random() - 0.5) * 0.12,
        dy: (Math.random() - 0.5) * 0.12,
        opacity: 0.02 + Math.random() * 0.03,
        pulse: Math.random() * Math.PI * 2,
        pulseSpeed: 0.004 + Math.random() * 0.004,
        parallaxFactor: 0.3 + Math.random() * 0.8
      });
    }

    var frame = 0;
    function draw() {
      ctx.clearRect(0, 0, w, h);
      frame++;

      var mx = mouse.x - w / 2;
      var my = mouse.y - h / 2;

      // Draw architectural grid lines
      ctx.lineWidth = 0.5;
      for (var i = 0; i < gridLines.length; i++) {
        var gl = gridLines[i];
        // Subtle mouse proximity effect
        var mouseDist = gl.type === 'h'
          ? Math.abs(mouse.y - gl.y)
          : Math.abs(mouse.x - (gl.x || 0));
        var mouseInfluence = mouseDist < 200 ? (1 - mouseDist / 200) * 0.015 : 0;

        ctx.globalAlpha = gl.opacity + mouseInfluence;
        ctx.strokeStyle = '#888888';
        ctx.beginPath();
        if (gl.type === 'h') {
          ctx.moveTo(0, gl.y);
          ctx.lineTo(w, gl.y);
        } else {
          ctx.moveTo(gl.x, 0);
          ctx.lineTo(gl.x, h);
        }
        ctx.stroke();
      }
      ctx.globalAlpha = 1;

      // Draw travel route connections
      for (var i = 0; i < connections.length; i++) {
        var c = connections[i];
        var a = nodes[c.a];
        var b = nodes[c.b];
        var alpha = (1 - c.dist / c.maxDist) * 0.025;

        // Animate connection opacity
        alpha *= 0.7 + Math.sin(frame * 0.005 + i * 0.5) * 0.3;

        ctx.globalAlpha = alpha;
        ctx.strokeStyle = '#FFFFFF';
        ctx.lineWidth = 0.5;
        ctx.beginPath();
        ctx.moveTo(a.x, a.y);
        ctx.lineTo(b.x, b.y);
        ctx.stroke();
      }
      ctx.globalAlpha = 1;

      // Update and draw nodes (travel destinations)
      for (var i = 0; i < nodes.length; i++) {
        var n = nodes[i];
        n.x += n.vx;
        n.y += n.vy;
        n.pulse += n.pulseSpeed;

        // Wrap
        if (n.x < -20) n.x = w + 20;
        if (n.x > w + 20) n.x = -20;
        if (n.y < -20) n.y = h + 20;
        if (n.y > h + 20) n.y = -20;

        var op = n.opacity * (0.6 + Math.sin(n.pulse) * 0.4);

        // Node glow
        var glowR = n.radius * 3;
        var gradient = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, glowR);
        gradient.addColorStop(0, 'rgba(26,26,26,' + (op * 0.5) + ')');
        gradient.addColorStop(1, 'rgba(26,26,26,0)');
        ctx.beginPath();
        ctx.arc(n.x, n.y, glowR, 0, Math.PI * 2);
        ctx.fillStyle = gradient;
        ctx.fill();

        // Node core
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.radius, 0, Math.PI * 2);
        ctx.fillStyle = '#FFFFFF';
        ctx.fill();
      }

      // Draw floating particles with parallax
      for (var i = 0; i < particles.length; i++) {
        var p = particles[i];
        var pmx = mx * 0.0005 * p.parallaxFactor;
        var pmy = my * 0.0005 * p.parallaxFactor;

        p.x += p.dx + pmx * (i % 2 === 0 ? 0.2 : -0.2);
        p.y += p.dy + pmy * (i % 2 === 0 ? 0.2 : -0.2);
        p.pulse += p.pulseSpeed;

        if (p.x < -10) p.x = w + 10;
        if (p.x > w + 10) p.x = -10;
        if (p.y < -10) p.y = h + 10;
        if (p.y > h + 10) p.y = -10;

        var op = p.opacity * (0.5 + Math.sin(p.pulse) * 0.5);
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = '#FFFFFF';
        ctx.fill();
      }

      // Draw subtle animated route paths (curved travel lines)
      if (frame % 2 === 0) {
        ctx.globalAlpha = 0.008;
        ctx.strokeStyle = '#FFFFFF';
        ctx.lineWidth = 0.5;
        ctx.setLineDash([4, 8]);

        // Draw a few curved paths
        for (var i = 0; i < Math.min(3, nodes.length - 1); i++) {
          var n1 = nodes[i * 2] || nodes[0];
          var n2 = nodes[i * 2 + 1] || nodes[1];
          var cpx = (n1.x + n2.x) / 2 + (Math.sin(frame * 0.003 + i) * 40);
          var cpy = (n1.y + n2.y) / 2 + (Math.cos(frame * 0.003 + i) * 40);

          ctx.beginPath();
          ctx.moveTo(n1.x, n1.y);
          ctx.quadraticCurveTo(cpx, cpy, n2.x, n2.y);
          ctx.stroke();
        }
        ctx.setLineDash([]);
        ctx.globalAlpha = 1;
      }

      requestAnimationFrame(draw);
    }
    draw();
  }

  // --- Floating Geometric Shapes (solid charcoal) ---
  function initFloatingShapes() {
    var container = document.querySelector('.ks-cinema-bg');
    if (!container) return;

    var shapes = [];
    var count = Math.min(4, Math.floor(window.innerWidth / 400));

    for (var i = 0; i < count; i++) {
      var shape = document.createElement('div');
      var size = 150 + Math.random() * 250;
      var opacity = 0.003 + Math.random() * 0.008;
      shape.style.cssText = [
        'position: absolute',
        'border-radius: 50%',
        'background: #0A0A0A',
        'border: 1px solid #0A0A0A',
        'width: ' + size + 'px',
        'height: ' + size + 'px',
        'left: ' + (Math.random() * 100) + '%',
        'top: ' + (Math.random() * 100) + '%',
        'transform: translate(-50%, -50%)',
        'filter: blur(' + (80 + Math.random() * 60) + 'px)',
        'pointer-events: none',
        'will-change: transform'
      ].join(';');

      container.appendChild(shape);

      shapes.push({
        el: shape,
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        speedX: (Math.random() - 0.5) * 0.06,
        speedY: (Math.random() - 0.5) * 0.06,
        phase: Math.random() * Math.PI * 2,
        phaseSpeed: 0.001 + Math.random() * 0.002
      });
    }

    function animate() {
      for (var i = 0; i < shapes.length; i++) {
        var s = shapes[i];
        s.phase += s.phaseSpeed;
        s.x += s.speedX + Math.sin(s.phase) * 0.04;
        s.y += s.speedY + Math.cos(s.phase) * 0.03;

        if (s.x < -300) s.x = window.innerWidth + 150;
        if (s.x > window.innerWidth + 300) s.x = -150;
        if (s.y < -300) s.y = window.innerHeight + 150;
        if (s.y > window.innerHeight + 300) s.y = -150;

        s.el.style.transform = 'translate(-50%, -50%) translate(' + s.x + 'px, ' + s.y + 'px)';
      }
      requestAnimationFrame(animate);
    }
    animate();
  }

  // --- Ambient Light Orbs (solid charcoal) ---
  function initAmbientLights() {
    if (document.querySelector('.ks-ambient-light')) return;

    var lights = [
      { cls: 'ks-ambient-light ks-ambient-light-1' },
      { cls: 'ks-ambient-light ks-ambient-light-2' },
      { cls: 'ks-ambient-light ks-ambient-light-3' }
    ];

    lights.forEach(function(l) {
      var el = document.createElement('div');
      el.className = l.cls;
      el.style.background = '#0A0A0A';
      document.body.appendChild(el);
    });
  }

  // --- Mouse Parallax for Cards ---
  function initMouseParallax() {
    var cards = document.querySelectorAll('.ks-glass, .ks-metric, .ks-glass-panel');
    if (!cards.length) return;

    document.addEventListener('mousemove', function(e) {
      var x = e.clientX;
      var y = e.clientY;

      cards.forEach(function(card) {
        var rect = card.getBoundingClientRect();
        if (rect.top > window.innerHeight || rect.bottom < 0) return;

        card.style.setProperty('--mouse-x', ((x - rect.left) / rect.width * 100) + '%');
        card.style.setProperty('--mouse-y', ((y - rect.top) / rect.height * 100) + '%');
      });
    }, { passive: true });

    document.addEventListener('mouseleave', function() {
      cards.forEach(function(card) {
        card.style.setProperty('--mouse-x', '50%');
        card.style.setProperty('--mouse-y', '50%');
      });
    });
  }

  // --- Scroll Parallax ---
  function initScrollParallax() {
    var elements = document.querySelectorAll('[data-ks-parallax]');
    if (!elements.length) return;

    var ticking = false;
    window.addEventListener('scroll', function() {
      if (!ticking) {
        requestAnimationFrame(function() {
          var scrollY = window.pageYOffset;
          for (var i = 0; i < elements.length; i++) {
            var el = elements[i];
            var speed = parseFloat(el.getAttribute('data-ks-parallax')) || 0.1;
            var rect = el.getBoundingClientRect();
            var offset = (rect.top + scrollY - window.innerHeight / 2) * speed;
            el.style.transform = 'translateY(' + (-offset) + 'px)';
          }
          ticking = false;
        });
        ticking = true;
      }
    }, { passive: true });
  }

  // --- Reveal on Scroll ---
  function initRevealOnScroll() {
    var elements = document.querySelectorAll('.ks-reveal');
    if (!elements.length) return;

    var observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('ks-revealed');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

    elements.forEach(function(el) { observer.observe(el); });
  }

  // --- Staggered Reveal ---
  function initStaggeredReveal() {
    var groups = document.querySelectorAll('.ks-stagger-group');
    if (!groups.length) return;

    var observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          var items = entry.target.querySelectorAll('.ks-stagger-item');
          items.forEach(function(item, idx) {
            item.style.animationDelay = (idx * 0.08) + 's';
            item.classList.add('ks-animate-in');
          });
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

    groups.forEach(function(g) { observer.observe(g); });
  }

  // --- Navbar scroll effect ---
  function initNavbarScroll() {
    var nav = document.querySelector('.ks-glass-nav') || document.querySelector('.ks-nav');
    if (!nav) return;

    var ticking = false;
    function check() {
      if (!ticking) {
        requestAnimationFrame(function() {
          nav.classList.toggle('scrolled', window.scrollY > 20);
          ticking = false;
        });
        ticking = true;
      }
    }
    check();
    window.addEventListener('scroll', check, { passive: true });
  }

  // --- Smooth Anchor Scrolling ---
  function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
      anchor.addEventListener('click', function(e) {
        var target = document.querySelector(this.getAttribute('href'));
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    });
  }

  // --- Init all ---
  function init() {
    initParticles();
    initFloatingShapes();
    initAmbientLights();
    initMouseParallax();
    initScrollParallax();
    initRevealOnScroll();
    initStaggeredReveal();
    initNavbarScroll();
    initSmoothScroll();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
