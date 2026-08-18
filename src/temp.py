import sqlite3

DB_FILE = "../database/people.db"

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

cursor.execute("""
    SELECT *
    FROM person_360
""")

rows = cursor.fetchall()

print(f"person_360 rows: {len(rows)}")
print("=" * 100)

for row in rows[:60]:
    print(row)

conn.close()