"""Saves the public website as plain HTML files (no PHP needed to serve them).

    python tools/export_static.py <address of a running copy> <real site host> <output folder>

The pages are fetched as the real site address, so they carry the right search-engine tags.
Writes <output>/static-site/... and prints the list of page addresses for the .htaccess rules.
"""
import os, re, sys, urllib.request
base, host, out = sys.argv[1].rstrip('/'), sys.argv[2], sys.argv[3]
root = os.path.join(out, 'static-site')
def fetch(path):
    req = urllib.request.Request(base + path, headers={'Host': host})
    try:
        with urllib.request.urlopen(req) as r: return r.status, r.read()
    except urllib.error.HTTPError as e: return e.code, e.read()
def save(rel, data):
    path = os.path.join(root, rel); os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'wb').write(data)
status, sitemap = fetch('/sitemap.xml'); assert status == 200
pages = [u.replace('https://' + host, '') for u in re.findall(r'<loc>([^<]+)', sitemap.decode())]
for page in pages:
    status, html = fetch(page); assert status == 200, (page, status)
    text = html.decode()
    assert 'noindex' not in text and f'<link rel="canonical" href="https://{host}{page}">' in text, page
    save((page.strip('/') + '/index.html').lstrip('/'), html)
status, notfound = fetch('/this-page-does-not-exist'); assert status == 404 and b'noindex' in notfound
save('404.html', notfound)
save('sitemap.xml', sitemap)
status, robots = fetch('/robots.txt'); assert status == 200 and b'Allow: /' in robots
save('robots.txt', robots)
print('\n'.join(pages))
