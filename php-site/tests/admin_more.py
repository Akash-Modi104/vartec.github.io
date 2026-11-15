"""Second admin test: every screen on desktop and phone, the newer admin items, and the remaining actions.

Run against a throwaway copy with an EMPTY data folder (the test creates an account and publishes):

    export VARTEC_DATA_DIR=$(mktemp -d)
    VARTEC_TEST_EXTRA=$PWD/tests/stand-ins php -S 127.0.0.1:8900 -t public public/index.php &
    python tests/admin_more.py
"""
import json, os, secrets, sys, urllib.request, urllib.error
from playwright.sync_api import sync_playwright

BASE = os.environ.get("VARTEC_TEST_BASE", "http://127.0.0.1:8900")
DATA = os.environ["VARTEC_DATA_DIR"]
SHOTS = os.environ.get("VARTEC_TEST_SHOTS", "/tmp/vartec-shots")
FIX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
os.makedirs(SHOTS, exist_ok=True)
USER, PASSWORD = "tester", secrets.token_urlsafe(12)      # throwaway local test account
results = []

def check(name, ok, detail=""):
    results.append((name, bool(ok)))
    print(("PASS " if ok else "FAIL ") + name + (("  -> " + str(detail)) if detail and not ok else ""))

def guarded(name):
    return json.loads(open(f"{DATA}/{name}.php", encoding="utf8").read().split("?>\n", 1)[1])

def get(path):
    try:
        with urllib.request.urlopen(BASE + path) as r:
            return r.status, r.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")

