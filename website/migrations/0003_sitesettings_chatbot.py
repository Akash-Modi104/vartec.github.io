from django.db import migrations, models


def add_homepage_guidance(apps, schema_editor):
    TextKey = apps.get_model("website", "TextKey")
    values = {
        "HERO_TITLE": "Solar energy projects, engineered for performance.",
        "HERO_SUMMARY": "From early design and procurement through construction, commissioning and long-term maintenance.",
    }
    for key, value in values.items():
        TextKey.objects.get_or_create(key=key, defaults={"default_text": value, "description": "Homepage hero content"})


class Migration(migrations.Migration):
    dependencies = [("website", "0002_english_only_appearance")]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="chatbot_enabled",
            field=models.BooleanField(default=True, help_text="Show the website help chat in the bottom corner."),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="chatbot_title",
            field=models.CharField(default="VARTEC Assistant", max_length=80),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="chatbot_welcome",
            field=models.CharField(default="Hello. How can we help with your solar energy project?", max_length=240),
        ),
        migrations.RunPython(add_homepage_guidance, migrations.RunPython.noop),
    ]
