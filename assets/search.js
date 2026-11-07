(function () {
  var root = document.getElementById("directory-search");
  if (!root) return;
  var indexUrl = root.getAttribute("data-index");
  var base = root.getAttribute("data-root") || "";
  var preset = root.getAttribute("data-state") || "";
  var form = root.querySelector("form");
  var out = document.getElementById("search-results");
  var more = document.getElementById("search-more");
  var count = document.getElementById("search-count");
  var shown = 0;
  var matches = [];
  var pageSize = 24;

  function text(id) {
    var el = document.getElementById(id);
    return el ? el.value.trim().toLowerCase() : "";
  }

  function apply() {
    var q = text("q");
    var state = text("state") || preset.toLowerCase();
    var own = text("ownership");
    var signal = text("signal");
    matches = (window.ER_INDEX || []).filter(function (row) {
      if (state && row.st !== state) return false;
      if (own && row.o !== own && !(own === "pe_owned" && row.o === "platform_owned")) return false;
      if (signal && row.g !== signal) return false;
      if (!q) return true;
      return (row.n + " " + row.c + " " + row.sv + " " + row.rb).toLowerCase().indexOf(q) !== -1;
    });
    shown = 0;
    out.innerHTML = "";
    renderMore();
  }

  function badge(label, cls) {
    return '<span class="badge ' + cls + '">' + label + "</span>";
  }

  function locationsBadge(row) {
    if (!row.lc || row.lc < 2) return "";
    return badge(row.lc + " listed locations", "locations");
  }

  function branchLinks(row) {
    if (!row.lc || row.lc < 2 || !row.br || !row.br.length) return "";
    var links = row.br.map(function (peer) {
      return '<a href="' + base + peer.p + '">' + escapeHtml(peer.c) + "</a>";
    }).join(" · ");
    return '<p class="branch-links"><a href="' + base + row.p + '#listed-locations">' +
      row.lc + " listed locations</a> in this directory · " + links +
      '<span class="source-note">Matched to one cited location page. Not an ownership label. Not a national total.</span></p>';
  }

  function ownBadge(code) {
    if (code === "platform_owned" || code === "pe_owned") return badge("PE or platform-owned", "platform");
    if (code === "franchise") return badge("Franchise", "franchise");
    if (code === "independent") return badge("Independent", "");
    if (code === "utility") return badge("Utility-owned", "platform");
    if (code === "other_corporate") return badge("Other corporate owner", "platform");
    return badge("Ownership: unverified", "quiet");
  }

  function renderMore() {
    var slice = matches.slice(shown, shown + pageSize);
    slice.forEach(function (row) {
      var article = document.createElement("article");
      article.className = "card";
      var signal = row.g === "mechanical_license_only"
        ? badge("Mechanical license only", "license")
        : badge("Heat pump program roster", "");
      article.innerHTML =
        "<h3><a href=\"" + base + row.p + "\">" + escapeHtml(row.n) + "</a></h3>" +
        '<p class="meta">' + escapeHtml(row.c) + ", " + escapeHtml(row.sn) + "</p>" +
        '<p class="badges">' + ownBadge(row.o) + signal + locationsBadge(row) + "</p>" +
        branchLinks(row);
      out.appendChild(article);
    });
    shown += slice.length;
    count.textContent = matches.length + (matches.length === 1 ? " listing" : " listings");
    more.hidden = shown >= matches.length;
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, function (ch) {
      return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[ch];
    });
  }

  var params = new URLSearchParams(window.location.search);
  var initialQuery = params.get("q");
  if (initialQuery) {
    var queryInput = document.getElementById("q");
    if (queryInput) queryInput.value = initialQuery;
  }

  fetch(indexUrl)
    .then(function (res) { return res.json(); })
    .then(function (data) {
      window.ER_INDEX = data;
      if (preset) {
        var stateInput = document.getElementById("state");
        if (stateInput) stateInput.value = preset;
      }
      apply();
    })
    .catch(function () {
      count.textContent = "Search is unavailable. Use the state and city links below.";
    });

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    apply();
  });
  ["q", "state", "ownership", "signal"].forEach(function (id) {
    var el = document.getElementById(id);
    if (el) el.addEventListener("input", apply);
    if (el) el.addEventListener("change", apply);
  });
  more.addEventListener("click", renderMore);
})();
