from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db.models import Avg, Q
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import json, os, urllib.request, urllib.error, uuid
from .forms import UserRegistrationForm, UserLoginForm, ForgotPasswordForm, ResetPasswordForm, ProfileUpdateForm, HostelUploadForm
from .models import Hostel, User, ContactMessage, Profile, Room, Booking, Review, Favorite, Message, Notification, Payment, RoomStatus, BookingStatus, RoomImage, HostelImage
from .local_ai import get_local_ai_response
from .email_utils import send_booking_receipt

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


def generate_room_labels(start_label, end_label, label_type):
    if not start_label and not end_label:
        return []
    if label_type == "alphabetic":
        start_char = (start_label or "A").strip().upper()
        end_char = (end_label or "Z").strip().upper()
        if len(start_char) != 1 or len(end_char) != 1 or not start_char.isalpha() or not end_char.isalpha():
            return []
        start_index = ord(start_char) - ord('A')
        end_index = ord(end_char) - ord('A')
        if end_index < start_index:
            start_index, end_index = end_index, start_index
        return [chr(ord('A') + idx) for idx in range(start_index, end_index + 1)]

    try:
        start_num = int(str(start_label).strip()) if str(start_label).strip() else 1
        end_num = int(str(end_label).strip()) if str(end_label).strip() else start_num
    except ValueError:
        return []
    if end_num < start_num:
        start_num, end_num = end_num, start_num
    return list(range(start_num, end_num + 1))


