"""End-to-end test of the VARTEC PHP site: public pages, contact form, admin and its security.

Run against a throwaway copy with an empty data folder (the test creates an account and publishes):

    export VARTEC_DATA_DIR=$(mktemp -d)
    VARTEC_TEST_EXTRA=$PWD/tests/stand-ins php -S 127.0.0.1:8900 -t public public/index.php &
    python tests/e2e.py

Needs Python with Playwright and a Chrome/Chromium binary (set CHROME to its path).
"""
import json, os, re, secrets, sys, subprocess, urllib.request
from playwright.sync_api import sync_playwright

BASE = os.environ.get("VARTEC_TEST_BASE", "http://127.0.0.1:8900")
DATA = os.environ["VARTEC_DATA_DIR"]          # the test server's private data folder
SHOTS = os.environ.get("VARTEC_TEST_SHOTS", "/tmp/vartec-shots")
FIX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
os.makedirs(SHOTS, exist_ok=True)
USER, PASSWORD = "tester", secrets.token_urlsafe(12)   # throwaway local test account
results = []

def check(name, ok, detail=""):
    results.append((name, bool(ok)))
    print(("PASS " if ok else "FAIL ") + name + (("  -> " + str(detail)) if detail and not ok else ""))

def guarded(name):
    raw = open(f"{DATA}/{name}.php", encoding="utf8").read()
    return json.loads(raw.split("?>\n", 1)[1])

