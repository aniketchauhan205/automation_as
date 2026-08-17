import sqlite3

DB_FILE = "../database/people.db"


def create_database():

    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # -----------------------------
    # Master person table
    # -----------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS persons (
            person_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            city TEXT
        )
    """)

    # -----------------------------
    # Naukri source records
    # -----------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS naukri_records (
            record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id INTEGER NOT NULL,
            name TEXT,
            email TEXT,
            phone TEXT,
            city TEXT,
            experience_years REAL,
            current_ctc REAL,
            applied_date TEXT,
            skills TEXT,

            FOREIGN KEY (person_id)
                REFERENCES persons(person_id)
        )
    """)

    # -----------------------------
    # Gig worker source records
    # -----------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gig_worker_records (
            record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id INTEGER NOT NULL,
            name TEXT,
            email TEXT,
            rate REAL,
            location TEXT,
            status TEXT,
            skill_tags TEXT,

            FOREIGN KEY (person_id)
                REFERENCES persons(person_id)
        )
    """)

    # -----------------------------
    # CB Nexus source records
    # -----------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cbnexus_records (
            record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id INTEGER NOT NULL,
            name TEXT,
            phone TEXT,
            city TEXT,
            verified TEXT,
            projects_completed INTEGER,

            FOREIGN KEY (person_id)
                REFERENCES persons(person_id)
        )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_database()
    print("Database created successfully.")