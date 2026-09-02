from django.core.validators import RegexValidator
from django.db import migrations, models


def keep_english_active(apps, schema_editor):
    Language = apps.get_model("website", "Language")
    Language.objects.exclude(code="en").update(is_active=False, is_default=False)
    Language.objects.filter(code="en").update(is_active=True, is_default=True, sort_order=0)


class Migration(migrations.Migration):
    dependencies = [("website", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="font_family",
            field=models.CharField(
                choices=[
                    ("montserrat", "Montserrat"),
                    ("helvetica", "Helvetica / Segoe UI"),
                    ("arial", "Arial"),
                    ("georgia", "Georgia"),
                ],
                default="montserrat",
                help_text="Typography used across the public website.",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="secondary_colour",
            field=models.CharField(
                default="#080909",
                help_text="Dark logo colour used for headings and panels.",
                max_length=7,
                validators=[RegexValidator("^#[0-9A-Fa-f]{6}$", "Use a six-digit hex colour such as #080909.")],
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="surface_colour",
            field=models.CharField(
                default="#F5F5F2",
                help_text="Light neutral shade used behind content cards.",
                max_length=7,
                validators=[RegexValidator("^#[0-9A-Fa-f]{6}$", "Use a six-digit hex colour such as #F5F5F2.")],
            ),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="primary_colour",
            field=models.CharField(
                default="#FFC107",
                help_text="Primary gold from the VARTEC logo.",
                max_length=7,
                validators=[RegexValidator("^#[0-9A-Fa-f]{6}$", "Use a six-digit hex colour such as #FFC107.")],
            ),
        ),
        migrations.RunPython(keep_english_active, migrations.RunPython.noop),
    ]
