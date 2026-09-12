/* Marigui — nav, filters, lightbox, cursor pill */
(function () {
  // Mobile nav
  var nav = document.getElementById('nav'), tg = document.querySelector('.navtoggle');
  if (tg) tg.addEventListener('click', function () {
    var open = nav.classList.toggle('open');
    tg.setAttribute('aria-expanded', open ? 'true' : 'false');
  });

  // "See work" pill following the cursor over home tiles
  var pill = document.getElementById('cpill');
  if (pill) {
    addEventListener('mousemove', function (e) { pill.style.left = e.clientX + 'px'; pill.style.top = e.clientY + 'px'; });
    document.querySelectorAll('.tile').forEach(function (t) {
      t.addEventListener('mouseenter', function () { pill.classList.add('show'); });
      t.addEventListener('mouseleave', function () { pill.classList.remove('show'); });
    });
  }

  // Masonry walls: each shot goes to the shortest column, in its original order
  var walls = Array.prototype.slice.call(document.querySelectorAll('.wall'));
  var shots = Array.prototype.slice.call(document.querySelectorAll('.wall .shot'));
  shots.forEach(function (s) { s.setAttribute('tabindex', '0'); s.setAttribute('role', 'button'); });
  function frac(s) { return s.classList.contains('s-66') ? .66 : s.classList.contains('s-82') ? .82 : 1; }
  function layoutWall(wall) {
    var n = parseInt(getComputedStyle(wall).getPropertyValue('--cols')) || 3;
    if (wall._cols === n) return;
    wall._cols = n;
    var items = Array.prototype.slice.call(wall.querySelectorAll('.shot'));
    var cols = [], heights = [];
    for (var i = 0; i < n; i++) { var c = document.createElement('div'); c.className = 'col'; cols.push(c); heights.push(0); }
    items.forEach(function (s) {
      var im = s.querySelector('img'), r = (im.getAttribute('height') / im.getAttribute('width')) || 1;
      var f = window.innerWidth <= 520 ? 1 : frac(s);
      var k = heights.indexOf(Math.min.apply(null, heights));
      cols[k].appendChild(s); heights[k] += r * f + .06;
    });
    wall.querySelectorAll('.col').forEach(function (c) { c.remove(); });
    cols.forEach(function (c) { wall.appendChild(c); });
    wall.classList.add('ready');
  }
  function layout() { walls.forEach(layoutWall); }
  layout();
  var rt; addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(layout, 120); });

  // Lightbox
  var lb = document.getElementById('lb'); if (!lb || !shots.length) return;
  var img = document.getElementById('lbimg'), cap = document.getElementById('lbcap'), num = document.getElementById('lbnum');
  var cur = -1;
  function visible() { return shots; }
  function preload(list, i) { var s = list[i]; if (s) { var p = new Image(); p.src = s.dataset.hd; } }
  function show(i) {
    var list = visible(); if (!list.length) return;
    cur = (i + list.length) % list.length;
    var s = list[cur];
    img.src = s.dataset.hd; img.alt = s.querySelector('img').alt;
    cap.textContent = s.dataset.cap || '';
    num.textContent = (cur + 1) + ' / ' + list.length;
    preload(list, (cur + 1) % list.length); preload(list, (cur - 1 + list.length) % list.length);
  }
  function open(s) {
    lb.classList.add('open'); lb.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    show(visible().indexOf(s));
  }
  function close() {
    lb.classList.remove('open'); lb.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = ''; img.removeAttribute('src');
    if (cur >= 0 && visible()[cur]) visible()[cur].focus();
  }
  shots.forEach(function (s) {
    s.addEventListener('click', function () { open(s); });
    s.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(s); } });
  });
  lb.querySelector('.lb-x').addEventListener('click', close);
  lb.querySelector('.lb-prev').addEventListener('click', function (e) { e.stopPropagation(); show(cur - 1); });
  lb.querySelector('.lb-next').addEventListener('click', function (e) { e.stopPropagation(); show(cur + 1); });
  lb.addEventListener('click', function (e) { if (e.target === lb || e.target.tagName === 'FIGURE') close(); });
  img.addEventListener('click', function (e) { e.stopPropagation(); show(cur + 1); });
  document.addEventListener('keydown', function (e) {
    if (!lb.classList.contains('open')) return;
    if (e.key === 'Escape') close();
    else if (e.key === 'ArrowRight') show(cur + 1);
    else if (e.key === 'ArrowLeft') show(cur - 1);
  });
  // Touch swipe
  var x0 = null;
  lb.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
  lb.addEventListener('touchend', function (e) {
    if (x0 === null) return; var dx = e.changedTouches[0].clientX - x0; x0 = null;
    if (Math.abs(dx) > 40) show(dx < 0 ? cur + 1 : cur - 1);
  });
})();
