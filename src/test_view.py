import sqlite3

conn = sqlite3.connect("../database/people.db")
cursor = conn.cursor()

cursor.execute("""
    SELECT COUNT(*)
    FROM person_360
""")

print("person_360 rows:", cursor.fetchone()[0])


print("\nFIRST 10 PEOPLE")
print("========================")

cursor.execute("""
    SELECT *
    FROM person_360
    LIMIT 10
""")

for row in cursor.fetchall():
    print(row)


conn.close()
