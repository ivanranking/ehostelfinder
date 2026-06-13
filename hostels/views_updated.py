from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils import timezone
import json
import os
import urllib.request
import urllib.error
from .forms import UserRegistrationForm, UserLoginForm
from .models import Hostel, Message as DjangoMessage, User, Booking as DjangoBooking, ContactMessage
from .local_ai import get_local_ai_response

def home(request):
    university = request.GET.get('university', 'All Universities')
    
    if university and university != 'All Universities':
        hostels_qs = Hostel.objects.filter(university=university)
    else:
        hostels_qs = Hostel.objects.all()
    
    hostels = list(hostels_qs.values())
    
    universities_set = set()
    for hostel in hostels:
        if 'university' in hostel:
            universities_set.add(hostel['university'])
    
    context = {
        'hostels': hostels,
        'universities': ['All Universities'] + sorted(list(universities_set)),
        'selected_university': university,
    }
    return render(request, 'home.html', context)

def hostel_detail(request, id):
    try:
        hostel = get_object_or_404(Hostel, id=id)
        messages_list = list(DjangoMessage.objects.filter(hostel_id=id).values())
        
        hostel_dict = {
            'id': hostel.id,
            'name': hostel.name,
            'description': hostel.description,
            'university': hostel.university,
            'distance': hostel.distance,
            'price': hostel.price,
            'rating': float(hostel.rating),
            'review_count': hostel.review_count,
            'image_url': hostel.image_url,
            'amenities': hostel.amenities if isinstance(hostel.amenities, list) else [],
            'contact': hostel.contact,
            'address': hostel.address,
            'available': hostel.available,
        }
    except Exception as e:
        print(f"Error in hostel_detail: {e}")
        messages.error(request, 'Error loading hostel details')
        return redirect('home')
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to send a message')
            return redirect('login')
        
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        
        DjangoMessage.objects.create(
            hostel_id=id,
            user_id=request.user.id,
            full_name=f"{request.user.first_name} {request.user.last_name}",
            email=request.user.email,
            phone='',
            message=data.get('content', '')
        )
        
        messages.success(request, 'Message sent successfully!')
        
        if request.content_type == 'application/json':
            return JsonResponse({'success': True})
        return redirect('hostel_detail', id=id)
    
    context = {
        'hostel': hostel_dict,
        'messages': messages_list,
    }
    return render(request, 'hostel_detail.html', context)

def universities(request):
    hostels_qs = Hostel.objects.all()
    universities_set = set()
    for h in hostels_qs:
        if h.university:
            universities_set.add(h.university)
    
    context = {
        'universities': sorted(list(universities_set)),
    }
    return render(request, 'universities.html', context)

def how_it_works(request):
    return render(request, 'how_it_works.html')

def contact(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
            
            contact_message = ContactMessage.objects.create(
                full_name=data.get('name', ''),
                email=data.get('email', ''),
                subject=data.get('subject', ''),
                message=data.get('message', '')
            )
            
            if request.content_type == 'application/json':
                return JsonResponse({
                    'success': True,
                    'message': 'Thank you for your message! We\'ll get back to you soon.'
                })
            
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')
        except Exception as e:
            if request.content_type == 'application/json':
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
            messages.error(request, 'Failed to send message. Please try again.')
            return redirect('contact')
    
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
    
    try:
        if university and university != 'All Universities':
            hostels_qs = Hostel.objects.filter(university=university)
        else:
            hostels_qs = Hostel.objects.all()
        
        hostels = list(hostels_qs.values())
        return JsonResponse(hostels, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def get_hostel_by_id(request, id):
    try:
        hostel = get_object_or_404(Hostel, id=id)
        hostel_dict = {
            'id': hostel.id,
            'name': hostel.name,
            'description': hostel.description,
            'university': hostel.university,
            'distance': hostel.distance,
            'price': hostel.price,
            'rating': float(hostel.rating),
            'review_count': hostel.review_count,
            'image_url': hostel.image_url,
            'amenities': hostel.amenities if isinstance(hostel.amenities, list) else [],
            'contact': hostel.contact,
            'address': hostel.address,
            'available': hostel.available,
        }
        return JsonResponse(hostel_dict)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["POST"])
def create_booking(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'Authentication required'}, status=401)
            
            django_booking = DjangoBooking.objects.create(
                hostel_id=data.get('hostelId'),
                full_name=data.get('fullName', ''),
                email=data.get('email', ''),
                phone=data.get('phone', ''),
                university=data.get('university', ''),
                student_id=data.get('studentId', ''),
                move_in_date=data.get('moveInDate', ''),
                room_type=data.get('roomType', ''),
                special_requests=data.get('specialRequests', ''),
                status=data.get('status', 'pending')
            )
            
            booking = {
                'id': django_booking.id,
                'hostel_id': django_booking.hostel_id,
                'full_name': django_booking.full_name,
                'email': django_booking.email,
                'phone': django_booking.phone,
                'university': django_booking.university,
                'student_id': django_booking.student_id,
                'move_in_date': django_booking.move_in_date,
                'room_type': django_booking.room_type,
                'special_requests': django_booking.special_requests,
                'status': django_booking.status,
            }
            
            return JsonResponse(booking, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@require_http_methods(["GET"])
def get_booking_by_id(request, id):
    try:
        booking = get_object_or_404(DjangoBooking, id=id)
        
        if request.user.is_authenticated:
            booking_dict = {
                'id': booking.id,
                'hostel_id': booking.hostel_id,
                'full_name': booking.full_name,
                'email': booking.email,
                'phone': booking.phone,
                'university': booking.university,
                'student_id': booking.student_id,
                'move_in_date': booking.move_in_date,
                'room_type': booking.room_type,
                'special_requests': booking.special_requests,
                'status': booking.status,
            }
            return JsonResponse(booking_dict)
        return JsonResponse({'error': 'Not authorized'}, status=403)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["POST"])
