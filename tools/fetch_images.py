#!/usr/bin/env python
"""Fetch + normalize product/brand imagery for the G&W Biotechnologie GmbH site."""
import os, re, sys, io, json, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "website", "assets", "img")
os.makedirs(os.path.join(OUT, "products"), exist_ok=True)
os.makedirs(os.path.join(OUT, "brand"), exist_ok=True)

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"}

CACHE = "https://www.gwbioth.com/image/cache/catalog/"
ORIG = "https://www.gwbioth.com/image/catalog/"

# slug -> source path inside /image/catalog/ (original, high-res)
PRODUCTS = {
    "actsep-cd3-cd28": "tl-main-images-20260620/GMP-TL603.jpg",
    "maxsortin-cd3": "tl_prod/tlbio-20260611-gmp-grade-maxsortin-cd3-beads.png",
    "maxsortin-cd4": "MaxSortin® CD4 Beads.png",
    "maxsortin-cd14": "MaxSortin® CD14 Beads.png",
    "maxsortin-cd14-kit": "tl_prod/tlbio-20260611-tl-625kit-maxsortin-cd14-isolation-kit.jpg",
    "actcel-t-activation": "ActCel T Cell Activation Reagent.png",
    "cd3-mab": "CD3.png",
    "cd28-mab": "gmp-tl102-0500.png",
    "cd16-mab": "TL-201-0500 Anti-human CD16 mAb.jpg",
    "cd52-mab": "GMP-TL112-0100 Anti-human CD52 mAb.jpg",
    "cd137-mab": "CD137 mAb.jpg",
    "il2": "GMP-TL504-0100.jpg",
    "il3": "GMP-TL505-0050.jpg",
    "il7": "GMP-TL506-0050.jpg",
    "il12": "GMP-TL508-0050.jpg",
    "il15": "GMP-TL509-0050.jpg",
    "il18": "GMP-TL511-0050.jpg",
    "il21": "GMP-TL512-0050.jpg",
    "activin-a": "TL-910-0050 Recombinant Human Activin A Protein.jpg",
    "bfgf": "TL-901-0010.jpg",
    "egf": "tl-main-images-20260620/GMP-TL613.png",
    "fibronectin": "GMP-TL903-0050.jpg",
    "tnfa": "TL-303-0010 Recombinant Human TNFαProtein.png",
    "4-1bb-ligand": "GMP-TL695-0050 Recombinant Human 4-1BB Ligand Protein.jpg",
    "scf": "GMP-TL633-0100.jpg",
    "flt3l": "GMP-TL644-0050.jpg",
    "noggin": "GMP-TL651-0100.jpg",
    "tgf-b1": "GMP-TL902-0050.jpg",
    "laminin-511": "GMP-TL906-0100.jpg",
    "vitronectin": "TL-109-0010.jpg",
    "nk-kit-30": "AS-25 AMMS®NK Cell Culture Kit 3.0.png",
    "nk-kit-20": "AS-22 AMMS®NK Cell Culture Kit 2.0.jpg",
    "msc-kit-20": "tl-main-images-20260620/AS-33.png",
    "psc-medium": "tl-main-images-20260620/AS-35.jpg",
    "hek293-medium": "as-11-1.png",
    "organoid-matrix": "tl-main-images-20260620/AS-41.jpg",
    "cik-kit": "tl-main-images-20260620/AS-15.jpg",
    "cryo-solution": "tl-main-images-20260620/AS-36.png",
    "ok432": "432.png",
    "cd8-beads": "TL-514-0010.jpg",
    "tcr-ab-beads": "TL-607-0050.jpg",
    "cd20-mab": "GMP-TL201-0500 Anti-human CD20 mAb.jpg",
}

BRAND = {
    "logo-color.png": ORIG + "home/LOGO_1b.png",
    "logo-white.png": CACHE + "home/logo_white_h1-400x187fill.png",
    "texture-molecule.jpg": ORIG + "home/p_cover4.jpg",
    "texture-network.jpg": ORIG + "home/p_cover1.jpg",
    "banner-service.jpg": ORIG + "home/P_service_1.jpg",
    "lab-wide.jpg": ORIG + "home/we-proudly-serve1.jpg",
}


def get(url, timeout=45):
    req = urllib.request.Request(urllib.parse.quote(url, safe=":/?=&%"), headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def save_webp(data, path, size, pad=False):
    from PIL import Image
    im = Image.open(io.BytesIO(data))
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        bg.alpha_composite(im)
        im = bg.convert("RGB")
    else:
        im = im.convert("RGB")
    if pad:
        # square canvas, product centered, generous margin
        w, h = im.size
        side = int(max(w, h) * 1.06)
        canvas = Image.new("RGB", (side, side), (255, 255, 255))
        canvas.paste(im, ((side - w) // 2, (side - h) // 2))
        im = canvas
    im.thumbnail((size, size), Image.LANCZOS)
    im.save(path, "WEBP", quality=90, method=6)
    return im.size


ok, fail = 0, []
for slug, src in PRODUCTS.items():
    dst = os.path.join(OUT, "products", slug + ".webp")
    if os.path.exists(dst) and os.path.getsize(dst) > 3000:
        ok += 1
        continue
    try:
        data = get(ORIG + src)
        save_webp(data, dst, 640, pad=True)
        ok += 1
        print("ok  ", slug)
    except Exception as e:
        fail.append((slug, src, str(e)))
        print("FAIL", slug, e)

for name, url in BRAND.items():
    dst = os.path.join(OUT, "brand", name)
    if os.path.exists(dst) and os.path.getsize(dst) > 3000:
        continue
    try:
        data = get(url)
        if name.endswith(".png"):
            open(dst, "wb").write(data)
        else:
            save_webp(data, dst, 1800)
        print("ok  ", name)
    except Exception as e:
        print("FAIL", name, e)

print(f"\nproducts ok={ok} fail={len(fail)}")
for f in fail:
    print("  ", f)
