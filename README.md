# VARTEC: packages that were uploaded to the hosting

This branch only holds ready-made packages for Network Solutions. The source is on
`feature/php-site`; the instructions are in `php-site/deploy/go-live/GO-LIVE.md` there.

| File | What it is | Built from | SHA-256 |
| --- | --- | --- | --- |
| `static-site.zip` | **Live now.** The public pages as plain HTML (`static-site/`). Unzipped in `/htdocs` on 15 Nov 2026. | `feature/php-site` ad997ed | `04dc9c3bf0521def8f056e3210a6eda6ee70b0d6b989a3f69642f992ec5e9bb7` |
| `vartec-site-files.zip` | The PHP version with the admin (`index.php`, `app/`, `media/`, `assets/`, `.user.ini`). Unzipped in `/htdocs` on 15 Nov 2026, reachable only with the tester cookie. | `feature/php-site` 015349b | `3d2ba0bb35d1a68d643a554864b7c2f964c606aeb1b23071ff86b1f4e7664618` |

Neither package contains a `send_mail.php` or a root `.htaccess`, so unzipping one cannot change
the mail script or switch the site.

`static-site.zip` also carries `static-site/htaccess.txt`, the `.htaccess` template that was used
for the switch. It was removed from the server after the switch.

## Every time a new package goes to the hosting

1. Build it on `feature/php-site` (`php-site/tools/build_static_package.sh` for the static pages).
2. Replace the file here, update the table above (source commit and SHA-256: `sha256sum <file>`),
   commit and push.
3. Upload and unzip it in `/htdocs`, then run `php-site/tools/check_live.sh`.

To fetch a package by an address that can never change, use the commit id, not the branch name:
`https://raw.githubusercontent.com/Akash-Modi104/vartec.github.io/<commit id>/static-site.zip`
