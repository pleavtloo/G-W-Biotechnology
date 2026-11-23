# -*- coding: utf-8 -*-
"""Static site generator for the T&L Biotechnology redesign."""
import os, json, shutil, html as H
from content import (COMPANY, CATEGORIES, APPLICATIONS, PRODUCTS, SERVICES,
                     ARTICLES, FAQ, NAV, POSITIONING, STACK, LOOP,
                     PORTFOLIO_NOW, PORTFOLIO_NEXT, AUTOMATION, NETWORK, EXPERT)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "website")
IMG = "assets/img"
NSKU = len(PRODUCTS)

# --------------------------------------------------------------------------
# icons
# --------------------------------------------------------------------------
I = {
"magnet": '<path d="M6 4v7a6 6 0 0 0 12 0V4"/><path d="M6 4h4"/><path d="M14 4h4"/><path d="M6 9h4"/><path d="M14 9h4"/>',
"antibody": '<path d="M4 3v6a4 4 0 0 0 4 4h8a4 4 0 0 1 4 4v4"/><path d="M20 3v6a4 4 0 0 1-4 4H8a4 4 0 0 0-4 4v4"/>',
"protein": '<circle cx="7" cy="8" r="2.6"/><circle cx="17" cy="7" r="2.2"/><circle cx="12" cy="16" r="3"/><path d="M9.2 9.6 10.6 13"/><path d="M15.2 8.6 13.4 13.4"/>',
"flask": '<path d="M9 3h6"/><path d="M10 3v5.5L5.6 17A2.4 2.4 0 0 0 7.7 20.5h8.6A2.4 2.4 0 0 0 18.4 17L14 8.5V3"/><path d="M7.2 14h9.6"/>',
"dna": '<path d="M7 3c0 4.5 10 4.5 10 9s-10 4.5-10 9"/><path d="M17 3c0 4.5-10 4.5-10 9s10 4.5 10 9"/><path d="M8.4 6.6h7.2"/><path d="M8.4 17.4h7.2"/><path d="M9.6 12h4.8"/>',
"beaker": '<path d="M6 3h12"/><path d="M8 3v13a4 4 0 0 0 8 0V3"/><path d="M8 11h8"/>',
"chart": '<path d="M4 20V6"/><path d="M4 20h16"/><path d="M8 17v-4"/><path d="M12 17V9"/><path d="M16 17v-7"/>',
"car": '<path d="M4 15V9a2 2 0 0 1 1.2-1.8l4-1.7h5.6l4 1.7A2 2 0 0 1 20 9v6"/><path d="M4 15h16"/><circle cx="7.5" cy="17.5" r="1.8"/><circle cx="16.5" cy="17.5" r="1.8"/>',
"arrow": '<path d="M5 12h13"/><path d="m12.5 5.5 6.5 6.5-6.5 6.5"/>',
"arrow-up-right": '<path d="M7 17 17 7"/><path d="M8 7h9v9"/>',
"search": '<circle cx="11" cy="11" r="7"/><path d="m16.5 16.5 4 4"/>',
"menu": '<path d="M3.5 7h17"/><path d="M3.5 12h17"/><path d="M3.5 17h17"/>',
"close": '<path d="M6 6l12 12"/><path d="M18 6 6 18"/>',
"check": '<path d="M4.5 12.5 9 17l10.5-10.5"/>',
"shield": '<path d="M12 3 5 6v6c0 4.2 3 7.6 7 9 4-1.4 7-4.8 7-9V6l-7-3Z"/><path d="m9 12 2.2 2.2L15.5 10"/>',
"doc": '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8l-5-5Z"/><path d="M14 3v5h5"/><path d="M9 13h6"/><path d="M9 17h4"/>',
"download": '<path d="M12 4v10"/><path d="m8 11 4 4 4-4"/><path d="M5 19h14"/>',
"phone": '<path d="M6.5 3.5h3l1.5 4-2 1.5a11 11 0 0 0 5 5l1.5-2 4 1.5v3a2 2 0 0 1-2.2 2A16.5 16.5 0 0 1 4.5 5.7 2 2 0 0 1 6.5 3.5Z"/>',
"mail": '<rect x="3" y="5.5" width="18" height="13" rx="2"/><path d="m3.5 7 8.5 6 8.5-6"/>',
"pin": '<path d="M12 21s7-5.5 7-11a7 7 0 1 0-14 0c0 5.5 7 11 7 11Z"/><circle cx="12" cy="10" r="2.6"/>',
"globe": '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17"/><path d="M12 3.5c2.4 2.4 3.6 5.4 3.6 8.5S14.4 18.1 12 20.5c-2.4-2.4-3.6-5.4-3.6-8.5S9.6 5.9 12 3.5Z"/>',
"chev": '<path d="m9 5 7 7-7 7"/>',
"plus": '<path d="M12 5v14"/><path d="M5 12h14"/>',
"clock": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 1.8"/>',
"users": '<circle cx="9" cy="8.5" r="3.2"/><path d="M3.5 20c.6-3.2 2.8-5 5.5-5s4.9 1.8 5.5 5"/><path d="M16 5.6a3.2 3.2 0 0 1 0 6"/><path d="M17.5 15.4c1.7.5 2.8 2 3.1 4.1"/>',
"factory": '<path d="M3.5 20.5V9.5l5 3V9.5l5 3V6.5l7-2v16Z"/><path d="M3.5 20.5h17"/><path d="M8 17h2"/><path d="M14 17h2"/>',
"award": '<circle cx="12" cy="9" r="5.5"/><path d="m8.5 13.6-1 7 4.5-2.4 4.5 2.4-1-7"/>',
"lock": '<rect x="4.5" y="10.5" width="15" height="10" rx="2"/><path d="M8 10.5V8a4 4 0 0 1 8 0v2.5"/>',
"layers": '<path d="m12 3 8.5 4.5L12 12 3.5 7.5 12 3Z"/><path d="m4 12 8 4.3 8-4.3"/><path d="m4 16.5 8 4.3 8-4.3"/>',
"grid": '<rect x="3.5" y="3.5" width="7" height="7" rx="1.5"/><rect x="13.5" y="3.5" width="7" height="7" rx="1.5"/><rect x="3.5" y="13.5" width="7" height="7" rx="1.5"/><rect x="13.5" y="13.5" width="7" height="7" rx="1.5"/>',
"spark": '<path d="M12 3v4"/><path d="M12 17v4"/><path d="M3 12h4"/><path d="M17 12h4"/><path d="m6 6 2.5 2.5"/><path d="m15.5 15.5 2.5 2.5"/><path d="m18 6-2.5 2.5"/><path d="m8.5 15.5-2.5 2.5"/>',
"scale": '<path d="M12 3.5v17"/><path d="M6 20.5h12"/><path d="M4 8h16"/><path d="m4 8-2 5a3.2 3.2 0 0 0 6 0L6 8"/><path d="m18 8-2 5a3.2 3.2 0 0 0 6 0l-2-5"/>',
"refresh": '<path d="M20 12a8 8 0 1 1-2.6-5.9"/><path d="M20 4.5V10h-5.4"/>',
}


def ic(name, cls="", sw="1.7"):
    p = I.get(name, "")
    return ('<svg class="%s" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="%s" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg>'
            % (cls, sw, p))


def e(s):
    # normalise so pre-escaped entities are not double-escaped
    return H.escape(H.unescape(str(s)), quote=True)


def money(v):
    return "${:,}".format(v) if v else "Quote"


def prod(slug):
    for p in PRODUCTS:
        if p["slug"] == slug:
            return p
    raise KeyError(slug)


# --------------------------------------------------------------------------
# chrome
# --------------------------------------------------------------------------
def head(title, desc, page, extra=""):
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="icon" type="image/png" href="assets/img/brand/favicon.png">
<link rel="stylesheet" href="assets/css/style.css">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
{extra}
</head>
<body data-page="{page}">
<a class="skip" href="#main" style="position:absolute;left:-9999px">Skip to content</a>
""".format(title=e(title), desc=e(desc), page=page, extra=extra)


def mega_products():
    cats = "".join(
        '<a class="mega__link" href="products.html?cat={cid}">'
        '<span class="mega__ico">{ico}</span><span><span class="mega__name">{name}</span>'
        '<span class="mega__desc">{desc}</span></span></a>'.format(
            cid=c["id"], ico=ic(c["icon"]), name=e(c["name"]),
            desc=e(c["tag"]))
        for c in CATEGORIES)
    apps = "".join(
        '<a class="mega__link" href="applications.html#{aid}">'
        '<span class="mega__ico">{ico}</span><span><span class="mega__name">{name}</span>'
        '<span class="mega__desc">{n} catalogue products</span></span></a>'.format(
            aid=a["id"], ico=ic("layers"), name=e(a["name"]), n=a["count"])
        for a in APPLICATIONS)
    return """
<div class="mega mega--wide">
  <div>
    <div class="mega__col-title">By product family</div>
    <div class="mega__list">{cats}</div>
  </div>
  <div>
    <div class="mega__col-title">By application</div>
    <div class="mega__list">{apps}</div>
  </div>
  <div class="mega__promo">
    <div>
      <h4>Built on validated tool families</h4>
      <p>{n} catalogue products today, with nucleic acid extraction, purification and antibody discovery next.</p>
    </div>
    <a class="link-arrow" href="products.html">See the full portfolio {ar}</a>
  </div>
</div>""".format(cats=cats, apps=apps, ar=ic("arrow"), n=NSKU)


def mega_platform():
    items = "".join(
        '<a class="mega__link" href="platform.html#{n}">'
        '<span class="mega__ico">{ico}</span><span><span class="mega__name">{t}</span>'
        '<span class="mega__desc">{m}</span></span></a>'.format(
            n=layer["n"], ico=ic(["layers", "spark", "flask", "grid"][i]),
            t=e(layer["k"] + " — " + layer["title"]), m=e(layer["meta"]))
        for i, layer in enumerate(STACK))
    return """
<div class="mega">
  <div>
    <div class="mega__col-title">The four-layer stack</div>
    <div class="mega__list">{items}</div>
  </div>
  <div class="mega__promo">
    <div>
      <h4>AI plans the run. The bench runs it.</h4>
      <p>Models propose the construct, the host and the conditions; the lab executes and returns the data.</p>
    </div>
    <a class="link-arrow" href="platform.html">How the platform works {ar}</a>
  </div>
</div>""".format(items=items, ar=ic("arrow"))


def mega_services():
    links = [("services.html#custom", "Custom development", "Beads, proteins, gene editing, formulation"),
             ("services.html#automation", "Lab automation", "High-throughput capability, phased"),
             ("services.html#network", "Capacity network", "One order, routed across qualified labs"),
             ("services.html#experts", "Application science", "Protocol review with a named scientist")]
    items = "".join(
        '<a class="mega__link" href="{h}"><span class="mega__ico">{i}</span>'
        '<span><span class="mega__name">{n}</span><span class="mega__desc">{d}</span></span></a>'.format(
            h=h, i=ic("arrow-up-right"), n=e(n), d=e(d)) for h, n, d in links)
    return """
<div class="mega">
  <div>
    <div class="mega__col-title">Service lines</div>
    <div class="mega__list">{items}</div>
  </div>
  <div class="mega__promo">
    <div>
      <h4>Automation is the roadmap, not the claim.</h4>
      <p>Manual and expert-led today, semi-automated next, high-throughput through the network after that.</p>
    </div>
    <a class="link-arrow" href="services.html#automation">See the roadmap {ar}</a>
  </div>
</div>""".format(items=items, ar=ic("arrow"))


def mega_apps():
    items = "".join(
        '<a class="mega__link" href="applications.html#{aid}">'
        '<span class="mega__ico">{ico}</span><span><span class="mega__name">{name}</span>'
        '<span class="mega__desc">{pill}</span></span></a>'.format(
            aid=a["id"], ico=ic("layers"), name=e(a["name"]), pill=e(a["pill"]))
        for a in APPLICATIONS)
    return """
<div class="mega">
  <div>
    <div class="mega__col-title">Cell therapy applications</div>
    <div class="mega__list">{items}</div>
  </div>
  <div class="mega__promo">
    <div>
      <h4>Start from your workflow, not our catalogue</h4>
      <p>Map isolate → activate → expand → engineer, and see exactly which reagent sits at each step.</p>
    </div>
    <a class="link-arrow" href="index.html#workflow">See the workflow {ar}</a>
  </div>
</div>""".format(items=items, ar=ic("arrow"))


def mega_company():
    links = [("about.html", "About T&amp;L", "Facility, team and history"),
             ("quality.html", "Quality &amp; Regulatory", "ISO, GMP and DMF filings"),
             ("services.html", "Custom Services", "Beads, proteins, gene editing"),
             ("partners.html", "Partners", "Distribution, OEM and referrals"),
             ("resources.html", "Resources", "COA lookup and technical notes"),
             ("contact.html", "Contact", "Offices, distributors, support"),
             ("about.html#careers", "Careers", "Open positions")]
    items = "".join(
        '<a class="mega__link" href="{h}"><span class="mega__ico">{i}</span>'
        '<span><span class="mega__name">{n}</span><span class="mega__desc">{d}</span></span></a>'.format(
            h=h, i=ic("arrow-up-right"), n=n, d=d) for h, n, d in links)
    return """
