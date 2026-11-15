/* EMPI Shoes - JS de la parte publica. JS puro, sin librerias.
   Cubre: carrusel 3D, inclinacion de tarjetas, filtros (bottom sheet + fetch a la API existente),
   pagina de producto (galeria 3D por color, compartir) y el formulario de WhatsApp. */
(function () {
  'use strict';

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- toast ---------- */
  var toastTimer;
  function toast(msg) {
    var t = $('#toast');
    if (!t) return;
    $('span', t).textContent = msg;
    t.classList.add('is-show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { t.classList.remove('is-show'); }, 2600);
  }

  /* ---------- coverflow 3D ---------- */
  function Coverflow(root, opts) {
    opts = opts || {};
    var track = $('.cf-track', root);
    var items = [];
    var n = 0, active = 0;
    var dragging = false, startX = 0, dx = 0, suppress = false;
    var timer = null, userPaused = false, hover = false, visible = true;
    var dotsBox = opts.dots || null;
    var self = {};

    function gapPx() {
      var g = parseFloat(getComputedStyle(root).getPropertyValue('--cf-gap'));
      return g > 0 ? g : 120;
    }

    function layout() {
      var frac = dragging ? dx / gapPx() : 0;
      items.forEach(function (it, i) {
        var o = i - active;
        if (n > 2) o = ((o + n / 2) % n + n) % n - n / 2;
        var oe = o + frac;
        var a = Math.min(Math.abs(oe), 3);
        it.style.setProperty('--o', oe.toFixed(3));
        it.style.setProperty('--a', a.toFixed(3));
        it.style.zIndex = String(Math.round(100 - a * 10));
        it.classList.toggle('is-far', Math.abs(o) > 2);
        it.classList.toggle('is-active', i === active);
        if (it.tagName === 'A') it.tabIndex = i === active ? 0 : -1;
      });
    }

    function renderDots() {
      if (!dotsBox) return;
      dotsBox.innerHTML = '';
      items.forEach(function (_, i) {
        var b = document.createElement('button');
        b.type = 'button';
        b.className = 'cf-dot';
        b.setAttribute('aria-label', 'Ir al elemento ' + (i + 1) + ' de ' + n);
        b.addEventListener('click', function () { go(i, true); });
        dotsBox.appendChild(b);
      });
      markDots();
    }
    function markDots() {
      if (!dotsBox) return;
      $$('.cf-dot', dotsBox).forEach(function (b, i) { b.setAttribute('aria-current', i === active ? 'true' : 'false'); });
    }

    function go(i, user) {
      if (!n) return;
      active = ((i % n) + n) % n;
      layout();
      markDots();
      if (opts.onChange) opts.onChange(active, items[active]);
      if (user) restart();
    }
    function next(user) { go(active + 1, user); }
    function prev(user) { go(active - 1, user); }

    function stop() { clearInterval(timer); timer = null; }
    function start() {
      stop();
      if (!opts.auto || reduce || userPaused || hover || dragging || !visible || document.hidden || n < 2) return;
      timer = setInterval(function () { next(false); }, opts.interval || 4500);
    }
    function restart() { stop(); start(); }

    function onDown(e) {
      if (e.button !== undefined && e.button !== 0) return;
      dragging = true; dx = 0; startX = e.clientX; suppress = false;
      stop();
      window.addEventListener('pointermove', onMove);
      window.addEventListener('pointerup', onUp);
      window.addEventListener('pointercancel', onUp);
    }
    function onMove(e) {
      if (!dragging) return;
      dx = e.clientX - startX;
      if (Math.abs(dx) > 6) { suppress = true; root.classList.add('is-dragging'); }
      layout();
    }
    function onUp() {
      if (!dragging) return;
      var moved = dx;
      dragging = false; dx = 0;
      root.classList.remove('is-dragging');
      window.removeEventListener('pointermove', onMove);
      window.removeEventListener('pointerup', onUp);
      window.removeEventListener('pointercancel', onUp);
      if (Math.abs(moved) > Math.max(36, gapPx() * 0.22)) {
        go(moved < 0 ? active + 1 : active - 1, false);
      } else {
        layout();
      }
      setTimeout(function () { suppress = false; }, 30);
      start();
    }

    function bindItems() {
      items = $$('.cf-item', track);
      n = items.length;
      items.forEach(function (it, i) {
        it.addEventListener('click', function (e) {
          if (suppress) { e.preventDefault(); e.stopPropagation(); return; }
          if (i !== active) { e.preventDefault(); go(i, true); }
        });
      });
    }

    root.addEventListener('pointerdown', onDown);
    root.addEventListener('dragstart', function (e) { e.preventDefault(); });
    root.addEventListener('mouseenter', function () { hover = true; stop(); });
    root.addEventListener('mouseleave', function () { hover = false; start(); });
    root.addEventListener('focusin', stop);
    root.addEventListener('focusout', start);
    root.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { e.preventDefault(); next(true); }
      else if (e.key === 'ArrowLeft') { e.preventDefault(); prev(true); }
    });
    var pb = $('.cf-prev', root), nb = $('.cf-next', root);
    if (pb) pb.addEventListener('click', function () { prev(true); });
    if (nb) nb.addEventListener('click', function () { next(true); });
    document.addEventListener('visibilitychange', start);
    window.addEventListener('resize', layout);
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (en) { visible = en[0].isIntersecting; start(); }).observe(root);
    }

    self.go = go;
    self.refresh = function () { bindItems(); active = 0; renderDots(); layout(); if (opts.onChange) opts.onChange(0, items[0]); start(); };
    self.setPaused = function (p) { userPaused = p; if (p) stop(); else start(); };
    bindItems(); renderDots(); layout(); start();
    return self;
  }

  /* ---------- hero (carrusel de los catalogos) ---------- */
  var heroRoot = $('#hero-cf');
  if (heroRoot) {
    var pad2 = function (v) { return (v < 10 ? '0' : '') + v; };
    var hero = Coverflow(heroRoot, {
      auto: true, interval: 4500, dots: $('#hero-dots'),
      onChange: function (i, el) {
        if (!el) return;
        $('#hi-brand').textContent = el.dataset.brand || '';
        $('#hi-name').textContent = el.dataset.name || '';
        $('#hi-price').textContent = el.dataset.price || '';
        var old = $('#hi-old');
        old.textContent = el.dataset.old || '';
        old.hidden = !el.dataset.old;
        $('#hi-link').setAttribute('href', el.getAttribute('href'));
        $('#hero-num').textContent = pad2(i + 1);
      }
    });
    hero.go(0, false);
    var pauseBtn = $('.cf-pause');
    if (pauseBtn) {
      if (reduce) { pauseBtn.setAttribute('aria-pressed', 'true'); pauseBtn.setAttribute('aria-label', 'Reanudar carrusel'); }
      pauseBtn.addEventListener('click', function () {
        var p = pauseBtn.getAttribute('aria-pressed') !== 'true';
        pauseBtn.setAttribute('aria-pressed', String(p));
        pauseBtn.setAttribute('aria-label', p ? 'Reanudar carrusel' : 'Pausar carrusel');
        hero.setPaused(p);
      });
    }
  }

  /* ---------- tarjetas: inclinacion 3D ---------- */
  function bindTilt(card) {
    if (reduce) return;
    function tilt(e) {
      var r = card.getBoundingClientRect();
      var px = (e.clientX - r.left) / r.width - 0.5;
      var py = (e.clientY - r.top) / r.height - 0.5;
      card.style.setProperty('--ry', (px * 12).toFixed(2) + 'deg');
      card.style.setProperty('--rx', (-py * 12).toFixed(2) + 'deg');
      card.classList.add('is-tilting');
    }
    function reset() {
      card.classList.remove('is-tilting');
      card.style.setProperty('--ry', '0deg');
      card.style.setProperty('--rx', '0deg');
    }
    card.addEventListener('pointerdown', tilt);
    card.addEventListener('pointermove', function (e) { if (e.pointerType === 'mouse' || e.buttons) tilt(e); });
    card.addEventListener('pointerleave', reset);
    card.addEventListener('pointerup', function () { setTimeout(reset, 140); });
    card.addEventListener('pointercancel', reset);
  }

  /* ---------- catalogo: filtros + bottom sheet ---------- */
  var grid = $('#grid');
  if (grid) {
    $$('.card', grid).forEach(bindTilt);

    var filtroUrl = grid.dataset.filtroUrl;
    var detalleBase = grid.dataset.detalleUrl || '';
    var logo = grid.dataset.logo || '';
    var empty = $('#empty');
    var loading = $('#loading-indicator');
    var form = $('#filters');
    var wrap = $('#filters-wrap'), backdrop = $('.sheet-backdrop'), openBtn = $('.filters-open');
    var lastFocus = null;
    var peticion = 0;

    /* ----- utilidades de formato (mismo resultado que el template de Django) ----- */
    var esc = function (s) {
      return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
        return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#x27;' }[c];
      });
    };
    var pad = function (v) { return (v < 10 ? '0' : '') + v; };
    var money = function (v) {
      var n = Number(v);
      return Math.round(n * 100) % 100 === 0 ? String(Math.round(n)) : n.toFixed(2);
    };
    /* redondeo al par mas cercano, igual que round() de Python que usa {% widthratio %} */
    var redondear = function (x) {
      var f = Math.floor(x), d = x - f;
      if (d > 0.5) return f + 1;
      if (d < 0.5) return f;
      return f % 2 === 0 ? f : f + 1;
    };
    var hexValido = function (h) { return /^#[0-9a-fA-F]{3,8}$/.test(h) ? h : '#ffffff'; };
    var chipStock = function (s) {
      if (s === 0) return '<span class="chip chip-ok">Disponible</span>';
      if (s === 1) return '<span class="chip chip-warn">Pocas unidades</span>';
      if (s === 2) return '<span class="chip chip-out">Agotado</span>';
      if (s === 3) return '<span class="chip chip-soon">Próximamente</span>';
      return '';
    };

    /* ----- tarjeta: misma estructura que catalogo_publico_base.html ----- */
    var tarjetaHTML = function (p, idx) {
      var precio = Number(p.precio) || 0;
      var desc = p.precio_descuento ? Number(p.precio_descuento) : null;
      var nombre = esc(p.marca) + ' ' + esc(p.nombre);
      var href = detalleBase.replace(/\/0\/$/, '/' + p.id + '/');
      var badge = '';
      if (desc) {
        var razon = precio > 0 ? redondear(desc / precio * 100) : 0;
        badge = '<span class="badge">' + (razon - 100) + '%</span>';
      }
      var precioHTML = desc
        ? '<strong>$' + money(desc) + '</strong><s aria-label="Precio anterior">$' + money(precio) + '</s>'
        : '<strong>$' + money(precio) + '</strong>';
      var colores = p.colores || [];
      var dots = colores.slice(0, 4).map(function (c) {
        return '<span class="dot" style="--c: ' + hexValido(c.codigo_hex) + '" role="img" aria-label="Color ' + esc(c.nombre) + '"></span>';
      }).join('');
      if (colores.length > 4) dots += '<span class="dots-more">+' + (colores.length - 4) + '</span>';
      return '<article class="card' + (p.stock === 2 ? ' is-out' : '') + '">' +
        '<a class="card-link" href="' + href + '" draggable="false">' +
        '<span class="card-idx" aria-hidden="true">' + pad(idx + 1) + '</span>' +
        '<span class="card-media"><span class="disc"><img src="' + esc(p.imagen_url || logo) + '" alt="' + nombre + '" loading="lazy" draggable="false"></span>' + badge + '</span>' +
        '<span class="card-body">' +
        '<span class="brand-tag">' + esc(p.marca) + '</span>' +
        '<h3 class="card-title">' + esc(p.nombre) + '</h3>' +
        '<span class="price">' + precioHTML + '</span>' +
        '<span class="dots" role="group" aria-label="Colores disponibles">' + dots + '</span>' +
        chipStock(p.stock) +
        '</span></a></article>';
    };

    var actualizarContador = function (n) {
      var c = $('.count-n');
      if (c) c.textContent = pad(n);
      var nf = $$('input[name="marca"]:checked', form).length + ($('input[name="precio"]:checked', form) ? 1 : 0);
      var badge = $('#filters-n');
      if (badge) { badge.hidden = !nf; badge.textContent = nf; }
    };

    var renderizarProductos = function (productos) {
      grid.innerHTML = productos.map(tarjetaHTML).join('');
      $$('.card', grid).forEach(bindTilt);
      empty.hidden = productos.length > 0;
      actualizarContador(productos.length);
    };

    var getCookie = function (name) {
      var v = null;
      if (document.cookie && document.cookie !== '') {
        document.cookie.split(';').forEach(function (c) {
          c = c.trim();
          if (c.substring(0, name.length + 1) === (name + '=')) v = decodeURIComponent(c.substring(name.length + 1));
        });
      }
      return v;
    };

    var aplicarFiltros = function () {
      var mi = ++peticion;
      loading.hidden = false;
      grid.setAttribute('aria-busy', 'true');
      var precio = $('input[name="precio"]:checked', form);
      var filtros = {
        marcas: $$('input[name="marca"]:checked', form).map(function (i) { return i.value; }),
        precio: precio ? precio.value : '',
        colores: $$('input[name="color"]:checked', form).map(function (i) { return i.value; })
      };
      var token = getCookie('csrftoken');
      if (!token) { var t = $('input[name="csrfmiddlewaretoken"]', form); token = t ? t.value : ''; }
      fetch(filtroUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': token },
        body: JSON.stringify(filtros)
      })
        .then(function (r) {
          if (!r.ok) throw new Error('Error HTTP: ' + r.status);
          return r.json();
        })
        .then(function (data) {
          if (mi !== peticion) return;
          if (data.productos) renderizarProductos(data.productos);
          else if (data.error) toast('Error al filtrar productos: ' + data.error);
        })
        .catch(function (err) {
          if (mi !== peticion) return;
          console.error('Error al filtrar:', err);
          toast('Error de conexión. Intenta nuevamente.');
        })
        .then(function () {
          if (mi !== peticion) return;
          loading.hidden = true;
          grid.removeAttribute('aria-busy');
        });
    };

    $$('input', form).forEach(function (i) {
      if (i.type === 'checkbox' || i.type === 'radio') i.addEventListener('change', aplicarFiltros);
    });
    form.addEventListener('submit', function (e) { e.preventDefault(); });
    var limpiar = $('#limpiar-filtros');
    if (limpiar) limpiar.addEventListener('click', function () {
      $$('input[type="checkbox"], input[type="radio"]', form).forEach(function (i) { i.checked = false; });
      aplicarFiltros();
    });

    /* ----- bottom sheet de filtros (movil) ----- */
    var openSheet = function () {
      lastFocus = document.activeElement;
      backdrop.hidden = false;
      requestAnimationFrame(function () { backdrop.classList.add('is-open'); });
      wrap.classList.add('is-open');
      document.body.classList.add('sheet-open');
      openBtn.setAttribute('aria-expanded', 'true');
      var f = $('.filters-close', wrap);
      if (f) f.focus();
    };
    var closeSheet = function () {
      wrap.classList.remove('is-open');
      backdrop.classList.remove('is-open');
      document.body.classList.remove('sheet-open');
      openBtn.setAttribute('aria-expanded', 'false');
      setTimeout(function () { backdrop.hidden = true; }, 320);
      if (lastFocus && lastFocus.focus) lastFocus.focus();
    };
    openBtn.addEventListener('click', openSheet);
    backdrop.addEventListener('click', closeSheet);
    $('.filters-close').addEventListener('click', closeSheet);
    $('.filters-apply').addEventListener('click', function () {
      closeSheet();
      var t = $('#catalogo');
      if (t) t.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth' });
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && wrap.classList.contains('is-open')) closeSheet();
      if (e.key === 'Tab' && wrap.classList.contains('is-open')) {
        var f = $$('button, input', wrap).filter(function (x) { return !x.disabled && x.offsetParent !== null; });
        if (!f.length) return;
        var first = f[0], last = f[f.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    });
  }

  /* ---------- pagina de producto ---------- */
  var prod = $('#producto');
  if (prod) {
    var stage = $('#stage');
    var galRoot = $('#gal-cf');
    var galTrack = $('#gal-track');

    /* fotos que dibujo el servidor: {src, alt, color} */
    var GAL = $$('.cf-item', galTrack).map(function (it) {
      var im = $('img', it);
      return { s: im.getAttribute('src'), a: im.getAttribute('alt') || '', c: it.dataset.color || '' };
    });
    var gal = Coverflow(galRoot, { dots: $('#gal-dots') });

    var buildGallery = function (colorId) {
      var list = GAL.filter(function (g) { return colorId && g.c === String(colorId); });
      if (!list.length) list = GAL.slice();
      var items = list.map(function (g) { return { s: g.s, a: g.a, m: false }; });
      var k = 0;
      while (items.length < 3 && list.length) { items.push({ s: list[k % list.length].s, a: list[k % list.length].a, m: true }); k++; }
      galTrack.innerHTML = '';
      items.forEach(function (it) {
        var d = document.createElement('div');
        d.className = 'cf-item';
        var disc = document.createElement('span');
        disc.className = 'disc';
        var im = document.createElement('img');
        im.src = it.s; im.alt = it.a; im.draggable = false;
        if (it.m) im.className = 'is-mirror';
        disc.appendChild(im); d.appendChild(disc); galTrack.appendChild(d);
      });
      gal.refresh();
    };

    var colorInicial = $('input[name="color"]:checked');
    buildGallery(colorInicial ? colorInicial.dataset.id : '');

    /* color: tinte del escenario + transicion 3D de la galeria */
    var colores = $('#p-colors');
    if (colores) colores.addEventListener('change', function (e) {
      if (e.target.name !== 'color') return;
      var nombre = $('#p-color-name');
      if (nombre) nombre.textContent = e.target.value;
      if (e.target.dataset.hex) stage.style.setProperty('--c', e.target.dataset.hex);
      buildGallery(e.target.dataset.id);
      galTrack.classList.remove('spin');
      void galTrack.offsetWidth;
      galTrack.classList.add('spin');
    });
    galTrack.addEventListener('animationend', function () { galTrack.classList.remove('spin'); });

    /* compartir: navigator.share o copiar el enlace */
    var copyText = function (txt) {
      if (navigator.clipboard && navigator.clipboard.writeText) return navigator.clipboard.writeText(txt);
      return new Promise(function (res, rej) {
        var t = document.createElement('textarea');
        t.value = txt; t.setAttribute('readonly', ''); t.className = 'sr-only';
        document.body.appendChild(t); t.select();
        try { document.execCommand('copy') ? res() : rej(); } catch (err) { rej(err); }
        document.body.removeChild(t);
      });
    };
    var share = function () {
      var url = prod.dataset.canonical;
      var data = { title: prod.dataset.title, text: prod.dataset.text, url: url };
      if (navigator.share) {
        navigator.share(data).catch(function () { /* cancelado por el usuario */ });
      } else {
        copyText(url).then(function () { toast('Enlace copiado'); }, function () { toast('No se pudo copiar: ' + url); });
      }
    };
    $$('.js-share').forEach(function (b) { b.addEventListener('click', share); });
  }

  /* ---------- formulario de WhatsApp (contacto y pedido de producto) ----------
     Comportamiento portado de menu.js sin cambios. */
  var contactForm = document.getElementById('contactForm');
  if (contactForm) {
    contactForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var formEl = this;
      var formData = new FormData(formEl);

      fetch(formEl.action, {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
        .then(function (response) { return response.json(); })
        .then(function (data) {
          if (data.success) {
            alert('¡Gracias por tu mensaje! Te responderemos pronto.');
            window.location.href = data.url_wasap;
          }
        })
        .catch(function (error) {
          console.error('Error:', error);
          formEl.submit(); // Fallback
        });
    });
  }
})();
