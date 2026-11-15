#!/usr/bin/env bash
# Is PHP on the hosting reliable yet? Run this before switching from the static pages to the PHP version.
#
#   tools/php_health.sh [site address] [number of requests]
#
# It only sends harmless GET requests to send_mail.php, which answers "Invalid request".
# NEVER test send_mail.php with a POST: every POST sends a real email to the company inbox.
B="${1:-https://vartec.global}"
N="${2:-50}"
ok=0; stock=0; other=0
for i in $(seq 1 "$N"); do
  body=$(curl -s -m 20 "$B/send_mail.php?x=$i" | head -c 300)
  case "$body" in
    "Invalid request"*) ok=$((ok+1)) ;;
    *"Page Not Found"*) stock=$((stock+1)) ;;
    *) other=$((other+1)) ;;
  esac
  sleep 0.3
done
echo "$ok of $N answered by PHP, $stock got the hosting's own 'Page Not Found', $other gave no answer"
if [ "$ok" -eq "$N" ]; then
  echo "PHP looks healthy. Run it again an hour later before switching."
else
  echo "PHP is still unreliable: stay on the static pages."
  exit 1
fi