<div class="mega">
  <div>
    <div class="mega__col-title">Company</div>
    <div class="mega__list">{items}</div>
  </div>
  <div class="mega__promo">
    <div>
      <h4>Established 2011 · 3,200 m² R&amp;D and GMP base</h4>
      <p>Half of the company works in R&amp;D and production. That is where the lot-to-lot consistency comes from.</p>
    </div>
    <a class="link-arrow" href="about.html">Inside the facility {ar}</a>
  </div>
</div>""".format(items=items, ar=ic("arrow"))


def header(active):
    megas = {"platform": mega_platform(), "products": mega_products(),
             "applications": mega_apps(), "services": mega_services(),
             "company": mega_company()}
    lis = []
    for n in NAV:
        cls = "nav__item"
        if n["label"] == active:
            cls += " is-active-item"
        link_cls = "nav__link" + (" is-active" if n["label"] == active else "")
        if n["mega"]:
            lis.append(
                '<div class="{cls}" data-mega><a class="{lc}" href="{h}" aria-expanded="false">'
                '{l}{caret}</a>{mega}</div>'.format(
                    cls=cls, lc=link_cls, h=n["href"], l=e(n["label"]),
                    caret='<svg class="nav__caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="m6 9 6 6 6-6"/></svg>',
                    mega=megas[n["mega"]]))
        else:
            lis.append('<div class="{cls}"><a class="{lc}" href="{h}">{l}</a></div>'.format(
                cls=cls, lc=link_cls, h=n["href"], l=e(n["label"])))

    return """
<div class="topbar">
  <div class="container topbar__inner">
    <div class="topbar__note"><span class="topbar__dot"></span>
      AI-designed tools · validated in a 3,200 m² lab · ISO 13485 &amp; ISO 9001 certified</div>
    <div class="topbar__links">
      <a href="platform.html">Platform</a>
      <a href="resources.html#coa">COA lookup</a>
      <a href="contact.html">+1 442 944 9891</a>
    </div>
  </div>
</div>
<header class="header" id="header">
  <div class="container nav">
    <a class="brand" href="index.html" aria-label="T&amp;L Biotechnology — home">
      <img src="assets/img/brand/logo-mark.png" alt="">
      <span class="brand__tag"><b>Biotechnology</b><span>AI for science</span></span>
    </a>
    <nav class="nav__menu" aria-label="Primary">{lis}</nav>
    <div class="nav__actions">
      <button class="search-trigger" id="search-open" aria-label="Search products" aria-haspopup="dialog">
        {search}
        <span class="search-trigger__txt">Search {nsku} products</span>
        <kbd>⌘K</kbd>
      </button>
      <a class="btn btn--sm" href="contact.html#quote">Request a quote</a>
      <button class="icon-btn nav__toggle" id="nav-toggle" aria-label="Menu"
              aria-expanded="false" aria-controls="mobile-menu">
        <span class="i-menu">{menu}</span><span class="i-close">{close}</span>
      </button>
    </div>
  </div>
</header>
<div class="mobile-menu" id="mobile-menu">
  <button class="mm-search" id="mm-search" type="button">
    {search}<span>Search {nsku} products, targets, documents</span>
  </button>
  <nav aria-label="Mobile">
    {mlinks}
  </nav>
  <div class="mobile-menu__cta">
    <a class="btn btn--block" href="contact.html#quote">Request a quote</a>
  </div>
  <div class="mobile-menu__meta">
    <a href="resources.html#coa">COA lookup</a>
    <a href="quality.html">Quality &amp; regulatory</a>
    <a href="tel:{phone}">{phonetext}</a>
  </div>
</div>
<div class="search-pop" id="search-pop" role="dialog" aria-modal="true" aria-label="Search">
  <div class="search-pop__box">
    <div class="search-pop__field">
      {search}
      <input type="search" id="search-input" placeholder="Search products, targets or applications…" autocomplete="off">
      <kbd>ESC</kbd>
    </div>
    <div class="search-pop__results" id="search-results"></div>
    <div class="search-pop__hint">Try <b>CD3</b>, <b>IL-15</b>, <b>NK kit</b> or <b>DMF</b></div>
  </div>
</div>
""".format(lis="".join(lis), search=ic("search"), menu=ic("menu"), close=ic("close"),
           nsku=NSKU,
           mlinks="".join('<a class="mm-link" href="%s">%s</a>' % (n["href"], e(n["label"]))
                          for n in NAV),
           phone=COMPANY["phone_raw"], phonetext=COMPANY["phone"])


def footer():
    cats = "".join('<li><a href="products.html?cat={c}">{n}</a></li>'.format(
        c=c["id"], n=e(c["name"])) for c in CATEGORIES)
    apps = "".join('<li><a href="applications.html#{i}">{n}</a></li>'.format(
        i=a["id"], n=e(a["name"])) for a in APPLICATIONS)
    return """
<footer class="footer">
  <div class="container">
    <div class="footer__main">
      <div class="footer__brand">
        <img src="assets/img/brand/logo-color.png" alt="T&amp;L Biotechnology" style="height:42px">
        <p>An AI-native life science tool stack — reagents designed in silico, validated at the
           bench, and delivered through a network of qualified laboratories.</p>
        <div class="footer__badges">
          <span>ISO 13485:2016</span><span>ISO 9001</span><span>FDA DMF 038124</span><span>FDA DMF 038820</span>
        </div>
      </div>
      <div class="footer__col">
        <h4>Platform</h4>
        <ul>
          <li><a href="platform.html">AI for science</a></li>
          <li><a href="products.html">Products</a></li>
          <li><a href="services.html#automation">Lab automation</a></li>
          <li><a href="services.html#network">Capacity network</a></li>
          <li><a href="services.html#experts">Application science</a></li>
          <li><a href="quality.html">Quality &amp; regulatory</a></li>
        </ul>
      </div>
      <div class="footer__col">
        <h4>Applications</h4>
        <ul>{apps}</ul>
      </div>
      <div class="footer__col">
        <h4>Company</h4>
        <ul>
          <li><a href="about.html">About T&amp;L</a></li>
          <li><a href="partners.html">Partners</a></li>
          <li><a href="resources.html">Resources</a></li>
          <li><a href="resources.html#coa">COA lookup</a></li>
          <li><a href="contact.html">Contact</a></li>
          <li><a href="about.html#careers">Careers</a></li>
        </ul>
      </div>
    </div>
    <div class="footer__offices">
      <div class="office">{pin}<div><b>United States</b>
        <p>6076 Corte Del Cedro, Carlsbad, CA 92011<br>
        Tel +1 442 944 9891 · Mon–Fri, 9:00–17:00 PT</p></div></div>
      <div class="office">{factory}<div><b>Manufacturing &amp; R&amp;D</b>
        <p>3,200 m² GMP cleanroom and R&amp;D laboratory<br>
        Bead, protein and serum-free medium platforms</p></div></div>
    </div>
    <div class="footer__legal">
      <span>© 2026 T&amp;L Biotechnology Ltd. All rights reserved. For research use or further
        manufacturing use only.</span>
      <span class="footer__legal-links">
        <a href="contact.html">Contact</a>
        <a href="resources.html#faq">FAQ</a>
        <a href="#">Privacy policy</a>
        <a href="#">Terms of sale</a>
      </span>
    </div>
  </div>
</footer>
<div class="ai-widget" id="ai-widget">
  <button class="ai-launch" id="ai-launch" aria-expanded="false" aria-controls="ai-panel">
    <span class="ai-launch__av"><img src="assets/img/avatar/avatar-b1.jpg" alt=""></span>
    <span class="ai-launch__dot"></span>
    <span class="ai-launch__label">Ask T&amp;L AI</span>
  </button>

  <div class="ai-panel" id="ai-panel" role="dialog" aria-modal="false" aria-label="T&amp;L application AI">
    <div class="ai-panel__head">
      <span class="ai-panel__av"><img src="assets/img/avatar/avatar-b1.jpg" alt=""></span>
      <div class="ai-panel__id">
        <div class="ai-panel__name">T&amp;L Application AI</div>
        <div class="ai-panel__status"><i></i>Online · expression design · 42 products</div>
      </div>
      <div class="ai-panel__acts">
        <button type="button" id="ai-presence-btn" title="Digital human view" aria-label="Digital human view">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M4 9V5.5A1.5 1.5 0 0 1 5.5 4H9"/><path d="M15 4h3.5A1.5 1.5 0 0 1 20 5.5V9"/><path d="M20 15v3.5a1.5 1.5 0 0 1-1.5 1.5H15"/><path d="M9 20H5.5A1.5 1.5 0 0 1 4 18.5V15"/></svg>
        </button>
        <button type="button" id="ai-close" title="Close" aria-label="Close">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6 6 18"/></svg>
        </button>
      </div>
    </div>

    <div class="ai-presence" id="ai-presence">
      <div class="ai-presence__cap">
        <span class="ai-wave"><i></i><i></i><i></i><i></i><i></i></span>
        <span id="ai-caption">Describe a target and a constraint — I will propose a construct, a host and a bench plan.</span>
      </div>
    </div>

    <div class="ai-body" id="ai-body">
      <div class="ai-msg">
        <span class="ai-msg__av"><img src="assets/img/avatar/avatar-b1.jpg" alt=""></span>
        <div class="ai-bubble" id="ai-greeting">Tell me what you need to express — the target, the yield you need, and your timeline. I can propose a construct and a bench plan.</div>
      </div>
      <div class="ai-chips" id="ai-chips">
        <button type="button" class="ai-chip">Design a construct for a 45 kDa target</button>
        <button type="button" class="ai-chip">Which host for a disulfide-rich domain?</button>
        <button type="button" class="ai-chip">Plan a 24-condition screen</button>
      </div>
    </div>

    <form class="ai-input" id="ai-form">
      <input type="text" id="ai-text" placeholder="Describe a target, a yield, a constraint…" aria-label="Your question" autocomplete="off">
      <button type="button" class="ai-input__mic" title="Voice input" aria-label="Voice input">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0"/><path d="M12 18v3"/></svg>
      </button>
      <button type="submit" aria-label="Send">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h15"/><path d="m13 6 6 6-6 6"/></svg>
      </button>
    </form>

    <div class="ai-foot">
      <span>AI-generated · verify before use</span>
      <a href="contact.html#quote">Talk to a human scientist
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M5 12h13"/><path d="m12 5 7 7-7 7"/></svg>
      </a>
    </div>
  </div>
</div>
<script src="assets/js/data.js"></script>
<script src="assets/js/main.js"></script>
</body>
</html>
""".format(cats=cats, apps=apps, pin=ic("pin"), factory=ic("factory"))


# --------------------------------------------------------------------------
# components
# --------------------------------------------------------------------------
def section_head(eyebrow, title, desc="", link=None, link_text="View all", num=""):
    l = ('<a class="link-arrow" href="%s">%s %s</a>' % (link, e(link_text), ic("arrow"))) if link else ""
    n = '<span class="eyebrow__num">%s</span>' % num if num else ""
    return """
<div class="section-head reveal">
  <div class="section-head__text">
    <div class="eyebrow">{n}{eb}</div>
    <h2>{t}</h2>
    {d}
  </div>
  {l}
</div>""".format(n=n, eb=e(eyebrow), t=title, d='<p>%s</p>' % e(desc) if desc else "", l=l)


def pcard(cat):
    idx = [c["id"] for c in CATEGORIES].index(cat["id"]) + 1
    return """
<a class="pcard pcard--{cid} reveal" href="products.html?cat={cid}">
  <div class="pcard__media">
    <img src="{img}" alt="{alt}" loading="lazy">
    <span class="pcard__idx">{idx:02d}</span>
    <span class="pcard__ico">{ico}</span>
  </div>
  <div class="pcard__body">
    <div class="pcard__kicker">{kicker}</div>
    <div class="pcard__title">{name}</div>
    <div class="pcard__desc">{blurb}</div>
    <div class="pcard__foot">
      <span class="pcard__count">{n} products</span>
      <span class="pcard__arrow">{ar}</span>
    </div>
  </div>
</a>""".format(cid=cat["id"], img=IMG + "/products/" + cat["img"] + "-tile.webp",
               alt=e(cat["name"]), kicker=e(cat["short"]), name=e(cat["name"]),
               blurb=e(cat["blurb"]), n=sum(1 for p in PRODUCTS if p["cat"] == cat["id"]),
               idx=idx, ico=ic(cat["icon"]), ar=ic("arrow"))


FEATURED = ["actsep-cd3-cd28", "maxsortin-cd3", "cd3-mab", "il2", "il7", "nk-kit-30"]


def fcard(slug):
    p = prod(slug)
    cat = next(c for c in CATEGORIES if c["id"] == p["cat"])
    if p["price"]:
        price = 'From %s <i>/ %s</i>' % (money(p["price"]), e(p["sizes"][0]))
    else:
        price = "Price on request"
    return """
