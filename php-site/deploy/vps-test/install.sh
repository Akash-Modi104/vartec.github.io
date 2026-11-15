#!/usr/bin/env bash
# Puts the VARTEC PHP site on a test server behind its existing nginx.
# With Docker: Apache + PHP 8.2 in one container. Without: PHP-FPM (installed if missing).
# It adds one nginx site and touches no other site. Safe to run again to update.
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
command -v nginx >/dev/null || { echo "nginx is not installed on this server. Stopping without changing anything."; exit 1; }
MODE=fpm; command -v docker >/dev/null && MODE=docker

say "Fetching the site code (${BRANCH})"
mkdir -p "$ROOT"
if [ -d "$ROOT/repo/.git" ]; then
  git -C "$ROOT/repo" fetch --depth 1 origin "$BRANCH" && git -C "$ROOT/repo" reset --hard FETCH_HEAD
else
  git clone --depth 1 --branch "$BRANCH" "$REPO" "$ROOT/repo"
fi
SITE="$ROOT/repo/php-site"
mkdir -p "$SITE/vartec-data"
# Test stand-in for the live mail script: records the message instead of emailing anyone.
cp "$SITE/tests/stand-ins/send_mail.php" "$SITE/public/send_mail.php"
chown -R 33:33 "$SITE/vartec-data" "$SITE/public/media"

CONF=/etc/nginx/sites-available/${NAME}.conf
[ -d /etc/nginx/sites-available ] || CONF=/etc/nginx/conf.d/${NAME}.conf

if [ "$MODE" = docker ]; then
  say "Starting Apache + PHP 8.2 in Docker on 127.0.0.1:${PORT}"
  docker rm -f "$NAME" >/dev/null 2>&1 || true
  docker run -d --name "$NAME" --restart unless-stopped -p "127.0.0.1:${PORT}:80" \
    -v "$SITE/public:/var/www/html" -v "$SITE/vartec-data:/var/www/vartec-data" \
    php:8.2-apache bash -c "a2enmod rewrite headers >/dev/null && apache2-foreground" >/dev/null
  for _ in $(seq 1 30); do curl -fsS -o /dev/null "http://127.0.0.1:${PORT}/" && break; sleep 1; done
  curl -fsS -o /dev/null "http://127.0.0.1:${PORT}/" || { echo "The container did not start. See: docker logs $NAME"; exit 1; }
  BODY="    location / {
        proxy_pass http://127.0.0.1:${PORT};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }"
else
  # No Docker: run the site with PHP-FPM behind nginx. The rules below mirror public/.htaccess.
  if ! ls /run/php/php*-fpm.sock >/dev/null 2>&1; then
    say "Installing PHP (php-fpm, gd, mbstring)"
    DEBIAN_FRONTEND=noninteractive apt-get install -y -q php-fpm php-gd php-mbstring >/dev/null
  fi
  SOCK="$(ls /run/php/php*-fpm.sock | grep -v 'php-fpm.sock' | sort -V | tail -1)"
  [ -n "$SOCK" ] || SOCK=/run/php/php-fpm.sock
  say "Using PHP-FPM at ${SOCK}"
  BODY="    root ${SITE}/public;
    location ~ ^/(app|data)(/|\$) { return 404; }
    location ~ /\\.(?!well-known/) { return 404; }
    location ~* ^/media/.*\\.(php|phtml|phar)\$ { return 403; }
    location = /send_mail.php { include fastcgi_params; fastcgi_param SCRIPT_FILENAME \$document_root/send_mail.php; fastcgi_pass unix:${SOCK}; }
    location ~ /\$ { rewrite ^ /index.php last; }
    location / { try_files \$uri /index.php\$is_args\$args; }
    location = /index.php { include fastcgi_params; fastcgi_param SCRIPT_FILENAME \$document_root/index.php; fastcgi_pass unix:${SOCK}; }
    location ~ \\.php\$ { return 404; }"
fi

say "Adding the nginx site ${HOST}"
if [ ! -f "$CONF" ] || ! grep -q 'listen 443' "$CONF"; then
  cat > "$CONF" <<NGINX
server {
    listen 80;
    server_name ${HOST};
    client_max_body_size 80m;
${BODY}
}
NGINX
  [ -d /etc/nginx/sites-enabled ] && ln -sf "$CONF" "/etc/nginx/sites-enabled/${NAME}.conf"
  if ! nginx -t 2>/tmp/${NAME}-nginx.err; then
    cat /tmp/${NAME}-nginx.err
    rm -f "$CONF" "/etc/nginx/sites-enabled/${NAME}.conf"
    echo "nginx rejected the new site, so it was removed again. Nothing else was changed."; exit 1
  fi
  systemctl reload nginx
  if command -v certbot >/dev/null; then
    certbot --nginx -d "$HOST" --non-interactive --redirect >/dev/null 2>&1 || echo "(No HTTPS certificate was issued; the site works over http.)"
  fi
fi
SCHEME="$(grep -q 'listen 443' "$CONF" && echo https || echo http)"

curl -ksS -o /dev/null "${SCHEME}://${HOST}/admin/" || true   # creates the setup code on first run
say "Done (${MODE})"
echo "Website:  ${SCHEME}://${HOST}/"
echo "Admin:    ${SCHEME}://${HOST}/admin/"
echo "Checks:   home $(curl -ksS -o /dev/null -w '%{http_code}' "${SCHEME}://${HOST}/")  page $(curl -ksS -o /dev/null -w '%{http_code}' "${SCHEME}://${HOST}/services/epc/")  private $(curl -ksS -o /dev/null -w '%{http_code}' "${SCHEME}://${HOST}/app/bootstrap.php")  admin $(curl -ksS -o /dev/null -w '%{http_code}' "${SCHEME}://${HOST}/admin/")"
if [ -f "$SITE/vartec-data/setup-code.php" ]; then
  echo "Setup code for the first admin account: $(grep -o '"code": "[A-Z0-9]*"' "$SITE/vartec-data/setup-code.php" | cut -d'"' -f4)"
else
  echo "An admin account already exists on this server."
fi
echo "To remove everything: rm -f ${CONF} /etc/nginx/sites-enabled/${NAME}.conf; systemctl reload nginx; rm -rf ${ROOT}"
[ "$MODE" = docker ] && echo "                      docker rm -f ${NAME}" || true
