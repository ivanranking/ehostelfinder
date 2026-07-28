from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db.models import Avg
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import json, os, urllib.request, urllib.error, uuid, secrets
from .forms import UserRegistrationForm, UserLoginForm, ForgotPasswordForm, ResetPasswordForm, ProfileUpdateForm, HostelUploadForm
from .models import Hostel, User, ContactMessage, Profile, Room, Booking, Review, Favorite, Message, Notification, Payment, RoomStatus, BookingStatus, RoommateRequest, ChatRoom, ChatMessage
from .local_ai import get_local_ai_response

KAMPALA_AREA_UNIVERSITIES = ["Makerere University", "Makerere University Business School", "Kyambogo University", "Kampala International University", "Uganda Christian University", "Ndejje University", "Bugema University", "Cavendish University Uganda", "St. Lawrence University Uganda", "Mutesa I Royal University"]

def get_university_options():
    university_names, seen = [], set()
    def normalize(name):
        if not name: return ""
        n = name.strip().lower()
        if "makerere" in n and "business school" in n: return "Makerere University Business School"
        if "makerere" in n: return "Makerere University"
        return name.strip()
    for name in KAMPALA_AREA_UNIVERSITIES + list(Hostel.objects.exclude(university="").values_list("university", flat=True)):
        if name:
            normalized = normalize(name)
            if normalized.lower() not in seen:
                university_names.append(normalized)
                seen.add(normalized.lower())
    return [{"name": n} for n in university_names]

def home(request):
    university = request.GET.get("university", "All Universities")
    city = request.GET.get("city", "")
    country = request.GET.get("country", "")
    min_price = request.GET.get("min_price", "")
    max_price = request.GET.get("max_price", "")
    sort_by = request.GET.get("sort", "-created_at")
    page = request.GET.get("page", 1)
    valid_sorts = ["name", "-name", "price", "-price", "rating", "-rating", "created_at", "-created_at"]
    if sort_by not in valid_sorts: sort_by = "-created_at"
    hostels = Hostel.objects.all()
    if university and university != "All Universities": hostels = hostels.filter(university=university)
    if city: hostels = hostels.filter(city__icontains=city)
    if country: hostels = hostels.filter(country__icontains=country)
    if min_price:
        try: hostels = hostels.filter(price__gte=float(min_price)).distinct()
        except ValueError: pass
    if max_price:
        try: hostels = hostels.filter(price__lte=float(max_price)).distinct()
        except ValueError: pass
    hostels = hostels.order_by(sort_by)
    paginator = Paginator(hostels, 12)
    try: page_obj = paginator.page(page)
    except: page_obj = paginator.page(1)
    cities_list = sorted(Hostel.objects.values_list("city", flat=True).exclude(city="").distinct())
    countries_list = sorted(Hostel.objects.values_list("country", flat=True).exclude(country="").distinct())
    universities = get_university_options()
    rated_hostels = Hostel.objects.exclude(rating__isnull=True)
    avg_rating = round(sum(float(h.rating) for h in rated_hostels) / rated_hostels.count(), 1) if rated_hostels.exists() else 0.0
    hostel_list = []
    for h in page_obj:
        cover = h.images.filter(is_cover=True).first()
        available_room = h.rooms.filter(status="Available").first()
        hostel_list.append({
        "id": str(h.id), "name": h.name, "description": h.description, "city": h.city, "country": h.country,
        "university": h.university, "image_url": h.image_url or (cover.image_url if cover else None),
        "facilities": [{"name": f.facility_name, "icon": f.icon or ""} for f in h.facilities.all()],
        "available": h.available, "rating": float(h.rating) if h.rating else round(float(h.average_rating), 1),
        "distance": h.distance or "Near campus",
        "price": str(h.price) if h.price else (str(available_room.price_per_night) if available_room else "0"),
        "amenities": h.amenities or [],
        })
    favorite_ids = []
    if request.user.is_authenticated:
        favorite_ids = list(Favorite.objects.filter(customer=request.user).values_list("hostel_id", flat=True))
    return render(request, "home.html", {
    "hostels": hostel_list, "cities": cities_list, "countries": countries_list, "universities": universities,
    "selected_city": city, "selected_country": country, "selected_university": university, "selected_sort": sort_by,
    "total_hostels": Hostel.objects.count(), "total_universities": len(universities), "avg_rating": avg_rating,
    "total_cities": len(cities_list), "page_obj": page_obj, "favorite_ids": [str(fid) for fid in favorite_ids],
    })

