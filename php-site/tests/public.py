"""Interaction checks on the public site: phone menu, desktop dropdown, banner slider, reveal, chat, form."""
import sys
from playwright.sync_api import sync_playwright
base, out = sys.argv[1], sys.argv[2]
res = []
def check(name, ok, detail=''): res.append(ok); print(('PASS ' if ok else 'FAIL ') + name + (f'  -> {detail}' if not ok else ''))
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    # phone
    ctx = b.new_context(viewport={'width': 390, 'height': 780}, has_touch=True); pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    pg.goto(base + '/', wait_until='load'); pg.wait_for_timeout(500)
    pg.click('.menu-toggle'); pg.wait_for_timeout(400)
    check('phone menu opens', pg.locator('.primary-nav.open').count() == 1)
    pg.click('.nav-group >> nth=0 >> button'); pg.wait_for_timeout(200)
    check('phone menu lists services', pg.locator('.nav-group.open .nav-dropdown a').first.is_visible())
    pg.screenshot(path=f'{out}/menu-390.png')
    box = pg.locator('.primary-nav').bounding_box(); check('phone menu fits the screen', box['x'] >= 0 and box['x'] + box['width'] <= 391, box)
    pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
    check('Escape closes the phone menu', pg.locator('.primary-nav.open').count() == 0)
    # reveal: something below the fold is hidden first, shown after scrolling
    hidden = pg.locator('.reveal:not(.in)').count()
    pg.evaluate("async () => { for (let y = 0; y < document.body.scrollHeight; y += 400) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 80)); } }"); pg.wait_for_timeout(900)
    check('sections ease in on scroll and none stay hidden', hidden > 0 and pg.locator('.reveal:not(.in)').count() == 0, (hidden, pg.locator('.reveal:not(.in)').count()))
    check('header gets its scrolled style', pg.locator('.site-header.scrolled').count() == 1)
    check('no script errors on phone', not errs, errs[:3]); ctx.close()
    # desktop
    ctx = b.new_context(viewport={'width': 1366, 'height': 800}); pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    pg.goto(base + '/', wait_until='load'); pg.wait_for_timeout(600)
    check('slider controls appear', pg.locator('[data-hero-controls]').is_visible() and pg.locator('[data-hero-dots] button').count() == 6)
    pg.click('[data-hero-next]'); pg.wait_for_timeout(1600)
    check('next arrow changes the banner photo', pg.locator('.hero-img.is-active').count() == 1 and pg.locator('[data-hero-dots] button[aria-current=true]').get_attribute('aria-label').startswith('Photo 2'))
    pg.screenshot(path=f'{out}/slide2-1366.png')
    pg.click('[data-hero-dots] button >> nth=4'); pg.wait_for_timeout(1600)
    check('dots jump to a photo', 'Photo 5' in pg.locator('[data-hero-dots] button[aria-current=true]').get_attribute('aria-label'))
    pg.hover('.nav-group >> nth=1'); pg.wait_for_timeout(250)
    check('desktop dropdown opens on hover', pg.locator('.nav-group >> nth=1 >> .nav-dropdown').is_visible())
    pg.screenshot(path=f'{out}/dropdown-1366.png')
    pg.mouse.move(600, 500)
    check('help button is compact over the banner', pg.locator('.chatbot.compact').count() == 1)
    pg.click('[data-chat-open]'); pg.wait_for_timeout(300); pg.fill('[data-chat-input]', 'Do you do battery storage?'); pg.keyboard.press('Enter'); pg.wait_for_timeout(500)
    check('help chat answers', 'battery' in pg.locator('.chatbot-message.bot').last.inner_text().lower())
    pg.screenshot(path=f'{out}/chat-1366.png'); pg.click('[data-chat-close]')
    pg.evaluate("document.querySelector('#about').scrollIntoView()"); pg.wait_for_timeout(1500)
    check('video starts once it is on screen', pg.evaluate("!document.querySelector('[data-inview-video]').paused"))
    pg.goto(base + '/services/epc/', wait_until='load'); pg.wait_for_timeout(400)
    check('services marked as current in the menu', pg.locator('.nav-group.current').count() == 1 and pg.locator('.nav-dropdown a[aria-current=page]').count() == 1)
    check('breadcrumb present', pg.locator('.breadcrumb li').count() == 3)
    check('no script errors on desktop', not errs, errs[:3]); ctx.close(); b.close()
print(f'{sum(res)} of {len(res)} passed'); sys.exit(0 if all(res) else 1)
