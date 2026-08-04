import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehostelfinder.settings')
import django
django.setup()
from datetime import date
from hostels.models import User, Hostel, Room, Booking
from hostels.email_utils import send_booking_receipt

user, _ = User.objects.get_or_create(
    email='receipt-test@example.com',
    defaults={'first_name': 'Receipt', 'last_name': 'Test', 'is_email_verified': True}
)
user.set_password('pass1234')
user.save()

hostel, _ = Hostel.objects.get_or_create(
    name='Receipt Hostel',
    defaults={'description': 'Test', 'address': '1 Test', 'city': 'Testville', 'country': 'Uganda'}
)
room, _ = Room.objects.get_or_create(
    hostel=hostel,
    room_number='777',
    defaults={'room_name': 'Test Room', 'room_type': 'Single', 'capacity': 1, 'price_per_semester': 100000, 'status': 'Available', 'is_available': True}
)
booking, _ = Booking.objects.get_or_create(
    hostel=hostel,
    room=room,
    customer=user,
    booking_reference='BK-VERIFY-001',
    defaults={'check_in': date(2026, 8, 1), 'check_out': date(2026, 8, 3), 'students': 1, 'semesters': 2, 'total_price': 200000, 'booking_status': 'Pending', 'payment_status': 'Pending'}
)

send_booking_receipt(booking, None)
print('sent')
