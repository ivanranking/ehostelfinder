from django.db import migrations


def clear_hostels(apps, schema_editor):
    pass  # Disabled: no longer clearing hostels on deploy


class Migration(migrations.Migration):
    dependencies = [
        ('hostels', '0005_demo_hostel_seed'),
    ]

    operations = [
        migrations.RunPython(clear_hostels, migrations.RunPython.noop),
    ]
