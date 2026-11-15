# VARTEC on Network Solutions: where things stand and what to do

Two rules for every step:

- `send_mail.php`, DNS and the mailboxes are never touched. No package contains a `send_mail.php`.
- Never test `send_mail.php` with a POST: every POST sends a real email to the company inbox. A GET
  (`/send_mail.php?x=1`) answers "Invalid request" and is safe.

## Where things stand (15 Nov 2026, 14:56 UTC)

- **Live for visitors: the new design as plain HTML files.** They sit in `/htdocs/static-site/` and
  `/htdocs/.htaccess` maps the clean addresses to them. That `.htaccess` is `htaccess-4-static.txt`
  with the tester word filled in. There is no admin on the live site yet.
- **The PHP version with the admin is uploaded but not live.** `index.php`, `app/`, `media/`, `data/`
  and `.user.ini` are in `/htdocs`. Only a browser carrying the tester cookie reaches it.
- **Why not live:** about 1 in 5 PHP requests on this hosting gets Network Solutions' own
  "Page Not Found" page (693 bytes). It also affects the old `send_mail.php`, so it existed before
  this work. Plain files are not affected. Network Solutions confirmed a fault on their server on
  15 Nov 2026 (support reference I-27429191) and asked to check back after 24 hours.
- **Contact form:** it posts to the existing `send_mail.php` exactly as the old site did. While the
  fault lasts, about 1 send in 5 fails; the visitor sees the error message, keeps the text and can
  press send again.
- **The old site is still on the server**, unused by visitors: `index.html`, `main.*.js` and the
  rest, plus `archive_261115_113032.tar`. Nothing of it was deleted.
- **Old page in the browser:** someone who opened the old site recently can still see it from the
  browser's own cache until they refresh once (Ctrl + F5, on a Mac Cmd + Shift + R).

## Every time the site changes while the static pages are live

1. Make the change in `php-site/` and look at it locally (see `php-site/README.md`, "Run locally").
   If you changed CSS or JavaScript, raise `APP_VERSION` in `public/app/bootstrap.php` so browsers
   fetch the new files.
2. Run the tests (`tests/e2e.py`, `tests/admin_more.py`, `tests/public.py`, `tests/seo.py`).
3. Build the package: `tools/build_static_package.sh` prints the pages and writes `static-site.zip`.
4. In File Manager open `/htdocs`, upload `static-site.zip`, unzip it there and delete the zip. It
   only overwrites files inside `static-site/`.
5. Upload any changed or new file from `public/assets/` and `public/media/` to the same folder in
   `/htdocs`. The pages load their stylesheet, scripts and pictures from there.
6. Only if a page was added or removed: add or remove its name in the two page lists near the end
   of `/htdocs/.htaccess` (same lines as in `htaccess-4-static.txt`).
7. Wait a minute, then run `tools/check_live.sh`. Every line must say OK.
8. Commit and push `feature/php-site`, and put the new `static-site.zip` on the `go-live-package`
   branch so the package that is live is always in git.

If you cannot upload by hand, `helper-fetch.php.txt` makes the hosting fetch the zip from GitHub.
Its instructions are at the top of the file.

## Roll back

- **Back to the old site for everyone:** paste `htaccess-1-current.txt` into `/htdocs/.htaccess`.
- **Back to "old site for visitors, new site for testers":** in File Manager open
  `/htdocs/.htaccess.before-static` and paste its contents into `/htdocs/.htaccess`.

Either takes effect within about a minute.

## When Network Solutions says PHP is fixed

1. Run `tools/php_health.sh`. It must report 50 of 50. Run it again an hour later.
2. Become a tester: on vartec.global open the browser console and run
   `document.cookie="vartec_stage=YOUR-WORD; path=/; max-age=86400; secure"`, then reload. The word
   is the one in `/htdocs/.htaccess`.
   - Open every page, on a phone too.
   - `/admin/`: create the first account with the setup code from `/htdocs/data/setup-code.php`
     (File Manager). Sign in and out several times, save a draft, publish, upload and remove a
     picture. Reload often: the hosting runs on several servers and they must agree.
   - Send the contact form once. One real email must arrive as it does today, and a copy must
     appear under Enquiries.
3. Switch: replace `/htdocs/.htaccess` with `htaccess-3-live.txt`. Check the home page, one service,
   one project, `/admin/`, the contact form, `/robots.txt` and `/sitemap.xml`.
4. If anything is wrong, paste `htaccess-4-static.txt` (with the tester word) back: the static pages
   are live again.
5. A week later delete what is no longer used: `static-site/`, `.htaccess.before-static`,
   `index.html`, `main.*.js`, `polyfills.*.js`, `runtime.*.js`, `scripts.*.js`, `styles.*.css`,
   `MaterialIcons-*`, `poppins-*`, `owl.video.play.*.png`, `3rdpartylicenses.txt`, the old picture
   folders inside `assets/`, and `archive_261115_113032.tar`. Keep `send_mail.php`, `favicon.ico`
   and `.htaccess`.
6. Add Craig under Settings > Editors with a temporary password; he must choose his own at first
   sign-in. Both of you should turn on two-step sign-in. Add the site to Google Search Console and
   paste the verification code under Settings.

## The `.htaccess` files in this folder

| File | What it does |
| --- | --- |
| `htaccess-1-current.txt` | The original. Old site for everyone. |
| `htaccess-2-stage.txt` | Old site for visitors, PHP version for testers. |
| `htaccess-3-live.txt` | PHP version (with admin) for everyone. |
| `htaccess-4-static.txt` | **In use now.** Static pages for visitors, PHP version for testers. |

Files 2 and 4 contain `PUT-A-LONG-RANDOM-WORD-HERE`. The real word is only on the server, never in
git: this repository is public.

## What is known about this hosting

- Starter (Hosting-Unix), Apache behind openresty, PHP 8.2.35 (cgi-fcgi). GD with WebP, mbstring,
  fileinfo, iconv, curl, zip, sessions and `mail()` are present. Upload limit 100 MB, memory
  512 MB, `.user.ini` supported.
- HTTPS is reported to PHP correctly (`HTTPS=on`, `X-Forwarded-Proto: https`), so the admin's HTTPS
  redirect cannot loop.
- PHP cannot create a folder next to `htdocs`, so the site keeps its data in `htdocs/data`. That
  folder is refused by `.htaccess`, has its own deny file, and every file in it starts with an exit
  line.
- The hosting runs on several servers. A file just created can return "Page Not Found" for up to
  about a minute on some requests. Wait a minute after each upload before judging a result.
- **Support actions can rewrite `.htaccess`.** When support reinstalled PHP on 15 Nov 2026 the file
  was rewritten without its comments and blank lines. The rules survived. After any support
  action, open `/htdocs/.htaccess` and compare its rules with the file that should be there.
- Since that reinstall `allow_url_fopen` is off. The site does not need it; curl works.
- A request for a `.php` address can get the hosting's own 404 instead of the 403 from `.htaccess`
  while the fault lasts. Private files are not exposed either way.

## Rehearsal

Every switch was first run on a local Apache copy of the live `htdocs`: staging kept the visitors'
home page byte-identical, the PHP version passed all 114 checks with the final `.htaccess` and the
data folder inside `htdocs`, and the static setup passed the page, redirect, 404 and private-path
checks that `tools/check_live.sh` now repeats on the live site.
