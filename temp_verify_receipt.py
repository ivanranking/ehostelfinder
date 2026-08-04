import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehostelfinder.settings')
import django
django.setup()
from django.test.utils import override_settings
from django.core import mail
from hostels.models import User, Hostel, Room, Booking
from hostels.email_utils import send_booking_receipt

user = User.objects.create(email='receipt-test@example.com', first_name='Receipt', last_name='Test', is_email_verified=True)
user.set_password('pass1234')
user.save()
hostel = Hostel.objects.create(name='Receipt Hostel', description='Test', address='1 Test', city='Testville', country='Uganda')
room = Room.objects.create(hostel=hostel, room_number='777', room_name='Test Room', room_type='Single', capacity=1, price_per_semester=100000, status='Available', is_available=True)
booking = Booking.objects.create(hostel=hostel, room=room, customer=user, check_in='2026-08-01', check_out='2026-08-03', students=1, semesters=2, total_price=200000, booking_reference='BK-VERIFY-001', booking_status='Pending', payment_status='Pending')
with override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
    send_booking_receipt(booking, None)
    print('mail_count', len(mail.outbox))
    if mail.outbox:
        msg = mail.outbox[0]
        print('subject', msg.subject)
        print('to', msg.to)
        print('body_has_reference', 'BK-VERIFY-001' in msg.body)
