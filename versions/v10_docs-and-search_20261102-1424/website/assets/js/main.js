/* T&L Biotechnology — interaction layer */
(function () {
  "use strict";

  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  /* ---------------- sticky header ---------------- */
  var header = $("#header");
  function onScroll() {
    if (!header) return;
    header.classList.toggle("is-stuck", window.scrollY > 8);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---------------- mega menu ---------------- */
  $$("[data-mega]").forEach(function (item) {
    var closeTimer;
    function open() {
      clearTimeout(closeTimer);
      $$("[data-mega]").forEach(function (o) { if (o !== item) o.classList.remove("is-open"); });
      item.classList.add("is-open");
      positionMega(item);
      var a = item.querySelector(".nav__link");
      if (a) a.setAttribute("aria-expanded", "true");
    }
    function close() {
      item.classList.remove("is-open");
      var a = item.querySelector(".nav__link");
      if (a) a.setAttribute("aria-expanded", "false");
    }
    item.addEventListener("mouseenter", open);
    item.addEventListener("mouseleave", function () {
      closeTimer = setTimeout(close, 140);
    });
    item.addEventListener("focusin", open);
    item.addEventListener("focusout", function (e) {
      if (!item.contains(e.relatedTarget)) close();
    });
  });
  function positionMega(item) {
    if (window.innerWidth <= 860) return;
    var menu = item.querySelector(".mega");
    if (!menu) return;
    var r = item.getBoundingClientRect();
    var w = menu.offsetWidth || 860;
    var left = r.left + r.width / 2 - w / 2;
    left = Math.max(16, Math.min(left, window.innerWidth - w - 16));
    menu.style.left = left - r.left + "px";
  }
  window.addEventListener("resize", function () {
    $$(".nav__item.is-open").forEach(positionMega);
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      $$("[data-mega]").forEach(function (o) { o.classList.remove("is-open"); });
      closeSearch();
      setNav(false);
    }
  });

  /* ---------------- mobile nav ---------------- */
  var toggle = $("#nav-toggle");
  var mobileMenu = $("#mobile-menu");
  function setNav(open) {
    document.body.classList.toggle("nav-open", open);
    if (mobileMenu) mobileMenu.classList.toggle("is-open", open);
    if (toggle) toggle.setAttribute("aria-expanded", open ? "true" : "false");
  }
  if (toggle) {
    toggle.addEventListener("click", function () {
      setNav(!document.body.classList.contains("nav-open"));
    });
  }
  if (mobileMenu) {
    mobileMenu.addEventListener("click", function (e) {
      if (e.target.closest("a")) setNav(false);
    });
  }

  /* ---------------- search ---------------- */
  var pop = $("#search-pop");
  var input = $("#search-input");
  var results = $("#search-results");

  function openSearch() {
    if (!pop) return;
    pop.classList.add("is-open");
    if (input && !input.value) renderResults("");
    setTimeout(function () { input && input.focus(); }, 60);
  }
  function closeSearch() {
    if (pop) pop.classList.remove("is-open");
  }
  var openBtn = $("#search-open");
  if (openBtn) openBtn.addEventListener("click", openSearch);
  var mmSearch = $("#mm-search");
  if (mmSearch) {
    mmSearch.addEventListener("click", function () {
      var toggle = $("#nav-toggle");
      if (toggle && document.body.classList.contains("nav-open")) toggle.click();
      openSearch();
    });
  }
  if (pop) pop.addEventListener("click", function (e) { if (e.target === pop) closeSearch(); });
  document.addEventListener("keydown", function (e) {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      openSearch();
    }
    if (e.key === "Escape") closeSearch();
  });

  var DATA = window.TL || { products: [], cats: {}, apps: {} };

  var POPULAR = ["CD3", "CD28", "IL-7", "NK kit", "DMF", "CAR-T"];

  function renderDefault() {
    if (!results) return;
    var chips = POPULAR.map(function (t) {
      return '<button type="button" class="search-pop__chip" data-q="' + t + '">' + t + "</button>";
    }).join("");
    var cats = Object.keys(DATA.cats || {}).map(function (id) {
      return '<a class="search-pop__cat" href="products.html?cat=' + id + '">' +
        DATA.cats[id] + "<span>" + DATA.products.filter(function (p) {
          return p.cat === id;
        }).length + "</span></a>";
    }).join("");
    results.innerHTML =
      '<div class="search-pop__group">Popular searches</div>' +
      '<div class="search-pop__chips">' + chips + "</div>" +
      '<div class="search-pop__group">Browse by family</div>' +
      '<div class="search-pop__cats">' + cats + "</div>";
  }

  function renderResults(q) {
    if (!results) return;
    q = (q || "").trim().toLowerCase();
    if (!q) { renderDefault(); return; }
    var hits = DATA.products.filter(function (p) {
      return (p.name + " " + p.blurb + " " + (DATA.cats[p.cat] || "") + " " +
        Object.keys(p.specs || {}).map(function (k) { return p.specs[k]; }).join(" ")
      ).toLowerCase().indexOf(q) > -1;
    });
    if (!hits.length) {
      results.innerHTML = '<div class="search-pop__empty">No product matches <b>' + q +
        "</b>. Try <b>CD3</b>, <b>IL-15</b> or <b>NK</b>, or " +
        '<a href="contact.html#quote">ask a scientist</a>.</div>';
      return;
    }
    var shown = hits.slice(0, 6);
    results.innerHTML =
      '<div class="search-pop__group">' + hits.length + " product" +
      (hits.length === 1 ? "" : "s") + "</div>" +
      shown.map(function (p) {
        return '<a class="search-pop__result" href="product.html?p=' + p.slug + '">' +
          '<img src="assets/img/products/' + p.slug + '-tile.webp" alt="">' +
          "<span><b>" + p.name + "</b><i>" + (DATA.cats[p.cat] || "") +
          (p.price ? " · from $" + p.price : "") + "</i></span></a>";
      }).join("") +
      '<a class="search-pop__all" href="products.html?q=' + encodeURIComponent(q) +
      '">See all ' + hits.length + " in the catalogue</a>";
  }

  if (input) {
    input.addEventListener("input", function () { renderResults(input.value); });
    input.addEventListener("keydown", function (e) {
      if (e.key === "Enter") {
        var first = results && results.querySelector(".search-pop__result");
        if (first) window.location.href = first.getAttribute("href");
      }
    });
  }
  if (results) {
    results.addEventListener("click", function (e) {
      var chip = e.target.closest(".search-pop__chip");
      if (!chip) return;
      input.value = chip.getAttribute("data-q");
      renderResults(input.value);
      input.focus();
    });
  }

  /* ---------------- reveal on scroll ---------------- */
  var reveals = $$(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          en.target.classList.add("is-in");
          io.unobserve(en.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    reveals.forEach(function (el, i) {
      el.style.transitionDelay = Math.min(i % 6, 5) * 60 + "ms";
      io.observe(el);
    });

    var flow = $("#flow");
    if (flow) {
      var io2 = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) { flow.classList.add("is-in"); io2.disconnect(); }
        });
      }, { threshold: 0.25 });
      io2.observe(flow);
    }
  } else {
    reveals.forEach(function (el) { el.classList.add("is-in"); });
  }

  /* ---------------- counters ---------------- */
  var counters = $$("[data-count]");
  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduceMotion) counters = [];
  if (counters.length && "IntersectionObserver" in window) {
    var io3 = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var el = en.target;
        var target = parseFloat(el.getAttribute("data-count"));
        var small = el.querySelector("small");
        var start = performance.now();
        var dur = 1300;
        function tick(now) {
          var t = Math.min(1, (now - start) / dur);
          var eased = 1 - Math.pow(1 - t, 3);
          var val = Math.round(target * eased);
          el.firstChild.nodeValue = val.toLocaleString("en-US");
          if (t < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
        io3.unobserve(el);
      });
    }, { threshold: 0.4 });
    counters.forEach(function (c) { io3.observe(c); });
  }

  /* ---------------- application tabs ---------------- */
  var appTabs = $$(".apps__tab");
  appTabs.forEach(function (tab) {
    tab.addEventListener("click", function () {
      var id = tab.getAttribute("data-tab");
      appTabs.forEach(function (t) { t.classList.toggle("is-active", t === tab); });
      $$("[data-panel]").forEach(function (p) {
        p.style.display = p.getAttribute("data-panel") === id ? "" : "none";
      });
    });
  });

  /* ---------------- faq ---------------- */
  $$(".faq__q").forEach(function (q) {
    q.addEventListener("click", function () {
      var item = q.parentElement;
      var open = item.classList.contains("is-open");
      $$(".faq__item").forEach(function (i) {
        i.classList.remove("is-open");
        var a = i.querySelector(".faq__a");
        if (a) a.style.maxHeight = null;
      });
      if (!open) {
        item.classList.add("is-open");
        var a = item.querySelector(".faq__a");
        if (a) a.style.maxHeight = a.scrollHeight + "px";
      }
    });
  });

  /* ---------------- product catalogue ---------------- */
  var grid = $("#grid");
  if (grid) {
    var cards = $$(".gcard", grid);
    var boxes = $$('input[data-filter]');
    var q = $("#cat-search");
    var sort = $("#sort");
    var countEl = $("#count-visible");
    var emptyEl = $("#empty");

    function apply() {
      var cats = boxes.filter(function (b) { return b.getAttribute("data-filter") === "cat" && b.checked; })
        .map(function (b) { return b.value; });
      var apps = boxes.filter(function (b) { return b.getAttribute("data-filter") === "app" && b.checked; })
        .map(function (b) { return b.value; });
      var term = (q && q.value || "").trim().toLowerCase();
      var shown = 0;

      cards.forEach(function (c) {
        var okCat = !cats.length || cats.indexOf(c.getAttribute("data-cat")) > -1;
        var cApps = (c.getAttribute("data-apps") || "").split(",").filter(Boolean);
        var okApp = !apps.length || apps.some(function (a) { return cApps.indexOf(a) > -1; });
        var okTerm = !term || (c.getAttribute("data-name") || "").toLowerCase().indexOf(term) > -1;
        var ok = okCat && okApp && okTerm;
        c.style.display = ok ? "" : "none";
        if (ok) shown++;
      });

      if (countEl) countEl.textContent = shown;
      if (emptyEl) emptyEl.style.display = shown ? "none" : "";
      sortNow();
    }

    function sortNow() {
      if (!sort) return;
      var mode = sort.value;
      if (mode === "default") return;
      var list = cards.slice().sort(function (a, b) {
        if (mode === "name") return a.getAttribute("data-name").localeCompare(b.getAttribute("data-name"));
        var pa = parseFloat(a.getAttribute("data-price")) || 1e9;
        var pb = parseFloat(b.getAttribute("data-price")) || 1e9;
        return mode === "price-asc" ? pa - pb : pb - pa;
      });
      list.forEach(function (c) { grid.appendChild(c); });
    }

    boxes.forEach(function (b) { b.addEventListener("change", apply); });
    if (q) q.addEventListener("input", apply);
    if (sort) sort.addEventListener("change", sortNow);

    var ftoggle = $("#filter-toggle");
    var fcount = $("#filter-count");
    function syncFilterCount() {
      if (!fcount) return;
      var n = boxes.filter(function (b) { return b.checked; }).length;
      fcount.textContent = n;
      fcount.style.display = n ? "" : "none";
    }
    if (ftoggle) {
      ftoggle.addEventListener("click", function () {
        var f = document.querySelector(".filters");
        var open = f.classList.toggle("is-open");
        ftoggle.setAttribute("aria-expanded", open ? "true" : "false");
      });
    }
    boxes.forEach(function (b) { b.addEventListener("change", syncFilterCount); });
    syncFilterCount();

    var reset = $("#reset");
    if (reset) reset.addEventListener("click", function () {
      boxes.forEach(function (b) { b.checked = false; });
      if (q) q.value = "";
      if (sort) sort.value = "default";
      apply();
    });

    // deep link: products.html?cat=beads or ?q=CD3
    var params = new URLSearchParams(location.search);
    var term = params.get("q");
    if (term && q) { q.value = term; apply(); }
    var cat = params.get("cat");
    if (cat) {
      boxes.forEach(function (b) {
        if (b.getAttribute("data-filter") === "cat" && b.value === cat) b.checked = true;
      });
      apply();
    }
  }

  /* ---------------- product detail ---------------- */
  var pdpTitle = $("#pdp-title");
  if (pdpTitle && DATA.products.length) {
    var params = new URLSearchParams(location.search);
    var slug = params.get("p") || "actsep-cd3-cd28";
    var p = DATA.products.filter(function (x) { return x.slug === slug; })[0] || DATA.products[0];

    document.title = p.name + " — T&L Biotechnology";
    $("#pdp-title").textContent = p.name;
    $("#pdp-blurb").textContent = p.blurb;
    $("#pdp-crumb").textContent = p.name;
    $("#pdp-img").src = "assets/img/products/" + p.slug + "-tile.webp";
    $("#pdp-img").alt = p.name;
    $("#pdp-catpill").textContent = DATA.cats[p.cat] || "";
    $("#pdp-cat").textContent = DATA.cats[p.cat] || "Catalogue";
    $("#pdp-cat").href = "products.html?cat=" + p.cat;
    $("#pdp-desc").textContent = p.desc;
    $("#pdp-price").innerHTML = p.price
      ? "$" + p.price.toLocaleString("en-US") + " <span>USD</span>"
      : "Price on request";

    $("#pdp-highlights").innerHTML = p.highlights.map(function (h) {
      return "<li>" + h + "</li>";
    }).join("");

    $("#pdp-specs").innerHTML = Object.keys(p.specs).slice(0, 4).map(function (k) {
      return '<div class="spec-row"><dt>' + k + "</dt><dd>" + p.specs[k] + "</dd></div>";
    }).join("");

    $("#pdp-spectable").innerHTML = Object.keys(p.specs).map(function (k) {
      return '<div class="spec-row"><dt>' + k + "</dt><dd>" + p.specs[k] + "</dd></div>";
    }).join("");

    // documents for this SKU (sds is per family, the rest per product)
    $$("[data-doc]").forEach(function (a) {
      var kind = a.getAttribute("data-doc");
      var key = kind === "sds" ? p.cat : p.slug;
      a.setAttribute("href", "docs/" + kind + "-" + key + ".pdf");
      a.setAttribute("download", "");
      a.setAttribute("target", "_blank");
      a.setAttribute("rel", "noopener");
    });

    $("#pdp-sizes").innerHTML = p.sizes.map(function (s, i) {
      return '<button class="size' + (i === 0 ? " is-active" : "") + '">' + s + "</button>";
    }).join("");
    $$("#pdp-sizes .size").forEach(function (b) {
      b.addEventListener("click", function () {
        $$("#pdp-sizes .size").forEach(function (x) { x.classList.remove("is-active"); });
        b.classList.add("is-active");
      });
    });

    $("#pdp-thumbs").innerHTML = [p.slug, p.slug, p.slug].map(function (s, i) {
      return '<div class="pdp__thumb' + (i === 0 ? " is-active" : "") +
        '"><img src="assets/img/products/' + s + '-tile.webp" alt=""></div>';
    }).join("");

    var related = DATA.products.filter(function (x) {
      return x.slug !== p.slug && (x.cat === p.cat || x.apps.some(function (a) { return p.apps.indexOf(a) > -1; }));
    }).slice(0, 4);
    $("#pdp-related").innerHTML = related.map(function (x) {
      return '<a class="mini-prod" href="product.html?p=' + x.slug + '">' +
        '<img src="assets/img/products/' + x.slug + '-tile.webp" alt="">' +
        '<div><div class="mini-prod__t">' + x.name + "</div>" +
        '<div class="mini-prod__s">' + x.blurb.slice(0, 56) + "…</div></div></a>";
    }).join("");

    $$("[data-ptab]").forEach(function (t) {
      t.addEventListener("click", function () {
        $$("[data-ptab]").forEach(function (x) { x.classList.toggle("is-active", x === t); });
        $$("[data-ppanel]").forEach(function (pan) {
          pan.style.display = pan.getAttribute("data-ppanel") === t.getAttribute("data-ptab") ? "" : "none";
        });
      });
    });
  }

  /* ---------------- forms ---------------- */
  $$("form[data-form]").forEach(function (f) {
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      var ok = f.querySelector("[data-ok]");
      if (ok) ok.classList.add("is-visible");
      var btn = f.querySelector("button[type=submit]");
      if (btn) { btn.disabled = true; btn.style.opacity = ".7"; }
      setTimeout(function () {
        if (btn) { btn.disabled = false; btn.style.opacity = ""; }
      }, 2500);
    });
  });

  /* ---------------- smooth anchor offset ---------------- */
  $$('a[href^="#"]').forEach(function (a) {
    a.addEventListener("click", function (e) {
      var id = a.getAttribute("href");
      if (id.length < 2) return;
      var el = document.querySelector(id);
      if (!el) return;
      e.preventDefault();
      var y = el.getBoundingClientRect().top + window.scrollY - 96;
      window.scrollTo({ top: y, behavior: "smooth" });
      document.body.classList.remove("nav-open");
    });
  });
})();