def create_message(request):
    try:
        data = json.loads(request.body)
        get_object_or_404(Hostel, id=data.get('hostelId'))
        
        message_obj = DjangoMessage.objects.create(
            hostel_id=data.get('hostelId'),
            user_id=data.get('userId') if request.user.is_authenticated else None,
            full_name=data.get('fullName', ''),
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            message=data.get('content', '') or data.get('message', '')
        )
        message = {
            'id': message_obj.id,
            'hostel_id': message_obj.hostel_id,
            'full_name': message_obj.full_name,
            'email': message_obj.email,
            'phone': message_obj.phone,
            'message': message_obj.message,
            'created_at': message_obj.created_at.isoformat() if message_obj.created_at else None,
        }
        
        return JsonResponse(message, status=201)
    except Exception as e:
        return JsonResponse({'error': 'Failed to send message'}, status=500)

@csrf_exempt
@require_http_methods(['POST'])
def ai_chat(request):
    try:
        data = json.loads(request.body.decode('utf-8') if isinstance(request.body, bytes) else request.body)
        question = data.get('question', '').strip()
        if not question:
            return JsonResponse({'error': 'Question is required.'}, status=400)

        # Try to use the external Google API first
        api_key = os.getenv('GOOGLE_GENERATIVE_API_KEY')
        if api_key:
            try:
                prompt = (
                    'You are a helpful hostel assistant for EHostelFinder. Answer questions about hostel services, bookings, and amenities. '
                    'Be friendly, concise, and helpful. Context: EHostelFinder helps students find safe, comfortable, affordable accommodation near universities. '
                    f'Question: {question}'
                )
                payload = json.dumps({
                    'contents': [{
                        'parts': [{
                            'text': prompt
                        }]
                    }]
                }).encode('utf-8')
                url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}'
                req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'}, method='POST')
                with urllib.request.urlopen(req, timeout=30) as resp:
                    resp_data = resp.read().decode('utf-8')
                    result = json.loads(resp_data)
                return JsonResponse(result)
            except (urllib.error.HTTPError, urllib.error.URLError, OSError):
                # Fall back to local AI if external API fails
                pass
        
        # Use local AI fallback
        ai_response = get_local_ai_response(question)
        return JsonResponse({
            'candidates': [{
                'content': {
                    'parts': [{'text': ai_response}]
                }
            }]
        })
    except Exception:
        # For any other errors, still use local AI fallback
        try:
            question = data.get('question', '').strip()
            ai_response = get_local_ai_response(question)
            return JsonResponse({
                'candidates': [{
                    'content': {
                        'parts': [{'text': ai_response}]
                    }
                }]
            })
        except Exception:
            return JsonResponse({'error': 'AI service temporarily unavailable'}, status=500)

@require_http_methods(["GET"])
def get_messages_by_hostel(request, hostel_id):
    try:
        messages_qs = DjangoMessage.objects.filter(hostel_id=hostel_id)
        messages_list = list(messages_qs.values())
        return JsonResponse(messages_list, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET", "POST"])
def login(request):
    if request.method == 'GET':
        form = UserLoginForm()
        return render(request, 'login.html', {'form': form})

@require_http_methods(["GET", "POST"])
def signup(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'signup.html', {'form': form})

@require_http_methods(["GET"])
def logout_view(request):
    logout(request)
    return redirect('home')

def cookie_policy(request):
    return render(request, 'cookie_policy.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def terms_of_use(request):
    return render(request, 'terms_of_use.html')

@require_http_methods(["GET"])
def admin_messages(request):
    """View all contact messages - admin only"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    messages = ContactMessage.objects.all()[:100]
    messages_data = [{
        'id': msg.id,
        'full_name': msg.full_name,
        'email': msg.email,
        'subject': msg.subject,
        'message': msg.message,
        'created_at': msg.created_at.isoformat(),
        'is_read': msg.is_read,
    } for msg in messages]
    
    return JsonResponse({'messages': messages_data})

def ai_assistant(request):
    return render(request, 'ai_assistant.html')
