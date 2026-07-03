from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db.models import Avg
import json
import os
import urllib.request
import urllib.error
from .forms import UserRegistrationForm, UserLoginForm, ForgotPasswordForm, ResetPasswordForm, ProfileUpdateForm, HostelUploadForm
from .models import Hostel, User, ContactMessage, Profile, Room, Booking, Review, Favorite, Message, RoomStatus, BookingStatus
from django.contrib.auth.decorators import login_required
from .local_ai import get_local_ai_response

KAMPALA_AREA_UNIVERSITIES = [
    'Makerere University',
    'Makerere University Business School',
    'Kyambogo University',
    'Kampala International University',
    'Uganda Christian University',
    'Ndejje University',
    'Bugema University',
    'Cavendish University Uganda',
    'St. Lawrence University Uganda',
    'Mutesa I Royal University',
]


def get_university_options():
    university_names = []
    seen = set()
    
    def normalize_university(name):
        if not name:
            return ''
        name = name.strip()
        name_lower = name.lower()
        if 'makerere' in name_lower and 'business school' in name_lower:
            return 'Makerere University Business School'
        if 'makerere' in name_lower:
            return 'Makerere University'
        return name
    
    for name in KAMPALA_AREA_UNIVERSITIES:
        if name:
            normalized = normalize_university(name)
            lower = normalized.lower()
            if lower not in seen:
                university_names.append(normalized)
                seen.add(lower)

    for name in Hostel.objects.exclude(university='').values_list('university', flat=True):
        if name:
            normalized = normalize_university(name)
            lower = normalized.lower()
            if lower not in seen:
                university_names.append(normalized)
                seen.add(lower)

    return [{'name': name} for name in university_names]


