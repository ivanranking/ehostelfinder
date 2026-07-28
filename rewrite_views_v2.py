#!/usr/bin/env python3
"""Write a clean views.py with all required functions."""
import ast, os

os.chdir('c:/Users/user/ehostelfinder')
content = r'''
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
import json, os, urllib.request, urllib.error, uuid
from .forms import UserRegistrationForm, UserLoginForm, ForgotPasswordForm, ResetPasswordForm, ProfileUpdateForm, HostelUploadForm
from .models import Hostel, User, ContactMessage, Profile, Room, Booking, Review, Favorite, Message, Notification, Payment, RoomStatus, BookingStatus
from .local_ai import get_local_ai_response

KAMPALA_AREA_UNIVERSITIES = ["Makerere University", "Makerere University Business School", "Kyambogo University", "Kampala International University", "Uganda Christian University", "Ndejje University", "Bugema University", "Cavendish University Uganda", "St. Lawrence University Uganda", "Mutesa I Royal University"]

def get_university_options():
    university_names, seen = [], set()
    for name in KAMPALA_AREA_UNIVERSITIES + list(Hostel.objects.exclude(university="").values_list("university", flat=True)):
        normalized = name.strip() if name else ""
        if not normalized or normalized.lower() in seen:
            continue
        university_names.append(normalized)
        seen.add(normalized.lower())
    return [{"name": n} for n in sorted(university_names)]

def home(request):
    university = request.GET.get("university", "All Universities")
    city = request.GET.get("city", "")
    country = request.GET.get("country", "")
    min_price = request.GET.get("min_price", "")
    max_price = request.GET.get("max_price", "")
    sort_by = request.GET.get("sort", "-created_at")
    page = request.GET.get("page", 1)
    valid_sorts = ["name", "-name", "price", "-price", "rating", "-rating", "created_at", "-created_at"]
    if sort_by not in valid_sorts:
        sort_by = "-created_at"
    hostels = Hostel.objects.all()
    if university and university != "All Universities":
        hostels = hostels.filter(university=university)
    if city:
        hostels = hostels.filter(city__icontains=city)
    if country:
        hostels = hostels.filter(country__icontains=country)
    if min_price:
        try:
            hostels = hostels.filter(price__gte=float(min_price)).distinct()
        except:
            pass
    if max_price:
        try:
            hostels = hostels.filter(price__lte=float(max_price)).distinct()
        except:
            pass
    hostels = hostels.order_by(sort_by)
    paginator = Paginator(hostels, 12)
    try:
        page_obj = paginator.page(page)
    except:
        page_obj = paginator.page(1)
    cities_list = sorted(Hostel.objects.values_list("city", flat=True).exclude(city="").distinct())
    countries_list = sorted(Hostel.objects.values_list("country", flat=True).exclude(country="").distinct())
    universities = get_university_options()
    rated_hostels = Hostel.objects.exclude(rating__isnull=True)
    avg_rating = 0.0
    if rated_hostels.exists():
        avg = sum(float(h.rating) for h in rated_hostels) / rated_hostels.count()
        avg_rating = round(avg, 1)
    hostel_list = []
    for h in page_obj:
        cover = h.images.filter(is_cover=True).first()
        avail_room = h.rooms.filter(status="Available").first()
        hostel_list.append({
            "id": str(h.id), "name": h.name, "description": h.description,
            "city": h.city, "country": h.country, "university": h.university,
            "image_url": h.image_url or (cover.image_url if cover else None),
            "facilities": [{"name": f.facility_name, "icon": f.icon or ""} for f in h.facilities.all()],
            "available": h.available,
            "rating": float(h.rating) if h.rating else round(float(h.average_rating), 1),
            "distance": h.distance or "Near campus",
            "price": str(h.price) if h.price else (str(avail_room.price_per_night) if avail_room else "0"),
            "amenities": h.amenities or [],
        })
    favorite_ids = []
    if request.user.is_authenticated:
        favorite_ids = list(Favorite.objects.filter(customer=request.user).values_list("hostel_id", flat=True))
    return render(request, "home.html", {
        "hostels": hostel_list, "cities": cities_list, "countries": countries_list,
        "universities": universities, "selected_city": city, "selected_country": country,
        "selected_university": university, "selected_sort": sort_by,
        "total_hostels": Hostel.objects.count(), "total_universities": len(universities),
        "avg_rating": avg_rating, "total_cities": len(cities_list),
        "page_obj": page_obj, "favorite_ids": [str(fid) for fid in favorite_ids],
    })

def hostel_detail(request, id):
    try:
        hostel = get_object_or_404(Hostel, id=id)
        rooms = Room.objects.filter(hostel=hostel, status="Available")
        images = hostel.images.all()
        cover = hostel.images.filter(is_cover=True).first()
        facilities = hostel.facilities.all()
        reviews = hostel.reviews.select_related("customer").all()
        rooms_data = [{
            "id": str(r.id), "room_number": r.room_number, "room_name": r.room_name,
            "room_type": r.room_type, "capacity": r.capacity, "available_quantity": r.available_quantity,
            "price_per_night": str(r.price_per_night), "description": r.description,
            "size_sq_meters": str(r.size_sq_meters) if r.size_sq_meters else None,
            "private_bathroom": r.private_bathroom, "air_conditioning": r.air_conditioning,
            "balcony": r.balcony, "television": r.television, "wifi": r.wifi,
            "images": [ri.image_url for ri in r.images.all()],
        } for r in rooms]
        reviews_data = [{
            "id": str(rv.id), "customer_name": rv.customer.get_full_name() or rv.customer.email,
            "rating": rv.rating, "comment": rv.comment, "created_at": rv.created_at.strftime("%Y-%m-%d"),
        } for rv in reviews]
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
            "rooms": rooms_data, "facilities": [{"name": f.facility_name, "icon": f.icon or ""} for f in facilities],
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
    try:
        if min_price: hostels = hostels.filter(price__gte=float(min_price))
        if max_price: hostels = hostels.filter(price__lte=float(max_price))
    except: pass
    results = []
    for h in hostels:
        cover = h.images.filter(is_cover=True).first()
        results.append({
            "id": str(h.id), "name": h.name, "city": h.city, "country": h.country,
            "university": h.university, "address": h.address, "description": h.description,
            "average_rating": round(float(h.average_rating), 2),
            "rating": float(h.rating) if h.rating else round(float(h.average_rating), 2),
            "review_count": h.reviews.count(),
            "image_url": h.image_url or (cover.image_url if cover else None),
            "facilities": [f.facility_name for f in h.facilities.all()],
            "amenities": h.amenities or [], "distance": h.distance or "",
            "price": float(h.price) if h.price else 0,
            "contact": h.contact or "", "available": h.available,
        })
    return JsonResponse(results, safe=False)

@require_http_methods(["GET"])
def api_hostel_detail(request, id):
    hostel = get_object_or_404(Hostel, id=id)
    rooms = Room.objects.filter(hostel=hostel)
    cover = hostel.images.filter(is_cover=True).first()
    rooms_data = [{
        "id": str(r.id), "room_number": r.room_number, "room_name": r.room_name,
        "room_type": r.room_type, "capacity": r.capacity, "available_quantity": r.available_quantity,
        "price_per_night": str(r.price_per_night), "description": r.description,
        "private_bathroom": r.private_bathroom, "air_conditioning": r.air_conditioning, "wifi": r.wifi,
        "status": r.status,
    } for r in rooms]
    return JsonResponse({
        "id": str(hostel.id), "name": hostel.name, "description": hostel.description,
        "address": hostel.address, "city": hostel.city, "country": hostel.country,
        "phone": hostel.phone, "email": hostel.email,
        "latitude": str(hostel.latitude) if hostel.latitude else None,
        "longitude": str(hostel.longitude) if hostel.longitude else None,
        "image_url": cover.image_url if cover else None, "rooms": rooms_data,
        "facilities": [{"name": f.facility_name} for f in hostel.facilities.all()],
    })

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
        user = authenticate(request, username=form.cleaned_data["email"], password=form.cleaned_data["password"])
        if user:
            auth_login(request, user)
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
            except Exception:
                pass
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

@login_required
def admin_messages(request):
    msgs = ContactMessage.objects.all()[:100]
    return JsonResponse({"messages": [{
        "id": msg.id, "full_name": msg.full_name, "email": msg.email,
        "subject": msg.subject, "message": msg.message,
        "created_at": msg.created_at.isoformat(), "is_read": msg.is_read,
    } for msg in msgs]})

@require_http_methods(["GET", "POST"])
def get_user(request):
    if request.user.is_authenticated:
        p = getattr(request.user, "profile", None)
        return JsonResponse({
            "id": request.user.id, "email": request.user.email,
            "first_name": request.user.first_name, "last_name": request.user.last_name,
            "profile_image_url": p.profile_photo if p else None,
            "role": p.role if p else "customer", "full_name": p.full_name if p else "",
        })
    return JsonResponse({"error": "Not authenticated"}, status=401)

@require_http_methods(["POST"])
def create_booking(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Auth required"}, status=401)
    try:
        from datetime import datetime
        data = json.loads(request.body)
        room = get_object_or_404(Room, id=data.get("room_id"))
        check_in = datetime.strptime(data.get("check_in"), "%Y-%m-%d").date()
        check_out = datetime.strptime(data.get("check_out"), "%Y-%m-%d").date()
        guests = int(data.get("guests", 1))
        nights = (check_out - check_in).days
        if nights <= 0:
            return JsonResponse({"error": "Invalid date range"}, status=400)
        total_price = room.price_per_night * nights
        booking = Booking.objects.create(
            hostel_id=room.hostel_id, room=room, customer_id=request.user.id,
            check_in=check_in, check_out=check_out, guests=guests, nights=nights,
            total_price=total_price, special_requests=data.get("special_requests", ""),
            booking_status="Pending", payment_status="Pending",
        )
        Notification.objects.create(
            user=request.user, title="Booking Created",
            message=f"Booking at {room.hostel.name} (Ref: {booking.booking_reference}) created.",
        )
        return JsonResponse({
            "id": str(booking.id), "booking_reference": booking.booking_reference,
            "check_in": booking.check_in.isoformat(), "check_out": booking.check_out.isoformat(),
            "guests": guests, "nights": nights, "total_price": str(total_price),
            "booking_status": "Pending", "payment_status": "Pending",
        }, status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@require_http_methods(["GET"])
def get_booking_by_id(request, id):
    try:
        booking = get_object_or_404(Booking, id=id)
        if request.user.id == booking.customer_id:
            return JsonResponse({
                "id": str(booking.id), "booking_reference": booking.booking_reference,
                "check_in": booking.check_in.isoformat(), "check_out": booking.check_out.isoformat(),
                "guests": booking.guests, "nights": booking.nights,
                "total_price": str(booking.total_price), "booking_status": booking.booking_status,
                "payment_status": booking.payment_status,
            })
        return JsonResponse({"error": "Not authorized"}, status=403)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@require_http_methods(["POST"])
def create_message(request):
    try:
        data = json.loads(request.body)
        hostel = get_object_or_404(Hostel, id=data.get("hostelId"))
        msg = Message.objects.create(
            hostel=hostel, user=request.user if request.user.is_authenticated else None,
            full_name=data.get("fullName", ""), email=data.get("email", ""),
            phone=data.get("phone", ""), subject=data.get("subject", ""),
            content=data.get("content", "") or data.get("message", ""),
        )
        return JsonResponse({"id": str(msg.id), "created_at": msg.created_at.isoformat()}, status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def ai_chat(request):
    try:
        question = json.loads(request.body).get("question", "").strip()
        if not question:
            return JsonResponse({"error": "Question required"}, status=400)
        api_key = os.getenv("GOOGLE_GENERATIVE_API_KEY")
        if api_key:
            try:
                prompt = f"You are a hostel assistant for EHostelFinder. Question: {question}"
                payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
                req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return JsonResponse(json.loads(resp.read().decode("utf-8")))
            except Exception:
                pass
        return JsonResponse({"candidates": [{"content": {"parts": [{"text": get_local_ai_response(question)}]}}]})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@require_http_methods(["GET"])
def get_messages_by_hostel(request, hostel_id):
    msgs = Message.objects.filter(hostel_id=hostel_id)
    return JsonResponse([{
        "id": str(m.id), "hostel_id": str(m.hostel_id), "full_name": m.full_name,
        "email": m.email, "subject": m.subject, "message": m.content,
        "created_at": m.created_at.isoformat(),
    } for m in msgs], safe=False)

@require_http_methods(["GET"])
def universities(request):
    uni_options = get_university_options()
    unis = []
    for uni in uni_options:
        name = uni["name"]
        count = Hostel.objects.filter(university=name).count()
        top = Hostel.objects.filter(university=name).order_by("-rating").first()
        unis.append({
            "name": name, "count": count,
            "top_hostel": top.name if top else "",
            "rating": float(top.rating) if top and top.rating else 0,
        })
    unis.sort(key=lambda x: x["name"])
    return render(request, "universities.html", {"universities": unis})

@csrf_exempt
def contact(request):
    if request.method == "POST":
        try:
            ContactMessage.objects.create(
                full_name=request.POST.get("name", ""), email=request.POST.get("email", ""),
                subject=request.POST.get("subject", ""), message=request.POST.get("message", ""),
            )
            return JsonResponse({"success": True, "message": "Message sent!"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return render(request, "contact.html")

def google_auth(request):
    import urllib.parse
    from django.conf import settings
    redirect_uri = request.build_absolute_uri("/api/auth/google/callback/")
    params = {"client_id": settings.GOOGLE_CLIENT_ID, "redirect_uri": redirect_uri,
              "response_type": "code", "scope": "email profile", "access_type": "online"}
    return redirect(f"https://accounts.google.com/o/oauth2/auth?{urllib.parse.urlencode(params)}")

def google_auth_callback(request):
    import urllib.parse
    from django.conf import settings
    from django.contrib.auth import login as auth_login
    code = request.GET.get("code")
    if not code:
        messages.error(request, "Google auth failed")
        return redirect("login")
    redirect_uri = request.build_absolute_uri("/api/auth/google/callback/")
    token_data = urllib.parse.urlencode({
        "code": code, "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": redirect_uri, "grant_type": "authorization_code",
    }).encode()
    try:
        req = urllib.request.Request("https://oauth2.googleapis.com/token", data=token_data, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        with urllib.request.urlopen(req, timeout=10) as resp:
            token_result = json.loads(resp.read().decode())
        user_req = urllib.request.Request(
            f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={token_result.get('access_token')}"
        )
        with urllib.request.urlopen(user_req, timeout=10) as resp:
            user_info = json.loads(resp.read().decode())
        email = user_info.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create(
                id=str(uuid.uuid4()), email=email,
                first_name=user_info.get("given_name", email.split("@")[0]),
                last_name=user_info.get("family_name", ""), provider="google",
            )
        auth_login(request, user)
        return redirect("home")
    except Exception as e:
        messages.error(request, f"Google auth failed: {e}")
        return redirect("login")

@login_required
def manager_dashboard(request):
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != "manager":
        messages.error(request, "Access denied.")
        return redirect("home")
    if not profile.hostel:
        messages.error(request, "No hostel assigned.")
        return redirect("home")
    return render(request, "manager/dashboard.html", {"hostel": profile.hostel})

@login_required
def admin_manager_assign(request):
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != "admin":
        messages.error(request, "Access denied.")
        return redirect("home")
    return render(request, "admin/manager_assign.html")

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
            cd = form.cleaned_data
            hostel = Hostel.objects.create(
                name=cd["name"], description=cd.get("description", "") or "",
                address=cd["address"], city=cd["city"],
                country=cd.get("country") or "Uganda",
                university=cd.get("university", "") or "", distance="Near campus",
                price=cd.get("price_single") or 0, rating=cd.get("rating") or 0,
                amenities=[x.strip() for x in cd.get("amenities", "").split(",") if x.strip()],
                image_url=cd.get("image_url", "") or "",
            )
            for idx, (rt, price, avail) in enumerate([
                ("Single", cd.get("price_single"), request.POST.get("room_available_single")),
                ("Double", cd.get("price_double"), request.POST.get("room_available_double")),
                ("Triple", cd.get("price_triple"), request.POST.get("room_available_triple")),
                ("Quadruple", cd.get("price_quadruple"), request.POST.get("room_available_quadruple")),
            ], 1):
                if price and price > 0:
                    cap = {"Single": 1, "Double": 2, "Triple": 3, "Quadruple": 4}.get(rt, 1)
                    Room.objects.create(
                        hostel=hostel, room_number=str(idx), room_name=f"{rt} Room",
                        room_type=rt, capacity=cap, available_quantity=1,
                        price_per_night=price, is_available=avail == "on",
                    )
            messages.success(request, "Hostel created.")
            return redirect("hostel_upload")
    else:
        form = HostelUploadForm()
    return render(request, "admin/hostel_upload.html", {"form": form})

@require_http_methods(["GET"])
def manager_bookings(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Auth required"}, status=401)
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != "manager":
        return JsonResponse({"error": "Access denied"}, status=403)
    hostel = profile.hostel
    if not hostel:
        return JsonResponse({"error": "No hostel"}, status=400)
    bookings = Booking.objects.filter(hostel=hostel).select_related("customer", "room").order_by("-booked_at")
    return JsonResponse([{
        "id": str(b.id), "booking_reference": b.booking_reference,
        "customer_name": b.customer.get_full_name() or b.customer.email,
        "customer_email": b.customer.email, "room_number": b.room.room_number,
        "room_name": b.room.room_name, "check_in": b.check_in.isoformat(),
        "check_out": b.check_out.isoformat(), "guests": b.guests, "nights": b.nights,
        "total_price": str(b.total_price), "booking_status": b.booking_status,
        "payment_status": b.payment_status, "special_requests": b.special_requests or "",
    } for b in bookings], safe=False)

@require_http_methods(["POST"])
def manager_update_booking(request, booking_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Auth required"}, status=401)
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != "manager":
        return JsonResponse({"error": "Access denied"}, status=403)
    hostel = profile.hostel
    if not hostel:
        return JsonResponse({"error": "No hostel"}, status=400)
    try:
        data = json.loads(request.body)
        booking = get_object_or_404(Booking, id=booking_id, hostel=hostel)
        new_status = data.get("booking_status")
        if new_status and new_status in dict(BookingStatus.choices).keys():
            booking.booking_status = new_status
            booking.save(update_fields=["booking_status"])
            Notification.objects.create(
                user=booking.customer, title="Booking Updated",
                message=f"Booking {booking.booking_reference} is now {new_status}.",
            )
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@require_http_methods(["GET"])
def manager_checkins(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Auth required"}, status=401)
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != "manager":
        return JsonResponse({"error": "Access denied"}, status=403)
    hostel = profile.hostel
    if not hostel:
        return JsonResponse({"error": "No hostel"}, status=400)
    bookings = Booking.objects.filter(hostel=hostel, booking_status="Checked In").select_related("customer", "room")
    return JsonResponse([{
        "id": str(b.id), "booking_reference": b.booking_reference,
        "customer_name": b.customer.get_full_name() or b.customer.email,
        "customer_email": b.customer.email, "room_number": b.room.room_number,
        "room_name": b.room.room_name, "check_in": b.check_in.isoformat(),
        "check_out": b.check_out.isoformat(), "guests": b.guests,
        "total_price": str(b.total_price),
    } for b in bookings], safe=False)

@require_http_methods(["GET", "POST"])
def manager_rooms(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Auth required"}, status=401)
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != "manager":
        return JsonResponse({"error": "Access denied"}, status=403)
    hostel = profile.hostel
    if not hostel:
        return JsonResponse({"error": "No hostel"}, status=400)
    if request.method == "GET":
        rooms = Room.objects.filter(hostel=hostel)
        return JsonResponse([{
            "id": str(r.id), "room_number": r.room_number, "room_name": r.room_name,
            "room_type": r.room_type, "capacity": r.capacity,
            "available_quantity": r.available_quantity, "price_per_night": str(r.price_per_night),
            "status": r.status, "is_available": r.is_available,
        } for r in rooms], safe=False)
    try:
        data = json.loads(request.body)
        room = get_object_or_404(Room, id=data.get("room_id"), hostel=hostel)
        s = data.get("status")
        if s and s in dict(RoomStatus.choices).keys():
            room.status = s
            room.is_available = s == "Available"
        if data.get("is_available") is not None:
            room.is_available = data["is_available"] in [True, "true"]
        if data.get("available_quantity") is not None:
            room.available_quantity = int(data["available_quantity"])
        room.save()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def admin_assign_manager(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Auth required"}, status=401)
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != "admin":
        return JsonResponse({"error": "Access denied"}, status=403)
    try:
        data = json.loads(request.body)
        manager_id, hostel_id = data.get("manager_id"), data.get("hostel_id")
        if not manager_id or not hostel_id:
            return JsonResponse({"error": "manager_id and hostel_id required"}, status=400)
        mp = get_object_or_404(Profile, id=manager_id, role="manager")
        mp.hostel = get_object_or_404(Hostel, id=hostel_id)
        mp.save()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@require_http_methods(["POST"])
def admin_remove_manager(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Auth required"}, status=401)
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != "admin":
        return JsonResponse({"error": "Access denied"}, status=403)
    try:
        mp = get_object_or_404(Profile, id=json.loads(request.body).get("manager_id"), role="manager")
        mp.hostel = None
        mp.save()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@require_http_methods(["GET"])
def api_managers(request):
    if not request.user.is_authenticated or getattr(getattr(request.user, "profile", None), "role", "") != "admin":
        return JsonResponse({"error": "Access denied"}, status=403)
    managers = Profile.objects.filter(role="manager").select_related("hostel")
    return JsonResponse([{
        "id": str(m.id), "full_name": m.full_name, "email": m.email,
        "hostel_id": str(m.hostel_id) if m.hostel else None,
        "hostel_name": m.hostel.name if m.hostel else None,
    } for m in managers], safe=False)

@csrf_exempt
@require_http_methods(["POST"])
def admin_create_manager(request):
    if not request.user.is_authenticated or getattr(getattr(request.user, "profile", None), "role", "") != "admin":
        return JsonResponse({"error": "Access denied"}, status=403)
    try:
        data = json.loads(request.body)
        full_name, email, password = data.get("full_name", "").strip(), data.get("email", "").strip(), data.get("password", "")
        if not full_name or not email or not password:
            return JsonResponse({"error": "Fields required"}, status=400)
        if len(password) < 8:
            return JsonResponse({"error": "Password min 8 chars"}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email exists"}, status=400)
        parts = full_name.split(" ", 1)
        user = User.objects.create(id=str(uuid.uuid4()), email=email, first_name=parts[0], last_name=parts[1] if len(parts) > 1 else "", is_email_verified=True)
        user.set_password(password)
        user.save()
        Profile.objects.create(user=user, full_name=full_name, email=email, role="manager")
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@require_http_methods(["GET"])
def api_unassigned_managers(request):
    if not request.user.is_authenticated or getattr(getattr(request.user, "profile", None), "role", "") != "admin":
        return JsonResponse({"error": "Access denied"}, status=403)
    managers = Profile.objects.filter(role="manager", hostel__isnull=True)
    return JsonResponse([{"id": str(m.id), "full_name": m.full_name, "email": m.email} for m in managers], safe=False)

@require_http_methods(["GET"])
def api_hostel_managers(request, hostel_id):
    if not request.user.is_authenticated or getattr(getattr(request.user, "profile", None), "role", "") != "admin":
        return JsonResponse({"error": "Access denied"}, status=403)
    hostel = get_object_or_404(Hostel, id=hostel_id)
    managers = Profile.objects.filter(role="manager", hostel=hostel)
    return JsonResponse([{"id": str(m.id), "full_name": m.full_name, "email": m.email} for m in managers], safe=False)

@require_http_methods(["POST"])
def manager_checkout(request, booking_id):
    if not request.user.is_authenticated or getattr(getattr(request.user, "profile", None), "role", "") != "manager":
        return JsonResponse({"error": "Access denied"}, status=403)
    if not getattr(getattr(request.user, "profile", None), "hostel", None):
        return JsonResponse({"error": "No hostel"}, status=400)
    try:
        booking = get_object_or_404(Booking, id=booking_id, hostel=request.user.profile.hostel)
        booking.booking_status = "Checked Out"
        booking.save()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@require_http_methods(["GET", "POST"])
def forgot_password(request):
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(email=form.cleaned_data["email"])
                from .email_utils import send_password_reset_email
                send_password_reset_email(user, request)
            except User.DoesNotExist:
                pass
            messages.success(request, "If an account exists, a reset link has been sent.")
            return redirect("login")
    else:
        form = ForgotPasswordForm()
    return render(request, "forgot_password.html", {"form": form})

@require_http_methods(["GET", "POST"])
def reset_password(request, token):
    from .models import PasswordResetToken
    try:
        reset_token = PasswordResetToken.objects.select_related("user").get(token=token)
    except PasswordResetToken.DoesNotExist:
        return render(request, "password_reset_status.html", {"status": "invalid", "message": "Invalid link."})
    if reset_token.is_expired:
        return render(request, "password_reset_status.html", {"status": "expired", "message": "Link expired."})
    if reset_token.is_used:
        return render(request, "password_reset_status.html", {"status": "used", "message": "Link already used."})
    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user = reset_token.user
            user.set_password(form.cleaned_data["new_password"])
            user.save()
            reset_token.used_at = timezone.now()
            reset_token.save()
            messages.success(request, "Password reset successfully.")
            return redirect("login")
    else:
        form = ResetPasswordForm()
    return render(request, "reset_password.html", {"form": form, "token": token})

@login_required
def profile(request):
    user = request.user
    profile_obj = getattr(user, "profile", None)
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=profile_obj)
        if form.is_valid():
            form.save()
            user.first_name = request.POST.get("first_name", user.first_name)
            user.last_name = request.POST.get("last_name", user.last_name)
            user.save(update_fields=["first_name", "last_name"])
            messages.success(request, "Profile updated.")
            return redirect("profile")
    else:
        form = ProfileUpdateForm(instance=profile_obj)
    return render(request, "profile.html", {"form": form, "profile": profile_obj})

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(customer=request.user).select_related("hostel", "room").order_by("-booked_at")
    return render(request, "my_bookings.html", {"bookings": bookings})

@login_required
@require_http_methods(["POST"])
def toggle_favorite(request):
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

@login_required
def my_favorites(request):
    favorites = Favorite.objects.filter(customer=request.user).select_related("hostel")
    hostel_list = []
    for fav in favorites:
        h = fav.hostel
        cover = h.images.filter(is_cover=True).first()
        avail = h.rooms.filter(status="Available").first()
        hostel_list.append({
            "id": str(h.id), "name": h.name, "city": h.city, "country": h.country,
            "university": h.university,
            "image_url": h.image_url or (cover.image_url if cover else None),
            "rating": float(h.rating) if h.rating else round(float(h.average_rating), 1),
            "price": str(h.price) if h.price else (str(avail.price_per_night) if avail else "0"),
        })
    return render(request, "my_favorites.html", {"hostels": hostel_list})

@login_required
def view_notifications(request):
    return render(request, "notifications.html", {"notifications": Notification.objects.filter(user=request.user).order_by("-created_at")})

@login_required
@require_http_methods(["GET"])
def api_notifications(request):
    data = [{
        "id": str(n.id), "title": n.title, "message": n.message,
        "is_read": n.is_read, "created_at": n.created_at.isoformat(),
    } for n in Notification.objects.filter(user=request.user).order_by("-created_at")[:50]]
    return JsonResponse(data, safe=False)

@login_required
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    try:
        n = get_object_or_404(Notification, id=notification_id, user=request.user)
        n.is_read = True
        n.save(update_fields=["is_read"])
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def mark_all_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({"success": True})

@login_required
@require_http_methods(["POST"])
def process_payment(request):
    try:
        data = json.loads(request.body)
        booking = get_object_or_404(Booking, id=data.get("booking_id"), customer=request.user)
        if booking.payment_status == "Paid":
            return JsonResponse({"error": "Already paid"}, status=400)
<create_file>
<absolute_path>c:/Users/user/ehostelfinder/fix_all.py</absolute_path>
<content>#!/usr/bin/env python3
"""Fix ALL indentation issues in views.py."""
import ast

with open('hostels/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

# Fix 1: signup function - the keep messages.success lines inside the if block, not under except
# Lines 210-213:  
#   210:             except Exception:
#   211:                 pass
#   212:                 messages.success(...)  # WRONG - should be under if form.is_valid():
#   213:                 return redirect("login")  # WRONG

# Change lines 211-213 so pass and the if-block's success/redirect are properly placed
# After 'except Exception:' body, the next statements should be at 'if' level (16 spaces)
# The fix: move messages.success and return redirect out of except body
lines[210] = '                pass\n'     # 16 spaces for except body
lines[211] = '            messages.success(request, "Account created! Please check your email to confirm.")\n'  # back to if level
lines[212] = '            return redirect("login")\n'  # back to if level

# Fix 2: logout_view function - body must be indented
for i in range(len(lines)):
    if lines[i].strip() == 'def logout_view(request):' and i+1 < len(lines):
        # Check if next line has body
        if lines[i+1].strip() and not lines[i+1].startswith(' '):
            lines[i+1] = '    ' + lines[i+1].lstrip()
            
    # Fix cookie_policy and similar one-liner functions that use ; (semicolons)
    # These are valid Python but need indented body
    if 'def cookie_policy(request):' in lines[i]:
        lines[i] = 'def cookie_policy(request):\n'
        # Move the body to next line indented
        lines.insert(i+1, '    return render(request, "cookie_policy.html")\n')
        # Remove the old line if it was a one-liner
        for j in range(i+2, min(i+5, len(lines))):
            if 'def ' in lines[j] or lines[j].strip() == '':
                break
            if 'cookie_policy' not in lines[j] and 'return render' in lines[j].lstrip():
                lines[j] = ''
    if 'def privacy_policy(request):' in lines[i]:
        lines[i] = 'def privacy_policy(request):\n'
        lines.insert(i+1, '    return render(request, "privacy_policy.html")\n')
    if 'def terms_of_use(request):' in lines[i]:
        lines[i] = 'def terms_of_use(request):\n'
        lines.insert(i+1, '    return render(request, "terms_of_use.html")\n')

with open('hostels/views.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

# Verify complete syntax
t = open('hostels/views.py').read()
try:
    tree = ast.parse(t)
    funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    print(f'SYNTAX OK! Total functions: {len(funcs)}')
    for fn in sorted(funcs):
        print(f'  - {fn}')
    
    # Check for missing functions
    required = ['cancel_booking', 'custom_404', 'custom_500', 'api_notifications',
                'mark_notification_read', 'mark_all_notifications_read',
                'view_notifications', 'my_favorites', 'toggle_favorite', 'process_payment']
    missing = [f for f in required if f not in funcs]
    if missing:
        print(f'\nMISSING functions to append: {missing}')
    else:
        print('\nAll required functions present!')
except (SyntaxError, IndentationError) as e:
    print(f'Error at line {e.lineno}: {e.msg}')
    lines_t = t.split('\n')
    if e.lineno and e.lineno <= len(lines_t):
        start = max(0, e.lineno - 3)
        for j in range(start, min(len(lines_t), e.lineno + 2)):
            marker = '>>>' if j == e.lineno - 1 else '   '
            print(f'  {marker} {j+1}: {lines_t[j]}')
