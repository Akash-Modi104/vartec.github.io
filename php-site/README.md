# VARTEC website (PHP)

The redesigned VARTEC website and its admin, written in plain PHP 8.2 so it runs on the existing
Network Solutions Starter hosting. No database, no framework and no build step.

## What is here

| Path | Purpose |
| --- | --- |
| `public/` | Everything that is uploaded to the web root (`/htdocs`). |
| `public/index.php` | Single entry point for the public pages and the admin. |
| `public/app/` | PHP code, page templates and the starting content. Never served directly. |
| `public/assets/` | CSS and JavaScript for the site and the admin. |
| `public/media/` | Images and video. Admin uploads go to `media/uploads/`. |
| `tools/build_seed.py` | Rebuilds the starting content from the approved Django redesign. |
| `tests/e2e.py` | Browser test of the public site, contact form, admin and security (52 checks). |
| `tests/admin_more.py` | Every admin screen on desktop and phone, plus wording, other pages, banner picture, chat answers, pictures (upload, details, remove and file deletion), enquiries, editors and first-sign-in password change (45 checks). Run it like `e2e.py`, on its own empty data folder. |
| `tools/build_guide.py` | Rebuilds the illustrated user guide served at `/admin/guide` (`public/app/guide/VARTEC-admin-guide.pdf`). |
| `tools/add_harbour_photo.php` | One-off for sites set up before the harbour floating-solar photo was restored. |
| `tests/public.py` | Public-site behaviour: phone menu, dropdowns, banner slider, scroll effects, help chat, video (17 checks). `python tests/public.py <address> <folder for screenshots>` |
| `tests/screens.py` | Full-page screenshots at any width, reporting sideways overflow, broken images and script errors. `python tests/screens.py <address> <folder> 'home-390\|/\|390' …` |
| `tests/seo.py` | Search-engine audit of every page in the sitemap (titles, descriptions, canonical, headings, image sizes, structured data). `python tests/seo.py <address> vartec.global` |
| `deploy/vps-test/install.sh` | One-command install on a test server. |
| `tools/export_static.py` | Saves the public pages as plain HTML files (used by the next script). |
| `tools/build_static_package.sh` | Builds `static-site.zip`, the plain-HTML copy of the public site that is live while PHP on the hosting is unreliable. |
| `tools/check_live.sh` | Checks the live site as a visitor sees it: pages, redirects, 404, private paths, files. Read-only. Run after every upload. |
| `tools/php_health.sh` | Measures whether PHP on the hosting answers every request. GET only. Run before switching to the PHP version. |
| `deploy/go-live/` | Where the live site stands, what to do for every change, how to roll back, and the four `.htaccess` versions. |

Content lives in a private data folder: `vartec-data/` beside the web root when the server allows
it, otherwise `public/data/`. Every data file is a `.php` file that exits immediately, so it reveals
nothing even if requested directly.

## How editing works

Editors change a **draft**, **preview** it (`?preview=1`, signed-in editors only) and **publish**.
Each publish keeps the version it replaced (last 30) under Settings > Earlier versions.

## Email

The contact form posts to the **existing** `send_mail.php` on the server with the same five fields
the previous site sent (`firstName`, `lastName`, `email`, `phone`, `message`). This project does not
contain, replace or change that script, and makes no DNS or mailbox change. After the email is
sent the browser also stores a copy of the enquiry for the admin inbox (`/enquiry`); that copy can
fail without affecting the email.

## Security

- Passwords stored as salted hashes; minimum 10 characters; easy passwords refused.
- Optional two-step sign-in with an authenticator app (Settings).
- Sign-in limits per visitor (8 tries) and per account (20 tries) in 15 minutes.
- Sessions: HttpOnly, SameSite, Secure on HTTPS; signed out after 2 hours idle or 12 hours.
  Changing a password signs out every other browser.
- Every form carries a one-time security token (CSRF protection).
- The first account can only be created with a setup code written to the private data folder.
- Uploads are checked by reading the file, renamed, resized, and cannot run as programs.
- Editor text is always escaped; the admin runs under a strict Content-Security-Policy.
- Activity log of sign-ins, publishing and account changes (Settings > Recent activity).
- On the live address the admin redirects to HTTPS.

## Run locally

```bash
export VARTEC_DATA_DIR=$(mktemp -d)
VARTEC_TEST_EXTRA=$PWD/tests/stand-ins php -S 127.0.0.1:8900 -t public public/index.php
# open http://127.0.0.1:8900/ and http://127.0.0.1:8900/admin/
# the setup code is in $VARTEC_DATA_DIR/setup-code.php
python tests/e2e.py   # in another terminal; needs Playwright and Chrome
```

## Install on a test server

```bash
curl -fsSL https://raw.githubusercontent.com/Akash-Modi104/vartec.github.io/feature/php-site/php-site/deploy/vps-test/install.sh | sudo bash
```

Needs Docker and nginx. It runs Apache + PHP 8.2 in one container (so `.htaccess` behaves as on
Network Solutions), adds one nginx site and prints the address and the setup code. The test server
uses a stand-in `send_mail.php` that records messages instead of emailing them.

## Go live on Network Solutions

Everything about the live hosting is in [`deploy/go-live/GO-LIVE.md`](deploy/go-live/GO-LIVE.md):
where things stand, what to do every time the site changes, how to roll back, and how to switch
to this PHP version once Network Solutions has fixed PHP on their server.

Since 15 Nov 2026 visitors get a plain-HTML copy of the public pages built from this project
(`tools/build_static_package.sh`). The PHP version with the admin is uploaded but only reachable
with the tester cookie.
