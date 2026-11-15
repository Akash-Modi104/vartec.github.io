#!/usr/bin/env bash
# Checks the live site the way a visitor sees it. Read-only: GET requests, nothing is changed or sent.
#
#   tools/check_live.sh [site address]
#
# Run it after every upload. It expects the static-pages setup (deploy/go-live/htaccess-4-static.txt).
B="${1:-https://vartec.global}"
fails=0
chk() { # path, expected status (or "403|404"), text expected in the redirect target or page title
  local code loc title ok=OK try
  for try in 1 2 3; do
    code=$(curl -s -m 30 -o /tmp/vt-check.bin -D /tmp/vt-check.hdr -w "%{http_code}" "$B$1")
    [ "$code" != "000" ] && break
    sleep 2
  done
  loc=$(grep -i '^location:' /tmp/vt-check.hdr | tr -d '\r' | cut -d' ' -f2)
  title=$(grep -o '<title>[^<]*' /tmp/vt-check.bin | head -1 | cut -c8-70)
  [[ "$code" =~ ^($2)$ ]] || ok=FAIL
  if [ -n "${3:-}" ]; then echo "$loc|$title" | grep -qF -- "$3" || ok=FAIL; fi
  [ "$ok" = FAIL ] && fails=$((fails+1))
  printf '%-4s %s %-38s %s %s\n' "$ok" "$code" "$1" "$loc" "$title"
}
PAGES="services/epc services/consulting services/operation-maintenance projects/battery-storage projects/carports projects/ev-charging projects/floating-solar projects/security-systems projects/solar-parks"

echo "== pages"
chk / 200 "VARTEC"
for p in $PAGES; do chk "/$p/" 200 "VARTEC"; done
echo "== addresses of the previous site and addresses without the final slash"
for p in $PAGES; do chk "/$p" 301 "/$p/"; done
chk /project/batterystorage 301 "/projects/battery-storage/"
chk /project/carpots 301 "/projects/carports/"
chk /project/evcharging 301 "/projects/ev-charging/"
chk /project/floating 301 "/projects/floating-solar/"
chk /project/security 301 "/projects/security-systems/"
chk /project/solarparks 301 "/projects/solar-parks/"
chk /services/operationmaintenance 301 "/services/operation-maintenance/"
chk /home 301 "$B/"
chk /index.html 301 "$B/"
echo "== not found"
chk /this-page-does-not-exist 404 "not found"
chk /static-site/index.html 404
echo "== private (403; a .php address may show the hosting's own 404 while its PHP fault lasts)"
chk /index.php "403|404"
chk /app/bootstrap.php "403|404"
chk /data/ 403
chk /.htaccess 403
chk /.user.ini 403
echo "== files"
for f in /robots.txt /sitemap.xml /assets/site.css /assets/site.js /assets/contact.js /favicon.ico; do chk "$f" 200; done
echo "== mail script still there (GET only; never POST to it)"
body=$(curl -s -m 30 "$B/send_mail.php?x=1" | head -c 200)
case "$body" in
  "Invalid request"*) echo "OK   send_mail.php answers" ;;
  *"Page Not Found"*) echo "NOTE send_mail.php got the hosting's own 404 this time (the known PHP fault); run tools/php_health.sh" ;;
  *) echo "FAIL send_mail.php gave an unexpected answer"; fails=$((fails+1)) ;;
esac
echo
[ "$fails" -eq 0 ] && echo "All checks passed." || { echo "$fails check(s) failed."; exit 1; }
