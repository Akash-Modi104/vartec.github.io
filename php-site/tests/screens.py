"""Full-page screenshots at several widths + layout checks (overflow, broken images, console errors)."""
import sys, json
from playwright.sync_api import sync_playwright
base, out = sys.argv[1], sys.argv[2]
specs = sys.argv[3:]          # name|path|width
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    for spec in specs:
        name, path, width = spec.split('|'); width = int(width)
        ctx = b.new_context(viewport={'width': width, 'height': 900 if width > 700 else 780}, reduced_motion='reduce', device_scale_factor=1)
        pg = ctx.new_page(); errs = []; failed = []
        pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
        pg.on('pageerror', lambda e: errs.append('PAGEERROR ' + str(e)))
        pg.on('response', lambda r: failed.append(f'{r.status} {r.url}') if r.status >= 400 else None)
        pg.goto(base + path, wait_until='load', timeout=90000); pg.wait_for_timeout(700)
        pg.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager')"); pg.wait_for_function('[...document.images].every(i=>i.complete)', timeout=60000); pg.wait_for_timeout(200)
        pg.evaluate("async () => { for (let y = 0; y < document.body.scrollHeight; y += 600) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); } await Promise.all([...document.images].map(i => i.decode().catch(() => {}))); window.scrollTo(0, 0); }")
        pg.wait_for_timeout(500)
        info = pg.evaluate("""() => {
          const vw = document.documentElement.clientWidth, over = [];
          document.querySelectorAll('body *').forEach(el => { const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
            if (r.width > 0 && (r.right > vw + 1 || r.left < -1) && cs.position !== 'fixed' && !el.closest('.hero-stage,.chatbot-panel,[hidden]')) over.push(el.tagName + '.' + el.className + ' ' + Math.round(r.left) + '..' + Math.round(r.right)); });
          return {scrollW: document.documentElement.scrollWidth, vw, over: over.slice(0, 6),
            broken: [...document.images].filter(i => i.complete && i.naturalWidth === 0).map(i => i.getAttribute('src')),
            h1: [...document.querySelectorAll('h1')].map(e => e.innerText.replace(/\\n/g, ' / ')),
            noalt: [...document.images].filter(i => !i.hasAttribute('alt')).length}; }""")
        pg.screenshot(path=f'{out}/{name}.png', full_page=True)
        pg.screenshot(path=f'{out}/{name}-top.png')
        bad = info['scrollW'] > info['vw'] or info['over'] or info['broken'] or errs or failed
        print(('ISSUE ' if bad else 'ok    ') + name, json.dumps({**info, 'errors': errs[:4], 'failed': failed[:4]}) if bad else info['h1'])
        ctx.close()
    b.close()
