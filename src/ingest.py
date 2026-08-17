import pandas as pd
import sqlite3
from pathlib import Path


DATA_DIR = Path("../data")
DB_FILE = "../people.db"


# -----------------------------------
# Load source files
# -----------------------------------

source1 = pd.read_csv(
    DATA_DIR / "source1_naukri_applicants.csv"
)

source2 = pd.read_csv(
    DATA_DIR / "source2_gig_workers.csv"
)

source3 = pd.read_csv(
    DATA_DIR / "source3_cbnexus_contacts.csv"
)


# -----------------------------------
# Connect to database
# -----------------------------------

conn = sqlite3.connect(DB_FILE)

cursor = conn.cursor()


# -----------------------------------
# Helper: find existing person
# -----------------------------------

def find_person(email=None, phone=None):

    if email:
        cursor.execute(
            """
            SELECT person_id
            FROM persons
            WHERE email = ?
            """,
            (email,)
        )

        result = cursor.fetchone()

        if result:
            return result[0]

    if phone:
        cursor.execute(
            """
            SELECT person_id
            FROM persons
            WHERE phone = ?
            """,
            (phone,)
        )

        result = cursor.fetchone()

        if result:
            return result[0]

    return None


# -----------------------------------
# Helper: create person
# -----------------------------------

def create_person(name, email=None, phone=None, city=None):

    cursor.execute(
        """
        INSERT INTO persons
        (name, email, phone, city)
        VALUES (?, ?, ?, ?)
        """,
        (name, email, phone, city)
    )

    return cursor.lastrowid


# -----------------------------------
# SOURCE 1 - Naukri
# -----------------------------------

for _, row in source1.iterrows():

    name = row["Full Name"]
    email = row["Email"]
    phone = str(row["Phone_cleaned"])
    city = row["City"]

    person_id = find_person(
        email=email,
        phone=phone
    )

    if person_id is None:

        person_id = create_person(
            name=name,
            email=email,
            phone=phone,
            city=city
        )

    cursor.execute(
        """
        INSERT OR REPLACE INTO naukri_applicants
        (
            person_id,
            experience_years,
            current_ctc,
            applied_date,
            skills
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            person_id,
            row["Experience (Years)"],
            row["ctc_cleaned"],
            row["date_cleaned"],
            row["Skills"]
        )
    )


# -----------------------------------
# SOURCE 2 - Gig Workers
# -----------------------------------

for _, row in source2.iterrows():

    name = row["worker_name"]
    email = row["normalized_email"]
    city = row["location"]

    person_id = find_person(
        email=email
    )

    if person_id is None:

        person_id = create_person(
            name=name,
            email=email,
            city=city
        )

    cursor.execute(
        """
        INSERT OR REPLACE INTO gig_workers
        (
            person_id,
            rate,
            location,
            status,
            skill_tags
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            person_id,
            row["rate"],
            row["location"],
            row["status"],
            row["skill_tags"]
        )
    )


# -----------------------------------
# SOURCE 3 - CB Nexus
# -----------------------------------

for _, row in source3.iterrows():

    name = row["Name"]
    phone = str(row["normalized_phone_no"])
    city = row["City"]

    person_id = find_person(
        phone=phone
    )

    if person_id is None:

        person_id = create_person(
            name=name,
            phone=phone,
            city=city
        )

    cursor.execute(
        """
        INSERT OR REPLACE INTO cbnexus_contacts
        (
            person_id,
            verified,
            projects_completed
        )
        VALUES (?, ?, ?)
        """,
        (
            person_id,
            row["norm_verified"],
            row["Projects Completed"]
        )
    )


# -----------------------------------
# Save
# -----------------------------------

conn.commit()
conn.close()

print("Ingestion completed successfully.")