#!/usr/bin/env python3
"""Append remaining functions to views.py"""
import os, py_compile

os.chdir('c:/Users/user/ehostelfinder')

with open('hostels/views.py', 'r') as f:
    existing = f.read()

remaining = """

@require_http_methods(["GET"])
def api_hostels(request):
    city = request.GET.get('city', ''); country = request.GET.get('country', '')
    room_type = request.GET.get('room_type', ''); university = request.GET.get('university', '')
    min_price = request.GET.get('min_price', ''); max_price = request.GET.get('max_price', '')
    hostels = Hostel.objects.all()
    if city: hostels = hostels.filter(city__icontains=city)
    if country: hostels = hostels.filter(country__icontains=country)
    if university: hostels = hostels.filter(university=university)
    if room_type: hostels = hostels.filter(rooms__room_type=room_type).distinct()
    if min_price:
        try: hostels = hostels.filter(price__gte=float(min_price)).distinct()
        except: pass
    if max_price:
        try: hostels = hostels.filter(price__lte=float(max_price)).distinct()
        except: pass
    results = []
    for h in hostels:
        cover = h.images.filter(is_cover=True).first()
        results.append({'id': str(h.id), 'name': h.name, 'city': h.city, 'country': h.country, 'university': h.university, 'address': h.address, 'description': h.description, 'average_rating': round(float(h.average_rating), 2), 'rating': float(h.rating) if h.rating else round(float(h.average_rating), 2), 'review_count': h.reviews.count(), 'image_url': h.image_url or (cover.image_url if cover else None), 'facilities': [f.facility_name for f in h.facilities.all()], 'amenities': h.amenities or [], 'check_in_time': h.check_in_time.strftime('%H:%M') if h.check_in_time else '14:00', 'check_out_time': h.check_out_time.strftime('%H:%M') if h.check_out_time else '11:00', 'distance': h.distance or '', 'price': float(h.price) if h.price else 0, 'contact': h.contact or '', 'available': h.available})
    return JsonResponse(results, safe=False)


@require_http_methods(["GET"])
def api_hostel_detail(request, id):
    hostel = get_object_or_404(Hostel, id=id)
    rooms = Room.objects.filter(hostel=hostel)
    cover = hostel.images.filter(is_cover=True).first()
    rooms_data = [{'id': str(r.id), 'room_number': r.room_number, 'room_name': r.room_name, 'room_type': r.room_type, 'capacity': r.capacity, 'price_per_night': str(r.price_per_night), 'description': r.description, 'private_bathroom': r.private_bathroom, 'air_conditioning': r.air_conditioning, 'wifi': r.wifi, 'status': r.status} for r in rooms]
    return JsonResponse({'id': str(hostel.id), 'name': hostel.name, 'description': hostel.description, 'address': hostel.address, 'city': hostel.city, 'country': hostel.country, 'phone': hostel.phone, 'email': hostel.email, 'latitude': str(hostel.latitude) if hostel.latitude else None, 'longitude': str(hostel.longitude) if hostel.longitude else None, 'image_url': cover.image_url if cover else None, 'rooms': rooms_data, 'facilities': [{'name': f.facility_name} for f in hostel.facilities.all()]})


@require_http_methods(["GET"])
def api_cities(request):
    return JsonResponse(sorted(Hostel.objects.values_list('city', flat=True).exclude(city='').distinct()), safe=False)


@require_http_methods(["GET"])
def api_countries(request):
    return JsonResponse(sorted(Hostel.objects.values_list('country', flat=True).exclude(country='').distinct()), safe=False)


@require_http_methods(["GET", "POST"])
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html', {'form': UserLoginForm()})
    form = UserLoginForm(request.POST)
    if form.is_valid():
        from django.contrib.auth import authenticate, login as auth_login
        user = authenticate(request, username=form.cleaned_data['email'], password=form.cleaned_data['password'])
        if user:
            auth_login(request, user)
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
            except: pass
            messages.success(request, 'Account created! Please check your email to confirm.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


def cookie_policy(request): return render(request, 'cookie_policy.html')
def privacy_policy(request): return render(request, 'privacy_policy.html')
def terms_of_use(request): return render(request, 'terms_of_use.html')
def ai_assistant(request): return render(request, 'ai_assistant.html')
def how_it_works(request): return render(request, 'how_it_works.html')


@require_http_methods(["GET"])
def admin_messages(request):
    if not request.user.is_authenticated: return JsonResponse({'error': 'Auth required'}, status=401)
    msgs = ContactMessage.objects.all()[:100]
    return JsonResponse({'messages': [{'id': msg.id, 'full_name': msg.full_name, 'email': msg.email, 'subject': msg.subject, 'message': msg.message, 'created_at': msg.created_at.isoformat(), 'is_read': msg.is_read} for msg in msgs]})


@require_http_methods(["GET", "POST"])
def get_user(request):
    if request.user.is_authenticated:
        p = getattr(request.user, 'profile', None)
        return JsonResponse({'id': request.user.id, 'email': request.user.email, 'first_name': request.user.first_name, 'last_name': request.user.last_name, 'profile_image_url': p.profile_photo if p else None, 'role': p.role if p else 'customer', 'full_name': p.full_name if p else ''})
    return JsonResponse({'error': 'Not authenticated'}, status=401)


@require_http_methods(["POST"])
def create_booking(request):
    if not request.user.is_authenticated: return JsonResponse({'error': 'Auth required'}, status=401)
    try:
        data = json.loads(request.body)
        room = get_object_or_404(Room, id=data.get('room_id'))
        from datetime import datetime
        check_in = datetime.strptime(data.get('check_in'), '%Y-%m-%d').date()
        check_out = datetime.strptime(data.get('check_out'), '%Y-%m-%d').date()
        guests = int(data.get('guests', 1))
        nights = (check_out - check_in).days
        if nights <= 0: return JsonResponse({'error': 'Invalid date range'}, status=400)
        total_price = room.price_per_night * nights
        booking = Booking.objects.create(hostel_id=room.hostel_id, room=room, customer_id=request.user.id, check_in=check_in, check_out=check_out, guests=guests, nights=nights, total_price=total_price, special_requests=data.get('special_requests', ''), booking_status='Pending', payment_status='Pending')
        Notification.objects.create(user=request.user, title='Booking Created', message=f'Your booking at {room.hostel.name} (Ref: {booking.booking_reference}) has been created.')
        return JsonResponse({'id': str(booking.id), 'booking_reference': booking.booking_reference, 'hostel_id': str(booking.hostel_id), 'room_id': str(booking.room_id), 'check_in': booking.check_in.isoformat(), 'check_out': booking.check_out.isoformat(), 'guests': booking.guests, 'nights': booking.nights, 'total_price': str(booking.total_price), 'booking_status': booking.booking_status, 'payment_status': booking.payment_status, 'special_requests': booking.special_requests}, status=201)
    except Exception as e: return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["GET"])
def get_booking_by_id(request, id):
    try:
        booking = get_object_or_404(Booking, id=id)
        if request.user.id == booking.customer_id:
            return JsonResponse({'id': str(booking.id), 'booking_reference': booking.booking_reference, 'hostel_id': str(booking.hostel_id), 'room_id': str(booking.room_id), 'check_in': booking.check_in.isoformat(), 'check_out': booking.check_out.isoformat(), 'guests': booking.guests, 'nights': booking.nights, 'total_price': str(booking.total_price), 'booking_status': booking.booking_status, 'payment_status': booking.payment_status, 'special_requests': booking.special_requests})
        return JsonResponse({'error': 'Not authorized'}, status=403)
    except Exception as e: return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
def create_message(request):
    try:
        data = json.loads(request.body)
        hostel = get_object_or_404(Hostel, id=data.get('hostelId'))
        msg = Message.objects.create(hostel=hostel, user=request.user if request.user.is_authenticated else None, full_name=data.get('fullName', ''), email=data.get('email', ''), phone=data.get('phone', ''), subject=data.get('subject', ''), content=data.get('content', '') or data.get('message', ''))
        return JsonResponse({'id': str(msg.id), 'hostel_id': str(msg.hostel_id), 'full_name': msg.full_name, 'email': msg.email, 'phone': msg.phone, 'subject': msg.subject, 'message': msg.content, 'created_at': msg.created_at.isoformat()}, status=201)
    except Exception as e: return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def ai_chat(request):
    try:
        data = json.loads(request.body)
        question = data.get('question', '').strip()
        if not question: return JsonResponse({'error': 'Question is required.'}, status=400)
        api_key = os.getenv('GOOGLE_GENERATIVE_API_KEY')
        if api_key:
            try:
                prompt = f'You are a helpful hostel assistant for EHostelFinder. Be friendly, concise, and helpful. Question: {question}'
                payload = json.dumps({'contents': [{'parts': [{'text': prompt}]}]}).encode('utf-8')
                url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}'
                req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'}, method='POST')
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return JsonResponse(json.loads(resp.read().decode('utf-8')))
            except: pass
        return JsonResponse({'candidates': [{'content': {'parts': [{'text': get_local_ai_response(question)}]}}]})
    except Exception as e: return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_messages_by_hostel(request, hostel_id):
    try:
        msgs = Message.objects.filter(hostel_id=hostel_id)
        return JsonResponse([{'id': str(m.id), 'hostel_id': str(m.hostel_id), 'full_name': m.full_name, 'email': m.email, 'phone': m.phone, 'subject': m.subject, 'message': m.content, 'created_at': m.created_at.isoformat()} for m in msgs], safe=False)
    except Exception as e: return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def universities(request):
    university_options = get_university_options()
    universities_data = []
    for uni in university_options:
        name = uni['name']
        count = Hostel.objects.filter(university=name).count()
        top = Hostel.objects.filter(university=name).order_by('-rating').first()
        universities_data.append({'name': name, 'count': count, 'top_hostel': top.name if top else '', 'rating': float(top.rating) if top and top.rating else 0})
    universities_data.sort(key=lambda x: x['name'])
    return render(request, 'universities.html', {'universities': universities_data})


@csrf_exempt
def contact(request):
    if request.method == 'POST':
        try:
            ContactMessage.objects.create(full_name=request.POST.get('name', ''), email=request.POST.get('email', ''), subject=request.POST.get('subject', ''), message=request.POST.get('message', ''))
            return JsonResponse({'success': True, 'message': 'Message sent successfully!'})
        except Exception as e: return JsonResponse({'error': str(e)}, status=400)
    return render(request, 'contact.html')


def google_auth(request):
    import urllib.parse
    from django.conf import settings
    redirect_uri = request.build_absolute_uri('/api/auth/google/callback/')
    params = {'client_id': settings.GOOGLE_CLIENT_ID, 'redirect_uri': redirect_uri, 'response_type': 'code', 'scope': 'email profile', 'access_type': 'online'}
    return redirect(f"https://accounts.google.com/o/oauth2/auth?{urllib.parse.urlencode(params)}")


def google_auth_callback(request):
    import urllib.parse, urllib.request
    from django.conf import settings
    from django.contrib.auth import login as auth_login
    code = request.GET.get('code')
    if not code:
        messages.error(request, 'Google authentication failed')
        return redirect('login')
    redirect_uri = request.build_absolute_uri('/api/auth/google/callback/')
    token_data = urllib.parse.urlencode({'code': code, 'client_id': settings.GOOGLE_CLIENT_ID, 'client_secret': settings.GOOGLE_CLIENT_SECRET, 'redirect_uri': redirect_uri, 'grant_type': 'authorization_code'}).encode()
    try:
        req = urllib.request.Request('https://oauth2.googleapis.com/token', data=token_data, method='POST')
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        with urllib.request.urlopen(req, timeout=10) as resp:
            token_result = json.loads(resp.read().decode())
        access_token = token_result.get('access_token')
        user_req = urllib.request.Request(f'https://www.googleapis.com/oauth2/v2/userinfo?access_token={access_token}')
        with urllib.request.urlopen(user_req, timeout=10) as resp:
            user_info = json.loads(resp.read().decode())
        email = user_info.get('email')
        first_name = user_info.get('given_name', '')
        last_name = user_info.get('family_name', '')
        try: user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create(id=str(uuid.uuid4()), email=email, first_name=first_name or email.split('@')[0], last_name=last_name, provider='google')
        auth_login(request, user)
        return redirect('home')
    except Exception as e:
        messages.error(request, 'Google authentication failed')
        return redirect('login')


def manager_dashboard(request):
    if not request.user.is_authenticated: return redirect('login')
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'manager':
        messages.error(request, 'Access denied.'); return redirect('home')
    hostel = profile.hostel
    if not hostel:
        messages.error(request, 'No hostel assigned.'); return redirect('home')
    return render(request, 'manager/dashboard.html', {'hostel': hostel})


@login_required
def admin_manager_assign(request):
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'admin':
        messages.error(request, 'Access denied.'); return redirect('home')
    return render(request, 'admin/manager_assign.html')


@login_required
@require_http_methods(["GET", "POST"])
def hostel_upload(request):
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'admin':
        messages.error(request, 'Access denied.'); return redirect('home')
    if request.method == 'POST':
        form = HostelUploadForm(request.POST)
        if form.is_valid():
            hostel = Hostel.objects.create(name=form.cleaned_data['name'], description=form.cleaned_data['description'] or '', address=form.cleaned_data['address'], city=form.cleaned_data['city'], country=form.cleaned_data.get('country') or 'Uganda', university=form.cleaned_data['university'] or '', distance='Near campus', price=form.cleaned_data['price_single'] or 0, rating=form.cleaned_data['rating'] or 0, amenities=[item.strip() for item in form.cleaned_data['amenities'].split(',') if item.strip()], image_url=form.cleaned_data['image_url'] or '')
            room_types = [('Single', form.cleaned_data['price_single'], request.POST.get('room_available_single')), ('Double', form.cleaned_data['price_double'], request.POST.get('room_available_double')), ('Triple', form.cleaned_data['price_triple'], request.POST.get('room_available_triple')), ('Quadruple', form.cleaned_data['price_quadruple'], request.POST.get('room_available_quadruple'))]
            for index, (room_type, price, is_avail) in enumerate(room_types, start=1):
                if price is None or price == 0: continue
                capacity = 1 if room_type == 'Single' else 2 if room_type == 'Double' else 3 if room_type == 'Triple' else 4
                Room.objects.create(hostel=hostel, room_number=str(index), room_name=f'{room_type} Room', room_type=room_type, capacity=capacity, available_quantity=1, price_per_night=price, is_available=is_avail == 'on')
            messages.success(request, 'Hostel created successfully.')
            return redirect('hostel_upload')
    else:
        form = HostelUploadForm()
    return render(request, 'admin/hostel_upload.html', {'form': form})


@require_http_methods(["GET"])
def manager_bookings(request):
    if not request.user.is_authenticated: return JsonResponse({'error': 'Auth required'}, status=401)
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'manager': return JsonResponse({'error': 'Access denied'}, status=403)
    hostel = profile.hostel
    if not hostel: return JsonResponse({'error': 'No hostel assigned'}, status=400)
    bookings = Booking.objects.filter(hostel=hostel).select_related('customer', 'room').order_by('-booked_at')
    return JsonResponse([{'id': str(b.id), 'booking_reference': b.booking_reference, 'customer_name': b.customer.get_full_name() or b.customer.email, 'customer_email': b.customer.email, 'room_number': b.room.room_number, 'room_name': b.room.room_name, 'check_in': b.check_in.isoformat(), 'check_out': b.check_out.isoformat(), 'guests': b.guests, 'nights': b.nights, 'total_price': str(b.total_price), 'booking_status': b.booking_status, 'payment_status': b.payment_status, 'special_requests': b.special_requests or ''} for b in bookings], safe=False)


@require_http_methods(["POST"])
def manager_update_booking(request, booking_id):
    if not request.user.is_authenticated: return JsonResponse({'error': 'Auth required'}, status=401)
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'manager': return JsonResponse({'error': 'Access denied'}, status=403)
    hostel = profile.hostel
    if not hostel: return JsonResponse({'error': 'No hostel assigned'}, status=400)
    try:
        data = json.loads(request.body)
        booking = get_object_or_404(Booking, id=booking_id, hostel=hostel)
        status = data.get('booking_status')
        if status and status in dict(BookingStatus.choices).keys():
            booking.booking_status = status
            booking.save(update_fields=['booking_status'])
        return JsonResponse({'success': True})
    except Exception as e: return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["GET", "POST"])
def manager_checkins(request):
    if not request.user.is_authenticated: return JsonResponse({'error': 'Auth required'}, status=401)
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'manager': return JsonResponse({'error': 'Access denied'}, status=403)
    hostel = profile.hostel
    if not hostel: return JsonResponse({'error': 'No hostel assigned'}, status=400)
    if request.method == 'GET':
        bookings = Booking.objects.filter(hostel=hostel, booking_status='Checked In').select_related('customer', 'room')
        return JsonResponse([{'id': str(b.id), 'booking_reference': b.booking_reference, 'customer_name': b.customer.get_full_name() or b.customer.email, 'customer_email': b.customer.email, 'room_number': b.room.room_number, 'room_name': b.room.room_name, 'check_in': b.check_in.isoformat(), 'check_out': b.check_out.isoformat(), 'guests': b.guests, 'total_price': str(b.total_price)} for b in bookings], safe=False)


@require_http_methods(["GET", "POST"])
def manager_rooms(request):
    if not request.user.is_authenticated: return JsonResponse({'error': 'Auth required'}, status=401)
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'manager': return JsonResponse({'error': 'Access denied'}, status=403)
    hostel = profile.hostel
    if not hostel: return JsonResponse({'error': 'No hostel assigned'}, status=400)
    if request.method == 'GET':
        rooms = Room.objects.filter(hostel=hostel)
        return JsonResponse([{'id': str(r.id), 'room_number': r.room_number, 'room_name': r.room_name, 'room_type': r.room_type, 'capacity': r.capacity, 'available_quantity': r.available_quantity, 'price_per_night': str(r.price_per_night), 'status': r.status, 'is_available': r.is_available} for r in rooms], safe=False)
    try:
        data = json.loads(request.body)
        room_id = data.get('room_id')
        room = get_object_or_404(Room, id=room_id, hostel=hostel)
        status = data.get('status')
        if status and status in dict(RoomStatus.choices).keys():
            room.status = status; room.is_available = status == 'Available'
        if data.get('is_available') is not None:
            room.is_available = data.get('is_available') in [True, 'true']
        if data.get('available_quantity') is not None:
            room.available_quantity = int(data.get('available_quantity'))
        room.save()
        return JsonResponse({'success': True})
    except Exception as e: return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def admin_assign_manager(request):
    if not request.user.is_authenticated: return JsonResponse({'error': 'Auth required'}, status=401)
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'admin': return JsonResponse({'error': 'Access denied'}, status=403)
    try:
        data = json.loads(request.body)
        manager_id, hostel_id = data.get('manager_id'), data.get('hostel_id')
        if not manager_id or not hostel_id: return JsonResponse({'error': 'manager_id and hostel_id required'}, status=400)
        manager_profile = get_object_or_404(Profile, id=manager_id, role='manager')
        hostel = get_object_or_404(Hostel, id=hostel_id)
        manager_profile.hostel = hostel; manager_profile.save()
        return JsonResponse({'success': True, 'message': f'Manager {manager_profile.full_name} assigned to {hostel.name}'})
    except Exception as e: return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["POST"])
def admin_remove_manager(request):
    if not request.user.is_authenticated: return JsonResponse({'error': 'Auth required'}, status=401)
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'admin': return JsonResponse({'error': 'Access denied'}, status=403)
    try:
        data = json.loads(request.body)
        manager_id = data.get('manager_id')
        if not manager_id: return JsonResponse({'error': 'manager_id required'}, status=400)
        manager_profile = get_object_or_404(Profile, id=manager_id, role='manager')
        manager_profile.hostel = None; manager_profile.save()
        return JsonResponse({'success': True})
    except Exception as e: return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["GET"])
def api_managers(request):
    if not request.user.is_authenticated: return JsonResponse({'error': 'Auth required'}, status=401)
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'admin': return JsonResponse({'error': 'Access denied'}, status=403)
    managers = Profile.objects.filter(role='manager').select_related('hostel')
    return JsonResponse([{'id': str(m.id), 'full_name': m.full_name, 'email': m.email, 'hostel_id': str(m.hostel_id) if m.hostel else None, 'hostel_name': m.hostel.name if m.hostel else None} for m in managers], safe=False)


@csrf_exempt
@require_http_methods(["POST"])
def admin_create_manager(request):
    if not request.user.is_authenticated: return JsonResponse({'error': 'Auth required'}, status=401)
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'admin': return JsonResponse({'error': 'Access denied'}, status=403)
    try:
        data = json.loads(request.body)
        full_name = data.get('full_name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        password = data.get('password', '')
        if not full_name or not email or not password: return JsonResponse({'error': 'Full name, email, and password required'}, status=400)
        if len(password) < 8: return JsonResponse({'error': 'Password must be at least 8 characters'}, status=400)
        if User.objects.filter(email=email).exists(): return JsonResponse({'error': 'Email already exists'}, status=400)
        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0] if name_parts else full_name
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        user = User.objects.create(id=str(uuid.uuid4()), email=email, first_name=first_name, last_name=last_name, is_email_verified=True)
        user.set_password(password); user.save()
        Profile.objects.create(user=user, full_name=full_name, email=email, phone=phone or None, role='manager')
        return JsonResponse({'success': True, 'message': f'Manager {full_name} created successfully'})
    except Exception as e: return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["GET"])
def api_unassigned_managers(request):
    if not request.user.is_authenticated: return JsonResponse({'error': 'Auth required'}, status=401)
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'admin': return JsonResponse({'error': 'Access denied'}, status=403)
    managers = Profile.objects.filter(role='manager', hostel__isnull=True)
    return JsonResponse([{'id': str(m.id), 'full_name': m.full_name, 'email': m.email} for m in managers], safe=False)


@require_http_methods(["GET"])
def api_hostel_managers(request, hostel_id):
    if not request.user.is_authenticated: return JsonResponse({'error': 'Auth required'}, status=401)
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'admin': return JsonResponse({'error': 'Access denied'}, status=403)
    hostel = get_object_or_404(Hostel, id=hostel_id)
    managers = Profile.objects.filter(role='manager', hostel=hostel)
    return JsonResponse([{'id': str(m.id), 'full_name': m.full_name, 'email': m.email} for m in managers], safe=False)


@require_http_methods(["POST"])
def manager_checkout(request, booking_id):
    if not request.user.is_authenticated: return JsonResponse({'error': 'Auth required'}, status=401)
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'manager': return JsonResponse({'error': 'Access denied'}, status=403)
    hostel = profile.hostel
    if not hostel: return JsonResponse({'error': 'No hostel assigned'}, status=400)
    try:
        booking = get_object_or_404(Booking, id=booking_id, hostel=hostel)
        booking.booking_status = 'Checked Out'; booking.save()
        return JsonResponse({'success': True})
    except Exception as e: return JsonResponse({'error': str(e)}, status=400)


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
            except User.DoesNotExist: pass
            messages.success(request, 'If an account with that email exists, a reset link has been sent.')
            return redirect('login')
    else: form = ForgotPasswordForm()
    return render(request, 'forgot_password.html', {'form': form})


@require_http_methods(["GET", "POST"])
def reset_password(request, token):
    from .models import PasswordResetToken
    try: reset_token = PasswordResetToken.objects.select_related('user').get(token=token)
    except PasswordResetToken.DoesNotExist:
        return render(request, 'password_reset_status.html', {'status': 'invalid', 'message': 'Invalid reset link.'})
    if reset_token.is_expired:
        return render(request, 'password_reset_status.html', {'status': 'expired', 'message': 'This reset link has expired.'})
    if reset_token.is_used:
        return render(request, 'password_reset_status.html', {'status': 'used', 'message': 'This link has already been used.'})
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user = reset_token.user
            user.set_password(form.cleaned_data['new_password']); user.save()
            reset_token.used_at = timezone.now(); reset_token.save()
            messages.success(request, 'Your password has been reset.'); return redirect('login')
    else: form = ResetPasswordForm()
    return render(request, 'reset_password.html', {'form': form, 'token': token})


@login_required
def profile(request):
    user = request.user
    profile_obj = getattr(user, 'profile', None)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=profile_obj)
        if form.is_valid():
            form.save()
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.save(update_fields=['first_name', 'last_name'])
            messages.success(request, 'Profile updated successfully'); return redirect('profile')
    else: form = ProfileUpdateForm(instance=profile_obj)
    return render(request, 'profile.html', {'form': form, 'profile': profile_obj})


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(customer=request.user).select_related('hostel', 'room').order_by('-booked_at')
    return render(request, 'my_bookings.html', {'bookings': bookings})


# FAVORITES
@login_required
@require_http_methods(["POST"])
def toggle_favorite(request):
    try:
        data = json.loads(request.body)
        hostel = get_object_or_404(Hostel, id=data.get('hostel_id'))
        fav, created = Favorite.objects.get_or_create(customer=request.user, hostel=hostel)
        if not created: fav.delete(); return JsonResponse({'favorited': False})
        return JsonResponse({'favorited': True})
    except Exception as e: return JsonResponse({'error': str(e)}, status=400)


@login_required
def my_favorites(request):
    favorites = Favorite.objects.filter(customer=request.user).select_related('hostel')
    return render(request, 'my_favorites.html', {'favorites': favorites})


# BOOKING CANCELLATION
@login_required
@require_http_methods(["POST"])
def cancel_booking(request, booking_id):
    try:
        booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
        if booking.booking_status in ['Checked In', 'Checked Out']:
            return JsonResponse({'error': 'Cannot cancel an active or completed booking'}, status=400)
        if booking.booking_status == 'Cancelled':
            return JsonResponse({'error': 'Booking is already cancelled'}, status=400)
        booking.booking_status = 'Cancelled'; booking.payment_status = 'Refunded'
        booking.save(update_fields=['booking_status', 'payment_status'])
        Notification.objects.create(user=request.user, title='Booking Cancelled', message=f'Booking {booking.booking_reference} cancelled.')
        return JsonResponse({'success': True, 'message': 'Booking cancelled successfully'})
    except Exception as e: return JsonResponse({'error': str(e)}, status=400)


# NOTIFICATIONS
@login_required
def view_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    return render(request, 'notifications.html', {'notifications': notifications, 'unread_count': unread_count})


@login_required
@require_http_methods(["GET"])
def api_notifications(request):
    notifications = Notification.objects.filter(user=request.user).orderThe file has basic functions but is missing ~30 remaining functions. Let me complete it by writing a Python script file and executing it to append all remaining functions:

<create_file>
<absolute_path>c:/Users/user/ehostelfinder/append_views.py</absolute_path>
<content>#!/usr/bin/env python3
import os, py_compile
os.chdir(r'c:/Users/user/ehostelfinder')

lines = []

def L(s):
    lines.append(s)

L('')
L('')
L('@require_http_methods(["GET"])')
L('def api_hostels(request):')
L('    city = request.GET.get("city", "")')
L('    country = request.GET.get("country", "")')
L('    room_type = request.GET.get("room_type", "")')
L('    university = request.GET.get("university", "")')
L('    min_price = request.GET.get("min_price", "")')
L('    max_price = request.GET.get("max_price", "")')
L('    hostels = Hostel.objects.all()')
L('    if city: hostels = hostels.filter(city__icontains=city)')
L('    if country: hostels = hostels.filter(country__icontains=country)')
L('    if university: hostels = hostels.filter(university=university)')
L('    if room_type: hostels = hostels.filter(rooms__room_type=room_type).distinct()')
L('    if min_price:')
L('        try: hostels = hostels.filter(price__gte=float(min_price)).distinct()')
L('        except ValueError: pass')
L('    if max_price:')
L('        try: hostels = hostels.filter(price__lte=float(max_price)).distinct()')
L('        except ValueError: pass')
L('    results = []')
L('    for h in hostels:')
L('        cover = h.images.filter(is_cover=True).first()')
L('        results.append({')
L('            "id": str(h.id), "name": h.name, "city": h.city, "country": h.country,')
L('            "university": h.university, "address": h.address, "description": h.description,')
L('            "average_rating": round(float(h.average_rating), 2),')
L('            "rating": float(h.rating) if h.rating else round(float(h.average_rating), 2),')
L('            "review_count": h.reviews.count(),')
L('            "image_url": h.image_url or (cover.image_url if cover else None),')
L('            "facilities": [f.facility_name for f in h.facilities.all()],')
L('            "amenities": h.amenities or [],')
L('            "distance": h.distance or "", "price": float(h.price) if h.price else 0,')
L('            "contact": h.contact or "", "available": h.available,')
L('        })')
L('    return JsonResponse(results, safe=False)')
L('')
L('')
L('@require_http_methods(["GET"])')
L('def api_hostel_detail(request, id):')
L('    hostel = get_object_or_404(Hostel, id=id)')
L('    rooms = Room.objects.filter(hostel=hostel)')
L('    cover = hostel.images.filter(is_cover=True).first()')
L('    rooms_data = [{"id": str(r.id), "room_number": r.room_number, "room_name": r.room_name, "room_type": r.room_type, "capacity": r.capacity, "price_per_night": str(r.price_per_night), "description": r.description, "private_bathroom": r.private_bathroom, "air_conditioning": r.air_conditioning, "wifi": r.wifi, "status": r.status} for r in rooms]')
L('    return JsonResponse({"id": str(hostel.id), "name": hostel.name, "description": hostel.description, "address": hostel.address, "city": hostel.city, "country": hostel.country, "phone": hostel.phone, "email": hostel.email, "latitude": str(hostel.latitude) if hostel.latitude else None, "longitude": str(hostel.longitude) if hostel.longitude else None, "image_url": cover.image_url if cover else None, "rooms": rooms_data, "facilities": [{"name": f.facility_name} for f in hostel.facilities.all()]})')
L('')
L('')
L('@require_http_methods(["GET"])')
L('def api_cities(request):')
L('    return JsonResponse(sorted(Hostel.objects.values_list("city", flat=True).exclude(city="").distinct()), safe=False)')
L('')
L('')
L('@require_http_methods(["GET"])')
L('def api_countries(request):')
L('    return JsonResponse(sorted(Hostel.objects.values_list("country", flat=True).exclude(country="").distinct()), safe=False)')
L('')
L('')
L('@require_http_methods(["GET", "POST"])')
L('def login(request):')
L('    if request.method == "GET":')
L('        return render(request, "login.html", {"form": UserLoginForm()})')
L('    form = UserLoginForm(request.POST)')
L('    if form.is_valid():')
L('        from django.contrib.auth import authenticate, login as auth_login')
L('        user = authenticate(request, username=form.cleaned_data["email"], password=form.cleaned_data["password"])')
L('        if user:')
L('            auth_login(request, user)')
L('            return redirect("home")')
L('        messages.error(request, "Invalid email or password")')
L('    else:')
L('        messages.error(request, "Invalid email or password")')
L('    return render(request, "login.html", {"form": form})')
L('')
L('')
L('@require_http_methods(["GET", "POST"])')
L('def signup(request):')
L('    if request.method == "POST":')
L('        form = UserRegistrationForm(request.POST)')
L('        if form.is_valid():')
L('            user = form.save()')
L('            try:')
L('                from .email_utils import send_email_confirmation')
L('                send_email_confirmation(user, request)')
L('            except Exception: pass')
L('            messages.success(request, "Account created! Please check your email to confirm.")')
L('            return redirect("login")')
L('    else: form = UserRegistrationForm()')
L('    return render(request, "signup.html", {"form": form})')
L('')
L('')
L('@require_http_methods(["GET"])')
L('def logout_view(request):')
L('    logout(request); return redirect("home")')
L('')
L('')
L('def cookie_policy(request): return render(request, "cookie_policy.html")')
L('def privacy_policy(request): return render(request, "privacy_policy.html")')
L('def terms_of_use(request): return render(request, "terms_of_use.html")')
L('def ai_assistant(request): return render(request, "ai_assistant.html")')
L('def how_it_works(request): return render(request, "how_it_works.html")')
L('')
L('')
L('@require_http_methods(["GET"])')
L('def admin_messages(request):')
L('    if not request.user.is_authenticated: return JsonResponse({"error": "Auth required"}, status=401)')
L('    msgs = ContactMessage.objects.all()[:100]')
L('    return JsonResponse({"messages": [{"id": msg.id, "full_name": msg.full_name, "email": msg.email, "subject": msg.subject, "message": msg.message, "created_at": msg.created_at.isoformat(), "is_read": msg.is_read} for msg in msgs]})')
L('')
L('')
L('@require_http_methods(["GET", "POST"])')
L('def get_user(request):')
L('    if request.user.is_authenticated:')
L('        p = getattr(request.user, "profile", None)')
L('        return JsonResponse({"id": request.user.id, "email": request.user.email, "first_name": request.user.first_name, "last_name": request.user.last_name, "profile_image_url": p.profile_photo if p else None, "role": p.role if p else "customer", "full_name": p.full_name if p else ""})')
L('    return JsonResponse({"error": "Not authenticated"}, status=401)')
L('')
L('')
L('@require_http_methods(["POST"])')
L('def create_booking(request):')
L('    if not request.user.is_authenticated: return JsonResponse({"error": "Auth required"}, status=401)')
L('    try:')
L('        data = json.loads(request.body)')
L('        room = get_object_or_404(Room, id=data.get("room_id"))')
L('        from datetime import datetime')
L('        check_in = datetime.strptime(data.get("check_in"), "%Y-%m-%d").date()')
L('        check_out = datetime.strptime(data.get("check_out"), "%Y-%m-%d").date()')
L('        guests = int(data.get("guests", 1))')
L('        nights = (check_out - check_in).days')
L('        if nights <= 0: return JsonResponse({"error": "Invalid date range"}, status=400)')
L('        total_price = room.price_per_night * nights')
L('        booking = Booking.objects.create(hostel_id=room.hostel_id, room=room, customer_id=request.user.id, check_in=check_in, check_out=check_out, guests=guests, nights=nights, total_price=total_price, special_requests=data.get("special_requests", ""), booking_status="Pending", payment_status="Pending")')
L('        Notification.objects.create(user=request.user, title="Booking Created", message=f"Booking at {room.hostel.name} (Ref: {booking.booking_reference}) created.")')
L('        return JsonResponse({"id": str(booking.id), "booking_reference": booking.booking_reference, "hostel_id": str(booking.hostel_id), "room_id": str(booking.room_id), "check_in": booking.check_in.isoformat(), "check_out": booking.check_out.isoformat(), "guests": booking.guests, "nights": booking.nights, "total_price": str(booking.total_price), "booking_status": booking.booking_status, "payment_status": booking.payment_status, "special_requests": booking.special_requests}, status=201)')
L('    except Exception as e: return JsonResponse({"error": str(e)}, status=400)')
L('')
L('')
L('@require_http_methods(["GET"])')
L('def get_booking_by_id(request, id):')
L('    try:')
L('        booking = get_object_or_404(Booking, id=id)')
L('        if request.user.id == booking.customer_id:')
L('            return JsonResponse({"id": str(booking.id), "booking_reference": booking.booking_reference, "hostel_id": str(booking.hostel_id), "room_id": str(booking.room_id), "check_in": booking.check_in.isoformat(), "check_out": booking.check_out.isoformat(), "guests": booking.guests, "nights": booking.nights, "total_price": str(booking.total_price), "booking_status": booking.booking_status, "payment_status": booking.payment_status, "special_requests": booking.special_requests})')
L('        return JsonResponse({"error": "Not authorized"}, status=403)')
L('    except Exception as e: return JsonResponse({"error": str(e)}, status=500)')
L('')
L('')
L('@require_http_methods(["POST"])')
L('def create_message(request):')
L('    try:')
L('        data = json.loads(request.body)')
L('        hostel = get_object_or_404(Hostel, id=data.get("hostelId"))')
L('        msg = Message.objects.create(hostel=hostel, user=request.user if request.user.is_authenticated else None, full_name=data.get("fullName", ""), email=data.get("email", ""), phone=data.get("phone", ""), subject=data.get("subject", ""), content=data.get("content", "") or data.get("message", ""))')
L('        return JsonResponse({"id": str(msg.id), "hostel_id": str(msg.hostel_id), "full_name": msg.full_name, "email": msg.email, "subject": msg.subject, "message": msg.content, "created_at": msg.created_at.isoformat()
