"""
QA gate for the built site. Run after `tools/build_dist.py`.

  python tools/check.py             # check dist/
  python tools/check.py website     # check the dev copy

Exit code 0 = all hard checks pass. Warnings never fail the build.
Designed to be the single command an agent (or CI) runs before saying "done".
"""
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = sys.argv[1] if len(sys.argv) > 1 else "dist"
BASE = os.path.join(ROOT, TARGET)

HARD, WARN = [], []


def hard(msg):
    HARD.append(msg)


def warn(msg):
    WARN.append(msg)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def main():
    if not os.path.isdir(BASE):
        print("no such directory: %s" % BASE)
        return 2

    skip = {"design-ai-entry.html", "design-avatar.html", "__m.html"}
    pages = sorted(p for p in os.listdir(BASE)
                   if p.endswith(".html") and p not in skip)
    if not pages:
        print("no html files in %s" % BASE)
        return 2

    titles, descs = Counter(), Counter()

    for page in pages:
        html = read(os.path.join(BASE, page))
        where = "%s: " % page

        # ---- required head tags ----
        t = re.search(r"<title>(.*?)</title>", html, re.S)
        d = re.search(r'<meta name="description" content="(.*?)">', html, re.S)
        if not t or not t.group(1).strip():
            hard(where + "missing <title>")
        else:
            titles[t.group(1).strip()] += 1
        if not d or len(d.group(1).strip()) < 50:
            hard(where + "missing or too short meta description")
        else:
            descs[d.group(1).strip()] += 1

        if 'rel="canonical"' not in html:
            hard(where + "missing canonical")
        if 'property="og:image"' not in html:
            hard(where + "missing og:image")
        if 'lang="en"' not in html:
            hard(where + "html lang is not en")

        # ---- one h1 ----
        h1 = len(re.findall(r"<h1[\s>]", html))
        if h1 != 1:
            hard(where + "expected exactly 1 <h1>, found %d" % h1)

        # ---- local references resolve ----
        refs = re.findall(r'(?:src|href)="([^"#?:]+\.(?:css|js|webp|png|jpg|svg|woff2|pdf|ico))"', html)
        for r in refs:
            if r.startswith(("http://", "https://", "//", "mailto:", "tel:")):
                continue
            if not os.path.exists(os.path.join(BASE, r)):
                hard(where + "missing asset: " + r)

        for r in re.findall(r'href="([a-z0-9_-]+\.html)', html):
            if not os.path.exists(os.path.join(BASE, r)):
                hard(where + "broken page link: " + r)

        # ---- images have alt ----
        for img in re.findall(r"<img\b[^>]*>", html):
            if "alt=" not in img:
                warn(where + "img without alt: " + img[:70])

        # ---- structured data parses ----
        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
            try:
                json.loads(block.replace("<\\/", "</"))
            except Exception as e:
                hard(where + "invalid JSON-LD: %s" % str(e)[:60])

    # ---- duplicate metadata ----
    for title, n in titles.items():
        if n > 1:
            hard("duplicate <title> on %d pages: %s" % (n, title[:60]))
    for desc, n in descs.items():
        if n > 1:
            warn("duplicate meta description on %d pages" % n)

    # ---- build hygiene ----
    if TARGET == "dist":
        for bad in ("design-ai-entry.html", "design-avatar.html", "README.md", "__m.html"):
            if os.path.exists(os.path.join(BASE, bad)):
                hard("design/dev file leaked into dist: " + bad)
        for f in ("sitemap.xml", "robots.txt", "_headers", "404.html"):
            if not os.path.exists(os.path.join(BASE, f)):
                hard("missing build artifact: " + f)

        sm = os.path.join(BASE, "sitemap.xml")
        if os.path.exists(sm):
            locs = re.findall(r"<loc>(.*?)</loc>", read(sm))
            if len(locs) < len(pages):
                warn("sitemap has %d urls for %d pages" % (len(locs), len(pages)))
            host = re.match(r"https?://[^/]+", locs[0]).group(0) if locs else ""
            if "example.com" in host:
                hard("sitemap still points at example.com")

        rb = os.path.join(BASE, "robots.txt")
        if os.path.exists(rb) and "Sitemap:" not in read(rb):
            hard("robots.txt has no Sitemap directive")

    # ---- server config gate (independent of the page target) ----
    wrangler = os.path.join(ROOT, "server", "wrangler.toml")
    worker = os.path.join(ROOT, "server", "worker.js")
    if os.path.exists(wrangler):
        cfg = read(wrangler)
        if "TURNSTILE_SECRET" not in cfg:
            hard("server/wrangler.toml: TURNSTILE_SECRET undocumented (required in production)")
        if 'binding = "LEAD_KV"' not in cfg:
            hard("server/wrangler.toml: no LEAD_KV binding (rate limiting would stay off)")
        if 'ENVIRONMENT = "production"' not in cfg:
            warn('server/wrangler.toml: ENVIRONMENT = "production" missing (fail-closed check off)')
        if "SPF" not in cfg and "DKIM" not in cfg:
            warn("server/wrangler.toml: no SPF/DKIM reminder - check the sending domain before launch")

    # ---- turnstile wiring: site key and secret must travel together ----
    worker_src = read(worker) if os.path.exists(worker) else ""
    data_js = os.path.join(BASE, "assets", "js", "data.js")
    key = ""
    if os.path.exists(data_js):
        m = re.search(r'"turnstileSiteKey"\s*:\s*"([^"]*)"', read(data_js))
        key = m.group(1) if m else ""
    if not key:
        warn("data.js has no Turnstile site key - forms rely on rate limit + honeypot only")
    elif "TURNSTILE_SECRET" not in worker_src:
        hard("site key injected but server/worker.js has no Turnstile verification")

    # ---- product files: images must exist, and identity fields must be unique.
    # Duplicating an entry in the CMS copies slug/sku/order, which silently makes
    # one product shadow another - catch it here instead. ----
    try:
        import glob as _glob
        import yaml as _yaml

        seen = {"slug": {}, "sku_code": {}, "order": {}}
        for pfile in sorted(_glob.glob(os.path.join(ROOT, "content", "products", "*.yaml"))):
            with open(pfile, encoding="utf-8") as fh:
                item = _yaml.safe_load(fh) or {}
            fname = os.path.basename(pfile)
            slug = item.get("slug", fname)

            tile = (item.get("image_tile") or "").strip()
            if not tile:
                hard("product %s: image_tile is empty - its card would be blank" % slug)
            else:
                full = tile if os.path.isabs(tile) else os.path.join(ROOT, "website", tile)
                if not os.path.exists(full):
                    hard("product %s: image missing -> %s" % (slug, tile))

            for key in seen:
                value = item.get(key)
                if value in (None, ""):
                    continue
                if value in seen[key]:
                    hard("product %s: duplicate %s %r (also used by %s)"
                         % (fname, key, value, seen[key][value]))
                else:
                    seen[key][value] = fname
    except ImportError:
        pass

    # ---- report ----
    print("%s: %d pages" % (TARGET, len(pages)))
    if HARD:
        print("\nFAIL (%d)" % len(HARD))
        for m in HARD:
            print("  x " + m)
    if WARN:
        print("\nwarn (%d)" % len(WARN))
        for m in WARN[:20]:
            print("  ! " + m)
        if len(WARN) > 20:
            print("  ... %d more" % (len(WARN) - 20))
    if not HARD:
        print("\nPASS - %d hard checks clean" % (len(pages) * 4))
    return 1 if HARD else 0


if __name__ == "__main__":
    sys.exit(main())
