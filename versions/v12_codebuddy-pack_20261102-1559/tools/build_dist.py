"""
Produce a deployable build in dist/.

  python tools/build_dist.py            # build + minify + sitemap + headers
  python tools/build_dist.py --no-min   # skip minification (debugging)

Output:
  dist/                  static site, ready for Cloudflare Pages / any CDN
  dist/sitemap.xml       generated from the page list
  dist/robots.txt
  dist/_headers          security + cache policy (Cloudflare Pages / Netlify)
  dist/_redirects        trailing-slash and legacy paths

Design pages (design-*.html) and README are excluded from the build.
"""
import os
import re
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "website")
DIST = os.path.join(ROOT, "dist")

sys.path.insert(0, HERE)
from content import COMPANY  # noqa: E402

EXCLUDE_FILES = {"design-ai-entry.html", "design-avatar.html", "README.md", "__m.html"}
EXCLUDE_DIRS = set()

# pages that go into the sitemap, with priority
SITEMAP = [
    ("/", 1.0, "weekly"),
    ("/products.html", 0.9, "weekly"),
    ("/platform.html", 0.9, "monthly"),
    ("/applications.html", 0.8, "monthly"),
    ("/services.html", 0.8, "monthly"),
    ("/quality.html", 0.8, "monthly"),
    ("/resources.html", 0.7, "weekly"),
    ("/about.html", 0.6, "monthly"),
    ("/partners.html", 0.6, "monthly"),
    ("/contact.html", 0.7, "monthly"),
]


# ---------------------------------------------------------------- minify
def minify_html(html):
    # keep <pre>, <textarea>, <script>, <style> contents untouched
    guards = []

    def stash(m):
        guards.append(m.group(0))
        return "\x00%d\x00" % (len(guards) - 1)

    html = re.sub(r"<(pre|textarea|script|style)\b[^>]*>.*?</\1>", stash, html, flags=re.S | re.I)
    html = re.sub(r"<!--(?!\[if).*?-->", "", html, flags=re.S)
    # collapse whitespace between tags
    html = re.sub(r">\s+<", "><", html)
    # collapse runs of spaces/newlines inside text nodes
    html = re.sub(r"[ \t]{2,}", " ", html)
    html = re.sub(r"\n\s*\n+", "\n", html)
    html = html.strip()

    def restore(m):
        return guards[int(m.group(1))]

    return re.sub(r"\x00(\d+)\x00", restore, html)


def minify_css(css):
    out = []
    i, n = 0, len(css)
    in_str = None
    while i < n:
        ch = css[i]
        if in_str:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(css[i + 1])
                i += 2
                continue
            if ch == in_str:
                in_str = None
            i += 1
            continue
        if ch in "\"'":
            in_str = ch
            out.append(ch)
            i += 1
            continue
        if css.startswith("/*", i):
            j = css.find("*/", i + 2)
            i = n if j < 0 else j + 2
            continue
        out.append(ch)
        i += 1
    css = "".join(out)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};:,>])\s*", r"\1", css)
    css = re.sub(r";}", "}", css)
    # url( "x" ) -> url(x) is safe only for unquoted-safe paths; leave quotes alone
    css = re.sub(r"\s*!\s*important", "!important", css)
    return css.strip()


# ---------------------------------------------------------------- generators
def sitemap_xml():
    today = time.strftime("%Y-%m-%d")
    rows = []
    for path, prio, freq in SITEMAP:
        rows.append(
            "  <url><loc>%s%s</loc><lastmod>%s</lastmod>"
            "<changefreq>%s</changefreq><priority>%.1f</priority></url>"
            % (COMPANY["site_url"], path, today, freq, prio)
        )
    # product detail URLs share one template; list them explicitly so search engines
    # can discover every SKU without crawling the catalogue filter
    from content import PRODUCTS
    for p in PRODUCTS:
        rows.append(
            "  <url><loc>%s/product.html?p=%s</loc><lastmod>%s</lastmod>"
            "<changefreq>monthly</changefreq><priority>0.7</priority></url>"
            % (COMPANY["site_url"], p["slug"], today)
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(rows)
        + "\n</urlset>\n"
    )


ROBOTS = """User-agent: *
Allow: /
Disallow: /design-ai-entry.html
Disallow: /design-avatar.html

# AI crawlers: allowed on public pages, blocked from nothing else
User-agent: GPTBot
Allow: /

Sitemap: {site}/sitemap.xml
"""

HEADERS = """# Cloudflare Pages / Netlify header rules
/*
  X-Content-Type-Options: nosniff
  X-Frame-Options: SAMEORIGIN
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: geolocation=(), microphone=(), camera=()
  Strict-Transport-Security: max-age=31536000; includeSubDomains

/*.html
  Cache-Control: public, max-age=0, must-revalidate

/assets/*
  Cache-Control: public, max-age=31536000, immutable

/docs/*
  Content-Disposition: inline
  Cache-Control: public, max-age=86400
"""

REDIRECTS = """# trailing slash for the root only; everything else is a real file
/index.html    /    301
"""


# ---------------------------------------------------------------- main
def main():
    no_min = "--no-min" in sys.argv

    if not os.path.exists(os.path.join(SRC, "index.html")):
        print("website/ is empty - run tools/build_site.py first")
        return 1

    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST)

    stats = {"html": [0, 0], "css": [0, 0], "js": [0, 0], "other": 0}

    for base, dirs, files in os.walk(SRC):
        rel = os.path.relpath(base, SRC)
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        target_dir = DIST if rel == "." else os.path.join(DIST, rel)
        os.makedirs(target_dir, exist_ok=True)
        for name in files:
            if rel == "." and name in EXCLUDE_FILES:
                continue
            src = os.path.join(base, name)
            dst = os.path.join(target_dir, name)
            ext = os.path.splitext(name)[1].lower()
            if ext in (".html", ".css") and not no_min:
                raw = open(src, encoding="utf-8").read()
                out = minify_html(raw) if ext == ".html" else minify_css(raw)
                open(dst, "w", encoding="utf-8", newline="").write(out)
                key = ext[1:]
                stats[key][0] += len(raw.encode())
                stats[key][1] += len(out.encode())
            else:
                shutil.copy2(src, dst)
                if ext == ".js":
                    stats["js"][0] += os.path.getsize(src)
                    stats["js"][1] += os.path.getsize(src)
                else:
                    stats["other"] += os.path.getsize(src)

    open(os.path.join(DIST, "sitemap.xml"), "w", encoding="utf-8").write(sitemap_xml())
    open(os.path.join(DIST, "robots.txt"), "w", encoding="utf-8").write(
        ROBOTS.format(site=COMPANY["site_url"]))
    open(os.path.join(DIST, "_headers"), "w", encoding="utf-8").write(HEADERS)
    open(os.path.join(DIST, "_redirects"), "w", encoding="utf-8").write(REDIRECTS)

    total = sum(os.path.getsize(os.path.join(b, f))
                for b, _, fs in os.walk(DIST) for f in fs)
    print("\nbuild -> dist/")
    for k in ("html", "css", "js"):
        a, b = stats[k]
        if a:
            print("  %-5s %7.1f KB -> %6.1f KB  (-%.0f%%)"
                  % (k, a / 1024, b / 1024, (1 - b / a) * 100))
    print("  other %7.1f KB (images, fonts, pdf)" % (stats["other"] / 1024))
    print("  total %7.1f MB" % (total / 1024 / 1024))
    print("  sitemap: %d urls" % (len(SITEMAP) + 42))
    return 0


if __name__ == "__main__":
    sys.exit(main())
