from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('hostel/<int:id>/', views.hostel_detail, name='hostel_detail'),
    path('universities/', views.universities, name='universities'),
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    path('contact/', views.contact, name='contact'),
    
    # API endpoints
    path('api/user/', views.get_user, name='api_user'),
    path('api/hostels/', views.get_hostels, name='api_hostels'),
    path('api/hostels/<int:id>/', views.get_hostel_by_id, name='api_hostel_by_id'),
    path('api/bookings/', views.create_booking, name='api_create_booking'),
    path('api/bookings/<int:id>/', views.get_booking_by_id, name='api_booking_by_id'),
    path('api/messages/', views.create_message, name='api_create_message'),
    path('api/messages/<int:hostel_id>/', views.get_messages_by_hostel, name='api_hostel_messages'),
    
    # Auth
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('cookie-policy/', views.cookie_policy, name='cookie_policy'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-use/', views.terms_of_use, name='terms_of_use'),
    path('api/admin/messages/', views.admin_messages, name='admin_messages'),
]