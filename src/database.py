import sqlite3

DB_FILE = "../database/people.db"


def create_database():
    conn = sqlite3.connect(DB_FILE)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS persons (
            person_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            phone TEXT UNIQUE,
            city TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS naukri_applicants (
            person_id INTEGER PRIMARY KEY,
            experience_years REAL,
            current_ctc REAL,
            applied_date TEXT,
            skills TEXT,
            FOREIGN KEY (person_id) REFERENCES persons(person_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gig_workers (
            person_id INTEGER PRIMARY KEY,
            rate REAL,
            location TEXT,
            status TEXT,
            skill_tags TEXT,
            FOREIGN KEY (person_id) REFERENCES persons(person_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cbnexus_contacts (
            person_id INTEGER PRIMARY KEY,
            verified TEXT,
            projects_completed INTEGER,
            FOREIGN KEY (person_id) REFERENCES persons(person_id)
        )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_database()
    print("Database created successfully.")