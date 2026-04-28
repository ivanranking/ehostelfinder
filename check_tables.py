import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("Tables in database:")
print("-" * 30)
for table in tables:
    print(f"  - {table[0]}")

print(f"\nTotal: {len(tables)} tables")
conn.close()