<a class="fcard fcard--{cat}" href="product.html?p={slug}">
  <div class="fcard__media">
    <img src="{img}" alt="{name}" loading="lazy">
    <span class="fcard__cat">{kicker}</span>
  </div>
  <div class="fcard__body">
    <div class="fcard__name">{name}</div>
    <div class="fcard__foot">
      <span class="fcard__price">{price}</span>
      <span class="fcard__arrow">{ar}</span>
    </div>
  </div>
</a>""".format(cat=p["cat"], slug=p["slug"], img=IMG + "/products/" + p["slug"] + "-tile.webp",
               name=e(p["name"]), kicker=e(cat["short"]), price=price, ar=ic("arrow"))


def gcard(p):
    cat = next(c for c in CATEGORIES if c["id"] == p["cat"])
    price = ('<div class="gcard__price">%s <span>/ %s</span></div>' % (money(p["price"]), e(p["sizes"][0]))) \
        if p["price"] else '<div class="gcard__price"><span>Price on request</span></div>'
    return """
<article class="gcard" data-cat="{cat}" data-apps="{apps}" data-name="{name}"
         data-price="{pv}" data-slug="{slug}">
  <div class="gcard__media-wrap">
    <a class="gcard__media" href="product.html?p={slug}">
      <img src="{img}" alt="{name}" loading="lazy">
      <span class="gcard__tag">{kicker}</span>
    </a>
    <a class="gcard__dl" href="docs/datasheet-{slug}.pdf" download
       title="Technical datasheet (PDF)" aria-label="Download datasheet">{doc}</a>
  </div>
  <div class="gcard__body">
    <a class="gcard__name" href="product.html?p={slug}">{name}</a>
    <p class="gcard__desc">{blurb}</p>
    <div class="gcard__foot">
      {price}
      <div class="gcard__actions">
        <a class="mini-btn" href="docs/coa-{slug}.pdf" download
           title="Certificate of analysis (PDF)">COA</a>
        <a class="mini-btn mini-btn--primary" href="contact.html?p={slug}#quote">Quote</a>
      </div>
    </div>
  </div>
</article>""".format(cat=p["cat"], apps=",".join(p["apps"]), name=e(p["name"]),
                     pv=p["price"] or 0, slug=p["slug"], img=IMG + "/products/" + p["slug"] + "-tile.webp",
                     kicker=e(cat["short"]), blurb=e(p["blurb"]), price=price,
                     doc=ic("doc"))


def mini_prod(slug):
    p = prod(slug)
    return """
<a class="mini-prod" href="product.html?p={s}">
  <img src="{img}" alt="{n}" loading="lazy">
  <div><div class="mini-prod__t">{n}</div><div class="mini-prod__s">{b}</div></div>
</a>""".format(s=slug, img=IMG + "/products/" + slug + "-tile.webp", n=e(p["name"]),
               b=e(p["blurb"][:58] + ("…" if len(p["blurb"]) > 58 else "")))


# --------------------------------------------------------------------------
# page: home
# --------------------------------------------------------------------------
def page_home():
    flow = [
        ("01", "Isolate", "CD3, CD4, CD8, CD14 and TCRαβ selection from 50 nm nanobeads.", "products.html?cat=beads", "magnet"),
        ("02", "Activate", "CD3/CD28 beads or bead-free ActCel reagent for signal 1 + 2.", "product.html?p=actsep-cd3-cd28", "spark"),
        ("03", "Expand", "IL-2, IL-7, IL-15, IL-21 and serum-free expansion kits.", "products.html?cat=proteins", "protein"),
        ("04", "Engineer", "Low-endotoxin reagents for viral and non-viral gene delivery.", "services.html", "dna"),
        ("05", "Release", "Cryopreservation, COA and lot traceability for release testing.", "quality.html", "shield"),
    ]
    flow_html = "".join("""
    <div class="flow__step">
      <div class="flow__rail"></div>
      <div class="flow__head"><span class="flow__ico">{ico}</span><span class="flow__num">{n}</span></div>
      <div class="flow__title">{t}</div>
      <p class="flow__desc">{d}</p>
      <a class="flow__link" href="{h}">Explore {ar}</a>
    </div>""".format(ico=ic(i), n=n, t=e(t), d=e(d), h=h, ar=ic("arrow")) for n, t, d, h, i in flow)

    trust = [
        ("shield", "ISO 13485:2016", "Medical-device quality system applied to CGT reagents"),
        ("doc", "FDA DMF 038124 / 038820", "Type II filings sponsors can reference in an IND"),
        ("scale", "3,200 m² GMP base", "Bead, protein and medium platforms under one roof"),
        ("users", "30+ customer audits", "Audit data packages and on-site inspection support"),
    ]
    trust_html = "".join("""
    <div class="trust__item">{ico}<div><div class="trust__k">{k}</div><div class="trust__v">{v}</div></div></div>
    """.format(ico=ic(i), k=e(k), v=e(v)) for i, k, v in trust)

    # applications tab panels
    tabs = "".join("""
    <button class="apps__tab{act}" data-tab="{aid}">{name}<span>{n}</span></button>
    """.format(act=" is-active" if i == 0 else "", aid=a["id"], name=e(a["name"]), n=a["count"])
        for i, a in enumerate(APPLICATIONS))

    panels = "".join("""
    <div class="apps__panel" data-panel="{aid}"{hide}>
      <div class="apps__panel-head">
        <div><h3>{title}</h3><p>{desc}</p></div>
        <span class="apps__pill">{pill}</span>
      </div>
      <div class="apps__steps">{steps}</div>
      <div class="apps__products">{prods}</div>
      <div style="margin-top:22px"><a class="link-arrow" href="applications.html#{aid}">
        Full {name} workflow {ar}</a></div>
    </div>""".format(
        aid=a["id"], hide="" if i == 0 else ' style="display:none"', title=e(a["title"]),
        desc=e(a["desc"]), pill=e(a["pill"]),
        steps="".join('<div class="apps__step"><b>%s</b><span>%s</span></div>' % (e(s[0]), e(s[1]))
                      for s in a["steps"]),
        prods="".join(mini_prod(s) for s in a["products"]),
        name=e(a["name"]), ar=ic("arrow"))
        for i, a in enumerate(APPLICATIONS))

    svc = "".join("""
    <div class="svc__card reveal">
      <span class="svc__idx">{idx:02d}</span>
      <div class="svc__ico">{ico}</div>
      <h3>{t}</h3>
      <p>{d}</p>
      <div class="svc__tags">{tags}</div>
    </div>""".format(ico=ic(s["icon"]), t=e(s["title"]), d=e(s["desc"]), idx=i + 1,
                     tags="".join("<span>%s</span>" % e(t) for t in s["tags"]))
        for i, s in enumerate(SERVICES[:3]))

    res = "".join("""
    <a class="res__card reveal" href="resources.html">
      <div class="res__media"><img src="{img}" alt="" loading="lazy">
        <span class="res__media-tag">{tag}</span></div>
      <div class="res__body">
        <span class="res__date">{date}</span>
        <h3>{title}</h3>
        <p>{ex}</p>
        <span class="res__link link-arrow">Read {ar}</span>
      </div>
    </a>""".format(img=IMG + "/brand/" + a["img"] + ".webp", tag=e(a["tag"]),
                    date=e(a["date"]), title=e(a["title"]), ex=e(a["excerpt"]),
                    ar=ic("arrow")) for a in ARTICLES)

    body = """
<main id="main">
<section class="hero">
  <div class="hero__grid-bg"></div>
  <span class="hero__blob hero__blob--a"></span>
  <span class="hero__blob hero__blob--b"></span>
  <div class="container hero__inner">
    <div class="hero__copy">
      <div class="hero__badge"><b>FDA DMF filed</b> Two Type II filings on record</div>
      <h1>Raw materials that survive <em>regulatory review</em>.</h1>
      <p class="hero__lede">GMP-grade magnetic beads, monoclonal antibodies, recombinant proteins and
        serum-free media for cell and gene therapy — supplied with the DMF references, COAs and
        audit package your CMC team will be asked for.</p>
      <div class="hero__cta">
        <a class="btn" href="products.html">Explore the catalogue {ar}</a>
        <a class="btn btn--ghost" href="contact.html#quote">Talk to a scientist</a>
      </div>
      <div class="hero__proof">
        <span>{ck} ISO 13485 &amp; ISO 9001</span>
        <span>{ck} DMF 038124 · 038820</span>
        <span>{ck} GMP &amp; RUO grades</span>
      </div>
    </div>
    <div class="hero__visual">
      <div class="stage">
        <div class="stage__rings"><span class="stage__ring"></span><span class="stage__ring"></span><span class="stage__ring"></span></div>
        <img class="stage__product" src="{pimg}" alt="ActSep CD3/CD28 separation and activation beads">
      </div>
      <div class="chip-float chip-float--a">
        <span class="chip-float__ico">{shield}</span>
        <div><div class="chip-float__k">Quality system</div><div class="chip-float__v">ISO 13485:2016</div></div>
      </div>
      <div class="chip-float chip-float--b">
        <span class="chip-float__ico">{scale}</span>
        <div><div class="chip-float__k">Facility</div><div class="chip-float__v">3,200 m² GMP</div></div>
      </div>
      <div class="chip-float chip-float--c">
        <span class="chip-float__ico">{clock}</span>
        <div><div class="chip-float__k">DMF</div><div class="chip-float__v">038124 / 038820</div></div>
      </div>
      <a class="stage-card" href="product.html?p=nk-kit-30">
        <img src="{nkimg}" alt="">
        <div><span>Also in the portfolio</span><b>AMMS® NK Cell Culture Kit 3.0</b></div>
      </a>
    </div>
  </div>
</section>

<section class="trust">
  <div class="container">
    <div class="trust__inner">{trust}</div>
  </div>
</section>

<section class="section section--tint" id="workflow">
  <div class="container">
    {head_flow}
    <div class="flow" id="flow">{flow}</div>
  </div>
</section>

<section class="section section--mist">
  <div class="container">
    {head_port}
    <div class="cards-4">{cards}</div>
  </div>
</section>

<section class="section section--ink ai-band" id="ai">
  <div class="container">
    <div class="section-head reveal">
      <div class="section-head__text">
        <div class="eyebrow"><span class="eyebrow__num">03</span>AI in the loop</div>
        <h2>AI designs the experiment. The bench proves it.</h2>
        <p>Send a target sequence and a constraint — yield, solubility, timeline. Models propose the
          construct, the host and the induction conditions; our lab runs the matrix and returns the
          data. What fails becomes the input for the next round.</p>
      </div>
      <a class="link-arrow" href="platform.html#02">How expression design works {ar}</a>
    </div>
    <div class="aiband">
      <div class="aiband__item"><span>01</span><b>Design</b><p>Codon-optimised, host-matched construct — not a catalogue default</p></div>
      <div class="aiband__item"><span>02</span><b>Predict</b><p>Solubility and yield ranked before anything is synthesised</p></div>
      <div class="aiband__item"><span>03</span><b>Test</b><p>24–96 condition matrix in one bench run, titre and soluble fraction</p></div>
      <div class="aiband__item"><span>04</span><b>Learn</b><p>Every result, including failures, updates the next design</p></div>
    </div>
    <div class="aiband__foot">
      <span class="aiband__ask">Describe a target to the T&amp;L AI — bottom right, any page</span>
      <a class="btn btn--light btn--sm" href="contact.html#quote">Start an expression design {ar}</a>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    {head_apps}
    <div class="apps">
      <div class="apps__tabs" role="tablist">{tabs}</div>
      <div class="apps__panels">{panels}</div>
    </div>
  </div>
</section>

<section class="section section--ink">
  <div class="container">
    <div class="section-head reveal">
      <div class="section-head__text">
        <div class="eyebrow">Quality by documentation</div>
        <h2>The paperwork is the product.</h2>
        <p>Any supplier can ship a vial. What decides whether your IND moves is whether the
          reagent has a filing, a batch record and an audit trail behind it.</p>
      </div>
      <a class="link-arrow" href="quality.html">Quality &amp; regulatory {ar}</a>
    </div>
    <div class="stats">
      <div class="stat"><div class="stat__n" data-count="3200">3,200<small> m²</small></div>
        <div class="stat__l">R&amp;D laboratory and GMP cleanroom</div></div>
      <div class="stat"><div class="stat__n" data-count="15">15<small>+ yrs</small></div>
        <div class="stat__l">CGT reagent development experience</div></div>
      <div class="stat"><div class="stat__n" data-count="50">50<small>%</small></div>
        <div class="stat__l">Of staff in R&amp;D and production</div></div>
      <div class="stat"><div class="stat__n" data-count="30">30<small>+</small></div>
        <div class="stat__l">Customer audits supported</div></div>
    </div>
    <div class="dmf">
      <div class="dmf__card">
        <div><div class="dmf__k">Type II Drug Master File</div>
          <div class="dmf__v">ActSep® CD3/CD28 separation &amp; activation beads</div></div>
        <div class="dmf__no">038124</div>
      </div>
      <div class="dmf__card">
        <div><div class="dmf__k">Type II Drug Master File</div>
          <div class="dmf__v">Anti-human CD28 monoclonal antibody</div></div>
        <div class="dmf__no">038820</div>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    {head_svc}
    <div class="svc">{svc}</div>
    <div style="margin-top:32px"><a class="btn btn--ghost" href="services.html">
      All custom services {ar}</a></div>
  </div>