def hostel_detail(request, id):
    try:
        hostel = get_object_or_404(Hostel, id=id)
        rooms = Room.objects.filter(hostel=hostel, status="Available")
        images = hostel.images.all()
        cover = hostel.images.filter(is_cover=True).first()
        facilities = hostel.facilities.all()
        reviews = hostel.reviews.select_related("customer").all()
        rooms_data = []
        for r in rooms:
            rooms_data.append({
            "id": str(r.id), "room_number": r.room_number, "room_name": r.room_name,
            "room_type": r.room_type, "capacity": r.capacity, "available_quantity": r.available_quantity,
            "price_per_night": str(r.price_per_night), "floor": r.floor or 1, "description": r.description,
            "private_bathroom": r.private_bathroom, "air_conditioning": r.air_conditioning,
            "balcony": r.balcony, "television": r.television, "wifi": r.wifi,
            "images": [ri.image_url for ri in r.images.all()],
            })
        reviews_data = []
        for rv in reviews:
            reviews_data.append({
            "id": str(rv.id), "customer_name": rv.customer.get_full_name() or rv.customer.email,
            "rating": rv.rating, "comment": rv.comment,
            "created_at": rv.created_at.strftime("%Y-%m-%d"),
            })
        context = {
        "hostel": {
        "id": str(hostel.id), "name": hostel.name, "description": hostel.description,
        "address": hostel.address, "city": hostel.city, "country": hostel.country,
        "university": hostel.university, "distance": hostel.distance or "Near campus",
        "price": float(hostel.price) if hostel.price else 0,
        "rating": float(hostel.rating) if hostel.rating else round(float(hostel.average_rating), 1),
        "available": hostel.available, "contact": hostel.contact or "",
        "amenities": hostel.amenities or [], "phone": hostel.phone, "email": hostel.email,
        "latitude": str(hostel.latitude) if hostel.latitude else None,
        "longitude": str(hostel.longitude) if hostel.longitude else None,
        "cover_image": cover.image_url if cover else None,
        "images": [{"url": img.image_url, "is_cover": img.is_cover} for img in images],
        },
        "rooms": rooms_data,
        "facilities": [{"name": f.facility_name, "icon": f.icon or ""} for f in facilities],
        "reviews": reviews_data,
        }
    except Exception as e:
        print(f"Error in hostel_detail: {e}")
        messages.error(request, "Error loading hostel details")
        return redirect("home")
    if request.method == "POST" and "review_submit" in request.POST:
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to leave a review")
            return redirect("login")
        rating = request.POST.get("rating", "").strip()
        comment = request.POST.get("comment", "").strip()
        if not rating or not rating.isdigit() or int(rating) not in range(1, 6):
            messages.error(request, "Please select a valid rating from 1 to 5.")
            return redirect("hostel_detail", id=hostel.id)
        Review.objects.create(hostel=hostel, customer=request.user, rating=int(rating), comment=comment)
        hostel.review_count = hostel.reviews.count()
        hostel.rating = round(hostel.reviews.aggregate(avg=Avg("rating"))["avg"] or 0, 2)
        hostel.save(update_fields=["review_count", "rating"])
        messages.success(request, "Your review has been submitted successfully.")
        return redirect("hostel_detail", id=hostel.id)
    return render(request, "hostel_detail.html", context)

