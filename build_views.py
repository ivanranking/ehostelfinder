#!/usr/bin/env python3
"""Build views.py from clean source. Write functions one at a time via Python file operations."""
import ast

# I'll write the complete views.py as individual f-strings to avoid quoting issues
# Using heredoc-style with proper Python

code = """from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db.models import Avg
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import json
import os
import urllib.request
import urllib.error
import uuid
from .forms import UserRegistrationForm, UserLoginForm, ForgotPasswordForm, ResetPasswordForm, ProfileUpdateForm, HostelUploadForm
from .models import Hostel, User, ContactMessage, Profile, Room, Booking, Review, Favorite, Message, Notification, Payment, RoomStatus, BookingStatus
from .local_ai import get_local_ai_response

KAMPALA_AREA_UNIVERSITIES = [
    "Makerere University",
    "Makerere University Business School",
    "Kyambogo University",
    "Kampala International University",
    "Uganda Christian University",
    "Ndejje University",
    "Bugema University",
    "Cavendish University Uganda",
    "St. Lawrence University Uganda",
    "Mutesa I Royal University",
]


def get_university_options():
    university_names = []
    seen = set()
    for name in KAMPALA_AREA_UNIVERSITIES + list(Hostel.objects.exclude(university="").values_list("university", flat=True)):
        normalized = name.strip() if name else ""
        if not normalized:
            continue
        lower = normalized.lower()
        if lower not in seen:
            university_names.append(normalized)
            seen.add(lower)
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
        except ValueError:
            pass
    if max_price:
        try:
            hostels = hostels.filter(price__lte=float(max_price)).distinct()
        except ValueError:
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
            "id": str(h.id),
            "name": h.name,
            "description": h.description,
            "city": h.city,
            "country": h.country,
            "university": h.university,
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
        "hostels": hostel_list,
        "cities": cities_list,
        "countries": countries_list,
        "universities": universities,
        "selected_city": city,
        "selected_country": country,
        "selected_university": university,
        "selected_sort": sort_by,
        "total_hostels": Hostel.objects.count(),
        "total_universities": len(universities),
        "avg_rating": avg_rating,
        "total_cities": len(cities_list),
        "page_obj": page_obj,
        "favorite_ids": [str(fid) for fid in favorite_ids],
    })
"""

# Use triple-quoted strings to write the whole file
# Write just the first batch first to verify
with open('hostels/views_new.py', 'w', encoding='utf-8') as f:
    f.write(code)

try:
    ast.parse(code)
    print("Part 1 syntax OK!")
except SyntaxError as e:
    print(f"Part 1 syntax error: {e}")
