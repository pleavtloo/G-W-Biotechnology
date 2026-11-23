#!/usr/bin/env python3
"""Daily backup of everything that cannot be rebuilt.

The site itself is regenerated from these files, so this is the only copy that
matters: product/FAQ/article YAML, plus the order and account records. Builds a
dated tarball, keeps two weeks, and emails the newest one every Monday.
"""

import datetime
import glob
import json
import os
import smtplib
import sys
import tarfile
from email.message import EmailMessage

# Only what cannot be rebuilt: the YAML the site is generated from, plus the
# runtime records. Code comes from git, so it is deliberately left out.
SRC_DIRS = [
    ("/opt/tl-src/content", "content"),
]
API_FILES = [
    "orders.jsonl", "users.jsonl", "sessions.jsonl",
    "resets.jsonl", "hits.jsonl", "deploy-status.json",
]
DEST = os.environ.get("BACKUP_DIR", "/opt/backups")
STATUS_FILE = os.environ.get("BACKUP_STATUS", "/opt/tl-api/backup-status.json")
KEEP = int(os.environ.get("BACKUP_KEEP", "14"))
ENV_FILE = os.environ.get("MAIL_ENV", "/etc/tl-mail.env")
TO = os.environ.get("BACKUP_TO", "info@gwbioth.com")


def load_env(path):
    data = {}
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                data[k.strip()] = v.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return data


def make_archive():
    os.makedirs(DEST, exist_ok=True)
    stamp = datetime.date.today().isoformat()
    path = os.path.join(DEST, "tl-backup-%s.tar.gz" % stamp)

    with tarfile.open(path, "w:gz") as tar:
        for src, arc in SRC_DIRS:
            if os.path.isdir(src):
                tar.add(src, arcname=arc)
        for name in API_FILES:
            full = os.path.join("/opt/tl-api", name)
            if os.path.isfile(full):
                tar.add(full, arcname="api/" + name)
    return path


def prune():
    files = sorted(glob.glob(os.path.join(DEST, "tl-backup-*.tar.gz")))
    for old in files[:-KEEP]:
        try:
            os.remove(old)
        except OSError:
            pass
    return len(files[:-KEEP])


def send(path):
    env = load_env(ENV_FILE)
    host = env.get("SMTP_HOST", "smtp.exmail.qq.com")
    port = int(env.get("SMTP_PORT", "465"))
    user = env.get("SMTP_USER", "")
    password = env.get("SMTP_PASS", "")
    if not user or not password:
        return False, "SMTP credentials missing"

    size = os.path.getsize(path)
    msg = EmailMessage()
    msg["Subject"] = "[G&W] Weekly content backup — %s (%.0f KB)" % (
        datetime.date.today().isoformat(), size / 1024.0)
    msg["From"] = user
    msg["To"] = TO
    msg.set_content(
        "Weekly backup of the site content and order records.\n\n"
        "Contents:\n"
        "  content/   product, FAQ and article YAML (the source the site is built from)\n"
        "  api/       orders.jsonl (order requests), users.jsonl (accounts)\n\n"
        "To restore: extract over /opt/tl-src/content and /opt/tl-api, "
        "then run /opt/rebuild.sh.\n\n"
        "Size: %.1f KB\n" % (size / 1024.0)
    )
    with open(path, "rb") as fh:
        msg.add_attachment(fh.read(), maintype="application", subtype="gzip",
                           filename=os.path.basename(path))

    with smtplib.SMTP_SSL(host, port, timeout=30) as smtp:
        smtp.login(user, password)
        smtp.send_message(msg)
    return True, "sent"


def main():
    now = datetime.datetime.now().astimezone()
    path = make_archive()
    removed = prune()
    size = os.path.getsize(path)
    print("%s backup=%s size=%.1fKB pruned=%d" % (
        now.isoformat(timespec="seconds"),
        os.path.basename(path), size / 1024.0, removed))

    # The admin panel reads this file, so a silent failure is visible there.
    status = {
        "ok": True,
        "at": now.isoformat(timespec="seconds"),
        "file": os.path.basename(path),
        "size": size,
        "kept": KEEP,
        "pruned": removed,
        "mailed": False,
    }
    try:
        with open(STATUS_FILE, encoding="utf-8") as fh:
            previous = json.load(fh)
        status["mailed_at"] = previous.get("mailed_at", "")
    except Exception:
        status["mailed_at"] = ""

    if now.weekday() == 0:                      # Monday: ship it off the box
        try:
            ok, note = send(path)
        except Exception as exc:                # SMTP down must not lose the archive
            ok, note = False, str(exc)[:160]
        status["mailed"] = ok
        status["mail_note"] = note
        if ok:
            status["mailed_at"] = now.isoformat(timespec="seconds")
        print("  email:", note)

    try:
        with open(STATUS_FILE, "w", encoding="utf-8") as fh:
            json.dump(status, fh, ensure_ascii=False, indent=2)
    except Exception as exc:
        print("  status write failed:", exc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
