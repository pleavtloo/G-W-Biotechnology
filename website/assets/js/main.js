/* G&W Biotechnologie GmbH — interaction layer */
(function () {
  "use strict";

  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  /* ---------------- cart (localStorage, no account required) ---------------- */

  var CART_KEY = "tl-cart-v1";

  function cartRead() {
    try {
      return JSON.parse(localStorage.getItem(CART_KEY) || "[]");
    } catch (e) {
      return [];
    }
  }

  function cartWrite(items) {
    try {
      localStorage.setItem(CART_KEY, JSON.stringify(items));
    } catch (e) { /* private mode: cart simply does not persist */ }
    cartRender();
  }

  function cartCount() {
    return cartRead().reduce(function (n, it) { return n + (Number(it.qty) || 0); }, 0);
  }

  function cartRender() {
    var el = document.getElementById("cart-count");
    if (!el) return;
    var n = cartCount();
    el.textContent = String(n);
    el.hidden = n === 0;
  }

  function cartAdd(item) {
    var items = cartRead();
    var hit = null;
    for (var i = 0; i < items.length; i += 1) {
      if (items[i].key === item.key) { hit = items[i]; break; }
    }
    if (hit) {
      hit.qty = Math.min(99, (Number(hit.qty) || 0) + item.qty);
    } else {
      items.push(item);
    }
    cartWrite(items);
  }

  function fmtMoney(n) {
    var v = Number(n) || 0;
    return v.toLocaleString("en-US", { minimumFractionDigits: 0, maximumFractionDigits: 2 });
  }

  // Renders cart.html; no-op on every other page.
  function cartPageRender() {
    var host = document.getElementById("cart-lines");
    if (!host) return;

    var items = cartRead();
    var empty = document.getElementById("cart-empty");
    var body = document.getElementById("cart-body");

    if (!items.length) {
      if (empty) empty.hidden = false;
      if (body) body.hidden = true;
      return;
    }
    if (empty) empty.hidden = true;
    if (body) body.hidden = false;

    var total = 0;
    host.innerHTML = items.map(function (it, i) {
      var line = (Number(it.price) || 0) * (Number(it.qty) || 0);
      total += line;
      return '<div class="cart-line">' +
        '<div class="cart-line__main"><b>' + it.name + "</b><span>" +
        it.spec + (it.sku ? " · " + it.sku : "") +
        (it.price === null || it.price === undefined ? " · price on request" : "") +
        "</span></div>" +
        '<div class="cart-line__qty"><div class="qty qty--sm">' +
        '<button type="button" data-dec="' + i + '" aria-label="Decrease quantity">&minus;</button>' +
        '<input type="number" value="' + it.qty + '" min="1" max="99" data-set="' + i + '" aria-label="Quantity">' +
        '<button type="button" data-inc="' + i + '" aria-label="Increase quantity">+</button>' +
        "</div></div>" +
        '<div class="cart-line__price">' +
        (it.price === null || it.price === undefined ? "—" : (window.TL_CUR; "$") + fmtMoney(line)) +
        "</div>" +
        '<button type="button" class="cart-line__del" data-del="' + i + '" aria-label="Remove">&times;</button>' +
        "</div>";
    }).join("");

    var sub = document.getElementById("cart-subtotal");
    if (sub) sub.textContent = (window.TL_CUR; "$") + fmtMoney(total);

    function setQty(index, value) {
      var arr = cartRead();
      if (!arr[index]) return;
      arr[index].qty = Math.max(1, Math.min(99, value));
      cartWrite(arr);
      cartPageRender();
    }

    // Delegated once per render; assigning (not addEventListener) avoids stacking.
    host.onclick = function (e) {
      var el = e.target;
      var del = el.getAttribute && el.getAttribute("data-del");
      if (del !== null && del !== undefined) {
        var arr = cartRead();
        arr.splice(Number(del), 1);
        cartWrite(arr);
        cartPageRender();
        return;
      }
      var inc = el.getAttribute && el.getAttribute("data-inc");
      var dec = el.getAttribute && el.getAttribute("data-dec");
      if (inc !== null && inc !== undefined) {
        var a1 = cartRead();
        setQty(Number(inc), (Number(a1[Number(inc)] && a1[Number(inc)].qty) || 1) + 1);
      } else if (dec !== null && dec !== undefined) {
        var a2 = cartRead();
        setQty(Number(dec), (Number(a2[Number(dec)] && a2[Number(dec)].qty) || 1) - 1);
      }
    };

    host.onchange = function (e) {
      var idx = e.target.getAttribute && e.target.getAttribute("data-set");
      if (idx === null || idx === undefined) return;
      setQty(Number(idx), Number(e.target.value) || 1);
    };
  }

  // Replaces the checkout form with a prompt when the visitor cannot order yet.
  function checkoutGate(form, kind) {
    var body = kind === "signin"
      ? "<b>Sign in to place your order.</b> We ask for an account so we can confirm stock, " +
        "quote shipping and keep your order history in one place. It takes about 30 seconds."
      : "<b>Your account is awaiting approval.</b> We review every account individually so we " +
        "can price and ship correctly. You will hear from us within one business day (Mon–Fri).";
    var actions = kind === "signin"
      ? '<a class="btn" href="login.html?next=checkout.html">Sign in</a>' +
        '<a class="btn btn--ghost" href="register.html?next=checkout.html">Create an account</a>'
      : '<a class="btn" href="account.html">View your account</a>' +
        '<a class="btn btn--ghost" href="contact.html">Contact us</a>';
    form.innerHTML = '<div class="co-gate"><p>' + body + "</p>" +
      '<div class="co-gate__actions">' + actions + "</div></div>";
  }

  // Renders checkout.html: order summary plus a hidden field the email will carry.
  function checkoutPageRender() {
    var host = document.getElementById("checkout-summary");
    if (!host) return;

    // Back from Stripe: confirm server-side rather than trusting the URL.
    var qs = new URLSearchParams(location.search);
    var sessionId = qs.get("session_id");
    if (sessionId) {
      var shell = document.querySelector(".checkout");
      if (shell) {
        shell.innerHTML = '<div class="checkout__done"><h2>Confirming payment…</h2>' +
          "<p>This takes a moment. Do not close this page.</p></div>";
      }
      fetch("/api/order/verify", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ session_id: sessionId }),
      }).then(function (r) { return r.json(); }).then(function (d) {
        var paid = d && d.paid;
        if (paid) cartWrite([]);
        var amount = d && d.amount ? (window.TL_CUR; "$") + fmtMoney(d.amount / 100) : "";
        var box = document.querySelector(".checkout");
        if (!box) return;
        box.innerHTML = '<div class="checkout__done">' +
          "<h2>" + (paid ? "Payment received" : "Payment not completed") + "</h2>" +
          (d && d.id ? '<p class="checkout__id">Order reference <b>' + d.id + "</b></p>" : "") +
          (paid ? '<p class="checkout__pay">Charged ' + amount + "</p>" : "") +
          "<p>" + (paid
            ? "Thank you. We will confirm stock and shipping within one business day (Mon–Fri). " +
              "Stripe has emailed your receipt."
            : "Your card was not charged. You can try again, or reply to our confirmation email " +
              "and we will send a new link.") + "</p>" +
          '<a class="btn" href="products.html">Back to the catalogue</a>' +
          "</div>";
      }).catch(function () {
        var box = document.querySelector(".checkout");
        if (box) {
          box.innerHTML = '<div class="checkout__done"><h2>Could not confirm the payment</h2>' +
            "<p>Your order is safe either way. Reply to the confirmation email and we will check " +
            "it manually.</p>" +
            '<a class="btn" href="products.html">Back to the catalogue</a></div>';
        }
      });
      return;
    }

    var items = cartRead();
    var form = document.querySelector('form[data-form="checkout"]');
    var btn = form ? form.querySelector("button[type=submit]") : null;

    if (!items.length) {
      host.innerHTML = '<p class="checkout__empty">Your cart is empty. ' +
        '<a href="products.html">Browse the catalogue</a>.</p>';
      if (btn) btn.disabled = true;
      return;
    }

    var total = 0;
    var lines = items.map(function (it) {
      var line = (Number(it.price) || 0) * (Number(it.qty) || 0);
      total += line;
      return '<div class="sum-line"><span>' + it.spec + " <em>× " + it.qty + "</em></span><b>" +
        (it.price === null || it.price === undefined ? "—" : (window.TL_CUR; "$") + fmtMoney(line)) + "</b></div>";
    }).join("");

    function payLabel() {
      var picked = document.querySelector('input[name="payment"]:checked');
      return picked && picked.value === "online" ? "Card (link by email)" : "Bank transfer / PO";
    }

    host.innerHTML = lines +
      '<div class="sum-total"><span>Subtotal</span><b>$' + fmtMoney(total) + "</b></div>" +
      '<div class="sum-pay"><span>Payment</span><b id="sum-pay-label">' + payLabel() + "</b></div>";

    var hidden = document.getElementById("order-items");
    if (hidden) {
      hidden.value = items.map(function (it) {
        var line = (Number(it.price) || 0) * (Number(it.qty) || 0);
        return it.name + " — " + it.spec + (it.sku ? " (" + it.sku + ")" : "") + " × " + it.qty +
          (it.price === null || it.price === undefined
            ? " = price on request"
            : " = $" + fmtMoney(line));
      }).join("; ");
    }

    // Orders are account-only: replace the form with the right prompt instead of
    // letting the customer fill it in and get rejected at submit.
    var coForm = document.querySelector('form[data-form="checkout"]');
    if (coForm) {
      fetch("/api/me").then(function (r) { return r.json(); }).then(function (d) {
        var u = d && d.user;
        if (!u) return checkoutGate(coForm, "signin");
        if ((u.status || "pending") !== "active") return checkoutGate(coForm, "pending");
      }).catch(function () {});
    }

    // Bank details only matter for invoice customers.
    var payBox = document.getElementById("bank-fields");
    Array.prototype.forEach.call(document.querySelectorAll('input[name="payment"]'), function (r) {
      r.addEventListener("change", function () {
        var picked = document.querySelector('input[name="payment"]:checked');
        if (payBox) payBox.hidden = !!(picked && picked.value !== "bank_transfer");
        var lab = document.getElementById("sum-pay-label");
        if (lab) lab.textContent = payLabel();
      });
    });
  }

  // expose for the cart page
  window.TLCart = {
    read: cartRead, write: cartWrite, add: cartAdd, count: cartCount,
    render: cartRender, page: cartPageRender, checkout: checkoutPageRender,
  };

  // Header: swap "Sign in" for the first name once we know who is signed in.
  function refreshAccountLink() {
    var el = document.getElementById("nav-account");
    if (!el) return;
    fetch("/api/me", { headers: { accept: "application/json" } })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (d && d.user) {
          el.textContent = String(d.user.name || "").split(" ")[0] || "Account";
          el.href = "account.html";
        }
      })
      .catch(function () {});
  }

  function bootCart() {
    cartRender();
    cartPageRender();
    checkoutPageRender();
    refreshAccountLink();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bootCart);
  } else {
    bootCart();
  }

  /* ---------------- rich text ----------------
   * Descriptions are edited in the admin as HTML. Old records are plain text, so
   * everything goes through richToHtml; cleanHtml strips anything the toolbar
   * cannot produce, in case a value was pasted in with markup.
   */
  var RICH_TAGS = /^(P|BR|STRONG|B|EM|I|U|S|UL|OL|LI|H2|H3|H4|BLOCKQUOTE|A|TABLE|THEAD|TBODY|TR|TH|TD|HR|CODE)$/;

  function cleanHtml(html) {
    var box = document.createElement("div");
    box.innerHTML = String(html == null ? "" : html);
    Array.prototype.forEach.call(
      box.querySelectorAll("script,style,iframe,object,embed,form,input,button"),
      function (n) { n.parentNode.removeChild(n); });

    var nodes = Array.prototype.slice.call(box.querySelectorAll("*"));
    nodes.forEach(function (n) {
      if (!n.parentNode) return;
      if (!RICH_TAGS.test(n.tagName)) {
        n.parentNode.replaceChild(document.createTextNode(n.textContent || ""), n);
        return;
      }
      Array.prototype.slice.call(n.attributes).forEach(function (a) {
        if (n.tagName === "A" && a.name === "href") return;
        n.removeAttribute(a.name);
      });
      if (n.tagName === "A") {
        var href = n.getAttribute("href") || "";
        if (!/^(https?:\/\/|mailto:|\/)/i.test(href)) n.removeAttribute("href");
        n.setAttribute("rel", "noopener");
        n.setAttribute("target", "_blank");
      }
    });
    return box.innerHTML;
  }

  function richToHtml(value) {
    var raw = String(value == null ? "" : value);
    if (/<(p|h2|h3|h4|ul|ol|table|strong|em|br|blockquote)\b/i.test(raw)) {
      return cleanHtml(raw);
    }
    // legacy plain text: blank line = new paragraph, single newline = line break
    return raw.split(/\n{2,}/).map(function (block) {
      var text = block.trim();
      if (!text) return "";
      var safe = text.replace(/[&<>]/g, function (c) {
        return { "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c];
      });
      return "<p>" + safe.replace(/\n/g, "<br>") + "</p>";
    }).filter(Boolean).join("");
  }

  function stripHtml(value) {
    var box = document.createElement("div");
    box.innerHTML = richToHtml(value);
    return (box.textContent || "").replace(/\s+/g, " ").trim();
  }

  // Product tile: honour the image_tile field from the CMS, fall back to the slug
  // convention so existing products keep working without that field filled in.
  function tileSrc(p) {
    var slug = typeof p === "string" ? p : (p && p.slug) || "";
    var custom = p && typeof p === "object" ? p.imageTile : "";
    if (custom) {
      // The CMS may store a bare file name (media library) or a full path (hand written).
      return custom.indexOf("/") > -1 || custom.charAt(0) === "/" || /^(https?:)?\/\//.test(custom)
        ? custom
        : "assets/img/products/" + custom;
    }
    return "assets/img/products/" + slug + "-tile.webp";
  }

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

  // Inter has no glyph for U+2318, so the label defaults to "Ctrl K" and only
  // switches to the command symbol on Apple platforms (system font covers it).
  var kbd = document.querySelector("[data-kbd]");
  if (kbd && /Mac|iPhone|iPad|iPod/.test(navigator.platform || "")) kbd.textContent = "\u2318K";

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
          '<img src="' + tileSrc(p) + '" alt="">' +
          "<span><b>" + p.name + "</b><i>" + (DATA.cats[p.cat] || "") +
          (p.price ? " · from " + (window.TL_CUR; "$") + p.price : "") + "</i></span></a>";
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

    document.title = p.name + " — G&W Biotechnologie GmbH";
    $("#pdp-title").textContent = p.name;
    $("#pdp-blurb").textContent = p.blurb;
    $("#pdp-crumb").textContent = p.name;
    $("#pdp-img").src = tileSrc(p);
    $("#pdp-img").alt = p.name;

    // Cart: choose a pack size, set a quantity, add to the local cart.
    var qtyInput = document.getElementById("pdp-qty");
    var addBtn = document.getElementById("pdp-add");
    var quoteBtn = document.getElementById("pdp-secondary");
    if (quoteBtn) quoteBtn.href = "contact.html?p=" + p.slug + "#quote";

    function currentPack() {
      var all = document.querySelectorAll("#pdp-sizes .size");
      var idx = 0;
      for (var i = 0; i < all.length; i += 1) {
        if (all[i].classList.contains("is-active")) { idx = i; break; }
      }
      return packs[idx] || packs[0];
    }

    if (qtyInput) {
      $$(".qty button").forEach(function (b) {
        b.addEventListener("click", function () {
          var step = b.id === "qty-minus" ? -1 : 1;
          var v = Math.max(1, Math.min(99, (Number(qtyInput.value) || 1) + step));
          qtyInput.value = String(v);
        });
      });
    }

    if (addBtn) {
      addBtn.addEventListener("click", function () {
        var pack = currentPack();
        var qty = Math.max(1, Math.min(99, Number(qtyInput && qtyInput.value) || 1));
        cartAdd({
          key: p.slug + "|" + (pack.sku || pack.spec),
          slug: p.slug,
          name: p.name,
          sku: pack.sku || "",
          spec: pack.spec,
          price: pack.price,
          qty: qty,
        });
        var label = addBtn.textContent;
        addBtn.textContent = "Added to cart ✓";
        addBtn.disabled = true;
        setTimeout(function () {
          addBtn.textContent = label;
          addBtn.disabled = false;
        }, 1400);
      });
    }
    $("#pdp-catpill").textContent = DATA.cats[p.cat] || "";
    $("#pdp-cat").textContent = DATA.cats[p.cat] || "Catalogue";
    $("#pdp-cat").href = "products.html?cat=" + p.cat;
    $("#pdp-desc").innerHTML = richToHtml(p.desc);
    $("#pdp-price").innerHTML = p.price
      ? (window.TL_CUR; "$") + p.price.toLocaleString("en-US") + " <span>" + (window.TL_CUR_CODE; "USD") + "</span>"
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

    // Product structured data (Google reads JSON-LD injected after render)
    (function () {
      var ld = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": p.name,
        "description": stripHtml(p.desc),
        "sku": p.slug,
        "category": DATA.cats[p.cat] || "Life science reagents",
        "image": location.origin + "/assets/img/products/" + p.slug + ".webp",
        "brand": { "@type": "Brand", "name": "G&W Biotechnologie GmbH" },
        "manufacturer": { "@type": "Organization", "name": "G&W Biotechnologie GmbH Ltd." }
      };
      if (p.price) {
        ld.offers = {
          "@type": "Offer",
          "price": p.price,
          "priceCurrency": "USD",
          "availability": "https://schema.org/InStock",
          "url": location.href,
          "priceValidUntil": "2027-12-31",
          "seller": { "@type": "Organization", "name": "G&W Biotechnologie GmbH Ltd." }
        };
      }
      var el = document.createElement("script");
      el.type = "application/ld+json";
      el.textContent = JSON.stringify(ld);
      document.head.appendChild(el);
    })();

    // documents for this SKU (sds is per family, the rest per product)
    $$("[data-doc]").forEach(function (a) {
      var kind = a.getAttribute("data-doc");
      var key = kind === "sds" ? p.cat : p.slug;
      a.setAttribute("href", "docs/" + kind + "-" + key + ".pdf");
      a.setAttribute("download", "");
      a.setAttribute("target", "_blank");
      a.setAttribute("rel", "noopener");
    });

    // Pack sizes carry their own price when the official price list has one.
    var packs = (p.variants && p.variants.length)
      ? p.variants.map(function (v) { return { spec: v.spec, price: v.price, sku: v.sku }; })
      : p.sizes.map(function (s) { return { spec: s, price: null, sku: "" }; });
    $("#pdp-sizes").innerHTML = packs.map(function (v, i) {
      var price = (v.price === null || v.price === undefined)
        ? "Price on request"
        : (window.TL_CUR; "$") + Number(v.price).toLocaleString("en-US");
      return '<button class="size' + (i === 0 ? " is-active" : "") + '">' +
        '<span class="size__spec">' + v.spec + '</span>' +
        '<span class="size__price">' + price + "</span></button>";
    }).join("");
    $$("#pdp-sizes .size").forEach(function (b) {
      b.addEventListener("click", function () {
        $$("#pdp-sizes .size").forEach(function (x) { x.classList.remove("is-active"); });
        b.classList.add("is-active");
      });
    });

    // Catalogue numbers, so a customer can quote the exact code to sales.
    var skus = packs.map(function (v) { return v.sku; }).filter(Boolean);
    var skuLine = document.getElementById("pdp-skus");
    if (!skuLine) {
      skuLine = document.createElement("p");
      skuLine.id = "pdp-skus";
      skuLine.className = "pdp__skus";
      var host = document.getElementById("pdp-sizes");
      if (host && host.parentNode) host.parentNode.insertBefore(skuLine, host.nextSibling);
    }
    skuLine.textContent = skus.length
      ? "Catalogue no. " + skus.join("  ·  ")
      : "";

    $("#pdp-thumbs").innerHTML = [p.slug, p.slug, p.slug].map(function (s, i) {
      return '<div class="pdp__thumb' + (i === 0 ? " is-active" : "") +
        '"><img src="' + tileSrc(s) + '" alt=""></div>';
    }).join("");

    var related = DATA.products.filter(function (x) {
      return x.slug !== p.slug && (x.cat === p.cat || x.apps.some(function (a) { return p.apps.indexOf(a) > -1; }));
    }).slice(0, 4);
    $("#pdp-related").innerHTML = related.map(function (x) {
      return '<a class="mini-prod" href="product.html?p=' + x.slug + '">' +
        '<img src="' + tileSrc(x) + '" alt="">' +
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
  /* ---------------- forms: real submit ---------------- */
  var API = (window.TL && window.TL.api) || "/api";
  var MAIL = (window.TL && window.TL.contact && window.TL.contact.email) || "info@gwbioth.com";
  // Public Turnstile site key, injected at build time. Empty = widget off (local builds).
  var TS_KEY = (window.TL && window.TL.turnstileSiteKey) || "";

  var DEFAULT_ERR = "We could not send that just now. Please retry, or email " +
    '<a href="mailto:' + MAIL + '">' + MAIL + "</a> directly — we answer within one business day (Mon–Fri).";

  function fieldKey(el) {
    var name = el.getAttribute("name");
    if (name) return name;
    var fld = el.closest(".fld");
    var label = fld && fld.querySelector("label");
    var raw = (label && label.textContent) || el.getAttribute("aria-label") ||
      el.getAttribute("placeholder") || "field";
    return raw.replace(/[*\s]+/g, " ").trim().toLowerCase().replace(/\s+/g, "_").slice(0, 40);
  }

  function collect(form) {
    var out = {};
    $$("input, select, textarea", form).forEach(function (el) {
      if (!el.type || el.type === "submit" || el.type === "button") return;
      if (el.name === "website_url") return;
      var v = (el.value || "").trim();
      if (!v) return;
      out[fieldKey(el)] = v;
    });
    return out;
  }

  function honeypot(form) {
    if (form.querySelector('input[name="website_url"]')) return;
    var hp = document.createElement("input");
    hp.type = "text";
    hp.name = "website_url";
    hp.tabIndex = -1;
    hp.autocomplete = "off";
    hp.setAttribute("aria-hidden", "true");
    hp.style.cssText = "position:absolute;left:-9999px;width:1px;height:1px;opacity:0";
    form.appendChild(hp);
  }

  function ensureError(form) {
    var el = form.querySelector("[data-err]");
    if (el) return el;
    el = document.createElement("div");
    el.className = "form-err";
    el.setAttribute("role", "alert");
    el.setAttribute("data-err", "");
    el.innerHTML = DEFAULT_ERR;
    var ok = form.querySelector("[data-ok]");
    if (ok && ok.parentNode) ok.parentNode.insertBefore(el, ok);
    else form.appendChild(el);
    return el;
  }

  // kind: "rate" | "verify" | "generic" — every branch keeps a mailto way out.
  function showError(err, kind, retryAfter) {
    if (kind === "rate") {
      var mins = Math.max(1, Math.round((retryAfter || 300) / 60));
      err.innerHTML = "Too many submissions from this connection. Please try again in " + mins +
        " minutes, or email " + '<a href="mailto:' + MAIL + '">' + MAIL + "</a> directly.";
    } else if (kind === "verify") {
      err.innerHTML = "Please complete the verification above the button, then send again. " +
        "If it does not load, email " + '<a href="mailto:' + MAIL + '">' + MAIL + "</a> directly.";
    } else {
      err.innerHTML = DEFAULT_ERR;
    }
    err.classList.add("is-visible");
  }

  function mountTurnstile(form) {
    var holder = document.createElement("div");
    holder.setAttribute("data-turnstile", "");
    holder.style.marginTop = "16px";
    var anchor = form.querySelector(".form-grid") || form.querySelector(".field-row");
    if (anchor && anchor.parentNode) anchor.parentNode.insertBefore(holder, anchor.nextSibling);
    else form.appendChild(holder);

    if (!TS_KEY || !window.turnstile || !window.turnstile.render) {
      holder.style.display = "none";
      return;
    }
    form._tlWidget = window.turnstile.render(holder, {
      sitekey: TS_KEY,
      theme: "light",
      size: "flexible",
      callback: function (token) { form._tlToken = token; },
      "error-callback": function () { form._tlToken = ""; },
      "expired-callback": function () { form._tlToken = ""; }
    });
  }

  function resetTurnstile(form) {
    form._tlToken = "";
    if (window.turnstile && form._tlWidget != null) {
      try { window.turnstile.reset(form._tlWidget); } catch (e) { /* widget already gone */ }
    }
  }

  // Turnstile is only mounted on lead forms, and only when a site key exists.
  var leadForms = $$("form[data-form]").filter(function (f) {
    return f.getAttribute("data-form") !== "coa";
  });

  if (TS_KEY && leadForms.length) {
    var tsApi = document.createElement("script");
    tsApi.src = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";
    tsApi.async = true;
    tsApi.defer = true;
    tsApi.onload = function () { leadForms.forEach(mountTurnstile); };
    tsApi.onerror = function () { /* widget stays hidden; the server side still guards */ };
    document.head.appendChild(tsApi);
  }

  $$("form[data-form]").forEach(function (form) {
    honeypot(form);

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (form.dataset.busy === "1") return;

      var hp = form.querySelector('input[name="website_url"]');
      if (hp && hp.value) return;                        // silent drop

      var btn = form.querySelector("button[type=submit]");
      var ok = form.querySelector("[data-ok]");
      var err = ensureError(form);
      var label = btn ? btn.innerHTML : "";
      var kind = form.getAttribute("data-form") || "lead";
      var url = kind === "coa" ? API + "/coa"
        : kind === "checkout" ? API + "/order"
        : API + "/lead";
      var checkToken = TS_KEY && kind !== "coa";

      if (checkToken && (!form._tlWidget || !form._tlToken)) {
        showError(err, "verify");
        return;
      }

      form.dataset.busy = "1";
      err.classList.remove("is-visible");
      if (ok) ok.classList.remove("is-visible");
      if (btn) { btn.disabled = true; btn.setAttribute("aria-busy", "true"); btn.innerHTML = "Sending…"; }

      var payload = {
        form: kind,
        page: document.body.getAttribute("data-page") || "",
        path: location.pathname + location.search,
        fields: collect(form),
        referrer: document.referrer || "",
        ts: Date.now()
      };

      // Checkout carries the cart itself so the server can price and store it.
      if (kind === "checkout") {
        payload.items = cartRead().map(function (it) {
          return { name: it.name, sku: it.sku, spec: it.spec, qty: it.qty, price: it.price };
        });
        var payPick = form.querySelector('input[name="payment"]:checked');
        payload.payment = payPick ? payPick.value : "bank_transfer";
      }
      if (checkToken) payload.turnstileToken = form._tlToken;

      fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      })
        .then(function (r) {
          return r.json().catch(function () { return {}; }).then(function (body) {
            return {
              status: r.status,
              body: body,
              retryAfter: Number(r.headers.get("Retry-After")) || Number(body.retryAfter) || 0
            };
          });
        })
        .then(function (res) {
          if (res.status === 429) {
            showError(err, "rate", res.retryAfter);
            resetTurnstile(form);
            return;
          }
          if (res.status === 403) {
            showError(err, "verify");
            resetTurnstile(form);
            return;
          }
          if (res.status < 200 || res.status >= 300) {
            // Show what the server actually said instead of a blanket failure.
            var serverMsg = (res.body && res.body.error) || ("HTTP " + res.status);
            if (err) {
              err.textContent = serverMsg;
              err.classList.add("is-visible");
            }
            resetTurnstile(form);
            throw new Error("__shown__");
          }
          if (ok) {
            if (kind === "coa" && res.body.found === false) {
              ok.innerHTML = "We do not have that lot indexed yet. QA will email the certificate " +
                "within one business day (Mon–Fri).";
            }
            ok.classList.add("is-visible");
          }

          // Checkout empties the cart and replaces the whole block with a confirmation.
          if (kind === "checkout") {
            // Card: Stripe hosts the payment page, so hand the browser over and
            // keep the cart until the payment actually comes back confirmed.
            if (res.body && res.body.checkoutUrl) {
              location.href = res.body.checkoutUrl;
              return;
            }
            cartWrite([]);
            var oid = (res.body && res.body.id) || "";
            var isBank = payload.payment === "bank_transfer";
            var next = isBank
              ? "Within one business day (Mon–Fri) we will confirm stock and email an invoice with our " +
                "bank details. Please quote the reference above with your transfer."
              : "Within one business day (Mon–Fri) we will confirm stock and email a secure payment link. " +
                "Your card details are entered on Stripe's page, never on this site.";
            var wrap = document.querySelector(".checkout");
            if (wrap) {
              wrap.innerHTML = '<div class="checkout__done">' +
                "<h2>Order request received</h2>" +
                (oid ? '<p class="checkout__id">Order reference <b>' + oid + "</b></p>" : "") +
                '<p class="checkout__pay">Payment method: <b>' +
                (isBank ? "Bank transfer / purchase order" : "Card (link by email)") + "</b></p>" +
                "<p>" + next + "</p>" +
                "<p>A copy of this request has been emailed to you.</p>" +
                '<a class="btn" href="products.html">Back to the catalogue</a>' +
                "</div>";
            }
            resetTurnstile(form);
            return;
          }

          form.reset();
          resetTurnstile(form);
        })
        .catch(function (e) {
          if (e && e.message === "__shown__") return;   // already displayed
          showError(err, "generic");
        })
        .finally(function () {
          form.dataset.busy = "";
          if (btn) { btn.disabled = false; btn.removeAttribute("aria-busy"); btn.innerHTML = label; }
        });
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

/* ---------------- product assistant panel (lookup only) ---------------- */
(function () {
  "use strict";

  var widget = document.getElementById("ai-widget");
  if (!widget) return;

  var launch = document.getElementById("ai-launch");
  var closeBtn = document.getElementById("ai-close");
  var body = document.getElementById("ai-body");
  var chips = document.getElementById("ai-chips");
  var form = document.getElementById("ai-form");
  var text = document.getElementById("ai-text");
  var greeting = document.getElementById("ai-greeting");

  var DATA = window.TL || { products: [], cats: {} };
  var MAIL = (window.TL && window.TL.contact && window.TL.contact.email) || "info@gwbioth.com";
  var AV = '<img src="assets/img/avatar/avatar-b1.jpg" alt="">';

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

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

  /* ---- lookup: every answer is built from data.js, nothing is invented ---- */
  function norm(s) {
    return String(s || "").toLowerCase().replace(/[^a-z0-9]/g, "");
  }

  function words(q) {
    return String(q || "").toLowerCase().replace(/[^a-z0-9]+/g, " ").split(" ").filter(function (t) {
      return t.length > 2;
    });
  }

  function specText(p, max) {
    var specs = p.specs || {};
    var out = [];
    for (var k in specs) {
      if (!Object.prototype.hasOwnProperty.call(specs, k)) continue;
      if (out.length >= max) break;
      out.push("<b>" + esc(k) + "</b> " + esc(specs[k]));
    }
    return out.join(" · ");
  }

  function rank(q) {
    var qn = norm(q);
    var tk = words(q);
    var hits = [];
    (DATA.products || []).forEach(function (p) {
      var s = 0;
      var nameKey = norm(p.name);
      var slugKey = norm(p.slug);
      if (nameKey.length >= 4 && qn.indexOf(nameKey) > -1) s += 8;
      if (slugKey.length >= 3 && qn.indexOf(slugKey) > -1) s += 6;
      String(p.slug || "").split("-").forEach(function (part) {
        if (part.length >= 3 && tk.indexOf(part) > -1) s += 2;
      });
      if (s > 0) hits.push({ p: p, s: s });
    });
    hits.sort(function (a, b) { return b.s - a.s; });
    return hits;
  }

  function productAnswer(p, q) {
    var lower = String(q).toLowerCase();
    var wantsSpec = /spec|endotoxin|purity|storage|shelf|size|concentration|format|grade|µm|nm/.test(lower);
    var specs = specText(p, wantsSpec ? 5 : 2);
    var catName = (DATA.cats && DATA.cats[p.cat]) || "";
    return "<b>" + esc(p.name) + "</b>" + (catName ? " · " + esc(catName) : "") +
      "<br>" + esc(p.blurb) +
      (specs ? "<br>" + specs : "") +
      '<br><a href="product.html?p=' + esc(p.slug) + '">Specifications, sizes and COA</a>' +
      ' · <a href="contact.html?p=' + esc(p.slug) + '#quote">Request a quote</a>';
  }

  function handoff(lead) {
    return (lead || "That one needs a person.") + " " +
      '<a href="contact.html#quote">Send it to the team</a> — a named specialist replies within one business day (Mon–Fri). ' +
      "Or email " + '<a href="mailto:' + MAIL + '">' + MAIL + "</a>.";
  }

  function answerFor(q) {
    var lower = String(q).toLowerCase();

    // selection, method design, clinical or regulatory judgement -> human handoff
    if (/which (one|product|bead|beads|kit|antibody|medium|reagent)|recommend|should i|best |choose|select|suggest|design (a|an|the)|protocol|screen|clinical|dose|dosing/.test(lower)) {
      return handoff("Method design and reagent selection are a scientist's call.");
    }

    var hits = rank(q);
    if (hits.length && hits[0].s >= 4) {
      var html = productAnswer(hits[0].p, q);
      if (hits[1] && hits[1].s === hits[0].s) html += "<br><br>" + productAnswer(hits[1].p, q);
      return html;
    }

    if (/coa|certificate|lot number|lot no|batch/.test(lower)) {
      return "Lot-specific certificates come from the COA lookup — paste the lot number printed on the vial label: " +
        '<a href="resources.html#coa">COA lookup</a>. If the lot is not indexed yet, QA emails the certificate ' +
        "within one business day (Mon–Fri).";
    }
    if (/dmf|drug master|regulatory|authorisation|authorization/.test(lower)) {
      return "Two Type II Drug Master Files are on record: DMF 038124 (separation and activation beads) and " +
        "DMF 038820 (anti-human CD28). The <a href=\"quality.html\">quality page</a> covers what a DMF does; " +
        'letters of authorisation are issued per sponsor — <a href="contact.html#quote">request one here</a>.';
    }
    if (/datasheet|data sheet|document|pdf|quality overview|manual/.test(lower)) {
      return "Datasheets, COAs and the quality system overview sit under " +
        '<a href="resources.html">Resources</a>, and every product page links its own datasheet and COA.';
    }
    if (/shipping|ship|distribut|dealer|territor|reseller/.test(lower)) {
      return "Distribution is territory-based — the models and the application form are on the " +
        '<a href="partners.html">partners page</a>.';
    }

    return handoff("");
  }

  var asking = false;

  function ask(raw) {
    var q = String(raw || "").trim();
    if (!q || asking) return;
    text.value = "";
    addMsg("user", q);
    asking = true;
    setTimeout(function () {
      addMsg("ai", answerFor(q));
      asking = false;
    }, 320);
  }

  // preset questions send straight away — filling the box and waiting read as "broken"
  chips.addEventListener("click", function (e) {
    var chip = e.target.closest(".ai-chip");
    if (!chip) return;
    ask(chip.textContent);
  });

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    ask(text.value);
  });

  // contextual greeting on product pages
  var params = new URLSearchParams(location.search);
  var slug = params.get("p");
  if (slug && window.TL && window.TL.products) {
    var p = window.TL.products.filter(function (x) { return x.slug === slug; })[0];
    if (p) {
      greeting.innerHTML = "You are looking at <b>" + esc(p.name) + "</b>. Ask for its specifications, " +
        "sizes or documents; for method design I will hand you to an application scientist.";
    }
  }
})();
