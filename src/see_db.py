import sqlite3

DB_FILE = "../database/people.db"

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Get all tables
cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name
""")

tables = [row[0] for row in cursor.fetchall()]

print("\nDATABASE")
print("=" * 60)

for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM [{table}]")
    count = cursor.fetchone()[0]

    print(f"\nTABLE: {table}")
    print("-" * 60)
    print(f"Rows: {count}")

    # Get column names
    cursor.execute(f"PRAGMA table_info([{table}])")
    columns = [row[1] for row in cursor.fetchall()]

    print("Columns:")
    print(", ".join(columns))

    # Show first 10 rows
    cursor.execute(f"SELECT * FROM [{table}] LIMIT 10")
    rows = cursor.fetchall()

    print("\nFirst 10 rows:")
    for row in rows:
        print(row)

conn.close()