"""Minimal SMTP sidecar.

Accepts the same JSON body the worker sends to the Resend API and forwards it
through an authenticated SMTP account (Tencent Exmail here). Standard library
only — no pip packages on the server.

    POST /send
    {"from": "...", "to": ["a@b.c"], "subject": "...", "text": "...", "reply_to": "..."}
"""
import json
import os
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.exmail.qq.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
BIND = os.environ.get("BIND", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8082"))


def log(**kw):
    print(json.dumps(kw), flush=True)


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        length = int(self.headers.get("content-length") or 0)
        try:
            data = json.loads(self.rfile.read(length) or b"{}")
        except Exception:
            return self._json({"ok": False, "error": "bad json"}, 400)

        to = data.get("to") or []
        if isinstance(to, str):
            to = [part.strip() for part in to.split(",") if part.strip()]
        if not to:
            return self._json({"ok": False, "error": "no recipients"}, 400)
        if not SMTP_USER or not SMTP_PASS:
            return self._json({"ok": False, "error": "smtp credentials missing"}, 500)

        msg = EmailMessage()
        # Tencent requires the From address to match the authenticated account.
        msg["From"] = data.get("from") or SMTP_USER
        msg["To"] = ", ".join(to)
        msg["Subject"] = data.get("subject") or "(no subject)"
        msg["Date"] = formatdate(localtime=True)
        msg["Message-ID"] = make_msgid(domain=SMTP_USER.split("@")[-1])
        reply_to = data.get("reply_to") or data.get("replyTo")
        if reply_to:
            msg["Reply-To"] = reply_to
        msg.set_content(data.get("text") or "")

        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context, timeout=25) as smtp:
                smtp.login(SMTP_USER, SMTP_PASS)
                smtp.send_message(msg)
            log(evt="smtp_sent", n=len(to), subject=msg["Subject"][:60])
            return self._json({"ok": True, "id": "smtp"})
        except Exception as exc:  # noqa: BLE001
            log(evt="smtp_error", err=str(exc)[:200])
            return self._json({"ok": False, "error": str(exc)[:200]}, 502)

    def do_GET(self):
        self._json({"ok": True, "service": "smtp-sidecar",
                    "configured": bool(SMTP_USER and SMTP_PASS)})

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    log(evt="smtp_sidecar_start", host=SMTP_HOST, port=SMTP_PORT,
        user=SMTP_USER, configured=bool(SMTP_USER and SMTP_PASS))
    ThreadingHTTPServer((BIND, PORT), Handler).serve_forever()
