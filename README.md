# VARTEC website (vartec.global)

Code for the VARTEC website, hosted on Network Solutions (Starter, Hosting-Unix).
This page is the map of the repository: what each branch holds, and what to do every time.

## What is live right now (since 15 Nov 2026)

- **Visitors get the new design as plain HTML pages.** They are built from `feature/php-site`;
  the exact package that was uploaded is on `go-live-package`.
- **The PHP version with the admin panel is uploaded but switched off for visitors.** PHP on the
  hosting fails about 1 request in 5. Network Solutions confirmed the fault on their server
  (support reference I-27429191). Once it is fixed, the admin is switched on (step 5 below).
- **The contact form** uses the hosting's own `send_mail.php`, which was not changed.

Full detail: [GO-LIVE.md](https://github.com/Akash-Modi104/vartec.github.io/blob/feature/php-site/php-site/deploy/go-live/GO-LIVE.md).

## Branches

| Branch | What it holds | Status |
| --- | --- | --- |
| `main` | The previous website: an Angular 14 app. `docs/` is a prebuilt copy for GitHub Pages. Also this README. | Kept as the record of the old site. No new work here. |
| [`feature/php-site`](https://github.com/Akash-Modi104/vartec.github.io/tree/feature/php-site) | **The new website.** Everything is in `php-site/`: the PHP 8.2 site with its admin, the tests, the build and check scripts, and the go-live notes. The Django files beside it are what it grew out of. | **Active. All new work goes here.** |
| [`go-live-package`](https://github.com/Akash-Modi104/vartec.github.io/tree/go-live-package) | Only the zip packages that were uploaded to the hosting, with their checksums. | Updated on every upload. |
| `codex/django-redesign` | The redesign as a Django CMS (September 2026). The Network Solutions plan cannot run Django, so its design and content became the starting point of the PHP site. | Parked. |
| `fix/remove-copytrack-floating-photo` | `main` plus one commit that removes the harbour floating-solar photo from the Angular site. | Not merged. The photo stays on the site. |
| `fix/redesign-remove-copytrack-photo` | The same removal in the Django redesign. `feature/php-site` was built on top of it and put the photo back later. | Nothing to do. |

## What to do every time

All commands run inside `php-site/` on `feature/php-site`.

### 1. Change something on the website

```bash
git checkout feature/php-site && git pull
cd php-site
export VARTEC_DATA_DIR=$(mktemp -d)
VARTEC_TEST_EXTRA=$PWD/tests/stand-ins php -S 127.0.0.1:8900 -t public public/index.php
# site: http://127.0.0.1:8900/    admin: http://127.0.0.1:8900/admin/
# the setup code for the first admin account is in $VARTEC_DATA_DIR/setup-code.php
```

- Design: `public/assets/site.css` and `site.js`. Pages: `public/app/templates/public/`.
  Starting content: `public/app/seed/content.json`.
- If you changed CSS or JavaScript, raise `APP_VERSION` in `public/app/bootstrap.php`.
- Run the tests (they need Playwright and Chrome): `python tests/e2e.py`,
  `python tests/admin_more.py`, `python tests/public.py`, `python tests/seo.py`.
- Commit and push.

### 2. Put the change live (while the plain HTML pages are live)

1. `tools/build_static_package.sh` builds `static-site.zip` and prints its pages.
2. In the hosting's File Manager open `/htdocs`, upload `static-site.zip`, unzip it there and
   delete the zip.
3. Upload any changed or new file from `public/assets/` and `public/media/` to the same folder
   in `/htdocs`.
4. Only if a page was added or removed: update the two page lists near the end of
   `/htdocs/.htaccess`.
5. Wait a minute, then run `tools/check_live.sh`. Every line must say OK.
6. Put the new zip on `go-live-package` and update the table in its README.

### 3. Try it on the test server first (optional)

```bash
curl -fsSL https://raw.githubusercontent.com/Akash-Modi104/vartec.github.io/feature/php-site/php-site/deploy/vps-test/install.sh | sudo bash
```

Run it on the test server. It installs or updates the PHP site behind the server's nginx and
touches no other site there.

### 4. Roll back

- Back to the old site for everyone: paste `php-site/deploy/go-live/htaccess-1-current.txt` into
  `/htdocs/.htaccess`.
- Back to the state before the plain HTML pages (old site for visitors, new one for testers):
  paste the contents of `/htdocs/.htaccess.before-static` into `/htdocs/.htaccess`.

Nothing of the old site was deleted on the hosting, so either works within about a minute.

### 5. When Network Solutions says PHP is fixed: switch on the admin

1. `tools/php_health.sh` must report 50 of 50. Run it again an hour later.
2. Follow "When Network Solutions says PHP is fixed" in GO-LIVE.md: test as a tester, create
   the admin account, switch `.htaccess` to `htaccess-3-live.txt`, check, and clean up a week
   later.

## Rules that never change

- Never touch `send_mail.php`, DNS or the mailboxes. No package contains a `send_mail.php`.
- Never test `send_mail.php` with a POST: every POST sends a real email to the company inbox.
  `tools/check_live.sh` and `tools/php_health.sh` only send harmless GET requests.
- This repository is public. The tester word, passwords, setup codes and recovery codes stay on
  the server and are never committed. The `.htaccess` files in git carry a placeholder.
- After any support action on the hosting, open `/htdocs/.htaccess` and check that its rules are
  still the ones that should be there.
- Before a bigger change, take a backup in the hosting panel or zip `/htdocs` in File Manager.

## The old Angular app (this branch)

```bash
npm install
npm start             # http://localhost:4200/
npm run build:pages   # prerenders into docs/ for GitHub Pages
```
