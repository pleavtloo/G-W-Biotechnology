"""
Local preview server: serves dist/ and implements the /api/* routes so forms can be
tested end to end without deploying.

  python server/dev_server.py            # http://127.0.0.1:8080 + LAN addresses
  python server/dev_server.py 9000
  python server/dev_server.py 8080 --local   # loopback only, nothing on the LAN

By default the server listens on 0.0.0.0 so a phone on the same Wi-Fi can open it.
That also exposes the form API and /api/_reset to the local network — fine for a
short test, not for a shared office network.

Submissions are written to server/outbox/YYYY-MM-DD.jsonl (never committed).
Rate limiting, CRM push and the visitor receipt mirror server/worker.js so the same
acceptance cases run locally. This is a development tool: no TLS, no auth, and the
rate-limit window lives in memory (restart or POST /api/_reset clears it).

Env overrides (optional):
  TL_RL_MAX=5            submissions per window
  TL_RL_WINDOW=300       window length in seconds
  TL_RL_OFF=1            disable the limiter (load testing)
  CRM_WEBHOOK=<url>      POST the flat CRM record here; otherwise logged as skipped
  RECEIPT_SIGNER=...     signature on the visitor receipt
  IP_SALT=...            pepper for the rate-limit key hash
"""
import hashlib
import json
import os
import re
import socket
import sys
import threading
import time
import urllib.request
from datetime import date
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DIST = os.path.join(ROOT, "dist")
OUTBOX = os.path.join(HERE, "outbox")

MAX_BODY = 16 * 1024
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

RL_MAX = int(os.environ.get("TL_RL_MAX", "5"))
RL_WINDOW = int(os.environ.get("TL_RL_WINDOW", "300"))
RL_OFF = os.environ.get("TL_RL_OFF") == "1"
RL = {}
RL_LOCK = threading.Lock()

# keys echoed back to the visitor, mirroring worker.js
RECEIPT_KEYS = ("full_name", "name", "organisation", "organization", "company", "country",
                "i_am_interested_in", "interest", "application",
                "what_are_you_working_on", "message")


