from django.urls import path
from . import views
from . import views_email

urlpatterns = [
    path('', views.home, name='home'),
    path('hostel/<int:id>/', views.hostel_detail, name='hostel_detail'),
    path('universities/', views.universities, name='universities'),
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    path('contact/', views.contact, name='contact'),
    path('ai-assistant/', views.ai_assistant, name='ai_assistant'),
    path('cookie-policy/', views.cookie_policy, name='cookie_policy'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-use/', views.terms_of_use, name='terms_of_use'),
    
    # Manager dashboard
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    path('manager/bookings/', views.manager_bookings, name='manager_bookings'),
    path('manager/bookings/<int:booking_id>/update/', views.manager_update_booking, name='manager_update_booking'),
    path('manager/checkins/', views.manager_checkins, name='manager_checkins'),
    path('manager/rooms/', views.manager_rooms, name='manager_rooms'),
    path('manager/checkout/<int:booking_id>/', views.manager_checkout, name='manager_checkout'),
    path('admin/hostels/upload/', views.hostel_upload, name='hostel_upload'),
    path('admin/managers/', views.admin_manager_assign, name='admin_manager_assign'),
    path('api/admin/managers/', views.api_managers, name='api_managers'),
    path('api/admin/managers/create/', views.admin_create_manager, name='api_create_manager'),
    path('api/admin/managers/unassigned/', views.api_unassigned_managers, name='api_unassigned_managers'),
    path('api/admin/hostels/<int:hostel_id>/managers/', views.api_hostel_managers, name='api_hostel_managers'),
    path('api/admin/managers/assign/', views.admin_assign_manager, name='admin_assign_manager'),
    path('api/admin/managers/remove/', views.admin_remove_manager, name='admin_remove_manager'),
    
    # API endpoints
    path('api/user/', views.get_user, name='api_user'),
    path('api/hostels/', views.api_hostels, name='api_hostels'),
    path('api/hostels/<int:id>/', views.api_hostel_detail, name='api_hostel_by_id'),
    path('api/cities/', views.api_cities, name='api_cities'),
    path('api/countries/', views.api_countries, name='api_countries'),
    path('api/bookings/', views.create_booking, name='api_create_booking'),
    path('api/bookings/<int:id>/', views.get_booking_by_id, name='api_booking_by_id'),
    path('api/messages/', views.create_message, name='api_create_message'),
    path('api/ai-chat/', views.ai_chat, name='api_ai_chat'),
    path('api/messages/<int:hostel_id>/', views.get_messages_by_hostel, name='api_hostel_messages'),
    path('api/admin/messages/', views.admin_messages, name='admin_messages'),
    
    # Auth
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('signup/verify/', views_email.signup_with_email_verification, name='signup_with_email_verification'),
    path('confirm-email/<str:token>/', views_email.confirm_email, name='confirm_email'),
    path('api/auth/google/', views.google_auth, name='api_google_auth'),
    path('api/auth/google/callback/', views.google_auth_callback, name='api_google_callback'),
    path('api/auth/resend-confirmation/', views_email.resend_confirmation, name='resend_confirmation'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
    path('profile/', views.profile, name='profile'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
]