def home(request):
    university = request.GET.get('university', 'All Universities')
    city = request.GET.get('city', '')
    country = request.GET.get('country', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    hostels = Hostel.objects.all()
    if university and university != 'All Universities':
        hostels = hostels.filter(university=university)
    if city:
        hostels = hostels.filter(city__icontains=city)
    if country:
        hostels = hostels.filter(country__icontains=country)
    if min_price:
        try:
            hostels = hostels.filter(price__gte=float(min_price)).distinct()
        except ValueError:
            pass
    if max_price:
        try:
            hostels = hostels.filter(price__lte=float(max_price)).distinct()
        except ValueError:
            pass

    cities = sorted(Hostel.objects.values_list('city', flat=True).exclude(city='').distinct())
    countries = sorted(Hostel.objects.values_list('country', flat=True).exclude(country='').distinct())
    universities = get_university_options()

    rated_hostels = Hostel.objects.exclude(rating__isnull=True)
    avg_rating = 0.0
    if rated_hostels.exists():
        avg = sum(float(h.rating) for h in rated_hostels) / rated_hostels.count()
        avg_rating = round(avg, 1)

    hostel_list = []
    for h in hostels:
        cover = h.images.filter(is_cover=True).first()
        available_room = h.rooms.filter(status='Available').first()
        hostel_list.append({
            'id': str(h.id),
            'name': h.name,
            'description': h.description,
            'city': h.city,
            'country': h.country,
            'university': h.university,
            'image_url': h.image_url or (cover.image_url if cover else None),
            'facilities': [{'name': f.facility_name, 'icon': f.icon or ''} for f in h.facilities.all()],
            'available': h.available,
            'rating': float(h.rating) if h.rating else round(float(h.average_rating), 1),
            'distance': h.distance or 'Near campus',
            'price': str(h.price) if h.price else (str(available_room.price_per_night) if available_room else '0'),
            'amenities': h.amenities or [],
        })

    context = {
        'hostels': hostel_list,
        'cities': cities,
        'countries': countries,
        'universities': universities,
        'selected_city': city,
        'selected_country': country,
        'selected_university': university,
        'total_hostels': Hostel.objects.count(),
        'total_universities': len(universities),
        'avg_rating': avg_rating,
        'total_cities': len(cities),
    }
    return render(request, 'home.html', context)


def hostel_detail(request, id):
    try:
        hostel = get_object_or_404(Hostel, id=id)
        rooms = Room.objects.filter(hostel=hostel, status='Available')
        images = hostel.images.all()
        cover = hostel.images.filter(is_cover=True).first()
        facilities = hostel.facilities.all()
        reviews = hostel.reviews.select_related('customer').all()

        rooms_data = [{
            'id': str(r.id),
            'room_number': r.room_number,
            'room_name': r.room_name,
            'room_type': r.room_type,
            'capacity': r.capacity,
            'available_quantity': r.available_quantity,
            'price_per_night': str(r.price_per_night),
            'description': r.description,
            'size_sq_meters': str(r.size_sq_meters) if r.size_sq_meters else None,
            'private_bathroom': r.private_bathroom,
            'air_conditioning': r.air_conditioning,
            'balcony': r.balcony,
            'television': r.television,
            'wifi': r.wifi,
            'images': [ri.image_url for ri in r.images.all()],
        } for r in rooms]

        reviews_data = [{
            'id': str(rv.id),
            'customer_name': rv.customer.get_full_name() or rv.customer.email,
            'rating': rv.rating,
            'comment': rv.comment,
            'created_at': rv.created_at.strftime('%Y-%m-%d'),
        } for rv in reviews]

        context = {
            'hostel': {
                'id': str(hostel.id),
                'name': hostel.name,
                'description': hostel.description,
                'address': hostel.address,
                'city': hostel.city,
                'country': hostel.country,
                'university': hostel.university,
                'distance': hostel.distance or 'Near campus',
                'price': float(hostel.price) if hostel.price else 0,
                'rating': float(hostel.rating) if hostel.rating else round(float(hostel.average_rating), 1),
                'available': hostel.available,
                'contact': hostel.contact or '',
                'amenities': hostel.amenities or [],
                'phone': hostel.phone,
                'email': hostel.email,
                'latitude': str(hostel.latitude) if hostel.latitude else None,
                'longitude': str(hostel.longitude) if hostel.longitude else None,
                'cover_image': cover.image_url if cover else None,
                'images': [{'url': img.image_url, 'is_cover': img.is_cover} for img in images],
            },
            'rooms': rooms_data,
            'facilities': [{'name': f.facility_name, 'icon': f.icon or ''} for f in facilities],
            'reviews': reviews_data,
        }
    except Exception as e:
        print(f"Error in hostel_detail: {e}")
        messages.error(request, 'Error loading hostel details')
        return redirect('home')

    if request.method == 'POST':
        if 'review_submit' in request.POST:
            if not request.user.is_authenticated:
                messages.error(request, 'You must be logged in to leave a review')
                return redirect('login')

            rating = request.POST.get('rating', '').strip()
            comment = request.POST.get('comment', '').strip()

            if not rating or not rating.isdigit() or int(rating) not in range(1, 6):
                messages.error(request, 'Please select a valid rating from 1 to 5.')
                return redirect('hostel_detail', id=hostel.id)

            Review.objects.create(
                hostel=hostel,
                customer=request.user,
                rating=int(rating),
                comment=comment,
            )

            hostel.review_count = hostel.reviews.count()
            hostel.rating = round(hostel.reviews.aggregate(avg=Avg('rating'))['avg'] or 0, 2)
            hostel.save(update_fields=['review_count', 'rating'])
            messages.success(request, 'Your review has been submitted successfully.')
            return redirect('hostel_detail', id=hostel.id)

        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to send a message')
            return redirect('login')

    return render(request, 'hostel_detail.html', context)


@require_http_methods(["GET"])
def api_hostels(request):
    city = request.GET.get('city', '')
    country = request.GET.get('country', '')
    room_type = request.GET.get('room_type', '')
    university = request.GET.get('university', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    hostels = Hostel.objects.all()
    if city:
        hostels = hostels.filter(city__icontains=city)
    if country:
        hostels = hostels.filter(country__icontains=country)
    if university:
        hostels = hostels.filter(university=university)
    if room_type:
        hostels = hostels.filter(rooms__room_type=room_type).distinct()
    if min_price:
        try:
            hostels = hostels.filter(price__gte=float(min_price)).distinct()
        except ValueError:
            pass
    if max_price:
        try:
            hostels = hostels.filter(price__lte=float(max_price)).distinct()
        except ValueError:
            pass

    results = []
    for h in hostels:
        cover = h.images.filter(is_cover=True).first()
        results.append({
            'id': str(h.id),
            'name': h.name,
            'city': h.city,
            'country': h.country,
            'university': h.university,
            'address': h.address,
            'description': h.description,
            'average_rating': round(float(h.average_rating), 2),
            'rating': float(h.rating) if h.rating else round(float(h.average_rating), 2),
            'review_count': h.reviews.count(),
            'image_url': h.image_url or (cover.image_url if cover else None),
            'facilities': [f.facility_name for f in h.facilities.all()],
            'amenities': h.amenities or [],
            'check_in_time': h.check_in_time.strftime('%H:%M') if h.check_in_time else '14:00',
            'check_out_time': h.check_out_time.strftime('%H:%M') if h.check_out_time else '11:00',
            'distance': h.distance or '',
            'price': float(h.price) if h.price else 0,
            'contact': h.contact or '',
            'available': h.available,
        })
    return JsonResponse(results, safe=False)


@require_http_methods(["GET"])
def api_hostel_detail(request, id):
    hostel = get_object_or_404(Hostel, id=id)
    rooms = Room.objects.filter(hostel=hostel)
    cover = hostel.images.filter(is_cover=True).first()

    rooms_data = [{
        'id': str(r.id),
        'room_number': r.room_number,
        'room_name': r.room_name,
        'room_type': r.room_type,
        'capacity': r.capacity,
        'available_quantity': r.available_quantity,
        'price_per_night': str(r.price_per_night),
        'description': r.description,
        'size_sq_meters': str(r.size_sq_meters) if r.size_sq_meters else None,
        'private_bathroom': r.private_bathroom,
        'air_conditioning': r.air_conditioning,
        'balcony': r.balcony,
        'television': r.television,
        'wifi': r.wifi,
        'status': r.status,
        'images': [ri.image_url for ri in r.images.all()],
    } for r in rooms]

    result = {
        'id': str(hostel.id),
        'name': hostel.name,
        'description': hostel.description,
        'address': hostel.address,
        'city': hostel.city,
        'country': hostel.country,
        'phone': hostel.phone,
        'email': hostel.email,
        'latitude': str(hostel.latitude) if hostel.latitude else None,
        'longitude': str(hostel.longitude) if hostel.longitude else None,
        'check_in_time': hostel.check_in_time.strftime('%H:%M') if hostel.check_in_time else '14:00',
        'check_out_time': hostel.check_out_time.strftime('%H:%M') if hostel.check_out_time else '11:00',
        'image_url': cover.image_url if cover else None,
        'images': [{'url': img.image_url, 'is_cover': img.is_cover} for img in hostel.images.all()],
        'rooms': rooms_data,
        'facilities': [{'name': f.facility_name, 'icon': f.icon or ''} for f in hostel.facilities.all()],
    }
    return JsonResponse(result)


@require_http_methods(["GET"])
def api_cities(request):
    cities = sorted(Hostel.objects.values_list('city', flat=True).exclude(city='').distinct())
    return JsonResponse(cities, safe=False)


@require_http_methods(["GET"])
def api_countries(request):
    countries = sorted(Hostel.objects.values_list('country', flat=True).exclude(country='').distinct())
    return JsonResponse(countries, safe=False)


@require_http_methods(["GET", "POST"])
def login(request):
    if request.method == 'GET':
        form = UserLoginForm()
        return render(request, 'login.html', {'form': form})
    form = UserLoginForm(request.POST)
    if form.is_valid():
        from django.contrib.auth import authenticate, login as auth_login
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = authenticate(request, username=email, password=password)
        if user:
            auth_login(request, user)
            if not user.is_email_verified:
                messages.info(request, 'You signed in successfully. Your email verification is still pending, but you can continue using the site.')
            return redirect('home')
        messages.error(request, 'Invalid email or password')
    else:
        messages.error(request, 'Invalid email or password')
    return render(request, 'login.html', {'form': form})


@require_http_methods(["GET", "POST"])
def signup(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            try:
                from .email_utils import send_email_confirmation
                send_email_confirmation(user, request)
            except Exception:
                pass
            messages.success(request, 'Account created! Please check your email to confirm your account before logging in.')
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


@require_http_methods(["GET", "POST"])
def get_user(request):
    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        user_data = {
            'id': request.user.id,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'profile_image_url': profile.profile_photo if profile else None,
            'role': profile.role if profile else 'customer',
            'full_name': profile.full_name if profile else '',
        }
        return JsonResponse(user_data)
    return JsonResponse({'error': 'Not authenticated'}, status=401)


@require_http_methods(["POST"])
def create_booking(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        data = json.loads(request.body)
        room = get_object_or_404(Room, id=data.get('room_id'))
        
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        guests = int(data.get('guests', 1))
        
        nights = (check_out - check_in).days
        if nights <= 0:
            return JsonResponse({'error': 'Invalid date range'}, status=400)
        
        total_price = room.price_per_night * nights
        
        booking = Booking.objects.create(
            hostel_id=room.hostel_id,
            room=room,
            customer_id=request.user.id,
            check_in=check_in,
            check_out=check_out,
            guests=guests,
            nights=nights,
            total_price=total_price,
            special_requests=data.get('special_requests', ''),
            booking_status='Pending',
            payment_status='Pending',
        )
        
        result = {
            'id': str(booking.id),
            'booking_reference': booking.booking_reference,
            'hostel_id': str(booking.hostel_id),
            'room_id': str(booking.room_id),
            'customer_id': str(booking.customer_id),
            'check_in': booking.check_in.isoformat(),
            'check_out': booking.check_out.isoformat(),
            'guests': booking.guests,
            'nights': booking.nights,
            'total_price': str(booking.total_price),
            'booking_status': booking.booking_status,
            'payment_status': booking.payment_status,
            'special_requests': booking.special_requests,
            'booked_at': booking.booked_at.isoformat(),
        }
        return JsonResponse(result, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["GET"])
def get_booking_by_id(request, id):
    try:
        booking = get_object_or_404(Booking, id=id)
        if request.user.id == booking.customer_id:
            result = {
                'id': str(booking.id),
                'booking_reference': booking.booking_reference,
                'hostel_id': str(booking.hostel_id),
                'room_id': str(booking.room_id),
                'check_in': booking.check_in.isoformat(),
                'check_out': booking.check_out.isoformat(),
                'guests': booking.guests,
                'nights': booking.nights,
                'total_price': str(booking.total_price),
                'booking_status': booking.booking_status,
                'payment_status': booking.payment_status,
                'special_requests': booking.special_requests,
            }
            return JsonResponse(result)
        return JsonResponse({'error': 'Not authorized'}, status=403)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
def create_message(request):
    try:
        data = json.loads(request.body)
        hostel = get_object_or_404(Hostel, id=data.get('hostelId'))
        
        message = Message.objects.create(
            hostel=hostel,
            user=request.user if request.user.is_authenticated else None,
            full_name=data.get('fullName', ''),
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            subject=data.get('subject', ''),
            content=data.get('content', '') or data.get('message', '')
        )
        
        result = {
            'id': str(message.id),
            'hostel_id': str(message.hostel_id),
            'full_name': message.full_name,
            'email': message.email,
            'phone': message.phone,
            'subject': message.subject,
            'message': message.message,
            'created_at': message.created_at.isoformat(),
        }
        return JsonResponse(result, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def ai_chat(request):
    try:
        data = json.loads(request.body.decode('utf-8') if isinstance(request.body, bytes) else request.body)
        question = data.get('question', '').strip()
        if not question:
            return JsonResponse({'error': 'Question is required.'}, status=400)

        api_key = os.getenv('GOOGLE_GENERATIVE_API_KEY')
        if api_key:
            try:
                prompt = (
                    'You are a helpful hostel assistant for EHostelFinder. Answer questions about hostel services, bookings, and amenities. '
                    'Be friendly, concise, and helpful. Context: EHostelFinder helps students find safe, comfortable, affordable accommodation near universities. '
                    f'Question: {question}'
                )
                payload = json.dumps({
                    'contents': [{'parts': [{'text': prompt}]}]
                }).encode('utf-8')
                url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}'
                req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'}, method='POST')
                with urllib.request.urlopen(req, timeout=30) as resp:
                    resp_data = resp.read().decode('utf-8')
                    result = json.loads(resp_data)
                return JsonResponse(result)
            except (urllib.error.HTTPError, urllib.error.URLError, OSError):
                pass
        
        ai_response = get_local_ai_response(question)
        return JsonResponse({
            'candidates': [{
                'content': {
                    'parts': [{'text': ai_response}]
                }
            }]
        })
    except Exception:
        try:
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
        messages = Message.objects.filter(hostel_id=hostel_id)
        messages_list = [{
            'id': str(m.id),
            'hostel_id': str(m.hostel_id),
            'full_name': m.full_name,
            'email': m.email,
            'phone': m.phone,
            'subject': m.subject,
            'message': m.message,
            'created_at': m.created_at.isoformat(),
        } for m in messages]
        return JsonResponse(messages_list, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def how_it_works(request):
    return render(request, 'how_it_works.html')


@require_http_methods(["GET"])
def universities(request):
    university_options = get_university_options()
    universities_data = []
    for uni in university_options:
        name = uni['name']
        count = Hostel.objects.filter(university=name).count()
        top_hostel = Hostel.objects.filter(university=name).order_by('-rating').first()
        universities_data.append({
            'name': name,
            'count': count,
            'top_hostel': top_hostel.name if top_hostel else '',
            'rating': float(top_hostel.rating) if top_hostel and top_hostel.rating else 0,
        })
    universities_data.sort(key=lambda x: x['name'])
    return render(request, 'universities.html', {'universities': universities_data})


@csrf_exempt
def contact(request):
    if request.method == 'POST':
        try:
            ContactMessage.objects.create(
                full_name=request.POST.get('name', ''),
                email=request.POST.get('email', ''),
                subject=request.POST.get('subject', ''),
                message=request.POST.get('message', '')
            )
            return JsonResponse({'success': True, 'message': 'Message sent successfully!'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return render(request, 'contact.html')


def google_auth(request):
    import urllib.parse
    from django.conf import settings
    
    redirect_uri = request.build_absolute_uri('/api/auth/google/callback/')
    params = {
        'client_id': settings.GOOGLE_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'email profile',
        'access_type': 'online',
    }
    auth_url = f"https://accounts.google.com/o/oauth2/auth?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)


def google_auth_callback(request):
    import urllib.parse
    import urllib.request
    from django.conf import settings
    from django.contrib.auth import login as auth_login
    
    code = request.GET.get('code')
    if not code:
        messages.error(request, 'Google authentication failed')
        return redirect('login')
    
    redirect_uri = request.build_absolute_uri('/api/auth/google/callback/')
    token_data = urllib.parse.urlencode({
        'code': code,
        'client_id': settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code',
    }).encode()
    
    try:
        req = urllib.request.Request('https://oauth2.googleapis.com/token', data=token_data, method='POST')
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        with urllib.request.urlopen(req, timeout=10) as resp:
            token_result = json.loads(resp.read().decode())
        
        access_token = token_result.get('access_token')
        user_req = urllib.request.Request(f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={access_token}")
        with urllib.request.urlopen(user_req, timeout=10) as resp:
            user_info = json.loads(resp.read().decode())
        
        email = user_info.get('email')
        first_name = user_info.get('given_name', '')
        last_name = user_info.get('family_name', '')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            import uuid
            user = User.objects.create(
                id=str(uuid.uuid4()),
                email=email,
                first_name=first_name or email.split('@')[0],
                last_name=last_name,
                provider='google'
            )
        
        auth_login(request, user)
        return redirect('home')
    except Exception as e:
        messages.error(request, 'Google authentication failed')
        return redirect('login')


def manager_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'manager':
        messages.error(request, 'Access denied. Manager only.')
        return redirect('home')
    hostel = profile.hostel
    if not hostel:
        messages.error(request, 'No hostel assigned to your profile.')
        return redirect('home')
    return render(request, 'manager/dashboard.html', {'hostel': hostel})


@login_required
def admin_manager_assign(request):
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'admin':
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')
    return render(request, 'admin/manager_assign.html')


@login_required
@require_http_methods(['GET', 'POST'])
def hostel_upload(request):
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'admin':
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')

    if request.method == 'POST':
        form = HostelUploadForm(request.POST)
        if form.is_valid():
            hostel = Hostel.objects.create(
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'] or '',
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                country=form.cleaned_data.get('country') or 'Uganda',
                university=form.cleaned_data['university'] or '',
                distance='Near campus',
                price=form.cleaned_data['price_single'] or 0,
                rating=form.cleaned_data['rating'] or 0,
                amenities=[item.strip() for item in form.cleaned_data['amenities'].split(',') if item.strip()],
                image_url=form.cleaned_data['image_url'] or '',
            )

            room_types = [
                ('Single', form.cleaned_data['price_single'], request.POST.get('room_available_single')),
                ('Double', form.cleaned_data['price_double'], request.POST.get('room_available_double')),
                ('Triple', form.cleaned_data['price_triple'], request.POST.get('room_available_triple')),
                ('Quadruple', form.cleaned_data['price_quadruple'], request.POST.get('room_available_quadruple')),
            ]
            for index, (room_type, price, is_avail) in enumerate(room_types, start=1):
                if price is None or price == 0:
                    continue
                capacity = 1 if room_type == 'Single' else 2 if room_type == 'Double' else 3 if room_type == 'Triple' else 4
                Room.objects.create(
                    hostel=hostel,
                    room_number=str(index),
                    room_name=f'{room_type} Room',
                    room_type=room_type,
                    capacity=capacity,
                    available_quantity=1,
                    price_per_night=price,
                    is_available=is_avail == 'on',
                )

            messages.success(request, 'Hostel created successfully.')
            return redirect('hostel_upload')
    else:
        form = HostelUploadForm()

    return render(request, 'admin/hostel_upload.html', {'form': form})


@require_http_methods(['GET'])
def manager_bookings(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'manager':
        return JsonResponse({'error': 'Access denied'}, status=403)
    hostel = profile.hostel
    if not hostel:
        return JsonResponse({'error': 'No hostel assigned'}, status=400)
    bookings = Booking.objects.filter(hostel=hostel).select_related('customer', 'room').order_by('-booked_at')
    bookings_data = [{
        'id': str(b.id),
        'booking_reference': b.booking_reference,
        'customer_name': b.customer.get_full_name() or b.customer.email,
        'customer_email': b.customer.email,
        'room_number': b.room.room_number,
        'room_name': b.room.room_name,
        'check_in': b.check_in.isoformat(),
        'check_out': b.check_out.isoformat(),
        'guests': b.guests,
        'nights': b.nights,
        'total_price': str(b.total_price),
        'booking_status': b.booking_status,
        'payment_status': b.payment_status,
        'special_requests': b.special_requests or '',
        'booked_at': b.booked_at.isoformat(),
    } for b in bookings]
    return JsonResponse(bookings_data, safe=False)


@require_http_methods(['POST'])
def manager_update_booking(request, booking_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'manager':
        return JsonResponse({'error': 'Access denied'}, status=403)
    hostel = profile.hostel
    if not hostel:
        return JsonResponse({'error': 'No hostel assigned'}, status=400)
    try:
        data = json.loads(request.body)
        booking = get_object_or_404(Booking, id=booking_id, hostel=hostel)
        status = data.get('booking_status')
        if status and status in dict(BookingStatus.choices).keys():
            booking.booking_status = status
            booking.save(update_fields=['booking_status'])
        return JsonResponse({'success': True, 'message': 'Booking updated'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(['GET', 'POST'])
def manager_checkins(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'manager':
        return JsonResponse({'error': 'Access denied'}, status=403)
    hostel = profile.hostel
    if not hostel:
        return JsonResponse({'error': 'No hostel assigned'}, status=400)
    if request.method == 'GET':
        bookings = Booking.objects.filter(hostel=hostel, booking_status='Checked In').select_related('customer', 'room')
        checkins = [{
            'id': str(b.id),
            'booking_reference': b.booking_reference,
            'customer_name': b.customer.get_full_name() or b.customer.email,
            'customer_email': b.customer.email,
            'room_number': b.room.room_number,
            'room_name': b.room.room_name,
            'check_in': b.check_in.isoformat(),
            'check_out': b.check_out.isoformat(),
            'guests': b.guests,
            'total_price': str(b.total_price),
        } for b in bookings]
        return JsonResponse(checkins, safe=False)


@require_http_methods(['GET', 'POST'])
def manager_rooms(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'manager':
        return JsonResponse({'error': 'Access denied'}, status=403)
    hostel = profile.hostel
    if not hostel:
        return JsonResponse({'error': 'No hostel assigned'}, status=400)
    if request.method == 'GET':
        rooms = Room.objects.filter(hostel=hostel)
        rooms_data = [{
            'id': str(r.id),
            'room_number': r.room_number,
            'room_name': r.room_name,
            'room_type': r.room_type,
            'capacity': r.capacity,
            'available_quantity': r.available_quantity,
            'price_per_night': str(r.price_per_night),
            'status': r.status,
            'is_available': r.is_available,
        } for r in rooms]
        return JsonResponse(rooms_data, safe=False)
    else:
        try:
            data = json.loads(request.body)
            room_id = data.get('room_id')
            status = data.get('status')
            available_quantity = data.get('available_quantity')
            is_available = data.get('is_available')
            room = get_object_or_404(Room, id=room_id, hostel=hostel)
            if status in dict(RoomStatus.choices).keys():
                room.status = status
                room.is_available = status == 'Available'
            if is_available is not None:
                room.is_available = is_available == 'true' or is_available is True
            if available_quantity is not None:
                room.available_quantity = int(available_quantity)
            room.save()
            return JsonResponse({'success': True, 'message': 'Room updated'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(['POST'])
def admin_assign_manager(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'admin':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        manager_id = data.get('manager_id')
        hostel_id = data.get('hostel_id')
        
        if not manager_id or not hostel_id:
            return JsonResponse({'error': 'manager_id and hostel_id are required'}, status=400)
        
        manager_profile = get_object_or_404(Profile, id=manager_id, role='manager')
        hostel = get_object_or_404(Hostel, id=hostel_id)
        
        manager_profile.hostel = hostel
        manager_profile.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Manager {manager_profile.full_name} assigned to {hostel.name}',
            'manager_id': str(manager_profile.id),
            'hostel_id': str(hostel.id)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(['POST'])
def admin_remove_manager(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'admin':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        manager_id = data.get('manager_id')
        
        if not manager_id:
            return JsonResponse({'error': 'manager_id is required'}, status=400)
        
        manager_profile = get_object_or_404(Profile, id=manager_id, role='manager')
        manager_profile.hostel = None
        manager_profile.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Manager {manager_profile.full_name} removed from hostel'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(['GET'])
def api_managers(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'admin':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    managers = Profile.objects.filter(role='manager').select_related('hostel')
    managers_data = [{
        'id': str(m.id),
        'full_name': m.full_name,
        'email': m.email,
        'phone': m.phone,
        'hostel_id': str(m.hostel_id) if m.hostel else None,
        'hostel_name': m.hostel.name if m.hostel else None,
    } for m in managers]
    
    return JsonResponse(managers_data, safe=False)


@csrf_exempt
@require_http_methods(['POST'])
def admin_create_manager(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'admin':
        return JsonResponse({'error': 'Access denied'}, status=403)

    try:
        data = json.loads(request.body)
        full_name = data.get('full_name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        password = data.get('password', '')

        if not full_name or not email or not password:
            return JsonResponse({'error': 'Full name, email, and password are required'}, status=400)

        if len(password) < 8:
            return JsonResponse({'error': 'Password must be at least 8 characters'}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'User with this email already exists'}, status=400)

        import uuid
        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0] if name_parts else full_name
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        user = User.objects.create(
            id=str(uuid.uuid4()),
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_email_verified=True,
        )
        user.set_password(password)
        user.save()

        manager_profile = Profile.objects.create(
            user=user,
            full_name=full_name,
            email=email,
            phone=phone or None,
            role='manager',
        )

        return JsonResponse({
            'success': True,
            'message': f'Manager {full_name} created successfully',
            'manager': {
                'id': str(manager_profile.id),
                'full_name': manager_profile.full_name,
                'email': manager_profile.email,
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(['GET'])
def api_unassigned_managers(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'admin':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    managers = Profile.objects.filter(role='manager', hostel__isnull=True)
    managers_data = [{
        'id': str(m.id),
        'full_name': m.full_name,
        'email': m.email,
    } for m in managers]
    
    return JsonResponse(managers_data, safe=False)


@require_http_methods(['GET'])
def api_hostel_managers(request, hostel_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'admin':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    hostel = get_object_or_404(Hostel, id=hostel_id)
    managers = Profile.objects.filter(role='manager', hostel=hostel)
    managers_data = [{
        'id': str(m.id),
        'full_name': m.full_name,
        'email': m.email,
        'phone': m.phone,
    } for m in managers]

    return JsonResponse(managers_data, safe=False)


@require_http_methods(['POST'])
def manager_checkout(request, booking_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'manager':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    hostel = profile.hostel
    if not hostel:
        return JsonResponse({'error': 'No hostel assigned'}, status=400)
    
    try:
        booking = get_object_or_404(Booking, id=booking_id, hostel=hostel)
        booking.booking_status = 'Checked Out'
        booking.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["GET", "POST"])
def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                from .email_utils import send_password_reset_email
                send_password_reset_email(user, request)
            except User.DoesNotExist:
                pass
            messages.success(request, 'If an account with that email exists, a password reset link has been sent.')
            return redirect('login')
    else:
        form = ForgotPasswordForm()
    return render(request, 'forgot_password.html', {'form': form})


@require_http_methods(["GET", "POST"])
def reset_password(request, token):
    from .models import PasswordResetToken
    try:
        reset_token = PasswordResetToken.objects.select_related('user').get(token=token)
    except PasswordResetToken.DoesNotExist:
        return render(request, 'password_reset_status.html', {
            'status': 'invalid',
            'message': 'Invalid reset link.'
        })
    
    if reset_token.is_expired:
        return render(request, 'password_reset_status.html', {
            'status': 'expired',
            'message': 'This reset link has expired. Please request a new one.'
        })
    
    if reset_token.is_used:
        return render(request, 'password_reset_status.html', {
            'status': 'used',
            'message': 'This reset link has already been used.'
        })
    
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user = reset_token.user
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            reset_token.used_at = timezone.now()
            reset_token.save()
            messages.success(request, 'Your password has been reset. You can now log in.')
            return redirect('login')
    else:
        form = ResetPasswordForm()
    return render(request, 'reset_password.html', {'form': form, 'token': token})


@login_required
def profile(request):
    user = request.user
    profile = getattr(user, 'profile', None)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.save(update_fields=['first_name', 'last_name'])
            messages.success(request, 'Profile updated successfully')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=profile)
    return render(request, 'profile.html', {'form': form, 'profile': profile})


@login_required
def my_bookings(request):
    user = request.user
    bookings = Booking.objects.filter(customer=user).select_related('hostel', 'room').order_by('-booked_at')
    return render(request, 'my_bookings.html', {'bookings': bookings})