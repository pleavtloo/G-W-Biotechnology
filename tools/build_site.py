# -*- coding: utf-8 -*-
"""Static site generator for the G&W Biotechnologie GmbH redesign."""
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
"cart": '<circle cx="9.5" cy="20" r="1.5"/><circle cx="18.5" cy="20" r="1.5"/><path d="M2.5 3.5h2.6l2.5 11.4a2 2 0 0 0 2 1.6h8.6a2 2 0 0 0 1.9-1.5L22 8H6"/>',
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
PAGE_PATH = {
    "home": "/",
    "platform": "/platform.html",
    "products": "/products.html",
    "product": "/product.html",
    "applications": "/applications.html",
    "services": "/services.html",
    "quality": "/quality.html",
    "resources": "/resources.html",
    "about": "/about.html",
    "partners": "/partners.html",
    "contact": "/contact.html",
}

ORG_LD = {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": COMPANY["name"],
    "legalName": COMPANY["legal"],
    "url": COMPANY["site_url"],
    "logo": COMPANY["site_url"] + "/assets/img/brand/logo-mark.png",
    "foundingDate": str(COMPANY["founded"]),
    "email": COMPANY["email"],
    "telephone": COMPANY["phone"],
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "Pfarrer-Bergmann-Straße 59",
        "addressLocality": "Mainz",
        "addressRegion": "CA",
        "postalCode": "92011",
        "addressCountry": "US",
    },
    "description": "AI-designed, bench-validated life science tools: recombinant proteins, "
                   "antibodies, separation reagents and culture systems.",
}


