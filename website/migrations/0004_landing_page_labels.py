from django.db import migrations


def editable_labels(apps, schema_editor):
    TextKey = apps.get_model('website', 'TextKey')
    labels = {
        'DISCUSS_PROJECT': 'Discuss a project',
        'CAPABILITY_DESIGN': 'Engineering & design',
        'CAPABILITY_EPC': 'EPC delivery',
        'CAPABILITY_COMMISSIONING': 'Commissioning',
        'CAPABILITY_MAINTENANCE': 'Operations & maintenance',
        'VIDEO_LABEL': 'VARTEC in action',
        'VIEW_PROJECT': 'View project',
    }
    for key, value in labels.items():
        TextKey.objects.get_or_create(key=key, defaults={
            'default_text': value, 'description': 'Landing page label',
        })


class Migration(migrations.Migration):
    dependencies = [('website', '0003_sitesettings_chatbot')]
    operations = [migrations.RunPython(editable_labels, migrations.RunPython.noop)]
