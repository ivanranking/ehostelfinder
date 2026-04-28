import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Check messages table
cursor.execute("SELECT COUNT(*) FROM hostels_message")
count = cursor.fetchone()[0]
print(f"Total messages: {count}")

if count > 0:
    print("\nMessages in database:")
    print("-" * 50)
    cursor.execute("SELECT id, user_id, hostel_id, subject, created_at FROM hostels_message")
    for row in cursor.fetchall():
        print(f"  ID: {row[0]}")
        print(f"  User ID: {row[1]}")
        print(f"  Hostel ID: {row[2]}")
        print(f"  Subject: {row[3]}")
        print(f"  Created: {row[4]}")
        print("-" * 50)
else:
    print("\nNo messages found in the database.")

conn.close()