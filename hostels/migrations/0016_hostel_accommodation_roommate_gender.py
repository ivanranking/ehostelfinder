from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hostels', '0015_add_profile_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='hostel',
            name='accommodation',
            field=models.CharField(
                choices=[('male_only', 'Male only'), ('female_only', 'Female only'), ('mixed', 'Mixed')],
                default='mixed',
                max_length=12,
            ),
        ),
        migrations.AddField(
            model_name='roommaterequest',
            name='own_gender',
            field=models.CharField(
                choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other'), ('unspecified', 'Not specified')],
                default='unspecified',
                max_length=12,
            ),
        ),
        migrations.AlterField(
            model_name='roommaterequest',
            name='preferred_gender',
            field=models.CharField(
                choices=[('any', 'Any'), ('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
                default='any',
                max_length=10,
            ),
        ),
    ]