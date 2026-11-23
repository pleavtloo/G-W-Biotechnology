#!/bin/bash
# Rebuild the site from the YAML on disk and swap it into place.
# No git operations: the admin UI writes files directly, the cron job handles
# pulling in code changes from the repository.
set -euo pipefail

SRC=/opt/tl-src
OUT=/var/www/tl

cd "$SRC"

python3 tools/build_site.py >/tmp/tl-build.log 2>&1 || {
  echo "BUILD_SITE_FAILED"
  tail -25 /tmp/tl-build.log
  exit 1
}

python3 tools/build_dist.py >>/tmp/tl-build.log 2>&1 || {
  echo "BUILD_DIST_FAILED"
  tail -25 /tmp/tl-build.log
  exit 1
}

rsync -a --delete "$SRC/dist/" "$OUT/"
chown -R www-data:www-data "$OUT"

echo "rebuilt $(date -Is)"
