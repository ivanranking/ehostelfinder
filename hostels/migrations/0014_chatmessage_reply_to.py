from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hostels', '0013_rename_booking_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmessage',
            name='reply_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='replies', to='hostels.chatmessage'),
        ),
    ]
