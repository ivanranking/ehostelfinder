from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hostels', '0012_hostel_is_full_total_floors'),
    ]

    operations = [
        migrations.RenameField(
            model_name='room',
            old_name='price_per_night',
            new_name='price_per_semester',
        ),
        migrations.RenameField(
            model_name='booking',
            old_name='guests',
            new_name='students',
        ),
        migrations.RenameField(
            model_name='booking',
            old_name='nights',
            new_name='semesters',
        ),
    ]