def create_hostel_room_inventory(hostel, room_type_prices, request_post):
    room_label_type = request_post.get("room_label_type") or "numeric"
    room_label_start = (request_post.get("room_label_start") or "").strip()
    room_label_end = (request_post.get("room_label_end") or "").strip()
    floor_count = max(1, int(request_post.get("floor_count") or 1))

    generated_labels = generate_room_labels(room_label_start, room_label_end, room_label_type)
    hostel.room_label_range = {
        "type": room_label_type,
        "start": room_label_start,
        "end": room_label_end,
        "floors": floor_count,
    }
    hostel.total_floors = floor_count
    hostel.save(update_fields=["room_label_range", "total_floors"])

    for room_type, price, is_avail in room_type_prices:
        if price is None or price == 0:
            continue
        capacity = 1 if room_type == "Single" else 2 if room_type == "Double" else 3 if room_type == "Triple" else 4
        if generated_labels:
            for index, label in enumerate(generated_labels):
                floor_number = (index % floor_count) + 1
                room_number = str(label)
                Room.objects.create(
                    hostel=hostel,
                    room_number=room_number,
                    room_name=f"{room_type} Room {room_number}",
                    room_type=room_type,
                    capacity=capacity,
                    available_quantity=1,
                    price_per_semester=price,
                    floor=floor_number,
                    status="Available" if is_avail == "on" else "Maintenance",
                    is_available=is_avail == "on",
                )
            continue

        Room.objects.create(
            hostel=hostel,
            room_number=str(room_type[0].upper()) if room_type else "1",
            room_name=f"{room_type} Room",
            room_type=room_type,
            capacity=capacity,
            available_quantity=1,
            price_per_semester=price,
            status="Available" if is_avail == "on" else "Maintenance",
            is_available=is_avail == "on",
        )

    hostel.update_full_status()


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
            "available": h.available and not h.is_full, "rating": float(h.rating) if h.rating else round(float(h.average_rating), 1),
            "distance": h.distance or "Near campus",
            "price": str(h.price) if h.price else (str(available_room.price_per_semester) if available_room else "0"),
            "amenities": h.amenities or [], "is_full": h.is_full,
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
        all_rooms = Room.objects.filter(hostel=hostel).order_by('floor', 'room_number')
        available_rooms = all_rooms.filter(status="Available")
        images = hostel.images.all()
        cover = hostel.images.filter(is_cover=True).first()
        facilities = hostel.facilities.all()
        reviews = hostel.reviews.select_related("customer").all()

        # Build room numbers list
        room_numbers = [r.room_number for r in all_rooms]

        # Build floors data for the Building Overview section
        floors_data = []
        floor_numbers = all_rooms.values_list('floor', flat=True).distinct().order_by('floor')
        for floor_num in floor_numbers:
            if floor_num is None: continue
            floor_rooms = all_rooms.filter(floor=floor_num)
            floor_rooms_data = []
            for r in floor_rooms:
                floor_rooms_data.append({
                    "id": str(r.id),
                    "room_number": r.room_number,
                    "room_name": r.room_name,
                    "room_type": r.room_type,
                    "status": r.status,
                    "is_available": r.is_available,
                    "capacity": r.capacity,
                    "price_per_semester": str(r.price_per_semester),
                })
            floors_data.append({
                "floor_number": floor_num,
                "rooms": floor_rooms_data,
            })

        rooms_data = []
        for r in available_rooms:
            rooms_data.append({
                "id": str(r.id), "room_number": r.room_number, "room_name": r.room_name, "room_type": r.room_type,
                "capacity": r.capacity, "available_quantity": r.available_quantity, "price_per_semester": str(r.price_per_semester),
                "single_bed_price": str(r.single_bed_price) if r.single_bed_price else None,
                "floor": r.floor or 1, "description": r.description,
                "size_sq_meters": str(r.size_sq_meters) if r.size_sq_meters else None,
                "private_bathroom": r.private_bathroom, "air_conditioning": r.air_conditioning,
                "balcony": r.balcony, "television": r.television, "wifi": r.wifi,
                "status": r.status, "is_available": r.is_available,
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
                "is_full": hostel.is_full,
                "total_floors": hostel.total_floors,
            },
            "rooms": rooms_data,
            "room_numbers": room_numbers,
            "floors_data": floors_data,
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
        Review.objects.create(hostel=hostel, customer=request.user, rating=int(rating), comment=comment or "")
        hostel.review_count = hostel.reviews.count()
        hostel.rating = round(hostel.reviews.aggregate(avg=Avg("rating"))["avg"] or 0, 2)
        hostel.save(update_fields=["review_count", "rating"])
        messages.success(request, "Your review has been submitted successfully.")
        return redirect("hostel_detail", id=hostel.id)

    return render(request, "hostel_detail.html", context)


# ========== API ENDPOINTS ==========

@require_http_methods(["GET"])
def api_hostels(request):
    city = request.GET.get("city", ""); country = request.GET.get("country", "")
    room_type = request.GET.get("room_type", ""); university = request.GET.get("university", "")
    min_price = request.GET.get("min_price", ""); max_price = request.GET.get("max_price", "")
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
        results.append({"id": str(h.id), "name": h.name, "city": h.city, "country": h.country, "university": h.university, "address": h.address, "description": h.description, "average_rating": round(float(h.average_rating), 2), "rating": float(h.rating) if h.rating else round(float(h.average_rating), 2), "review_count": h.reviews.count(), "image_url": h.image_url or (cover.image_url if cover else None), "facilities": [f.facility_name for f in h.facilities.all()], "amenities": h.amenities or [], "distance": h.distance or "", "price": float(h.price) if h.price else 0, "contact": h.contact or "", "available": h.available and not h.is_full, "is_full": h.is_full, "status": "Full" if h.is_full else "Available"})
    return JsonResponse(results, safe=False)


@require_http_methods(["GET"])
def api_hostel_detail(request, id):
    hostel = get_object_or_404(Hostel, id=id)
    rooms = Room.objects.filter(hostel=hostel)
    cover = hostel.images.filter(is_cover=True).first()
    rooms_data = [{"id": str(r.id), "room_number": r.room_number, "room_name": r.room_name, "room_type": r.room_type, "capacity": r.capacity, "price_per_semester": str(r.price_per_semester), "description": r.description, "private_bathroom": r.private_bathroom, "air_conditioning": r.air_conditioning, "wifi": r.wifi, "status": r.status} for r in rooms]
    return JsonResponse({"id": str(hostel.id), "name": hostel.name, "description": hostel.description, "address": hostel.address, "city": hostel.city, "country": hostel.country, "phone": hostel.phone, "email": hostel.email, "latitude": str(hostel.latitude) if hostel.latitude else None, "longitude": str(hostel.longitude) if hostel.longitude else None, "image_url": cover.image_url if cover else None, "rooms": rooms_data, "facilities": [{"name": f.facility_name} for f in hostel.facilities.all()]})


@require_http_methods(["GET"])
def api_cities(request):
    return JsonResponse(sorted(Hostel.objects.values_list("city", flat=True).exclude(city="").distinct()), safe=False)


@require_http_methods(["GET"])
def api_countries(request):
    return JsonResponse(sorted(Hostel.objects.values_list("country", flat=True).exclude(country="").distinct()), safe=False)


@require_http_methods(["GET", "POST"])
def login(request):
    if request.method == "GET":
        return render(request, "login.html", {"form": UserLoginForm()})
    form = UserLoginForm(request.POST)
    if form.is_valid():
        from django.contrib.auth import authenticate, login as auth_login
        email = form.cleaned_data["email"].strip().lower()
        user = authenticate(request, username=email, password=form.cleaned_data["password"])
        if user:
            auth_login(request, user)
            if user.is_staff or (hasattr(user, 'profile') and user.profile.role == 'admin'):
                return redirect("admin:index")
            return redirect("home")
        messages.error(request, "Invalid email or password")
    else:
        messages.error(request, "Invalid email or password")
    return render(request, "login.html", {"form": form})


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


def cookie_policy(request): return render(request, "cookie_policy.html")
def privacy_policy(request): return render(request, "privacy_policy.html")
def terms_of_use(request): return render(request, "terms_of_use.html")
def ai_assistant(request): return render(request, "ai_assistant.html")
def how_it_works(request): return render(request, "how_it_works.html")


@require_http_methods(["GET"])
def admin_messages(request):
    if not request.user.is_authenticated: return JsonResponse({"error": "Auth required"}, status=401)
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
    if not request.user.is_authenticated: return JsonResponse({"error": "Auth required"}, status=401)
    try:
        data = json.loads(request.body)
        room = get_object_or_404(Room, id=data.get("room_id"))
        hostel = room.hostel
        if hostel.is_full:
            return JsonResponse({"error": "This hostel is currently marked as full and is not accepting new bookings."}, status=400)
        if room.status != "Available" or not room.is_available:
            return JsonResponse({"error": "This room is not available for booking."}, status=400)
        from datetime import datetime
        check_in = datetime.strptime(data.get("check_in"), "%Y-%m-%d").date()
        check_out = datetime.strptime(data.get("check_out"), "%Y-%m-%d").date()
        students = int(data.get("students", 1))
        semesters = (check_out - check_in).days
        if semesters <= 0: return JsonResponse({"error": "Invalid date range"}, status=400)
        total_price = room.price_per_semester * semesters
        booking = Booking.objects.create(hostel_id=room.hostel_id, room=room, customer_id=request.user.id, check_in=check_in, check_out=check_out, students=students, semesters=semesters, total_price=total_price, special_requests=data.get("special_requests", ""), booking_status="Pending", payment_status="Pending")
        Notification.objects.create(user=request.user, title="Booking Created", message=f"Booking at {room.hostel.name} (Ref: {booking.booking_reference}) created.")
        try:
            send_booking_receipt(booking, request)
        except Exception:
            pass
        return JsonResponse({"id": str(booking.id), "booking_reference": booking.booking_reference, "hostel_id": str(booking.hostel_id), "room_id": str(booking.room_id), "check_in": booking.check_in.isoformat(), "check_out": booking.check_out.isoformat(), "students": booking.students, "semesters": booking.semesters, "total_price": str(booking.total_price), "booking_status": booking.booking_status, "payment_status": booking.payment_status, "special_requests": booking.special_requests}, status=201)
    except Exception as e: return JsonResponse({"error": str(e)}, status=400)


@require_http_methods(["GET"])
def get_booking_by_id(request, id):
    try:
        booking = get_object_or_404(Booking, id=id)
        if request.user.id == booking.customer_id:
            return JsonResponse({"id": str(booking.id), "booking_reference": booking.booking_reference, "hostel_id": str(booking.hostel_id), "room_id": str(booking.room_id), "check_in": booking.check_in.isoformat(), "check_out": booking.check_out.isoformat(), "students": booking.students, "semesters": booking.semesters, "total_price": str(booking.total_price), "booking_status": booking.booking_status, "payment_status": booking.payment_status, "special_requests": booking.special_requests})
        return JsonResponse({"error": "Not authorized"}, status=403)
    except Exception as e: return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["POST"])
