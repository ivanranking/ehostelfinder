from django.db import migrations


def clear_hostels(apps, schema_editor):
    Hostel = apps.get_model('hostels', 'Hostel')
    Hostel.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('hostels', '0005_demo_hostel_seed'),
    ]

    operations = [
        migrations.RunPython(clear_hostels, migrations.RunPython.noop),
    ]
