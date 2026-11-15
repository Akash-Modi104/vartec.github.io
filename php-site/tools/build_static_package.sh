#!/usr/bin/env bash
# Builds static-site.zip: the public pages as plain HTML files, ready to unzip in /htdocs.
# Used while PHP on the hosting is unreliable (see deploy/go-live/GO-LIVE.md).
#
#   tools/build_static_package.sh [output folder]
#       content = the starting content in public/app/seed
#   VARTEC_DATA_DIR=/path/to/data tools/build_static_package.sh [output folder]
#       content = a data folder you edited and published in the local admin
#
# Needs php, python3, curl and zip.
set -euo pipefail
cd "$(dirname "$0")/.."
OUT="${1:-/tmp/vartec-static}"
PORT="${PORT:-8905}"
HOST="${HOST:-vartec.global}"
DATA="${VARTEC_DATA_DIR:-$(mktemp -d)}"

rm -rf "$OUT/static-site" "$OUT/static-site.zip"
mkdir -p "$OUT"
VARTEC_DATA_DIR="$DATA" php -S "127.0.0.1:$PORT" -t public public/index.php >/dev/null 2>&1 &
SERVER=$!
trap 'kill "$SERVER" 2>/dev/null || true' EXIT
for _ in $(seq 1 50); do
  curl -fs -o /dev/null "http://127.0.0.1:$PORT/robots.txt" && break
  sleep 0.2
done

echo "Pages:"
python3 tools/export_static.py "http://127.0.0.1:$PORT" "$HOST" "$OUT"
(cd "$OUT" && zip -qr -X static-site.zip static-site)
echo
echo "Package: $OUT/static-site.zip"
sha256sum "$OUT/static-site.zip"
echo "If a page was added or removed above, also update the two page lists in /htdocs/.htaccess"
echo "(template: deploy/go-live/htaccess-4-static.txt)."
