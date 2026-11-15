#!/usr/bin/env bash
# Puts the VARTEC PHP site on a test server (Apache + PHP 8.2 in Docker, behind the server's nginx).
# It adds one container and one nginx site and touches nothing else. Safe to run again to update.
#
#   curl -fsSL https://raw.githubusercontent.com/Akash-Modi104/vartec.github.io/feature/php-site/php-site/deploy/vps-test/install.sh | sudo bash
#
set -euo pipefail

BRANCH="${BRANCH:-feature/php-site}"
REPO="https://github.com/Akash-Modi104/vartec.github.io"
ROOT=/opt/vartec-php
PORT="${PORT:-8095}"
IP="$(curl -fsS -4 https://ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')"
HOST="${HOST:-vartec-php.${IP//./-}.sslip.io}"
NAME=vartec-php-test

say() { printf '\n== %s\n' "$*"; }
command -v docker >/dev/null || { echo "Docker is not installed on this server. Stopping without changing anything."; exit 1; }
command -v nginx >/dev/null || { echo "nginx is not installed on this server. Stopping without changing anything."; exit 1; }
if ss -ltn 2>/dev/null | grep -q ":${PORT} " && ! docker ps --format '{{.Names}}' | grep -qx "$NAME"; then
  echo "Port ${PORT} is already used by something else. Re-run with PORT=<free port>."; exit 1
fi

say "Fetching the site code (${BRANCH})"
mkdir -p "$ROOT"
if [ -d "$ROOT/repo/.git" ]; then
  git -C "$ROOT/repo" fetch --depth 1 origin "$BRANCH" && git -C "$ROOT/repo" reset --hard FETCH_HEAD
else
  git clone --depth 1 --branch "$BRANCH" "$REPO" "$ROOT/repo"
fi
mkdir -p "$ROOT/vartec-data"
# Test stand-in for the live mail script: records the message instead of emailing anyone.
cp "$ROOT/repo/php-site/tests/stand-ins/send_mail.php" "$ROOT/repo/php-site/public/send_mail.php"
chown -R 33:33 "$ROOT/vartec-data" "$ROOT/repo/php-site/public/media"

say "Starting Apache + PHP 8.2 on 127.0.0.1:${PORT}"
docker rm -f "$NAME" >/dev/null 2>&1 || true
docker run -d --name "$NAME" --restart unless-stopped -p "127.0.0.1:${PORT}:80" \
  -e VARTEC_DATA_DIR=/var/www/vartec-data \
  -v "$ROOT/repo/php-site/public:/var/www/html" -v "$ROOT/vartec-data:/var/www/vartec-data" \
  php:8.2-apache bash -c "a2enmod rewrite headers >/dev/null && apache2-foreground" >/dev/null
for _ in $(seq 1 30); do curl -fsS -o /dev/null "http://127.0.0.1:${PORT}/" && break; sleep 1; done
curl -fsS -o /dev/null "http://127.0.0.1:${PORT}/" || { echo "The container did not start. See: docker logs $NAME"; exit 1; }

say "Adding the nginx site ${HOST}"
CONF=/etc/nginx/sites-available/${NAME}.conf
[ -d /etc/nginx/sites-available ] || CONF=/etc/nginx/conf.d/${NAME}.conf
if [ ! -f "$CONF" ]; then
  cat > "$CONF" <<NGINX
server {
    listen 80;
    server_name ${HOST};
    client_max_body_size 80m;
    location / {
        proxy_pass http://127.0.0.1:${PORT};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
NGINX
  [ -d /etc/nginx/sites-enabled ] && ln -sf "$CONF" "/etc/nginx/sites-enabled/${NAME}.conf"
  if ! nginx -t 2>/dev/null; then
    rm -f "$CONF" "/etc/nginx/sites-enabled/${NAME}.conf"
    echo "nginx rejected the new site, so it was removed again. Nothing else was changed."; exit 1
  fi
  systemctl reload nginx
  if command -v certbot >/dev/null; then
    certbot --nginx -d "$HOST" --non-interactive --redirect >/dev/null 2>&1 && SCHEME=https || echo "(No HTTPS certificate was issued; the site works over http.)"
  fi
fi
SCHEME="${SCHEME:-$(grep -q 'listen 443' "$CONF" && echo https || echo http)}"

curl -fsS -o /dev/null "http://127.0.0.1:${PORT}/admin/" || true   # creates the setup code on first run
say "Done"
echo "Website:  ${SCHEME}://${HOST}/"
echo "Admin:    ${SCHEME}://${HOST}/admin/"
if [ -f "$ROOT/vartec-data/setup-code.php" ]; then
  echo "Setup code for the first admin account: $(grep -o '"code": "[A-Z0-9]*"' "$ROOT/vartec-data/setup-code.php" | cut -d'"' -f4)"
else
  echo "An admin account already exists on this server."
fi
echo "To remove everything: docker rm -f ${NAME}; rm -f ${CONF} /etc/nginx/sites-enabled/${NAME}.conf; systemctl reload nginx; rm -rf ${ROOT}"
