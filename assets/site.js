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

  // Masonry wall: shots go to the shortest column, in their original order
  var wall = document.getElementById('wall');
  var shots = Array.prototype.slice.call(document.querySelectorAll('#wall .shot'));
  var bar = document.getElementById('bar');
  shots.forEach(function (s) { s.setAttribute('tabindex', '0'); s.setAttribute('role', 'button'); });
  var lastCols = 0;
  function layout(force) {
    if (!wall) return;
    var n = parseInt(getComputedStyle(wall).getPropertyValue('--cols')) || 3;
    if (!force && n === lastCols) return;
    lastCols = n;
    var cols = [], heights = [];
    for (var i = 0; i < n; i++) { var c = document.createElement('div'); c.className = 'col'; cols.push(c); heights.push(0); }
    shots.forEach(function (s) {
      if (s.classList.contains('hide')) return;
      var im = s.querySelector('img'), r = (im.getAttribute('height') / im.getAttribute('width')) || 1;
      var k = heights.indexOf(Math.min.apply(null, heights));
      cols[k].appendChild(s); heights[k] += r;
    });
    wall.querySelectorAll('.col').forEach(function (c) { c.remove(); });
    cols.forEach(function (c) { wall.appendChild(c); });
    wall.classList.add('ready');
  }
  layout(true);
  var rt; addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(function () { layout(false); }, 120); });

  // Filters
  function applyFilter(f) {
    shots.forEach(function (s) { s.classList.toggle('hide', !(f === 'all' || s.dataset.f === f)); });
    layout(true);
    if (history.replaceState) history.replaceState(null, '', f === 'all' ? location.pathname : '#' + f);
  }
  if (bar) {
    bar.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return;
      bar.querySelectorAll('button').forEach(function (x) { x.classList.remove('on'); });
      b.classList.add('on');
      applyFilter(b.dataset.f);
    });
    var h = location.hash.slice(1), init = h && bar.querySelector('button[data-f="' + h + '"]');
    if (init) init.click();
  }

  // Lightbox
  var lb = document.getElementById('lb'); if (!lb || !shots.length) return;
  var img = document.getElementById('lbimg'), cap = document.getElementById('lbcap'), num = document.getElementById('lbnum');
  var cur = -1;
  function visible() { return shots.filter(function (s) { return !s.classList.contains('hide'); }); }
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
