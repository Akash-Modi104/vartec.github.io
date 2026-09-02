import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from website.models import (
    HeroSlide,
    HomeBlock,
    HomeFeature,
    Language,
    MediaAsset,
    Page,
    PageSection,
    SectionItem,
    SiteSettings,
    TextKey,
    TextTranslation,
)


EXTRA_TEXT = {
    "en": {
        "HERO_EYEBROW": "Solar engineering across the UK and Europe",
        "LIFECYCLE_EYEBROW": "VARTEC capabilities",
        "LIFECYCLE_TITLE": "From design through operation and maintenance",
        "LIFECYCLE_DESC": "A clear view of the services already available from VARTEC across the solar project lifecycle.",
        "LIFECYCLE_ENGINEERING_TITLE": "Engineering and detailed design",
        "LIFECYCLE_ENGINEERING_BODY": "Detailed design, calculations, engineering and project planning for solar PV and battery storage systems.",
        "LIFECYCLE_CONSTRUCTION_TITLE": "Procurement and construction",
        "LIFECYCLE_CONSTRUCTION_BODY": "Component procurement, construction management and turnkey EPC delivery.",
        "LIFECYCLE_COMMISSIONING_TITLE": "Commissioning and quality control",
        "LIFECYCLE_COMMISSIONING_BODY": "Plant commissioning, inspections, compliance support and quality control.",
        "LIFECYCLE_OM_TITLE": "Operations and maintenance",
        "LIFECYCLE_OM_BODY": "Monitoring, reporting, diagnostics, testing, cleaning and planned site maintenance.",
        "SELECTED_PROJECTS": "Selected renewable energy projects",
        "EXPLORE_SERVICE": "Explore service",
        "SKIP_TO_CONTENT": "Skip to content",
        "MENU": "Menu",
        "CONTACT_FORM_ERROR": "Please review the highlighted fields.",
        "CONTACT_SUCCESS": "Thank you. Your message has been received.",
        "CONTENT_ADMIN_HELP": "Content for this page can be added from the website admin.",
    },
    "nl": {
        "HERO_EYEBROW": "Zonne-energie engineering in het Verenigd Koninkrijk en Europa",
        "LIFECYCLE_EYEBROW": "VARTEC-diensten",
        "LIFECYCLE_TITLE": "Van ontwerp tot beheer en onderhoud",
        "LIFECYCLE_DESC": "Een helder overzicht van de VARTEC-diensten gedurende de volledige levenscyclus van een zonneproject.",
        "LIFECYCLE_ENGINEERING_TITLE": "Engineering en gedetailleerd ontwerp",
        "LIFECYCLE_ENGINEERING_BODY": "Gedetailleerd ontwerp, berekeningen, engineering en projectplanning voor zonne-PV- en batterijopslagsystemen.",
        "LIFECYCLE_CONSTRUCTION_TITLE": "Inkoop en bouw",
        "LIFECYCLE_CONSTRUCTION_BODY": "Inkoop van componenten, bouwmanagement en turn-key EPC-realisatie.",
        "LIFECYCLE_COMMISSIONING_TITLE": "Inbedrijfstelling en kwaliteitscontrole",
        "LIFECYCLE_COMMISSIONING_BODY": "Inbedrijfstelling, inspecties, ondersteuning bij naleving en kwaliteitscontrole.",
        "LIFECYCLE_OM_TITLE": "Beheer en onderhoud",
        "LIFECYCLE_OM_BODY": "Monitoring, rapportage, diagnose, testen, reiniging en gepland terreinonderhoud.",
        "SELECTED_PROJECTS": "Geselecteerde duurzame-energieprojecten",
        "EXPLORE_SERVICE": "Bekijk dienst",
        "SKIP_TO_CONTENT": "Ga naar de inhoud",
        "MENU": "Menu",
        "CONTACT_FORM_ERROR": "Controleer de gemarkeerde velden.",
        "CONTACT_SUCCESS": "Bedankt. Uw bericht is ontvangen.",
        "CONTENT_ADMIN_HELP": "Inhoud voor deze pagina kan via het websitebeheer worden toegevoegd.",
    },
}