def create_message(request):
    try:
        data = json.loads(request.body)
        hostel = get_object_or_404(Hostel, id=data.get("hostelId"))
        msg = Message.objects.create(hostel=hostel, user=request.user if request.user.is_authenticated else None, full_name=data.get("fullName", ""), email=data.get("email", ""), phone=data.get("phone", ""), subject=data.get("subject", ""), content=data.get("content", "") or data.get("message", ""))
        return JsonResponse({"id": str(msg.id), "hostel_id": str(msg.hostel_id), "full_name": msg.full_name, "email": msg.email, "subject": msg.subject, "message": msg.content, "created_at": msg.created_at.isoformat()}, status=201)
    except Exception as e: return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def ai_chat(request):
    try:
        data = json.loads(request.body)
        question = data.get("question", "").strip()
        if not question: return JsonResponse({"error": "Question is required."}, status=400)
        api_key = os.getenv("GOOGLE_GENERATIVE_API_KEY")
        if api_key:
            try:
                prompt = f"You are a helpful hostel assistant for EHostelFinder. Question: {question}"
                payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
                req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return JsonResponse(json.loads(resp.read().decode("utf-8")))
            except: pass
        return JsonResponse({"candidates": [{"content": {"parts": [{"text": get_local_ai_response(question)}]}}]})
    except Exception as e: return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["GET"])
def get_messages_by_hostel(request, hostel_id):
    try:
        msgs = Message.objects.filter(hostel_id=hostel_id)
        return JsonResponse([{"id": str(m.id), "hostel_id": str(m.hostel_id), "full_name": m.full_name, "email": m.email, "subject": m.subject, "message": m.content, "created_at": m.created_at.isoformat()} for m in msgs], safe=False)
    except Exception as e: return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["GET"])
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


@csrf_exempt
def contact(request):
    if request.method == "POST":
        try:
            ContactMessage.objects.create(full_name=request.POST.get("name", ""), email=request.POST.get("email", ""), subject=request.POST.get("subject", ""), message=request.POST.get("message", ""))
            return JsonResponse({"success": True, "message": "Message sent successfully!"})
        except Exception as e: return JsonResponse({"error": str(e)}, status=400)
    return render(request, "contact.html")


def google_auth(request):
    import urllib.parse; from django.conf import settings
    redirect_uri = settings.GOOGLE_CALLBACK_URL or request.build_absolute_uri("/api/auth/google/callback/")
    params = {"client_id": settings.GOOGLE_CLIENT_ID, "redirect_uri": redirect_uri, "response_type": "code", "scope": "https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile", "access_type": "online"}
    return redirect(f"https://accounts.google.com/o/oauth2/auth?{urllib.parse.urlencode(params)}")


def google_auth_callback(request):
    import urllib.parse, urllib.request; from django.conf import settings
    from django.contrib.auth import login as auth_login
    code = request.GET.get("code")
    if not code: messages.error(request, "Google auth failed"); return redirect("login")
    redirect_uri = settings.GOOGLE_CALLBACK_URL or request.build_absolute_uri("/api/auth/google/callback/")
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
        first_name = user_info.get("given_name", "")
        last_name = user_info.get("family_name", "")
        try: user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create(id=str(uuid.uuid4()), email=email, first_name=first_name or email.split("@")[0], last_name=last_name, provider="google")
        auth_login(request, user)
        return redirect("home")
    except Exception as e:
        messages.error(request, "Google authentication failed")
        return redirect("login")


def github_auth(request):
    import urllib.parse; from django.conf import settings
    redirect_uri = settings.GITHUB_CALLBACK_URL or request.build_absolute_uri("/api/auth/github/callback/")
    params = {"client_id": settings.GITHUB_CLIENT_ID, "redirect_uri": redirect_uri, "scope": "user:email"}
    return redirect(f"https://github.com/login/oauth/authorize?{urllib.parse.urlencode(params)}")


