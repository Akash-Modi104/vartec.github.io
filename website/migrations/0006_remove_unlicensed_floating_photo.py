from django.db import migrations

# Stock photo of a floating solar array in a harbour (rights holder: YayImages).
# Flagged in Copytrack case 83734B on 15 November 2026 and removed from the site.
REMOVED_PATHS = (
    "image/hero3-min.webp",
    "project/Floating solar/floating solar 2.webp",
)


def remove_photo(apps, schema_editor):
    HeroSlide = apps.get_model("website", "HeroSlide")
    MediaAsset = apps.get_model("website", "MediaAsset")
    Page = apps.get_model("website", "Page")
    PageSection = apps.get_model("website", "PageSection")

    # A banner slide exists only to show its image, so the slide goes with it.
    HeroSlide.objects.filter(legacy_image_path__in=REMOVED_PATHS).delete()
    HeroSlide.objects.filter(media__legacy_path__in=REMOVED_PATHS).delete()
    # Sections and page cards keep their wording; only the picture is detached.
    PageSection.objects.filter(legacy_image_path__in=REMOVED_PATHS).update(legacy_image_path="")
    PageSection.objects.filter(media__legacy_path__in=REMOVED_PATHS).update(media=None)
    Page.objects.filter(legacy_card_image_path__in=REMOVED_PATHS).update(legacy_card_image_path="")
    Page.objects.filter(card_media__legacy_path__in=REMOVED_PATHS).update(card_media=None)
    MediaAsset.objects.filter(legacy_path__in=REMOVED_PATHS).delete()


class Migration(migrations.Migration):
    dependencies = [("website", "0005_logo_gold_theme")]
    operations = [migrations.RunPython(remove_photo, migrations.RunPython.noop)]
