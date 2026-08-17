import pandas as pd
import sqlite3
from pathlib import Path


DATA_DIR = Path("../data")
DB_FILE = "../database/people.db"


# =========================================================
# LOAD DATA
# =========================================================

source1 = pd.read_csv(
    DATA_DIR / "source1_naukri_applicants.csv"
)

source2 = pd.read_csv(
    DATA_DIR / "source2_gig_workers.csv"
)

source3 = pd.read_csv(
    DATA_DIR / "source3_cbnexus_contacts.csv"
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()


# =========================================================
# HELPER: FIND PERSON
# =========================================================

def find_person(email=None, phone=None):

    # First try email
    if email:

        cursor.execute("""
            SELECT person_id
            FROM persons
            WHERE lower(email) = lower(?)
        """, (email,))

        result = cursor.fetchone()

        if result:
            return result[0]

    # Then try phone
    if phone:

        cursor.execute("""
            SELECT person_id
            FROM persons
            WHERE phone = ?
        """, (phone,))

        result = cursor.fetchone()

        if result:
            return result[0]

    return None


# =========================================================
# HELPER: CREATE PERSON
# =========================================================

def create_person(name, email=None, phone=None, city=None):

    cursor.execute("""
        INSERT INTO persons
        (
            name,
            email,
            phone,
            city
        )
        VALUES (?, ?, ?, ?)
    """, (
        name,
        email,
        phone,
        city
    ))

    return cursor.lastrowid


# =========================================================
# SOURCE 1 — NAUKRI
# =========================================================

for _, row in source1.iterrows():

    name = row["Full Name"]

    email = str(row["Email"]).strip().lower()

    phone = str(row["Phone_cleaned"]).strip()

    city = row["City"]


    # Find existing person
    person_id = find_person(
        email=email,
        phone=phone
    )


    # If not found, create person
    if person_id is None:

        person_id = create_person(
            name=name,
            email=email,
            phone=phone,
            city=city
        )


    # Store original source record
    cursor.execute("""
        INSERT INTO naukri_records
        (
            person_id,
            name,
            email,
            phone,
            city,
            experience_years,
            current_ctc,
            applied_date,
            skills
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        person_id,
        name,
        email,
        phone,
        city,
        row["Experience (Years)"],
        row["ctc_cleaned"],
        row["date_cleaned"],
        row["Skills"]
    ))


# =========================================================
# SOURCE 2 — GIG WORKERS
# =========================================================

for _, row in source2.iterrows():

    name = row["worker_name"]

    email = str(row["normalized_email"]).strip().lower()

    location = row["location"]


    # Find existing person using email
    person_id = find_person(
        email=email
    )


    # Create if not found
    if person_id is None:

        person_id = create_person(
            name=name,
            email=email,
            city=location
        )


    # Store source record
    cursor.execute("""
        INSERT INTO gig_worker_records
        (
            person_id,
            name,
            email,
            rate,
            location,
            status,
            skill_tags
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        person_id,
        name,
        email,
        row["rate"],
        location,
        row["status"],
        row["skill_tags"]
    ))


# =========================================================
# SOURCE 3 — CB NEXUS
# =========================================================

for _, row in source3.iterrows():

    name = row["Name"]

    phone = str(row["normalized_phone_no"]).strip()

    city = row["City"]


    # Find existing person using phone
    person_id = find_person(
        phone=phone
    )


    # Create if not found
    if person_id is None:

        person_id = create_person(
            name=name,
            phone=phone,
            city=city
        )


    # Store source record
    cursor.execute("""
        INSERT INTO cbnexus_records
        (
            person_id,
            name,
            phone,
            city,
            verified,
            projects_completed
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        person_id,
        name,
        phone,
        city,
        row["norm_verified"],
        row["Projects Completed"]
    ))


# =========================================================
# COMMIT
# =========================================================

conn.commit()

conn.close()

print("Ingestion completed successfully.")