</section>

<section class="section section--mist">
  <div class="container">
    {head_res}
    <div class="res">{res}</div>
  </div>
</section>

<section class="section section--tight">
  <div class="container">
    <div class="cta-band reveal">
      <div>
        <h2>Send us your spec. We will send back a protocol.</h2>
        <p>Tell us the cell type, scale and grade you are working at. A technical specialist
          replies within one business day — with the datasheet, the DMF letter of authorisation
          if relevant, and a quote.</p>
      </div>
      <form class="cta-band__form" data-form="lead">
        <div class="field-row">
          <input type="email" required placeholder="Work email address" aria-label="Work email">
          <button class="btn btn--light" type="submit">Request</button>
        </div>
        <div class="cta-band__note">We reply from a named scientist, not a ticketing queue.
          No newsletters unless you ask.</div>
        <div class="form-ok" data-ok>{ck} Thanks — check your inbox for a reply within one business day.</div>
      </form>
    </div>
  </div>
</section>
</main>
""".format(ar=ic("arrow"), ck=ic("check"), shield=ic("shield"), scale=ic("scale"),
           clock=ic("clock"), pimg=IMG + "/products/actsep-cd3-cd28-tile.webp",
           nkimg=IMG + "/products/nk-kit-30-tile.webp",
           trust=trust_html, flow=flow_html,
           head_flow=section_head("Process fit", "Five steps. One supplier for each of them.",
                                  "Most process failures trace back to a reagent change halfway through development. Build the whole chain from one qualified source and the tech transfer gets shorter.", num="01"),
           head_port=section_head("Product families", "Four platforms, one quality system.",
                                  "Beads, antibodies, proteins and media are developed in-house, so a change in one does not invalidate the others.",
                                  "products.html", "Browse all %d products" % NSKU, num="02"),
           cards="".join(pcard(c) for c in CATEGORIES),
           head_apps=section_head("By application", "Built for the cell type you are manufacturing.",
                                  "Each application page maps the workflow step to the reagent, with the grade and documentation you need at that stage.", num="04"),
           tabs=tabs, panels=panels,
           head_svc=section_head("Custom development", "When the catalogue does not fit, we build the reagent.",
                                 "Bead conjugation, GMP protein expression, gene editing and formulation — developed against your process, not a generic spec.",
                                 "services.html", "Explore services", num="05"),
           svc=svc,
           head_res=section_head("Resources", "Technical notes from the people who make it.",
                                 "Application notes, protocols and regulatory explainers — written by our R&amp;D and quality teams.",
                                 "resources.html", "Visit the library", num="06"),
           res=res)
    return head("T&L Biotechnology — GMP raw materials for cell & gene therapy",
                "GMP-grade magnetic beads, monoclonal antibodies, recombinant proteins and serum-free media for CGT. FDA DMF 038124 and 038820, ISO 13485 and ISO 9001 certified.",
                "home") + header("Home") + body + footer()


# --------------------------------------------------------------------------
# page: platform
# --------------------------------------------------------------------------
def page_platform():
    detail = [
        ("a", "01", "Data", "Assay and process data",
         "Every project produces two kinds of output: the answer you asked for, and everything the "
         "bench learned on the way. Most suppliers keep the first and discard the second.",
         ["Lot-level records for every catalogue SKU",
          "Protocol outcomes, including the conditions that failed",
          "QC release data structured for re-use, not just filing"],
         "What it changes: the next project starts from a measured prior, not a guess."),
        ("b", "02", "Models", "Expression design models",
         "A sequence on its own does not express. Codon usage, signal peptide, tag position, host and "
         "induction window decide whether you get protein or inclusion bodies. The models propose that "
         "combination and rank it before anything is synthesised.",
         ["Codon optimisation against the chosen host",
          "Signal peptide, tag and vector architecture",
          "Solubility and yield prediction, ranked per candidate"],
         "What it changes: you stop finding out at the bench what could have been predicted."),
        ("c", "03", "Products", "Physical reagents",
         "The layer your experiment actually touches. Designed against an assay rather than a "
         "catalogue slot, then released under a quality system that survives audit.",
         ["%d catalogue products across four families" % NSKU,
          "GMP and RUO grades of the same design",
          "Custom builds when the catalogue does not fit"],
         "What it changes: a reagent you can qualify once and scale without a redesign."),
        ("d", "04", "Lab network", "Capacity to run the work",
         "Our own laboratory executes: expression, purification, assay, release. When volume exceeds "
         "one bench, qualified partner facilities absorb the overflow under our methods and our "
         "quality system.",
         ["3,200 m² in-house R&D and GMP base",
          "Qualified partner facilities for overflow",
          "Capacity roadmap with committed windows"],
         "What it changes: throughput stops being a function of one building."),
    ]

    rows = "".join("""
    <article class="prow prow--{tone}" id="{n}">
      <div class="prow__side">
        <span class="prow__n">{n}</span>
        <span class="prow__k">{k}</span>
      </div>
      <div class="prow__body">
        <h2>{title}</h2>
        <p class="prow__desc">{desc}</p>
        <ul class="prow__list">{pts}</ul>
        <div class="prow__note">{note}</div>
      </div>
    </article>""".format(tone=t, n=n, k=e(k), title=e(title), desc=e(desc),
                       pts="".join("<li>%s</li>" % e(x) for x in pts), note=e(note))
        for t, n, k, title, desc, pts, note in detail)

    loop = "".join("""
    <div class="loop__step">
      <span class="loop__n">{n:02d}</span>
      <div class="loop__t">{t}</div>
      <p class="loop__d">{d}</p>
    </div>""".format(n=i + 1, t=e(t), d=e(d)) for i, (t, d) in enumerate(LOOP))

    dont = [
        ("We are not a model company.", "We do not sell software licences or a foundation model. "
         "The models are internal tooling that makes our experiments and reagents better."),
        ("We are not a CRO.", "We do not take on every assay. We take work that extends the tool "
         "stack — if it teaches the platform nothing, we will say so."),
        ("We are not an instrument company.", "We do not sell hardware, plate readers or closed "
         "cartridges. We design the experiment for the platform already on your bench, and route "
         "the work when the bench is not yours."),
    ]
    dont_html = "".join("""
      <div class="dont__item"><h3>{t}</h3><p>{d}</p></div>""".format(t=e(t), d=e(d)) for t, d in dont)

    body = """
<main id="main">
<section class="phero">
  <div class="phero__grid"></div>
  <div class="container phero__inner">
    <div class="crumbs"><a href="index.html">Home</a>{c}<span>Platform</span></div>
    <h1>AI plans the experiment. The bench runs it.</h1>
    <p>Four layers — experiment data, design models, the reagents a run consumes, and the capacity to
      execute it — wired into one loop. Owning the loop is the difference between selling reagents and
      running experiments.</p>
    <div class="phero__meta">
      <span class="pill pill--brand">{spark} AI-designed constructs</span>
      <span class="pill">Execution in our own lab</span>
      <span class="pill">{nsku} reagents behind every run</span>
      <span class="pill">Overflow capacity, qualified</span>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    {rows}
  </div>
</section>

<section class="section section--mist">
  <div class="container">
    {head_loop}
    <div class="loop">{loop}</div>
    <p class="loop__note">The loop is the product. A reagent shipped without its assay data is a
      commodity; the same reagent shipped with the data that shaped it is a head start.</p>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head reveal">
      <div class="section-head__text">
        <div class="eyebrow"><span class="eyebrow__num">05</span>Boundaries</div>
        <h2>What we are not.</h2>
        <p>AI claims are cheap. Being specific about the boundary is what makes the rest credible.</p>
      </div>
    </div>
    <div class="dont">{dont}</div>
  </div>
</section>

<section class="section section--tight">
  <div class="container">
    <div class="cta-band reveal">
      <div><h2>See the loop run on your target.</h2>
        <p>Send an assay that is not behaving. We will tell you which layer is failing — and whether
          it is worth fixing with a tool, a protocol, or a different approach entirely.</p></div>
      <div style="display:flex;gap:10px;flex-wrap:wrap">
        <a class="btn btn--light" href="contact.html#quote">Talk to an application scientist {ar}</a>
        <a class="btn btn--outline-light" href="services.html">See the services</a>
      </div>
    </div>
  </div>
</section>
</main>""".format(c=ic("chev"), ar=ic("arrow"), spark=ic("spark"), rows=rows, loop=loop,
                  dont=dont_html, nsku=NSKU,
                  head_loop=section_head("The loop", "Design, build, test, learn.",
                                         "Four steps per round, including the rounds that fail. The failure is the data.",
                                         num="04"))
    return head("Platform — AI for science at T&L Biotechnology",
                "A four-layer platform that plans experiments in silico and executes them at the bench: experiment data, design models, reagents and lab capacity in one loop.",
                "platform") + header("Platform") + body + footer()


# --------------------------------------------------------------------------
# page: products
# --------------------------------------------------------------------------
def page_products():
    counts = {c["id"]: sum(1 for p in PRODUCTS if p["cat"] == c["id"]) for c in CATEGORIES}
    checks = "".join("""
      <label class="check"><input type="checkbox" data-filter="cat" value="{cid}">
        {n}<span class="check__count">{c}</span></label>""".format(
        cid=c["id"], n=e(c["name"]), c=counts[c["id"]]) for c in CATEGORIES)
    apps = "".join("""
      <label class="check"><input type="checkbox" data-filter="app" value="{aid}">
        {n}<span class="check__count">{c}</span></label>""".format(
        aid=a["id"], n=e(a["name"]),
        c=sum(1 for p in PRODUCTS if a["id"] in p["apps"])) for a in APPLICATIONS)

    body = """
<main id="main">
<section class="phero">
  <div class="phero__grid"></div>
  <div class="container phero__inner">
    <div class="crumbs"><a href="index.html">Home</a>{c}<span>Products</span></div>
    <h1>The product catalogue</h1>
    <p>{nsku} reagents across four families — cell separation and activation, monoclonal antibodies,
      recombinant proteins, and serum-free media. Filter by family or by the cell type you work with.</p>
    <div class="phero__meta">
      <span class="pill pill--brand">{ck} GMP &amp; RUO grades</span>
      <span class="pill">{d} COA with every lot</span>
      <span class="pill">{d} Four more families in development</span>
    </div>
  </div>
</section>

<div class="container">
  <button class="filter-toggle" id="filter-toggle" aria-expanded="false">
    {ft} Filters <span id="filter-count">0</span>
  </button>
  <div class="catalog">
    <aside class="filters">
      <div>
        <div class="filter__head"><span class="filter__title">Search</span></div>
        <div class="filter__search">{s}
          <input type="search" id="cat-search" placeholder="Product or target…" aria-label="Search products">
        </div>
      </div>
      <div>
        <div class="filter__head"><span class="filter__title">Product family</span>
          <button class="filter__reset" id="reset">Reset</button></div>
        {checks}
      </div>
      <div>
        <div class="filter__head"><span class="filter__title">Application</span></div>
        {apps}
      </div>
      <div style="border:1px solid var(--line);border-radius:14px;padding:18px;background:var(--mist)">
        <div class="filter__title" style="margin-bottom:8px">Not sure which grade?</div>
        <p style="font-size:.82rem;color:var(--muted);line-height:1.55">RUO for research, GMP for
          clinical supply. We will tell you which one your stage actually needs.</p>
        <a class="link-arrow" style="margin-top:12px;font-size:.82rem" href="contact.html#quote">
          Ask a specialist {ar}</a>
      </div>
    </aside>
    <div>
      <div class="catalog__docs">
        <span class="catalog__docs-k">{doc} Documents</span>
        <span>Every product ships with a datasheet, a representative COA and an SDS. Download
          from the card, or open the
          <a href="resources.html#docs">document library</a>.</span>
      </div>
      <div class="catalog__bar">
        <div class="catalog__count">Showing <b id="count-visible">{nsku}</b> of <b>{nsku}</b> products</div>
        <select class="select" id="sort">
          <option value="default">Sort: recommended</option>
          <option value="price-asc">Price: low to high</option>
          <option value="price-desc">Price: high to low</option>
          <option value="name">Name: A–Z</option>
        </select>
      </div>
      <div class="grid-products" id="grid">{grid}</div>
      <div class="empty" id="empty" style="display:none">
        <h3>No products match those filters</h3>
        <p>Clear the filters, or tell us the target and we will point you at the closest match.</p>
        <p style="margin-top:16px"><a class="btn btn--ghost btn--sm" href="contact.html#quote">Ask a specialist</a></p>
      </div>
    </div>
  </div>
</div>

