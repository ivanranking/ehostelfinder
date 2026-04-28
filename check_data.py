import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Check all messages (including null user)
cursor.execute("SELECT id, user_id, hostel_id, subject, content, created_at FROM hostels_message")
rows = cursor.fetchall()

print(f"Total messages in database: {len(rows)}")
print("-" * 60)

if rows:
    for row in rows:
        print(f"ID: {row[0]}")
        print(f"User ID: {row[1]}")
        print(f"Hostel ID: {row[2]}")
        print(f"Subject: {row[3]}")
        print(f"Content: {row[4][:50]}..." if row[4] and len(row[4]) > 50 else f"Content: {row[4]}")
        print(f"Created: {row[5]}")
        print("-" * 60)
else:
    print("No messages found.")

# Also check bookings
cursor.execute("SELECT COUNT(*) FROM hostels_booking")
booking_count = cursor.fetchone()[0]
print(f"\nTotal bookings: {booking_count}")

# Check hostels
cursor.execute("SELECT COUNT(*) FROM hostels_hostel")
hostel_count = cursor.fetchone()[0]
print(f"Total hostels: {hostel_count}")

conn.close()