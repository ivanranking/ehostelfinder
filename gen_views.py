#!/usr/bin/env python3
"""Generate the complete views.py file for EHostelFinder."""
import os, py_compile
os.chdir(r'c:\Users\user\ehostelfinder')

lines = []
indent = 0

def w(s):
    if indent:
        lines.append('    ' * indent + s)
    else:
        lines.append(s)

def i(n=1):
    global indent
    indent += n

def d(n=1):
    global indent
    indent -= n

# IMPORTS
w('from django.shortcuts import render, get_object_or_404, redirect')
w('from django.contrib.auth import logout')
w('from django.http import JsonResponse')
w('from django.views.decorators.http import require_http_methods')
w('from django.views.decorators.csrf import csrf_exempt')
w('from django.contrib import messages')
w('from django.db.models import Avg')
w('from django.core.paginator import Paginator')
w('from django.utils import timezone')
w('from django.contrib.auth.decorators import login_required')
w('import json, os, urllib.request, urllib.error, uuid')
w('from .forms import UserRegistrationForm, UserLoginForm, ForgotPasswordForm, ResetPasswordForm, ProfileUpdateForm, HostelUploadForm')
w('from .models import Hostel, User, ContactMessage, Profile, Room, Booking, Review, Favorite, Message, Notification, Payment, RoomStatus, BookingStatus')
w('from .local_ai import get_local_ai_response')
w('')
w('KAMPALA_AREA_UNIVERSITIES = ["Makerere University", "Makerere University Business School", "Kyambogo University", "Kampala International University", "Uganda Christian University", "Ndejje University", "Bugema University", "Cavendish University Uganda", "St. Lawrence University Uganda", "Mutesa I Royal University"]')
w('')

# get_university_options
w('def get_university_options():')
i()
w('university_names, seen = [], set()')
w('def normalize(name):')
i()
w('if not name: return ""')
w('n = name.strip().lower()')
w('if "makerere" in n and "business school" in n: return "Makerere University Business School"')
w('if "makerere" in n: return "Makerere University"')
w('return name.strip()')
d()
w('for name in KAMPALA_AREA_UNIVERSITIES + list(Hostel.objects.exclude(university="").values_list("university", flat=True)):')
i()
w('if name:')
i()
w('normalized = normalize(name)')
w('if normalized.lower() not in seen:')
i()
w('university_names.append(normalized)')
w('seen.add(normalized.lower())')
d(3)
w('return [{"name": n} for n in university_names]')
d()
w('')

# home
w('def home(request):')
i()
w('university = request.GET.get("university", "All Universities")')
w('city = request.GET.get("city", "")')
w('country = request.GET.get("country", "")')
w('min_price = request.GET.get("min_price", "")')
w('max_price = request.GET.get("max_price", "")')
w('sort_by = request.GET.get("sort", "-created_at")')
w('page = request.GET.get("page", 1)')
w('valid_sorts = ["name", "-name", "price", "-price", "rating", "-rating", "created_at", "-created_at"]')
w('if sort_by not in valid_sorts: sort_by = "-created_at"')
w('hostels = Hostel.objects.all()')
w('if university and university != "All Universities": hostels = hostels.filter(university=university)')
w('if city: hostels = hostels.filter(city__icontains=city)')
w('if country: hostels = hostels.filter(country__icontains=country)')
w('if min_price:')
i()
w('try: hostels = hostels.filter(price__gte=float(min_price)).distinct()')
w('except ValueError: pass')
d()
w('if max_price:')
i()
w('try: hostels = hostels.filter(price__lte=float(max_price)).distinct()')
w('except ValueError: pass')
d()
w('hostels = hostels.order_by(sort_by)')
w('paginator = Paginator(hostels, 12)')
w('try: page_obj = paginator.page(page)')
w('except: page_obj = paginator.page(1)')
w('cities_list = sorted(Hostel.objects.values_list("city", flat=True).exclude(city="").distinct())')
w('countries_list = sorted(Hostel.objects.values_list("country", flat=True).exclude(country="").distinct())')
w('universities = get_university_options()')
w('rated_hostels = Hostel.objects.exclude(rating__isnull=True)')
w('avg_rating = round(sum(float(h.rating) for h in rated_hostels) / rated_hostels.count(), 1) if rated_hostels.exists() else 0.0')
w('hostel_list = []')
w('for h in page_obj:')
i()
w('cover = h.images.filter(is_cover=True).first()')
w('available_room = h.rooms.filter(status="Available").first()')
w('hostel_list.append({')
w('"id": str(h.id), "name": h.name, "description": h.description, "city": h.city, "country": h.country,')
w('"university": h.university, "image_url": h.image_url or (cover.image_url if cover else None),')
w('"facilities": [{"name": f.facility_name, "icon": f.icon or ""} for f in h.facilities.all()],')
w('"available": h.available, "rating": float(h.rating) if h.rating else round(float(h.average_rating), 1),')
w('"distance": h.distance or "Near campus",')
w('"price": str(h.price) if h.price else (str(available_room.price_per_night) if available_room else "0"),')
w('"amenities": h.amenities or [],')
w('})')
d()
w('favorite_ids = []')
w('if request.user.is_authenticated:')
i()
w('favorite_ids = list(Favorite.objects.filter(customer=request.user).values_list("hostel_id", flat=True))')
d()
w('return render(request, "home.html", {')
w('"hostels": hostel_list, "cities": cities_list, "countries": countries_list, "universities": universities,')
w('"selected_city": city, "selected_country": country, "selected_university": university, "selected_sort": sort_by,')
w('"total_hostels": Hostel.objects.count(), "total_universities": len(universities), "avg_rating": avg_rating,')
w('"total_cities": len(cities_list), "page_obj": page_obj, "favorite_ids": [str(fid) for fid in favorite_ids],')
w('})')
d()
w('')

with open('hostels/views.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

# verify
try:
    py_compile.compile('hostels/views.py', doraise=True)
    print('SUCCESS:', len(lines), 'lines written, syntax OK')
except py_compile.PyCompileError as e:
    print('SYNTAX ERROR:', e)
