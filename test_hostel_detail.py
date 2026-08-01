import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehostelfinder.settings')
import django
django.setup()
from django.conf import settings
settings.ALLOWED_HOSTS = ['*']

from django.test import Client
from hostels.models import User, Hostel, Room

c = Client()
user = User.objects.get(email='manager@test.com')
c.force_login(user)

hostel = Hostel.objects.get(name='Test Hostel')

# Test hostel detail page for manager
resp = c.get(f'/hostel/{hostel.id}/')
print(f"Hostel detail (manager): {resp.status_code}")
html = resp.content.decode()

# Check for management buttons
print(f"  Has 'Add Room' button: {'Add Room' in html}")
print(f"  Has 'Edit Room' button: {'Edit Room' in html}")
print(f"  Has 'Delete Room' button: {'Delete Room' in html}")
print(f"  Has room-modal-detail: {'room-modal-detail' in html}")
print(f"  Has rooms-data-detail JSON: {'rooms-data-detail' in html}")
print(f"  Has 'Book This Room' (should be hidden for manager): {'Book This Room' in html}")
print(f"  Has 'Manage Hostel': {'Manage Hostel' in html}")

# Check that available rooms are still shown
print(f"  Has 'Available Rooms' section: {'Available Rooms' in html}")
print(f"  Has 'Room 102': {'Room 102' in html}")
print(f"  Has 'Suite 201': {'Suite 201' in html}")

# Test as a customer (non-manager)
from django.contrib.auth.models import AnonymousUser
# Create a customer
customer, created = User.objects.get_or_create(email='customer@test.com',
    defaults={'first_name': 'Test', 'last_name': 'Customer'})
customer.set_password('test123')
customer.save()
from hostels.models import Profile
Profile.objects.get_or_create(user=customer, defaults={'full_name': 'Test Customer', 'email': 'customer@test.com', 'role': 'customer'})

c2 = Client()
c2.force_login(customer)

resp = c2.get(f'/hostel/{hostel.id}/')
print(f"\nHostel detail (customer): {resp.status_code}")
html2 = resp.content.decode()
print(f"  Has 'Add Room' button: {'Add Room' in html2}")
print(f"  Has 'Edit Room' button: {'Edit Room' in html2}")
print(f"  Has 'Delete Room' button: {'Delete Room' in html2}")
print(f"  Has 'Book This Room': {'Book This Room' in html2}")
print(f"  Has 'Manage Hostel': {'Manage Hostel' in html2}")

# Test the API endpoints still work with CSRF
from django.test import Client
c3 = Client(enforce_csrf_checks=False)
c3.force_login(user)

# Test create room via API
import json
resp = c3.post('/manager/rooms/', json.dumps({
    'room_number': '301',
    'room_name': 'Deluxe 301',
    'room_type': 'Double',
    'capacity': 2,
    'available_quantity': 1,
    'price_per_semester': '300',
    'floor': 3,
    'description': 'Deluxe room',
    'wifi': True,
    'air_conditioning': True,
    'private_bathroom': True,
    'balcony': True,
    'television': True,
    'status': 'Available',
    'is_available': True,
}), content_type='application/json')
print(f"\nCreate room via API: {resp.status_code} - {resp.json()}")

# Verify hostel detail shows new room
resp = c.get(f'/hostel/{hostel.id}/')
html = resp.content.decode()
print(f"  New room 'Deluxe 301' on hostel detail: {'Deluxe 301' in html}")
