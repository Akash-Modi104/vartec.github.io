# Putting the new site live on Network Solutions

Rule for every step: `send_mail.php`, DNS and the mailboxes are never touched. The package contains no `send_mail.php`.

## What was checked on the hosting (15 Nov 2026)
- Starter (Hosting-Unix), Apache, PHP 8.2.35 (cgi-fcgi). GD with WebP, mbstring, fileinfo, iconv, sessions and `mail()` are present. Upload limit 100 MB, memory 512 MB, `.user.ini` supported.
- HTTPS is reported to PHP correctly (`HTTPS=on`, `X-Forwarded-Proto: https`), so the admin's HTTPS redirect cannot loop.
- PHP cannot create a folder next to `htdocs`, so the site keeps its data in `htdocs/data`. That folder is refused by `.htaccess`, has its own deny file, and every file in it starts with an exit line.
- The hosting runs on several servers. A file just created can return "Page Not Found" for up to about a minute on some requests. Wait a minute after each upload before judging a result.
- Current files in `htdocs` match the backup `vartec-backup-2026-11-15.zip`.

## Rehearsal
The whole sequence below was run on a local Apache copy of the live `htdocs`: visitors' home page stayed byte-identical during staging, and all 114 checks passed with the final `.htaccess` and the data folder inside `htdocs`.

## Steps
1. **Backup.** Hosting > Website Backups, or File Manager > select all > Zip, and download it. Keep `htaccess-1-current.txt` to hand.
2. **Stage (no visible change).** In File Manager, edit `/htdocs/.htaccess` and replace its contents with `htaccess-2-stage.txt` (with your own long random word in the four places). Open the site in a private window: it must look exactly as before. If anything is wrong, paste `htaccess-1-current.txt` back.
3. **Upload.** Upload `vartec-site-files.zip` into `/htdocs` and unzip it there. It adds `index.php`, `app/`, `media/`, `.user.ini` and new files inside `assets/`. It overwrites nothing that exists today. Wait a minute.
4. **Test as a tester.** On vartec.global open the browser console and run
   `document.cookie="vartec_stage=YOUR-WORD; path=/; max-age=86400; secure"`, then reload. You now see the new site; everyone else sees the old one.
   - Open every page, on a phone too.
   - `/admin/`: create the first account with the setup code from `/htdocs/data/setup-code.php` (File Manager). Sign in and out several times, save a draft, publish, upload and remove a picture. Reload often: this is the check that the several servers agree with each other.
   - Send the contact form once. One real email must arrive exactly as it does today, and a copy must appear under Enquiries.
5. **Switch.** Replace `/htdocs/.htaccess` with `htaccess-3-live.txt`. The new site is live for everyone. Check the home page, one service, one project, `/admin/`, the contact form, `/robots.txt` and `/sitemap.xml`.
6. **Roll back if needed.** Paste `htaccess-1-current.txt` into `/htdocs/.htaccess`. The old site is back within about a minute; nothing of it was deleted.
7. **A week later.** Delete the old files: `index.html`, `main.*.js`, `polyfills.*.js`, `runtime.*.js`, `scripts.*.js`, `styles.*.css`, `MaterialIcons-*`, `poppins-*`, `owl.video.play.*.png`, `3rdpartylicenses.txt`, the old picture folders inside `assets/`, and `archive_261115_113032.tar`. Keep `send_mail.php`, `favicon.ico`, `.htaccess`.

## After going live
- Add Craig under Settings > Editors with a temporary password; he must choose his own at first sign-in. Both of you should turn on two-step sign-in.
- Add the site to Google Search Console and paste the verification code under Settings.
- Old addresses such as `/project/carports` redirect to the new ones automatically.