/* ---------------- AI assistant widget ---------------- */
(function () {
  "use strict";

  var widget = document.getElementById("ai-widget");
  if (!widget) return;

  var launch = document.getElementById("ai-launch");
  var panel = document.getElementById("ai-panel");
  var closeBtn = document.getElementById("ai-close");
  var presenceBtn = document.getElementById("ai-presence-btn");
  var presence = document.getElementById("ai-presence");
  var caption = document.getElementById("ai-caption");
  var body = document.getElementById("ai-body");
  var chips = document.getElementById("ai-chips");
  var form = document.getElementById("ai-form");
  var text = document.getElementById("ai-text");
  var greeting = document.getElementById("ai-greeting");

  var AV = '<img src="assets/img/avatar/avatar-b1.jpg" alt="">';

  function setOpen(open) {
    widget.classList.toggle("is-open", open);
    launch.setAttribute("aria-expanded", open ? "true" : "false");
    if (open) setTimeout(function () { text && text.focus(); }, 180);
  }

  launch.addEventListener("click", function () { setOpen(true); });
  closeBtn.addEventListener("click", function () { setOpen(false); });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && widget.classList.contains("is-open")) setOpen(false);
  });

  // digital human view
  presenceBtn.addEventListener("click", function () {
    var on = presence.classList.toggle("is-on");
    presenceBtn.style.background = on ? "rgba(255,255,255,.18)" : "";
    if (on) caption.textContent = "Describe a target and a constraint — I will propose a construct, a host and a bench plan.";
  });

  // quick prompts
  chips.addEventListener("click", function (e) {
    var chip = e.target.closest(".ai-chip");
    if (!chip) return;
    text.value = chip.textContent;
    text.focus();
  });

  function addMsg(who, html) {
    var row = document.createElement("div");
    row.className = "ai-msg" + (who === "user" ? " ai-msg--user" : "");
    row.innerHTML = who === "user"
      ? '<div class="ai-bubble"></div>'
      : '<span class="ai-msg__av">' + AV + '</span><div class="ai-bubble">' + html + "</div>";
    if (who === "user") row.querySelector(".ai-bubble").textContent = html;
    body.appendChild(row);
    body.scrollTop = body.scrollHeight;
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var q = (text.value || "").trim();
    if (!q) return;
    text.value = "";
    addMsg("user", q);
    setTimeout(function () {
      addMsg("ai", "This is a front-end demo — the design engine is not connected yet. " +
        "In production this reply would return a construct proposal (codon table, host, tags), " +
        "a predicted yield band, and a bench plan you can approve or send to a scientist.");
    }, 550);
  });

  // contextual greeting on product pages
  var params = new URLSearchParams(location.search);
  var slug = params.get("p");
  if (slug && window.TL && window.TL.products) {
    var p = window.TL.products.filter(function (x) { return x.slug === slug; })[0];
    if (p) {
      greeting.innerHTML = "You are looking at <b>" + p.name + "</b>. Tell me what you need it for — " +
        "I can check whether it fits your workflow, or design a construct around it.";
      caption.textContent = "Ask how " + p.name + " fits your experiment.";
    }
  }
})();
