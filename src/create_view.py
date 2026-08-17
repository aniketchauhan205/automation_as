import sqlite3

DB_FILE = "../database/people.db"

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()


cursor.execute("""
    DROP VIEW IF EXISTS person_360
""")


cursor.execute("""
    CREATE VIEW person_360 AS

    SELECT
        p.person_id,
        p.name,
        p.email,
        p.phone,
        p.city,

        n.experience_years,
        n.current_ctc,
        n.applied_date,
        n.skills,

        g.rate,
        g.location,
        g.status,
        g.skill_tags,

        c.verified,
        c.projects_completed

    FROM persons p

    LEFT JOIN (

        SELECT
            person_id,
            MAX(experience_years) AS experience_years,
            MAX(current_ctc) AS current_ctc,
            MAX(applied_date) AS applied_date,
            MAX(skills) AS skills

        FROM naukri_records

        GROUP BY person_id

    ) n
        ON p.person_id = n.person_id

    LEFT JOIN (

        SELECT
            person_id,
            MAX(rate) AS rate,
            MAX(location) AS location,
            MAX(status) AS status,
            MAX(skill_tags) AS skill_tags

        FROM gig_worker_records

        GROUP BY person_id

    ) g
        ON p.person_id = g.person_id

    LEFT JOIN (

        SELECT
            person_id,
            MAX(verified) AS verified,
            MAX(projects_completed) AS projects_completed

        FROM cbnexus_records

        GROUP BY person_id

    ) c
        ON p.person_id = c.person_id
""")


conn.commit()

print("person_360 view created successfully.")

conn.close()