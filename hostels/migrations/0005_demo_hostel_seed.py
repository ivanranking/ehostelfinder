from django.db import migrations


def remove_existing_hostels_and_seed_demo(apps, schema_editor):
    Hostel = apps.get_model('hostels', 'Hostel')
    Hostel.objects.all().delete()

    Hostel.objects.create(
        name='Demo Hostel',
        description='A demo hostel left for testing. You can replace this listing with your own later.',
        address='123 Demo Street',
        city='Kampala',
        country='Uganda',
        university='Makerere University',
        distance='2 km from campus',
        price=150000,
        rating=4.50,
        amenities=['Wi-Fi', 'Breakfast', '24/7 Security'],
        contact='+256700000000',
        available=True,
        image_url='https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=1200&q=80',
        phone='+256700000000',
        email='demo@ehostelfinder.com',
        latitude=0.347596,
        longitude=32.582520,
        check_in_time='14:00:00',
        check_out_time='11:00:00',
        review_count=1,
    )


class Migration(migrations.Migration):
    dependencies = [
        ('hostels', '0004_passwordresettoken'),
    ]

    operations = [
        migrations.RunPython(remove_existing_hostels_and_seed_demo, migrations.RunPython.noop),
    ]