<section class="section section--mist">
  <div class="container">
    {head_pipe}
    <div class="pipe">{pipe}</div>
  </div>
</section>

<section class="section section--tight">
  <div class="container">
    <div class="cta-band reveal">
      <div>
        <h2>Need a bulk quote or a GMP lot?</h2>
        <p>Catalogue prices cover research pack sizes. For process-scale quantities, technical
          agreements or a GMP lot reservation, talk to us directly.</p>
      </div>
      <div style="display:flex;gap:10px;flex-wrap:wrap">
        <a class="btn btn--light" href="contact.html#quote">Request a quote {ar}</a>
        <a class="btn btn--outline-light" href="resources.html#coa">Find a COA</a>
      </div>
    </div>
  </div>
</section>
</main>
""".format(c=ic("chev"), ck=ic("check"), d=ic("check"), s=ic("search"), ft=ic("grid"),
           checks=checks, apps=apps, ar=ic("arrow"), nsku=NSKU, doc=ic("doc"),
           head_pipe=section_head("Roadmap", "What joins the catalogue next.",
                                  "Each new family reuses the same design and validation loop, which is why "
                                  "the timeline is a quarter, not a decade.", num="02"),
           pipe="".join("""
      <div class="pipe__item">
        <span class="pipe__tag">{tag}</span>
        <div class="pipe__t">{t}</div>
        <p class="pipe__d">{d}</p>
      </div>""".format(tag=e(tag), t=e(t), d=e(d)) for t, d, tag in PORTFOLIO_NEXT),
           grid="".join(gcard(p) for p in PRODUCTS))
    return head("Products — T&L Biotechnology",
                "Browse %d GMP-grade CGT reagents: cell separation beads, monoclonal antibodies, recombinant proteins and serum-free media." % NSKU,
                "products") + header("Products") + body + footer()


# --------------------------------------------------------------------------
# page: product detail
# --------------------------------------------------------------------------
def page_product():
    body = """
<main id="main">
<div class="container">
  <div class="crumbs" style="padding-top:28px">
    <a href="index.html">Home</a>{c}<a href="products.html">Products</a>{c}
    <a href="products.html" id="pdp-cat">Catalogue</a>{c}<span id="pdp-crumb">…</span>
  </div>
  <div class="pdp">
    <div class="pdp__gallery">
      <div class="pdp__main"><img id="pdp-img" src="" alt=""></div>
      <div class="pdp__thumbs" id="pdp-thumbs"></div>
    </div>
    <div class="pdp__info">
      <div class="phero__meta" style="margin:0 0 6px">
        <span class="pill pill--brand" id="pdp-grade">GMP grade available</span>
        <span class="pill" id="pdp-catpill">…</span>
      </div>
      <h1 class="pdp__title" id="pdp-title">Loading…</h1>
      <p class="pdp__sub" id="pdp-blurb"></p>
      <dl class="pdp__specs" id="pdp-specs"></dl>
      <div class="buybox">
        <div class="buybox__row">
          <div>
            <div class="buybox__price" id="pdp-price">—</div>
            <div style="font-size:.78rem;color:var(--muted-2);margin-top:2px">Research pack size · excl. shipping</div>
          </div>
          <div class="sizes" id="pdp-sizes"></div>
        </div>
        <div class="buybox__actions">
          <a class="btn" href="contact.html#quote" style="flex:1">Request a quote {ar}</a>
          <a class="btn btn--ghost" href="#" data-doc="datasheet" download>{d} Datasheet</a>
        </div>
        <div class="pdp__docs" id="pdp-docs">
          <span class="pdp__docs-k">Documents</span>
          <a href="#" data-doc="datasheet" download>{d} Datasheet <i>PDF</i></a>
          <a href="#" data-doc="coa" download>{d} COA <i>PDF</i></a>
          <a href="#" data-doc="sds" download>{d} SDS <i>PDF</i></a>
        </div>
        <div class="buybox__meta">
          <span>{ck} COA with every lot</span>
          <span>{ck} DMF letter on request</span>
          <span>{ck} Ships worldwide</span>
        </div>
      </div>
    </div>
  </div>

  <div class="tabs" role="tablist">
    <button class="tab is-active" data-ptab="overview">Overview</button>
    <button class="tab" data-ptab="specs">Specifications</button>
    <button class="tab" data-ptab="docs">Documentation</button>
    <button class="tab" data-ptab="related">Related products</button>
  </div>

  <div class="tabpanel" data-ppanel="overview">
    <h3>About this product</h3>
    <p id="pdp-desc"></p>
    <h3 style="margin-top:24px">Why teams standardise on it</h3>
    <ul id="pdp-highlights"></ul>
  </div>
  <div class="tabpanel" data-ppanel="specs" style="display:none">
    <h3>Specifications</h3>
    <dl id="pdp-spectable"></dl>
  </div>
  <div class="tabpanel" data-ppanel="docs" style="display:none">
    <h3>Documents you can download now</h3>
    <p>Datasheet, representative COA and the safety data sheet for this product are available
      without a request. The lot-specific COA ships with your order; the DMF letter of
      authorisation and the quality agreement are released under a technical agreement.</p>
    <div class="doclist">
      <a class="doc" href="#" data-doc="datasheet" download>{d}<b>Technical datasheet</b><span>PDF · 2 pages</span></a>
      <a class="doc" href="#" data-doc="coa" download>{d}<b>Certificate of Analysis</b><span>Representative lot · PDF</span></a>
      <a class="doc" href="#" data-doc="sds" download>{d}<b>Safety data sheet</b><span>PDF · 16 sections</span></a>
      <a class="doc" href="docs/dmf-summary.pdf" download>{d}<b>DMF filing summary</b><span>PDF</span></a>
      <a class="doc" href="docs/quality-overview.pdf" download>{d}<b>Quality system overview</b><span>PDF</span></a>
      <a class="doc" href="contact.html#quote">{d}<b>DMF letter of authorisation</b><span>On request</span></a>
    </div>
  </div>
  <div class="tabpanel" data-ppanel="related" style="display:none">
    <h3>Often used together</h3>
    <div class="apps__products" id="pdp-related"></div>
  </div>
</div>

<section class="section section--tight">
  <div class="container">
    <div class="cta-band reveal">
      <div>
        <h2>Need the batch record, not just the brochure?</h2>
        <p>We can share the quality overview, a representative COA and — where a DMF exists —
          the letter of authorisation for your IND.</p>
      </div>
      <div style="display:flex;gap:10px;flex-wrap:wrap">
        <a class="btn btn--light" href="contact.html#quote">Talk to a scientist {ar}</a>
        <a class="btn btn--outline-light" href="quality.html">Quality overview</a>
      </div>
    </div>
  </div>
</section>
</main>
""".format(c=ic("chev"), ar=ic("arrow"), ck=ic("check"), d=ic("doc"))
    return head("Product — T&L Biotechnology",
                "Product details, specifications and documentation for T&L Biotechnology CGT reagents.",
                "product") + header("Products") + body + footer()


# --------------------------------------------------------------------------
# page: applications
# --------------------------------------------------------------------------
def page_applications():
    blocks = []
    for i, a in enumerate(APPLICATIONS):
        steps = "".join("""
        <div class="apps__step"><b>{k}</b><span>{v}</span></div>""".format(k=e(s[0]), v=e(s[1]))
            for s in a["steps"])
        blocks.append("""
<section class="section{pf}" id="{aid}">
  <div class="container">
    <div class="appblock{rev}">
      <div class="appblock__copy reveal">
        <div class="eyebrow">{pill}</div>
        <h2>{title}</h2>
        <p class="appblock__desc">{desc}</p>
        <div class="appsteps">{steps}</div>
        <a class="btn btn--ghost" href="products.html">Shop {name} reagents {ar}</a>
      </div>
      <div class="appblock__side reveal">
        <div class="appside">
          <div class="appside__head">Recommended reagent set<span>{n} products</span></div>
          <div class="appside__list">{prods}</div>
          <a class="link-arrow appside__more" href="products.html">See the full set {ar}</a>
        </div>
      </div>
    </div>
  </div>
</section>""".format(pf=" section--mist" if i % 2 else "", rev=" appblock--rev" if i % 2 else "",
                    aid=a["id"], pill=e(a["pill"]), title=e(a["title"]), desc=e(a["desc"]),
                    steps=steps, name=e(a["name"]), ar=ic("arrow"), n=a["count"],
                    prods="".join(mini_prod(s) for s in a["products"])))

    body = """
<main id="main">
<section class="phero">
  <div class="phero__grid"></div>
  <div class="container phero__inner">
    <div class="crumbs"><a href="index.html">Home</a>{c}<span>Applications</span></div>
    <h1>Organised by what you are manufacturing.</h1>
    <p>Cell type determines the isolation target, the activation signal, the cytokine cocktail and
      the medium. Six workflows, each mapped to the reagent that sits at every step.</p>
  </div>
</section>
{blocks}
<section class="section section--tight">
  <div class="container">
    <div class="cta-band reveal">
      <div><h2>Working on something not listed here?</h2>
        <p>&gamma;&delta; T cells, TIL, CAR-macrophage, exosome manufacturing &mdash; the reagent set usually exists,
          it just is not a catalogue page yet. Tell us the process and we will map it.</p></div>
      <div style="display:flex;gap:10px;flex-wrap:wrap">
        <a class="btn btn--light" href="contact.html#quote">Describe your process {ar}</a>
      </div>
    </div>
  </div>
</section>
</main>""".format(c=ic("chev"), ar=ic("arrow"), blocks="".join(blocks))
    return head("Applications — T&L Biotechnology",
                "Workflow-matched reagents for T cell, NK, MSC, iPSC, hematopoietic and dendritic cell manufacturing.",
                "applications") + header("Applications") + body + footer()


# --------------------------------------------------------------------------
# page: quality
# --------------------------------------------------------------------------
def page_quality():
    cards = [
        ("shield", "ISO 13485:2016", "The medical-device quality management system applied to reagent manufacture — design control, risk management and traceability from raw material to release."),
        ("doc", "ISO 9001", "Company-wide quality management covering the R&amp;D, production and commercial processes around the ISO 13485 scope."),
        ("factory", "GMP cleanroom", "3,200 m² R&amp;D and production base with a GMP-level clean workshop for bead, protein and medium manufacture."),
        ("lock", "Two Type II DMFs", "DMF 038124 (ActSep® CD3/CD28 beads) and DMF 038820 (anti-human CD28 mAb), referenceable by sponsors in an IND."),
        ("chart", "Analytical release testing", "Identity, purity and activity testing per lot: SDS-PAGE, SEC-HPLC, endotoxin, residual host-cell protein and cell-based potency where applicable."),
        ("users", "Audit support", "Audit data packages delivered for more than 30 customers, plus on-site and remote inspection hosting."),
    ]
    q = "".join("""
    <div class="qcard reveal"><div class="qcard__ico">{i}</div><h3>{t}</h3><p>{d}</p></div>
    """.format(i=ic(i), t=e(t), d=d) for i, t, d in cards)

    rows = [
        ("038124", "Type II", "ActSep® CD3/CD28 Separation &amp; Activation Magnetic Beads", "On file"),
        ("038820", "Type II", "Anti-Human CD28 Monoclonal Antibody", "On file"),
    ]
    trs = "".join("""
      <tr><td><b>{n}</b></td><td>{t}</td><td>{p}</td><td><span class="pill pill--ok" style="font-size:.72rem">{s}</span></td></tr>
    """.format(n=n, t=t, p=p, s=s) for n, t, p, s in rows)

    body = """
<main id="main">
<section class="phero">
  <div class="phero__grid"></div>
  <div class="container phero__inner">
    <div class="crumbs"><a href="index.html">Home</a>{c}<span>Quality &amp; regulatory</span></div>
    <h1>Regulatory status, stated plainly.</h1>
    <p>Which filings exist, what they cover, and what a sponsor can actually reference. If a
      document is missing from this page, ask for it — the answer is usually "here it is".</p>
    <div class="phero__meta">
      <span class="pill pill--brand">{ck} ISO 13485:2016</span>
      <span class="pill pill--brand">{ck} ISO 9001</span>
      <span class="pill">DMF 038124</span><span class="pill">DMF 038820</span>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head reveal">
      <div class="section-head__text">
        <div class="eyebrow">Quality system</div>
        <h2>Six things an auditor will ask about.</h2>
        <p>Each of them is answered before the question is finished — because the system was built
          for CGT customers, not adapted from a general chemical catalogue.</p>
      </div>
    </div>
    <div class="qgrid">{q}</div>
  </div>
</section>

