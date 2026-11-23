#!/usr/bin/env python3
"""Content API: read/write the YAML that the site is built from.

The Node bridge cannot parse YAML (no npm on the box), so it forwards admin
requests here. This process never faces the internet: it listens on loopback
and every call must carry the shared key from /etc/tl-api.env.

Endpoints (all under /content):
    GET    /content/<kind>              list ids (+ a short label each)
    GET    /content/<kind>/<id>         one record as JSON
    PUT    /content/<kind>/<id>         replace a record
    POST   /content/<kind>              create (id comes from the payload slug)
    DELETE /content/<kind>/<id>         remove a record
    POST   /rebuild                     build the site and swap /var/www/tl
"""

import base64
import io
import json
import os
import re
import subprocess
import sys
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import yaml

try:
    from PIL import Image
except ImportError:          # uploads degrade gracefully if Pillow is absent
    Image = None

CONTENT = os.environ.get("CONTENT_DIR", "/opt/tl-src/content")
KEY = os.environ.get("CONTENT_KEY", "")
PORT = int(os.environ.get("PORT", "8084"))
REBUILD = os.environ.get("REBUILD_SCRIPT", "/opt/rebuild.sh")

# kind -> (subdirectory, is a single file holding a list)
KINDS = {
    "products": ("products", False),
    "faq": ("faq", False),
    "articles": ("articles", False),
    "applications": ("applications", False),
    "site": ("site.yaml", True),
    "categories": ("categories.yaml", True),
}

SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,80}$")
_build_lock = threading.Lock()

REPO = os.environ.get("GIT_REPO", "/opt/tl-src")
IMG_DIR = os.path.join(REPO, "website", "assets", "img", "products")
IMG_MAX_W = 1600
IMG_MAX_H = 1200
IMG_MAX_BYTES = 12 * 1024 * 1024


def save_upload(name, data_url):
    """Decode a data URL, resize it down and store it as WebP next to the others."""
    if Image is None:
        raise ValueError("image support is not installed on this server")

    payload = data_url.split(",", 1)[-1]
    raw = base64.b64decode(payload)
    if len(raw) > IMG_MAX_BYTES:
        raise ValueError("image is larger than 9 MB")

    img = Image.open(io.BytesIO(raw))
    img = img.convert("RGB")
    img.thumbnail((IMG_MAX_W, IMG_MAX_H), Image.LANCZOS)

    safe = re.sub(r"[^a-z0-9-]+", "-", (name or "upload").lower()).strip("-")[:60] or "upload"
    os.makedirs(IMG_DIR, exist_ok=True)
    path = os.path.join(IMG_DIR, safe + ".webp")
    img.save(path, "WEBP", quality=84, method=4)

    return {
        "path": "assets/img/products/" + safe + ".webp",
        "width": img.width,
        "height": img.height,
        "bytes": os.path.getsize(path),
    }


def kind_dir(kind):
    return os.path.join(CONTENT, KINDS[kind][0])


def record_path(kind, ident):
    sub, single = KINDS[kind]
    if single:
        return os.path.join(CONTENT, sub)
    if not SAFE_ID.match(ident or ""):
        raise ValueError("invalid id")
    return os.path.join(kind_dir(kind), ident + ".yaml")


def read_yaml(path):
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def write_yaml(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        yaml.safe_dump(data, fh, allow_unicode=True, sort_keys=False,
                       default_flow_style=False, width=100)
    os.replace(tmp, path)


def list_records(kind):
    sub, single = KINDS[kind]
    if single:
        return [{"id": kind, "label": kind}]
    out = []
    folder = kind_dir(kind)
    if not os.path.isdir(folder):
        return out
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".yaml"):
            continue
        ident = name[:-5]
        label = ident
        order = 0
        try:
            data = read_yaml(os.path.join(folder, name)) or {}
            label = data.get("name") or data.get("title") or data.get("q") or ident
            if isinstance(label, str):
                label = label[:80]
            if isinstance(data.get("order"), (int, float)):
                order = data["order"]
        except Exception:
            pass
        out.append({"id": ident, "label": label, "_order": order})

    # Records that carry an "order" field come first, in that order; everything
    # else keeps the alphabetical listing (stable sort).
    out.sort(key=lambda r: (r["_order"], r["id"]))
    for row in out:
        row.pop("_order", None)
    return out