class Command(BaseCommand):
    help = "Seed VARTEC's existing English content, media, services and projects into the CMS."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Replace sections on the seeded VARTEC pages.")
        parser.add_argument("--if-empty", action="store_true", help="Seed only when the CMS has no pages; safe for recurring deploys.")

    def handle(self, *args, **options):
        force = options["force"]
        if options["if_empty"] and Page.objects.exists():
            self.stdout.write("CMS already contains pages; seed skipped.")
            return
        content = self._load_translations()
        languages = self._seed_languages()
        keys = self._seed_text(content, languages)
        assets = self._seed_media(keys)
        self._seed_settings()
        self._seed_hero(keys, assets)
        self._seed_home_blocks(keys)
        self._seed_pages(keys, assets, force)
        self.stdout.write(self.style.SUCCESS("VARTEC CMS content and media are ready."))

    def _load_translations(self):
        output = {}
        for code in ("en",):
            path = settings.BASE_DIR / "src" / "assets" / "i18n" / f"{code}.json"
            output[code] = json.loads(path.read_text(encoding="utf-8"))
            output[code].update(EXTRA_TEXT[code])
        return output

    def _seed_languages(self):
        Language.objects.exclude(code="en").update(is_active=False, is_default=False)
        definitions = {
            "en": {"name": "English", "native_name": "English", "is_default": True, "sort_order": 0, "legacy_flag_path": "image/language/english.png"},
        }
        return {code: Language.objects.update_or_create(code=code, defaults={**values, "is_active": True})[0] for code, values in definitions.items()}

    def _seed_text(self, content, languages):
        keys = {}
        for key, default in content["en"].items():
            item, _ = TextKey.objects.update_or_create(key=key, defaults={"default_text": default})
            keys[key] = item
            for code, language in languages.items():
                TextTranslation.objects.update_or_create(text_key=item, language=language, defaults={"value": content[code].get(key, default)})
        return keys

    def _seed_media(self, keys):
        root = settings.BASE_DIR / "src" / "assets"
        assets = {}
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix.lower() in {".json", ".gitkeep"}:
                continue
            legacy = path.relative_to(root).as_posix()
            kind = MediaAsset.VIDEO if path.suffix.lower() in {".mp4", ".webm"} else MediaAsset.IMAGE
            title = path.stem.replace("_", " ").replace("-", " ").strip().title()
            asset, _ = MediaAsset.objects.get_or_create(legacy_path=legacy, defaults={"title": title, "kind": kind, "is_active": True})
            assets[legacy] = asset
        return assets

    def _seed_settings(self):
        settings_obj = SiteSettings.load()
        settings_obj.brand_name = "VARTEC"
        settings_obj.legacy_logo_path = "image/logo.png"
        settings_obj.legacy_video_path = "video/finalmerge.mp4"
        settings_obj.save()

    def _seed_hero(self, keys, assets):
        for index in range(1, 8):
            path = f"image/hero{index}-min.webp"
            HeroSlide.objects.update_or_create(
                title=f"VARTEC hero {index}",
                defaults={"media": assets.get(path), "legacy_image_path": path, "alt_text_key": keys.get("VARTEC_DESC"), "sort_order": index, "is_active": True},
            )

    def _seed_home_blocks(self, keys):
        block, _ = HomeBlock.objects.update_or_create(
            admin_name="Existing VARTEC capabilities",
            defaults={"title_key": keys["LIFECYCLE_TITLE"], "intro_key": keys["LIFECYCLE_DESC"], "background": HomeBlock.LIGHT, "sort_order": 10, "is_active": True},
        )
        definitions = [
            ("LIFECYCLE_ENGINEERING_TITLE", "LIFECYCLE_ENGINEERING_BODY"),
            ("LIFECYCLE_CONSTRUCTION_TITLE", "LIFECYCLE_CONSTRUCTION_BODY"),
            ("LIFECYCLE_COMMISSIONING_TITLE", "LIFECYCLE_COMMISSIONING_BODY"),
            ("LIFECYCLE_OM_TITLE", "LIFECYCLE_OM_BODY"),
        ]
        for order, (title, body) in enumerate(definitions):
            HomeFeature.objects.update_or_create(block=block, title_key=keys[title], defaults={"body_key": keys[body], "sort_order": order, "is_active": True})

    def _seed_pages(self, keys, assets, force):
        pages = [
            (Page.SERVICE, "epc", "EPC_TITLE", "EPC_DESCRIPTION1", "image/services/e&m/engineering procurement and construction (EPC).webp", [
                ("EPC delivery", "EPC_IMAGE", "EPC_DESCRIPTION2", "image/services/e&m/engineering procurement and construction (EPC).webp"),
                ("Engineering", "ENGINEERING", None, "image/services/e&m/Engineering.webp"),
                ("Procurement", "PROCUREMENT", None, "image/services/e&m/procurement.webp"),
            ]),
            (Page.SERVICE, "consulting", "CONSULTING_SERVICES", "CONSULTING_SERVICES_DESCRIPTION", "image/services/Consulting services/design CAD.webp", [
                ("Design CAD", "DESIGN_CAD", "CONSULTING_SERVICES_DESCRIPTION", "image/services/Consulting services/design CAD.webp"),
                ("Health and safety", "HEALTH_AND_SAFETY", None, "image/services/Consulting services/health and safety.webp"),
            ]),
            (Page.SERVICE, "operation-maintenance", "OPERATION_MAINTENANCE_TITLE", "OPERATION_MAINTENANCE_DESC1", "image/services/Operation and Maintenance/OM services.webp", [
                ("Operations", "OPERATIONS", "OPERATION_MAINTENANCE_DESC2", "image/services/Operation and Maintenance/operation and maintenance floating solar.webp"),
                ("Maintenance", "MAINTENANCE", None, "image/services/Operation and Maintenance/grass cutting.webp"),
                ("Electrical testing", "ELECTRICAL_TESTING", None, "image/services/Operation and Maintenance/electrical testing.webp"),
                ("Panel cleaning", "PANEL_CLEANING", None, "image/services/Operation and Maintenance/panel cleaning.webp"),
                ("Robot panel cleaning", "ROBOT_PANEL_CLEANING", None, "image/services/Operation and Maintenance/robot panel cleaning.webp"),
                ("Solar panel testing", "SOLAR_PANEL_TESTING", None, "image/services/Operation and Maintenance/solar panel testing.webp"),
            ]),
            (Page.PROJECT, "battery-storage", "WELCOME_TITLE", "WELCOME_DESCRIPTION", "project/Battery storage/Energy-storage-on-page-1-scaled.webp", [
                ("Battery project 1", "PROJECT_1_TITLE", None, "project/Battery storage/Energy-storage-on-page-1-scaled.webp"),
                ("Battery project 2", "PROJECT_2_TITLE", None, "project/Battery storage/battery storage.webp"),
                ("Battery project 3", "PROJECT_3_TITLE", None, "project/Battery storage/Solar with storage.webp"),
                ("Battery project 4", "PROJECT_4_TITLE", None, "project/Battery storage/battery storage.webp"),
            ]),
            (Page.PROJECT, "carports", "WELCOME_CARPORTS_TITLE", "WELCOME_CARPORTS_DESCRIPTION", "project/Carports/solar carport with ev charging.webp", [
                ("Carport 1", "CARPORTS_PROJECT_1_TITLE", None, "project/Carports/DJI_0062.webp"),
                ("Carport 2", "CARPORTS_PROJECT_2_TITLE", None, "project/Carports/IMG-20211013-WA0001.webp"),
                ("Carport 3", "CARPORTS_PROJECT_3_TITLE", None, "project/Carports/IMG-20211013-WA0004 - copia.webp"),
                ("Carport 4", "CARPORTS_PROJECT_4_TITLE", None, "project/Carports/solar carport with ev charging.webp"),
            ]),
            (Page.PROJECT, "ev-charging", "EV_CHARGING_TITLE", "EV_CHARGING_DESCRIPTION", "project/EV charging/solar carport charging station.webp", [
                ("EV charging 1", "EV_PROJECT_1_TITLE", None, "project/EV charging/solar carport charging station.webp"),
                ("EV charging 2", "EV_PROJECT_2_TITLE", None, "project/EV charging/solar carport.webp"),
                ("EV charging 3", "EV_PROJECT_3_TITLE", None, "project/EV charging/solar carport.webp"),
            ]),
            (Page.PROJECT, "floating-solar", "WELCOME_FLOATING_SOLAR_TITLE", "WELCOME_FLOATING_SOLAR_DESCRIPTION", "project/Floating solar/15MWp floating solar.webp", [
                ("Floating solar 1", "FLOATING_SOLAR_PROJECT_1_TITLE", None, "project/Floating solar/15MWp floating solar.webp"),
                ("Floating solar 2", "FLOATING_SOLAR_PROJECT_2_TITLE", None, "project/Floating solar/floating solar 2.webp"),
                ("Floating solar 3", "FLOATING_SOLAR_PROJECT_3_TITLE", None, "project/Floating solar/operation and maintenance floating solar.webp"),
            ]),
            (Page.PROJECT, "security-systems", "WELCOME_SECURITY_SYSTEMS_TITLE", "WELCOME_SECURITY_SYSTEMS_DESCRIPTION", "project/Security systems/radar PTZ camera unit.webp", [
                ("Security 1", "SECURITY_SYSTEMS_PROJECT_1_TITLE", None, "project/Security systems/radar PTZ camera unit.webp"),
                ("Security 2", "SECURITY_SYSTEMS_PROJECT_2_TITLE", None, "project/Security systems/security fencing.webp"),
                ("Security 3", "SECURITY_SYSTEMS_PROJECT_3_TITLE", None, "project/Security systems/CCTV camera.webp"),
            ]),
            (Page.PROJECT, "solar-parks", "WELCOME_SOLAR_PARKS_TITLE", "WELCOME_SOLAR_PARKS_DESCRIPTION", "project/solar parks/potash_solar_farm.webp", [
                ("Beachampton", "SOLAR_PARKS_PROJECT_0_TITLE", "SOLAR_PARKS_PROJECT_0_DESCRIPTION", "project/solar parks/potash_solar_farm.webp"),
                ("Emmen", "SOLAR_PARKS_PROJECT_1_TITLE", "SOLAR_PARKS_PROJECT_1_DESCRIPTION", "project/solar parks/Solar park Emmen.webp"),
                ("Nieuwendijk", "SOLAR_PARKS_PROJECT_2_TITLE", "SOLAR_PARKS_PROJECT_2_DESCRIPTION", "project/solar parks/Solar park Nieuwendijk.webp"),
                ("Vlaamseweg", "SOLAR_PARKS_PROJECT_3_TITLE", "SOLAR_PARKS_PROJECT_3_DESCRIPTION", "project/solar parks/Solarpark Vlaamseweg_The Netherlands.webp"),
            ]),
        ]
        for order, (kind, slug, title_key, intro_key, card_path, sections) in enumerate(pages):
            page, created = Page.objects.update_or_create(
                kind=kind,
                slug=slug,
                defaults={"title_key": keys[title_key], "intro_key": keys.get(intro_key), "card_media": assets.get(card_path), "legacy_card_image_path": card_path, "sort_order": order, "is_active": True},
            )
            if force:
                page.sections.all().delete()
            if created or force or not page.sections.exists():
                for section_order, (admin_name, section_title, body, image_path) in enumerate(sections):
                    section = PageSection.objects.create(
                        page=page,
                        admin_name=admin_name,
                        title_key=keys.get(section_title),
                        body_key=keys.get(body) if body else None,
                        media=assets.get(image_path),
                        legacy_image_path=image_path,
                        layout=PageSection.TEXT_LEFT if section_order % 2 == 0 else PageSection.TEXT_RIGHT,
                        background=PageSection.WHITE if section_order % 2 == 0 else PageSection.GOLD,
                        sort_order=section_order,
                    )
                    if slug == "operation-maintenance" and admin_name == "Operations":
                        self._add_items(section, keys, ["REMOTE_MONITORING", "TASK_MANAGEMENT", "REMOTE_PLANT_CONTROL", "SITE_PERFORMANCE_REPORTING", "TREND_ANALYSIS", "PANEL_CLEANING_TIMETABLE"])
                    if slug == "operation-maintenance" and admin_name == "Maintenance":
                        self._add_items(section, keys, ["FIXED_PRICE_PACKAGES", "INSPECTIONS_MAINTENANCE", "INVERTERS", "TRANSFORMERS", "SWITCHGEAR", "SENSORS", "STRUCTURE", "MODULES", "CABLING", "THERMAL_IMAGING", "OUTAGE_DIAGNOSTICS", "SITE_MAINTENANCE"])
                    if slug == "consulting" and admin_name == "Design CAD":
                        self._add_items(section, keys, ["CONSULTING_DETAILED_DESIGNS", "CONSULTING_PROJECT_MANAGEMENT", "CONSULTING_HEALTH_SAFETY", "CONSULTING_CONSTRUCTION_MANAGEMENT"])

    def _add_items(self, section, keys, names):
        for order, name in enumerate(names):
            SectionItem.objects.create(section=section, text_key=keys[name], item_type=SectionItem.BULLET, sort_order=order)
