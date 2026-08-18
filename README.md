# Multi-Source People Database

## 1. Overview

This project builds a clean SQLite database from three heterogeneous CSV files:

1. `source1_naukri_applicants.csv`
2. `source2_gig_workers.csv`
3. `source3_cbnexus_contacts.csv`

The main challenge was that the three sources did not contain a common person ID. Therefore, the solution performs data cleaning, normalization, duplicate handling, and entity resolution before loading the data into a relational database.

The final database uses a master `persons` table with a unique `person_id`. Source-specific records are stored in separate tables and linked to the master person using foreign keys.

This allows the same person appearing in multiple sources to be represented by one master person while retaining all source-specific information.

---

# 2. Project Structure

```text
consultbae/
│
├── data/
│   ├── source1_naukri_applicants.csv
│   ├── source2_gig_workers.csv
│   └── source3_cbnexus_contacts.csv
│
├── database/
│   └── people.db
│
├── src/
│   ├── database.py
│   ├── ingest.py
│   ├── check_duplicates.py
│   ├── check_db.py
│   └── create_views.py
│
├── requirements.txt
└── README.md