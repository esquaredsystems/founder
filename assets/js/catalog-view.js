/* Renders a dedicated course/training page from the JSON Jekyll builds from
   _data/teaching.csv or _data/trainings.csv (courses/courses.json,
   trainings/trainings.json), matched against this page's ?slug= query
   parameter. One shared page per type, so a new row in the CSV gets a
   working, shareable, bookmarkable URL without adding a file for it. */
(function () {
  function qs(name) {
    var m = new RegExp('[?&]' + name + '=([^&]*)').exec(window.location.search);
    return m ? decodeURIComponent(m[1].replace(/\+/g, ' ')) : null;
  }

  function escapeHtml(s) {
    return String(s === null || s === undefined ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  var DOWNLOAD_ICON = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" focusable="false"><path d="M12 3v10.6l3.3-3.3 1.4 1.4L12 16.4l-4.7-4.7 1.4-1.4 3.3 3.3V3h2ZM4 19h16v2H4v-2Z"/></svg>';

  function renderMaterials(materials) {
    if (!materials || !materials.length) return '';
    var videos = [];
    var files = [];
    materials.forEach(function (m) {
      if (m.kind === 'video') { videos.push(m); } else { files.push(m); }
    });

    var html = '';
    videos.forEach(function (v) {
      html += '<div class="catalog-video">' +
        '<video controls preload="metadata" src="' + v.path + '"></video>' +
        '<p class="course__meta">' + escapeHtml(v.name) + '</p></div>';
    });
    if (files.length) {
      html += '<p class="course__materials-label">' + DOWNLOAD_ICON +
        ' Materials <span class="course__count">' + files.length + '</span></p>';
      html += '<ul class="course__files">';
      files.forEach(function (f) {
        html += '<li><a href="' + f.path + '" download>' + escapeHtml(f.name) +
          '<span class="course__ext">' + escapeHtml(f.ext) + '</span></a></li>';
      });
      html += '</ul>';
    }
    return html;
  }

  function showNotFound(mount, listUrl, listLabel) {
    mount.innerHTML = '<p>Couldn’t find that one. <a href="' + listUrl + '">Back to ' +
      escapeHtml(listLabel) + '</a>.</p>';
  }

  window.renderCatalogView = function (opts) {
    var mount = document.getElementById('catalog-view');
    if (!mount) return;
    var slug = qs('slug');
    if (!slug) { showNotFound(mount, opts.listUrl, opts.listLabel); return; }

    fetch(opts.jsonUrl)
      .then(function (res) { return res.json(); })
      .then(function (items) {
        var item = null;
        for (var i = 0; i < items.length; i++) {
          if (items[i].slug === slug) { item = items[i]; break; }
        }
        if (!item) { showNotFound(mount, opts.listUrl, opts.listLabel); return; }

        var title = item.title || item.course || '';
        document.title = title + ' · ' + opts.siteTitle;
        var h1 = document.querySelector('.page-head h1');
        if (h1) h1.textContent = title;

        var metaBits = [];
        if (item.date) metaBits.push(item.date);
        if (item.venue) metaBits.push(item.venue);
        if (item.term) metaBits.push(item.term);
        var metaHtml = metaBits.length ?
          '<p class="course__meta">' + escapeHtml(metaBits.join(' · ')) + '</p>' : '';

        var body = item.summary || item.topics || '';
        var bodyHtml = body ? '<div class="course__body">' + escapeHtml(body) + '</div>' : '';

        mount.innerHTML = metaHtml + bodyHtml + renderMaterials(item.materials);
      })
      .catch(function () { showNotFound(mount, opts.listUrl, opts.listLabel); });
  };
})();
