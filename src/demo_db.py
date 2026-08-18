"""
Demo Script: Show the Database Creation & Data
Run this to demonstrate the database pipeline end-to-end
"""

import sqlite3
import pandas as pd
from tabulate import tabulate

conn = sqlite3.connect("../database/people.db")
cursor = conn.cursor()

print("\n" + "="*70)
print("CONSULTBAE DATABASE DEMO")
print("="*70)

# ==========================================
# 1. SCHEMA OVERVIEW
# ==========================================

print("\n[STEP 1] DATABASE SCHEMA")
print("-" * 70)
print("\nTables created:")
print("""
  • persons              (Master table - unique people)
  • naukri_records       (Records from source1)
  • gig_worker_records   (Records from source2)
  • cbnexus_records      (Records from source3)
""")

# ==========================================
# 2. DATA INGESTION STATS
# ==========================================

print("\n[STEP 2] DATA INGESTION SUMMARY")
print("-" * 70)

tables = {
    "persons": "Master Persons",
    "naukri_records": "Naukri Applicants",
    "gig_worker_records": "Gig Workers",
    "cbnexus_records": "CBNexus Contacts"
}

stats = []
for table, label in tables.items():
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    stats.append([label, count])

print(tabulate(stats, headers=["Table", "Records"], tablefmt="grid"))

# ==========================================
# 3. DEDUPLICATION RESULTS
# ==========================================

print("\n[STEP 3] DEDUPLICATION RESULTS")
print("-" * 70)

cursor.execute("""
    SELECT
        p.person_id,
        p.name,
        p.email,
        COUNT(DISTINCT source) AS sources
    FROM (
        SELECT person_id, 'naukri' AS source FROM naukri_records
        UNION ALL
        SELECT person_id, 'gig' AS source FROM gig_worker_records
        UNION ALL
        SELECT person_id, 'cbnexus' AS source FROM cbnexus_records
    ) AS all_sources
    JOIN persons p ON p.person_id = all_sources.person_id
    GROUP BY p.person_id, p.name, p.email
    ORDER BY sources DESC
    LIMIT 10
""")

result = cursor.fetchall()
print(f"\nTop 10 people appearing in multiple sources:")
print(tabulate(result, headers=["Person ID", "Name", "Email", "# Sources"], tablefmt="grid"))

# Count cross-source matches
cursor.execute("""
    SELECT
        COUNT(DISTINCT CASE WHEN sources = 2 THEN person_id END) AS two_sources,
        COUNT(DISTINCT CASE WHEN sources = 3 THEN person_id END) AS three_sources
    FROM (
        SELECT person_id, COUNT(DISTINCT source) AS sources
        FROM (
            SELECT person_id, 'naukri' AS source FROM naukri_records
            UNION ALL
            SELECT person_id, 'gig' AS source FROM gig_worker_records
            UNION ALL
            SELECT person_id, 'cbnexus' AS source FROM cbnexus_records
        ) AS all_sources
        GROUP BY person_id
    )
""")

two_src, three_src = cursor.fetchone()
print(f"\n✓ People found in 2 sources: {two_src}")
print(f"✓ People found in all 3 sources: {three_src}")

# ==========================================
# 4. SAMPLE RECORDS (Person across sources)
# ==========================================

print("\n[STEP 4] EXAMPLE: Person Matched Across Sources")
print("-" * 70)

# Get a person in all 3 sources
cursor.execute("""
    SELECT p.person_id, p.name, p.email
    FROM persons p
    WHERE EXISTS (SELECT 1 FROM naukri_records n WHERE n.person_id = p.person_id)
    AND EXISTS (SELECT 1 FROM gig_worker_records g WHERE g.person_id = p.person_id)
    AND EXISTS (SELECT 1 FROM cbnexus_records c WHERE c.person_id = p.person_id)
    LIMIT 1
""")

person = cursor.fetchone()
if person:
    person_id, name, email = person
    print(f"\nPerson ID: {person_id}")
    print(f"Master Name: {name}")
    print(f"Master Email: {email}")
    
    # Naukri records
    print("\n  → Naukri Record:")
    cursor.execute("""
        SELECT name, email, phone, current_ctc 
        FROM naukri_records WHERE person_id = ?
    """, (person_id,))
    naukri = cursor.fetchone()
    if naukri:
        print(f"    Name: {naukri[0]}, Email: {naukri[1]}, Phone: {naukri[2]}, CTC: {naukri[3]}")
    
    # Gig worker records
    print("\n  → Gig Worker Record:")
    cursor.execute("""
        SELECT name, email, phone, hourly_rate
        FROM gig_worker_records WHERE person_id = ?
    """, (person_id,))
    gig = cursor.fetchone()
    if gig:
        print(f"    Name: {gig[0]}, Email: {gig[1]}, Phone: {gig[2]}, Rate: {gig[3]}")
    
    # CBNexus records
    print("\n  → CBNexus Record:")
    cursor.execute("""
        SELECT name, email, phone, organization
        FROM cbnexus_records WHERE person_id = ?
    """, (person_id,))
    cbnexus = cursor.fetchone()
    if cbnexus:
        print(f"    Name: {cbnexus[0]}, Email: {cbnexus[1]}, Phone: {cbnexus[2]}, Org: {cbnexus[3]}")
    
    print("\n  ✓ Same person successfully linked across all 3 sources!")

# ==========================================
# 5. DATA QUALITY METRICS
# ==========================================

print("\n[STEP 5] DATA QUALITY METRICS")
print("-" * 70)

cursor.execute("SELECT COUNT(*) FROM persons WHERE email IS NOT NULL")
emails = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM persons WHERE phone IS NOT NULL")
phones = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM persons")
total = cursor.fetchone()[0]

print(f"\nData completeness in master 'persons' table:")
print(f"  • Total records: {total}")
print(f"  • Records with email: {emails} ({emails/total*100:.1f}%)")
print(f"  • Records with phone: {phones} ({phones/total*100:.1f}%)")

# ==========================================
# SUMMARY
# ==========================================

print("\n" + "="*70)
print("✓ DATABASE DEMO COMPLETE")
print("="*70)
print("""
Key Results:
  1. Successfully cleaned and normalized data from 3 CSV sources
  2. Identified duplicate persons using phone/email matching
  3. Created master 'persons' table with unique person_id
  4. Linked source-specific records via foreign keys
  5. Demonstrated entity resolution: same person → single ID
""")
print("="*70 + "\n")

conn.close()