@require_http_methods(["GET"])
def api_hostels(request):
    city = request.GET.get("city", "")
    country = request.GET.get("country", "")
    room_type = request.GET.get("room_type", "")
    university = request.GET.get("university", "")
    min_price = request.GET.get("min_price", "")
    max_price = request.GET.get("max_price", "")
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
        results.append({"id": str(h.id), "name": h.name, "city": h.city, "country": h.country, "university": h.university, "address": h.address, "description": h.description, "average_rating": round(float(h.average_rating), 2), "rating": float(h.rating) if h.rating else round(float(h.average_rating), 2), "review_count": h.reviews.count(), "image_url": h.image_url or (cover.image_url if cover else None), "facilities": [f.facility_name for f in h.facilities.all()], "amenities": h.amenities or [], "distance": h.distance or "", "price": float(h.price) if h.price else 0, "contact": h.contact or "", "available": h.available})
    return JsonResponse(results, safe=False)

@require_http_methods(["GET"])
def api_hostel_detail(request, id):
    hostel = get_object_or_404(Hostel, id=id)
    rooms = Room.objects.filter(hostel=hostel)
    cover = hostel.images.filter(is_cover=True).first()
    rooms_data = [{"id": str(r.id), "room_number": r.room_number, "room_name": r.room_name, "room_type": r.room_type, "capacity": r.capacity, "price_per_night": str(r.price_per_night), "description": r.description, "private_bathroom": r.private_bathroom, "air_conditioning": r.air_conditioning, "wifi": r.wifi, "status": r.status} for r in rooms]
    return JsonResponse({"id": str(hostel.id), "name": hostel.name, "description": hostel.description, "address": hostel.address, "city": hostel.city, "country": hostel.country, "phone": hostel.phone, "email": hostel.email, "latitude": str(hostel.latitude) if hostel.latitude else None, "longitude": str(hostel.longitude) if hostel.longitude else None, "image_url": cover.image_url if cover else None, "rooms": rooms_data, "facilities": [{"name": f.facility_name} for f in hostel.facilities.all()]})

@require_http_methods(["GET"])
def api_cities(request):
    return JsonResponse(sorted(Hostel.objects.values_list("city", flat=True).exclude(city="").distinct()), safe=False)

@require_http_methods(["GET"])
def api_countries(request):
    return JsonResponse(sorted(Hostel.objects.values_list("country", flat=True).exclude(country="").distinct()), safe=False)

