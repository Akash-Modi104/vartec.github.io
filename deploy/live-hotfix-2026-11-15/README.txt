VARTEC live site hotfix - 15 November 2026
Removes the floating-solar harbour photo named in Copytrack case 83734B (rights holder: YayImages).

What changed
- Home page banner: the slide using assets/image/hero3-min.jpg is no longer shown.
- /project/floating: the third block ("Floating Solar Installation"), which only showed that photo, is removed.
- Nothing else on the site changes.

How to apply (Network Solutions > Hosting > File Manager, or FTP), in this order
1. Upload main.48d9d426cf68df14.js to the web root (next to index.html).
2. Upload index.html, replacing the existing one.
3. Delete these three files from the server:
     main.eb39adcf0c764422.js
     assets/image/hero3-min.jpg
     assets/project/Floating solar/floating solar 2.jpg
4. Open https://vartec.global/project/floating in a private window and confirm only two projects show.

To undo: re-upload the previous index.html (kept in backup/index.html in this folder) and the old main file.