INVOICE_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
INVOICE_FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def render_invoice(order):
    """Proforma invoice (or receipt once paid) as PDF bytes."""
    from fpdf import FPDF
    import datetime

    f = order.get("fields") or {}
    items = order.get("items") or []
    total = float(order.get("total") or 0)
    paid = str(order.get("status") or "") in ("paid", "shipped")

    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(True, margin=18)
    pdf.set_margins(18, 16, 18)
    pdf.add_page()
    pdf.add_font("DJ", "", INVOICE_FONT)
    pdf.add_font("DJ", "B", INVOICE_FONT_B)

    # letterhead
    pdf.set_font("DJ", "B", 15)
    pdf.cell(0, 8, "G&W Biotechnologie GmbH", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DJ", "", 8.5)
    pdf.set_text_color(110, 110, 110)
    pdf.cell(0, 4.8, "Pfarrer-Bergmann-Straße 59, 55127 Mainz, Deutschland",
             new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 4.8, "info@gwbioth.com   ·   +49 6131 000000",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(90, 110, 190)
    pdf.cell(0, 4.8, "To Life. From Discovery to Therapy",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(110, 110, 110)
    pdf.ln(7)

    pdf.set_text_color(20, 20, 20)
    pdf.set_font("DJ", "B", 13)
    pdf.cell(0, 8, "RECEIPT" if paid else "PROFORMA INVOICE",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DJ", "", 9.5)
    pdf.cell(0, 5.2, "Reference   " + str(order.get("id", "")), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5.2, "Date        " + datetime.date.today().isoformat(),
             new_x="LMARGIN", new_y="NEXT")
    if f.get("po_number"):
        pdf.cell(0, 5.2, "PO number   " + str(f["po_number"]), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # billed to
    pdf.set_font("DJ", "B", 9.5)
    pdf.cell(0, 5.5, "Billed to", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DJ", "", 9.5)
    for line in [
        f.get("billing_name") or f.get("organisation") or "",
        f.get("full_name") or "",
        f.get("work_email") or "",
        ", ".join([str(x) for x in [f.get("address"), f.get("city"),
                                    f.get("postcode"), f.get("country")] if x]),
        ("VAT / tax ID  " + str(f["vat_number"])) if f.get("vat_number") else "",
    ]:
        if line:
            pdf.cell(0, 4.9, str(line), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # items table
    widths = [34, 84, 14, 26, 28]
    heads = ["Catalogue no.", "Description", "Qty", "Unit price", "Amount"]
    pdf.set_font("DJ", "B", 8.6)
    pdf.set_fill_color(244, 246, 249)
    for w, h in zip(widths, heads):
        pdf.cell(w, 7, h, border="B", fill=True)
    pdf.ln()

    pdf.set_font("DJ", "", 8.6)
    subtotal = 0.0
    for it in items:
        qty = float(it.get("qty") or 0)
        unit = it.get("price")
        amount = (float(unit) * qty) if isinstance(unit, (int, float)) else None
        if amount is not None:
            subtotal += amount
        pdf.cell(widths[0], 6.4, str(it.get("sku") or "-"))
        pdf.cell(widths[1], 6.4, (str(it.get("name") or "")[:52]))
        pdf.cell(widths[2], 6.4, str(int(qty)))
        pdf.cell(widths[3], 6.4, "%.2f" % unit if isinstance(unit, (int, float)) else "on request")
        pdf.cell(widths[4], 6.4, "%.2f" % amount if amount is not None else "-", new_x="LMARGIN", new_y="NEXT")
        # spec on its own line so the description column stays readable
        if it.get("spec"):
            pdf.set_font("DJ", "", 7.6)
            pdf.set_text_color(120, 120, 120)
            pdf.cell(widths[0], 4.6, "")
            pdf.cell(widths[1], 4.6, "   " + str(it["spec"]))
            pdf.ln(4.6)
            pdf.set_text_color(20, 20, 20)
            pdf.set_font("DJ", "", 8.6)

    pdf.ln(3)
    pdf.set_font("DJ", "B", 9.5)
    pdf.cell(sum(widths[:4]), 7, "Subtotal", border="T")
    pdf.cell(widths[4], 7, "%.2f USD" % (subtotal or total), border="T",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DJ", "", 8)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 5, "Shipping and any applicable taxes are quoted separately.",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(20, 20, 20)
    pdf.ln(6)

    # payment block
    pdf.set_font("DJ", "B", 9.5)
    pdf.cell(0, 5.5, "Payment", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DJ", "", 9)
    if paid:
        pdf.cell(0, 4.9, "Paid by card. Thank you.", new_x="LMARGIN", new_y="NEXT")
    elif order.get("payment") == "bank_transfer":
        try:
            site = read_yaml(os.path.join(CONTENT, "site.yaml")) or {}
            bank = site.get("bank") or {}
        except Exception:
            bank = {}
        for label, key in [("Beneficiary", "beneficiary"), ("Account", "account"),
                           ("SWIFT / BIC", "swift"), ("Bank", "bank_name"),
                           ("Bank address", "bank_address"), ("Terms", "terms")]:
            if bank.get(key):
                pdf.cell(0, 4.9, "%-14s %s" % (label + ":", bank[key]),
                         new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        pdf.cell(0, 4.9, "Please quote reference %s with your transfer." % order.get("id", ""),
                 new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.cell(0, 4.9, "A secure card payment link will be emailed to you.",
                 new_x="LMARGIN", new_y="NEXT")

    pdf.ln(8)
    pdf.set_font("DJ", "", 7.6)
    pdf.set_text_color(130, 130, 130)
    pdf.multi_cell(0, 4.2, "For research and manufacturing use only. Terms of sale: "
                   "www.gwbioth.com/terms.html. Shipping and returns: "
                   "www.gwbioth.com/shipping.html.")

    out = pdf.output()
    return bytes(out)


def git_commit(message):
    """Keep a version history on the box even though GitHub is no longer the source."""
    repo = os.environ.get("GIT_REPO", "/opt/tl-src")
    try:
        subprocess.run(["git", "-C", repo, "add", "-A"], timeout=30,
                       capture_output=True, check=False)
        subprocess.run(
            ["git", "-C", repo, "-c", "user.name=tl-admin",
             "-c", "user.email=admin@localhost", "commit", "-q", "-m", message],
            timeout=30, capture_output=True, check=False)
    except Exception:
        pass


def git_history(rel_path, limit=25):
    """Recent commits that touched one file, newest first."""
    repo = os.environ.get("GIT_REPO", "/opt/tl-src")
    try:
        r = subprocess.run(
            ["git", "-C", repo, "log", "--format=%h\x1f%ad\x1f%s", "--date=short",
             "-n", str(limit), "--", rel_path],
            capture_output=True, text=True, timeout=30)
    except Exception:
        return []
    rows = []
    for line in (r.stdout or "").splitlines():
        bits = line.split("\x1f")
        if len(bits) == 3:
            rows.append({"sha": bits[0], "date": bits[1], "subject": bits[2]})
    return rows


def git_show(rel_path, sha):
    repo = os.environ.get("GIT_REPO", "/opt/tl-src")
    if not re.match(r"^[0-9a-f]{7,40}$", sha or ""):
        raise ValueError("bad revision")
    r = subprocess.run(["git", "-C", repo, "show", "%s:%s" % (sha, rel_path)],
                       capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        raise ValueError("revision not found")
    return r.stdout


def git_restore(rel_path, sha):
    repo = os.environ.get("GIT_REPO", "/opt/tl-src")
    if not re.match(r"^[0-9a-f]{7,40}$", sha or ""):
        raise ValueError("bad revision")
    r = subprocess.run(["git", "-C", repo, "checkout", sha, "--", rel_path],
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise ValueError((r.stderr or "could not restore")[:160])
    git_commit("content: restore %s from %s" % (rel_path, sha))


def run_rebuild():
    if not _build_lock.acquire(blocking=False):
        return {"ok": True, "skipped": "build already running"}
    try:
        proc = subprocess.run([REBUILD], capture_output=True, text=True, timeout=300)
        return {
            "ok": proc.returncode == 0,
            "code": proc.returncode,
            "tail": (proc.stdout or "")[-1500:] + (proc.stderr or "")[-800:],
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "build timed out"}
    finally:
        _build_lock.release()


class Handler(BaseHTTPRequestHandler):
    server_version = "tl-content/1.0"

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json; charset=utf-8")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _authorised(self):
        return bool(KEY) and self.headers.get("x-content-key") == KEY

    def _body(self):
        length = int(self.headers.get("content-length") or 0)
        if not length:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            return {}

    def do_GET(self):
        if not self._authorised():
            return self._send({"ok": False, "error": "unauthorized"}, 401)
        parts = [p for p in self.path.split("?")[0].split("/") if p]

        # GET /history?kind=products&id=<slug> — recent commits for one record.
        if parts[:1] == ["history"]:
            qs = urllib.parse.parse_qs(self.path.split("?", 1)[1] if "?" in self.path else "")
            kind = (qs.get("kind") or [""])[0]
            ident = (qs.get("id") or [""])[0]
            if not SAFE_ID.match(ident or ""):
                return self._send({"ok": False, "error": "bad id"}, 400)
            rel = os.path.relpath(record_path(kind, ident),
                                  os.environ.get("GIT_REPO", "/opt/tl-src"))
            return self._send({"ok": True, "history": git_history(rel)})

        if parts[:1] != ["content"] or len(parts) < 2:
            return self._send({"ok": False, "error": "not found"}, 404)
        kind = parts[1]
        if kind not in KINDS:
            return self._send({"ok": False, "error": "unknown kind"}, 400)
        try:
            if len(parts) == 2:
                return self._send({"ok": True, "items": list_records(kind)})
            data = read_yaml(record_path(kind, parts[2]))
            return self._send({"ok": True, "id": parts[2], "data": data})
        except FileNotFoundError:
            return self._send({"ok": False, "error": "not found"}, 404)
        except Exception as exc:
            return self._send({"ok": False, "error": str(exc)[:200]}, 400)

    def do_PUT(self):
        if not self._authorised():
            return self._send({"ok": False, "error": "unauthorized"}, 401)
        parts = [p for p in self.path.split("?")[0].split("/") if p]
        if parts[:1] != ["content"] or len(parts) != 3:
            return self._send({"ok": False, "error": "not found"}, 404)
        kind, ident = parts[1], parts[2]
        if kind not in KINDS:
            return self._send({"ok": False, "error": "unknown kind"}, 400)
        payload = self._body()
        data = payload.get("data")
        if not isinstance(data, dict):
            return self._send({"ok": False, "error": "data must be an object"}, 400)
        try:
            write_yaml(record_path(kind, ident), data)
            git_commit("content: update %s/%s" % (kind, ident))
        except Exception as exc:
            return self._send({"ok": False, "error": str(exc)[:200]}, 400)
        result = run_rebuild() if payload.get("rebuild", True) else {"ok": True}
        return self._send({"ok": True, "id": ident, "build": result})

    def do_POST(self):
        if not self._authorised():
            return self._send({"ok": False, "error": "unauthorized"}, 401)
        parts = [p for p in self.path.split("?")[0].split("/") if p]
        if parts == ["rebuild"]:
            return self._send({"ok": True, "build": run_rebuild()})
        if parts == ["reorder"]:
            # Renumber "order" across a whole list in one pass, then rebuild once.
            payload = self._body()
            kind = str(payload.get("kind") or "products")
            ids = payload.get("ids") or []
            if kind not in KINDS or KINDS[kind][1]:
                return self._send({"ok": False, "error": "bad kind"}, 400)
            if not isinstance(ids, list) or not ids:
                return self._send({"ok": False, "error": "ids required"}, 400)
            changed = 0
            for i, ident in enumerate(ids):
                ident = str(ident)
                if not SAFE_ID.match(ident):
                    continue
                path = record_path(kind, ident)
                try:
                    data = read_yaml(path)
                except Exception:
                    continue
                if not isinstance(data, dict):
                    continue
                want = (i + 1) * 10
                if data.get("order") != want:
                    data["order"] = want
                    write_yaml(path, data)
                    changed += 1
            if changed:
                git_commit("content: reorder %s (%d changed)" % (kind, changed))
                return self._send({"ok": True, "changed": changed, "build": run_rebuild()})
            return self._send({"ok": True, "changed": 0, "build": {"ok": True, "skipped": True}})

        if parts == ["revision"]:
            payload = self._body()
            kind = str(payload.get("kind") or "")
            ident = str(payload.get("id") or "")
            sha = str(payload.get("sha") or "")
            if not SAFE_ID.match(ident or ""):
                return self._send({"ok": False, "error": "bad id"}, 400)
            rel = os.path.relpath(record_path(kind, ident),
                                  os.environ.get("GIT_REPO", "/opt/tl-src"))
            try:
                text = git_show(rel, sha)
            except Exception as exc:
                return self._send({"ok": False, "error": str(exc)[:160]}, 400)
            return self._send({"ok": True, "content": text})
        if parts == ["restore"]:
            payload = self._body()
            kind = str(payload.get("kind") or "")
            ident = str(payload.get("id") or "")
            sha = str(payload.get("sha") or "")
            if not SAFE_ID.match(ident or ""):
                return self._send({"ok": False, "error": "bad id"}, 400)
            rel = os.path.relpath(record_path(kind, ident),
                                  os.environ.get("GIT_REPO", "/opt/tl-src"))
            try:
                git_restore(rel, sha)
            except Exception as exc:
                return self._send({"ok": False, "error": str(exc)[:160]}, 400)
            return self._send({"ok": True, "build": run_rebuild()})
        if parts == ["invoice"]:
            payload = self._body()
            order = payload.get("order")
            if not isinstance(order, dict):
                return self._send({"ok": False, "error": "order required"}, 400)
            try:
                blob = render_invoice(order)
            except Exception as exc:
                return self._send({"ok": False, "error": str(exc)[:180]}, 500)
            self.send_response(200)
            self.send_header("content-type", "application/pdf")
            self.send_header("content-length", str(len(blob)))
            self.send_header("content-disposition",
                             'inline; filename="%s.pdf"' % str(order.get("id", "invoice")))
            self.end_headers()
            self.wfile.write(blob)
            return
        if parts == ["upload"]:
            payload = self._body()
            try:
                info = save_upload(payload.get("name", ""), payload.get("data", ""))
            except Exception as exc:
                return self._send({"ok": False, "error": str(exc)[:180]}, 400)
            return self._send({"ok": True, "file": info, "build": run_rebuild()})
        if parts[:1] != ["content"] or len(parts) != 2:
            return self._send({"ok": False, "error": "not found"}, 404)
        kind = parts[1]
        if kind not in KINDS:
            return self._send({"ok": False, "error": "unknown kind"}, 400)
        payload = self._body()
        data = payload.get("data")
        if not isinstance(data, dict):
            return self._send({"ok": False, "error": "data must be an object"}, 400)
        ident = payload.get("id") or data.get("slug")
        try:
            path = record_path(kind, ident)
        except Exception as exc:
            return self._send({"ok": False, "error": str(exc)[:200]}, 400)
        if os.path.exists(path):
            return self._send({"ok": False, "error": "already exists"}, 409)
        try:
            write_yaml(path, data)
            git_commit("content: create %s/%s" % (kind, ident))
        except Exception as exc:
            return self._send({"ok": False, "error": str(exc)[:200]}, 400)
        result = run_rebuild() if payload.get("rebuild", True) else {"ok": True}
        return self._send({"ok": True, "id": ident, "build": result})

    def do_DELETE(self):
        if not self._authorised():
            return self._send({"ok": False, "error": "unauthorized"}, 401)
        parts = [p for p in self.path.split("?")[0].split("/") if p]
        if parts[:1] != ["content"] or len(parts) != 3:
            return self._send({"ok": False, "error": "not found"}, 404)
        kind, ident = parts[1], parts[2]
        if kind not in KINDS:
            return self._send({"ok": False, "error": "unknown kind"}, 400)
        try:
            os.remove(record_path(kind, ident))
            git_commit("content: delete %s/%s" % (kind, ident))
        except FileNotFoundError:
            return self._send({"ok": False, "error": "not found"}, 404)
        except Exception as exc:
            return self._send({"ok": False, "error": str(exc)[:200]}, 400)
        payload = self._body()
        result = run_rebuild() if payload.get("rebuild", True) else {"ok": True}
        return self._send({"ok": True, "id": ident, "build": result})


if __name__ == "__main__":
    if not KEY:
        sys.exit("CONTENT_KEY is not set")
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    sys.stderr.write("tl-content listening on 127.0.0.1:%d content=%s\n" % (PORT, CONTENT))
    srv.serve_forever()