def ld(obj):
    """Serialise JSON-LD without breaking on </script> inside strings."""
    import json
    return ('<script type="application/ld+json">%s</script>'
            % json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"))


PAGE_LABEL = {
    "platform": "Platform", "products": "Products", "product": "Product",
    "applications": "Applications", "services": "Services", "quality": "Quality",
    "resources": "Resources", "about": "Company", "partners": "Partners",
    "contact": "Contact",
}


def head(title, desc, page, extra="", jsonld=None, og_type="website", noindex=False):
    path = PAGE_PATH.get(page, "/" + page + ".html")
    url = COMPANY["site_url"] + path
    img = COMPANY["site_url"] + "/" + COMPANY["og_image"]
    blocks = [ORG_LD]
    if page != "home":
        blocks.append({
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home",
                 "item": COMPANY["site_url"] + "/"},
                {"@type": "ListItem", "position": 2,
                 "name": PAGE_LABEL.get(page, page.title()), "item": url},
            ],
        })
    if jsonld:
        blocks = blocks + (jsonld if isinstance(jsonld, list) else [jsonld])
    ld_html = "".join(ld(b) for b in blocks)
    robots = ('<meta name="robots" content="noindex,nofollow">' if noindex
              else '<meta name="robots" content="index,follow,max-image-preview:large">')
    tw = ""
    if COMPANY.get("twitter"):
        tw = ('<meta name="twitter:site" content="%s">' % e(COMPANY["twitter"]))
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
{robots}
<link rel="icon" type="image/png" href="assets/img/brand/favicon.png">
<link rel="apple-touch-icon" href="assets/img/brand/favicon.png">
<link rel="preload" href="assets/fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/css/style.css">
<meta property="og:site_name" content="{site}">
<meta property="og:locale" content="en_US">
<meta property="og:type" content="{ogtype}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{img}">
{tw}{extra}
{ld}
</head>
<body data-page="{page}">
<a class="skip" href="#main" style="position:absolute;left:-9999px">Skip to content</a>
""".format(title=e(title), desc=e(desc), page=page, extra=extra, url=url, img=img,
           robots=robots, tw=tw, ld=ld_html, ogtype=og_type,
           site=e(COMPANY["name"]))


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
             ("services.html#experts", "Application science", "Protocol review with a named scientist"),
             ("transmembrane-protein.html", "Transmembrane proteins",
              "VLP, detergent and nanodisc, with a paid feasibility stage")]
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
    links = [("about.html", "About G&W", "Facility, team and history"),
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
      <h4>Established 2011 · 3,400 m² R&amp;D and GMP base</h4>
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
      AI-designed tools · validated in a 3,400 m² lab · ISO 13485 &amp; ISO 9001 certified</div>
    <div class="topbar__links">
      <a href="platform.html">Platform</a>
      <a href="resources.html#coa">COA lookup</a>
      <a href="contact.html">+49 6131 000000</a>
    </div>
  </div>
</div>
<header class="header" id="header">
  <div class="container nav">
    <a class="brand" href="index.html" aria-label="G&W Biotechnologie GmbH — home">
      <img src="assets/img/brand/logo-mark.png" alt="G&amp;W Biotechnologie">
    </a>
    <nav class="nav__menu" aria-label="Primary">{lis}</nav>
    <div class="nav__actions">
      <button class="search-trigger" id="search-open" aria-label="Search products" aria-haspopup="dialog">
        {search}
        <span class="search-trigger__txt">Search {nsku} products</span>
        <kbd data-kbd>Ctrl K</kbd>
      </button>
      <a class="nav__account" id="nav-account" href="login.html">Sign in</a>
      <a class="cart-btn" id="cart-btn" href="cart.html" aria-label="Cart">
        {cart}<span class="cart-btn__count" id="cart-count" hidden>0</span>
      </a>
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
           cart=ic("cart"),
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
        <img src="assets/img/brand/logo-color.png" alt="G&W Biotechnologie GmbH" style="height:42px">
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
          <li><a href="transmembrane-protein.html">Transmembrane proteins</a></li>
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
          <li><a href="about.html">About G&W</a></li>
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
        <p>Pfarrer-Bergmann-Straße 59, 55127 Mainz<br>
        Tel +49 6131 000000 · Mon–Fri, 9:00–17:00 PT</p></div></div>
      <div class="office">{factory}<div><b>Manufacturing &amp; R&amp;D</b>
        <p>3,400 m² GMP cleanroom and R&amp;D laboratory<br>
        Bead, protein and serum-free medium platforms</p></div></div>
    </div>
    <div class="footer__legal">
      <span>© 2026 G&W Biotechnologie GmbH All rights reserved. For research use or further
        manufacturing use only.</span>
      <span class="footer__legal-links">
        <a href="contact.html">Contact</a>
        <a href="resources.html#faq">FAQ</a>
        <a href="shipping.html">Shipping &amp; returns</a>
        <a href="privacy.html">Privacy policy</a>
        <a href="terms.html">Terms of sale</a>
      </span>
    </div>
  </div>
</footer>
<div class="ai-widget" id="ai-widget">
  <button class="ai-launch" id="ai-launch" aria-expanded="false" aria-controls="ai-panel">
    <span class="ai-launch__av"><img src="assets/img/avatar/avatar-b1.jpg" alt=""></span>
    <span class="ai-launch__dot"></span>
    <span class="ai-launch__label">Ask G&W</span>
  </button>

  <div class="ai-panel" id="ai-panel" role="dialog" aria-modal="false" aria-label="G&W product and document lookup">
    <div class="ai-panel__head">
      <span class="ai-panel__av"><img src="assets/img/avatar/avatar-b1.jpg" alt=""></span>
      <div class="ai-panel__id">
        <div class="ai-panel__name">G&W Product Assistant</div>
        <div class="ai-panel__status"><i></i>Online · product &amp; document lookup · {nsku} SKUs</div>
      </div>
      <div class="ai-panel__acts">
        <button type="button" id="ai-close" title="Close" aria-label="Close">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6 6 18"/></svg>
        </button>
      </div>
    </div>

    <div class="ai-body" id="ai-body">
      <div class="ai-msg">
        <span class="ai-msg__av"><img src="assets/img/avatar/avatar-b1.jpg" alt=""></span>
        <div class="ai-bubble" id="ai-greeting">Ask about a product, a specification, a document or a lot number. For method design or choosing between two reagents, I will hand you to an application scientist.</div>
      </div>
      <div class="ai-chips" id="ai-chips">
        <button type="button" class="ai-chip">MaxSortin® CD3 bead size</button>
        <button type="button" class="ai-chip">Endotoxin spec for IL-7</button>
        <button type="button" class="ai-chip">Where is the COA for a lot?</button>
      </div>
    </div>

    <form class="ai-input" id="ai-form">
      <input type="text" id="ai-text" placeholder="Ask about a product, a spec or a document…" aria-label="Your question" autocomplete="off">
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
<script>
/* Cookie-free pageview ping. Failures never surface to the visitor. */
(function () {{
  try {{
    var body = JSON.stringify({{ p: location.pathname, r: document.referrer || "" }});
    if (!window.fetch) return;
    fetch("/api/hit", {{
      method: "POST",
      headers: {{ "content-type": "application/json" }},
      body: body,
      keepalive: true
    }}).catch(function () {{}});
  }} catch (e) {{}}
}})();
</script>
</body>
</html>
""".format(cats=cats, apps=apps, pin=ic("pin"), factory=ic("factory"), nsku=NSKU)


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
        ("scale", "3,400 m² GMP base", "Bead, protein and medium platforms under one roof"),
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
        <div><div class="chip-float__k">Facility</div><div class="chip-float__v">3,400 m² GMP</div></div>
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
      <span class="aiband__ask">Describe a target to the G&W AI — bottom right, any page</span>
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
      <div class="stat"><div class="stat__n" data-count="3400">3,400<small> m²</small></div>
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
    <p class="svc__more">
      <a href="transmembrane-protein.html">Full-length transmembrane proteins</a> &mdash;
      VLP, Detergent and Nanodisc formats, with a paid feasibility stage before scale-up.</p>
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
          replies within one business day (Mon–Fri) — with the datasheet, the DMF letter of authorisation
          if relevant, and a quote.</p>
      </div>
      <form class="cta-band__form" data-form="lead">
        <div class="field-row">
          <input type="email" required placeholder="Work email address" aria-label="Work email">
          <button class="btn btn--light" type="submit">Request</button>
        </div>
        <div class="cta-band__note">We reply from a named scientist, not a ticketing queue.
          No newsletters unless you ask.</div>
        <div class="form-ok" data-ok>{ck} Thanks — check your inbox for a reply within one business day (Mon–Fri).</div>
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
    # Brand line above the hero badge; the text lives in site.yaml so the
    # German site can carry its own.
    body = body.replace(
        '<div class="hero__badge"><b>FDA DMF filed</b>',
        '<div class="hero__eyebrow">' + e(COMPANY.get("slogan") or "") +
        '</div>\n      <div class="hero__badge"><b>FDA DMF filed</b>', 1)

    return head("G&W Biotechnologie GmbH — GMP raw materials for cell & gene therapy",
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
         ["%d catalogue products across five families" % NSKU,
          "GMP and RUO grades of the same design",
          "Custom builds when the catalogue does not fit"],
         "What it changes: a reagent you can qualify once and scale without a redesign."),
        ("d", "04", "Lab network", "Capacity to run the work",
         "Our own laboratory executes: expression, purification, assay, release. When volume exceeds "
         "one bench, qualified partner facilities absorb the overflow under our methods and our "
         "quality system.",
         ["3,400 m² in-house R&D and GMP base",
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
        ("We are not a generalist CRO.", "We do not take on every assay. We take work that extends the tool "
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
    return head("Platform — AI for science at G&W Biotechnologie GmbH",
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
    <p>{nsku} products across five families — cell separation and activation, monoclonal antibodies,
      recombinant proteins, serum-free media, and filtration consumables. Filter by family or by the
      cell type you work with.</p>
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
    return head("Products — G&W Biotechnologie GmbH",
                "Browse %d GMP-grade CGT reagents: cell separation beads, monoclonal antibodies, recombinant proteins and serum-free media." % NSKU,
                "products") + header("Products") + body + footer()


# --------------------------------------------------------------------------
# page: cart
# --------------------------------------------------------------------------
def page_cart():
    body = """
<main id="main">
<section class="phero phero--slim">
  <div class="phero__grid"></div>
  <div class="container phero__inner">
    <div class="crumbs"><a href="index.html">Home</a>{c}<span>Cart</span></div>
    <h1>Your cart</h1>
    <p>Review the pack sizes below, then send the enquiry. Prices are list prices in USD,
      excluding shipping and local duties.</p>
  </div>
</section>
<section class="section section--tight">
  <div class="container">
    <div class="cart-empty" id="cart-empty" hidden>
      <p><b>Your cart is empty.</b></p>
      <p>Browse the catalogue and add a pack size to get started.</p>
      <a class="btn" href="products.html">Browse products {ar}</a>
    </div>
    <div id="cart-body" hidden>
      <div class="cart-lines" id="cart-lines"></div>
      <div class="cart-foot">
        <div class="cart-total">Subtotal <b id="cart-subtotal">$0</b></div>
        <div class="cart-actions">
          <a class="btn" id="cart-checkout" href="checkout.html">Proceed to checkout {ar}</a>
          <a class="btn btn--ghost" id="cart-quote" href="contact.html#quote">Request a quote</a>
        </div>
      </div>
      <p class="cart-note">Shipping and taxes are quoted separately. GMP lots and process-scale
        quantities are quoted individually.</p>
    </div>
  </div>
</section>
</main>
""".format(c=ic("chev"), ar=ic("arrow"))
    return (head("Cart — G&W Biotechnologie GmbH", "Review the pack sizes in your cart.", "cart")
            + header("Cart") + body + footer())


# --------------------------------------------------------------------------
# page: checkout
# --------------------------------------------------------------------------
def page_checkout():
    body = """
<main id="main">
<section class="phero phero--slim">
  <div class="phero__grid"></div>
  <div class="container phero__inner">
    <div class="crumbs"><a href="index.html">Home</a>{c}<a href="cart.html">Cart</a>{c}<span>Checkout</span></div>
    <h1>Request an order</h1>
    <p>Tell us where to ship and we will confirm availability, shipping cost and lead time
      within one business day (Mon–Fri). No payment is taken on this page.</p>
  </div>
</section>
<section class="section section--tight">
  <div class="container checkout">
    <form class="checkout__form" data-form="checkout">
      <h2 class="checkout__h">Shipping details</h2>
      <div class="form-grid">
        <div class="fld"><label>Full name <i>*</i></label><input name="full_name" required placeholder="Jane Doe" autocomplete="name"></div>
        <div class="fld"><label>Work email <i>*</i></label><input name="work_email" type="email" required placeholder="jane@company.com" autocomplete="email"></div>
        <div class="fld"><label>Organisation <i>*</i></label><input name="organisation" required placeholder="Company / institute" autocomplete="organization"></div>
        <div class="fld"><label>Phone</label><input name="phone" placeholder="+1 555 0100" autocomplete="tel"></div>
        <div class="fld fld--wide"><label>Shipping address <i>*</i></label><input name="address" required placeholder="Street and number" autocomplete="street-address"></div>
        <div class="fld"><label>City</label><input name="city" autocomplete="address-level2"></div>
        <div class="fld"><label>Postal code</label><input name="postcode" autocomplete="postal-code"></div>
        <div class="fld"><label>Country <i>*</i></label><input name="country" required placeholder="United States" autocomplete="country-name"></div>
      </div>
      <div class="fld" style="margin-top:14px">
        <label>Notes for the team</label>
        <textarea name="notes" rows="3" placeholder="Delivery deadline, special handling, internal reference…"></textarea>
      </div>
      <h2 class="checkout__h" style="margin-top:26px">Payment</h2>
      <div class="pay-opts">
        <label class="pay-opt">
          <input type="radio" name="payment" value="bank_transfer" checked>
          <span><b>Bank transfer / purchase order</b>
            <em>We confirm stock, then email an invoice with our bank details.
              Payment due within 30 days of the invoice date. Nothing is charged now.</em></span>
        </label>
        <label class="pay-opt">
          <input type="radio" name="payment" value="online">
          <span><b>Card payment</b>
            <em>We confirm stock, then email a secure payment link within one business day (Mon–Fri).
              Card details are entered on Stripe's page, never on this site.</em></span>
        </label>
      </div>

      <div id="bank-fields" class="bank-block">
        <h3 class="bank-block__h">Invoice details</h3>
        <p class="bank-block__note">Only needed for bank transfer — these go on the invoice we email with our bank details.</p>
        <div class="form-grid">
          <div class="fld"><label>PO number</label>
            <input name="po_number" placeholder="Optional"></div>
          <div class="fld"><label>Invoice name</label>
            <input name="billing_name" placeholder="Legal entity to invoice"></div>
          <div class="fld"><label>VAT / tax ID</label>
            <input name="vat_number" placeholder="Optional"></div>
        </div>
      </div>

      <input type="hidden" name="order_items" id="order-items">
      <div class="form-ok" data-ok>Request received. We will confirm availability and shipping within one business day (Mon–Fri).</div>
      <button class="btn" type="submit" style="margin-top:18px">Submit order request {ar}</button>
      <p class="checkout__note">Submitting creates an enquiry, not a binding order. We confirm stock,
        shipping cost and lead time before anything ships.</p>
    </form>

    <aside class="checkout__side">
      <h2 class="checkout__h">Order summary</h2>
      <div id="checkout-summary"></div>
      <a class="checkout__edit" href="cart.html">Edit cart</a>
    </aside>
  </div>
</section>
</main>
""".format(c=ic("chev"), ar=ic("arrow"))
    return (head("Checkout — G&W Biotechnologie GmbH", "Request an order and we confirm within one business day (Mon–Fri).", "checkout")
            + header("Checkout") + body + footer())


# --------------------------------------------------------------------------
# page: manage (own admin UI, replaces the GitHub-backed editor)
# --------------------------------------------------------------------------
def page_manage():
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Manage — G&W Biotechnologie GmbH</title>
<link rel="icon" href="assets/img/brand/favicon-128.png">
<link rel="stylesheet" href="assets/css/style.css">
<style>
  html, body { height: 100%; margin: 0; }
  body.mg-body { background: #f4f6f9; font-size: 14px; }
  /* display:flex below would otherwise beat the hidden attribute */
  [hidden] { display: none !important; }

  .mg { display: grid; grid-template-columns: 208px 300px minmax(0, 1fr); height: 100vh; }

  /* left rail */
  .mg__nav { background: #101828; color: #c8d2e0; padding: 18px 14px; display: flex; flex-direction: column; gap: 18px; }
  .mg__brand { font-size: 14px; font-weight: 700; color: #fff; letter-spacing: .02em; }
  .mg__brand span { display: block; font-size: 11px; font-weight: 500; color: #7c8ba1; margin-top: 2px; letter-spacing: .06em; }
  .mg__nav nav { display: flex; flex-direction: column; gap: 2px; }
  .mg__nav nav button { text-align: left; padding: 9px 11px; border: 0; border-radius: 8px; background: none; color: inherit; font: inherit; cursor: pointer; }
  .mg__nav nav button:hover { background: #1b2537; color: #fff; }
  .mg__nav nav button.is-on { background: #1d4ed8; color: #fff; }
  .mg__user { margin-top: auto; font-size: 12px; color: #7c8ba1; display: flex; flex-direction: column; gap: 8px; }
  .mg__user button { padding: 7px; border: 1px solid #2c3a4f; border-radius: 7px; background: none; color: #c8d2e0; font: inherit; cursor: pointer; }
  .mg__user button:hover { border-color: #4a5b74; color: #fff; }

  /* middle: list */
  .mg__list { background: #fff; border-right: 1px solid #e3e8ef; display: flex; flex-direction: column; min-height: 0; }
  .mg__listhead { padding: 14px; border-bottom: 1px solid #eef1f6; display: flex; gap: 8px; }
  .mg__listhead input { flex: 1; min-width: 0; padding: 8px 10px; border: 1px solid #d5dce6; border-radius: 8px; font: inherit; }
  .mg__listhead button { padding: 8px 12px; border: 0; border-radius: 8px; background: #1d4ed8; color: #fff; font: inherit; cursor: pointer; white-space: nowrap; }
  .mg__filters { display: flex; gap: 8px; padding: 0 14px 12px; border-bottom: 1px solid #eef1f6; }
  .mg__filters select, .mg__filters button { padding: 7px 10px; border: 1px solid #d5dce6; border-radius: 8px; background: #fff; font: inherit; font-size: 12.5px; }
  .mg__filters button { cursor: pointer; }
  .mg__filters button:hover { border-color: #b9c4d4; }
  .mg__items { overflow: auto; flex: 1; }
  .mg__item { padding: 11px 14px; border-bottom: 1px solid #f2f5f9; cursor: pointer; display: flex; gap: 8px; align-items: flex-start; width: 100%; text-align: left; border-left: 3px solid transparent; background: none; font: inherit; color: inherit; }
  .mg__item:hover { background: #f8fafc; }
  .mg__item.is-on { background: #eff4ff; border-left-color: #1d4ed8; }
  .mg__item b { display: block; font-size: 13px; font-weight: 600; line-height: 1.35; }
  .mg__item span { display: block; font-size: 11.5px; color: #8b97a8; margin-top: 2px; font-family: ui-monospace, Menlo, Consolas, monospace; }

  /* right: editor */
  .mg__edit { overflow: auto; padding: 20px 24px 80px; min-height: 0; }
  .mg__empty { color: #8b97a8; padding: 60px 0; text-align: center; }
  .mg__hd { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; margin-bottom: 18px; }
  .mg__hd h2 { margin: 0; font-size: 17px; }
  .mg__hd p { margin: 4px 0 0; font-size: 12px; color: #8b97a8; font-family: ui-monospace, Menlo, Consolas, monospace; }

  .mg-field { margin-bottom: 15px; }
  .mg-field > label { display: block; font-size: 12px; font-weight: 600; color: #475467; margin-bottom: 5px; }
  .mg-field > label em { font-style: normal; color: #98a2b3; font-weight: 500; }
  .mg-field input[type=text], .mg-field input[type=number], .mg-field textarea, .mg-field select {
    width: 100%; padding: 8px 10px; border: 1px solid #d5dce6; border-radius: 8px;
    font: inherit; background: #fff; box-sizing: border-box;
  }
  .mg-field textarea { resize: vertical; min-height: 74px; line-height: 1.55; }
  .mg-field input[readonly] { background: #f6f7f9; color: #667085; }
  .mg-hint { font-size: 11.5px; color: #98a2b3; margin-top: 4px; }

  .mg-variants { border: 1px solid #e3e8ef; border-radius: 10px; overflow: hidden; }
  .mg-variants table { width: 100%; border-collapse: collapse; }
  .mg-variants th { text-align: left; font-size: 11px; text-transform: uppercase; letter-spacing: .04em; color: #667085; background: #f8fafc; padding: 8px 10px; font-weight: 600; }
  .mg-variants td { padding: 4px 6px; border-top: 1px solid #eef1f6; }
  .mg-variants input { width: 100%; padding: 6px 8px; border: 1px solid #e3e8ef; border-radius: 6px; font: inherit; font-size: 13px; box-sizing: border-box; }
  .mg-variants .mg-del { border: 0; background: none; color: #b42318; cursor: pointer; font-size: 15px; padding: 2px 6px; }
  .mg-add { margin-top: 8px; padding: 6px 12px; border: 1px dashed #c6d0dd; border-radius: 8px; background: #fff; font: inherit; font-size: 12px; cursor: pointer; color: #475467; }

  .mg-kv { border: 1px solid #e3e8ef; border-radius: 10px; padding: 8px; }
  /* rich text editor */
  .mg-rich { border: 1px solid #d5dce6; border-radius: 8px; overflow: hidden; background: #fff; }
  .mg-rich__bar { display: flex; gap: 4px; flex-wrap: wrap; padding: 6px; background: #f8fafc; border-bottom: 1px solid #eef1f6; }
  .mg-rich__area { padding: 10px 12px; min-height: 120px; max-height: 420px; overflow: auto; font-size: 13.5px; line-height: 1.6; outline: none; }
  .mg-rich__area:focus { background: #fdfdff; }
  .mg-rich__area p { margin: 0 0 10px; }
  .mg-rich__area h2 { font-size: 15px; margin: 14px 0 8px; }
  .mg-rich__area h3 { font-size: 13.5px; margin: 12px 0 6px; }
  .mg-rich__area ul, .mg-rich__area ol { margin: 0 0 10px; padding-left: 20px; }
  .mg-rich__area table { width: 100%; border-collapse: collapse; margin: 8px 0 12px; font-size: 12.5px; }
  .mg-rich__area th, .mg-rich__area td { border: 1px solid #d5dce6; padding: 5px 8px; text-align: left; }
  .mg-rich__area th { background: #f4f6f9; font-weight: 600; }
  .mg-rich__area a { color: #1d4ed8; }

  .mg-kv .row { display: grid; grid-template-columns: 170px 1fr 28px; gap: 6px; margin-bottom: 6px; }
  .mg-kv input { width: 100%; padding: 6px 8px; border: 1px solid #e3e8ef; border-radius: 6px; font: inherit; font-size: 13px; box-sizing: border-box; }

  .mg-bar { position: fixed; bottom: 0; right: 0; left: 508px; background: #fff; border-top: 1px solid #e3e8ef; padding: 12px 24px; display: flex; align-items: center; gap: 14px; }
  .mg-bar button { padding: 9px 18px; border: 0; border-radius: 9px; background: #1d4ed8; color: #fff; font: inherit; font-weight: 600; cursor: pointer; }
  .mg-bar button:disabled { opacity: .55; cursor: default; }
  .mg-bar .mg-status { font-size: 12.5px; color: #667085; }
  .mg-bar .mg-status.is-ok { color: #0f7a48; }
  .mg-bar .mg-status.is-bad { color: #b42318; }
  .mg-bar .mg-log { font: 11px/1.5 ui-monospace, Menlo, Consolas, monospace; color: #b42318; background: #fef3f2; border-radius: 6px; padding: 6px 8px; max-height: 90px; overflow: auto; white-space: pre-wrap; max-width: 520px; }

  @media (max-width: 1100px) {
    .mg { grid-template-columns: 168px 240px minmax(0, 1fr); }
    .mg-bar { left: 408px; }
  }
</style>
</head>
<body class="mg-body">
<div class="mg">
  <aside class="mg__nav">
    <div class="mg__brand">G&W Manage<span>CONTENT WORKSPACE</span></div>
    <nav id="mg-types"></nav>
    <div class="mg__user">
      <span id="mg-who">…</span>
      <button type="button" id="mg-out">Sign out</button>
    </div>
  </aside>

  <section class="mg__list">
    <div class="mg__listhead">
      <input id="mg-search" placeholder="Search…" autocomplete="off">
      <button type="button" id="mg-batch" hidden>Batch</button>
      <button type="button" id="mg-new">+ New</button>
    </div>
    <div class="mg__filters" id="mg-filters" hidden>
      <select id="mg-status">
        <option value="">All statuses</option>
        <option value="new">new</option>
        <option value="confirmed">confirmed</option>
        <option value="paid">paid</option>
        <option value="shipped">shipped</option>
        <option value="cancelled">cancelled</option>
      </select>
      <button type="button" id="mg-export">Export CSV</button>
    </div>
    <div class="mg__items" id="mg-items"></div>
  </section>

  <section class="mg__edit" id="mg-edit">
    <div class="mg__empty">Pick something on the left to edit.</div>
  </section>
</div>

<div class="mg-bar" id="mg-bar" hidden>
  <button type="button" id="mg-save">Save &amp; publish</button>
  <span class="mg-status" id="mg-status"></span>
  <pre class="mg-log" id="mg-log" hidden></pre>
</div>

<div class="mg-bar" id="mg-bulk" hidden>
  <b id="mg-bulk-count">0 selected</b>
  <span id="mg-bulk-btns" style="display:flex;gap:8px;flex-wrap:wrap"></span>
  <button type="button" id="mg-bulk-exit" style="background:#fff;color:#344054;border:1px solid #d5dce6">
    Done
  </button>
  <span class="mg-status" id="mg-bulk-status"></span>
</div>

<script src="assets/js/manage.js"></script>
</body>
</html>"""


# --------------------------------------------------------------------------
# pages: account (register / sign in)
# --------------------------------------------------------------------------
AUTH_JS = """
<script>
(function () {
  function post(url, data) {
    return fetch(url, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(data)
    }).then(function (r) { return r.json().catch(function () { return {}; }); });
  }

  function err(el, msg) {
    el.textContent = msg;
    el.hidden = !msg;
  }

  var reg = document.getElementById("reg-form");
  if (reg) {
    reg.addEventListener("submit", function (e) {
      e.preventDefault();
      var btn = reg.querySelector("button");
      var box = document.getElementById("reg-err");
      var data = Object.fromEntries(new FormData(reg).entries());
      btn.disabled = true;
      btn.textContent = "Creating…";
      post("/api/register", data).then(function (d) {
        if (!d.ok) {
          err(box, d.error || "Could not create the account.");
          btn.disabled = false;
          btn.textContent = "Create account";
          return;
        }
        var wantNext = new URLSearchParams(location.search).get("next") || "";
        if (!/^[a-z0-9-]+\.html$/i.test(wantNext)) wantNext = "";
        reg.outerHTML = '<p class="auth__ok">Account created. We review every account ' +
          'individually and will email you within one business day (Mon–Fri).' +
          (wantNext ? ' <a href="' + wantNext + '">Return to checkout</a>.' : "") + "</p>";
      }).catch(function () {
        err(box, "Network error. Please try again.");
        btn.disabled = false;
        btn.textContent = "Create account";
      });
    });
  }

  var signin = document.getElementById("login-form");
  if (signin) {
    signin.addEventListener("submit", function (e) {
      e.preventDefault();
      var btn = signin.querySelector("button");
      var box = document.getElementById("login-err");
      var data = Object.fromEntries(new FormData(signin).entries());
      btn.disabled = true;
      btn.textContent = "Signing in…";
      post("/api/login", data).then(function (d) {
        if (!d.ok) {
          err(box, d.error || "Email or password is incorrect.");
          btn.disabled = false;
          btn.textContent = "Sign in";
          return;
        }
        var next = new URLSearchParams(location.search).get("next") || "";
        if (!/^[a-z0-9-]+\.html$/i.test(next)) next = "";
        location.href = next ||
          ((d.user && d.user.role === "admin") ? "manage.html" : "account.html");
      }).catch(function () {
        err(box, "Network error. Please try again.");
        btn.disabled = false;
        btn.textContent = "Sign in";
      });
    });
  }
})();
</script>
"""


def page_register():
    body = """
<main id="main">
<section class="section" style="padding-top:132px">
  <div class="container auth">
    <h1 class="auth__h">Create an account</h1>
    <p class="auth__sub">We review every account individually so we can price and ship correctly.
      You will hear from us within one business day (Mon–Fri).</p>
    <form id="reg-form" class="auth__form" novalidate>
      <div class="fld"><label>Full name <i>*</i></label>
        <input name="name" required autocomplete="name" placeholder="Jane Doe"></div>
      <div class="fld"><label>Work email <i>*</i></label>
        <input name="email" type="email" required autocomplete="email" placeholder="jane@company.com"></div>
      <div class="fld"><label>Organisation <i>*</i></label>
        <input name="company" required autocomplete="organization" placeholder="Company / institute"></div>
      <div class="fld"><label>Password <i>*</i></label>
        <input name="password" type="password" required minlength="8" autocomplete="new-password">
        <span class="auth__hint">At least 8 characters.</span></div>
      <p class="auth__err" id="reg-err" hidden></p>
      <button class="btn" type="submit">Create account</button>
    </form>
    <p class="auth__alt">Already have an account? <a href="login.html">Sign in</a></p>
  </div>
</section>
</main>""" + AUTH_JS
    return (head("Create an account — G&W Biotechnologie GmbH",
                 "Register for a G&W Biotechnologie GmbH account.", "register", noindex=True)
            + header("Register") + body + footer())


def page_forgot():
    body = """
<main id="main">
<section class="section" style="padding-top:132px">
  <div class="container auth">
    <h1 class="auth__h">Reset your password</h1>
    <p class="auth__sub">Enter the email you registered with and we will send a link to set a new
      password. The link works once and expires in one hour.</p>
    <form id="forgot-form" class="auth__form" novalidate>
      <div class="fld"><label>Work email</label>
        <input name="email" type="email" required autocomplete="email" placeholder="jane@company.com"></div>
      <p class="auth__err" id="forgot-err" hidden></p>
      <p class="auth__ok" id="forgot-ok" hidden></p>
      <button class="btn" type="submit">Send reset link</button>
    </form>
    <p class="auth__alt">Remembered it? <a href="login.html">Sign in</a></p>
  </div>
</section>
</main>
<script>
(function () {
  var form = document.getElementById("forgot-form");
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var btn = form.querySelector("button");
    var err = document.getElementById("forgot-err");
    var ok = document.getElementById("forgot-ok");
    err.hidden = true;
    ok.hidden = true;
    btn.disabled = true;
    btn.textContent = "Sending…";
    fetch("/api/forgot", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ email: form.email.value })
    }).then(function (r) { return r.json(); }).then(function (d) {
      btn.disabled = false;
      btn.textContent = "Send reset link";
      if (!d.ok) {
        err.textContent = d.error || "Could not send the link.";
        err.hidden = false;
        return;
      }
      ok.textContent = d.message || "If that address has an account, a reset link is on its way.";
      ok.hidden = false;
      form.reset();
    }).catch(function () {
      btn.disabled = false;
      btn.textContent = "Send reset link";
      err.textContent = "Network error. Please try again.";
      err.hidden = false;
    });
  });
})();
</script>
"""
    return (head("Reset password — G&W Biotechnologie GmbH", "Reset your account password.",
                 "forgot", noindex=True) + header("Reset") + body + footer())


def page_reset():
    body = """
<main id="main">
<section class="section" style="padding-top:132px">
  <div class="container auth">
    <h1 class="auth__h">Set a new password</h1>
    <p class="auth__sub">Choose a password of at least 8 characters.</p>
    <form id="reset-form" class="auth__form" novalidate>
      <div class="fld"><label>New password</label>
        <input name="password" type="password" required minlength="8" autocomplete="new-password"></div>
      <div class="fld"><label>Confirm new password</label>
        <input name="confirm" type="password" required minlength="8" autocomplete="new-password"></div>
      <p class="auth__err" id="reset-err" hidden></p>
      <p class="auth__ok" id="reset-ok" hidden>Password updated. You can sign in now.</p>
      <button class="btn" type="submit">Update password</button>
    </form>
    <p class="auth__alt"><a href="login.html">Back to sign in</a></p>
  </div>
</section>
</main>
<script>
(function () {
  var token = new URLSearchParams(location.search).get("token") || "";
  var form = document.getElementById("reset-form");
  var err = document.getElementById("reset-err");
  var ok = document.getElementById("reset-ok");

  if (!/^[a-f0-9]{64}$/.test(token)) {
    form.hidden = true;
    err.textContent = "This link is not valid. Ask for a new one on the reset page.";
    err.hidden = false;
    return;
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var btn = form.querySelector("button");
    err.hidden = true;
    ok.hidden = true;
    if (form.password.value !== form.confirm.value) {
      err.textContent = "The two passwords do not match.";
      err.hidden = false;
      return;
    }
    btn.disabled = true;
    btn.textContent = "Updating…";
    fetch("/api/reset", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ token: token, password: form.password.value })
    }).then(function (r) { return r.json(); }).then(function (d) {
      btn.disabled = false;
      btn.textContent = "Update password";
      if (!d.ok) {
        err.textContent = d.error || "Could not update the password.";
        err.hidden = false;
        return;
      }
      ok.hidden = false;
      form.reset();
      setTimeout(function () { location.href = "login.html"; }, 1800);
    }).catch(function () {
      btn.disabled = false;
      btn.textContent = "Update password";
      err.textContent = "Network error. Please try again.";
      err.hidden = false;
    });
  });
})();
</script>
"""
    return (head("Set a new password — G&W Biotechnologie GmbH", "Choose a new password.",
                 "reset", noindex=True) + header("Reset") + body + footer())


def page_login():
    body = """
<main id="main">
<section class="section" style="padding-top:132px">
  <div class="container auth">
    <h1 class="auth__h">Sign in</h1>
    <p class="auth__sub">Your account shows pricing, previous orders and saved shipping details.</p>
    <form id="login-form" class="auth__form" novalidate>
      <div class="fld"><label>Work email</label>
        <input name="email" type="email" required autocomplete="email" placeholder="jane@company.com"></div>
      <div class="fld"><label>Password</label>
        <input name="password" type="password" required autocomplete="current-password"></div>
      <p class="auth__err" id="login-err" hidden></p>
      <button class="btn" type="submit">Sign in</button>
    </form>
    <p class="auth__alt">No account yet? <a href="register.html">Create one</a></p>
    <p class="auth__alt"><a href="forgot.html">Forgot your password?</a></p>
  </div>
</section>
</main>""" + AUTH_JS
    return (head("Sign in — G&W Biotechnologie GmbH",
                 "Sign in to your G&W Biotechnologie GmbH account.", "login", noindex=True)
            + header("Sign in") + body + footer())


# --------------------------------------------------------------------------
# page: one order (customer view)
# --------------------------------------------------------------------------
def page_order_detail():
    body = """
<main id="main">
<section class="section" style="padding-top:132px">
  <div class="container account">
    <p id="ord-loading" style="color:var(--muted)">Loading…</p>
    <p id="ord-error" class="auth__err" hidden></p>
    <div id="ord-body" hidden></div>
  </div>
</section>
</main>
<script>
(function () {
  function money(n) {
    return "$" + Number(n || 0).toLocaleString("en-US", { maximumFractionDigits: 2 });
  }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function when(ms) {
    var d = new Date(ms || Date.now());
    return d.toISOString().slice(0, 10) + " " + d.toTimeString().slice(0, 5);
  }

  var id = new URLSearchParams(location.search).get("id") || "";
  if (!/^[A-Za-z0-9-]+$/.test(id)) {
    document.getElementById("ord-loading").hidden = true;
    var e0 = document.getElementById("ord-error");
    e0.textContent = "No order specified.";
    e0.hidden = false;
    return;
  }

  fetch("/api/order/" + encodeURIComponent(id)).then(function (r) {
    if (r.status === 401) { location.href = "login.html?next=" + encodeURIComponent("order.html?id=" + id); throw new Error("auth"); }
    return r.json();
  }).then(function (d) {
    if (!d.ok) throw new Error(d.error || "not found");
    var o = d.order;
    var f = o.fields || {};
    var paid = o.status === "paid" || o.status === "shipped";

    var rows = (o.items || []).map(function (it) {
      var amount = it.price == null ? "—" : money(Number(it.price) * Number(it.qty));
      return '<tr>' +
        "<td>" + esc(it.sku || "—") + "</td>" +
        "<td>" + esc(it.name || "") + "<br><span class=\\"ord-sub\\">" + esc(it.spec || "") + "</span></td>" +
        "<td style='text-align:center'>" + esc(it.qty) + "</td>" +
        "<td style='text-align:right'>" + (it.price == null ? "on request" : money(it.price)) + "</td>" +
        "<td style='text-align:right'>" + amount + "</td>" +
        "</tr>";
    }).join("");

    document.getElementById("ord-body").innerHTML =
      '<div class="account__head"><div>' +
        "<h1 class='auth__h'>Order " + esc(o.id) + "</h1>" +
        '<p class="auth__sub">Placed ' + when(o.t) + " · " +
        '<span class="o-status o-status--' + esc(o.status) + '">' + esc(o.status) + "</span></p>" +
      "</div></div>" +

      "<h2 class='account__h'>Items</h2>" +
      '<table class="ord-table"><thead><tr>' +
        "<th>Catalogue no.</th><th>Description</th><th>Qty</th><th>Unit</th><th>Amount</th>" +
      "</tr></thead><tbody>" + rows + "</tbody>" +
      '<tfoot><tr><td colspan="4" style="text-align:right">Subtotal</td>' +
      '<td style="text-align:right"><b>' + money(o.total) + "</b></td></tr></tfoot></table>" +
      '<p class="cart-note">Shipping and any applicable taxes are quoted separately.</p>' +

      "<h2 class='account__h' style='margin-top:28px'>Delivery</h2>" +
      '<div class="ord-kv">' +
        "<div><span>Name</span><b>" + esc(f.full_name || "—") + "</b></div>" +
        "<div><span>Company</span><b>" + esc(f.organisation || "—") + "</b></div>" +
        "<div><span>Email</span><b>" + esc(f.work_email || "—") + "</b></div>" +
        "<div><span>Phone</span><b>" + esc(f.phone || "—") + "</b></div>" +
        "<div><span>Ship to</span><b>" +
          esc([f.address, f.city, f.postcode, f.country].filter(Boolean).join(", ") || "—") +
        "</b></div>" +
      "</div>" +

      "<h2 class='account__h' style='margin-top:28px'>Payment</h2>" +
      '<div class="ord-kv">' +
        "<div><span>Method</span><b>" +
          (o.payment === "bank_transfer" ? "Bank transfer / purchase order" : "Card") + "</b></div>" +
        (f.po_number ? "<div><span>PO number</span><b>" + esc(f.po_number) + "</b></div>" : "") +
        (f.billing_name ? "<div><span>Invoice to</span><b>" + esc(f.billing_name) + "</b></div>" : "") +
        (f.vat_number ? "<div><span>VAT / tax ID</span><b>" + esc(f.vat_number) + "</b></div>" : "") +
        "<div><span>Status</span><b>" + (paid ? "Paid" : "Awaiting payment") + "</b></div>" +
      "</div>" +
      (f.notes ? "<p class='ord-notes'><b>Your note:</b> " + esc(f.notes) + "</p>" : "") +

      '<div class="ord-actions">' +
        '<a class="btn" href="/api/invoice/' + encodeURIComponent(o.id) +
          '" target="_blank" rel="noopener">Invoice (PDF)</a>' +
        '<a class="btn btn--ghost" href="account.html">Back to my account</a>' +
        '<a class="btn btn--ghost" href="contact.html">Ask about this order</a>' +
      "</div>";

    document.getElementById("ord-loading").hidden = true;
    document.getElementById("ord-body").hidden = false;
  }).catch(function (err) {
    if (err.message === "auth") return;
    document.getElementById("ord-loading").hidden = true;
    var box = document.getElementById("ord-error");
    box.textContent = "We could not open that order. " +
      (err.message === "not found" ? "It may belong to a different account." : "");
    box.hidden = false;
  });
})();
</script>
"""
    return (head("Order — G&W Biotechnologie GmbH", "Your order details.", "order", noindex=True)
            + header("Order") + body + footer())


# --------------------------------------------------------------------------
# page: my account
# --------------------------------------------------------------------------
def page_account():
    body = """
<main id="main">
<section class="section" style="padding-top:132px">
  <div class="container account">
    <p id="acct-loading" style="color:var(--muted)">Loading…</p>
    <div id="acct-body" hidden>
      <div class="account__head">
        <div>
          <h1 class="auth__h" id="acct-name">—</h1>
          <p class="auth__sub" id="acct-meta"></p>
        </div>
        <button class="btn btn--ghost" id="acct-out" type="button">Sign out</button>
      </div>
      <div id="acct-status" class="account__status" hidden></div>
      <h2 class="account__h">Order requests</h2>
      <div id="acct-orders"></div>

      <h2 class="account__h" style="margin-top:36px">Change password</h2>
      <form id="pw-form" class="auth__form" style="max-width:380px" novalidate>
        <div class="fld"><label>Current password</label>
          <input name="current" type="password" required autocomplete="current-password"></div>
        <div class="fld"><label>New password</label>
          <input name="next" type="password" required minlength="8" autocomplete="new-password">
          <span class="auth__hint">At least 8 characters.</span></div>
        <div class="fld"><label>Confirm new password</label>
          <input name="confirm" type="password" required minlength="8" autocomplete="new-password"></div>
        <p class="auth__err" id="pw-err" hidden></p>
        <p class="auth__ok" id="pw-ok" hidden>Password updated.</p>
        <button class="btn" type="submit">Update password</button>
      </form>
    </div>
  </div>
</section>
</main>
<script>
(function () {
  function money(n) {
    return "$" + Number(n || 0).toLocaleString("en-US", { maximumFractionDigits: 2 });
  }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function when(ms) {
    var d = new Date(ms);
    return d.toISOString().slice(0, 10);
  }

  function render(d) {
    var u = d.user || {};
    document.getElementById("acct-name").textContent = u.name || "Your account";
    document.getElementById("acct-meta").textContent =
      [u.company, u.email].filter(Boolean).join(" · ");

    var box = document.getElementById("acct-status");
    if (u.status === "pending") {
      box.hidden = false;
      box.innerHTML = "<b>Awaiting approval.</b> We review every account individually. " +
        "You can browse and build a cart, and checkout opens as soon as we approve you " +
        "(usually within one business day (Mon–Fri)).";
    } else if (u.status === "rejected") {
      box.hidden = false;
      box.innerHTML = "<b>This account was not approved.</b> " +
        '<a href="contact.html">Contact us</a> if you think this is a mistake.';
    }

    var list = d.orders || [];
    var host = document.getElementById("acct-orders");
    if (!list.length) {
      host.innerHTML = '<p style="color:var(--muted)">No orders yet. ' +
        '<a href="products.html">Browse the catalogue</a>.</p>';
    } else {
      host.innerHTML = list.map(function (o) {
        var items = (o.items || []).map(function (it) {
          return esc(it.spec) + " × " + it.qty;
        }).join(", ");
        return '<div class="acct-order">' +
          '<div class="acct-order__top"><b>' + esc(o.id) + "</b>" +
          '<span class="o-status o-status--' + esc(o.status) + '">' + esc(o.status) + "</span></div>" +
          '<div class="acct-order__meta">' + when(o.t) + " · " + money(o.total) + "</div>" +
          '<div class="acct-order__items">' + items + "</div>" +
          '<div class="acct-order__actions">' +
          '<a href="order.html?id=' + esc(o.id) + '">View details</a>' +
          '<a href="/api/invoice/' + esc(o.id) +
          '" target="_blank" rel="noopener">Invoice (PDF)</a></div>' +
          "</div>";
      }).join("");
    }

    document.getElementById("acct-loading").hidden = true;
    document.getElementById("acct-body").hidden = false;
  }

  document.getElementById("acct-out").addEventListener("click", function () {
    fetch("/api/logout", { method: "POST" }).then(function () {
      location.href = "index.html";
    });
  });

  var pwForm = document.getElementById("pw-form");
  if (pwForm) {
    pwForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var err = document.getElementById("pw-err");
      var ok = document.getElementById("pw-ok");
      var btn = pwForm.querySelector("button");
      err.hidden = true;
      ok.hidden = true;

      if (pwForm.next.value !== pwForm.confirm.value) {
        err.textContent = "The two new passwords do not match.";
        err.hidden = false;
        return;
      }
      btn.disabled = true;
      btn.textContent = "Updating…";
      fetch("/api/password", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ current: pwForm.current.value, next: pwForm.next.value }),
      }).then(function (r) { return r.json(); }).then(function (d) {
        btn.disabled = false;
        btn.textContent = "Update password";
        if (!d.ok) {
          err.textContent = d.error || "Could not update the password.";
          err.hidden = false;
          return;
        }
        ok.hidden = false;
        pwForm.reset();
      }).catch(function () {
        btn.disabled = false;
        btn.textContent = "Update password";
        err.textContent = "Network error. Please try again.";
        err.hidden = false;
      });
    });
  }

  fetch("/api/my-orders").then(function (r) {
    if (r.status === 401) {
      location.href = "login.html";
      throw new Error("redirect");
    }
    return r.json();
  }).then(render).catch(function () {});
})();
</script>
"""
    return (head("My account — G&W Biotechnologie GmbH", "Your account and orders.",
                 "account", noindex=True) + header("Account") + body + footer())


# --------------------------------------------------------------------------
# pages: legal (text lives in content/legal/*.txt so it can be edited in place)
# --------------------------------------------------------------------------
LEGAL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "content", "legal")


def page_legal(slug, title, desc):
    paragraphs = []
    path = os.path.join(LEGAL_DIR, slug + ".txt")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            raw = fh.read()
        for para in raw.split("\n\n"):
            p = " ".join(para.split())
            if not p:
                continue
            # the scraped text repeats its own heading
            if p.lower().rstrip(":") in (title.lower(), title.lower().replace("sale", "& conditions")):
                continue
            paragraphs.append("<p>%s</p>" % e(p))
    body = """
<main id="main">
<section class="section" style="padding-top:132px">
  <div class="container legal">
    <h1 class="legal__h">{title}</h1>
    {body}
    <p class="legal__back"><a href="contact.html">Questions about this policy? Contact us</a></p>
  </div>
</section>
</main>
""".format(title=e(title), body="\n".join(paragraphs) or "<p>This page is being updated.</p>")
    return head(title + " — G&W Biotechnologie GmbH", desc, slug) + header("Legal") + body + footer()


def page_privacy():
    return page_legal("privacy", "Privacy Policy",
                      "How G&W Biotechnologie GmbH collects, uses and protects personal information.")


def page_terms():
    return page_legal("terms", "Terms of Sale",
                      "Order confirmation, returns, delivery, payment and quality terms.")


def page_shipping():
    return page_legal("shipping", "Shipping and Returns",
                      "Dispatch times, shipping costs, cold chain, returns and refunds.")


# --------------------------------------------------------------------------
# page: orders (staff only, noindex)
# --------------------------------------------------------------------------
def page_orders():
    body = """
<main id="main">
<section class="section" style="padding-top:130px">
  <div class="container">
    <div id="orders-login">
      <h1 style="font-size:1.6rem;margin:0 0 8px">Order requests</h1>
      <p style="color:var(--muted);margin:0 0 22px">Enter the access code to view orders.</p>
      <form id="orders-auth" style="display:flex;gap:10px;max-width:420px;flex-wrap:wrap">
        <input id="orders-token" type="password" placeholder="Access code"
               autocomplete="current-password"
               style="flex:1;min-width:200px;padding:10px 14px;border:1px solid var(--line-strong);border-radius:9px;font:inherit">
        <button class="btn" type="submit">View</button>
      </form>
      <p id="orders-err" style="color:#b42318;font-size:.85rem;margin-top:10px" hidden>Wrong access code.</p>
    </div>

    <div id="orders-view" hidden>
      <div style="display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap;margin-bottom:20px">
        <h1 style="font-size:1.6rem;margin:0">Order requests</h1>
        <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap">
          <span id="orders-count" style="color:var(--muted);font-size:.85rem"></span>
          <button class="btn btn--ghost" id="orders-export" type="button" style="padding:8px 14px;font-size:.82rem">Export CSV</button>
          <button class="btn btn--ghost" id="orders-out" type="button" style="padding:8px 14px;font-size:.82rem">Sign out</button>
        </div>
      </div>
      <div id="orders-list"></div>
    </div>
  </div>
</section>
</main>
<script>
(function () {
  var KEY = "tl-orders-token";
  var token = localStorage.getItem(KEY) || "";
  var cache = [];

  function $(id) { return document.getElementById(id); }

  function show(which) {
    $("orders-login").hidden = which !== "login";
    $("orders-view").hidden = which !== "list";
  }

  function api(path, opts) {
    opts = opts || {};
    opts.headers = Object.assign({ "content-type": "application/json" },
      opts.headers, { authorization: "Bearer " + token });
    return fetch(path, opts).then(function (r) {
      if (r.status === 401) {
        localStorage.removeItem(KEY);
        token = "";
        show("login");
        throw new Error("unauthorized");
      }
      return r.json();
    });
  }

  function money(n) {
    return "$" + Number(n || 0).toLocaleString("en-US", { maximumFractionDigits: 2 });
  }

  function when(ms) {
    var d = new Date(ms);
    return d.toISOString().slice(0, 10) + " " + d.toTimeString().slice(0, 5);
  }

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  var STATUS = ["new", "confirmed", "paid", "shipped", "cancelled"];

  function render(orders) {
    cache = orders;
    $("orders-count").textContent = orders.length + " request" + (orders.length === 1 ? "" : "s");
    if (!orders.length) {
      $("orders-list").innerHTML = '<p style="color:var(--muted)">No orders yet.</p>';
      return;
    }
    $("orders-list").innerHTML = orders.map(function (o) {
      var f = o.fields || {};
      var items = (o.items || []).map(function (it) {
        return esc(it.spec) + (it.sku ? " (" + esc(it.sku) + ")" : "") + " × " + it.qty +
          (it.price == null ? " — price on request" : " = " + money(Number(it.price) * it.qty));
      }).join("<br>");
      return '<details class="o-row">' +
        '<summary><span class="o-id">' + esc(o.id) + "</span>" +
        '<span class="o-co">' + esc(f.organisation || f.work_email || "") + "</span>" +
        '<span class="o-total">' + money(o.total) + "</span>" +
        '<span class="o-status o-status--' + esc(o.status) + '">' + esc(o.status) + "</span>" +
        '<span class="o-when">' + when(o.t) + "</span></summary>" +
        '<div class="o-body">' +
        "<p><b>" + esc(f.full_name || "-") + "</b> · " + esc(f.work_email || "-") +
        (f.phone ? " · " + esc(f.phone) : "") + "</p>" +
        "<p>" + esc([f.address, f.city, f.postcode, f.country].filter(Boolean).join(", ")) + "</p>" +
        "<p><b>Payment:</b> " + (o.payment === "bank_transfer"
          ? "Bank transfer / purchase order" : "Card (link to follow)") +
        (f.po_number ? " · PO " + esc(f.po_number) : "") +
        (f.billing_name ? " · Invoice to " + esc(f.billing_name) : "") +
        (f.vat_number ? " · VAT " + esc(f.vat_number) : "") + "</p>" +
        (f.notes ? "<p><i>" + esc(f.notes) + "</i></p>" : "") +
        '<div class="o-items">' + items + "</div>" +
        '<div class="o-actions">' + STATUS.map(function (s) {
          return '<button type="button" data-id="' + esc(o.id) + '" data-status="' + s + '"' +
            (s === o.status ? ' class="is-on"' : "") + ">" + s + "</button>";
        }).join("") + "</div>" +
        "</div></details>";
    }).join("");
  }

  function load() {
    return api("/api/orders").then(function (d) {
      render(d.orders || []);
      show("list");
    });
  }

  $("orders-auth").addEventListener("submit", function (e) {
    e.preventDefault();
    token = $("orders-token").value.trim();
    localStorage.setItem(KEY, token);
    $("orders-err").hidden = true;
    load().catch(function () {
      $("orders-err").hidden = false;
    });
  });

  $("orders-out").addEventListener("click", function () {
    localStorage.removeItem(KEY);
    token = "";
    show("login");
  });

  $("orders-list").addEventListener("click", function (e) {
    var b = e.target.closest("button[data-status]");
    if (!b) return;
    b.disabled = true;
    api("/api/orders/status", {
      method: "POST",
      body: JSON.stringify({ id: b.getAttribute("data-id"), status: b.getAttribute("data-status") })
    }).then(load).catch(function () { b.disabled = false; });
  });

  $("orders-export").addEventListener("click", function () {
    var rows = [["id", "date", "status", "company", "contact", "email", "total", "items"]];
    cache.forEach(function (o) {
      var f = o.fields || {};
      rows.push([o.id, when(o.t), o.status, f.organisation || "", f.full_name || "",
        f.work_email || "", String(o.total),
        (o.items || []).map(function (it) {
          return it.spec + (it.sku ? " (" + it.sku + ")" : "") + " x" + it.qty;
        }).join(" | ")]);
    });
    var csv = rows.map(function (r) {
      return r.map(function (v) { return '"' + String(v).replace(/"/g, '""') + '"'; }).join(",");
    }).join("\\n");
    var url = URL.createObjectURL(new Blob(["\\ufeff" + csv], { type: "text/csv" }));
    var a = document.createElement("a");
    a.href = url;
    a.download = "tl-orders.csv";
    a.click();
    URL.revokeObjectURL(url);
  });

  if (token) {
    load().catch(function () { show("login"); });
  } else {
    show("login");
  }
})();
</script>
"""
    return (head("Orders — G&W Biotechnologie GmbH", "Order requests.", "orders", noindex=True)
            + header("Orders") + body + footer())


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
        <div class="buybox__qty">
          <label for="pdp-qty">Quantity</label>
          <div class="qty">
            <button type="button" id="qty-minus" aria-label="Decrease quantity">−</button>
            <input id="pdp-qty" type="number" value="1" min="1" max="99" inputmode="numeric" aria-label="Quantity">
            <button type="button" id="qty-plus" aria-label="Increase quantity">+</button>
          </div>
        </div>
        <div class="buybox__actions">
          <button class="btn" id="pdp-add" type="button" style="flex:1">Add to cart {ar}</button>
          <a class="btn btn--ghost" id="pdp-secondary" href="contact.html#quote">Request a quote</a>
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
    <div class="pdp__desc" id="pdp-desc"></div>
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
    return head("Product — G&W Biotechnologie GmbH",
                "Product details, specifications and documentation for G&W Biotechnologie GmbH CGT reagents.",
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
    return head("Applications — G&W Biotechnologie GmbH",
                "Workflow-matched reagents for T cell, NK, MSC, iPSC, hematopoietic and dendritic cell manufacturing.",
                "applications") + header("Applications") + body + footer()


# --------------------------------------------------------------------------
# page: quality
# --------------------------------------------------------------------------
def page_quality():
    cards = [
        ("shield", "ISO 13485:2016", "The medical-device quality management system applied to reagent manufacture — design control, risk management and traceability from raw material to release."),
        ("doc", "ISO 9001", "Company-wide quality management covering the R&amp;D, production and commercial processes around the ISO 13485 scope."),
        ("factory", "GMP cleanroom", "3,400 m² R&amp;D and production base with a GMP-level clean workshop for bead, protein and medium manufacture."),
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
        Status reflects the position published on gwbioth.com. Confirm current status with our
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
    return head("Quality & Regulatory — G&W Biotechnologie GmbH",
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
      <a class="link-arrow" style="margin-top:10px;font-size:.85rem" href="{href}">
        Discuss a project {ar}</a>
    </div>""".format(i=ic(s["icon"]), t=e(s["title"]), d=e(s["desc"]), idx=i + 1,
                     tags="".join("<span>%s</span>" % e(t) for t in s["tags"]), ar=ic("arrow"),
                     href=e(s.get("href") or "contact.html#quote"))
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
    return head("Services — custom development, lab automation and capacity at G&W",
                "Custom reagent development, a published lab automation roadmap, and a qualified capacity network for high-throughput work.",
                "services") + header("Services") + body + footer()


def page_transmembrane():
    WHY = [
        ("Hydrophobic by design",
         "Transmembrane segments aggregate once the lipid environment is gone. A clean band "
         "on a gel is not evidence of a folded protein."),
        ("Expression is toxic",
         "Over-expressing a membrane protein loads the host. Yield and host choice are "
         "coupled, not independent."),
        ("Purification removes the context",
         "Every step that strips detergent or lipid takes the protein further from the state "
         "you need to assay against."),
        ("Conformation is a separate test",
         "Activity has to be shown, not assumed. That is why the assay panel is agreed "
         "before the project starts."),
    ]

    FORMATS = [
        ("VLP",
         "Displayed on a particle membrane. No detergent. Measured as BCA total protein, so "
         "values are not comparable with target-protein quantities."),
        ("Detergent",
         "Solubilised into micelles. Detergent is retained and cannot be stripped. Measured "
         "as target protein."),
        ("Nanodisc",
         "Reconstituted into an SMA lipid disc. No detergent. Measured as target protein."),
    ]

    STEPS = [
        ("01", "Enquiry", "1 business day",
         "RFQ form or email, NDA signed. Missing sequence, UniProt ID, topology or intended "
         "application is returned for completion."),
        ("02", "Review", "3 business days (5 for complex targets)",
         "Sequence analysis, topology prediction, platform recommendation, risk grading."),
        ("03", "Quotation", "3 business days, valid 30 days",
         "Proposal and priced quotation, one revision included."),
        ("04", "Contract", "5 business days",
         "MSA + SOW or PO. International orders add proforma invoice, Incoterms and export "
         "review."),
        ("05", "Execution", "per schedule",
         "Prepayment releases the run. Fortnightly updates. Go/No-Go at the end of Stage 0. "
         "Protein, CoA and cold chain. Acceptance. 30 days of technical support."),
    ]

    FAQS = [
        ("Why can't VLP purity be measured by SDS-PAGE?",
         "Because the product is a particle bearing the target alongside other membrane "
         "proteins, not a purified species. Purity methods built for single proteins do not "
         "apply. Concentration is reported as BCA total protein, and an ELISA data set is "
         "provided so you can judge the sample against your own antibody."),
        ("What is the difference between BCA total protein and target protein?",
         "BCA total protein counts everything in the sample. Target protein counts only the "
         "protein you asked for. VLP is quoted on the first basis; Detergent and Nanodisc on "
         "the second. The two are not interchangeable and should never be compared line by "
         "line."),
        ("What happens if Stage 0 fails?",
         "You pay the feasibility fee and nothing else. You keep the expression construct, the "
         "small-scale data, the feasibility report and any trial sample produced. There is no "
         "obligation to continue and no further charge."),
        ("Can you start from a plasmid instead of a sequence?",
         "Yes. Send the plasmid map or the sequence with the intended tag and host. If neither "
         "a sequence nor a construct exists, construct design is part of Stage 0."),
        ("Which platform should I choose?",
         "It depends on the downstream assay, not on the target. Immune raising and antibody "
         "screening favour VLP for cost and speed. Surface plasmon resonance, bio-layer "
         "interferometry and structural work need a defined quantity of target protein, which "
         "points to Detergent or Nanodisc. If the assay is not yet fixed, run all three in "
         "parallel and decide on the comparison report."),
        ("Is this GMP material?",
         "No. These are research-grade custom services for discovery and characterisation. "
         "They are not manufactured under GMP and are not intended for therapeutic use. Our "
         "GMP raw material lines are separate and carry their own documentation."),
        ("How much does scale-up cost?",
         "Scale-up is priced per project against the delivered quantity and the platform, so "
         "it is quoted after the target has been reviewed. Stage 0 pricing is published above; "
         "Stage 1 pricing is issued with the quotation."),
    ]

    why_html = "".join(
        '<div class="tsc__item"><h3>%s</h3><p>%s</p></div>' % (e(t), e(d)) for t, d in WHY)

    fmt_html = "".join(
        '<div class="tsc__item"><h3>%s</h3><p>%s</p></div>' % (e(t), e(d)) for t, d in FORMATS)

    step_rows = "".join(
        '<tr><td><b>%s</b></td><td>%s</td><td>%s</td><td>%s</td></tr>'
        % (e(a), e(b), e(c), e(d)) for a, b, c, d in STEPS)

    faq_html = "".join(
        '<div class="faq__item"><button class="faq__q">%s%s</button>'
        '<div class="faq__a"><p>%s</p></div></div>' % (e(q), ic("plus"), e(a))
        for q, a in FAQS)

    body = """
<main id="main">
<section class="phero">
  <div class="phero__grid"></div>
  <div class="container phero__inner">
    <div class="crumbs"><a href="index.html">Home</a>{c}<a href="services.html">Services</a>{c}
      <span>Transmembrane proteins</span></div>
    <div class="eyebrow">Custom development</div>
    <h1>Full-length transmembrane proteins,<br>from sequence to sample.</h1>
    <p>Three production formats, one decision point. We confirm the target is producible before
      you commit to scale-up &mdash; and if it is not, the data and the construct are still
      yours.</p>
    <div class="phero__meta">
      <a class="btn btn--sm" href="contact.html#quote">Brief a target {ar}</a>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    {head_why}
    <div class="tsc__grid tsc__grid--four">{why}</div>
  </div>
</section>

<section class="section section--mist">
  <div class="container">
    {head_fmt}
    <div class="tsc__figure">
      <img src="assets/img/fig-01-three-platforms.svg" alt="Same protein, three membrane environments" width="680">
    </div>
    <div class="tsc__grid tsc__grid--three">{fmt}</div>
    <div class="tsc__warning">
      <b>VLP is a mixture, not purified target protein.</b> We do not guarantee or measure
      target-protein content or particle count; an ELISA data set is supplied instead.
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    {head_two}
    <div class="tsc__figure">
      <img src="assets/img/fig-02-two-stage.svg" alt="Two-stage project flow with a Go / No-Go decision point" width="680">
    </div>

    <div class="tsc__stage">
      <div class="tsc__stage-head">
        <span class="tsc__badge">Stage 0</span>
        <h3>Feasibility</h3>
        <p>The answer to "can this be made", before you pay for the quantity.</p>
      </div>
      <div class="table-wrap">
        <table class="data">
          <thead><tr><th>Format</th><th>From</th><th>Lead time</th></tr></thead>
          <tbody>
            <tr><td>VLP</td><td>from $850</td><td>4&ndash;6 weeks</td></tr>
            <tr><td>Detergent</td><td>from $1,500</td><td>6&ndash;8 weeks</td></tr>
            <tr><td>Nanodisc</td><td>from $2,000</td><td>8&ndash;10 weeks</td></tr>
            <tr><td>All three, in parallel</td><td>from $3,500</td><td>12&ndash;15 weeks</td></tr>
          </tbody>
        </table>
      </div>
      <ul class="tsc__list">
        <li>Delivered: expression construct, small-scale expression and purification data,
          feasibility report, 20&ndash;50 &micro;g trial sample.</li>
        <li>A Go / Switch / Stop decision within 10 business days.</li>
        <li>The Stage 0 fee is credited in full against Stage 1.</li>
        <li>If the project stops, only the feasibility fee is charged.</li>
      </ul>
    </div>

    <div class="tsc__stage">
      <div class="tsc__stage-head">
        <span class="tsc__badge tsc__badge--alt">Stage 1</span>
        <h3>Scale-up</h3>
        <p>Priced against the quantity actually delivered.</p>
      </div>
      <ul class="tsc__list">
        <li>Priced by delivered protein: 100 &micro;g / 500 &micro;g / 1 mg.</li>
        <li>Indicative pricing is issued with the quotation &mdash; request it with your target.</li>
        <li>Delivered: purified protein, certificate of analysis, project report, retention
          sample, raw QC data.</li>
        <li>Below the agreed quantity or purity: the stage is not charged, or is settled pro
          rata against what was delivered.</li>
      </ul>
    </div>

    <div class="tsc__callout">
      <b>All three formats in parallel.</b> One construct, three small-scale runs, a comparison
      and recommendation report &mdash; priced below the sum of the three single-platform
      projects.
    </div>
  </div>
</section>

<section class="section section--mist">
  <div class="container">
    {head_del}
    <div class="tsc__figure">
      <img src="assets/img/fig-03-deliverables.svg" alt="Deliverables at each stage" width="680">
    </div>
    <p class="tsc__note">Dry ice, UN1845. Retention samples held 6 months.</p>
  </div>
</section>

<section class="section">
  <div class="container">
    {head_proc}
    <div class="table-wrap">
      <table class="data">
        <thead><tr><th>Step</th><th>Stage</th><th>Lead time</th><th>What happens</th></tr></thead>
        <tbody>{steps}</tbody>
      </table>
    </div>
  </div>
</section>

<section class="section section--mist" id="faq">
  <div class="container">
    {head_faq}
    <div class="faq">{faqs}</div>
  </div>
</section>

<section class="section">
  <div class="container tsc__close">
    <h2>Tell us the target and the assay.</h2>
    <p>Send the sequence, the downstream application and the quantity you need. We will come
      back with a feasibility view and an honest answer about whether we are the right
      partner.</p>
    <a class="btn" href="contact.html#quote">Brief a target {ar}</a>
  </div>
</section>
</main>""".format(
        c=ic("chev"), ar=ic("arrow"),
        head_why=section_head("Process reality",
                              "The protein is not the hard part. Keeping it folded is.",
                              num="00"),
        why=why_html,
        head_fmt=section_head("Platform choice", "Same protein, three membrane environments.",
                              num="01"),
        fmt=fmt_html,
        head_two=section_head("Commercial structure", "A failure should cost a known amount.",
                              "We split feasibility from scale-up. You pay for the answer to "
                              "\"can this be made\" before you pay for the quantity.", num="02"),
        head_del=section_head("Deliverables", "What actually ships.", num="03"),
        head_proc=section_head("Process", "Five steps, one working week to a price.", num="04"),
        steps=step_rows,
        head_faq=section_head("Questions we get first",
                              "The things a project manager asks on the first call.", num="05"),
        faqs=faq_html,
    )

    return head(
        "Transmembrane Protein Production \u2014 VLP, Detergent and Nanodisc | T&amp;L Biotechnology",
        "Full-length transmembrane protein production with a paid feasibility stage before "
        "scale-up. VLP, Detergent and Nanodisc formats, from $850.",
        "transmembrane-protein",
    ) + header("Services") + body + footer()


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
    return head("Partners — distributors, OEM and academic referrals | G&W Biotechnologie GmbH",
                "Distributor, OEM and referral partnerships for G&W life science tools. Territory defined by agreement, technical training included.",
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
    faq_ld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a.replace("&amp;", "&")}}
            for q, a in FAQ
        ],
    }
    return head("Resources — documents, COA lookup and technical library | G&W Biotechnologie GmbH",
                "COA lookup, technical datasheets, quality documents and application notes for CGT reagents.",
                "resources", jsonld=faq_ld) + header("Resources") + body + footer()


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
    <p>G&W began in 2011 as a reagent developer for cell and gene therapy. The platform came
      later: once you own the assay data, the design models and the manufacturing, the same loop
      can produce tools for any workflow — not just the one you started with.</p>
    <div class="phero__meta">
      <span class="pill pill--brand">Est. 2011</span>
      <span class="pill">3,400 m² base</span>
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
          <div class="datapanel__n">3,400<small> m²</small></div>
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
    return head("Company — G&W Biotechnologie GmbH",
                "Founded 2011, 3,400 m² R&D and GMP base, ISO 13485 and ISO 9001 certified, FDA DMF filings on record.",
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
      A named specialist replies within one business day (Mon–Fri).</p>
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
            within one business day (Mon–Fri).</div>
        </form>
      </div>
      <div class="reveal">
        <div class="qcard" style="margin-bottom:14px">
          <div class="qcard__ico">{pin}</div><h3>United States</h3>
          <p>Pfarrer-Bergmann-Straße 59<br>55127 Mainz<br>United States</p>
          <p style="margin-top:10px"><a href="tel:{pr}" style="color:var(--brand);font-weight:600">{ph}</a><br>
            <a href="mailto:{em}" style="color:var(--brand);font-weight:600">{em}</a></p>
          <p style="margin-top:10px">Mon–Fri, 9:00–17:00 PT</p>
        </div>
        <div class="qcard" style="margin-bottom:14px">
          <div class="qcard__ico">{fac}</div><h3>Manufacturing &amp; R&amp;D</h3>
          <p>3,400 m² GMP cleanroom and R&amp;D laboratory. On-site and remote audits by
            appointment — allow two weeks for scheduling.</p>
          <a class="link-arrow" style="margin-top:12px;font-size:.85rem" href="#audit">Schedule an audit {ar}</a>
        </div>
        <div class="qcard">
          <div class="qcard__ico">{clock}</div><h3>Response times</h3>
          <p>Technical and quote enquiries: one business day (Mon–Fri).<br>
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
    contact_ld = {
        "@context": "https://schema.org",
        "@type": "ContactPage",
        "name": "Contact G&W Biotechnologie GmbH",
        "url": COMPANY["site_url"] + "/contact.html",
    }
    return head("Contact — G&W Biotechnologie GmbH",
                "Request a quote, technical support, DMF letter of authorisation or schedule an audit. Mainz, California.",
                "contact", jsonld=contact_ld) + header("Contact") + body + footer()


# --------------------------------------------------------------------------
# data.js
# --------------------------------------------------------------------------
def write_data_js():
    payload = {
        "products": [dict(slug=p["slug"], name=p["name"], cat=p["cat"], apps=p["apps"],
                          price=p["price"], blurb=p["blurb"], desc=p["desc"],
                          highlights=p["highlights"], specs=p["specs"], sizes=p["sizes"],
                          variants=p.get("variants") or [],
                          imageTile=p.get("image_tile") or "",
                          shopId=p.get("shop_product_id"))
                     for p in PRODUCTS],
        "cats": {c["id"]: c["name"] for c in CATEGORIES},
        "apps": {a["id"]: a["name"] for a in APPLICATIONS},
        "contact": {"email": COMPANY["email"], "phone": COMPANY["phone"],
                    "address": COMPANY["us_address"]},
        "api": "/api",
        # live storefront (OpenCart). Buy buttons for products that have a shop id.
        "shop": COMPANY.get("shop_url", ""),
        # public Turnstile site key; empty disables the widget (local builds)
        "turnstileSiteKey": COMPANY.get("turnstile_sitekey", ""),
    }
    js = "window.TL = " + json.dumps(payload, ensure_ascii=False, indent=1) + ";\n"
    with open(os.path.join(OUT, "assets", "js", "data.js"), "w", encoding="utf-8") as f:
        f.write(js)


# --------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# page: 404
# --------------------------------------------------------------------------
def page_404():
    links = [
        ("products.html", "Browse the catalogue", "%d products across five families" % NSKU),
        ("platform.html", "How the platform works", "Data, models, products and capacity in one loop"),
        ("resources.html#docs", "Document library", "Datasheets, COAs and safety data sheets"),
        ("contact.html", "Talk to a scientist", "A named application scientist replies in one business day (Mon–Fri)"),
    ]
    items = "".join("""
    <a class="nf__link" href="{h}">
      <span><b>{t}</b><i>{d}</i></span>{ar}
    </a>""".format(h=h, t=e(t), d=e(d), ar=ic("arrow")) for h, t, d in links)

    body = """
<main id="main" class="nf">
  <div class="container nf__inner">
    <div class="nf__code">404</div>
    <h1>That page is not in the catalogue.</h1>
    <p class="nf__lede">The link may be out of date, or the product may have been renamed. Everything
      we publish is reachable from one of these four places.</p>
    <div class="nf__links">{items}</div>
    <p class="nf__foot">Looking for a specific lot? Try the
      <a href="resources.html#coa">COA lookup</a>, or email
      <a href="mailto:{email}">{email}</a>.</p>
  </div>
</main>""".format(items=items, email=COMPANY["email"])

    return head("Page not found — G&W Biotechnologie GmbH",
                "The page you requested does not exist. Browse the catalogue, the platform overview or the document library.",
                "404", noindex=True) + header("") + body + footer()


def stamp_assets():
    """Append a content hash to CSS/JS links so a deploy busts the browser cache.

    Without this, a browser that saw main.js once keeps using it until its
    heuristic cache expires, which makes "I deployed but see no change" a
    recurring confusion.
    """
    import hashlib
    import re

    def digest(rel):
        path = os.path.join(OUT, rel)
        try:
            with open(path, "rb") as fh:
                return hashlib.md5(fh.read()).hexdigest()[:10]
        except OSError:
            return ""

    versions = {}
    for rel in ("assets/css/style.css", "assets/js/main.js",
                "assets/js/manage.js", "assets/js/data.js"):
        v = digest(rel)
        if v:
            versions[rel] = v
    if not versions:
        return

    pattern = re.compile(
        r"(" + "|".join(re.escape(k) for k in versions) + r")(\?v=[0-9a-f]+)?")
    count = 0
    for name in os.listdir(OUT):
        if not name.endswith(".html"):
            continue
        path = os.path.join(OUT, name)
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        new, n = pattern.subn(
            lambda m: m.group(1) + "?v=" + versions[m.group(1)], text)
        if n:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(new)
            count += n
    print("stamped %d asset links" % count)


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
        "cart.html": page_cart,
        "checkout.html": page_checkout,
        "orders.html": page_orders,
        "privacy.html": page_privacy,
        "terms.html": page_terms,
        "shipping.html": page_shipping,
        "register.html": page_register,
        "login.html": page_login,
        "account.html": page_account,
        "order.html": page_order_detail,
        "forgot.html": page_forgot,
        "reset.html": page_reset,
        "manage.html": page_manage,
        "applications.html": page_applications,
        "quality.html": page_quality,
        "services.html": page_services,
        "transmembrane-protein.html": page_transmembrane,
        "partners.html": page_partners,
        "resources.html": page_resources,
        "about.html": page_about,
        "contact.html": page_contact,
        "404.html": page_404,
    }
    for name, fn in pages.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(fn())
        print("built", name)

    stamp_assets()

    # favicon from the mark (logo-mark.png holds the symbol alone, already square).
    # Falling back to logo-color.png would need guessing where the wordmark starts.
    brand = os.path.join(OUT, "assets", "img", "brand")
    src = os.path.join(brand, "favicon-source.png")
    if not os.path.exists(src):
        src = os.path.join(brand, "logo-mark.png")
    if os.path.exists(src):
        try:
            from PIL import Image

            im = Image.open(src).convert("RGBA")
            im = im.crop(im.getbbox())                  # trim stray transparent edges
            side = max(im.size)
            canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
            canvas.paste(im, ((side - im.width) // 2, (side - im.height) // 2), im)
            canvas.resize((128, 128), Image.LANCZOS).save(os.path.join(brand, "favicon.png"))
            print("built favicon 128x128 from logo-mark")
        except Exception as ex:
            print("favicon skipped:", ex)


if __name__ == "__main__":
    main()
