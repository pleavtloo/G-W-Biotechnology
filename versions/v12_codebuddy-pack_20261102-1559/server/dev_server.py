"""
Local preview server: serves dist/ and implements the /api/* routes so forms can be
tested end to end without deploying.

  python server/dev_server.py            # http://127.0.0.1:8080
  python server/dev_server.py 9000

Submissions are written to server/outbox/YYYY-MM-DD.jsonl (never committed).
This is a development tool, not production: no rate limiting, no TLS, no auth.
"""
import json
import os
import re
import sys
import time
from datetime import date
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DIST = os.path.join(ROOT, "dist")
OUTBOX = os.path.join(HERE, "outbox")

MAX_BODY = 16 * 1024
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def log_event(kind, payload):
    os.makedirs(OUTBOX, exist_ok=True)
    path = os.path.join(OUTBOX, "%s.jsonl" % date.today().isoformat())
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps({"evt": kind, "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                            **payload}, ensure_ascii=False) + "\n")


def clean_fields(fields):
    out = {}
    for i, (k, v) in enumerate((fields or {}).items()):
        if i >= 12 or not isinstance(v, str):
            continue
        key = re.sub(r"[^a-z0-9_ -]", "", k, flags=re.I)[:40]
        val = re.sub(r"\s+", " ", v).strip()[:2000]
        if key and val:
            out[key] = val
    return out


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=DIST, **kw)

    def log_message(self, fmt, *args):  # quieter
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    # ---------------- api ----------------
    def _json(self, body, status=200):
        raw = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("content-type", "application/json; charset=utf-8")
        self.send_header("cache-control", "no-store")
        self.send_header("content-length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _read(self):
        try:
            n = int(self.headers.get("content-length") or 0)
        except ValueError:
            return None, "bad length"
        if n > MAX_BODY:
            return None, "payload too large"
        try:
            return json.loads(self.rfile.read(n) or b"{}"), None
        except Exception:
            return None, "invalid json"

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("access-control-allow-methods", "POST, GET, OPTIONS")
        self.send_header("access-control-allow-headers", "content-type")
        self.end_headers()

    def do_POST(self):
        route = self.path.split("?")[0].rstrip("/")
        data, err = self._read()
        if err:
            return self._json({"ok": False, "error": err}, 400)

        if route == "/api/lead":
            fields = clean_fields(data.get("fields"))
            if data.get("fields", {}).get("website_url"):
                return self._json({"ok": True})            # honeypot
            if not fields:
                return self._json({"ok": False, "error": "empty submission"}, 400)
            email = next((v for k, v in fields.items()
                          if "email" in k.lower() and EMAIL_RE.match(v)), "")
            if not email:
                return self._json({"ok": False, "error": "a valid email address is required"}, 400)
            log_event("lead", {"form": data.get("form"), "email": email,
                               "page": data.get("path"), "fields": fields})
            return self._json({"ok": True, "mail": "queued"})

        if route == "/api/coa":
            lot = (data.get("fields", {}).get("lot_number") or "").upper()
            lot = re.sub(r"[^A-Z0-9-]", "", lot)[:24]
            if not lot:
                return self._json({"ok": False, "error": "lot number required"}, 400)
            # demo index: any lot ending in a digit resolves to a sample COA
            found = bool(re.search(r"\d", lot))
            log_event("coa", {"lot": lot, "found": found})
            return self._json({"ok": True, "found": found,
                               **({"url": "/docs/coa-actsep-cd3-cd28.pdf",
                                   "sku": "TL-BD-101", "released": "2026-08-14"} if found else {})})

        if route == "/api/chat":
            return self._json({"ok": False, "error": "assistant not configured"}, 501)

        return self._json({"ok": False, "error": "not found"}, 404)

    def do_GET(self):
        if self.path.rstrip("/") == "/api/health":
            return self._json({"ok": True, "ts": int(time.time())})
        # 404.html for unknown paths, like a static host would do
        path = self.translate_path(self.path)
        if not os.path.exists(path) and "." not in os.path.basename(path):
            self.path = "/404.html"
        return super().do_GET()


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    if not os.path.exists(os.path.join(DIST, "index.html")):
        print("dist/ missing - run: python tools/build_dist.py")
        return 1
    print("serving dist/ on http://127.0.0.1:%d  (api: /api/lead, /api/coa)" % port)
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    sys.exit(main())
