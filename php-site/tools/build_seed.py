"""Build the PHP site's starting content from the approved redesign.

Reads the rendered pages of the Django redesign (the version the client approved on the
dev server), extracts the wording and structure into app/seed/content.json and copies the
images into public/media/ under clean, hyphenated names.

Usage: python build_seed.py <dir of crawled html> <src/assets dir> <php-site/public dir>
"""
import hashlib, html, json, os, re, shutil, sys, unicodedata
from bs4 import BeautifulSoup
from PIL import Image

PAGES, ASSETS, PUBLIC = sys.argv[1:4]

# Reverse-image-search results from the 15 Nov 2026 audit: legacy path -> (licence, source).
UNLICENSED = {
    "project/EV charging/solar carport charging station.webp": "https://fastlane.gm.com/2014/12/03/department-energy-recognizes-gm-workplace-charging/",
    "project/EV charging/solar carport.webp": "https://i.insider.com/61031873aedf2100190f0d42",
    "image/hero2-min.webp": "https://www.shutterstock.com/image-photo/man-mows-grass-near-solar-panels-2444567545",
    "image/hero4-min.webp": "https://www.bigstockphoto.com/image-468595951/stock-photo-engineer-working-setup-floating-solar-panels-or-solar-cell-platform-system-on-the-lake-engineer-or",
    "image/hero5-min.webp": "https://www.shutterstock.com/image-photo/providing-surveillance-monitoring-solar-energy-sitesecured-2361622415",
    "image/hero6-min.webp": "https://www.shutterstock.com/image-photo/electric-vehicles-charging-station-on-background-1966719229",
    "project/Floating solar/15MWp floating solar.webp": "https://www.shutterstock.com/image-photo/largest-floating-solar-park-farm-europe-1869869446",
    "project/Battery storage/battery storage.webp": "https://www.alamy.com/batteries-for-energy-storage-supplying-and-stabilizing-a-larger-amount-of-renewable-energy-to-the-electric-grid-flevopolder-the-netherlands-image596545702.html",
    "project/Battery storage/Solar with storage.webp": "https://www.alamy.com/detailed-view-of-the-battery-energy-storage-located-in-an-open-industrial-container-on-a-lush-lawn-with-a-photovoltaic-power-plant-in-the-background-image560664409.html",
    "project/Carports/solar carport with ev charging.webp": "https://www.alamy.com/aerial-view-of-solar-panels-installed-as-shade-roof-over-parking-lot-with-parked-cars-for-effective-generation-of-clean-electricity-photovoltaic-image469999282.html",
    "project/Security systems/security fencing.webp": "https://www.alamy.com/power-station-with-solar-panels-in-a-field-behind-a-barbed-wire-fence-lighting-and-video-surveillance-equipment-on-a-bright-sunny-day-image566946847.html",
    "image/services/e&m/engineering procurement and construction (EPC).webp": "https://www.shutterstock.com/image-photo/architect-team-working-blueprints-sketching-construction-2374386943",
    "image/services/e&m/Engineering.webp": "https://www.alamy.com/design-or-project-concept-of-an-ecological-house-folding-ruler-in-the-shape-of-a-house-on-a-wheat-field-with-a-green-tree-clear-blue-sky-and-sunbea-image557502320.html",
    "image/services/e&m/procurement.webp": "https://www.shutterstock.com/image-photo/man-working-on-virtual-touch-screen-2332556547",
    "image/services/Consulting services/design CAD.webp": "https://www.alamy.com/over-the-shoulder-shot-of-engineer-working-with-cad-software-on-desktop-computer-screen-shows-technical-drafts-and-drawings-in-the-background-image376926136.html",
    "image/services/Consulting services/health and safety.webp": "https://www.shutterstock.com/image-photo/clean-energy-solar-cell-factory-concept-1122790478",
    "image/services/Operation and Maintenance/electrical testing.webp": "https://www.alamy.com/workers-use-multimeter-to-measure-the-voltage-of-electrical-wires-produced-from-solar-energy-for-confirm-to-systems-working-normal-image383625990.html",
}
UNKNOWN = {
    "image/services/Operation and Maintenance/solar panel testing.webp", "image/services/Operation and Maintenance/OM services.webp",
    "image/services/Operation and Maintenance/robot panel cleaning.webp", "image/services/Operation and Maintenance/panel cleaning.webp",
}
# The same photo saved under two names: audit status follows the first.
SAME_AS = {
    "image/services/Operation and Maintenance/grass cutting.webp": "image/hero2-min.webp",
    "image/services/Operation and Maintenance/operation and maintenance floating solar.webp": "image/hero4-min.webp",
    "project/Floating solar/operation and maintenance floating solar.webp": "image/hero4-min.webp",
    "project/Security systems/CCTV camera.webp": "image/hero5-min.webp",
}
NICE_NAMES = {"image/hero1-min.webp": "battery-storage-site", "image/hero2-min.webp": "grass-cutting-solar-park", "image/hero4-min.webp": "engineers-floating-solar",
              "image/hero5-min.webp": "cctv-camera-solar-park", "image/hero6-min.webp": "electric-vans-charging", "image/hero7-min.webp": "solar-carport-car-park",
              "project/Carports/DJI_0062.webp": "solar-carport-aerial", "project/Carports/IMG-20211013-WA0001.webp": "solar-carport-ground-view",
              "project/Carports/IMG-20211013-WA0004 - copia.webp": "solar-carport-wide-view", "project/Battery storage/Energy-storage-on-page-1-scaled.webp": "battery-storage-containers",
              "project/solar parks/potash_solar_farm.webp": "solar-farm-beachampton"}