<section class="section section--mist">
  <div class="container">
    <div class="section-head reveal">
      <div class="section-head__text">
        <div class="eyebrow">Regulatory filings</div>
        <h2>Drug Master File status</h2>
        <p>A Type II DMF is a closed reference: the sponsor cites the file in their IND and we
          provide a letter of authorisation. The content stays confidential to the agency.</p>
      </div>
      <a class="link-arrow" href="contact.html#quote">Request a letter of authorisation {ar}</a>
    </div>
    <div class="table-wrap">
      <table class="data">
        <thead><tr><th>DMF number</th><th>Type</th><th>Product covered</th><th>Status</th></tr></thead>
        <tbody>{trs}</tbody>
      </table>
    </div>
    <div style="margin-top:18px;display:grid;gap:10px;max-width:82ch">
      <p style="font-size:.86rem;color:var(--muted);line-height:1.6">
        Additional Type II filings are on record for the anti-human CD3 monoclonal antibody,
        recombinant human IL-7 (GMP-TL506) and recombinant human IL-15. File numbers are released
        to customers on request.</p>
      <p style="font-size:.78rem;color:var(--muted-2);line-height:1.55">
        Status reflects the position published on tlbiotechnology.com. Confirm current status with our
        regulatory team before citing a file in a submission.</p>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="split split--start">
      <div class="reveal">
        <div class="eyebrow">Documentation</div>
        <h2>What arrives with the box</h2>
        <p style="margin-top:16px;color:var(--muted);line-height:1.7">Documentation is released per
          lot, not per catalogue number. That distinction matters during a comparability exercise.</p>
        <div class="doclist" style="margin-top:24px">
          <a class="doc" href="resources.html#coa">{d}<b>Certificate of Analysis</b><span>Every lot</span></a>
          <a class="doc" href="contact.html#quote">{d}<b>Technical datasheet</b><span>On request</span></a>
          <a class="doc" href="contact.html#quote">{d}<b>Safety data sheet</b><span>On request</span></a>
          <a class="doc" href="contact.html#quote">{d}<b>DMF letter of authorisation</b><span>On request</span></a>
          <a class="doc" href="contact.html#quote">{d}<b>Quality agreement</b><span>Per customer</span></a>
          <a class="doc" href="contact.html#quote">{d}<b>Audit package</b><span>Per customer</span></a>
        </div>
      </div>
      <div class="reveal">
        <div class="eyebrow">Supply chain</div>
        <h2>Traceability end to end</h2>
        <p style="margin-top:16px;color:var(--muted);line-height:1.7">Raw-material sourcing,
          in-process controls and release testing are recorded against the lot number that appears
          on your COA, so a deviation investigation can be answered from the batch record.</p>
        <ul style="margin-top:20px;color:var(--muted);line-height:1.75;font-size:.94rem;padding-left:18px">
          <li>Animal-origin-free where the product claims it</li>
          <li>Lot-level retention samples held for the shelf life</li>
          <li>Cold-chain packaging validated for destination</li>
          <li>Change notification under quality agreement</li>
        </ul>
        <a class="btn btn--ghost" style="margin-top:26px" href="contact.html#audit">Schedule an audit {ar}</a>
      </div>
    </div>
  </div>
</section>
</main>""".format(c=ic("chev"), ar=ic("arrow"), ck=ic("check"), d=ic("doc"),
                  q=q, trs=trs)
    return head("Quality & Regulatory — T&L Biotechnology",
                "ISO 13485, ISO 9001, GMP manufacturing and FDA Drug Master Files 038124 and 038820.",
                "quality") + header("Quality") + body + footer()


# --------------------------------------------------------------------------
# page: services
# --------------------------------------------------------------------------
def page_services():
    cards = "".join("""
    <div class="svc__card reveal">
      <span class="svc__idx">{idx:02d}</span>
      <div class="svc__ico">{i}</div>
      <h3>{t}</h3><p>{d}</p>
      <div class="svc__tags">{tags}</div>
      <a class="link-arrow" style="margin-top:10px;font-size:.85rem" href="contact.html#quote">
        Discuss a project {ar}</a>
    </div>""".format(i=ic(s["icon"]), t=e(s["title"]), d=e(s["desc"]), idx=i + 1,
                     tags="".join("<span>%s</span>" % e(t) for t in s["tags"]), ar=ic("arrow"))
        for i, s in enumerate(SERVICES))

    auto = "".join("""
    <div class="auto__card auto__card--{tone}">
      <div class="auto__phase">{p}</div>
      <div class="auto__state">{s}</div>
      <p class="auto__desc">{d}</p>
      <ul class="auto__list">{pts}</ul>
    </div>""".format(tone=a["tone"], p=e(a["phase"]), s=e(a["state"]), d=e(a["desc"]),
                     pts="".join("<li>%s</li>" % e(x) for x in a["points"]))
        for a in AUTOMATION)

    net = "".join("""
    <div class="net__step">
      <span class="net__n">{n:02d}</span>
      <div class="net__t">{t}</div>
      <p class="net__d">{d}</p>
    </div>""".format(n=i + 1, t=e(t), d=e(d)) for i, (t, d) in enumerate(NETWORK))

    criteria = [
        ("Method fit", "The facility can run the assay to our written method, not an approximation of it."),
        ("Data format", "Results return in our schema — raw where it matters, summarised where it does not."),
        ("Quality system", "Documented training, equipment qualification and deviation handling."),
        ("Turnaround", "A committed window per batch, with escalation when it slips."),
    ]
    crit = "".join("""
      <div class="crit__item"><b>{t}</b><p>{d}</p></div>""".format(t=e(t), d=e(d)) for t, d in criteria)

    body = """
<main id="main">
<section class="phero">
  <div class="phero__grid"></div>
  <div class="container phero__inner">
    <div class="crumbs"><a href="index.html">Home</a>{c}<span>Services</span></div>
    <h1>Capacity, not just catalogue.</h1>
    <p>Custom development when the catalogue stops short, a published automation roadmap, and a
      network that lets throughput grow without waiting for one building to expand.</p>
    <div class="phero__meta">
      <a class="btn btn--sm" href="contact.html#quote">Scope a project {ar}</a>
      <a class="btn btn--sm btn--ghost" href="#automation">Automation roadmap</a>
    </div>
  </div>
</section>

<section class="section" id="custom">
  <div class="container">
    <div class="section-head reveal">
      <div class="section-head__text">
        <div class="eyebrow"><span class="eyebrow__num">01</span>Custom development</div>
        <h2>Six ways we get pulled into a programme.</h2>
        <p>Most engagements start with a reagent that almost works. The work is closing the gap
          between "almost" and a validated, documented supply.</p>
      </div>
    </div>
    <div class="svc">{cards}</div>
  </div>
</section>

<section class="section section--ink" id="automation">
  <div class="container">
    <div class="section-head reveal">
      <div class="section-head__text">
        <div class="eyebrow"><span class="eyebrow__num">02</span>Lab automation</div>
        <h2>Three tiers of capacity.</h2>
        <p>Start at bench scale and move up as the programme grows. Every tier runs under the same
          methods and the same quality system, so moving up does not mean re-qualifying the work.</p>
      </div>
    </div>
    <div class="auto">{auto}</div>
    <div class="auto__foot">
      <b>What "automation" means here:</b> liquid handling and scheduling across qualified sites.
      Scientists stay in the loop for design and exception handling — the model proposes, the
      platform executes, the scientist decides.
    </div>
  </div>
</section>

<section class="section" id="network">
  <div class="container">
    <div class="section-head reveal">
      <div class="section-head__text">
        <div class="eyebrow"><span class="eyebrow__num">03</span>Capacity network</div>
        <h2>One order. Many benches.</h2>
        <p>Academic core facilities and specialist laboratories already own capacity that sits idle
          between grants. We qualify that capacity, standardise the data it returns, and route work
          to it — so a customer sees one contract and one report.</p>
      </div>
      <a class="link-arrow" href="contact.html#quote">Discuss a volume programme {ar}</a>
    </div>
    <div class="net">{net}</div>
    <div class="crit">
      <div class="crit__head">What a partner facility has to pass before it receives work</div>
      {crit}
    </div>
    <div class="net__note">
      <b>Why we are building it this way:</b> a reagent supplier that also controls capacity can
      commit to a delivery date. One that does not, cannot — however good its catalogue is.
    </div>
  </div>
</section>

<section class="section section--mist" id="experts">
  <div class="container">
    <div class="expert">
      <div class="expert__copy reveal">
        <div class="eyebrow"><span class="eyebrow__num">04</span>Application science</div>
        <h2>{expert_title}</h2>
        <p class="expert__desc">{expert_desc}</p>
        <ul class="expert__list">{expert_bullets}</ul>
        <a class="btn" href="contact.html#quote">Book a technical call {ar}</a>
      </div>
      <div class="expert__card reveal">
        <div class="expert__avatar">{users}</div>
        <div class="expert__role">Application Science Lead</div>
        <div class="expert__bg">{expert_bg}</div>
        <div class="expert__rule"></div>
        <p>Runs the first technical call, reviews the protocol, and stays on the project through
          transfer — the same person, not a rotating account team.</p>
        <div class="expert__tags"><span>Immunology</span><span>Cell processing</span><span>Assay transfer</span></div>
      </div>
    </div>
  </div>
</section>

<section class="section section--tight">
  <div class="container">
    <div class="cta-band reveal">
      <div><h2>Tell us what the reagent has to do.</h2>
        <p>Send the target, the assay and the constraints. We will come back with a feasibility
          view and an honest answer about whether we are the right partner.</p></div>
      <div style="display:flex;gap:10px;flex-wrap:wrap">
        <a class="btn btn--light" href="contact.html#quote">Brief a project {ar}</a>
        <a class="btn btn--outline-light" href="platform.html">See the platform</a>
      </div>
    </div>
  </div>
</section>
</main>""".format(c=ic("chev"), ar=ic("arrow"), cards=cards, auto=auto, net=net, crit=crit,
                  users=ic("users"), expert_title=e(EXPERT["title"]),
                  expert_desc=e(EXPERT["desc"]), expert_bg=e(EXPERT["background"]),
                  expert_bullets="".join("<li>%s</li>" % e(x) for x in EXPERT["bullets"]))
    return head("Services — custom development, lab automation and capacity at T&L",
                "Custom reagent development, a published lab automation roadmap, and a qualified capacity network for high-throughput work.",
                "services") + header("Services") + body + footer()


# --------------------------------------------------------------------------
# page: partners
# --------------------------------------------------------------------------
def page_partners():
    models = [
        ("Authorised distributor",
         "You hold stock, sell into your territory, and provide first-line technical support. "
         "Territory is defined by country or region and reviewed annually.",
         ["Exclusive or non-exclusive by territory", "Local stock and logistics", "First-line application support"],
         "Fits: established reagent or instrument distributors with a life-science catalogue."),
        ("OEM &amp; private label",
         "Our reagents, our batch records, your brand. Formulation and packaging are fixed; labelling, "
         "documentation and market positioning are yours.",
         ["Your label, our manufacturing", "Batch records and COA under your name", "Minimum order applies"],
         "Fits: companies with a brand and a channel but no in-house manufacturing."),
        ("Referral &amp; academic",
         "You introduce a programme, we run the technical and commercial conversation, and the "
         "introduction is recognised for the life of the account.",
         ["No stock commitment", "Project-based recognition", "Technical team joins the first call"],
         "Fits: consultants, core facilities and academic groups."),
    ]
    models_html = "".join("""
    <article class="pmodel reveal">
      <div class="pmodel__n">{n:02d}</div>
      <h3>{t}</h3>
      <p class="pmodel__desc">{d}</p>
      <ul class="pmodel__list">{pts}</ul>
      <div class="pmodel__fit">{fit}</div>
    </article>""".format(n=i + 1, t=t, d=d, pts="".join("<li>%s</li>" % x for x in pts), fit=fit)
        for i, (t, d, pts, fit) in enumerate(models))

    benefits = [
        ("Territory", "Defined by agreement, reviewed annually — not by whoever emails first."),
        ("Technical training", "Application scientists train your team on the workflows, not just the catalogue."),
        ("Marketing assets", "Datasheets, imagery, DMF summaries and protocol notes, cleared for your market."),
        ("Supply commitment", "Stock reservation and lead-time commitments written into the agreement."),
        ("Regulatory support", "Letters of authorisation and quality documentation for your registrations."),
        ("Co-branded collateral", "Local-language material built with your team, not handed to you."),
    ]
    benefits_html = "".join("""
      <div class="qcard reveal"><h3>{t}</h3><p>{d}</p></div>""".format(t=t, d=d) for t, d in benefits)

    criteria = [
        ("Existing customer base", "An installed base in cell therapy, bioprocessing or diagnostics — not a cold start."),
        ("Technical capability", "Someone on your team can answer a protocol question without escalating."),
        ("Regulatory familiarity", "You have handled IVD or RUO registration in your territory before."),
        ("Logistics", "Cold-chain storage and a track record of compliant delivery."),
    ]
    criteria_html = "".join("""
      <div class="crit__item"><b>{t}</b><p>{d}</p></div>""".format(t=t, d=d) for t, d in criteria)

    steps = [("Apply", "Send the form below. Territory, current portfolio and volume estimate."),
             ("Screening call", "A 30-minute call with our channel team. We will tell you if the territory is open."),
             ("Agreement", "Territory, pricing tier, targets and support commitments, in writing."),
             ("Onboarding", "Product training, marketing assets, and a first stock order.")]
    steps_html = "".join("""
    <div class="net__step"><span class="net__n">{n:02d}</span><div class="net__t">{t}</div><p class="net__d">{d}</p></div>
    """.format(n=i + 1, t=t, d=d) for i, (t, d) in enumerate(steps))

    body = """
