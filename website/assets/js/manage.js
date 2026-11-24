/* Own admin UI: reads and writes the YAML through /api/admin, which the Node
 * bridge forwards to the content sidecar. Save = write file + git commit +
 * rebuild, so a change is live in a few seconds. */
(function () {
  "use strict";

  var API = "/api/admin";
  var TYPES = [
    { id: "products", label: "Products" },
    { id: "faq", label: "FAQ" },
    { id: "articles", label: "Articles" },
    { id: "applications", label: "Applications" },
    { id: "site", label: "Site settings" },
    { id: "orders", label: "Orders" },
    { id: "customers", label: "Customers" },
    { id: "system", label: "System" },
  ];

  // must match the values actually used in content/products/*.yaml
  var CATS = ["beads", "antibodies", "proteins", "media"];

  var SCHEMA = {
    products: [
      { k: "order", label: "Order", type: "number", hint: "Position on the catalogue page." },
      { k: "sku_code", label: "SKU code (internal)", type: "text" },
      { k: "slug", label: "Slug", type: "text", lock: true, hint: "URL, image and PDF use it. Do not change." },
      { k: "name", label: "Name", type: "text", wide: true },
      { k: "cat", label: "Category", type: "select", options: CATS },
      { k: "apps", label: "Applications", type: "list", hint: "One per line, e.g. tcell / nkcell / dc / msc" },
      { k: "price", label: "From price (USD)", type: "number" },
      { k: "variants", label: "Pack sizes and prices", type: "variants" },
      { k: "sizes", label: "Pack sizes shown on the page", type: "list" },
      { k: "blurb", label: "Short blurb", type: "text", wide: true },
      { k: "desc", label: "Description", type: "richtext" },
      { k: "highlights", label: "Highlights", type: "list" },
      { k: "specs", label: "Specifications", type: "kv" },
      { k: "image_tile", label: "Tile image", type: "text" },
      { k: "image", label: "Social image", type: "text" },
      { k: "shop_product_id", label: "Old shop product id", type: "number" },
    ],
    site: [
      { k: "name", label: "Site name", type: "text" },
      { k: "legal", label: "Legal name", type: "text" },
      { k: "email", label: "Public email", type: "text" },
      { k: "phone", label: "Phone (display)", type: "text" },
      { k: "phone_raw", label: "Phone (raw)", type: "text" },
      { k: "us_address", label: "US address", type: "text", wide: true },
      { k: "hours", label: "Office hours", type: "text" },
      { k: "founded", label: "Founded", type: "text" },
      { k: "dmf", label: "DMF number", type: "text" },
      { k: "site_url", label: "Site URL", type: "text" },
      { k: "shop_url", label: "Old shop URL", type: "text" },
      { k: "og_image", label: "Social image", type: "text" },
      { k: "twitter", label: "Twitter handle", type: "text" },
      { k: "turnstile_sitekey", label: "Turnstile site key", type: "text" },
      { k: "bank.beneficiary", label: "Bank · beneficiary", type: "text" },
      { k: "bank.account", label: "Bank · account number", type: "text" },
      { k: "bank.swift", label: "Bank · SWIFT / BIC", type: "text" },
      { k: "bank.bank_name", label: "Bank · bank name", type: "text" },
      { k: "bank.bank_address", label: "Bank · bank address", type: "text", wide: true },
      { k: "bank.terms", label: "Bank · payment terms", type: "text" },
    ],
  };

  var state = {
    kind: "products", items: [], current: null, data: null, dirty: false, status: "",
    bulk: false, selected: [],
  };

  function $(id) { return document.getElementById(id); }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  function money(n) {
    return (window.TL_CUR || "$") + Number(n || 0).toLocaleString("en-US", { maximumFractionDigits: 2 });
  }

  function when(ms) {
    var d = new Date(ms || Date.now());
    return d.toISOString().slice(0, 10) + " " + d.toTimeString().slice(0, 5);
  }

  // Fields such as "bank.account" address a nested object in the YAML.
  function getPath(obj, path) {
    var parts = String(path).split(".");
    var cur = obj;
    for (var i = 0; i < parts.length; i += 1) {
      if (cur == null) return undefined;
      cur = cur[parts[i]];
    }
    return cur;
  }

  function setPath(obj, path, value) {
    var parts = String(path).split(".");
    var cur = obj;
    for (var i = 0; i < parts.length - 1; i += 1) {
      if (typeof cur[parts[i]] !== "object" || cur[parts[i]] === null) cur[parts[i]] = {};
      cur = cur[parts[i]];
    }
    cur[parts[parts.length - 1]] = value;
  }

  function request(method, path, body) {
    var opts = { method: method, headers: { "content-type": "application/json" } };
    if (body !== undefined) opts.body = JSON.stringify(body);
    return fetch(API + path, opts).then(function (r) {
      if (r.status === 401) {
        location.href = "login.html";
        throw new Error("unauthorized");
      }
      return r.json();
    });
  }

  /* ---------------- sidebar ---------------- */

  function buildTypes() {
    var host = $("mg-types");
    host.innerHTML = "";
    TYPES.forEach(function (t) {
      var b = el("button", t.id === state.kind ? "is-on" : "", t.label);
      b.type = "button";
      b.addEventListener("click", function () { switchKind(t.id); });
      host.appendChild(b);
    });
  }

  function switchKind(kind) {
    if (state.dirty && !confirm("Discard unsaved changes?")) return;
    state.kind = kind;
    state.current = null;
    state.data = null;
    state.dirty = false;
    state.status = "";
    state.bulk = false;
    state.selected = [];
    $("mg-status").value = "";
    $("mg-search").value = "";
    $("mg-filters").hidden = kind !== "orders";
    $("mg-batch").hidden = kind !== "orders";
    $("mg-batch").textContent = "Batch";
    $("mg-bulk").hidden = true;
    buildTypes();
    $("mg-bar").hidden = true;
    $("mg-edit").innerHTML = '<div class="mg__empty">Pick something on the left to edit.</div>';
    loadList();
  }

  function visibleItems() {
    var q = ($("mg-search").value || "").toLowerCase();
    var st = state.status;
    return state.items.filter(function (it) {
      if (st && it.status !== st) return false;
      if (!q) return true;
      return (it.label || "").toLowerCase().indexOf(q) > -1 ||
        it.id.toLowerCase().indexOf(q) > -1 ||
        (it.sub || "").toLowerCase().indexOf(q) > -1;
    });
  }

  /* ---------------- list ---------------- */

  function loadList() {
    if (state.kind === "customers") return loadCustomers();
    if (state.kind === "orders") return loadOrders();
    if (state.kind === "system") return loadSystem();
    $("mg-items").innerHTML = '<div class="mg__empty">Loading…</div>';
    return request("GET", "/content/" + state.kind).then(function (d) {
      state.items = d.items || [];
      renderList();
    }).catch(function () {
      $("mg-items").innerHTML = '<div class="mg__empty">Could not load the list.</div>';
    });
  }

  /* ---------------- orders ---------------- */

  function loadOrders() {
    $("mg-items").innerHTML = '<div class="mg__empty">Loading…</div>';
    return fetch("/api/orders").then(function (r) { return r.json(); }).then(function (d) {
      state.items = (d.orders || []).map(function (o) {
        var f = o.fields || {};
        return {
          id: o.id,
          label: f.organisation || f.work_email || o.id,
          sub: money(o.total) + " · " + o.status + " · " + when(o.t),
          status: o.status,
          order: o,
        };
      });
      renderList();
    }).catch(function () {
      $("mg-items").innerHTML = '<div class="mg__empty">Could not load orders.</div>';
    });
  }

  function openOrder(id) {
    var hit = state.items.filter(function (i) { return i.id === id; })[0];
    var o = hit && hit.order;
    if (!o) return;
    state.current = id;
    state.dirty = false;
    renderList();
    $("mg-bar").hidden = true;

    var f = o.fields || {};
    var host = $("mg-edit");
    host.innerHTML = "";

    var hd = el("div", "mg__hd");
    var left = el("div");
    left.appendChild(el("h2", null, o.id));
    left.appendChild(el("p", null, "orders / " + (f.organisation || f.work_email || "")));
    hd.appendChild(left);

    // Documents sit with the title, not among the status buttons.
    var tools = el("div");
    tools.style.cssText = "display:flex;gap:8px;flex-wrap:wrap";

    var copy = el("button", null, "Copy link");
    copy.type = "button";
    copy.style.cssText = "padding:8px 14px;border:1px solid #d5dce6;border-radius:8px;" +
      "background:#fff;color:#344054;font-size:12.5px;cursor:pointer;white-space:nowrap";
    copy.addEventListener("click", function () {
      var url = location.origin + location.pathname + "?kind=orders&id=" +
        encodeURIComponent(o.id);
      var done = function () {
        copy.textContent = "Copied";
        setTimeout(function () { copy.textContent = "Copy link"; }, 1400);
      };
      if (navigator.clipboard) {
        navigator.clipboard.writeText(url).then(done).catch(function () { prompt("Copy this link", url); });
      } else {
        prompt("Copy this link", url);
      }
    });
    tools.appendChild(copy);

    var inv = el("a", null, "Invoice (PDF)");
    inv.href = "/api/invoice/" + encodeURIComponent(o.id);
    inv.target = "_blank";
    inv.rel = "noopener";
    inv.style.cssText = "padding:8px 14px;border:1px solid #d5dce6;border-radius:8px;" +
      "background:#fff;color:#344054;font-size:12.5px;text-decoration:none;white-space:nowrap";
    tools.appendChild(inv);

    hd.appendChild(tools);
    host.appendChild(hd);

    var rows = [
      ["Status", o.status],
      ["Placed", when(o.t)],
      ["Total", money(o.total)],
      ["Payment", o.payment === "bank_transfer" ? "Bank transfer / PO" : "Card"],
      ["Name", f.full_name || "—"],
      ["Company", f.organisation || "—"],
      ["Email", f.work_email || "—"],
      ["Phone", f.phone || "—"],
      ["Ship to", [f.address, f.city, f.postcode, f.country].filter(Boolean).join(", ") || "—"],
      ["PO number", f.po_number || "—"],
      ["Invoice to", f.billing_name || "—"],
      ["VAT", f.vat_number || "—"],
      ["Notes", f.notes || "—"],
    ];
    var box = el("div", "mg-kv");
    rows.forEach(function (r) {
      var row = el("div", "row");
      row.style.gridTemplateColumns = "150px 1fr";
      var k = el("input"); k.value = r[0]; k.readOnly = true;
      var v = el("input"); v.value = String(r[1]); v.readOnly = true;
      row.appendChild(k);
      row.appendChild(v);
      box.appendChild(row);
    });
    host.appendChild(box);

    var itemsBox = el("div");
    itemsBox.style.cssText = "margin-top:16px;border:1px solid #e3e8ef;border-radius:10px;padding:12px 14px";
    itemsBox.innerHTML = '<b style="font-size:12px;color:#475467">Items</b>' +
      (o.items || []).map(function (it) {
        return '<div style="display:flex;justify-content:space-between;gap:12px;margin-top:8px;font-size:13px">' +
          "<span>" + it.spec + " × " + it.qty + (it.sku ? " · " + it.sku : "") + "</span>" +
          "<b>" + (it.price == null ? "—" : money(Number(it.price) * Number(it.qty))) + "</b></div>";
      }).join("");
    host.appendChild(itemsBox);

    var statusHead = el("p");
    statusHead.style.cssText = "margin:24px 0 10px;font-size:12px;font-weight:600;color:#475467";
    statusHead.textContent = "Status";
    host.appendChild(statusHead);

    var actions = el("div");
    actions.style.cssText = "display:flex;gap:10px;flex-wrap:wrap";
    ["new", "confirmed", "paid", "shipped", "cancelled"].forEach(function (s) {
      var b = el("button", "mg-add", s);
      b.type = "button";
      b.style.padding = "9px 16px";
      if (s === o.status) {
        b.style.background = "#1d4ed8";
        b.style.color = "#fff";
        b.style.borderStyle = "solid";
      }
      b.addEventListener("click", function () { setOrderStatus(o.id, s); });
      actions.appendChild(b);
    });
    host.appendChild(actions);

    var hint = el("p", "mg-hint");
    hint.style.marginTop = "10px";
    hint.textContent = "Changing the status emails the customer (except back to new).";
    host.appendChild(hint);
  }

  function setOrderStatus(id, status) {
    fetch("/api/orders/status", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ id: id, status: status, notify: status !== "new" }),
    }).then(function (r) { return r.json(); }).then(function (d) {
      if (!d.ok) throw new Error(d.error || "failed");
      loadOrders();
      state.current = id;
      setTimeout(function () { openOrder(id); }, 350);
    }).catch(function (err) { alert(err.message || "Could not update."); });
  }

  function exportOrders() {
    var rows = visibleItems();
    if (!rows.length) {
      alert("Nothing to export with the current filter.");
      return;
    }
    var head = ["id", "placed", "status", "payment", "company", "contact", "email",
                "phone", "ship_to", "po_number", "invoice_to", "vat", "total", "items"];
    var lines = [head.map(function (h) { return '"' + h + '"'; }).join(",")];

    rows.forEach(function (r) {
      var o = r.order || {};
      var f = o.fields || {};
      var cells = [
        o.id, when(o.t), o.status,
        o.payment === "bank_transfer" ? "bank_transfer" : "card",
        f.organisation || "", f.full_name || "", f.work_email || "", f.phone || "",
        [f.address, f.city, f.postcode, f.country].filter(Boolean).join(", "),
        f.po_number || "", f.billing_name || "", f.vat_number || "",
        String(o.total || 0),
        (o.items || []).map(function (it) {
          return it.spec + " x" + it.qty + (it.sku ? " " + it.sku : "");
        }).join(" | "),
      ];
      lines.push(cells.map(function (v) {
        return '"' + String(v == null ? "" : v).replace(/"/g, '""') + '"';
      }).join(","));
    });

    var blob = new Blob(["\ufeff" + lines.join("\n")], { type: "text/csv;charset=utf-8" });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url;
    a.download = "tl-orders-" + new Date().toISOString().slice(0, 10) + ".csv";
    a.click();
    URL.revokeObjectURL(url);
  }

  /* ---------------- customers (accounts, not YAML) ---------------- */

  function loadCustomers() {
    $("mg-items").innerHTML = '<div class="mg__empty">Loading…</div>';
    fetch("/api/users").then(function (r) { return r.json(); }).then(function (d) {
      state.items = (d.users || []).map(function (u) {
        return {
          id: u.id,
          label: u.email,
          sub: [u.company, u.status].filter(Boolean).join(" · "),
          user: u,
        };
      });
      renderList();
    }).catch(function () {
      $("mg-items").innerHTML = '<div class="mg__empty">Could not load customers.</div>';
    });
  }

  function openCustomer(id) {
    var hit = state.items.filter(function (i) { return i.id === id; })[0];
    var u = hit && hit.user;
    if (!u) return;
    state.current = id;
    state.dirty = false;
    renderList();
    $("mg-bar").hidden = true;

    var host = $("mg-edit");
    host.innerHTML = "";

    var hd = el("div", "mg__hd");
    var left = el("div");
    left.appendChild(el("h2", null, u.name || u.email));
    left.appendChild(el("p", null, "customers / " + u.id));
    hd.appendChild(left);
    host.appendChild(hd);

    var rows = [
      ["Email", u.email, "email"],
      ["Name", u.name || "", "name"],
      ["Organisation", u.company || "", "company"],
      ["Status", u.status, null],
      ["Role", u.role || "customer", null],
      ["Signed up", new Date(u.created || Date.now()).toISOString().slice(0, 10), null],
    ];
    var box = el("div", "mg-kv");
    rows.forEach(function (r) {
      var row = el("div", "row");
      row.style.gridTemplateColumns = "150px 1fr";
      var k = el("input");
      k.value = r[0];
      k.readOnly = true;
      var v = el("input");
      v.value = String(r[1]);
      if (r[2]) {
        v.setAttribute("data-cu", r[2]);
        v.style.background = "#fff";
      } else {
        v.readOnly = true;
        v.style.background = "#f6f7f9";
        v.style.color = "#667085";
      }
      row.appendChild(k);
      row.appendChild(v);
      box.appendChild(row);
    });
    host.appendChild(box);

    var cuBar = el("div");
    cuBar.style.cssText = "display:flex;gap:10px;margin-top:14px;flex-wrap:wrap;align-items:center";
    var cuSave = el("button", null, "Save changes");
    cuSave.type = "button";
    cuSave.style.cssText = "padding:9px 16px;background:#1d4ed8;color:#fff;border:0;" +
      "border-radius:8px;font:inherit;font-size:12.5px;cursor:pointer";
    cuSave.addEventListener("click", function () { saveCustomer(u.id); });
    cuBar.appendChild(cuSave);

    var cuPw = el("button", null, "Set password");
    cuPw.type = "button";
    cuPw.style.cssText = "padding:9px 16px;border:1px dashed #c6d0dd;border-radius:8px;" +
      "background:#fff;color:#475467;font:inherit;font-size:12.5px;cursor:pointer";
    cuPw.addEventListener("click", function () { setCustomerPassword(u.id, u.email); });
    cuBar.appendChild(cuPw);

    var cuNote = el("span", "mg-hint");
    cuBar.appendChild(cuNote);
    host.appendChild(cuBar);
    host.appendChild(box);

    var actions = el("div");
    actions.style.cssText = "display:flex;gap:10px;margin-top:18px;flex-wrap:wrap";
    [["Approve", "active"], ["Reject", "rejected"], ["Set to pending", "pending"]]
      .forEach(function (pair) {
        var b = el("button", "mg-add", pair[0]);
        b.type = "button";
        b.style.padding = "9px 16px";
        if (u.status === pair[1]) {
          b.style.background = "#1d4ed8";
          b.style.color = "#fff";
          b.style.borderStyle = "solid";
        }
        b.addEventListener("click", function () { setCustomerStatus(u.id, pair[1]); });
        actions.appendChild(b);
      });
    host.appendChild(actions);

    var note = el("p", "mg-hint");
    note.style.marginTop = "14px";
    note.textContent = "Approved accounts can check out immediately. Pending accounts can browse and " +
      "build a cart, and see the waiting notice on their account page.";
    host.appendChild(note);

    // Their order history, keyed the same way the storefront does it.
    var head = el("p");
    head.style.cssText = "margin:26px 0 0;font-size:12px;font-weight:600;color:#475467";
    head.textContent = "Orders";
    host.appendChild(head);

    var listBox = el("div");
    listBox.style.cssText = "margin-top:10px";
    listBox.innerHTML = '<p class="mg-hint">Loading…</p>';
    host.appendChild(listBox);

    fetch("/api/orders").then(function (r) { return r.json(); }).then(function (d) {
      var mine = (d.orders || []).filter(function (o) {
        var of = o.fields || {};
        return (o.user && o.user === u.id) ||
          (!o.user && String(of.work_email || "").toLowerCase() === u.email);
      });
      if (!mine.length) {
        listBox.innerHTML = '<p class="mg-hint">No orders from this account yet.</p>';
        return;
      }
      var spent = mine.reduce(function (n, o) { return n + (Number(o.total) || 0); }, 0);
      listBox.innerHTML =
        '<p class="mg-hint" style="margin:0 0 10px">' + mine.length +
        (mine.length === 1 ? " order" : " orders") + " · " + money(spent) +
        " total · last " + when(mine[0].t) + "</p>" +
        mine.map(function (o) {
          return '<a href="manage.html?kind=orders&id=' + encodeURIComponent(o.id) + '" ' +
            'style="display:flex;justify-content:space-between;gap:12px;padding:9px 0;' +
            'border-bottom:1px solid #eef1f6;text-decoration:none;color:inherit;font-size:12.5px">' +
            "<span>" + o.id + "</span>" +
            '<span style="color:#8b97a8">' + when(o.t).slice(0, 10) + "</span>" +
            "<b>" + money(o.total) + "</b>" +
            '<span class="o-status o-status--' + o.status + '">' + o.status + "</span></a>";
        }).join("");
    }).catch(function () {
      listBox.innerHTML = '<p class="mg-hint">Could not load orders.</p>';
    });
  }

  function saveCustomer(id) {
    var payload = { id: id };
    Array.prototype.forEach.call(document.querySelectorAll("[data-cu]"), function (inp) {
      payload[inp.getAttribute("data-cu")] = inp.value.trim();
    });
    var note = document.querySelector("#mg-edit .mg-hint");
    fetch("/api/users/update", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(payload),
    }).then(function (r) { return r.json(); }).then(function (d) {
      if (!d.ok) throw new Error(d.error || "could not save");
      if (note) {
        note.textContent = "Saved — " + (d.changed || []).join(", ");
        note.style.color = "#0f7a48";
      }
      loadCustomers();
      setTimeout(function () { openCustomer(id); }, 300);
    }).catch(function (err) { alert(err.message || "Could not save."); });
  }

  function setCustomerPassword(id, email) {
    var pw = window.prompt("New password for " + email +
      "\n\nAt least 8 characters. Tell the customer directly — no email is sent.", "");
    if (!pw) return;
    fetch("/api/users/update", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ id: id, password: pw }),
    }).then(function (r) { return r.json(); }).then(function (d) {
      if (!d.ok) throw new Error(d.error || "could not set the password");
      alert("Password updated. Give it to the customer through a channel you trust.");
    }).catch(function (err) { alert(err.message || "Could not set the password."); });
  }

  function setCustomerStatus(id, status) {
    fetch("/api/users/status", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ id: id, status: status }),
    }).then(function (r) { return r.json(); }).then(function (d) {
      if (!d.ok) throw new Error(d.error || "failed");
      loadCustomers();
      state.current = id;
      setTimeout(function () { openCustomer(id); }, 350);
    }).catch(function (err) { alert(err.message || "Could not update."); });
  }

  function renderList() {
    var host = $("mg-items");
    host.innerHTML = "";
    var shown = visibleItems();
    if (!shown.length) {
      host.innerHTML = '<div class="mg__empty">Nothing matches.</div>';
      return;
    }
    shown.forEach(function (it) {
      var picked = state.bulk && state.selected.indexOf(it.id) > -1;
      var b = el("button", "mg__item" +
        ((state.bulk ? picked : state.current === it.id) ? " is-on" : ""));
      b.type = "button";

      if (state.bulk) {
        b.style.cssText = "display:flex;gap:10px;align-items:flex-start";
        var cb = el("input");
        cb.type = "checkbox";
        cb.checked = picked;
        cb.style.marginTop = "3px";
        b.appendChild(cb);
      }

      var txt = el("div");
      txt.style.flex = "1";
      txt.appendChild(el("b", null, it.label || it.id));
      txt.appendChild(el("span", null, it.sub || it.id));
      b.appendChild(txt);

      b.addEventListener("click", function () {
        if (state.bulk) {
          var i = state.selected.indexOf(it.id);
          if (i > -1) state.selected.splice(i, 1);
          else state.selected.push(it.id);
          bulkUpdate();
          renderList();
          return;
        }
        openItem(it.id);
      });

      // Products carry a display order; nudge it without touching YAML by hand.
      if (state.kind === "products" && !state.bulk) {
        var idx = shown.indexOf(it);
        var arrows = el("div");
        arrows.style.cssText = "display:flex;flex-direction:column;gap:2px;flex:none";

        [["▲", -1, idx === 0], ["▼", 1, idx === shown.length - 1]].forEach(function (spec) {
          var ab = el("button", null, spec[0]);
          ab.type = "button";
          ab.disabled = spec[2];
          ab.style.cssText = "width:24px;height:20px;padding:0;border:1px solid #e3e8ef;" +
            "border-radius:4px;background:#fff;color:#475467;font-size:10px;line-height:1;" +
            "cursor:pointer" + (spec[2] ? ";opacity:.3;cursor:default" : "");
          ab.addEventListener("click", function (e) {
            e.stopPropagation();
            if (spec[2]) return;
            moveProduct(it.id, spec[1]);
          });
          arrows.appendChild(ab);
        });
        b.appendChild(arrows);
      }

      host.appendChild(b);
    });
  }

  /* ---------------- system status ---------------- */

  function loadSystem() {
    $("mg-items").innerHTML = '<div class="mg__empty">Status is on the right →</div>';
    $("mg-bar").hidden = true;
    var host = $("mg-edit");
    host.innerHTML = '<div class="mg__empty">Checking…</div>';

    fetch("/api/system").then(function (r) { return r.json(); }).then(function (d) {
      if (!d.ok) throw new Error(d.error || "failed");
      renderSystem(d);
    }).catch(function (err) {
      host.innerHTML = '<div class="mg__empty">' +
        escapeHtml(err.message || "Could not read status.") + "</div>";
    });
  }

  function renderSystem(d) {
    var host = $("mg-edit");
    host.innerHTML = "";

    var hd = el("div", "mg__hd");
    var left = el("div");
    left.appendChild(el("h2", null, "System"));
    left.appendChild(el("p", null, "backups · services · disk"));
    hd.appendChild(left);
    host.appendChild(hd);

    function card(title, rows) {
      var box = el("div");
      box.style.cssText = "border:1px solid #e3e8ef;border-radius:10px;padding:14px 16px;" +
        "margin-bottom:14px;background:#fff;max-width:640px";
      var h = el("p", null, title);
      h.style.cssText = "margin:0 0 10px;font-size:12px;font-weight:600;color:#475467";
      box.appendChild(h);
      rows.forEach(function (r) {
        var line = el("div");
        line.style.cssText = "display:flex;gap:12px;padding:4px 0;font-size:12.5px;" +
          "border-bottom:1px solid #f5f7fa";
        var k = el("span", null, r[0]);
        k.style.cssText = "color:#8b97a8;min-width:120px;flex:none";
        var v = el("span", null, String(r[1]));
        v.style.cssText = "flex:1;color:#344054" + (r[2] ? ";" + r[2] : "");
        line.appendChild(k);
        line.appendChild(v);
        box.appendChild(line);
      });
      return box;
    }

    function stamp(s) {
      return s ? String(s).replace("T", " ").slice(0, 19) : "—";
    }

    var b = d.backup || {};
    var bk = [
      ["Last run", stamp(b.at)],
      ["Archive", b.file || "—"],
      ["Size", b.size ? Math.round(b.size / 1024) + " KB" : "—"],
      ["Kept", b.kept ? b.kept + " days" : "—"],
      ["Mailed", b.mailed_at ? stamp(b.mailed_at) : "not yet"],
    ];
    if (b.ok === false) {
      bk.unshift(["Status", b.note || "failed", "color:#b42318;font-weight:600"]);
    }
    host.appendChild(card("Backups", bk));

    if ((d.files || []).length) {
      host.appendChild(card("Recent archives", d.files.map(function (f) {
        return [f.name.replace("tl-backup-", "").replace(".tar.gz", ""),
                Math.round(f.size / 1024) + " KB"];
      })));
    }

    host.appendChild(card("Services", Object.keys(d.services || {}).map(function (k) {
      var v = d.services[k];
      return [k, v, v === "active" ? "color:#0f7a48;font-weight:600"
        : "color:#b42318;font-weight:600"];
    })));

    if (d.stripe) {
      var s = d.stripe;
      var modeRow = s.mode === "live"
        ? ["Mode", "live — real payments", "color:#0f7a48;font-weight:600"]
        : s.mode === "test"
          ? ["Mode", "test — no real money", "color:#b45309;font-weight:600"]
          : ["Mode", "not configured", "color:#b42318;font-weight:600"];

      var srows = [
        modeRow,
        ["Key", s.key_prefix || "—"],
        ["Webhook", s.webhook === "configured" ? "configured" : "missing",
          s.webhook === "configured" ? "color:#0f7a48" : "color:#b42318;font-weight:600"],
      ];
      if (s.account) srows.push(["Account", s.account]);
      if (s.business) srows.push(["Account name", s.business]);
      if (s.country) {
        srows.push(["Country / currency",
          s.country + " / " + String(s.currency || "").toUpperCase()]);
      }
      if (s.charges !== undefined) {
        srows.push(["Charges", s.charges ? "enabled" : "disabled",
          s.charges ? "color:#0f7a48;font-weight:600" : "color:#b42318;font-weight:600"]);
      }
      if (s.payouts !== undefined) {
        srows.push(["Payouts", s.payouts ? "enabled" : "disabled",
          s.payouts ? "color:#0f7a48" : "color:#b42318;font-weight:600"]);
      }
      if (s.reachable === false) {
        srows.push(["Stripe API", "unreachable", "color:#b42318;font-weight:600"]);
      }
      host.appendChild(card("Stripe", srows));
    }

    if (d.disk) {
      var p = d.disk.split(/\s+/);
      host.appendChild(card("Disk", [
        ["Size", p[1] || "—"],
        ["Used", p[2] || "—"],
        ["Available", p[3] || "—"],
        ["Use", p[4] || "—"],
      ]));
    }

    if (d.deploy && d.deploy.commit) {
      host.appendChild(card("Last deploy", [
        ["Commit", d.deploy.commit],
        ["At", stamp(d.deploy.at)],
        ["State", d.deploy.state || "—"],
      ]));
    }
  }

  /* ---------------- reordering ---------------- */

  function toast(msg, bad) {
    var t = document.getElementById("mg-toast");
    if (!t) {
      t = el("div");
      t.id = "mg-toast";
      t.style.cssText = "position:fixed;bottom:26px;left:50%;transform:translateX(-50%);" +
        "padding:10px 18px;border-radius:10px;background:#101828;color:#fff;" +
        "font-size:13px;z-index:99;transition:opacity .3s;box-shadow:0 8px 24px rgba(0,0,0,.18)";
      document.body.appendChild(t);
    }
    t.textContent = msg;
    t.style.background = bad ? "#b42318" : "#101828";
    t.style.opacity = "1";
    clearTimeout(t._hide);
    t._hide = setTimeout(function () { t.style.opacity = "0"; }, 1900);
  }

  function moveProduct(id, dir) {
    var items = visibleItems().slice();
    var i = -1;
    for (var k = 0; k < items.length; k += 1) {
      if (items[k].id === id) { i = k; break; }
    }
    var j = i + dir;
    if (i < 0 || j < 0 || j >= items.length) return;

    var swapped = items[i];
    items[i] = items[j];
    items[j] = swapped;

    var ids = items.map(function (x) { return x.id; });
    toast("Reordering…");
    request("POST", "/reorder", { kind: state.kind, ids: ids })
      .then(function (d) {
        if (!d.ok) throw new Error(d.error || "failed");
        return loadList();
      })
      .then(function () { toast("New order saved — live now."); })
      .catch(function (err) { toast(err.message || "Could not reorder.", true); });
  }

  /* ---------------- batch status (orders only) ---------------- */

  function toggleBulk() {
    state.bulk = !state.bulk;
    state.selected = [];
    state.current = null;
    $("mg-batch").textContent = state.bulk ? "Cancel" : "Batch";
    $("mg-bulk").hidden = !state.bulk;
    $("mg-bar").hidden = true;
    $("mg-bulk-status").textContent = "";
    if (!state.bulk) {
      $("mg-edit").innerHTML =
        '<div class="mg__empty">Pick something on the left to edit.</div>';
    }
    bulkUpdate();
    renderList();
  }

  function bulkUpdate() {
    $("mg-bulk-count").textContent = state.selected.length + " selected";
    var box = $("mg-bulk-btns");
    box.innerHTML = "";
    if (!state.selected.length) return;
    ["confirmed", "paid", "shipped", "cancelled"].forEach(function (s) {
      var b = el("button", null, "→ " + s);
      b.type = "button";
      b.style.cssText = "padding:8px 14px;border:1px solid #d5dce6;border-radius:8px;" +
        "background:#fff;color:#344054;font:inherit;font-size:12.5px;cursor:pointer";
      b.addEventListener("click", function () { bulkSetStatus(s); });
      box.appendChild(b);
    });
  }

  function bulkSetStatus(status) {
    var ids = state.selected.slice();
    if (!ids.length) return;
    var msg = "Set " + ids.length + " order" + (ids.length === 1 ? "" : "s") +
      ' to "' + status + '"? The customer is emailed for confirmed / paid / shipped / cancelled.';
    if (!confirm(msg)) return;

    var done = 0;
    var ok = 0;
    $("mg-bulk-status").textContent = "Updating 0/" + ids.length + "…";
    (function step(i) {
      if (i >= ids.length) {
        $("mg-bulk-status").textContent = ok + " of " + ids.length + " updated";
        state.selected = [];
        loadOrders().then(function () {
          bulkUpdate();
          renderList();
        });
        return;
      }
      fetch("/api/orders/status", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ id: ids[i], status: status, notify: status !== "new" }),
      }).then(function (r) { return r.json(); }).then(function (d) {
        if (d.ok) ok += 1;
      }).catch(function () { /* keep going */ }).then(function () {
        done += 1;
        $("mg-bulk-status").textContent = "Updating " + done + "/" + ids.length + "…";
        step(i + 1);
      });
    })(0);
  }

  /* ---------------- editor ---------------- */

  function openItem(id) {
    if (state.kind === "customers") return openCustomer(id);
    if (state.kind === "orders") return openOrder(id);
    if (state.dirty && !confirm("Discard unsaved changes?")) return;
    state.dirty = false;
    request("GET", "/content/" + state.kind + "/" + id).then(function (d) {
      state.current = id;
      state.data = d.data || {};
      renderList();
      renderForm();
    });
  }

  function fieldNode(f, value) {
    var wrap = el("div", "mg-field");
    var lab = el("label", null, f.label);
    if (f.hint) lab.appendChild(el("em", null, "  " + f.hint));
    wrap.appendChild(lab);

    var input;
    if (f.type === "richtext") {
      // The visible editor is contenteditable; a hidden textarea carries the
      // value so collect() reads it like any other field.
      var hidden = el("textarea");
      hidden.style.display = "none";
      hidden.setAttribute("data-field", f.k);
      hidden.value = richToHtml(value);
      wrap.appendChild(buildRichEditor(value, function (html) {
        hidden.value = html;
      }));
      wrap.appendChild(hidden);
      return wrap;
    }
    if (f.type === "textarea") {
      input = el("textarea");
      input.rows = f.rows || 4;
      input.value = value == null ? "" : String(value);
      input.setAttribute("data-field", f.k);
    } else if (f.type === "select") {
      input = el("select");
      var opts = (f.options || []).slice();
      // Never silently rewrite an unknown value to the first option: keep it
      // visible so a save cannot corrupt the record.
      if (value && opts.indexOf(value) === -1) opts.unshift(value);
      opts.forEach(function (o) {
        var opt = el("option", null, o);
        opt.value = o;
        if (o === value) opt.selected = true;
        input.appendChild(opt);
      });
      if (value && opts.indexOf(value) === -1) input.value = value;
      input.setAttribute("data-field", f.k);
    } else if (f.type === "number") {
      input = el("input");
      input.type = "number";
      input.value = value == null ? "" : String(value);
      input.setAttribute("data-field", f.k);
    } else if (f.type === "list") {
      input = el("textarea");
      input.rows = Math.max(3, (value || []).length + 1);
      input.value = (value || []).join("\n");
      input.setAttribute("data-field", f.k);
      input.setAttribute("data-kind", "list");
    } else {
      input = el("input");
      input.type = "text";
      input.value = value == null ? "" : String(value);
      input.setAttribute("data-field", f.k);
      if (f.lock) input.readOnly = true;
    }
    input.addEventListener("input", function () { state.dirty = true; });
    wrap.appendChild(input);

    // Image fields get an upload button: the file is resized and stored as WebP
    // server-side, then the path is written back into the field.
    if (f.k === "image_tile" || f.k === "image") {
      var picker = document.createElement("input");
      picker.type = "file";
      picker.accept = "image/*";
      picker.style.display = "none";

      var up = el("button", "mg-add", "Upload image");
      up.type = "button";
      up.style.marginTop = "6px";

      var note = el("span", "mg-hint");
      note.style.marginLeft = "10px";

      up.addEventListener("click", function () { picker.click(); });

      picker.addEventListener("change", function () {
        var file = picker.files && picker.files[0];
        if (!file) return;
        up.disabled = true;
        note.textContent = "Uploading…";

        var reader = new FileReader();
        reader.onload = function () {
          var slug = (state.data && state.data.slug) || state.current || "upload";
          var name = f.k === "image_tile" ? slug + "-tile" : slug;
          request("POST", "/upload", { name: name, data: reader.result })
            .then(function (d) {
              if (!d.ok) throw new Error(d.error || "upload failed");
              input.value = d.file.path;
              state.dirty = true;
              showPreview(Date.now());   // bust the cached copy of the old file
              var kb = Math.round((d.file.bytes || 0) / 1024);
              note.textContent = "Saved " + d.file.width + "×" + d.file.height +
                " · " + kb + " KB. Click Save & publish to go live.";
              var build = d.build || {};
              if (!build.ok) note.textContent += " (build failed — check the console)";
            })
            .catch(function (err) { note.textContent = err.message || "Upload failed."; })
            .then(function () { up.disabled = false; picker.value = ""; });
        };
        reader.readAsDataURL(file);
      });

      // Live preview: a wrong upload is obvious here, not after publishing.
      var prev = el("img");
      prev.alt = "";
      prev.style.cssText = "display:block;margin-top:10px;max-width:260px;max-height:170px;" +
        "object-fit:cover;border:1px solid #e3e8ef;border-radius:8px;background:#f8fafc;" +
        "cursor:zoom-in";

      function showPreview(stamp) {
        var v = (input.value || "").trim();
        if (!v) {
          prev.style.display = "none";
          return;
        }
        prev.style.display = "block";
        prev.src = "/" + v.replace(/^\/+/, "") + (stamp ? "?v=" + stamp : "");
      }

      prev.addEventListener("click", function () {
        if (prev.src) window.open(prev.src, "_blank", "noopener");
      });
      prev.addEventListener("error", function () { prev.style.display = "none"; });
      input.addEventListener("input", function () { showPreview(); });
      showPreview();

      wrap.appendChild(up);
      wrap.appendChild(note);
      wrap.appendChild(prev);
      wrap.appendChild(picker);
    }

    return wrap;
  }

  function variantsNode(value) {
    var wrap = el("div", "mg-field");
    var lab = el("label", null, "Pack sizes and prices");
    lab.appendChild(el("em", null, "  the rows customers actually buy"));
    wrap.appendChild(lab);

    var box = el("div", "mg-variants");
    var table = el("table");
    table.innerHTML = "<thead><tr><th>SKU</th><th>Spec</th><th>Price</th><th></th></tr></thead>";
    var tbody = el("tbody");
    table.appendChild(tbody);
    box.appendChild(table);
    wrap.appendChild(box);

    function addRow(v) {
      v = v || { sku: "", spec: "", price: null };
      var tr = el("tr");
      [["sku", "text", v.sku], ["spec", "text", v.spec],
       ["price", "number", v.price == null ? "" : v.price]].forEach(function (c) {
        var td = el("td");
        var inp = el("input");
        inp.type = c[1];
        inp.value = c[2] == null ? "" : String(c[2]);
        inp.setAttribute("data-v", c[0]);
        inp.addEventListener("input", function () { state.dirty = true; });
        td.appendChild(inp);
        tr.appendChild(td);
      });
      var tdDel = el("td");
      var del = el("button", "mg-del", "×");
      del.type = "button";
      del.addEventListener("click", function () {
        tr.remove();
        state.dirty = true;
      });
      tdDel.appendChild(del);
      tr.appendChild(tdDel);
      tbody.appendChild(tr);
    }

    (value || []).forEach(addRow);

    var add = el("button", "mg-add", "+ Add pack size");
    add.type = "button";
    add.addEventListener("click", function () {
      addRow();
      state.dirty = true;
    });
    wrap.appendChild(add);
    return wrap;
  }

  function kvNode(value) {
    var wrap = el("div", "mg-field");
    var lab = el("label", null, "Specifications");
    lab.appendChild(el("em", null, "  shown in the table on the product page"));
    wrap.appendChild(lab);

    var box = el("div", "mg-kv");
    function addRow(pair) {
      pair = pair || { k: "", v: "" };
      var row = el("div", "row");
      [["k", pair.k], ["v", pair.v]].forEach(function (p, i) {
        var inp = el("input");
        inp.type = "text";
        inp.value = p[1] == null ? "" : String(p[1]);
        inp.placeholder = i === 0 ? "Label" : "Value";
        inp.setAttribute("data-kv", p[0]);
        inp.addEventListener("input", function () { state.dirty = true; });
        row.appendChild(inp);
      });
      var del = el("button", "mg-del", "×");
      del.type = "button";
      del.addEventListener("click", function () {
        row.remove();
        state.dirty = true;
      });
      row.appendChild(del);
      box.appendChild(row);
    }
    (value || []).forEach(addRow);
    wrap.appendChild(box);

    var add = el("button", "mg-add", "+ Add row");
    add.type = "button";
    add.addEventListener("click", function () {
      addRow();
      state.dirty = true;
    });
    wrap.appendChild(add);
    return wrap;
  }

  function renderForm() {
    var host = $("mg-edit");
    host.innerHTML = "";

    var hd = el("div", "mg__hd");
    var left = el("div");
    left.appendChild(el("h2", null, (state.data.name || state.data.title || state.current || "New")));
    left.appendChild(el("p", null, state.kind + " / " + (state.current || "new")));
    hd.appendChild(left);

    if (state.current) {
      var tools = el("div");
      tools.style.cssText = "display:flex;gap:8px";
      var hist = el("button", null, "History");
      hist.type = "button";
      hist.style.cssText = "padding:7px 13px;border:1px solid #d5dce6;border-radius:8px;" +
        "background:#fff;color:#344054;font:inherit;font-size:12.5px;cursor:pointer";
      hist.addEventListener("click", openHistory);
      tools.appendChild(hist);
      hd.appendChild(tools);
    }

    host.appendChild(hd);

    var schema = SCHEMA[state.kind];
    if (!schema) {
      // generic fallback: one control per key, type guessed from the value
      schema = Object.keys(state.data).map(function (k) {
        var v = state.data[k];
        // Nested objects need an explicit schema entry; rendering one as a text
        // box would overwrite the whole block with "[object Object]" on save.
        if (v && typeof v === "object" && !Array.isArray(v)) return null;
        var type = typeof v === "number" ? "number"
          : Array.isArray(v) ? "list"
          : typeof v === "string" && v.length > 90 ? "textarea" : "text";
        return { k: k, label: k.replace(/_/g, " "), type: type };
      }).filter(Boolean);
    }

    schema.forEach(function (f) {
      if (f.type === "variants") host.appendChild(variantsNode(state.data.variants));
      else if (f.type === "kv") host.appendChild(kvNode(state.data.specs));
      else host.appendChild(fieldNode(f, getPath(state.data, f.k)));
    });

    $("mg-bar").hidden = false;
    $("mg-status").textContent = "";
    $("mg-status").className = "mg-status";
    $("mg-log").hidden = true;
  }

  /* ---------------- history ---------------- */

  function escapeHtml(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  /* ---------------- rich text ---------------- */

  var RICH_TAGS = /^(P|BR|STRONG|B|EM|I|U|S|UL|OL|LI|H2|H3|H4|BLOCKQUOTE|A|TABLE|THEAD|TBODY|TR|TH|TD|HR|CODE)$/;

  function cleanHtml(html) {
    var box = document.createElement("div");
    box.innerHTML = String(html == null ? "" : html);
    Array.prototype.forEach.call(
      box.querySelectorAll("script,style,iframe,object,embed,form,input,button"),
      function (n) { n.parentNode.removeChild(n); });

    Array.prototype.slice.call(box.querySelectorAll("*")).forEach(function (n) {
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
    return raw.split(/\n{2,}/).map(function (block) {
      var text = block.trim();
      if (!text) return "";
      return "<p>" + escapeHtml(text).replace(/\n/g, "<br>") + "</p>";
    }).filter(Boolean).join("");
  }

  function buildRichEditor(value, onChange) {
    var box = el("div", "mg-rich");
    var bar = el("div", "mg-rich__bar");
    var area = el("div", "mg-rich__area");
    area.contentEditable = "true";
    area.innerHTML = richToHtml(value);

    function sync() { onChange(cleanHtml(area.innerHTML)); }

    function run(name, arg) {
      area.focus();
      document.execCommand(name, false, arg);
      sync();
    }

    // Plan A: bold, italic, paragraph, lists, link. Headings and tables were
    // dropped — product descriptions are short and the extra buttons only
    // invited mis-clicks.
    [
      ["B", "bold", null, "font-weight:700"],
      ["I", "italic", null, "font-style:italic"],
      ["Body", "formatBlock", "<p>", ""],
      ["Bullets", "insertUnorderedList", null, ""],
      ["Numbers", "insertOrderedList", null, ""],
      ["Link", "link", null, ""],
      ["Clear", "removeFormat", null, ""],
    ].forEach(function (spec) {
      var btn = el("button", null, spec[0]);
      btn.type = "button";
      btn.style.cssText = "padding:4px 9px;border:1px solid #d5dce6;border-radius:6px;" +
        "background:#fff;color:#344054;font:inherit;font-size:11.5px;cursor:pointer;" +
        (spec[3] || "");
      // Keep the caret where it is: without this the editable area loses its
      // selection when the button takes focus, and execCommand does nothing.
      btn.addEventListener("mousedown", function (e) {
        e.preventDefault();
      });
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        if (spec[1] === "link") {
          var url = window.prompt("Link address (https://…)", "https://");
          if (url && /^(https?:\/\/|mailto:|\/)/i.test(url)) run("createLink", url);
        } else {
          run(spec[1], spec[2]);
        }
      });
      bar.appendChild(btn);
    });

    area.addEventListener("input", sync);
    area.addEventListener("blur", sync);
    // keep pasted markup out of the field: insert as plain text
    area.addEventListener("paste", function (e) {
      e.preventDefault();
      var clip = (e.clipboardData || window.clipboardData);
      var text = clip ? clip.getData("text/plain") : "";
      document.execCommand("insertText", false, text);
      sync();
    });

    box.appendChild(bar);
    box.appendChild(area);
    return box;
  }

  function openHistory() {
    var old = document.getElementById("mg-history");
    if (old) { old.remove(); return; }

    var host = $("mg-edit");
    var panel = el("div");
    panel.id = "mg-history";
    panel.style.cssText = "border:1px solid #e3e8ef;border-radius:10px;padding:14px;" +
      "margin-bottom:18px;background:#fbfcfe";
    panel.innerHTML = '<p class="mg-hint" style="margin:0">Loading history…</p>';
    host.insertBefore(panel, host.firstChild);

    request("GET", "/history?kind=" + encodeURIComponent(state.kind) +
            "&id=" + encodeURIComponent(state.current)).then(function (d) {
      var rows = d.history || [];
      if (!rows.length) {
        panel.innerHTML = '<p class="mg-hint" style="margin:0">' +
          "No earlier versions — this record has only been saved once.</p>";
        return;
      }
      panel.innerHTML =
        '<p class="mg-hint" style="margin:0 0 8px">Last ' + rows.length + " changes</p>" +
        rows.map(function (r) {
          return '<div style="display:flex;gap:10px;align-items:center;padding:6px 0;' +
            'border-bottom:1px solid #eef1f6;font-size:12.5px">' +
            '<span style="color:#8b97a8;font-family:ui-monospace,monospace">' + r.sha + "</span>" +
            '<span style="color:#8b97a8;white-space:nowrap">' + r.date + "</span>" +
            '<span style="flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis">' +
            escapeHtml(r.subject) + "</span>" +
            '<button type="button" data-view="' + r.sha + '" style="padding:4px 10px;' +
            'border:1px solid #d5dce6;border-radius:6px;background:#fff;font:inherit;' +
            'font-size:12px;cursor:pointer">View</button>' +
            '<button type="button" data-restore="' + r.sha + '" style="padding:4px 10px;' +
            'border:1px solid #f0c2bd;border-radius:6px;background:#fff;color:#b42318;' +
            'font:inherit;font-size:12px;cursor:pointer">Restore</button>' +
            "</div>";
        }).join("") +
        '<pre id="mg-history-view" hidden style="margin:10px 0 0;padding:10px;' +
        'background:#fff;border:1px solid #eef1f6;border-radius:8px;' +
        'font:11.5px/1.55 ui-monospace,monospace;max-height:260px;overflow:auto;' +
        'white-space:pre-wrap"></pre>';

      panel.addEventListener("click", function (e) {
        var view = e.target.getAttribute && e.target.getAttribute("data-view");
        var restore = e.target.getAttribute && e.target.getAttribute("data-restore");
        if (view) viewRevision(view);
        if (restore) restoreRevision(restore);
      });
    }).catch(function () {
      panel.innerHTML = '<p class="mg-hint" style="margin:0">Could not load history.</p>';
    });
  }

  function viewRevision(sha) {
    request("POST", "/revision", { kind: state.kind, id: state.current, sha: sha })
      .then(function (d) {
        var box = document.getElementById("mg-history-view");
        if (!box) return;
        box.hidden = false;
        box.textContent = d.ok ? d.content : (d.error || "Could not load that version.");
      })
      .catch(function () { /* ignore */ });
  }

  function restoreRevision(sha) {
    var msg = "Replace the current version with " + sha + "?\n\n" +
      "This rewrites the file, rebuilds the site and goes live immediately.";
    if (!confirm(msg)) return;
    request("POST", "/restore", { kind: state.kind, id: state.current, sha: sha })
      .then(function (d) {
        if (!d.ok) throw new Error(d.error || "could not restore");
        var panel = document.getElementById("mg-history");
        if (panel) panel.remove();
        openItem(state.current);
        $("mg-status").textContent = "Restored " + sha + " — live now.";
        $("mg-status").className = "mg-status is-ok";
      })
      .catch(function (err) { alert(err.message || "Could not restore."); });
  }

  /* ---------------- save ---------------- */

  function collect() {
    // Start from the record itself so keys the form does not render survive a save.
    var out = JSON.parse(JSON.stringify(state.data || {}));
    var edit = $("mg-edit");

    Array.prototype.forEach.call(edit.querySelectorAll("[data-field]"), function (inp) {
      var key = inp.getAttribute("data-field");
      if (inp.getAttribute("data-kind") === "list") {
        setPath(out, key, inp.value.split("\n").map(function (s) { return s.trim(); })
          .filter(function (s) { return s.length; }));
      } else if (inp.type === "number") {
        setPath(out, key, inp.value === "" ? null : Number(inp.value));
      } else {
        setPath(out, key, inp.value);
      }
    });

    var rows = edit.querySelectorAll(".mg-variants tbody tr");
    if (rows.length) {
      out.variants = Array.prototype.map.call(rows, function (tr) {
        var get = function (k) { return tr.querySelector('[data-v="' + k + '"]').value; };
        var price = get("price");
        return {
          sku: get("sku").trim(),
          spec: get("spec").trim(),
          price: price === "" ? null : Number(price),
        };
      });
    }

    var kvRows = edit.querySelectorAll(".mg-kv .row");
    if (kvRows.length) {
      out.specs = Array.prototype.map.call(kvRows, function (row) {
        return {
          k: row.querySelector('[data-kv="k"]').value.trim(),
          v: row.querySelector('[data-kv="v"]').value.trim(),
        };
      }).filter(function (p) { return p.k || p.v; });
    }

    return out;
  }

  function save() {
    var data = collect();
    var btn = $("mg-save");
    var status = $("mg-status");
    var log = $("mg-log");

    btn.disabled = true;
    status.className = "mg-status";
    status.textContent = "Saving…";
    log.hidden = true;

    request("PUT", "/content/" + state.kind + "/" + state.current,
            { data: data, rebuild: true })
      .then(function (d) {
        if (!d.ok) throw new Error(d.error || "save failed");
        var build = d.build || {};
        if (build.ok) {
          status.className = "mg-status is-ok";
          status.textContent = "Published — live now.";
          state.dirty = false;
          loadList();
        } else {
          status.className = "mg-status is-bad";
          status.textContent = "Saved, but the build failed. The site still shows the previous version.";
          log.textContent = (build.tail || build.error || "").slice(-1200);
          log.hidden = false;
        }
      })
      .catch(function (err) {
        status.className = "mg-status is-bad";
        status.textContent = err.message || "Could not save.";
      })
      .then(function () { btn.disabled = false; });
  }

  function createNew() {
    if (state.kind === "customers") {
      alert("Customers create their own account at /register.html — they cannot be added here.");
      return;
    }
    if (state.kind === "orders") {
      alert("Orders arrive from checkout — they cannot be created here.");
      return;
    }
    var id = prompt("New id (lowercase letters, digits, hyphens):");
    if (!id) return;
    id = id.trim().toLowerCase();
    if (!/^[a-z0-9][a-z0-9-]*$/.test(id)) {
      alert("Only lowercase letters, digits and hyphens.");
      return;
    }
    var base = state.kind === "products"
      ? { order: 999, sku_code: "", slug: id, name: "", cat: "beads", apps: [],
          price: null, variants: [], sizes: [], blurb: "", desc: "",
          highlights: [], specs: [], image_tile: "", image: "", shop_product_id: null }
      : {};

    request("POST", "/content/" + state.kind, { id: id, data: base, rebuild: false })
      .then(function (d) {
        if (!d.ok) throw new Error(d.error || "could not create");
        loadList();
        state.current = id;
        state.data = base;
        state.dirty = false;
        renderForm();
      })
      .catch(function (err) { alert(err.message || "Could not create."); });
  }

  /* ---------------- boot ---------------- */

  function boot() {
    fetch("/api/me").then(function (r) { return r.json(); }).then(function (d) {
      var u = d && d.user;
      if (!u || u.role !== "admin") {
        location.href = "login.html";
        return;
      }
      $("mg-who").textContent = (u.name || u.email) + " · admin";

      // Deep link: manage.html?kind=orders&id=TL-... opens that order directly.
      var qs = new URLSearchParams(location.search);
      var wantKind = qs.get("kind");
      var wantId = qs.get("id");
      if (wantKind && TYPES.some(function (t) { return t.id === wantKind; })) {
        state.kind = wantKind;
      }
      buildTypes();
      $("mg-filters").hidden = state.kind !== "orders";
      loadList().then(function () {
        if (wantId) openItem(wantId);
      });

      $("mg-search").addEventListener("input", renderList);
      $("mg-new").addEventListener("click", createNew);
      $("mg-save").addEventListener("click", save);
      $("mg-status").addEventListener("change", function () {
        state.status = this.value;
        renderList();
      });
      $("mg-export").addEventListener("click", exportOrders);
      $("mg-batch").addEventListener("click", toggleBulk);
      $("mg-bulk-exit").addEventListener("click", toggleBulk);
      $("mg-out").addEventListener("click", function () {
        fetch("/api/logout", { method: "POST" }).then(function () {
          location.href = "index.html";
        });
      });

      window.addEventListener("beforeunload", function (e) {
        if (state.dirty) {
          e.preventDefault();
          e.returnValue = "";
        }
      });
    }).catch(function () { location.href = "login.html"; });
  }

  boot();
})();
