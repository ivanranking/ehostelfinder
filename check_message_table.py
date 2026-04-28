import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

print("\n--- hostels_message table structure ---")
cursor.execute("PRAGMA table_info(hostels_message)")
for col in cursor.fetchall():
    print(col)

print("\n--- All messages (including null user) ---")
cursor.execute("SELECT * FROM hostels_message")
rows = cursor.fetchall()
for row in rows:
    print(row)

print(f"\nTotal messages: {len(rows)}")

print("\n--- Foreign key constraints ---")
cursor.execute("PRAGMA foreign_key_list(hostels_message)")
for fk in cursor.fetchall():
    print(fk)

conn.close()