@require_http_methods(["POST"])
def create_message(request):
    try:
        data = json.loads(request.body)
        hostel = get_object_or_404(Hostel, id=data.get("hostelId"))
        msg = Message.objects.create(
            hostel=hostel,
            user=request.user if request.user.is_authenticated else None,
            full_name=data.get("fullName", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            subject=data.get("subject", ""),
            content=data.get("content", "") or data.get("message", "")
        )
        return JsonResponse({"id": str(msg.id), "hostel_id": str(msg.hostel_id), "full_name": msg.full_name, "email": msg.email, "subject": msg.subject, "message": msg.content, "created_at": msg.created_at.isoformat()}, status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def ai_chat(request):
    try:
        data = json.loads(request.body)
        question = data.get("question", "").strip()
        if not question:
            return JsonResponse({"error": "Question is required."}, status=400)
        api_key = os.getenv("GOOGLE_GENERATIVE_API_KEY")
        if api_key:
            try:
                prompt = f"You are a helpful hostel assistant for EHostelFinder. Question: {question}"
                payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
                req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return JsonResponse(json.loads(resp.read().decode("utf-8")))
            except:
                pass
        return JsonResponse({"candidates": [{"content": {"parts": [{"text": get_local_ai_response(question)}]}}]})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@require_http_methods(["GET"])
def get_messages_by_hostel(request, hostel_id):
    try:
        msgs = Message.objects.filter(hostel_id=hostel_id)
        return JsonResponse([{"id": str(m.id), "hostel_id": str(m.hostel_id), "full_name": m.full_name, "email": m.email, "subject": m.subject, "message": m.content, "created_at": m.created_at.isoformat()} for m in msgs], safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@require_http_methods(["GET"])
def get_booking_by_id(request, id):
    try:
        booking = get_object_or_404(Booking, id=id)
        if request.user.id == booking.customer_id:
            return JsonResponse({"id": str(booking.id), "booking_reference": booking.booking_reference, "hostel_id": str(booking.hostel_id), "room_id": str(booking.room_id), "check_in": booking.check_in.isoformat(), "check_out": booking.check_out.isoformat(), "guests": booking.guests, "nights": booking.nights, "total_price": str(booking.total_price), "booking_status": booking.booking_status, "payment_status": booking.payment_status, "special_requests": booking.special_requests})
        return JsonResponse({"error": "Not authorized"}, status=403)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@require_http_methods(["GET", "POST"])
def login(request):
    if request.method == "GET":
        return render(request, "login.html", {"form": UserLoginForm()})
    form = UserLoginForm(request.POST)
    if form.is_valid():
        from django.contrib.auth import authenticate, login as auth_login
        user = authenticate(request, username=form.cleaned_data["email"], password=form.cleaned_data["password"])
        if user:
            auth_login(request, user)
            return redirect("home")
        messages.error(request, "Invalid email or password")
    else:
        messages.error(request, "Invalid email or password")
    return render(request, "login.html", {"form": form})

def forgot_password(request):
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            user = User.objects.filter(email=email).first()
            if user:
                token = secrets.token_urlsafe(32)
                from datetime import timedelta
                PasswordResetToken.objects.create(user=user, token=token, expires_at=timezone.now() + timedelta(hours=24))
            return redirect("password_reset_status")
    else:
        form = ForgotPasswordForm()
    return render(request, "forgot_password.html", {"form": form})

def reset_password(request, token):
    reset_token = PasswordResetToken.objects.filter(token=token).first()
    if not reset_token or reset_token.is_expired:
        return redirect("forgot_password")
    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            reset_token.user.set_password(form.cleaned_data["password"])
            reset_token.user.save()
            reset_token.used_at = timezone.now()
            reset_token.save()
            return redirect("login")
    else:
        form = ResetPasswordForm()
    return render(request, "reset_password.html", {"form": form})

@require_http_methods(["GET", "POST"])
def signup(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            try:
                from .email_utils import send_email_confirmation
                send_email_confirmation(user, request)
            except: pass
            messages.success(request, "Account created! Please check your email to confirm.")
            return redirect("login")
    else:
        form = UserRegistrationForm()
    return render(request, "signup.html", {"form": form})

@require_http_methods(["GET"])
def logout_view(request):
    logout(request)
    return redirect("home")

def cookie_policy(request):
    return render(request, "cookie_policy.html")

def privacy_policy(request):
    return render(request, "privacy_policy.html")

def terms_of_use(request):
    return render(request, "terms_of_use.html")

def ai_assistant(request):
    return render(request, "ai_assistant.html")

def how_it_works(request):
    return render(request, "how_it_works.html")

@require_http_methods(["GET"])
def admin_messages(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Auth required"}, status=401)
    msgs = ContactMessage.objects.all()[:100]
    return JsonResponse({"messages": [{"id": msg.id, "full_name": msg.full_name, "email": msg.email, "subject": msg.subject, "message": msg.message, "created_at": msg.created_at.isoformat(), "is_read": msg.is_read} for msg in msgs]})

@require_http_methods(["GET", "POST"])
def get_user(request):
    if request.user.is_authenticated:
        p = getattr(request.user, "profile", None)
        return JsonResponse({"id": request.user.id, "email": request.user.email, "first_name": request.user.first_name, "last_name": request.user.last_name, "profile_image_url": p.profile_photo if p else None, "role": p.role if p else "customer", "full_name": p.full_name if p else ""})
    return JsonResponse({"error": "Not authenticated"}, status=401)

@require_http_methods(["POST"])
def create_booking(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Auth required"}, status=401)
    try:
        data = json.loads(request.body)
        room = get_object_or_404(Room, id=data.get("room_id"))
        from datetime import datetime
        check_in = datetime.strptime(data.get("check_in"), "%Y-%m-%d").date()
        check_out = datetime.strptime(data.get("check_out"), "%Y-%m-%d").date()
        guests = int(data.get("guests", 1))
        nights = (check_out - check_in).days
        if nights <= 0:
            return JsonResponse({"error": "Invalid date range"}, status=400)
        total_price = room.price_per_night * nights
        booking = Booking.objects.create(hostel_id=room.hostel_id, room=room, customer=request.user, check_in=check_in, check_out=check_out, guests=guests, nights=nights, total_price=total_price, special_requests=data.get("special_requests", ""), booking_status="Pending", payment_status="Pending")
        Notification.objects.create(user=request.user, title="Booking Created", message=f"Booking at {room.hostel.name} (Ref: {booking.booking_reference}) created.")
        return JsonResponse({"id": str(booking.id), "booking_reference": booking.booking_reference, "hostel_id": str(booking.hostel_id), "room_id": str(booking.room_id), "check_in": booking.check_in.isoformat(), "check_out": booking.check_out.isoformat(), "guests": booking.guests, "nights": booking.nights, "total_price": str(booking.total_price), "booking_status": booking.booking_status, "payment_status": booking.payment_status, "special_requests": booking.special_requests}, status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

def roommate_finder(request):
    if not request.user.is_authenticated:
        return redirect("login")
    has_active_request = RoommateRequest.objects.filter(user=request.user, is_active=True).exists()
    my_request = RoommateRequest.objects.filter(user=request.user, is_active=True).first()
    my_chat_rooms = ChatRoom.objects.filter(participants=request.user).prefetch_related('participants')
    
    # Pre-select room/hostel from URL params
    preselected_room_id = request.GET.get('room_id')
    preselected_hostel_id = request.GET.get('hostel_id')
    single_price = request.GET.get('single_price')
    
    context = {
        "has_active_request": has_active_request,
        "my_request": my_request,
        "my_chat_rooms": my_chat_rooms,
        "hostels": Hostel.objects.all(),
        "preselected_room_id": preselected_room_id,
        "preselected_hostel_id": preselected_hostel_id,
        "single_price": single_price,
    }
    return render(request, "roommate_finder.html", context)

@require_http_methods(["GET", "POST"])
def api_roommate_requests(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Auth required"}, status=401)
    if request.method == "GET":
        requests = RoommateRequest.objects.filter(is_active=True).select_related('user', 'hostel').prefetch_related('room')
        results = []
        for req in requests:
            if req.user.id == request.user.id:
                continue
            results.append({
                "id": str(req.id),
                "user": {"id": req.user.id, "full_name": req.user.get_full_name() or req.user.email, "email": req.user.email},
                "hostel": {"id": str(req.hostel.id), "name": req.hostel.name, "city": req.hostel.city},
                "room": {"id": str(req.room.id), "room_name": req.room.room_name} if req.room else None,
                "preferred_gender": req.preferred_gender,
                "budget_min": str(req.budget_min) if req.budget_min else None,
                "budget_max": str(req.budget_max) if req.budget_max else None,
                "about_me": req.about_me,
                "lifestyle_preferences": req.lifestyle_preferences,
                "created_at": req.created_at.isoformat(),
            })
        return JsonResponse(results, safe=False)
    try:
        data = json.loads(request.body)
        if data.get("is_active") == False:
            RoommateRequest.objects.filter(user=request.user).update(is_active=False)
            return JsonResponse({"success": True, "cancelled": True})
        hostel = get_object_or_404(Hostel, id=data.get("hostel_id"))
        room = None
        if data.get("room_id"):
            room = get_object_or_404(Room, id=data.get("room_id"))
        defaults = {
            "hostel": hostel,
            "room": room,
            "preferred_gender": data.get("preferred_gender", "any"),
            "budget_min": data.get("budget_min"),
            "budget_max": data.get("budget_max"),
            "about_me": data.get("about_me", ""),
            "lifestyle_preferences": data.get("lifestyle_preferences", []),
            "is_active": True,
        }
        req, created = RoommateRequest.objects.update_or_create(
            user=request.user, defaults=defaults
        )
        return JsonResponse({"success": True, "id": str(req.id), "created": created}, status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@require_http_methods(["POST"])
def api_roommate_request_toggle(request, request_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Auth required"}, status=401)
    try:
        roommate_req = get_object_or_404(RoommateRequest, id=request_id)
        other_participant = roommate_req.user
        my_existing = RoommateRequest.objects.filter(user=request.user, is_active=True).first()
        
        chat_room, created = ChatRoom.objects.get_or_create(
            hostel=roommate_req.hostel
        )
        chat_room.participants.add(request.user, other_participant)
        chat_room.room = roommate_req.room
        chat_room.save()
        return JsonResponse({"success": True, "chat_room_id": str(chat_room.id)}, status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@require_http_methods(["GET"])
def api_chat_rooms(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Auth required"}, status=401)
    rooms = ChatRoom.objects.filter(participants=request.user).prefetch_related('participants', 'messages')
    results = []
    for room in rooms:
        other_participants = [p for p in room.participants.all() if p.id != request.user.id]
        last_msg = room.messages.order_by('-created_at').first()
        results.append({
            "id": str(room.id),
            "participants": [{"id": p.id, "full_name": p.get_full_name() or p.email, "email": p.email} for p in other_participants],
            "hostel": {"id": str(room.hostel.id), "name": room.hostel.name} if room.hostel else None,
            "room": {"id": str(room.room.id), "room_name": room.room.room_name} if room.room else None,
            "last_message": {"content": last_msg.content, "created_at": last_msg.created_at.isoformat(), "sender_id": last_msg.sender.id} if last_msg else None,
            "updated_at": room.updated_at.isoformat(),
        })
    return JsonResponse(results, safe=False)

@require_http_methods(["GET", "POST"])
def chat_room_detail(request, room_id):
    if not request.user.is_authenticated:
        return redirect("login")
    room = get_object_or_404(ChatRoom, id=room_id, participants=request.user)
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            ChatMessage.objects.create(chat_room=room, sender=request.user, content=content)
            room.updated_at = timezone.now()
            room.save()
    messages = room.messages.select_related('sender').order_by('created_at')
    return render(request, "chatbox.html", {"room": room, "messages": messages})

def my_chat_rooms(request):
    if not request.user.is_authenticated:
        return redirect("login")
    rooms = ChatRoom.objects.filter(participants=request.user).prefetch_related('participants', 'messages', 'hostel')
    return render(request, "my_chat_rooms.html", {"chat_rooms": rooms})

def send_ai_reply(room, content):
    """Send an AI-generated reply to a chat room."""
    from .local_ai import get_hf_ai_response
    try:
        ai_response = get_hf_ai_response(content, f"Hostel: {room.hostel.name if room.hostel else 'Unknown'}")
        return ChatMessage.objects.create(chat_room=room, sender=None, content=ai_response, is_ai=True)
    except Exception:
        return None

@require_http_methods(["POST"])
def api_send_message(request, room_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Auth required"}, status=401)
    try:
        room = get_object_or_404(ChatRoom, id=room_id, participants=request.user)
        content = ""
        try:
            data = json.loads(request.body)
            content = data.get("content", "")
        except json.JSONDecodeError:
            pass
        msg = ChatMessage.objects.create(chat_room=room, sender=request.user, content=content)
        room.updated_at = timezone.now()
        room.save()
        if len(content.strip()) > 5:
            send_ai_reply(room, content)
        return JsonResponse({"success": True, "id": str(msg.id), "content": msg.content, "created_at": msg.created_at.isoformat()}, status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

def universities(request):
    university_options = get_university_options()
    universities_data = []
    for uni in university_options:
        name = uni["name"]
        count = Hostel.objects.filter(university=name).count()
        top = Hostel.objects.filter(university=name).order_by("-rating").first()
        universities_data.append({"name": name, "count": count, "top_hostel": top.name if top else "", "rating": float(top.rating) if top and top.rating else 0})
    universities_data.sort(key=lambda x: x["name"])
    return render(request, "universities.html", {"universities": universities_data})

def contact(request):
    if request.method == "POST":
        try:
            ContactMessage.objects.create(full_name=request.POST.get("name", ""), email=request.POST.get("email", ""), subject=request.POST.get("subject", ""), message=request.POST.get("message", ""))
            return JsonResponse({"success": True, "message": "Message sent successfully!"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return render(request, "contact.html")

def google_auth(request):
    import urllib.parse
    from django.conf import settings
    redirect_uri = request.build_absolute_uri("/api/auth/google/callback/")
    params = {"client_id": settings.GOOGLE_CLIENT_ID, "redirect_uri": redirect_uri, "response_type": "code", "scope": "email profile", "access_type": "online"}
    return redirect(f"https://accounts.google.com/o/oauth2/auth?{urllib.parse.urlencode(params)}")

def google_auth_callback(request):
    import urllib.parse, urllib.request
    from django.conf import settings
    from django.contrib.auth import login as auth_login
    code = request.GET.get("code")
    if not code:
        messages.error(request, "Google auth failed")
        return redirect("login")
    redirect_uri = request.build_absolute_uri("/api/auth/google/callback/")
    token_data = urllib.parse.urlencode({"code": code, "client_id": settings.GOOGLE_CLIENT_ID, "client_secret": settings.GOOGLE_CLIENT_SECRET, "redirect_uri": redirect_uri, "grant_type": "authorization_code"}).encode()
    try:
        req = urllib.request.Request("https://oauth2.googleapis.com/token", data=token_data, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        with urllib.request.urlopen(req, timeout=10) as resp:
            token_result = json.loads(resp.read().decode())
        access_token = token_result.get("access_token")
        user_req = urllib.request.Request(f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={access_token}")
        with urllib.request.urlopen(user_req, timeout=10) as resp:
            user_info = json.loads(resp.read().decode())
        email = user_info.get("email")
        if email:
            user, created = User.objects.get_or_create(email=email, defaults={"first_name": user_info.get("given_name", ""), "last_name": user_info.get("family_name", ""), "provider": "google"})
            if created:
                user.set_password(secrets.token_urlsafe(16))
                user.save()
                Profile.objects.create(user=user, full_name=f"{user.first_name} {user.last_name}", email=email, role="customer")
            auth_login(request, user)
            return redirect("home")
        messages.error(request, "Could not get user info")
        return redirect("login")
    except Exception as e:
        messages.error(request, f"Google auth error: {str(e)}")
        return redirect("login")

def profile(request):
    if not request.user.is_authenticated:
        return redirect("login")
    if request.method == "POST":
        p, _ = Profile.objects.get_or_create(user=request.user)
        p.full_name = request.POST.get("full_name", "")
        p.phone = request.POST.get("phone", "")
        p.profile_photo = request.POST.get("profile_photo", "")
        p.save()
        request.user.first_name = request.POST.get("first_name", "")
        request.user.last_name = request.POST.get("last_name", "")
        request.user.email = request.POST.get("email", "")
        request.user.save()
        messages.success(request, "Profile updated!")
    p = getattr(request.user, "profile", None)
    return render(request, "profile.html", {"profile": p})

def my_bookings(request):
    if not request.user.is_authenticated:
        return redirect("login")
    bookings = Booking.objects.filter(customer=request.user).select_related("hostel", "room").order_by("-booked_at")
    return render(request, "my_bookings.html", {"bookings": bookings})

def my_favorites(request):
    if not request.user.is_authenticated:
        return redirect("login")
    favorites = Favorite.objects.filter(customer=request.user).select_related("hostel")
    return render(request, "my_favorites.html", {"favorites": favorites})

def view_notifications(request):
    if not request.user.is_authenticated:
        return redirect("login")
    notifications = Notification.objects.filter(user=request.user).order_by("-created_at")[:50]
    return render(request, "notifications.html", {"notifications": notifications})

@require_http_methods(["GET"])
def api_notifications(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Auth required"}, status=401)
    notifications = Notification.objects.filter(user=request.user).order_by("-created_at")[:10]
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({
        "notifications": [{"id": n.id, "title": n.title, "message": n.message, "is_read": n.is_read, "created_at": n.created_at.isoformat()} for n in notifications],
        "unread_count": unread_count
    })

@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Auth required"}, status=401)
    try:
        Notification.objects.filter(id=notification_id, user=request.user).update(is_read=True)
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@require_http_methods(["POST"])
def mark_all_notifications_read(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Auth required"}, status=401)
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({"success": True})

@require_http_methods(["POST"])
def toggle_favorite(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Auth required"}, status=401)
    try:
        data = json.loads(request.body)
        hostel = get_object_or_404(Hostel, id=data.get("hostel_id"))
        fav, created = Favorite.objects.get_or_create(customer=request.user, hostel=hostel)
        if not created:
            fav.delete()
            return JsonResponse({"favorited": False})
        return JsonResponse({"favorited": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@require_http_methods(["POST"])
def process_payment(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Auth required"}, status=401)
    try:
        data = json.loads(request.body)
        booking = get_object_or_404(Booking, id=data.get("booking_id"))
        if booking.customer != request.user:
            return JsonResponse({"error": "Not authorized"}, status=403)
        booking.payment_status = "Paid"
        booking.booking_status = "Confirmed"
        booking.save()
        Payment.objects.create(booking=booking, amount=booking.total_price, payment_method=data.get("payment_method", "Credit Card"), payment_status="Paid", paid_at=timezone.now())
        return JsonResponse({"success": True, "transaction_reference": f"TXN-{uuid.uuid4().hex[:12].upper()}"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@require_http_methods(["POST"])
def cancel_booking(request, booking_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Auth required"}, status=401)
    try:
        booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
        booking.booking_status = "Cancelled"
        booking.save()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

def manager_dashboard(request):
    if not request.user.is_authenticated or getattr(request.user, 'profile', None).role != 'manager':
        messages.error(request, "Access denied")
        return redirect("home")
    bookings = Booking.objects.filter(hostel=request.user.profile.hostel).select_related('room', 'customer') if request.user.profile.hostel else Booking.objects.none()
    return render(request, "manager_dashboard.html", {"bookings": bookings})

def manager_bookings(request):
    return render(request, "manager_bookings.html")

def manager_update_booking(request, booking_id):
    return JsonResponse({"success": True})

def manager_checkins(request):
    return render(request, "manager_checkins.html")

def manager_rooms(request):
    return render(request, "manager_rooms.html")

def manager_checkout(request, booking_id):
    return JsonResponse({"success": True})

def hostel_upload(request):
    return render(request, "hostel_upload.html")

def admin_manager_assign(request):
    return render(request, "admin_manager_assign.html")

@require_http_methods(["GET"])
def api_managers(request):
    return JsonResponse({"managers": []})

@require_http_methods(["POST"])
def admin_create_manager(request):
    return JsonResponse({"success": True})

@require_http_methods(["GET"])
def api_unassigned_managers(request):
    return JsonResponse({"managers": []})

@require_http_methods(["GET"])
def api_hostel_managers(request, hostel_id):
    return JsonResponse({"managers": []})

@require_http_methods(["POST"])
def admin_assign_manager(request):
    return JsonResponse({"success": True})

@require_http_methods(["POST"])
def admin_remove_manager(request):
    return JsonResponse({"success": True})

def custom_404(request, exception):
    return render(request, "404.html", status=404)

def custom_500(request):
    return render(request, "500.html", status=500)