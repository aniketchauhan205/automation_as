import os
import sqlite3
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "..", "database", "people.db")
RECORDINGS_DIR = os.path.join(BASE_DIR, "recordings")

os.makedirs(RECORDINGS_DIR, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def ensure_audio_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audio_submissions (
            submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id INTEGER NOT NULL,
            name TEXT,
            phone TEXT,
            filename TEXT,
            filepath TEXT,
            source TEXT,
            submitted_at TEXT,
            duration_sec REAL,
            sample_rate_hz INTEGER,
            sample_rate_khz REAL,
            channels INTEGER,
            bitrate_kbps REAL,
            loudness_dbfs REAL,
            noise_floor_db REAL,
            snr_estimate_db REAL,
            quality_label TEXT,

            FOREIGN KEY (person_id)
                REFERENCES persons(person_id)
        )
    """)
    conn.commit()
    conn.close()


def get_or_create_person(name: str, phone: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT person_id FROM persons WHERE phone = ?", (phone,))
    row = cursor.fetchone()
    if row:
        person_id = row[0]
    else:
        cursor.execute(
            "INSERT INTO persons (name, email, phone, city) VALUES (?, NULL, ?, NULL)",
            (name, phone),
        )
        person_id = cursor.lastrowid
        conn.commit()
    conn.close()
    return person_id


def insert_submission(person_id: int, name: str, phone: str, filename: str,
                       filepath: str, source: str, metrics: dict) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO audio_submissions (
            person_id, name, phone, filename, filepath, source, submitted_at,
            duration_sec, sample_rate_hz, sample_rate_khz, channels,
            bitrate_kbps, loudness_dbfs, noise_floor_db, snr_estimate_db, quality_label
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        person_id, name, phone, filename, filepath, source,
        datetime.now(timezone.utc).isoformat(),
        metrics["duration_sec"], metrics["sample_rate_hz"], metrics["sample_rate_khz"],
        metrics["channels"], metrics["bitrate_kbps"], metrics["loudness_dbfs"],
        metrics["noise_floor_db"], metrics["snr_estimate_db"], metrics["quality_label"],
    ))
    submission_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return submission_id


def fetch_recent_submissions(limit: int = 20):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT submission_id, name, phone, source, submitted_at, duration_sec,
               sample_rate_khz, bitrate_kbps, loudness_dbfs, snr_estimate_db, quality_label
        FROM audio_submissions
        ORDER BY submission_id DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    columns = [d[0] for d in cursor.description]
    conn.close()
    return columns, rows
