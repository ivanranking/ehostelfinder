# Generated migration for Room.is_available field

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('hostels', '0006_clear_uploaded_hostels'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='is_available',
            field=models.BooleanField(default=True),
        ),
    ]