SCREENS = [("dashboard", "/admin/"), ("home", "/admin/home"), ("services", "/admin/pages?kind=service"), ("projects", "/admin/pages?kind=project"),
           ("other-pages", "/admin/pages?kind=info"), ("new-service", "/admin/page?kind=service"), ("new-page", "/admin/page?kind=info"),
           ("media", "/admin/media"), ("media-check", "/admin/media?show=check"), ("media-unused", "/admin/media?show=unused"),
           ("wording", "/admin/wording"), ("enquiries", "/admin/enquiries"), ("settings", "/admin/settings"), ("history", "/admin/history"), ("help", "/admin/help")]

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=os.environ.get("CHROME", "/usr/bin/google-chrome"), args=["--no-sandbox"])
    ctx = browser.new_context(viewport={"width": 1366, "height": 900})
    page = ctx.new_page()
    problems = []
    page.on("console", lambda m: problems.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: problems.append("PAGEERROR " + str(e)))
    confirm = lambda: page.click("dialog.confirm-dialog .btn-primary")
    save = lambda: (page.click('.savebar button[type="submit"]'), page.wait_for_selector(".notice-ok"))
    publish = lambda: (page.goto(BASE + "/admin/"), page.click('header.topbar button:has-text("Publish to website")'), page.wait_for_selector(".notice-ok"))

    check("signed-out visitor is sent to set-up / sign-in, never into the admin", "Create the first account" in get("/admin/settings")[1])
    page.goto(BASE + "/admin/")
    page.fill('input[name="code"]', guarded("setup-code")["code"]); page.fill('input[name="username"]', USER); page.fill('input[name="password"]', PASSWORD)
    page.click('button[type="submit"]'); page.wait_for_url(BASE + "/admin/")

    # --- every screen opens, on desktop and on a phone, without script errors or sideways scrolling
    for width in (1366, 390):
        page.set_viewport_size({"width": width, "height": 900})
        bad = []
        for name, path in SCREENS:
            r = page.goto(BASE + path, wait_until="load")
            wide = page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth + 1")
            if r.status != 200 or wide or page.locator("h1").count() != 1:
                bad.append((name, r.status, "wide" if wide else ""))
            if width == 1366:
                page.screenshot(path=f"{SHOTS}/screen-{name}.png", full_page=True)
        check(f"all {len(SCREENS)} admin screens open cleanly at {width}px", not bad, bad)
    page.goto(BASE + "/admin/")
    page.click("[data-menu]"); page.wait_for_timeout(300)
    check("phone menu opens the sidebar", page.locator(".sidebar.open").count() == 1)
    page.set_viewport_size({"width": 1366, "height": 900})
    check("unknown admin address shows a not-found screen", page.goto(BASE + "/admin/nothing-here").status == 404)
    problems.clear()   # the browser logs that deliberate 404

    # --- the user guide is offered on first sign-in and is for signed-in editors only
    page.goto(BASE + "/admin/")
    check("dashboard welcomes a new editor with the guide", page.locator(".card-welcome").count() == 1)
    guide = page.request.get(BASE + "/admin/guide")
    check("the guide opens as a PDF for a signed-in editor", guide.status == 200 and guide.headers.get("content-type") == "application/pdf" and guide.body()[:5] == b"%PDF-")
    anon = urllib.request.Request(BASE + "/admin/guide"); 
    check("the guide is not handed to someone who is not signed in", b"%PDF-" not in urllib.request.urlopen(anon).read()[:5])
    page.click('.card-welcome button:has-text("Hide this")'); page.wait_for_load_state()
    check("the welcome card can be hidden and stays hidden", page.locator(".card-welcome").count() == 0 and (page.reload() or True) and page.locator(".card-welcome").count() == 0)
    page.goto(BASE + "/admin/help"); check("Help keeps a link to the guide", page.locator('a[href="/admin/guide"]').count() >= 1)

    # --- Wording: change a menu name and a button, check the standard text comes back when cleared
    page.goto(BASE + "/admin/wording")
    page.fill('input[name="w[menu_about]"]', "Who we are & why"); page.fill('input[name="w[btn_send]"]', "Send it <now>"); save()
    check("wording is a draft until published", "Who we are &amp; why" not in get("/")[1])
    publish()
    html = get("/")[1]
    check("published wording shows on the website, safely escaped", "Who we are &amp; why" in html and "Send it &lt;now&gt;" in html and "<now>" not in html)
    page.goto(BASE + "/admin/wording"); page.fill('input[name="w[menu_about]"]', ""); page.fill('input[name="w[btn_send]"]', ""); save(); publish()
    html = get("/")[1]
    check("clearing a box brings back the standard wording", ">About Us</a>" in html and "Send message" in html)

    # --- Other pages: add a privacy policy
    page.goto(BASE + "/admin/pages?kind=info"); page.click("text=Add a page")
    page.fill('input[name="title"]', "Admin"); page.click('.savebar button[type="submit"]'); page.wait_for_selector(".notice-error")
    check("an address the site itself uses is refused", "used by the website itself" in page.content())
    page.fill('input[name="title"]', "Privacy policy"); page.fill('textarea[name="intro"]', "How we handle the details you send us.")
    page.click("[data-add-section]"); sec = page.locator("[data-section]").last
    sec.locator('[data-name="heading"]').fill("What we collect"); sec.locator('[data-name="body"]').fill("Your name, email address, phone number and message.")
    save()
    check("the new page is not public before publishing", get("/privacy-policy/")[0] == 404)
    publish()
    status, html = get("/privacy-policy/")
    check("published page is served at its own address", status == 200 and "What we collect" in html and "<h1>Privacy policy</h1>" in html)
    check("it has a two-step breadcrumb and no project call-to-action", html.count('<li') >= 2 and 'class="page-lead"' in html and "#services" not in html.split('class="breadcrumb"')[1].split("</ol>")[0])
    check("every page links to it at the bottom", 'href="/privacy-policy/"' in get("/")[1] and 'href="/privacy-policy/"' in get("/services/epc/")[1])
    check("it is in the sitemap", "/privacy-policy/</loc>" in get("/sitemap.xml")[1])
    check("address without the final slash redirects to it", "What we collect" in get("/privacy-policy")[1])
    page.goto(BASE + "/admin/pages?kind=info")
    page.click('.sort-row .switch'); page.click('button:has-text("Save order and visibility")'); page.wait_for_selector(".notice-ok"); publish()
    check("hiding the page takes it off the website", get("/privacy-policy/")[0] == 404 and 'href="/privacy-policy/"' not in get("/")[1])

    # --- Order of services
    page.goto(BASE + "/admin/pages?kind=service")
    first = page.locator(".sort-title strong").first.inner_text()
    page.locator('.sort-row [data-move="1"]').first.click(); page.click('button:has-text("Save order and visibility")'); page.wait_for_selector(".notice-ok"); publish()
    home = get("/")[1]; menu = home.split('class="nav-dropdown"')[1]
    check("changing the order changes the menu", menu.index(first) > menu.index("Consulting Services"), first)

    # --- Banner picture chosen for a page
    page.goto(BASE + "/admin/pages?kind=service"); page.click("text=Consulting Services >> nth=0"); page.wait_for_selector("[data-section]")
    page.click('summary:has-text("Banner picture")'); page.locator(".narrow-picker [data-picker-open]").click()
    page.wait_for_selector("#media-dialog[open]"); tile = page.locator("#media-dialog [data-tile][data-kind=image]").nth(5)
    chosen = tile.get_attribute("data-url"); tile.click(); save(); publish()
    hero = get("/services/consulting/")[1].split('class="page-hero')[1].split("</section>")[0]
    check("the chosen banner picture is used behind the title", chosen in hero, chosen)

    # --- Settings: help chat answers, Google code, social links
    page.goto(BASE + "/admin/settings")
    page.click("[data-add-answer]"); row = page.locator("[data-answers] [data-list-item]").last
    row.locator('[data-name="topic"]').fill("Warranty"); row.locator('[data-name="keywords"]').fill("warranty, guarantee"); row.locator('[data-name="answer"]').fill("Every installation carries a workmanship warranty. Please contact us for the terms.")
    page.fill('input[name="google_verification"]', '<meta name="google-site-verification" content="abcDEF123456_-test-code" />')
    page.fill('input[name="social[linkedin]"]', "https://www.linkedin.com/company/example-test")
    save(); publish()
    html = get("/")[1]
    check("Google verification code is taken from the pasted line", '<meta name="google-site-verification" content="abcDEF123456_-test-code">' in html)
    check("social link shows in the footer and in the search data", 'href="https://www.linkedin.com/company/example-test"' in html and '"sameAs":["https://www.linkedin.com/company/example-test"]' in html)
    page.goto(BASE + "/admin/settings"); page.fill('input[name="social[facebook]"]', "javascript:alert(1)")
    page.evaluate("document.querySelector('input[name=\"social[facebook]\"]').type = 'text'"); page.click('.savebar button[type="submit"]'); page.wait_for_selector(".notice-error")
    check("a link that is not https is refused", "should start with https://" in page.content())
    visitor = browser.new_page(); visitor.goto(BASE + "/"); visitor.click("[data-chat-open]"); visitor.fill("[data-chat-input]", "Is there a guarantee?"); visitor.keyboard.press("Enter"); visitor.wait_for_timeout(500)
    reply = visitor.locator(".chatbot-message.bot").last
    check("the website chat gives the new answer", "workmanship warranty" in reply.inner_text() and reply.locator('a[href="#contact"]').count() == 1, reply.inner_text())
    visitor.fill("[data-chat-input]", "zzzz"); visitor.keyboard.press("Enter"); visitor.wait_for_timeout(500)
    check("unknown questions get the fall-back answer", "general information" in visitor.locator(".chatbot-message.bot").last.inner_text())
    visitor.close()

    # --- Images: details, licence, remove an unused one
    page.goto(BASE + "/admin/media")
    page.set_input_files('.upload input[type="file"]', os.path.join(FIX, "test-photo.jpg"))
    page.fill('.upload input[name="alt"]', "Spare test photo"); page.select_option('.upload select[name="licence"]', "unknown"); page.click('.upload button[type="submit"]'); page.wait_for_selector(".notice-ok")
    page.goto(BASE + "/admin/media?show=unused"); page.click('.media-card:has-text("Spare test photo") >> text=Details')
    page.fill('input[name="alt"]', "Spare photo, renamed"); page.select_option('select[name="licence"]', "licensed"); page.click('button:has-text("Save details")'); page.wait_for_selector(".notice-ok")
    item = [m for m in guarded("draft")["media"].values() if m.get("alt") == "Spare photo, renamed"]
    check("picture details and licence are saved", bool(item) and item[0]["licence"] == "licensed")
    page.goto(BASE + "/admin/media?show=unused"); page.click('.media-card:has-text("Spare photo, renamed") button:has-text("Remove")'); confirm(); page.wait_for_selector(".notice-ok")
    MEDIA = os.path.join(os.path.dirname(FIX), "..", "public", "media")
    check("a never-published picture is removed and its file deleted at once", not [m for m in guarded("draft")["media"].values() if m.get("alt") == "Spare photo, renamed"] and not os.path.exists(os.path.join(MEDIA, item[0]["file"])))
    page.goto(BASE + "/admin/media"); page.set_input_files('.upload input[type="file"]', os.path.join(FIX, "test-photo.jpg"))
    page.fill('.upload input[name="alt"]', "Published spare photo"); page.click('.upload button[type="submit"]'); page.wait_for_selector(".notice-ok"); publish()
    page.goto(BASE + "/admin/media?show=unused"); card = page.locator('.media-card:has-text("Published spare photo")')
    old_file = card.locator("img").get_attribute("src"); card.locator('button:has-text("Remove")').click(); confirm(); page.wait_for_selector(".notice-ok")
    check("a published picture stays reachable until the removal is published", get(old_file)[0] == 200 and "next publish" in page.locator(".notice-ok").inner_text(), old_file)
    publish()
    check("after publishing, the removed picture is gone from the server", get(old_file)[0] == 404 and not os.path.exists(os.path.join(MEDIA, old_file.split("/media/")[1])), old_file)
    used = page.request.post(BASE + "/admin/media/delete", form={"id": "logo", "_csrf": page.locator('meta[name="csrf"]').get_attribute("content")})
    check("a picture that is in use cannot be removed", used.status < 400 and "logo" in guarded("draft")["media"] and os.path.exists(os.path.join(MEDIA, "logo.png")), used.status)

    # --- Enquiries: mark done, delete
    visitor = browser.new_page(); visitor.goto(BASE + "/#contact")
    for name, value in [("firstName", "Sam"), ("lastName", "Tester"), ("email", "sam@example.com"), ("phone", "0800 000 000"), ("message", "Second test enquiry")]:
        visitor.fill(f'[name="{name}"]', value)
    visitor.click('[data-contact-form] button[type="submit"]'); visitor.wait_for_selector("[data-contact-status]:not([hidden])"); visitor.close()
    page.goto(BASE + "/admin/enquiries")
    check("new enquiry is counted in the menu", page.locator(".sidebar .pill").inner_text() == "1")
    page.click('button:has-text("Mark as done")'); page.wait_for_load_state()
    check("marking it done clears the counter", page.locator(".sidebar .pill").count() == 0 and "Done" in page.locator(".enquiry .badge").first.inner_text())
    page.click('.enquiry button:has-text("Delete")'); confirm(); page.wait_for_load_state()
    check("deleting removes it from the inbox", page.locator(".enquiry").count() == 0)

    # --- Editors: add, sign in as them, remove
    second_password = secrets.token_urlsafe(12)
    page.goto(BASE + "/admin/settings")
    page.fill('.add-editor input[name="username"]', "second"); page.fill('.add-editor input[name="password"]', "short");
    page.evaluate("document.querySelector('.add-editor input[name=password]').removeAttribute('minlength')"); page.click('.add-editor button'); page.wait_for_selector(".notice-error")
    check("a short password for a new editor is refused", "second" not in guarded("users"))
    page.fill('.add-editor input[name="username"]', "second"); page.fill('.add-editor input[name="password"]', second_password); page.click('.add-editor button'); page.wait_for_selector(".notice-ok")
    other = browser.new_context().new_page(); other.goto(BASE + "/admin/login")
    other.fill('input[name="username"]', "second"); other.fill('input[name="password"]', second_password); other.click('button[type="submit"]'); other.wait_for_load_state()
    check("a new editor must choose their own password first", "Choose your own password" in other.content())
    other.goto(BASE + "/admin/home"); check("and cannot reach any screen before doing so", "Choose your own password" in other.content() and "Banner" not in other.content())
    own_password = secrets.token_urlsafe(12)
    other.fill('input[name="current_password"]', second_password); other.fill('input[name="new_password"]', second_password); other.click('button:has-text("Save and continue")'); other.wait_for_load_state()
    check("re-using the temporary password is refused", "Choose your own password" in other.content())
    other.fill('input[name="current_password"]', second_password); other.fill('input[name="new_password"]', own_password); other.click('button:has-text("Save and continue")'); other.wait_for_url(BASE + "/admin/")
    check("after choosing a password the new editor reaches the dashboard", "Dashboard" in other.title())
    page.goto(BASE + "/admin/settings"); page.click('#editors .list-row:has-text("second") button'); confirm(); page.wait_for_selector(".notice-ok")
    other.goto(BASE + "/admin/home")
    check("a removed editor is signed out at once", other.url.endswith("/admin/login"))
    other.close()

    # --- Delete a page
    page.goto(BASE + "/admin/pages?kind=info"); page.click('.sort-title:has-text("Privacy policy")'); page.wait_for_selector("[data-section]")
    page.click('button:has-text("Delete this page")'); confirm(); page.wait_for_selector(".notice-ok")
    check("a deleted page leaves the list", page.locator(".sort-row").count() == 0)

    check("no script errors anywhere in the admin", not problems, problems[:3])
    browser.close()

log = "/tmp/php-admin-more.log"
if os.path.exists(log):
    bad = [l for l in open(log, errors="replace") if any(w in l for w in ("Warning", "Fatal", "Notice", "Deprecated"))]
    check("no PHP warnings during the run", not bad, bad[:2])
passed = sum(ok for _, ok in results)
print(f"\n{passed} of {len(results)} checks passed")
sys.exit(0 if passed == len(results) else 1)
