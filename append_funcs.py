#!/usr/bin/env python3
"""Append remaining 36 view functions to hostels/views.py"""
import os, ast, re, sys

os.chdir(r'c:\Users\user\ehostelfinder')

with open('hostels/views.py', 'r', encoding='utf-8') as f:
    existing = f.read()

# Remove trailing whitespace lines
lines = [l.rstrip() for l in existing.split('\n')]
while lines and lines[-1] == '':
    lines.pop()

indent = 0
def w(s):
    if indent:
        lines.append('    ' * indent + s)
    else:
        lines.append(s)
def i():
    global indent; indent += 1
def d():
    global indent; indent -= 1

# Mark where to insert - after last function
# We'll just append everything

# Get existing function names
tree = ast.parse('\n'.join(lines))
existing_funcs = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
print(f'Starting with {len(existing_funcs)} functions. Adding 36 missing ones...')

# ===== 1. ai_chat =====
w('')
w('@csrf_exempt')
w('@require_http_methods(["POST"])')
w('def ai_chat(request):')
i()
w('try:')
i()
w('data = json.loads(request.body.decode("utf-8") if isinstance(request.body, bytes) else request.body)')
w('question = data.get("question", "").strip()')
w('if not question:')
i()
w('return JsonResponse({"error": "Question is required."}, status=400)')
d()
w('api_key = os.getenv("GOOGLE_GENERATIVE_API_KEY")')
w('if api_key:')
i()
w('try:')
i()
w('prompt = "You are a helpful hostel assistant for EHostelFinder. "')
w('prompt += "Answer questions about hostel services, bookings, and amenities. "')
w('prompt += "Be friendly, concise, and helpful. "')
w('prompt += "Question: " + question')
w('payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")')
w('url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=" + api_key')
w('req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")')
w('with urllib.request.urlopen(req, timeout=30) as resp:')
i()
w('return JsonResponse(json.loads(resp.read().decode("utf-8")))')
d()
d()
w('except: pass')
d()
w('ai_response = get_local_ai_response(question)')
w('return JsonResponse({"candidates": [{"content": {"parts": [{"text": ai_response}]}}]})')
d()
w('except Exception:')
i()
w('try:')
i()
w('ai_response = get_local_ai_response(question)')
w('return JsonResponse({"candidates": [{"content": {"parts": [{"text": ai_response}]}}]})')
d()
w('except Exception:')
i()
w('return JsonResponse({"error": "AI service temporarily unavailable"}, status=500)')
d()
d()
d()

# ===== 2. get_booking_by_id =====
w('')
w('@require_http_methods(["GET"])')
w('def get_booking_by_id(request, id):')
i()
w('try:')
i()
w('booking = get_object_or_404(Booking, id=id)')
w('if request.user.id == booking.customer_id or request.user.is_staff:')
i()
w('return JsonResponse({"id": str(booking.id), "booking_reference": booking.booking_reference, "hostel_id": str(booking.hostel_id), "room_id": str(booking.room_id), "check_in": booking.check_in.isoformat(), "check_out": booking.check_out.isoformat(), "guests": booking.guests, "nights": booking.nights, "total_price": str(booking.total_price), "booking_status": booking.booking_status, "payment_status": booking.payment_status, "special_requests": booking.special_requests})')
d()
w('return JsonResponse({"error": "Not authorized"}, status=403)')
d()
w('except Exception as e:')
i()
w('return JsonResponse({"error": str(e)}, status=500)')
d()
d()

# ===== 3. create_message =====
w('')
w('@require_http_methods(["POST"])')
w('def create_message(request):')
i()
w('try:')
i()
w('data = json.loads(request.body)')
w('hostel = get_object_or_404(Hostel, id=data.get("hostelId"))')
w('message = Message.objects.create(hostel=hostel, user=request.user if request.user.is_authenticated else None, full_name=data.get("fullName", ""), email=data.get("email", ""), phone=data.get("phone", ""), subject=data.get("subject", ""), content=data.get("content", "") or data.get("message", ""))')
w('return JsonResponse({"id": str(message.id), "created_at": message.created_at.isoformat()}, status=201)')
d()
w('except Exception as e:')
i()
w('return JsonResponse({"error": str(e)}, status=500)')
d()
d()

# ===== 4. get_messages_by_hostel =====
w('')
w('@require_http_methods(["GET"])')
w('def get_messages_by_hostel(request, hostel_id):')
i()
w('try:')
i()
w('msgs = Message.objects.filter(hostel_id=hostel_id)')
w('return JsonResponse([{"id": str(m.id), "full_name": m.full_name, "email": m.email, "subject": m.subject, "message": m.content or m.message, "created_at": m.created_at.isoformat()} for m in msgs], safe=False)')
d()
w('except Exception as e:')
i()
w('return JsonResponse({"error": str(e)}, status=500)')
d()
d()

# ===== 5. universities =====
w('')
w('def universities(request):')
i()
w('university_options = get_university_options()')
w('universities_data = []')
w('for uni in university_options:')
i()
w('name = uni["name"]')
w('count = Hostel.objects.filter(university=name).count()')
w('top = Hostel.objects.filter(university=name).order_by("-rating").first()')
w('universities_data.append({"name": name, "count": count, "top_hostel": top.name if top else "", "rating": float(top.rating) if top and top.rating else 0})')
d()
w('universities_data.sort(key=lambda x: x["name"])')
w('return render(request, "universities.html", {"universities": universities_data})')
d()

# ===== 6. contact =====
w('')
w('@csrf_exempt')
w('def contact(request):')
i()
w('if request.method == "POST":')
i()
w('try:')
i()
w('ContactMessage.objects.create(full_name=request.POST.get("name", ""), email=request.POST.get("email", ""), subject=request.POST.get("subject", ""), message=request.POST.get("message", ""))')
w('return JsonResponse({"success": True, "message": "Message sent successfully!"})')
d()
w('except Exception as e:')
i()
w('return JsonResponse({"error": str(e)}, status=400)')
d()
d()
w('return render(request, "contact.html")')
d()

# ===== 7. google_auth =====
w('')
w('def google_auth(request):')
i()
w('import urllib.parse')
w('from django.conf import settings')
w('redirect_uri = request.build_absolute_uri("/api/auth/google/callback/")')
w('params = {"client_id": settings.GOOGLE_CLIENT_ID, "redirect_uri": redirect_uri, "response_type": "code", "scope": "email profile", "access_type": "online"}')
w('auth_url = "https://accounts.google.com/o/oauth2/auth?" + urllib.parse.urlencode(params)')
w('return redirect(auth_url)')
d()

# ===== 8. google_auth_callback =====
w('')
w('def google_auth_callback(request):')
i()
w('import urllib.parse')
w('from django.conf import settings')
w('from django.contrib.auth import login as auth_login')
