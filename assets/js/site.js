/* Theme toggle. The initial theme is set inline in <head> to avoid a flash. */
(function () {
  var root = document.documentElement;
  var btn = document.getElementById('theme-toggle');
  if (!btn) return;

  function current() {
    return root.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
  }

  btn.addEventListener('click', function () {
    var next = current() === 'dark' ? 'light' : 'dark';
    if (next === 'dark') {
      root.setAttribute('data-theme', 'dark');
    } else {
      root.removeAttribute('data-theme');
    }
    try { localStorage.setItem('theme', next); } catch (e) {}
    btn.setAttribute('aria-label', next === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
  });
})();

/* Nav dropdowns. CSS already opens them on hover and on keyboard focus; this
   adds a deliberate open/close for touch, where hover does not exist. */
(function () {
  var groups = document.querySelectorAll('[data-nav-group]');
  if (!groups.length) return;

  function closeAll(except) {
    Array.prototype.forEach.call(groups, function (g) {
      if (g !== except) {
        g.removeAttribute('data-open');
        var b = g.querySelector('[data-nav-toggle]');
        if (b) b.setAttribute('aria-expanded', 'false');
      }
    });
  }

  Array.prototype.forEach.call(groups, function (group) {
    var btn = group.querySelector('[data-nav-toggle]');
    if (!btn) return;
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      var open = group.getAttribute('data-open') === 'true';
      closeAll(group);
      if (open) {
        group.removeAttribute('data-open');
        btn.setAttribute('aria-expanded', 'false');
      } else {
        group.setAttribute('data-open', 'true');
        btn.setAttribute('aria-expanded', 'true');
      }
    });
  });

  document.addEventListener('click', function (e) {
    if (!e.target.closest('[data-nav-group]')) closeAll(null);
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeAll(null);
  });
})();

/* World map: name the country under the pointer, and link the flag chips to
   their shape on the map. Everything still works without this — the SVG paths
   carry <title> elements and the flags have CSS tooltips. */
(function () {
  var root = document.querySelector('[data-countries]');
  if (!root) return;

  var caption = root.querySelector('[data-caption]');
  var fallback = caption ? caption.innerHTML : '';
  var svg = root.querySelector('svg.worldmap');
  if (!svg || !caption) return;

  var byCode = {};
  Array.prototype.forEach.call(root.querySelectorAll('.flag'), function (flag) {
    byCode[flag.getAttribute('data-code')] = flag;
  });

  function describe(code) {
    var flag = byCode[code];
    return flag ? flag.getAttribute('data-name') : null;
  }

  function show(code) {
    var text = describe(code);
    if (!text) return;
    var path = svg.querySelector('#c-' + code);
    if (path) path.classList.add('is-active');
    var parts = text.split(' — ');
    caption.innerHTML = '<strong>' + parts[0] + '</strong>' +
      (parts[1] ? ' — ' + parts[1] : '');
  }

  function clear() {
    var active = svg.querySelector('.is-active');
    if (active) active.classList.remove('is-active');
    caption.innerHTML = fallback;
  }

  Object.keys(byCode).forEach(function (code) {
    var flag = byCode[code];
    ['mouseenter', 'focus'].forEach(function (ev) {
      flag.addEventListener(ev, function () { show(code); });
    });
    ['mouseleave', 'blur'].forEach(function (ev) {
      flag.addEventListener(ev, clear);
    });
  });

  svg.addEventListener('mouseover', function (e) {
    var id = e.target && e.target.id;
    if (id && id.indexOf('c-') === 0 && describe(id.slice(2))) show(id.slice(2));
  });
  svg.addEventListener('mouseleave', clear);
})();


/* Projects page: linking to /projects/#<slug> should open that entry's
   collapsible details (if it has any) and scroll it into view. */
(function () {
  function openTarget() {
    var hash = window.location.hash;
    if (!hash || hash.length < 2) return;
    var el = document.getElementById(hash.slice(1));
    if (!el) return;
    var details = el.querySelector('details');
    if (details) details.open = true;
    el.scrollIntoView();
  }
  window.addEventListener('hashchange', openTarget);
  openTarget();
})();