def slug(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

def clean(node):
    return re.sub(r"\s+", " ", node.get_text(" ", strip=True)).strip() if node else ""

def legacy(url):
    """/static/project/X/name.<12 hex>.webp -> project/X/name.webp"""
    path = html.unescape(url).split("/static/", 1)[1]
    return re.sub(r"\.[0-9a-f]{12}(\.[A-Za-z0-9]+)$", r"\1", path)

media, by_hash, skipped = {}, {}, []

def media_id(url, alt=""):
    if not url:
        return ""
    rel = legacy(url)
    src = os.path.join(ASSETS, rel)
    if not os.path.exists(src):
        # Removed from the project since the pages were rendered (e.g. the photo in Copytrack case 83734B).
        skipped.append(rel)
        return ""
    digest = hashlib.sha256(open(src, "rb").read()).hexdigest()
    if digest in by_hash:
        return by_hash[digest]
    ext = os.path.splitext(rel)[1].lower()
    name = NICE_NAMES.get(rel) or slug(os.path.splitext(os.path.basename(rel))[0])
    mid = name
    while mid in media:
        mid += "-2"
    os.makedirs(os.path.join(PUBLIC, "media"), exist_ok=True)
    shutil.copyfile(src, os.path.join(PUBLIC, "media", mid + ext))
    entry = {"file": mid + ext, "kind": "video" if ext == ".mp4" else "image", "alt": alt or mid.replace("-", " ").capitalize(), "source": "", "licence": "own"}
    if entry["kind"] == "image":
        with Image.open(src) as im:
            entry["w"], entry["h"] = im.size
    audit = SAME_AS.get(rel, rel)
    if audit in UNLICENSED:
        entry.update(licence="unlicensed", source=UNLICENSED[audit])
    elif audit in UNKNOWN:
        entry.update(licence="unknown")
    media[mid] = entry
    by_hash[digest] = mid
    return mid

def soup(name):
    return BeautifulSoup(open(os.path.join(PAGES, name), encoding="utf8").read(), "html.parser")

home = soup("_.html")
hero = home.select_one("section.hero")
about = home.select_one("#about")
feature = home.select_one("section.feature-section")
contact = home.select_one("#contact")
footer = home.select_one("footer.site-footer")
dl = {clean(d.dt): d.dd for d in contact.select("dl > div")}
hours = [s.strip() for s in dl["Office hours"].get_text("\n", strip=True).split("\n")]
copy_ps = [clean(p) for p in contact.select(".contact-copy > p") if "eyebrow" not in (p.get("class") or [])]

content = {
    "settings": {
        "brand_name": "VARTEC",
        "site_url": "https://vartec.global",
        "contact_email": clean(dl["Email"]),
        "phone": clean(dl["Phone"]),
        "office_hours_weekdays": hours[0],
        "office_hours_weekend": hours[1] if len(hours) > 1 else "",
        "footer_about": clean(footer.select_one(".footer-grid > div > p")),
        "footer_copyright": re.sub(r"\b20\d\d\b", "{year}", clean(footer.select_one(".footer-bottom"))),
        "seo_title": clean(home.title),
        "seo_description": home.select_one('meta[name="description"]')["content"],
        "logo": media_id(home.select_one("a.brand img")["src"], "VARTEC"),
        "chat_enabled": bool(home.select_one("[data-chatbot]")),
        "chat_title": clean(home.select_one(".chatbot-panel header strong")),
        "chat_welcome": clean(home.select_one(".chatbot-message.bot")),
    },
    "home": {
        "hero": {
            "eyebrow": clean(hero.select_one(".eyebrow")), "title": clean(hero.h1), "summary": clean(hero.select_one(".hero-content > p:not(.eyebrow)")),
            "points": [clean(s) for s in hero.select(".hero-proof strong")],
            "slides": [m for m in (media_id(s["data-src"]) for s in hero.select(".hero-slides span")) if m],
        },
        "about": {
            "heading": clean(about.h2), "paragraphs": [clean(p) for p in about.select(".section-copy > p") if "eyebrow" not in (p.get("class") or [])],
            "video": media_id(about.select_one("video source")["src"]) if about.select_one("video source") else "",
            "video_label": clean(about.select_one(".video-label")),
        },
        "capabilities": {
            "eyebrow": clean(feature.select_one(".eyebrow")), "heading": clean(feature.h2), "intro": clean(feature.select_one(".section-heading > p:not(.eyebrow)")),
            "cards": [{"title": clean(c.h3), "body": clean(c.p)} for c in feature.select(".feature-card")],
        },
        "services_heading": clean(home.select_one("#services h2")), "projects_heading": clean(home.select_one("#projects h2")),
        "contact": {"heading": clean(contact.select_one(".contact-copy h2")), "text": copy_ps, "form_heading": clean(contact.select_one(".contact-panel h2"))},
    },
    "pages": [],
}
content["home"]["about"]["poster"] = content["home"]["hero"]["slides"][0] if content["home"]["hero"]["slides"] else ""

cards = {a["href"]: a for a in home.select("#services a.media-card, #projects a.project-card")}
order = [a["href"] for a in home.select(".primary-nav .nav-dropdown a")]
for href in order:
    kind, page_slug = ("service" if href.startswith("/services/") else "project"), href.strip("/").split("/")[1]
    page = soup(href.replace("/", "_") + ".html")
    hero_box = page.select_one("section.page-hero")
    card_img = cards[href].img["src"] if href in cards and cards[href].img else ""
    title = clean(hero_box.h1)
    entry = {
        "id": f"{kind}-{page_slug}", "kind": kind, "slug": page_slug, "title": title,
        "intro": clean(hero_box.select_one(".shell > p:not(.eyebrow)")),
        "seo_title": "", "seo_description": "",
        "card_image": media_id(card_img, title), "visible": True, "sections": [],
    }
    seo_title, seo_desc = clean(page.title), page.select_one('meta[name="description"]')["content"]
    if seo_title != f"{title} | VARTEC":
        entry["seo_title"] = seo_title
    if seo_desc != entry["intro"]:
        entry["seo_description"] = seo_desc
    for n, sec in enumerate(page.select("section.detail-section")):
        copy = sec.select_one(".detail-copy")
        heading = clean(copy.find("h2", recursive=False))
        img = sec.select_one(".detail-media img")
        items = []
        box = copy.select_one(".section-items")
        for child in (box.find_all(recursive=False) if box else []):
            classes = child.get("class") or []
            kind_ = "subheading" if child.name == "h3" else ("numbered" if "numbered" in classes else "bullet" if "list-item" in classes else "paragraph")
            items.append({"type": kind_, "text": clean(child)})
        entry["sections"].append({"id": f"s{n + 1}", "heading": heading, "body": clean(copy.find("p", recursive=False)),
                                  "image": media_id(img["src"], img.get("alt", "")) if img else "", "items": items})
    content["pages"].append(entry)

content["media"] = media
out = os.path.join(PUBLIC, "app", "seed", "content.json")
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump(content, open(out, "w", encoding="utf8"), indent=1, ensure_ascii=False)
by_licence = {}
for m in media.values():
    by_licence[m["licence"]] = by_licence.get(m["licence"], 0) + 1
print("skipped (file no longer in project):", sorted(set(skipped)))
print("pages", len(content["pages"]), "| sections", sum(len(p["sections"]) for p in content["pages"]), "| media", len(media), by_licence)
