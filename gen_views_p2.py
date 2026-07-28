#!/usr/bin/env python3
"""Generate the complete views.py - Part 2: all remaining functions."""
import os, py_compile
os.chdir(r'c:\Users\user\ehostelfinder')

with open('hostels/views.py', 'r') as f:
    existing = f.read()

lines = existing.split('\n')
# Remove trailing empty lines
while lines and lines[-1] == '':
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

# hostel_detail
w('')
w('def hostel_detail(request, id):')
i()
w('try:')
i()
w('hostel = get_object_or_404(Hostel, id=id)')
w('rooms = Room.objects.filter(hostel=hostel, status="Available")')
w('images = hostel.images.all()')
w('cover = hostel.images.filter(is_cover=True).first()')
w('facilities = hostel.facilities.all()')
w('reviews = hostel.reviews.select_related("customer").all()')
w('rooms_data = []')
w('for r in rooms:')
i()
w('rooms_data.append({')
w('"id": str(r.id), "room_number": r.room_number, "room_name": r.room_name,')
w('"room_type": r.room_type, "capacity": r.capacity, "available_quantity": r.available_quantity,')
w('"price_per_night": str(r.price_per_night), "floor": r.floor or 1, "description": r.description,')
w('"private_bathroom": r.private_bathroom, "air_conditioning": r.air_conditioning,')
w('"balcony": r.balcony, "television": r.television, "wifi": r.wifi,')
w('"images": [ri.image_url for ri in r.images.all()],')
w('})')
d()
w('reviews_data = []')
w('for rv in reviews:')
i()
w('reviews_data.append({')
w('"id": str(rv.id), "customer_name": rv.customer.get_full_name() or rv.customer.email,')
w('"rating": rv.rating, "comment": rv.comment,')
w('"created_at": rv.created_at.strftime("%Y-%m-%d"),')
w('})')
d()
w('context = {')
w('"hostel": {')
w('"id": str(hostel.id), "name": hostel.name, "description": hostel.description,')
w('"address": hostel.address, "city": hostel.city, "country": hostel.country,')
w('"university": hostel.university, "distance": hostel.distance or "Near campus",')
w('"price": float(hostel.price) if hostel.price else 0,')
w('"rating": float(hostel.rating) if hostel.rating else round(float(hostel.average_rating), 1),')
w('"available": hostel.available, "contact": hostel.contact or "",')
w('"amenities": hostel.amenities or [], "phone": hostel.phone, "email": hostel.email,')
w('"latitude": str(hostel.latitude) if hostel.latitude else None,')
w('"longitude": str(hostel.longitude) if hostel.longitude else None,')
w('"cover_image": cover.image_url if cover else None,')
w('"images": [{"url": img.image_url, "is_cover": img.is_cover} for img in images],')
w('},')
w('"rooms": rooms_data,')
w('"facilities": [{"name": f.facility_name, "icon": f.icon or ""} for f in facilities],')
w('"reviews": reviews_data,')
w('}')
d()
w('except Exception as e:')
i()
w('print(f"Error in hostel_detail: {e}")')
w('messages.error(request, "Error loading hostel details")')
w('return redirect("home")')
d()
w('if request.method == "POST" and "review_submit" in request.POST:')
i()
w('if not request.user.is_authenticated:')
i()
w('messages.error(request, "You must be logged in to leave a review")')
w('return redirect("login")')
d()
w('rating = request.POST.get("rating", "").strip()')
w('comment = request.POST.get("comment", "").strip()')
w('if not rating or not rating.isdigit() or int(rating) not in range(1, 6):')
i()
w('messages.error(request, "Please select a valid rating from 1 to 5.")')
w('return redirect("hostel_detail", id=hostel.id)')
d()
w('Review.objects.create(hostel=hostel, customer=request.user, rating=int(rating), comment=comment)')
w('hostel.review_count = hostel.reviews.count()')
w('hostel.rating = round(hostel.reviews.aggregate(avg=Avg("rating"))["avg"] or 0, 2)')
w('hostel.save(update_fields=["review_count", "rating"])')
w('messages.success(request, "Your review has been submitted successfully.")')
w('return redirect("hostel_detail", id=hostel.id)')
d()
w('return render(request, "hostel_detail.html", context)')
d()

# Now write and verify
with open('hostels/views.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

try:
    py_compile.compile('hostels/views.py', doraise=True)
    print('STEP 2 SUCCESS:', len(lines), 'lines, syntax OK')
except py_compile.PyCompileError as e:
    print('STEP 2 SYNTAX ERROR:', e)
    # Print around the error
    import traceback
    traceback.print_exc()
