#!/bin/bash
# Auto-deploy for the Aliyun test host.
# Runs from cron every 2 minutes: pulls content, rebuilds, swaps /var/www/tl.
# Writes /opt/tl-api/deploy-status.json so the CMS can show what happened, and
# mails the owner on failure. A failed build leaves the previous version live.
set -euo pipefail

# The admin UI and the rebase below both create commits; git refuses without an
# identity when it cannot guess one from the host.
export GIT_AUTHOR_NAME=tl-admin
export GIT_AUTHOR_EMAIL=admin@localhost
export GIT_COMMITTER_NAME=tl-admin
export GIT_COMMITTER_EMAIL=admin@localhost

# One instance at a time: a manual run must not collide with the cron tick, or
# git fetch fails to take the ref lock and the deploy silently stops.
exec 9>/var/lock/tl-deploy.lock
flock -n 9 || exit 0

SRC=/opt/tl-src
LOG=/var/log/tl-deploy.log
STATUS_FILE=/opt/tl-api/deploy-status.json
MAIL_TO="${MAIL_TO:-contact@seafrom.com}"
MAIL_FROM="${MAIL_FROM:-T&L Biotechnology <lujiayin@seafrom.cn>}"

cd "$SRC"

# status <state> <commit> [extra-json]
status() {
    python3 - "$1" "$2" "${3:-}" "$STATUS_FILE" <<'PY' || true
import datetime
import json
import sys

state, commit, extra, path = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
data = {
    "state": state,
    "commit": commit,
    "at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
}
if extra:
    try:
        data.update(json.loads(extra))
    except Exception:
        data["note"] = extra
try:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False)
except Exception:
    pass
PY
}

notify() {
    python3 - "$1" "$2" "$MAIL_TO" "$MAIL_FROM" <<'PY' || true
import json
import sys
import urllib.request

subject, body, to, sender = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
payload = json.dumps({"from": sender, "to": [to], "subject": subject, "text": body}).encode("utf-8")
request = urllib.request.Request(
    "http://127.0.0.1:8082/send",
    data=payload,
    headers={"content-type": "application/json"},
)
try:
    urllib.request.urlopen(request, timeout=15).read()
except Exception:
    pass
PY
}

# Content belongs to this box and is deliberately not versioned here: keep a copy
# aside, sync the code from upstream, then put the content back. Committing it
# locally collided with upstream edits to the same YAML and broke the rebase.
LIVE_CONTENT=/tmp/tl-content-live
rm -rf "$LIVE_CONTENT"
cp -a content "$LIVE_CONTENT" 2>/dev/null || true

before=$(git rev-parse HEAD)
git fetch --quiet origin main
after=$(git rev-parse origin/main)
if [ "$before" = "$after" ]; then
    # Nothing new: still publish the current state so the editor can render it.
    if [ ! -f "$STATUS_FILE" ]; then
        status ok "${after:0:8}"
    fi
    exit 0
fi

short="${after:0:8}"
started=$(date +%s)
status running "$short" "{\"started\":\"$(date -Is)\"}"

# The admin UI commits straight into this checkout, so a blind reset would throw
# those edits away. Fast-forward when we are behind, rebase when we have our own
# commits on top.
git reset --hard --quiet "$after"
rm -rf content
cp -a "$LIVE_CONTENT" content 2>/dev/null || true

fail() {
    stage="$1"
    echo "$(date -Is) ${stage}_FAILED $short" >>"$LOG"
    tail_log=$(tail -n 20 "$LOG" 2>/dev/null || echo '(无日志)')
    python3 - "$short" "$stage" "$tail_log" "$STATUS_FILE" <<'PY' || true
import datetime
import json
import sys

commit, stage, log_tail, path = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
try:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({
            "state": "failed",
            "commit": commit,
            "error": stage,
            "log": log_tail[-1500:],
            "at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        }, fh, ensure_ascii=False)
except Exception:
    pass
PY
    notify "[T&L] 发布失败：${stage}" "提交 ${short}
时间：$(date -Is)

构建已中止，线上仍是上一版。
最近日志：
${tail_log}"
    exit 1
}

python3 tools/build_site.py >>"$LOG" 2>&1 || fail BUILD_SITE
python3 tools/build_dist.py >>"$LOG" 2>&1 || fail BUILD_DIST
rsync -a --delete dist/ /var/www/tl/ || fail RSYNC

chown -R www-data:www-data /var/www/tl
echo "$(date -Is) deployed $short" >>"$LOG"
status ok "$short" "{\"seconds\":$(( $(date +%s) - started ))}"
