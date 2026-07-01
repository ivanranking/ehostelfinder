from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Hostel, Booking, Message
import json

User = get_user_model()


class BaseTestCase(TestCase):
    """Base test case with common setup"""
    
    def setUp(self):
        self.client = Client()
        # Create a test user
        import uuid
        self.user = User(
            id=str(uuid.uuid4()),
            email='testuser@example.com',
            first_name='Test',
            last_name='User'
        )
        self.user.set_password('testpass123')
        self.user.save()
        # Create a hostel
        self.hostel = Hostel.objects.create(
            name='Test Hostel',
            description='A test hostel for testing purposes',
            address='123 Test Street',
            city='Kampala',
            country='Uganda',
            phone='+256700123456',
            email='test@example.com',
            check_in_time='14:00:00',
            check_out_time='11:00:00'
        )
        # Create a profile for the user
        from .models import Profile
        self.profile = Profile.objects.create(
            user=self.user,
            full_name='Test User',
            email='testuser@example.com',
            role='customer'
        )


class HomeViewTests(BaseTestCase):
    """Tests for the home page"""
    
    def test_home_page_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
    
    def test_home_page_has_hostels(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Test Hostel')
    
    def test_home_page_city_filter(self):
        response = self.client.get(reverse('home'), {'city': self.hostel.city})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Hostel')
    
    def test_home_page_country_filter(self):
        response = self.client.get(reverse('home'), {'country': self.hostel.country})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Hostel')


class UniversitiesViewTests(BaseTestCase):
    """Tests for the universities page"""
    
    def test_universities_page_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
    
    def test_universities_lists_cities(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Kampala')


class HostelDetailViewTests(BaseTestCase):
    """Tests for the hostel detail page"""
    
    def test_hostel_detail_page_loads(self):
        response = self.client.get(reverse('hostel_detail', args=[self.hostel.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hostel_detail.html')
    
    def test_hostel_detail_displays_info(self):
        response = self.client.get(reverse('hostel_detail', args=[self.hostel.id]))
        self.assertContains(response, 'Test Hostel')
        self.assertContains(response, 'A test hostel for testing purposes')
    
    def test_hostel_detail_404(self):
        response = self.client.get(reverse('hostel_detail', args=[999]))
        self.assertEqual(response.status_code, 404)


class HowItWorksViewTests(BaseTestCase):
    """Tests for the how it works page"""
    
    def test_how_it_works_page_loads(self):
        response = self.client.get(reverse('how_it_works'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'how_it_works.html')
    
    def test_how_it_works_has_steps(self):
        response = self.client.get(reverse('how_it_works'))
        self.assertContains(response, 'Choose Your University')
        self.assertContains(response, 'Browse Available Hostels')
        self.assertContains(response, 'Contact the Owner')
        self.assertContains(response, 'Book Your Stay')


class ContactViewTests(BaseTestCase):
    """Tests for the contact page"""
    
    def test_contact_page_loads(self):
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact.html')
    
    def test_contact_page_has_form(self):
        response = self.client.get(reverse('contact'))
        self.assertContains(response, 'Send us a message')


class LegalPagesTests(BaseTestCase):
    """Tests for legal pages"""
    
    def test_privacy_policy_page_loads(self):
        response = self.client.get(reverse('privacy_policy'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'privacy_policy.html')
    
    def test_terms_of_use_page_loads(self):
        response = self.client.get(reverse('terms_of_use'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'terms_of_use.html')
    
    def test_cookie_policy_page_loads(self):
        response = self.client.get(reverse('cookie_policy'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cookie_policy.html')


class UserRegistrationTests(BaseTestCase):
    """Tests for user registration"""
    
    def test_registration_page_loads(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signup.html')
    
    def test_valid_registration(self):
        import uuid
        response = self.client.post(reverse('signup'), {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'StrongPass123',
            'confirm_password': 'StrongPass123',
            'terms': 'on'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())
    
    def test_registration_password_mismatch(self):
        response = self.client.post(reverse('signup'), {
            'email': 'another@example.com',
            'first_name': 'Another',
            'last_name': 'User',
            'password': 'Pass123',
            'confirm_password': 'Different123',
            'terms': 'on'
        })
        # Should show error
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', None, 'Passwords do not match')
    
    def test_registration_short_password(self):
        response = self.client.post(reverse('signup'), {
            'email': 'short@example.com',
            'first_name': 'Short',
            'last_name': 'User',
            'password': 'Short1',
            'confirm_password': 'Short1',
            'terms': 'on'
        })
        self.assertEqual(response.status_code, 200)
    
    def test_registration_duplicate_email(self):
        response = self.client.post(reverse('signup'), {
            'email': 'testuser@example.com',  # Already exists
            'first_name': 'Duplicate',
            'last_name': 'User',
            'password': 'StrongPass123',
            'confirm_password': 'StrongPass123',
            'terms': 'on'
        })
        self.assertEqual(response.status_code, 200)


class UserLoginTests(BaseTestCase):
    """Tests for user login"""
    
    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
    
    def test_valid_login(self):
        response = self.client.post(reverse('login'), {
            'email': 'testuser@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to home
        self.assertRedirects(response, reverse('home'))
    
    def test_invalid_login(self):
        response = self.client.post(reverse('login'), {
            'email': 'testuser@example.com',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', None, 'Invalid email or password')
    
    def test_login_with_nonexistent_user(self):
        response = self.client.post(reverse('login'), {
            'email': 'nonexistent@example.com',
            'password': 'somepass'
        })
        self.assertEqual(response.status_code, 200)
    
    def test_logout(self):
        self.client.login(email='testuser@example.com', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))


class APIEndpointTests(BaseTestCase):
    """Tests for API endpoints"""
    
    def test_get_user_unauthenticated(self):
        response = self.client.get(reverse('api_user'))
        self.assertEqual(response.status_code, 401)
    
    def test_get_user_authenticated(self):
        self.client.login(email='testuser@example.com', password='testpass123')
        response = self.client.get(reverse('api_user'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['email'], 'testuser@example.com')
    
    def test_get_hostels(self):
        response = self.client.get(reverse('api_hostels'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
    
    def test_get_hostels_by_city(self):
        response = self.client.get(reverse('api_hostels'), {'city': self.hostel.city})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIsInstance(data, list)
    
    def test_get_hostel_by_id(self):
        response = self.client.get(reverse('api_hostel_by_id', args=[self.hostel.id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['name'], 'Test Hostel')
    
    def test_get_hostel_by_id_404(self):
        response = self.client.get(reverse('api_hostel_by_id', args=[999]))
        self.assertEqual(response.status_code, 404)
    
    def test_create_booking_authenticated(self):
        self.client.login(email='testuser@example.com', password='testpass123')
        from .models import Room
        room = Room.objects.create(
            hostel=self.hostel,
            room_number='101',
            room_name='Standard',
            room_type='Single',
            capacity=1,
            available_quantity=5,
            price_per_night=350000,
        )
        response = self.client.post(reverse('api_create_booking'),
            json.dumps({
                'room_id': str(room.id),
                'check_in': '2026-05-01',
                'check_out': '2026-05-03',
                'guests': 1,
                'special_requests': ''
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Booking.objects.count(), 1)
    
    def test_create_booking_unauthenticated(self):
        from .models import Room
        room = Room.objects.create(
            hostel=self.hostel,
            room_number='101',
            room_name='Standard',
            room_type='Single',
            capacity=1,
            available_quantity=5,
            price_per_night=350000,
        )
        response = self.client.post(reverse('api_create_booking'),
            json.dumps({
                'room_id': str(room.id),
                'check_in': '2026-05-01',
                'check_out': '2026-05-03',
                'guests': 1,
                'special_requests': ''
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)
    
    def test_create_message_unauthenticated(self):
        response = self.client.post(reverse('api_create_message'),
            json.dumps({
                'hostelId': str(self.hostel.id),
                'fullName': 'Test',
                'email': 'test@example.com',
                'phone': '',
                'subject': 'Test',
                'content': 'Test content'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Message.objects.count(), 1)
    
    def test_get_messages_by_hostel(self):
        Message.objects.create(
            hostel=self.hostel,
            full_name='Test',
            email='test@example.com',
            phone='',
            subject='Test',
            content='Test content'
        )
        response = self.client.get(reverse('api_hostel_messages', args=[self.hostel.id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)