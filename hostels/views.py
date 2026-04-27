from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import json
from django.db import models
from .models import Hostel, Booking, Message, User
from .forms import BookingForm, MessageForm, UserRegistrationForm, UserLoginForm

def home(request):
    hostels = Hostel.objects.filter(available=True)
    universities = Hostel.objects.values_list('university', flat=True).distinct()
    
    university_filter = request.GET.get('university', 'All Universities')
    if university_filter and university_filter != 'All Universities':
        hostels = hostels.filter(university=university_filter)
    
    context = {
        'hostels': hostels,
        'universities': ['All Universities'] + list(universities),
        'selected_university': university_filter,
    }
    return render(request, 'home.html', context)

def hostel_detail(request, id):
    hostel = get_object_or_404(Hostel, id=id)
    bookings = Booking.objects.filter(hostel=hostel)
    messages_list = Message.objects.filter(hostel=hostel).order_by('-created_at')
    
    if request.method == 'POST' and request.user.is_authenticated:
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.user = request.user
            message.hostel = hostel
            message.save()
            return redirect('hostel_detail', id=id)
    else:
        form = MessageForm()
    
    context = {
        'hostel': hostel,
        'bookings': bookings,
        'messages': messages_list,
        'form': form,
    }
    return render(request, 'hostel_detail.html', context)

def universities(request):
    universities = Hostel.objects.values_list('university', flat=True).distinct()
    context = {
        'universities': universities,
    }
    return render(request, 'universities.html', context)

def how_it_works(request):
    return render(request, 'how_it_works.html')

def contact(request):
    return render(request, 'contact.html')

@require_http_methods(["GET"])
def get_user(request):
    if request.user.is_authenticated:
        user_data = {
            'id': request.user.id,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'profile_image_url': request.user.profile_image_url,
        }
        return JsonResponse(user_data)
    return JsonResponse({'error': 'Not authenticated'}, status=401)

@require_http_methods(["GET"])
def get_hostels(request):
    university = request.GET.get('university')
    
    hostels = Hostel.objects.filter(available=True)
    if university and university != 'All Universities':
        hostels = hostels.filter(university=university)
    
    hostels_data = list(hostels.values())
    return JsonResponse(hostels_data, safe=False)

@require_http_methods(["GET"])
def get_hostel_by_id(request, id):
    hostel = get_object_or_404(Hostel, id=id)
    hostel_data = {
        'id': hostel.id,
        'name': hostel.name,
        'description': hostel.description,
        'university': hostel.university,
        'distance': hostel.distance,
        'price': hostel.price,
        'rating': str(hostel.rating),
        'review_count': hostel.review_count,
        'image_url': hostel.image_url,
        'amenities': hostel.amenities,
        'contact': hostel.contact,
        'address': hostel.address,
        'available': hostel.available,
    }
    return JsonResponse(hostel_data)

@require_http_methods(["POST"])
@login_required
def create_booking(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            hostel = get_object_or_404(Hostel, id=data.get('hostelId'))
            
            booking = Booking.objects.create(
                user=request.user,
                hostel=hostel,
                check_in=data.get('checkIn'),
                check_out=data.get('checkOut'),
                guests=data.get('guests'),
                total_price=data.get('totalPrice'),
                status=data.get('status', 'pending')
            )
            
            booking_data = {
                'id': booking.id,
                'user': booking.user.id,
                'hostelId': booking.hostel.id,
                'checkIn': booking.check_in.strftime('%Y-%m-%d'),
                'checkOut': booking.check_out.strftime('%Y-%m-%d'),
                'guests': booking.guests,
                'totalPrice': booking.total_price,
                'status': booking.status,
            }
            return JsonResponse(booking_data, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@require_http_methods(["GET"])
def get_booking_by_id(request, id):
    booking = get_object_or_404(Booking, id=id)
    if booking.user != request.user and not request.user.is_superuser:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    
    booking_data = {
        'id': booking.id,
        'user': booking.user.id,
        'hostelId': booking.hostel.id,
        'checkIn': booking.check_in.strftime('%Y-%m-%d'),
        'checkOut': booking.check_out.strftime('%Y-%m-%d'),
        'guests': booking.guests,
        'totalPrice': booking.total_price,
        'status': booking.status,
    }
    return JsonResponse(booking_data)

@require_http_methods(["POST"])
def create_message(request):
    try:
        data = json.loads(request.body)
        hostel = get_object_or_404(Hostel, id=data.get('hostelId'))
        
        message = Message.objects.create(
            user=request.user if request.user.is_authenticated else None,
            hostel=hostel,
            subject=data.get('subject', ''),
            content=data.get('content', ''),
        )
        
        message_data = {
            'id': message.id,
            'user': message.user.id if message.user else None,
            'hostelId': message.hostel.id,
            'subject': message.subject,
            'content': message.content,
            'createdAt': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
        return JsonResponse(message_data, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["GET"])
def get_messages_by_hostel(request, hostel_id):
    messages = Message.objects.filter(hostel_id=hostel_id).order_by('-created_at')
    messages_data = list(messages.values(
        'id', 'subject', 'content', 'created_at',
        user_id=models.F('user__id'),
        user_email=models.F('user__email'),
    ))
    return JsonResponse(messages_data, safe=False)

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid email or password')
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('home')

def signup(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'signup.html', {'form': form})

def cookie_policy(request):
    return render(request, 'cookie_policy.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def terms_of_use(request):
    return render(request, 'terms_of_use.html')