def github_auth_callback(request):
    import urllib.parse, urllib.request, json; from django.conf import settings
    from django.contrib.auth import login as auth_login
    code = request.GET.get("code")
    if not code: messages.error(request, "GitHub auth failed"); return redirect("login")
    redirect_uri = settings.GITHUB_CALLBACK_URL or request.build_absolute_uri("/api/auth/github/callback/")
    token_data = urllib.parse.urlencode({
        "client_id": settings.GITHUB_CLIENT_ID,
        "client_secret": settings.GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": redirect_uri,
    }).encode()
    try:
        req = urllib.request.Request("https://github.com/login/oauth/access_token", data=token_data, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        req.add_header("Accept", "application/json")
        with urllib.request.urlopen(req, timeout=10) as resp:
            token_result = json.loads(resp.read().decode())
        access_token = token_result.get("access_token")
        if not access_token:
            messages.error(request, "GitHub authentication failed")
            return redirect("login")
        user_req = urllib.request.Request("https://api.github.com/user", headers={"Authorization": f"token {access_token}"})
        with urllib.request.urlopen(user_req, timeout=10) as resp:
            user_info = json.loads(resp.read().decode())
        email = user_info.get("email") or user_info.get("primary_email")
        if not email:
            email_req = urllib.request.Request("https://api.github.com/user/emails", headers={"Authorization": f"token {access_token}"})
            with urllib.request.urlopen(email_req, timeout=10) as resp:
                emails = json.loads(resp.read().decode())
            for e in emails:
                if e.get("primary") and e.get("verified"):
                    email = e.get("email")
                    break
        first_name = user_info.get("name", "").split(" ")[0] if user_info.get("name") else email.split("@")[0]
        last_name = user_info.get("name", "").split(" ")[-1] if user_info.get("name") and len(user_info.get("name", "").split(" ")) > 1 else ""
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create(id=str(uuid.uuid4()), email=email, first_name=first_name, last_name=last_name, provider="github")
        auth_login(request, user)
        return redirect("home")
    except Exception as e:
        messages.error(request, "GitHub authentication failed")
        return redirect("login")# ========== MANAGER VIEWS ==========

@require_http_methods(["GET"])
def manager_dashboard(request):
    if not request.user.is_authenticated: return redirect("login")
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != "manager":
        messages.error(request, "Access denied.")
        return redirect("home")
    hostel = profile.hostel
    if not hostel:
        messages.error(request, "No hostel assigned.")
        return redirect("home")
    return render(request, "manager/dashboard.html", {"hostel": hostel})


@require_http_methods(["GET", "POST", "DELETE"])
def manager_rooms(request):
    """List, create, update, or delete rooms for the manager's hostel."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Auth required"}, status=401)
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != "manager":
        return JsonResponse({"error": "Access denied"}, status=403)
    hostel = profile.hostel
    if not hostel:
        return JsonResponse({"error": "No hostel assigned"}, status=400)

    if request.method == "GET":
        rooms = Room.objects.filter(hostel=hostel).order_by('floor', 'room_number')
        rooms_data = []
        for r in rooms:
            rooms_data.append({
                "id": str(r.id), "room_number": r.room_number, "room_name": r.room_name,
                "room_type": r.room_type, "capacity": r.capacity,
                "available_quantity": r.available_quantity,
                "price_per_semester": str(r.price_per_semester),
                "single_bed_price": str(r.single_bed_price) if r.single_bed_price else None,
                "floor": r.floor, "description": r.description or "",
                "private_bathroom": r.private_bathroom, "air_conditioning": r.air_conditioning,
                "balcony": r.balcony, "television": r.television, "wifi": r.wifi,
                "status": r.status, "is_available": r.is_available,
                "images": ",".join([img.image_url for img in r.images.all()]),
            })
        return JsonResponse(rooms_data, safe=False)

    if request.method == "DELETE":
        try:
            room_id = request.GET.get("room_id")
            if not room_id:
                data = json.loads(request.body) if request.body else {}
                room_id = data.get("room_id")
            if not room_id:
                return JsonResponse({"error": "room_id required"}, status=400)
            room = get_object_or_404(Room, id=room_id, hostel=hostel)
            room.delete()
            hostel.update_full_status()
            return JsonResponse({"success": True, "message": f"Room {room.room_number} deleted"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    try:
        data = json.loads(request.body)
        room_id = data.get("room_id")

        if room_id:
            room = get_object_or_404(Room, id=room_id, hostel=hostel)
            if data.get("room_number") is not None: room.room_number = data["room_number"]
            if data.get("room_name") is not None: room.room_name = data["room_name"]
            if data.get("room_type") is not None: room.room_type = data["room_type"]
            if data.get("capacity") is not None: room.capacity = int(data["capacity"])
            if data.get("available_quantity") is not None: room.available_quantity = int(data["available_quantity"])
            if data.get("price_per_semester") is not None: room.price_per_semester = data["price_per_semester"]
            if data.get("single_bed_price") is not None: room.single_bed_price = data["single_bed_price"] if data["single_bed_price"] else None
            if data.get("floor") is not None: room.floor = int(data["floor"]) if data["floor"] else None
            if data.get("description") is not None: room.description = data["description"]
            if data.get("status") is not None:
                room.status = data["status"]
                room.is_available = data["status"] == "Available"
            if data.get("is_available") is not None:
                room.is_available = data["is_available"] in [True, "true", "True"]
            if data.get("private_bathroom") is not None: room.private_bathroom = bool(data["private_bathroom"])
            if data.get("air_conditioning") is not None: room.air_conditioning = bool(data["air_conditioning"])
            if data.get("balcony") is not None: room.balcony = bool(data["balcony"])
            if data.get("television") is not None: room.television = bool(data["television"])
            if data.get("wifi") is not None: room.wifi = bool(data["wifi"])
            room.save()
            hostel.update_full_status()
            return JsonResponse({"success": True, "message": "Room updated"})
        else:
            room = Room.objects.create(
                hostel=hostel,
                room_number=data.get("room_number", ""),
                room_name=data.get("room_name", ""),
                room_type=data.get("room_type", "Single"),
                capacity=int(data.get("capacity", 1)),
                available_quantity=int(data.get("available_quantity", 1)),
                price_per_semester=data.get("price_per_semester", 0),
                single_bed_price=data.get("single_bed_price") if data.get("single_bed_price") else None,
                floor=int(data["floor"]) if data.get("floor") else None,
                description=data.get("description", ""),
                private_bathroom=bool(data.get("private_bathroom")),
                air_conditioning=bool(data.get("air_conditioning")),
                balcony=bool(data.get("balcony")),
                television=bool(data.get("television")),
                wifi=bool(data.get("wifi")),
                status=data.get("status", "Available"),
                is_available=data.get("is_available", True) in [True, "true", "True"],
            )
            images_str = data.get("images", "")
            if images_str:
                for url in images_str.split(","):
                    url = url.strip()
                    if url:
                        RoomImage.objects.create(room=room, image_url=url)
            hostel.update_full_status()
            return JsonResponse({"success": True, "message": "Room created", "room_id": str(room.id)}, status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@require_http_methods(["GET"])
def manager_bookings(request):
    if not request.user.is_authenticated: return JsonResponse({"error": "Auth required"}, status=401)
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != "manager": return JsonResponse({"error": "Access denied"}, status=403)
    hostel = profile.hostel
    if not hostel: return JsonResponse({"error": "No hostel assigned"}, status=400)
    bookings = Booking.objects.filter(hostel=hostel).select_related("customer", "room").order_by("-booked_at")
    return JsonResponse([{"id": str(b.id), "booking_reference": b.booking_reference, "customer_name": b.customer.get_full_name() or b.customer.email, "customer_email": b.customer.email, "room_number": b.room.room_number, "room_name": b.room.room_name, "check_in": b.check_in.isoformat(), "check_out": b.check_out.isoformat(), "students": b.students, "semesters": b.semesters, "total_price": str(b.total_price), "booking_status": b.booking_status, "payment_status": b.payment_status, "special_requests": b.special_requests or ""} for b in bookings], safe=False)


@require_http_methods(["POST"])
def manager_update_booking(request, booking_id):
    if not request.user.is_authenticated: return JsonResponse({"error": "Auth required"}, status=401)
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != "manager": return JsonResponse({"error": "Access denied"}, status=403)
    hostel = profile.hostel
    if not hostel: return JsonResponse({"error": "No hostel assigned"}, status=400)
    try:
        data = json.loads(request.body)
        booking = get_object_or_404(Booking, id=booking_id, hostel=hostel)
        status = data.get("booking_status")
        old_status = booking.booking_status
        if status and status in dict(BookingStatus.choices).keys():
            booking.booking_status = status
            booking.save(update_fields=["booking_status"])
            if status == "Checked In" and old_status != "Checked In":
                room = booking.room
                if room:
                    room.status = "Occupied"
                    room.is_available = False
                    room.save(update_fields=["status", "is_available"])
                    room.hostel.update_full_status()
            elif status in ["Checked Out", "Cancelled"] and old_status in ["Checked In", "Confirmed"]:
                room = booking.room
                if room:
                    room.status = "Available"
                    room.is_available = True
                    room.save(update_fields=["status", "is_available"])
                    room.hostel.update_full_status()
        return JsonResponse({"success": True})
    except Exception as e: return JsonResponse({"error": str(e)}, status=400)


@require_http_methods(["GET"])
def manager_checkins(request):
    if not request.user.is_authenticated: return JsonResponse({"error": "Auth required"}, status=401)
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != "manager": return JsonResponse({"error": "Access denied"}, status=403)
    hostel = profile.hostel
    if not hostel: return JsonResponse({"error": "No hostel assigned"}, status=400)
    bookings = Booking.objects.filter(hostel=hostel, booking_status="Checked In").select_related("customer", "room")
    return JsonResponse([{"id": str(b.id), "booking_reference": b.booking_reference, "customer_name": b.customer.get_full_name() or b.customer.email, "customer_email": b.customer.email, "room_number": b.room.room_number, "room_name": b.room.room_name, "check_in": b.check_in.isoformat(), "check_out": b.check_out.isoformat(), "students": b.students, "semesters": b.semesters, "total_price": str(b.total_price)} for b in bookings], safe=False)


@require_http_methods(["POST"])
def manager_checkout(request, booking_id):
    if not request.user.is_authenticated: return JsonResponse({"error": "Auth required"}, status=401)
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != "manager": return JsonResponse({"error": "Access denied"}, status=403)
    hostel = profile.hostel
    if not hostel: return JsonResponse({"error": "No hostel assigned"}, status=400)
    try:
        booking = get_object_or_404(Booking, id=booking_id, hostel=hostel)
        booking.booking_status = "Checked Out"
        booking.save()
        room = booking.room
        if room:
            room.status = "Available"
            room.is_available = True
            room.save(update_fields=["status", "is_available"])
            room.hostel.update_full_status()
        return JsonResponse({"success": True})
    except Exception as e: return JsonResponse({"error": str(e)}, status=400)


@require_http_methods(["GET", "POST"])
def manager_hostel_info(request):
    if not request.user.is_authenticated: return JsonResponse({"error": "Auth required"}, status=401)
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != "manager": return JsonResponse({"error": "Access denied"}, status=403)
    hostel = profile.hostel
    if not hostel: return JsonResponse({"error": "No hostel assigned"}, status=400)
    if request.method == "GET":
        return JsonResponse({
            "id": str(hostel.id), "name": hostel.name, "description": hostel.description,
            "address": hostel.address, "city": hostel.city, "country": hostel.country,
            "university": hostel.university, "distance": hostel.distance,
            "contact": hostel.contact or "", "phone": hostel.phone or "", "email": hostel.email or "",
            "amenities": hostel.amenities or [], "total_floors": hostel.total_floors,
            "available": hostel.available, "is_full": hostel.is_full,
            "check_in_time": hostel.check_in_time.strftime("%H:%M") if hostel.check_in_time else "14:00",
            "check_out_time": hostel.check_out_time.strftime("%H:%M") if hostel.check_out_time else "11:00",
        })
    try:
        data = json.loads(request.body)
        if data.get("name") is not None: hostel.name = data["name"]
        if data.get("description") is not None: hostel.description = data["description"]
        if data.get("address") is not None: hostel.address = data["address"]
        if data.get("city") is not None: hostel.city = data["city"]
        if data.get("country") is not None: hostel.country = data["country"]
        if data.get("university") is not None: hostel.university = data["university"]
        if data.get("distance") is not None: hostel.distance = data["distance"]
        if data.get("contact") is not None: hostel.contact = data["contact"]
        if data.get("phone") is not None: hostel.phone = data["phone"]
        if data.get("email") is not None: hostel.email = data["email"]
        if data.get("amenities") is not None: hostel.amenities = data["amenities"]
        if data.get("total_floors") is not None: hostel.total_floors = int(data["total_floors"])
        if data.get("available") is not None: hostel.available = data["available"] in [True, "true"]
        if data.get("is_full") is not None:
            hostel.is_full = data["is_full"] in [True, "true"]
            hostel.available = not hostel.is_full
        if data.get("check_in_time") is not None:
            from datetime import datetime as dt
            hostel.check_in_time = dt.strptime(data["check_in_time"], "%H:%M").time()
        if data.get("check_out_time") is not None:
            from datetime import datetime as dt
            hostel.check_out_time = dt.strptime(data["check_out_time"], "%H:%M").time()
        hostel.save()
        return JsonResponse({"success": True, "message": "Hostel info updated"})
    except Exception as e: return JsonResponse({"error": str(e)}, status=400)


# ========== ADMIN VIEWS ==========

@login_required
def admin_manager_assign(request):
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != "admin":
        messages.error(request, "Access denied.")
        return redirect("home")

    hostels = Hostel.objects.prefetch_related("managers").order_by("name")
    hostel_payload = [{
        "id": str(hostel.id),
        "name": hostel.name,
        "city": hostel.city,
        "country": hostel.country,
        "managers": [{
            "id": str(manager.id),
            "full_name": manager.full_name,
            "email": manager.email,
        } for manager in hostel.managers.select_related("user").all()],
    } for hostel in hostels]

    managers = Profile.objects.filter(role="manager").select_related("hostel", "user").order_by("full_name")
    manager_payload = [{
        "id": str(manager.id),
        "full_name": manager.full_name,
        "email": manager.email,
        "hostel_id": str(manager.hostel_id) if manager.hostel_id else None,
        "hostel_name": manager.hostel.name if manager.hostel else None,
    } for manager in managers if manager.hostel_id is None]

    return render(request, "admin/manager_assign.html", {
        "hostels_json": json.dumps(hostel_payload),
        "managers_json": json.dumps(manager_payload),
    })


@login_required
@require_http_methods(["GET", "POST"])
def hostel_upload(request):
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != "admin":
        messages.error(request, "Access denied.")
        return redirect("home")
    if request.method == "POST":
        form = HostelUploadForm(request.POST)
        if form.is_valid():
            hostel = Hostel.objects.create(
                name=form.cleaned_data["name"], description=form.cleaned_data["description"] or "",
                address=form.cleaned_data["address"], city=form.cleaned_data["city"],
                country=form.cleaned_data.get("country") or "Uganda",
                university=form.cleaned_data["university"] or "", distance="Near campus",
                price=form.cleaned_data["price_single"] or 0, rating=form.cleaned_data["rating"] or 0,
                amenities=[item.strip() for item in form.cleaned_data["amenities"].split(",") if item.strip()],
                image_url=form.cleaned_data["image_url"] or "",
                total_floors=max(1, int(request.POST.get("floor_count") or 1)),
            )
            room_types = [
                ("Single", form.cleaned_data["price_single"], request.POST.get("room_available_single")),
                ("Double", form.cleaned_data["price_double"], request.POST.get("room_available_double")),
                ("Triple", form.cleaned_data["price_triple"], request.POST.get("room_available_triple")),
                ("Quadruple", form.cleaned_data["price_quadruple"], request.POST.get("room_available_quadruple")),
            ]
            if request.POST.get("room_label_start") or request.POST.get("room_label_end"):
                create_hostel_room_inventory(hostel, room_types, request.POST)
            else:
                for index, (room_type, price, is_avail) in enumerate(room_types, start=1):
                    if price is None or price == 0: continue
                    capacity = 1 if room_type == "Single" else 2 if room_type == "Double" else 3 if room_type == "Triple" else 4
                    Room.objects.create(hostel=hostel, room_number=str(index), room_name=f"{room_type} Room", room_type=room_type, capacity=capacity, available_quantity=1, price_per_semester=price, is_available=is_avail == "on", status="Available" if is_avail == "on" else "Maintenance")
            hostel.update_full_status()
            messages.success(request, "Hostel created successfully.")
            return redirect("hostel_upload")
    else:
        form = HostelUploadForm()
    return render(request, "admin/hostel_upload.html", {"form": form})


@csrf_exempt
@require_http_methods(["POST"])
def admin_assign_manager(request):
    if not request.user.is_authenticated: return JsonResponse({"error": "Auth required"}, status=401)
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != "admin": return JsonResponse({"error": "Access denied"}, status=403)
    try:
        data = json.loads(request.body)
        manager_id, hostel_id = data.get("manager_id"), data.get("hostel_id")
        if not manager_id or not hostel_id: return JsonResponse({"error": "manager_id and hostel_id required"}, status=400)
        manager_profile = get_object_or_404(Profile, id=manager_id, role="manager")
        hostel = get_object_or_404(Hostel, id=hostel_id)
        manager_profile.hostel = hostel; manager_profile.save()
        return JsonResponse({"success": True, "message": f"Manager {manager_profile.full_name} assigned to {hostel.name}"})
    except Exception as e: return JsonResponse({"error": str(e)}, status=400)


@require_http_methods(["POST"])
def admin_remove_manager(request):
    if not request.user.is_authenticated: return JsonResponse({"error": "Auth required"}, status=401)
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != "admin": return JsonResponse({"error": "Access denied"}, status=403)
    try:
        data = json.loads(request.body)
        manager_id = data.get("manager_id")
        if not manager_id: return JsonResponse({"error": "manager_id required"}, status=400)
        manager_profile = get_object_or_404(Profile, id=manager_id, role="manager")
        manager_profile.hostel = None; manager_profile.save()
        return JsonResponse({"success": True})
    except Exception as e: return JsonResponse({"error": str(e)}, status=400)


@require_http_methods(["GET"])
def api_managers(request):
    if not request.user.is_authenticated: return JsonResponse({"error": "Auth required"}, status=401)
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != "admin": return JsonResponse({"error": "Access denied"}, status=403)
    managers = Profile.objects.filter(role="manager").select_related("hostel")
    return JsonResponse([{"id": str(m.id), "full_name": m.full_name, "email": m.email, "hostel_id": str(m.hostel_id) if m.hostel else None, "hostel_name": m.hostel.name if m.hostel else None} for m in managers], safe=False)


@csrf_exempt
@require_http_methods(["POST"])
def admin_create_manager(request):
    if not request.user.is_authenticated: return JsonResponse({"error": "Auth required"}, status=401)
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != "admin": return JsonResponse({"error": "Access denied"}, status=403)
    try:
        data = json.loads(request.body)
        full_name = data.get("full_name", "").strip()
        email = data.get("email", "").strip()
        phone = data.get("phone", "").strip()
        password = data.get("password", "")
        if not full_name or not email or not password: return JsonResponse({"error": "Full name, email, and password required"}, status=400)
        if len(password) < 8: return JsonResponse({"error": "Password must be at least 8 characters"}, status=400)
        if User.objects.filter(email=email).exists(): return JsonResponse({"error": "Email already exists"}, status=400)
        name_parts = full_name.split(" ", 1)
        first_name = name_parts[0] if name_parts else full_name
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        user = User.objects.create(id=str(uuid.uuid4()), email=email, first_name=first_name, last_name=last_name, is_email_verified=True)
        user.set_password(password); user.save()
        Profile.objects.create(user=user, full_name=full_name, email=email, phone=phone or None, role="manager")
        return JsonResponse({"success": True, "message": f"Manager {full_name} created successfully"})
    except Exception as e: return JsonResponse({"error": str(e)}, status=400)


@require_http_methods(["GET"])
def api_unassigned_managers(request):
    if not request.user.is_authenticated: return JsonResponse({"error": "Auth required"}, status=401)
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != "admin": return JsonResponse({"error": "Access denied"}, status=403)
    managers = Profile.objects.filter(role="manager", hostel__isnull=True)
    return JsonResponse([{"id": str(m.id), "full_name": m.full_name, "email": m.email} for m in managers], safe=False)


@require_http_methods(["GET"])
def api_hostel_managers(request, hostel_id):
    if not request.user.is_authenticated: return JsonResponse({"error": "Auth required"}, status=401)
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != "admin": return JsonResponse({"error": "Access denied"}, status=403)
    hostel = get_object_or_404(Hostel, id=hostel_id)
    managers = Profile.objects.filter(role="manager", hostel=hostel)
    return JsonResponse([{"id": str(m.id), "full_name": m.full_name, "email": m.email} for m in managers], safe=False)


# ========== USER VIEWS ==========

@require_http_methods(["GET", "POST"])
def forgot_password(request):
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                user = User.objects.get(email=email)
                from .email_utils import send_password_reset_email
                send_password_reset_email(user, request)
            except User.DoesNotExist: pass
            messages.success(request, "If an account with that email exists, a reset link has been sent.")
            return redirect("login")
    else:
        form = ForgotPasswordForm()
    return render(request, "forgot_password.html", {"form": form})


@require_http_methods(["GET", "POST"])
def reset_password(request, token):
    from .models import PasswordResetToken
    try: reset_token = PasswordResetToken.objects.select_related("user").get(token=token)
    except PasswordResetToken.DoesNotExist:
        return render(request, "password_reset_status.html", {"status": "invalid", "message": "Invalid reset link."})
    if reset_token.is_expired:
        return render(request, "password_reset_status.html", {"status": "expired", "message": "This reset link has expired."})
    if reset_token.is_used:
        return render(request, "password_reset_status.html", {"status": "used", "message": "This link has already been used."})
    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user = reset_token.user
            user.set_password(form.cleaned_data["new_password"]); user.save()
            reset_token.used_at = timezone.now(); reset_token.save()
            messages.success(request, "Your password has been reset."); return redirect("login")
    else:
        form = ResetPasswordForm()
    return render(request, "reset_password.html", {"form": form, "token": token})


@login_required
def profile(request):
    user = request.user
    profile_obj = getattr(user, "profile", None)
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile_obj)
        if form.is_valid():
            form.save()
            user.first_name = request.POST.get("first_name", user.first_name)
            user.last_name = request.POST.get("last_name", user.last_name)
            user.save(update_fields=["first_name", "last_name"])
            messages.success(request, "Profile updated successfully")
            return redirect("profile")
    else:
        form = ProfileUpdateForm(instance=profile_obj)
    return render(request, "profile.html", {"form": form, "profile": profile_obj, "user": user})


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(customer=request.user).select_related("hostel", "room").order_by("-booked_at")
    return render(request, "my_bookings.html", {"bookings": bookings})


# ========== FAVORITES ==========

@login_required
@require_http_methods(["POST"])
def toggle_favorite(request):
    try:
        data = json.loads(request.body)
        hostel = get_object_or_404(Hostel, id=data.get("hostel_id"))
        fav, created = Favorite.objects.get_or_create(customer=request.user, hostel=hostel)
        if not created: fav.delete(); return JsonResponse({"favorited": False})
        return JsonResponse({"favorited": True})
    except Exception as e: return JsonResponse({"error": str(e)}, status=400)


@login_required
def my_favorites(request):
    favorites = Favorite.objects.filter(customer=request.user).select_related("hostel")
    return render(request, "my_favorites.html", {"favorites": favorites})


# ========== BOOKING CANCELLATION ==========

@login_required
@require_http_methods(["POST"])
def cancel_booking(request, booking_id):
    try:
        booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
        if booking.booking_status in ["Checked In", "Checked Out"]:
            return JsonResponse({"error": "Cannot cancel an active or completed booking"}, status=400)
        if booking.booking_status == "Cancelled":
            return JsonResponse({"error": "Booking is already cancelled"}, status=400)
        booking.booking_status = "Cancelled"; booking.payment_status = "Refunded"
        booking.save(update_fields=["booking_status", "payment_status"])
        room = booking.room
        if room:
            room.status = "Available"
            room.is_available = True
            room.save(update_fields=["status", "is_available"])
            room.hostel.update_full_status()
        Notification.objects.create(user=request.user, title="Booking Cancelled", message=f"Booking {booking.booking_reference} cancelled.")
        return JsonResponse({"success": True, "message": "Booking cancelled successfully"})
    except Exception as e: return JsonResponse({"error": str(e)}, status=400)


# ========== NOTIFICATIONS ==========

@login_required
def view_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by("-created_at")
    unread_count = notifications.filter(is_read=False).count()
    return render(request, "notifications.html", {"notifications": notifications, "unread_count": unread_count})


@login_required
@require_http_methods(["GET"])
def api_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by("-created_at")[:20]
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({"notifications": [{"id": str(n.id), "title": n.title, "message": n.message, "is_read": n.is_read, "created_at": n.created_at.isoformat()} for n in notifications], "unread_count": unread_count})


@login_required
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    try:
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.is_read = True; notification.save()
        return JsonResponse({"success": True})
    except Exception as e: return JsonResponse({"error": str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def mark_all_notifications_read(request):
    try:
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({"success": True})
    except Exception as e: return JsonResponse({"error": str(e)}, status=400)


# ========== PAYMENT ==========

@csrf_exempt
@require_http_methods(["POST"])
def process_payment(request):
    if not request.user.is_authenticated: return JsonResponse({"error": "Auth required"}, status=401)
    try:
        data = json.loads(request.body)
        booking = get_object_or_404(Booking, id=data.get("booking_id"), customer=request.user)
        payment_method = data.get("payment_method", "Mobile Money")
        transaction_ref = data.get("transaction_reference") or f"TXN-{uuid.uuid4().hex[:12].upper()}"
        payment = Payment.objects.create(booking=booking, amount=booking.total_price, payment_method=payment_method, payment_status="Paid", transaction_reference=transaction_ref, paid_at=timezone.now())
        booking.payment_status = "Paid"
        booking.booking_status = "Confirmed"
        booking.save(update_fields=["payment_status", "booking_status"])
        try:
            send_booking_receipt(booking, request)
        except Exception:
            pass
        return JsonResponse({"success": True, "payment_id": str(payment.id)})
    except Exception as e: return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def verify_payment(request):
    return JsonResponse({"success": True, "message": "Payment verified"})


@csrf_exempt
@require_http_methods(["POST"])
def flutterwave_validate_payment(request):
    return JsonResponse({"success": True, "message": "Payment validated"})


@csrf_exempt
@require_http_methods(["POST"])
def flutterwave_webhook(request):
    return JsonResponse({"status": "received"})


@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    return JsonResponse({"status": "received"})


@csrf_exempt
@require_http_methods(["POST"])
def create_stripe_checkout_session(request):
    return JsonResponse({"error": "Stripe not configured"}, status=400)


@login_required
def payment_success(request):
    return render(request, "payment_success.html")


# ========== ROOMMATE FINDER ==========

from .models import RoommateRequest, ChatRoom, ChatMessage


@require_http_methods(["GET", "POST"])
def roommate_finder(request):
    if request.method == "POST":
        if not request.user.is_authenticated: return JsonResponse({"error": "Auth required"}, status=401)
        try:
            data = json.loads(request.body)
            req = RoommateRequest.objects.create(user=request.user, hostel_id=data.get("hostel_id"), room_id=data.get("room_id") or None, preferred_gender=data.get("preferred_gender", "any"), budget_min=data.get("budget_min") or None, budget_max=data.get("budget_max") or None, about_me=data.get("about_me", ""), lifestyle_preferences=data.get("lifestyle_preferences", []))
            return JsonResponse({"success": True, "request_id": str(req.id)}, status=201)
        except Exception as e: return JsonResponse({"error": str(e)}, status=400)
    return render(request, "roommate_finder.html")


@login_required
def my_chat_rooms(request):
    chat_rooms = ChatRoom.objects.filter(participants=request.user).order_by("-updated_at")
    return render(request, "my_chat_rooms.html", {"chat_rooms": chat_rooms})


@login_required
def chat_room_detail(request, room_id):
    chat_room = get_object_or_404(ChatRoom, id=room_id, participants=request.user)
    messages = chat_room.messages.select_related("sender", "reply_to").all().order_by("created_at")
    return render(request, "chatbox.html", {"room": chat_room, "messages": messages, "chat_room": chat_room})


@require_http_methods(["GET", "POST"])
def api_roommate_requests(request):
    if request.method == "GET":
        hostel_id = request.GET.get("hostel_id")
        room_id = request.GET.get("room_id")
        qs = RoommateRequest.objects.filter(is_active=True).select_related("user", "hostel", "room")
        if hostel_id: qs = qs.filter(hostel_id=hostel_id)
        if room_id: qs = qs.filter(room_id=room_id)
        return JsonResponse([{"id": str(r.id), "user_id": str(r.user.id), "user_name": r.user.get_full_name() or r.user.email, "hostel_id": str(r.hostel_id), "hostel_name": r.hostel.name, "room_id": str(r.room_id) if r.room else None, "preferred_gender": r.preferred_gender, "budget_min": str(r.budget_min) if r.budget_min else None, "budget_max": str(r.budget_max) if r.budget_max else None, "about_me": r.about_me, "lifestyle_preferences": r.lifestyle_preferences, "created_at": r.created_at.isoformat()} for r in qs], safe=False)
    if not request.user.is_authenticated: return JsonResponse({"error": "Auth required"}, status=401)
    try:
        data = json.loads(request.body)
        req = RoommateRequest.objects.create(user=request.user, hostel_id=data.get("hostel_id"), room_id=data.get("room_id") or None, preferred_gender=data.get("preferred_gender", "any"), about_me=data.get("about_me", ""))
        return JsonResponse({"success": True, "request_id": str(req.id)}, status=201)
    except Exception as e: return JsonResponse({"error": str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def api_roommate_request_toggle(request, request_id):
    try:
        req = get_object_or_404(RoommateRequest, id=request_id, user=request.user)
        req.is_active = not req.is_active
        req.save()
        return JsonResponse({"success": True, "is_active": req.is_active})
    except Exception as e: return JsonResponse({"error": str(e)}, status=400)


@login_required
@require_http_methods(["GET", "POST"])
def api_chat_rooms(request):
    if request.method == "GET":
        chat_rooms = ChatRoom.objects.filter(participants=request.user).order_by("-updated_at")
        return JsonResponse([{"id": str(cr.id), "hostel_id": str(cr.hostel_id), "hostel_name": cr.hostel.name, "participants": [{"id": str(p.id), "name": p.get_full_name() or p.email} for p in cr.participants.all()], "last_message": cr.last_message.content[:100] if cr.last_message else None, "last_message_time": cr.last_message.created_at.isoformat() if cr.last_message else None, "created_at": cr.created_at.isoformat()} for cr in chat_rooms], safe=False)
    try:
        data = json.loads(request.body)
        other_user_id = data.get("other_user_id")
        hostel_id = data.get("hostel_id")
        if not other_user_id or not hostel_id: return JsonResponse({"error": "other_user_id and hostel_id required"}, status=400)
        existing = ChatRoom.objects.filter(hostel_id=hostel_id, participants=request.user).filter(participants__id=other_user_id).first()
        if existing: return JsonResponse({"id": str(existing.id), "existing": True})
        cr = ChatRoom.objects.create(hostel_id=hostel_id)
        cr.participants.add(request.user, other_user_id)
        return JsonResponse({"id": str(cr.id), "existing": False}, status=201)
    except Exception as e: return JsonResponse({"error": str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def api_send_message(request, room_id):
    try:
        chat_room = get_object_or_404(ChatRoom, id=room_id, participants=request.user)
        reply_to = None
        if request.POST:
            content = request.POST.get('content', '').strip()
            reply_to_id = request.POST.get('reply_to_id')
            image = request.FILES.get('image') if request.FILES else None
            if reply_to_id:
                reply_to = get_object_or_404(ChatMessage, id=reply_to_id, chat_room=chat_room)
            if image:
                msg = ChatMessage.objects.create(chat_room=chat_room, sender=request.user, image=image, reply_to=reply_to, is_ai=False)
            else:
                if not content:
                    return JsonResponse({"error": "Message content is required"}, status=400)
                msg = ChatMessage.objects.create(chat_room=chat_room, sender=request.user, content=content, reply_to=reply_to, is_ai=False)
        else:
            data = json.loads(request.body or '{}')
            content = data.get('content', '').strip()
            reply_to_id = data.get('reply_to_id')
            if reply_to_id:
                reply_to = get_object_or_404(ChatMessage, id=reply_to_id, chat_room=chat_room)
            if not content:
                return JsonResponse({"error": "Message content is required"}, status=400)
            msg = ChatMessage.objects.create(chat_room=chat_room, sender=request.user, content=content, reply_to=reply_to, is_ai=False)
        chat_room.save(update_fields=['updated_at'])
        return JsonResponse({"success": True, "id": str(msg.id), "sender_id": str(msg.sender_id), "sender_name": request.user.get_full_name() or request.user.email, "content": msg.content, "image_url": msg.image.url if msg.image else None, "reply_to_id": str(msg.reply_to_id) if msg.reply_to_id else None, "created_at": msg.created_at.isoformat()}, status=201)
    except Exception as e: return JsonResponse({"error": str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def api_chat_messages(request, room_id):
    try:
        chat_room = get_object_or_404(ChatRoom, id=room_id, participants=request.user)
        messages_qs = chat_room.messages.select_related("sender", "reply_to").all().order_by("created_at")
        messages_qs.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
        payload = [{"id": str(m.id), "sender_id": str(m.sender_id) if m.sender else "AI", "sender_name": m.sender.get_full_name() or m.sender.email if m.sender else "AI Assistant", "content": m.content, "image_url": m.image.url if m.image else None, "is_ai": m.is_ai, "is_read": m.is_read, "reply_to_id": str(m.reply_to_id) if m.reply_to_id else None, "reply_to_content": m.reply_to.content if m.reply_to else None, "created_at": m.created_at.isoformat()} for m in messages_qs]
        return JsonResponse({"messages": payload}, safe=False)
    except Exception as e: return JsonResponse({"error": str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def api_delete_message(request, room_id, message_id):
    try:
        msg = get_object_or_404(ChatMessage, id=message_id, chat_room_id=room_id, sender=request.user)
        msg.delete()
        return JsonResponse({"success": True})
    except Exception as e: return JsonResponse({"error": str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def api_clear_chat(request, room_id):
    try:
        chat_room = get_object_or_404(ChatRoom, id=room_id, participants=request.user)
        deleted_count = chat_room.messages.count()
        chat_room.messages.all().delete()
        return JsonResponse({"success": True, "deleted_count": deleted_count})
    except Exception as e: return JsonResponse({"error": str(e)}, status=400)


# ========== ERROR HANDLERS ==========

def custom_404(request, exception):
    return render(request, "404.html", status=404)


def custom_500(request):
    return render(request, "500.html", status=500)
