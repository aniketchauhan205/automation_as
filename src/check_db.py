import sqlite3


conn = sqlite3.connect("../database/people.db")
cursor = conn.cursor()


tables = [
    "persons",
    "naukri_records",
    "gig_worker_records",
    "cbnexus_records"
]


# ==========================================
# DATABASE COUNTS
# ==========================================

print("\nDATABASE COUNTS")
print("========================")

for table in tables:

    cursor.execute(
        f"SELECT COUNT(*) FROM {table}"
    )

    count = cursor.fetchone()[0]

    print(f"{table}: {count}")


# ==========================================
# PEOPLE APPEARING IN MULTIPLE SOURCES
# ==========================================

print("\nPERSONS APPEARING IN MULTIPLE SOURCES")
print("========================")

cursor.execute("""
    SELECT
        p.person_id,
        p.name,
        p.email,
        p.phone,
        COUNT(DISTINCT source) AS source_count

    FROM (

        SELECT person_id, 'naukri' AS source
        FROM naukri_records

        UNION ALL

        SELECT person_id, 'gig' AS source
        FROM gig_worker_records

        UNION ALL

        SELECT person_id, 'cbnexus' AS source
        FROM cbnexus_records

    ) AS all_sources

    JOIN persons p
        ON p.person_id = all_sources.person_id

    GROUP BY
        p.person_id,
        p.name,
        p.email,
        p.phone

    HAVING source_count > 1

    ORDER BY p.person_id
""")


for row in cursor.fetchall():
    print(row)


# ==========================================
# PEOPLE PRESENT IN ALL 3 SOURCES
# ==========================================

print("\nPEOPLE PRESENT IN ALL 3 SOURCES")
print("========================")

cursor.execute("""
    SELECT
        p.person_id,
        p.name,
        p.email,
        p.phone

    FROM persons p

    JOIN naukri_records n
        ON p.person_id = n.person_id

    JOIN gig_worker_records g
        ON p.person_id = g.person_id

    JOIN cbnexus_records c
        ON p.person_id = c.person_id

    GROUP BY
        p.person_id,
        p.name,
        p.email,
        p.phone

    ORDER BY p.person_id
""")


for row in cursor.fetchall():
    print(row)


# ==========================================
# NIKHIL CHOPRA CHECK
# ==========================================

print("\nNIKHIL CHOPRA CHECK")
print("========================")

cursor.execute("""
    SELECT
        person_id,
        name,
        email,
        phone

    FROM persons

    WHERE name LIKE '%Nikhil Chopra%'
""")


for row in cursor.fetchall():
    print(row)


# ==========================================
# NIKHIL CHOPRA NAUKRI RECORDS
# ==========================================

print("\nNIKHIL CHOPRA NAUKRI RECORDS")
print("========================")

cursor.execute("""
    SELECT
        record_id,
        person_id,
        name,
        email,
        phone

    FROM naukri_records

    WHERE name LIKE '%Nikhil Chopra%'
""")


for row in cursor.fetchall():
    print(row)


conn.close()