<main id="main">
<section class="phero">
  <div class="phero__grid"></div>
  <div class="container phero__inner">
    <div class="crumbs"><a href="index.html">Home</a>{c}<span>Partners</span></div>
    <h1>Sell tools that arrive with the evidence.</h1>
    <p>We work with a small number of distributors, OEM partners and academic referrers per territory.
      If you already sell into cell therapy or bioprocessing, the conversation is short.</p>
    <div class="phero__meta">
      <span class="pill pill--brand">{ck} Territory defined by agreement</span>
      <span class="pill">Technical training included</span>
      <span class="pill">OEM available</span>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head reveal">
      <div class="section-head__text">
        <div class="eyebrow"><span class="eyebrow__num">01</span>Models</div>
        <h2>Three ways to work with us.</h2>
        <p>Pick the one that matches how you already sell. We would rather have one committed partner
          than three competing ones in the same country.</p>
      </div>
    </div>
    <div class="pmodels">{models}</div>
  </div>
</section>

<section class="section section--mist">
  <div class="container">
    <div class="section-head reveal">
      <div class="section-head__text">
        <div class="eyebrow"><span class="eyebrow__num">02</span>What you get</div>
        <h2>Support that is written down.</h2>
        <p>Channel agreements fail on the unwritten parts. These six are in the contract, not in
          the sales deck.</p>
      </div>
    </div>
    <div class="qgrid">{benefits}</div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="split split--start">
      <div class="reveal">
        <div class="eyebrow"><span class="eyebrow__num">03</span>Qualification</div>
        <h2>What we look for.</h2>
        <p class="prow__desc">Not a checklist to tick — these are the four things that decide whether
          a partnership works six months in.</p>
        <div class="crit" style="margin-top:24px">{criteria}</div>
      </div>
      <div class="reveal">
        <div class="eyebrow"><span class="eyebrow__num">04</span>Process</div>
        <h2>Four steps, about three weeks.</h2>
        <p class="prow__desc">From application to first stock order. The screening call is where most
          conversations end — usually because the territory is already covered.</p>
        <div class="net" style="grid-template-columns:1fr 1fr;margin-top:24px">{steps}</div>
      </div>
    </div>
  </div>
</section>

<section class="section section--tight">
  <div class="container">
    <div class="form-card reveal" style="max-width:820px;margin-inline:auto">
      <h2 style="font-size:1.5rem">Apply to partner</h2>
      <p style="margin-top:10px;color:var(--muted);font-size:.94rem">Tell us the territory and what you
        already sell. A member of the channel team replies within two business days.</p>
      <form style="margin-top:24px" data-form="partner">
        <div class="form-grid">
          <div class="fld"><label>Company <i>*</i></label><input required placeholder="Distributor or OEM name"></div>
          <div class="fld"><label>Website</label><input placeholder="https://"></div>
          <div class="fld"><label>Contact name <i>*</i></label><input required placeholder="Full name"></div>
          <div class="fld"><label>Work email <i>*</i></label><input type="email" required placeholder="name@company.com"></div>
          <div class="fld"><label>Territory <i>*</i></label><input required placeholder="Country or region"></div>
          <div class="fld"><label>Partnership model</label>
            <select>
              <option>Authorised distributor</option>
              <option>OEM &amp; private label</option>
              <option>Referral &amp; academic</option>
              <option>Not sure yet</option>
            </select></div>
          <div class="fld"><label>Current portfolio</label><input placeholder="What you sell today"></div>
          <div class="fld"><label>Estimated annual volume</label>
            <select>
              <option>Under $100k</option><option>$100k – $500k</option>
              <option>$500k – $1M</option><option>Above $1M</option>
            </select></div>
          <div class="fld fld--full"><label>Anything else</label>
            <textarea placeholder="Existing customers, registration status, warehouse capability."></textarea></div>
        </div>
        <div style="display:flex;align-items:center;gap:18px;margin-top:20px;flex-wrap:wrap">
          <button class="btn" type="submit">Submit application {ar}</button>
          <span class="form-note">We do not share applications outside the channel team.</span>
        </div>
        <div class="form-ok" style="margin-top:16px" data-ok>{ck} Received. The channel team will reply
          within two business days.</div>
      </form>
    </div>
  </div>
</section>
</main>""".format(c=ic("chev"), ar=ic("arrow"), ck=ic("check"),
                  models=models_html, benefits=benefits_html,
                  criteria=criteria_html, steps=steps_html)
    return head("Partners — distributors, OEM and academic referrals | T&L Biotechnology",
                "Distributor, OEM and referral partnerships for T&L life science tools. Territory defined by agreement, technical training included.",
                "partners") + header("Company") + body + footer()


# --------------------------------------------------------------------------
# page: resources
# --------------------------------------------------------------------------
def page_resources():
    cards = "".join("""
    <a class="res__card reveal" href="#">
      <div class="res__media"><img src="{img}" alt="" loading="lazy">
        <span class="res__media-tag">{tag}</span></div>
      <div class="res__body"><span class="res__date">{date}</span><h3>{title}</h3>
        <p>{ex}</p><span class="res__link link-arrow">Read the note {ar}</span></div>
    </a>""".format(img=IMG + "/brand/" + a["img"] + ".webp", tag=e(a["tag"]),
                    date=e(a["date"]), title=e(a["title"]), ex=e(a["excerpt"]), ar=ic("arrow"))
        for a in ARTICLES)

    dl_rows = "".join("""
      <tr>
        <td><a href="product.html?p={slug}">{name}</a><i>{code}</i></td>
        <td>{fam}</td>
        <td><a class="dl-link" href="docs/datasheet-{slug}.pdf" download>Datasheet</a></td>
        <td><a class="dl-link" href="docs/coa-{slug}.pdf" download>COA</a></td>
        <td><a class="dl-link" href="docs/sds-{cat}.pdf" download>SDS</a></td>
      </tr>""".format(slug=p["slug"], name=e(p["name"]), code=e(cat["short"]),
                   fam=e(cat["name"]), cat=p["cat"])
        for p in PRODUCTS for cat in [next(c for c in CATEGORIES if c["id"] == p["cat"])])

    faq = "".join("""
    <div class="faq__item">
      <button class="faq__q">{q}{p}</button>
      <div class="faq__a"><p>{a}</p></div>
    </div>""".format(q=e(q), p=ic("plus"), a=e(a)) for q, a in FAQ)

    body = """
<main id="main">
<section class="phero">
  <div class="phero__grid"></div>
  <div class="container phero__inner">
    <div class="crumbs"><a href="index.html">Home</a>{c}<span>Resources</span></div>
    <h1>Documents, protocols and straight answers.</h1>
    <p>Look up a Certificate of Analysis by lot, read the technical notes, or find the answer to the
      question that usually comes up in a first call.</p>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="split split--form">
      <div class="reveal">
        <div class="eyebrow" id="coa">COA lookup</div>
        <h2>Find the certificate for your lot.</h2>
        <p style="margin-top:16px;color:var(--muted);line-height:1.7">Enter the lot number printed on
          the vial label. If it is not indexed yet, we will send the certificate by email within one
          business day.</p>
        <form data-form="coa" style="margin-top:24px">
          <div class="field-row field-row--light" style="max-width:520px">
            <input type="text" required placeholder="Lot number, e.g. TL603-2409A" aria-label="Lot number">
            <button class="btn" type="submit">Look up {ar}</button>
          </div>
          <div class="form-ok" style="margin-top:14px" data-ok>{ck} Found. The COA for this lot is on
            its way to your inbox.</div>
        </form>
      </div>
      <div class="form-card reveal">
        <div class="eyebrow" style="margin-bottom:14px">Quick links</div>
        <div class="doclist">
          <a class="doc" href="#docs">{d}<b>Document library</b><span>{nsku} products · PDF</span></a>
          <a class="doc" href="docs/quality-overview.pdf" download>{d}<b>Quality system overview</b><span>PDF</span></a>
          <a class="doc" href="docs/dmf-summary.pdf" download>{d}<b>DMF filing summary</b><span>PDF</span></a>
          <a class="doc" href="contact.html#quote">{d}<b>DMF letter of authorisation</b><span>On request</span></a>
          <a class="doc" href="products.html">{d}<b>Full product catalogue</b><span>Web</span></a>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section" id="docs">
  <div class="container">
    <div class="section-head reveal">
      <div class="section-head__text">
        <div class="eyebrow">Document library</div>
        <h2>Every document, without asking.</h2>
        <p>Datasheets, representative certificates and safety data sheets for all {nsku} products.
          Lot-specific COAs ship with the order; anything that needs a signature is marked as such.</p>
      </div>
    </div>

    <div class="dlcards">
      <a class="dlcard" href="docs/quality-overview.pdf" download>
        <span class="dlcard__ico">{d}</span>
        <div><b>Quality system overview</b><span>ISO 13485 / 9001 scope, audit history · PDF</span></div>
        <i>Download</i>
      </a>
      <a class="dlcard" href="docs/dmf-summary.pdf" download>
        <span class="dlcard__ico">{d}</span>
        <div><b>DMF filing summary</b><span>038124 / 038820, how to reference · PDF</span></div>
        <i>Download</i>
      </a>
      <a class="dlcard" href="contact.html#quote">
        <span class="dlcard__ico dlcard__ico--lock">{lock}</span>
        <div><b>DMF letter of authorisation</b><span>Issued to the sponsor, not published</span></div>
        <i>Request</i>
      </a>
      <a class="dlcard" href="contact.html#quote">
        <span class="dlcard__ico dlcard__ico--lock">{lock}</span>
        <div><b>Quality agreement &amp; audit pack</b><span>Under NDA, before first GMP order</span></div>
        <i>Request</i>
      </a>
    </div>

    <div class="dltable">
      <table>
        <thead>
          <tr><th>Product</th><th>Family</th><th>Datasheet</th><th>COA</th><th>SDS</th></tr>
        </thead>
        <tbody>{dl_rows}</tbody>
      </table>
    </div>
    <p class="dl-note">{d} Representative COAs illustrate the test panel; the released certificate
      for your lot ships with the order. Files open in a new tab.</p>
  </div>
</section>

<section class="section section--mist">
  <div class="container">
    <div class="section-head reveal">
      <div class="section-head__text">
        <div class="eyebrow">Technical library</div>
        <h2>Notes from R&amp;D and regulatory.</h2>
        <p>Short, specific and written by the people who ran the experiment.</p>
      </div>
      <a class="link-arrow" href="#">All articles {ar}</a>
    </div>
    <div class="res">{cards}</div>
  </div>
</section>

<section class="section">
  <div class="container" style="max-width:920px">
    <div class="section-head reveal" id="faq">
      <div class="section-head__text">
        <div class="eyebrow">FAQ</div>
        <h2>The questions that come up first.</h2>
      </div>
    </div>
    <div class="faq">{faq}</div>
  </div>
</section>
</main>""".format(c=ic("chev"), ar=ic("arrow"), ck=ic("check"), d=ic("doc"),
                  cards=cards, faq=faq, dl_rows=dl_rows, nsku=NSKU, lock=ic("lock"))
    return head("Resources — T&L Biotechnology",
                "COA lookup, technical datasheets, quality documents and application notes for CGT reagents.",
                "resources") + header("Resources") + body + footer()


# --------------------------------------------------------------------------
# page: about
# --------------------------------------------------------------------------
def page_about():
    tl_items = [("2011", "Founded", "Company established as a CGT reagent developer."),
                ("2016", "Bead platform", "Cell-separation magnetic bead platform brought in-house."),
                ("2020", "ISO certified", "ISO 13485 and ISO 9001 quality systems in place."),
                ("2022", "DMF filed", "First Type II Drug Master File on record."),
                ("2024", "CGT Award", "\"Best Raw Material Supplier\" at CGT Asia 2024.")]
    tl = "".join("""
    <div class="tl"><div class="tl__y">{y}</div><div class="tl__t">{t}</div><div class="tl__d">{d}</div></div>
    """.format(y=y, t=e(t), d=e(d)) for y, t, d in tl_items)

    body = """