def log_event(kind, payload):
    os.makedirs(OUTBOX, exist_ok=True)
    path = os.path.join(OUTBOX, "%s.jsonl" % date.today().isoformat())
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps({"evt": kind, "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                            **payload}, ensure_ascii=False) + "\n")


def log_line(evt, **data):
    sys.stderr.write(json.dumps({"evt": evt, **data}, ensure_ascii=False) + "\n")


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


# ---------------------------------------------------------------- rate limit

def ip_hash(addr):
    salt = os.environ.get("IP_SALT", "tl-site")
    return hashlib.sha256(("%s|%s" % (addr, salt)).encode()).hexdigest()[:16]


def rate_limit(addr, endpoint):
    if RL_OFF or RL_MAX <= 0:
        return {"allowed": True, "off": True}
    key = (ip_hash(addr), endpoint)
    now = int(time.time())
    with RL_LOCK:
        hits = [t for t in RL.get(key, []) if now - t < RL_WINDOW]
        if len(hits) >= RL_MAX:
            RL[key] = hits
            return {"allowed": False,
                    "retryAfter": max(1, RL_WINDOW - (now - hits[-RL_MAX]))}
        hits.append(now)
        RL[key] = hits
    return {"allowed": True, "remaining": RL_MAX - len(hits)}


def reset_rate():
    with RL_LOCK:
        RL.clear()


# ---------------------------------------------------------------------- crm

def crm_push(payload):
    url = os.environ.get("CRM_WEBHOOK", "").strip()
    if not url:
        log_event("crm", {"skipped": True, "payload": payload})
        return "skip"
    try:
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode(),
            headers={"content-type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=2) as r:
            ok = 200 <= getattr(r, "status", 0) < 300
        log_event("crm", {"ok": ok, "payload": payload})
        return "ok" if ok else "err"
    except Exception as e:                                    # noqa: BLE001
        log_event("crm", {"ok": False, "error": str(e)[:160], "payload": payload})
        return "err"


# ------------------------------------------------------------------ receipt

def receipt_text(fields):
    signer = os.environ.get("RECEIPT_SIGNER", "").strip() or "Applications team, G&W Biotechnologie GmbH"
    lines = []
    for k, v in fields.items():
        if len(lines) >= 6 or "email" in k.lower() or k not in RECEIPT_KEYS:
            continue
        lines.append("  %s: %s" % (k.replace("_", " "), v[:200]))
    if not lines:
        for k, v in fields.items():
            if len(lines) >= 4 or "email" in k.lower():
                continue
            lines.append("  %s: %s" % (k.replace("_", " "), v[:160]))
    greeted = fields.get("full_name") or fields.get("name") or ""
    return "\n".join([
        ("Hello %s," % greeted.split(" ")[0]) if greeted else "Hello,",
        "",
        "Thank you for contacting G&W Biotechnologie GmbH. This is an automatic confirmation that your",
        "enquiry reached our applications team. A named specialist will reply within one business day (Mon–Fri).",
        "",
        "What we received:",
        *(lines or ["  (no details attached)"]),
        "",
        "This message confirms receipt only. Pricing and lead time are confirmed by the specialist",
        "handling your request, in their reply.",
        "",
        "If anything above is wrong, reply to this email and we will correct it.",
        "",
        signer,
        "G&W Biotechnologie GmbH · Mainz, California",
    ])


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=DIST, **kw)

    def log_message(self, fmt, *args):  # quieter
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def end_headers(self):
        # keep the browser from serving a stale page or script while you iterate
        path = (self.path or "").split("?")[0]
        if not path.startswith("/api") and (
                path in ("", "/") or path.endswith((".html", ".js", ".css"))):
            self.send_header("cache-control", "no-store")
        super().end_headers()

    # ---------------- api ----------------
    def _json(self, body, status=200, headers=None):
        raw = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("content-type", "application/json; charset=utf-8")
        self.send_header("cache-control", "no-store")
        for k, v in (headers or {}).items():
            self.send_header(k, v)
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

        if route == "/api/_reset":                       # dev only
            reset_rate()
            return self._json({"ok": True, "reset": True})

        if route == "/api/lead":
            started = time.time()
            if data.get("fields", {}).get("website_url"):
                return self._json({"ok": True})            # honeypot

            fields = clean_fields(data.get("fields"))
            if not fields:
                return self._json({"ok": False, "error": "empty submission"}, 400)

            addr = self.client_address[0]
            rl = rate_limit(addr, "lead")
            if not rl.get("allowed"):
                log_line("lead", form=data.get("form"), ok=False, reason="rate_limited",
                         mail="skip", crm="skip", rl="hit",
                         ms=int((time.time() - started) * 1000))
                return self._json(
                    {"ok": False, "error": "rate_limited", "retryAfter": rl["retryAfter"]},
                    429, {"retry-after": str(rl["retryAfter"])})

            email = next((v for k, v in fields.items()
                          if "email" in k.lower() and EMAIL_RE.match(v)), "")
            if not email:
                return self._json({"ok": False, "error": "a valid email address is required"}, 400)

            kind = re.sub(r"[^a-z0-9_-]", "", (data.get("form") or "lead"))[:24] or "lead"
            page = (data.get("path") or "")[:200]
            received = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

            log_event("lead", {"form": kind, "email": email, "page": page, "fields": fields})
            log_event("receipt", {"to": email,
                                  "subject": "We received your enquiry — G&W Biotechnologie GmbH",
                                  "text": receipt_text(fields)})
            crm = crm_push({"source": "website", "form": kind, "email": email, "page": page,
                            "fields": fields, "received": received})
            log_line("lead", form=kind, ok=True, mail="queued", crm=crm,
                     rl="off" if rl.get("off") else "ok",
                     ms=int((time.time() - started) * 1000),
                     fields=[{"k": k, "len": len(v)} for k, v in fields.items()])
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
            return self._json({
                "ok": True, "ts": int(time.time()),
                "cfg": {"turnstile": False,
                        "rateLimit": not RL_OFF,
                        "crm": bool(os.environ.get("CRM_WEBHOOK", "").strip()),
                        "mail": False},
            })
        # 404.html for unknown paths, like a static host would do
        path = self.translate_path(self.path)
        if not os.path.exists(path) and "." not in os.path.basename(path):
            self.path = "/404.html"
        return super().do_GET()


def lan_ips():
    """IPv4 addresses other devices on the LAN can use."""
    ips = []
    try:
        probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            probe.connect(("192.0.2.1", 9))       # no packet leaves; just picks a route
            ips.append(probe.getsockname()[0])
        finally:
            probe.close()
    except OSError:
        pass
    try:
        for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
            if not ip.startswith("127.") and ip not in ips:
                ips.append(ip)
    except OSError:
        pass
    return ips


def main():
    flags = [a for a in sys.argv[1:] if a.startswith("-")]
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    local_only = "--local" in flags or "-l" in flags
    port = int(args[0]) if args else 8080

    if not os.path.exists(os.path.join(DIST, "index.html")):
        print("dist/ missing - run: python tools/build_dist.py")
        return 1

    host = "127.0.0.1" if local_only else "0.0.0.0"
    print("serving dist/ on http://127.0.0.1:%d  (api: /api/lead, /api/coa)" % port)
    if local_only:
        print("loopback only (--local) - no other device can reach this")
    else:
        for ip in lan_ips():
            print("  LAN  http://%s:%d" % (ip, port))
        name = socket.gethostname()
        try:
            name.encode("ascii")
            print("  LAN  http://%s:%d   (hostname may not resolve on phones)" % (name, port))
        except UnicodeEncodeError:
            pass                                     # non-ASCII hostname: not worth printing
        print("  the forms API and /api/_reset are reachable from the LAN too;"
              " use --local to keep it on this machine")
    print("rate limit: %s (%d per %ds, key = salted ip hash)"
          % ("off" if RL_OFF else "on", RL_MAX, RL_WINDOW))
    try:
        ThreadingHTTPServer((host, port), Handler).serve_forever()
    except OSError as e:
        print("could not bind %s:%d - %s (is another copy already running?)" % (host, port, e))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
