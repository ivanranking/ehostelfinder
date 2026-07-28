#!/usr/bin/env python3
"""Rebuild hostels/views.py from scratch with all required view functions."""
import os, ast, re

os.chdir(r'c:\Users\user\ehostelfinder')

# First run gen_views.py and gen_views_p2.py to get base functions
exec(compile(open('gen_views.py', 'r', encoding='utf-8').read(), 'gen_views.py', 'exec'))
exec(compile(open('gen_views_p2.py', 'r', encoding='utf-8').read(), 'gen_views_p2.py', 'exec'))

# Now read the produced file
with open('hostels/views.py', 'r', encoding='utf-8') as f:
    existing = f.read()

lines = existing.rstrip().split('\n')
if lines and lines[-1] == '':
    lines.pop()

indent = 0
def w(s):
    if indent:
        lines.append('    ' * indent + s)
    else:
        lines.append(s)
def i(n=1):
    global indent; indent += n
def d(n=1):
    global indent; indent -= n

# ===== API Endpoints =====
w('')
w('@require_http_methods(["GET"])')
w('def api_hostels(request):')
i()
w('city = request.GET.get("city", "")')
w('country = request.GET.get("country", "")')
w('room_type = request.GET.get("room_type", "")')
w('university = request.GET.get("university", "")')
w('min_price = request.GET.get("min_price", "")')
w('max_price = request.GET.get("max_price", "")')
w('hostels = Hostel.objects.all()')
w('if city: hostels = hostels.filter(city__icontains=city)')
w('if country: hostels = hostels.filter(country__icontains=country)')
w('if university: hostels = hostels.filter(university=university)')
w('if room_type: hostels = hostels.filter(rooms__room_type=room_type).distinct()')
w('if min_price:')
i()
w('try: hostels = hostels.filter(price__gte=float(min_price)).distinct()')
w('except: pass')
d()
w('if max_price:')
i()
w('try: hostels = hostels.filter(price__lte=float(max_price)).distinct()')
w('except: pass')
d()
w('results = []')
w('for h in hostels:')
i()
w('cover = h.images.filter(is_cover=True).first()')
w('results.append({"id": str(h.id), "name": h.name, "city": h.city, "country": h.country, "university": h.university, "address": h.address, "description": h.description, "average_rating": round(float(h.average_rating), 2), "rating": float(h.rating) if h.rating else round(float(h.average_rating), 2), "review_count": h.reviews.count(), "image_url": h.image_url or (cover.image_url if cover else None), "facilities": [f.facility_name for f in h.facilities.all()], "amenities": h.amenities or [], "distance": h.distance or "", "price": float(h.price) if h.price else 0, "contact": h.contact or "", "available": h.available})')
d()
w('return JsonResponse(results, safe=False)')
d()

w('')
w('@require_http_methods(["GET"])')
w('def api_hostel_detail(request, id):')
i()
w('hostel = get_object_or_404(Hostel, id=id)')
w('rooms = Room.objects.filter(hostel=hostel)')
w('cover = hostel.images.filter(is_cover=True).first()')
w('rooms_data = [{"id": str(r.id), "room_number": r.room_number, "room_name": r.room_name, "room_type": r.room_type, "capacity": r.capacity, "price_per_night": str(r.price_per_night), "description": r.description, "private_bathroom": r.private_bathroom, "air_conditioning": r.air_conditioning, "wifi": r.wifi, "status": r.status} for r in rooms]')
w('return JsonResponse({"id": str(hostel.id), "name": hostel.name, "description": hostel.description, "address": hostel.address, "city": hostel.city, "country": hostel.country, "phone": hostel.phone, "email": hostel.email, "latitude": str(hostel.latitude) if hostel.latitude else None, "longitude": str(hostel.longitude) if hostel.longitude else None, "image_url": cover.image_url if cover else None, "rooms": rooms_data, "facilities": [{"name": f.facility_name} for f in hostel.facilities.all()]})')
d()

w('')
w('@require_http_methods(["GET"])')
w('def api_cities(request):')
i()
w('return JsonResponse(sorted(Hostel.objects.values_list("city", flat=True).exclude(city="").distinct()), safe=False)')
d()

w('')
w('@require_http_methods(["GET"])')
w('def api_countries(request):')
i()
w('return JsonResponse(sorted(Hostel.objects.values_list("country", flat=True).exclude(country="").distinct()), safe=False)')
d()

# ===== AUTH =====
w('')
w('@require_http_methods(["GET", "POST"])')
w('def login(request):')
i()
w('if request.method == "GET":')
i()
w('return render(request, "login.html", {"form": UserLoginForm()})')
d()
w('form = UserLoginForm(request.POST)')
w('if form.is_valid():')
i()
w('from django.contrib.auth import authenticate, login as auth_login')
w('user = authenticate(request, username=form.cleaned_data["email"], password=form.cleaned_data["password"])')
w('if user:')
i()
w('auth_login(request, user)')
w('return redirect("home")')
d()
w('messages.error(request, "Invalid email or password")')
d()
w('else:')
i()
w('messages.error(request, "Invalid email or password")')
d()
w('return render(request, "login.html", {"form": form})')
d()