<main id="main">
<section class="phero">
  <div class="phero__grid"></div>
  <div class="container phero__inner">
    <div class="crumbs"><a href="index.html">Home</a>{c}<span>Company</span></div>
    <h1>A tool company that runs its own bench.</h1>
    <p>T&amp;L began in 2011 as a reagent developer for cell and gene therapy. The platform came
      later: once you own the assay data, the design models and the manufacturing, the same loop
      can produce tools for any workflow — not just the one you started with.</p>
    <div class="phero__meta">
      <span class="pill pill--brand">Est. 2011</span>
      <span class="pill">3,200 m² base</span>
      <span class="pill">50% R&amp;D and production</span>
      <span class="pill">AI for science</span>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="split">
      <div class="reveal">
        <div class="eyebrow">Who we are</div>
        <h2>Fifteen years, one loop.</h2>
        <p style="margin-top:16px;color:var(--muted);line-height:1.75">We started in 2011 with a
          narrow question: what would it take for a CGT developer to buy a critical reagent from a
          supplier who understood the regulatory path, not just the catalogue?</p>
        <p style="margin-top:14px;color:var(--muted);line-height:1.75">The answer was four tool
          families — magnetic beads, monoclonal antibodies, recombinant proteins and serum-free
          media — developed in-house, manufactured under ISO 13485 and ISO 9001, and documented to
          the level a sponsor needs when the file goes to a regulator.</p>
        <p style="margin-top:14px;color:var(--muted);line-height:1.75">The next step is the part
          that makes it a platform rather than a catalogue: instrumenting the data behind those
          tools, letting models propose what to build next, and qualifying outside capacity so
          throughput is not capped by one building.</p>
        <div class="hero__proof" style="border-top:0;padding-top:22px;margin-top:26px">
          <span>{ck} FDA DMF 038124</span><span>{ck} FDA DMF 038820</span>
          <span>{ck} ISO 13485:2016</span><span>{ck} ISO 9001</span>
        </div>
      </div>
      <div class="reveal">
        <div class="datapanel">
          <div class="datapanel__k">R&amp;D and production base</div>
          <div class="datapanel__n">3,200<small> m²</small></div>
          <div class="datapanel__grid">
            <div><b>2011</b><span>Company founded</span></div>
            <div><b>50%</b><span>Of staff in R&amp;D and production</span></div>
            <div><b>2</b><span>Type II DMFs on record</span></div>
            <div><b>30+</b><span>Customer audits supported</span></div>
          </div>
          <div class="datapanel__foot">
            <span>ISO 13485:2016</span><span>ISO 9001</span><span>GMP cleanroom</span>
          </div>
        </div>
        <p style="margin-top:14px;font-size:.8rem;color:var(--muted);line-height:1.6">
          Three in-house development platforms — magnetic beads, recombinant protein expression and
          serum-free media — under a single quality system.</p>
      </div>
    </div>
  </div>
</section>

<section class="section section--mist">
  <div class="container">
    <div class="section-head reveal">
      <div class="section-head__text">
        <div class="eyebrow">Capability</div>
        <h2>Three development platforms, one quality system.</h2>
        <p>Bead development, eukaryotic and prokaryotic protein expression, and serum-free medium
          formulation sit under the same quality system — which is why a change in one does not
          force a re-qualification of the others.</p>
      </div>
    </div>
    <div class="qgrid" style="grid-template-columns:repeat(3,1fr)">
      <div class="qcard reveal"><div class="qcard__ico">{m}</div><h3>Cell-separation magnetic beads</h3>
        <p>Particle synthesis, antibody coupling, blocking and release chemistry, from 50 nm
          nanobeads to 4.5 µm activation beads.</p></div>
      <div class="qcard reveal"><div class="qcard__ico">{p}</div><h3>Protein expression</h3>
        <p>E. coli, HEK293 and CHO expression with process development, purification and
          characterisation under one roof.</p></div>
      <div class="qcard reveal"><div class="qcard__ico">{f}</div><h3>Serum-free media</h3>
        <p>Chemically defined, animal-origin-free formulations for NK, MSC, PSC and HEK293
          suspension culture.</p></div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head reveal">
      <div class="section-head__text">
        <div class="eyebrow">Milestones</div>
        <h2>Fifteen years, five turns.</h2>
      </div>
    </div>
    <div class="timeline">{tl}</div>
  </div>
</section>

<section class="section section--ink">
  <div class="container">
    <div class="section-head reveal">
      <div class="section-head__text">
        <div class="eyebrow">Recognition</div>
        <h2>Best Raw Material Supplier, 2024.</h2>
        <p>Awarded at the 5th CGT Asia 2024 cell and gene therapy innovation summit in Shanghai —
          voted by the people who actually run these processes.</p>
      </div>
      <a class="link-arrow" href="quality.html">Quality &amp; regulatory {ar}</a>
    </div>
    <div class="dmf">
      <div class="dmf__card"><div><div class="dmf__k">Award</div>
        <div class="dmf__v">CGT Awards 2024 — Best Raw Material Supplier</div></div>
        <div class="dmf__no" style="font-size:1.1rem">2024</div></div>
      <div class="dmf__card"><div><div class="dmf__k">Customers served</div>
        <div class="dmf__v">Phase I and Phase I-correction programmes, plus 30+ audit packages</div></div>
        <div class="dmf__no" style="font-size:1.1rem">30+</div></div>
    </div>
  </div>
</section>

<section class="section" id="careers">
  <div class="container">
    <div class="split">
      <div class="reveal">
        <div class="eyebrow">Careers</div>
        <h2>We hire people who like the unglamorous part.</h2>
        <p style="margin-top:16px;color:var(--muted);line-height:1.75">Bead chemistry, purification
          development, QA documentation, regulatory affairs. If you have done the bench work and
          also care whether the batch record is right, we should talk.</p>
        <a class="btn btn--ghost" style="margin-top:24px" href="contact.html">Send an introduction {ar}</a>
      </div>
      <div class="form-card reveal">
        <h3 style="font-size:1.05rem;margin-bottom:14px">Open areas</h3>
        <div class="doclist">
          <a class="doc" href="contact.html">{u}<b>Bead conjugation scientist</b><span>R&amp;D</span></a>
          <a class="doc" href="contact.html">{u}<b>Protein purification engineer</b><span>Process</span></a>
          <a class="doc" href="contact.html">{u}<b>QA documentation specialist</b><span>Quality</span></a>
          <a class="doc" href="contact.html">{u}<b>Regulatory affairs associate</b><span>Regulatory</span></a>
        </div>
      </div>
    </div>
  </div>
</section>
</main>""".format(c=ic("chev"), ar=ic("arrow"), ck=ic("check"), lab=IMG + "/brand/lab-wide.webp",
                  tl=tl, m=ic("magnet"), p=ic("protein"), f=ic("flask"), u=ic("arrow-up-right"))
    return head("Company — T&L Biotechnology",
                "Founded 2011, 3,200 m² R&D and GMP base, ISO 13485 and ISO 9001 certified, FDA DMF filings on record.",
                "about") + header("Company") + body + footer()


# --------------------------------------------------------------------------
# page: contact
# --------------------------------------------------------------------------
def page_contact():
    body = """
<main id="main">
<section class="phero">
  <div class="phero__grid"></div>
  <div class="container phero__inner">
    <div class="crumbs"><a href="index.html">Home</a>{c}<span>Contact</span></div>
    <h1>Talk to someone who has run the assay.</h1>
    <p>Quote requests, technical questions, audit scheduling, DMF letters of authorisation.
      A named specialist replies within one business day.</p>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="split split--wide">
      <div class="form-card reveal" id="quote">
        <h2 style="font-size:1.55rem">Request a quote or technical call</h2>
        <p style="margin-top:10px;color:var(--muted);font-size:.94rem">The more you tell us about the
          process, the more useful the first reply will be.</p>
        <form style="margin-top:24px" data-form="contact">
          <div class="form-grid">
            <div class="fld"><label>Full name <i>*</i></label><input required placeholder="Jane Doe"></div>
            <div class="fld"><label>Work email <i>*</i></label><input type="email" required placeholder="jane@company.com"></div>
            <div class="fld"><label>Organisation <i>*</i></label><input required placeholder="Company / institute"></div>
            <div class="fld"><label>Country</label><input placeholder="United States"></div>
            <div class="fld"><label>I am interested in</label>
              <select>
                <option>Product quote</option>
                <option>GMP-grade supply</option>
                <option>DMF letter of authorisation</option>
                <option>Custom development</option>
                <option>Audit scheduling</option>
                <option>Distribution</option>
              </select></div>
            <div class="fld"><label>Application</label>
              <select>
                <option>T cell therapy</option><option>NK cell therapy</option>
                <option>MSC / regenerative</option><option>iPSC / pluripotent</option>
                <option>Hematopoietic</option><option>Dendritic / macrophage</option>
                <option>Other</option>
              </select></div>
            <div class="fld fld--full"><label>What are you working on?</label>
              <textarea placeholder="Cell type, scale, grade, timeline — and any product you are already looking at."></textarea></div>
          </div>
          <div style="display:flex;align-items:center;gap:18px;margin-top:20px;flex-wrap:wrap">
            <button class="btn" type="submit">Send request {ar}</button>
            <span class="form-note">By submitting you agree to be contacted about this enquiry.
              We do not sell contact data.</span>
          </div>
          <div class="form-ok" style="margin-top:16px" data-ok>{ck} Received. A specialist will reply
            within one business day.</div>
        </form>
      </div>
      <div class="reveal">
        <div class="qcard" style="margin-bottom:14px">
          <div class="qcard__ico">{pin}</div><h3>United States</h3>
          <p>6076 Corte Del Cedro<br>Carlsbad, CA 92011<br>United States</p>
          <p style="margin-top:10px"><a href="tel:{pr}" style="color:var(--brand);font-weight:600">{ph}</a><br>
            <a href="mailto:{em}" style="color:var(--brand);font-weight:600">{em}</a></p>
          <p style="margin-top:10px">Mon–Fri, 9:00–17:00 PT</p>
        </div>
        <div class="qcard" style="margin-bottom:14px">
          <div class="qcard__ico">{fac}</div><h3>Manufacturing &amp; R&amp;D</h3>
          <p>3,200 m² GMP cleanroom and R&amp;D laboratory. On-site and remote audits by
            appointment — allow two weeks for scheduling.</p>
          <a class="link-arrow" style="margin-top:12px;font-size:.85rem" href="#audit">Schedule an audit {ar}</a>
        </div>
        <div class="qcard">
          <div class="qcard__ico">{clock}</div><h3>Response times</h3>
          <p>Technical and quote enquiries: one business day.<br>
            COA requests: same day where the lot is indexed.<br>
            DMF letters: two business days after a technical agreement.</p>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section section--tight" id="audit">
  <div class="container">
    <div class="cta-band reveal">
      <div><h2>Prefer to start with a document?</h2>
        <p>Request the quality overview, a representative COA or the DMF letter of authorisation
          and skip the first call entirely.</p></div>
      <div style="display:flex;gap:10px;flex-wrap:wrap">
        <a class="btn btn--light" href="quality.html">Quality overview {ar}</a>
        <a class="btn btn--outline-light" href="resources.html#coa">COA lookup</a>
      </div>
    </div>
  </div>
</section>
</main>""".format(c=ic("chev"), ar=ic("arrow"), ck=ic("check"), pin=ic("pin"),
                  fac=ic("factory"), clock=ic("clock"),
                  pr=COMPANY["phone_raw"], ph=e(COMPANY["phone"]), em=e(COMPANY["email"]))
    return head("Contact — T&L Biotechnology",
                "Request a quote, technical support, DMF letter of authorisation or schedule an audit. Carlsbad, California.",
                "contact") + header("Contact") + body + footer()


# --------------------------------------------------------------------------
# data.js
# --------------------------------------------------------------------------
def write_data_js():
    payload = {
        "products": [dict(slug=p["slug"], name=p["name"], cat=p["cat"], apps=p["apps"],
                          price=p["price"], blurb=p["blurb"], desc=p["desc"],
                          highlights=p["highlights"], specs=p["specs"], sizes=p["sizes"])
                     for p in PRODUCTS],
        "cats": {c["id"]: c["name"] for c in CATEGORIES},
        "apps": {a["id"]: a["name"] for a in APPLICATIONS},
    }
    js = "window.TL = " + json.dumps(payload, ensure_ascii=False, indent=1) + ";\n"
    with open(os.path.join(OUT, "assets", "js", "data.js"), "w", encoding="utf-8") as f:
        f.write(js)


# --------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------
def main():
    os.makedirs(os.path.join(OUT, "assets", "js"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "assets", "css"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "assets", "fonts"), exist_ok=True)
    write_data_js()

    pages = {
        "index.html": page_home,
        "platform.html": page_platform,
        "products.html": page_products,
        "product.html": page_product,
        "applications.html": page_applications,
        "quality.html": page_quality,
        "services.html": page_services,
        "partners.html": page_partners,
        "resources.html": page_resources,
        "about.html": page_about,
        "contact.html": page_contact,
    }
    for name, fn in pages.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(fn())
        print("built", name)

    # favicon from logo
    src = os.path.join(OUT, "assets", "img", "brand", "logo-color.png")
    if os.path.exists(src):
        try:
            from PIL import Image
            im = Image.open(src).convert("RGBA")
            w, h = im.size
            # crop the T&L mark (left ~ 62% of the lockup, top 72%)
            im = im.crop((0, 0, int(w * 0.60), int(h * 0.72)))
            im.thumbnail((128, 128), Image.LANCZOS)
            im.save(os.path.join(OUT, "assets", "img", "brand", "favicon.png"))
            print("built favicon")
        except Exception as ex:
            print("favicon skipped:", ex)


if __name__ == "__main__":
    main()