def get(path):
    with urllib.request.urlopen(BASE + path) as r:
        return r.read().decode()

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=os.environ.get("CHROME", "/usr/bin/google-chrome"), args=["--no-sandbox"])
    ctx = browser.new_context(viewport={"width": 1366, "height": 900})
    page = ctx.new_page()
    problems = []
    page.on("console", lambda m: problems.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: problems.append("PAGEERROR " + str(e)))

    # --- first-run setup needs the code from the private data folder
    page.goto(BASE + "/admin/")
    check("first visit shows account setup", "Create the first account" in page.content())
    page.fill('input[name="code"]', "WRONGCODE"); page.fill('input[name="username"]', USER); page.fill('input[name="password"]', PASSWORD)
    page.click('button[type="submit"]')
    check("wrong setup code is refused", "setup code is not right" in page.content())
    code = guarded("setup-code")["code"]
    page.fill('input[name="code"]', code); page.fill('input[name="username"]', USER); page.fill('input[name="password"]', PASSWORD)
    page.click('button[type="submit"]')
    page.wait_for_url(BASE + "/admin/")
    check("setup creates the account and signs in", "Dashboard" in page.title())
    check("setup code file is deleted afterwards", not os.path.exists(f"{DATA}/setup-code.php"))
    check("dashboard flags unlicensed images", "no licence on record" in page.content())
    page.screenshot(path=f"{SHOTS}/admin-dashboard.png", full_page=True)

    # --- edit a project on one screen: title, new section with a bullet
    page.goto(BASE + "/admin/pages?kind=project")
    page.screenshot(path=f"{SHOTS}/admin-projects.png", full_page=True)
    page.click("text=Carports >> nth=0")
    page.wait_for_selector("form[data-page-form]")
    before_sections = page.locator("[data-section]").count()
    page.fill('input[name="title"]', "Solar Carports")
    page.click("[data-add-section]")
    new = page.locator("[data-section]").last
    new.locator('[data-name="heading"]').fill("Hospital car park, 2026")
    new.locator('[data-name="body"]').fill("A 900 kWp carport with 40 charging bays.")
    new.locator('[data-add-item="bullet"]').click()
    new.locator('[data-item] [data-name="text"]').fill("Built in 14 weeks")
    page.screenshot(path=f"{SHOTS}/admin-page-editor.png", full_page=True)
    page.click('.savebar button[type="submit"]')
    page.wait_for_selector(".notice-ok")
    check("page saves as a draft", "saved as a draft" in page.content())
    check("new section kept after save", page.locator("[data-section]").count() == before_sections + 1)
    check("topbar shows unpublished changes", "changes that are not live yet" in page.content())
    live_html = get("/projects/carports/")
    check("live page is unchanged before publishing", "Hospital car park" not in live_html and "<h1>Carports</h1>" in live_html)
    page.goto(BASE + "/projects/carports/?preview=1")
    check("preview shows the draft to the signed-in editor", "Hospital car park, 2026" in page.content() and "Built in 14 weeks" in page.content())
    check("preview is marked noindex", 'content="noindex,nofollow"' in page.content())
    anon = get("/projects/carports/?preview=1")
    check("preview is not available to visitors", "Hospital car park" not in anon)

    # --- reorder sections with the arrows, then publish
    page.goto(BASE + "/admin/pages?kind=project"); page.click("text=Solar Carports >> nth=0"); page.wait_for_selector("[data-section]")
    page.locator("[data-section]").last.locator('.block-head [data-move="-1"]').click()
    page.click('.savebar button[type="submit"]'); page.wait_for_selector(".notice-ok")
    order = guarded("draft")["pages"]
    carports = [x for x in order if x["slug"] == "carports"][0]
    check("moving a section up changes the saved order", carports["sections"][-2]["heading"] == "Hospital car park, 2026")
    page.click('header.topbar button:has-text("Publish to website")')
    page.wait_for_selector(".notice-ok")
    live_html = get("/projects/carports/")
    check("publish makes the change live", "Hospital car park, 2026" in live_html and "<h1>Solar Carports</h1>" in live_html)
    check("home page and menu pick up the new title", "Solar Carports" in get("/"))

    # --- image upload: resized, described, licence recorded; bad file refused
    page.goto(BASE + "/admin/media")
    page.set_input_files('.upload input[type="file"]', os.path.join(FIX, "test-photo.jpg"))
    page.fill('.upload input[name="alt"]', "Test carport photo"); page.fill('.upload input[name="source"]', "Taken by our site team")
    page.select_option('.upload select[name="licence"]', "own"); page.click('.upload button[type="submit"]')
    page.wait_for_selector(".notice")
    media = guarded("draft")["media"]
    up = [m for m in media.values() if m.get("alt") == "Test carport photo"]
    check("upload is stored with description and licence", bool(up) and up[0]["licence"] == "own", page.locator(".notice").inner_text())
    check("upload is resized to 1600px wide WebP", bool(up) and up[0].get("w") == 1600 and up[0]["file"].endswith(".webp"), up[0] if up else "")
    page.set_input_files('.upload input[type="file"]', os.path.join(FIX, "not-an-image.jpg"))
    page.fill('.upload input[name="alt"]', "Not really a picture"); page.click('.upload button[type="submit"]'); page.wait_for_selector(".notice-error")
    check("a file that is not a real image is refused", "Upload a JPG" in page.content())
    page.screenshot(path=f"{SHOTS}/admin-media.png", full_page=False)

    # --- choose the uploaded image for a section through the chooser window
    page.goto(BASE + "/admin/pages?kind=project"); page.click("text=Solar Carports >> nth=0"); page.wait_for_selector("[data-section]")
    target = page.locator("[data-section]").nth(page.locator("[data-section]").count() - 2)
    target.locator("[data-picker-open]").click()
    page.wait_for_selector("#media-dialog[open]")
    page.screenshot(path=f"{SHOTS}/admin-picker.png")
    page.click('#media-dialog [data-tile][data-alt="Test carport photo"]')
    page.click('.savebar button[type="submit"]'); page.wait_for_selector(".notice-ok")
    draft = [x for x in guarded("draft")["pages"] if x["slug"] == "carports"][0]
    check("chosen image is saved on the section", any(media.get(s["image"], {}).get("alt") == "Test carport photo" for s in draft["sections"]))

    # --- home page editor
    page.goto(BASE + "/admin/home")
    page.fill('input[name="hero_eyebrow"]', "Solar engineering across the UK and Ireland")
    page.screenshot(path=f"{SHOTS}/admin-home.png", full_page=True)
    page.click('.savebar button[type="submit"]'); page.wait_for_selector(".notice-ok")
    check("home page saves", guarded("draft")["home"]["hero"]["eyebrow"].endswith("Ireland"))
    check("home banner keeps all its slides", len(guarded("draft")["home"]["hero"]["slides"]) == len(guarded("live")["home"]["hero"]["slides"]) >= 6)

    # --- discard brings the draft back to the live version
    page.goto(BASE + "/admin/")
    page.click('form[action="/admin/discard"] button'); page.click('dialog.confirm-dialog .btn-primary'); page.wait_for_selector(".notice-ok")
    check("discard removes unpublished changes", not os.path.exists(f"{DATA}/draft.php") and "Everything is published" in page.content())

    # --- restore the earlier version from history
    page.goto(BASE + "/admin/history")
    check("history lists the replaced version", page.locator(".list-row").count() == 1)
    page.click('.list-row button'); page.click('dialog.confirm-dialog .btn-primary'); page.wait_for_url(BASE + "/admin/")
    restored = [x for x in guarded("draft")["pages"] if x["slug"] == "carports"][0]
    check("restoring loads the old version as a draft", restored["title"] == "Carports")
    page.click('form[action="/admin/discard"] button'); page.click('dialog.confirm-dialog .btn-primary'); page.wait_for_selector(".notice-ok")

    # --- contact form: posts to send_mail.php in the old format, and the inbox gets a copy
    visitor = browser.new_context(viewport={"width": 1366, "height": 900}).new_page()
    vproblems = []
    visitor.on("console", lambda m: vproblems.append(m.text) if m.type == "error" else None)
    visitor.goto(BASE + "/services/epc/")
    visitor.fill('[name="firstName"]', "Jane"); visitor.fill('[name="lastName"]', "O'Neil & Co"); visitor.fill('[name="email"]', "jane@example.com")
    visitor.fill('[name="phone"]', "+44 20 7946 0000"); visitor.fill('[name="message"]', "Quote for a 2MWp carport?\nThanks")
    with visitor.expect_response(lambda r: r.url.endswith("/enquiry")):
        visitor.click('[data-contact-form] button[type="submit"]')
    visitor.wait_for_selector("[data-contact-status]:not([hidden])")
    check("visitor sees the thank-you message", "Thank you" in visitor.locator("[data-contact-status]").inner_text())
    sent = json.loads(open(f"{DATA}/test-mail.log").read().strip().split("\n")[-1])
    check("send_mail.php receives exactly the old five fields", sorted(sent.keys()) == ["email", "firstName", "lastName", "message", "phone"] and sent["lastName"] == "O'Neil & Co" and sent["message"] == "Quote for a 2MWp carport?\nThanks", sent)
    check("no browser errors on the public site", not vproblems, vproblems)
    page.goto(BASE + "/admin/enquiries")
    check("enquiry copy appears in the admin inbox", "Jane O'Neil & Co" in page.locator(".enquiry h2").first.inner_text() and "jane@example.com" in page.content())
    page.screenshot(path=f"{SHOTS}/admin-enquiries.png", full_page=True)

    # --- settings and mobile layout
    page.goto(BASE + "/admin/settings"); page.screenshot(path=f"{SHOTS}/admin-settings.png", full_page=True)
    mobile = browser.new_context(viewport={"width": 390, "height": 800}, storage_state=ctx.storage_state()).new_page()
    mobile.goto(BASE + "/admin/pages?kind=service"); mobile.screenshot(path=f"{SHOTS}/admin-mobile.png", full_page=True)
    mobile.goto(BASE + "/"); mobile.screenshot(path=f"{SHOTS}/public-mobile.png")
    check("no browser errors or blocked scripts in the admin", not problems, problems[:3])

    # --- text typed by an editor can never run as code on the public site
    page.goto(BASE + "/admin/pages?kind=service"); page.click("text=Consulting Services >> nth=0"); page.wait_for_selector("[data-section]")
    page.locator("[data-section]").first.locator('[data-name="heading"]').fill('Design <script>window.hacked=1</script> & "CAD"')
    page.click('.savebar button[type="submit"]'); page.wait_for_selector(".notice-ok")
    page.goto(BASE + "/services/consulting/?preview=1")
    check("typed HTML is shown as text, not run", page.evaluate("window.hacked") is None and "&lt;script&gt;" in page.content())
    page.goto(BASE + "/admin/"); page.click('form[action="/admin/discard"] button'); page.click('dialog.confirm-dialog .btn-primary'); page.wait_for_selector(".notice-ok")

    # --- forms without the security token are refused, even when signed in
    token_less = ctx.request.post(BASE + "/admin/publish", form={"x": "1"})
    check("a request without the form token is refused", token_less.status == 400)
    for private in ["/app/bootstrap.php", "/app/seed/content.json", "/data/live.php", "/.user.ini", "/.htaccess", "/media/.htaccess"]:
        r = ctx.request.get(BASE + private)
        check("private path is not served: " + private, r.status == 404)

    # --- activity log
    page.goto(BASE + "/admin/settings")
    check("activity log records publishing and account creation", "Published the website" in page.content() and "First account created" in page.content())

    # --- changing the password signs out every other browser using the account
    other = browser.new_context(storage_state=ctx.storage_state()).new_page()
    other.goto(BASE + "/admin/"); check("second browser starts signed in", "Dashboard" in other.title())
    NEW_PASSWORD = secrets.token_urlsafe(12)
    page.fill('form[action="/admin/settings/password"] input[name="new_password"]', "tester12345")
    page.fill('form[action="/admin/settings/password"] input[name="current_password"]', PASSWORD)
    page.click('form[action="/admin/settings/password"] button'); page.wait_for_selector(".notice-error")
    check("a password containing the username is refused", "too easy to guess" in page.content())
    page.fill('form[action="/admin/settings/password"] input[name="current_password"]', PASSWORD)
    page.fill('form[action="/admin/settings/password"] input[name="new_password"]', NEW_PASSWORD)
    page.click('form[action="/admin/settings/password"] button'); page.wait_for_selector(".notice-ok")
    PASSWORD = NEW_PASSWORD
    other.goto(BASE + "/admin/")
    check("password change signs out the other browser", other.url.endswith("/admin/login"))

    # --- two-step sign-in with an authenticator code
    import base64, hashlib, hmac, struct, time
    def totp(key, step_offset=0):
        counter = int(time.time()) // 30 + step_offset
        digest = hmac.new(base64.b32decode(key), struct.pack(">Q", counter), hashlib.sha1).digest()
        o = digest[19] & 15
        return f"{(struct.unpack('>I', digest[o:o+4])[0] & 0x7FFFFFFF) % 1000000:06d}"
    page.goto(BASE + "/admin/settings"); page.click('form[action="/admin/settings/two-step"] button:has-text("Set up")')
    key = page.locator("code.key").inner_text().replace(" ", "")
    page.fill('form[action="/admin/settings/two-step"] input[name="code"]', "000000"); page.click('button:has-text("Turn on")'); page.wait_for_selector(".notice-error")
    check("a wrong code does not turn two-step on", "not right" in page.content())
    page.fill('form[action="/admin/settings/two-step"] input[name="code"]', totp(key)); page.click('button:has-text("Turn on")'); page.wait_for_selector(".notice-ok")
    check("two-step sign-in turns on with a valid code", "Two-step sign-in is on" in page.content())
    page.click('form[action="/admin/logout"] button'); page.wait_for_url(BASE + "/admin/login")
    page.fill('input[name="username"]', USER); page.fill('input[name="password"]', PASSWORD); page.click('button[type="submit"]')
    check("password alone is no longer enough", "Enter your code" in page.content())
    page.goto(BASE + "/admin/"); check("still signed out before the code is entered", page.url.endswith("/admin/login"))
    page.fill('input[name="username"]', USER); page.fill('input[name="password"]', PASSWORD); page.click('button[type="submit"]')
    page.fill('input[name="code"]', totp(key)); page.click('button[type="submit"]')
    check("a code that was already used is refused", "not right" in page.content())
    page.fill('input[name="code"]', totp(key, 1)); page.click('button[type="submit"]'); page.wait_for_url(BASE + "/admin/")
    check("password plus a fresh code signs in", "Dashboard" in page.title())
    users_file = open(f"{DATA}/users.php", encoding="utf8").read()
    check("passwords are stored only as salted hashes", PASSWORD not in users_file and '"hash": "$2y$' in users_file)

    # --- sign out really ends the session
    page.goto(BASE + "/admin/"); page.click('form[action="/admin/logout"] button'); page.wait_for_url(BASE + "/admin/login")
    page.goto(BASE + "/admin/settings")
    check("signed-out visitors are sent to sign-in", page.url.endswith("/admin/login"))
    page.fill('input[name="username"]', USER); page.fill('input[name="password"]', "wrong-password-1"); page.click('button[type="submit"]')
    check("wrong password is refused", "not right" in page.content())
    page.screenshot(path=f"{SHOTS}/admin-login.png")
    for _ in range(8):
        page.fill('input[name="username"]', USER); page.fill('input[name="password"]', "wrong-password-1"); page.click('button[type="submit"]')
    check("repeated wrong passwords are locked out", "Too many attempts" in page.content())
    anon_post = browser.new_context().request.post(BASE + "/admin/publish", form={"x": "1"})
    check("signed-out requests cannot publish", anon_post.url.endswith("/admin/login"))
    browser.close()

failed = [n for n, ok in results if not ok]
print(f"\n{len(results) - len(failed)} of {len(results)} checks passed")
sys.exit(1 if failed else 0)