w('')
w('@require_http_methods(["GET", "POST"])')
w('def signup(request):')
i()
w('if request.method == "POST":')
i()
w('form = UserRegistrationForm(request.POST)')
w('if form.is_valid():')
i()
w('user = form.save()')
w('try:')
i()
w('from .email_utils import send_email_confirmation')
w('send_email_confirmation(user, request)')
d()
w('except: pass')
w('messages.success(request, "Account created! Please check your email to confirm.")')
w('return redirect("login")')
d()
d()
w('else:')
i()
w('form = UserRegistrationForm()')
d()
w('return render(request, "signup.html", {"form": form})')
d()

w('')
w('@require_http_methods(["GET"])')
w('def logout_view(request):')
i()
w('logout(request)')
w('return redirect("home")')
d()

# ===== STATIC PAGES =====
w('')
w('def cookie_policy(request):')
i()
w('return render(request, "cookie_policy.html")')
d()

w('')
w('def privacy_policy(request):')
i()
w('return render(request, "privacy_policy.html")')
d()

w('')
w('def terms_of_use(request):')
i()
w('return render(request, "terms_of_use.html")')
d()

w('')
w('def ai_assistant(request):')
i()
w('return render(request, "ai_assistant.html")')
d()

w('')
w('def how_it_works(request):')
i()
w('return render(request, "how_it_works.html")')
d()

w('')
w('@require_http_methods(["GET"])')
w('def admin_messages(request):')
i()
w('if not request.user.is_authenticated:')
i()
w('return JsonResponse({"error": "Auth required"}, status=401)')
d()
w('msgs = ContactMessage.objects.all()[:100]')
w('return JsonResponse({"messages": [{"id": msg.id, "full_name": msg.full_name, "email": msg.email, "subject": msg.subject, "message": msg.message, "created_at": msg.created_at.isoformat(), "is_read": msg.is_read} for msg in msgs]})')
d()

w('')
w('@require_http_methods(["GET", "POST"])')
w('def get_user(request):')
i()
w('if request.user.is_authenticated:')
i()
w('p = getattr(request.user, "profile", None)')
w('return JsonResponse({"id": request.user.id, "email": request.user.email, "first_name": request.user.first_name, "last_name": request.user.last_name, "profile_image_url": p.profile_photo if p else None, "role": p.role if p else "customer", "full_name": p.full_name if p else ""})')
d()
w('return JsonResponse({"error": "Not authenticated"}, status=401)')
d()

# ===== Booking =====
w('')
w('@require_http_methods(["POST"])')
w('def create_booking(request):')
i()
w('if not request.user.is_authenticated:')
i()
w('return JsonResponse({"error": "Auth required"}, status=401)')
d()
w('try:')
i()
w('data = json.loads(request.body)')
w('room = get_object_or_404(Room, id=data.get("room_id"))')
w('from datetime import datetime')
w('check_in = datetime.strptime(data.get("check_in"), "%Y-%m-%d").date()')
w('check_out = datetime.strptime(data.get("check_out"), "%Y-%m-%d").date()')
w('guests = int(data.get("guests", 1))')
w('nights = (check_out - check_in).days')
w('if nights <= 0:')
i()
w('return JsonResponse({"error": "Invalid date range"}, status=400)')
d()
w('total_price = room.price_per_night * nights')
w('booking = Booking.objects.create(hostel_id=room.hostel_id, room=room, customer=request.user, check_in=check_in, check_out=check_out, guests=guests, nights=nights, total_price=total_price, special_requests=data.get("special_requests", ""), booking_status="Pending", payment_status="Pending")')
w('Notification.objects.create(user=request.user, title="Booking Created", message=f"Booking at {room.hostel.name} (Ref: {booking.booking_reference}) created.")')
w('return JsonResponse({"id": str(booking.id), "booking_reference": booking.booking_reference, "hostel_id": str(booking.hostel_id), "room_id": str(booking.room_id), "check_in": booking.check_in.isoformat(), "check_out": booking.check_out.isoformat(), "guests": booking.guests, "nights": booking.nights, "total_price": str(booking.total_price), "booking_status": booking.booking_status, "payment_status": booking.payment_status, "special_requests": booking.special_requests}, status=201)')
d()
w('except Exception as e:')
i()
w('return JsonResponse({"error": str(e)}, status=400)')
d()
d()

# ===== Write it out and verify =====
final = '\n'.join(lines)
with open('hostels/views.py', 'w', encoding='utf-8') as f:
    f.write(final)

# Verify
try:
    tree = ast.parse(final)
    funcs = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    print(f'DONE: {len(funcs)} functions generated')
    
    with open('hostels/urls.py', 'r') as f:
        urls = f.read()
    needed = set()
    for m in re.finditer(r'views\.(\w+)', urls):
        needed.add(m.group(1))
    missing = needed - funcs
    if missing:
        print(f'MISSING ({len(missing)}): {sorted(missing)}')
    else:
        print('ALL FUNCTIONS PRESENT!')
except SyntaxError as e:
    print(f'SYNTAX ERROR at line {e.lineno}: {e.msg}')
