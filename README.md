# Multi-Source People Database

## Table of Contents
1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [Setup Instructions](#setup-instructions)
4. [Data Issues Report](#data-issues-report)
5. [Stuck Log](#stuck-log)
6. [Architecture](#architecture)
7. [Usage](#usage)
8. [Task 2: n8n Automation](#task-2-n8n-automation-csv-duplicate-detection)

---

## 1. Overview

This project builds a clean SQLite database from three heterogeneous CSV files:

1. `source1_naukri_applicants.csv` (Naukri job applicants)
2. `source2_gig_workers.csv` (Gig economy workers)
3. `source3_cbnexus_contacts.csv` (CBNexus contacts)

**The Challenge:** The three sources do not contain a common person ID. Records needed to be cross-referenced using email, phone number, and other identifying information.

**The Solution:** Data cleaning, normalization, duplicate detection, and entity resolution are performed to identify the same person across multiple sources. The final database uses a master `persons` table with a unique `person_id`. Source-specific records are stored in separate tables (`naukri_applicants`, `gig_workers`, `cbnexus_contacts`) and linked to the master person using foreign keys.

**Result:** The same person appearing in multiple sources is represented by one master person record, while all source-specific information is retained.

---

## 2. Project Structure

```text
consultbae/
│
├── data/
│   ├── source1_naukri_applicants.csv
│   ├── source2_gig_workers.csv
│   ├── source3_cbnexus_contacts.csv
│   └── incoming/
│
├── database/
│   └── people.db
│
├── src/
│   ├── database.py          # Database schema and initialization
│   ├── ingest.py            # Main ingestion pipeline
│   ├── check_duplicates.py  # Duplicate detection logic
│   ├── check_db.py          # Database verification
│   ├── create_view.py       # SQL view creation
│   └── temp.py
│
├── audioapp/
│   ├── app.py               # Flask audio application
│   ├── audio_utils.py       # Audio processing utilities
│   ├── db.py                # Audio app database integration
│   ├── requirements.txt
│   └── recordings/
│
├── convex/
│   ├── schema.ts            # Convex database schema
│   ├── seed.ts              # Data seeding script
│   ├── people.ts            # People table queries
│   └── _generated/          # Auto-generated API files
│
├── n8n workflow/
│   └── Duplicate detection.json   # n8n workflow for duplicate detection
│
├── requirements.txt
├── package.json
├── persons.csv
├── persons.json
└── README.md
```

---

## 3. Setup Instructions

### Prerequisites
- Python 3.8+
- SQLite3
- Node.js (for Convex integration)
- Docker (for n8n workflows)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd consultbae
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare data files**
   - Place CSV files in the `data/` directory:
     - `source1_naukri_applicants.csv`
     - `source2_gig_workers.csv`
     - `source3_cbnexus_contacts.csv`

4. **Initialize the database**
   ```bash
   python src/database.py
   ```

5. **Run the ingestion pipeline**
   ```bash
   python src/ingest.py
   ```

6. **Verify the database**
   ```bash
   python src/check_db.py
   ```

### Optional: Audio App Setup

If using the audio application:
```bash
cd audioapp
pip install -r requirements.txt
python app.py
```

### Optional: n8n Workflow Setup

1. Start n8n in Docker:
   ```bash
   docker run -d --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n n8nio/n8n:latest
   ```
   
   This command:
   - `-d`: Run as daemon (background)
   - `--name n8n`: Name the container
   - `-p 5678:5678`: Map port 5678 (n8n UI)
   - `-v n8n_data:/home/node/.n8n`: Persist workflows in named volume
   - `n8nio/n8n:latest`: Use official n8n image

2. Access n8n UI: `http://localhost:5678`

3. Import the workflow: `n8n workflow/Duplicate detection.json`

4. Configure the Convex API endpoint (pre-configured in workflow)

---

## 4. Data Issues Report

This section documents all data quality issues encountered and how they were resolved.

### Issue 1: Phone Numbers - Scientific Notation & Country Codes

**Problem:**
- Phone numbers were stored in scientific notation (e.g., `9.11E+09`)
- Some numbers had Indian country code (91) appended
- source3_cbnexus_contacts had negative values with "-" between country code and phone number

**Solution:**
- Converted scientific notation to decimal format
- Created `phone_clean` column with conditional logic:
  - If number length = 12 and starts with "91": extract last 10 digits
  - Otherwise: return the number as-is
- For negative values in source3: normalized by subtracting from 91 and extracting last 10 digits

**Outcome:** Standardized 10-digit phone numbers across all sources

---

### Issue 2: CTC (Cost to Company) - Mixed Units

**Problem:**
- Some CTC values were in rupees (e.g., `500000`)
- Others were in lakh rupees (e.g., `5` lakh = 500000)
- No consistent unit across sources

**Solution:**
- Created `curr_CTC_correct` column with conditional logic:
  - If CTC < 100: multiply by 100,000 (convert lakhs to rupees)
  - Otherwise: use the value as-is (already in rupees)

**Outcome:** All CTC values standardized to rupees

---

### Issue 3: Dates - Format Inconsistency (dd/mm/yy vs mm/dd/yy)

**Problem:**
- Some dates in dd/mm/yy format (e.g., `25/12/20`)
- Others in mm/dd/yy format (e.g., `12/25/20`)
- Ambiguous when both values ≤ 12

**Solution:**
- Created `normalized_dates` column
- Manually filled two reference values (one from each format) in mm/dd/yyyy format
- Used Excel Flash Fill to recognize the pattern
- Applied pattern across entire dataset

**Outcome:** All dates standardized to mm/dd/yyyy format

---

### Issue 4: Email Addresses - Case Inconsistency

**Problem:**
- Some emails in source2_gig_workers were in uppercase
- Inconsistent email casing prevents proper entity matching

**Solution:**
- Applied lookup function referencing source1_naukri_applicants
- Logic: If email found in source1 (case-insensitive), use that version; otherwise keep as-is
- This preserved the canonical email version for duplicate detection

**Outcome:** Emails standardized for consistent entity matching

---

### Issue 5: Circular Row Shift - Data Corruption

**Problem:**
- One row in source2_gig_workers was circularly shifted right by 1 position
- Data values were misaligned across columns

**Solution:**
- Manually identified and corrected the misaligned row
- Verified correction against other records

**Outcome:** 1 row corrected

---

### Issue 6: Duplicate Rows - Exact & Fuzzy Duplicates

**Problem:**
- **source1_naukri_applicants**: 42 rows, but only 41 unique emails and 40 unique phone numbers
- Two rows differed only in name ("R. Verma" vs "Rohit Verma") — same person
- Two entries had different Gmail addresses but same phone number (alternate vs primary email)

**Solution:**
- Removed exact duplicates using Excel's "Remove Duplicates" feature
- Used conditional formatting to identify fuzzy duplicates
- Manually verified and merged duplicate entries

**Outcome:** 40 unique people in source1; duplicates resolved before database load

---

## 5. Stuck Log

This section documents the most challenging parts of the project and how they were resolved.

### Challenge 1: Data Cleaning in Excel (Not Alteryx)

**The Problem:**
Coming from a data analyst background with Alteryx experience, having to perform all data cleaning in Excel was a significant learning curve. Alteryx provides a visual workflow interface with specialized data transformation tools. Excel, while powerful, requires manual formulas and conditional logic for the same operations.

**What I Searched:**
- "Excel Flash Fill tutorial"
- "Excel conditional formatting for duplicate detection"
- "Excel formulas for text manipulation"

**What I Asked AI:**
- "How do I convert scientific notation in Excel to decimal?"
- "What Excel formula can extract the last 10 characters of a string?"
- "How can I use Flash Fill in Excel to detect date format patterns?"

**Suggestions I Rejected & Why:**
- Writing Python scripts for preprocessing: rejected because the requirement was to demonstrate data cleaning proficiency in the native tool (Excel)
- Using online CSV conversion tools: rejected because it didn't provide visibility into transformation logic

**How I Got Unstuck:**
- Leveraged Excel's native features: Flash Fill (pattern recognition), conditional formatting (duplicate detection), formulas (data transformations)
- Broke down each data quality issue into discrete Excel operations
- Tested transformations on small subsets before applying to full datasets

---

### Challenge 2: Learning n8n for Workflow Automation

**The Problem:**
Had to learn n8n from scratch to automate the duplicate detection workflow. n8n is a workflow automation platform with a node-based interface, but had no prior experience with it.

**What I Searched:**
- "How to build n8n workflows"
- "n8n HTTP request node"

**What I Asked AI:**
- "How do to set up an HTTP request node in n8n?"
- "How do I pass data between n8n nodes?"
- "What's the n8n syntax for conditional logic in workflows?"

**Suggestions I Rejected & Why:**
- Using Zapier instead: rejected because we wanted an open-source, self-hosted solution
- Writing Python scripts instead: rejected because we needed a visual workflow for maintainability

**How I Got Unstuck:**
- Reviewed n8n's built-in node library and examples
- Started with simple workflows (HTTP request → data transform) before building complex logic
- Used n8n's debugging tools to inspect data at each node
- Tested workflows incrementally

---

### Challenge 3: n8n + Docker + SQLite Database Access (Solved with Convex)

**The Problem:**
n8n runs inside a Docker container, but the SQLite database (`people.db`) exists on the Windows host machine. There were three challenges:

1. **Path Mounting:** The Windows path (`C:\Users\sloth\Downloads\consultbae\database\people.db`) is not valid inside the Linux Docker container. Would need to mount the Windows directory to a container path (e.g., `/files/consultbae/database/people.db`).

2. **n8n SQLite Support:** n8n doesn't have a native SQLite database node. The platform excels at HTTP requests and data transformation, not direct file system database queries.

3. **Complexity:** Even with proper mounting, accessing SQLite from n8n would require:
   - Configuring Docker volume mounts correctly
   - Handling file permissions between Windows and Linux
   - Writing custom SQL or finding a workaround node

**What I Searched:**
- "n8n SQLite database integration"
- "Docker mount Windows folder to Linux path"
- "n8n local database access"
- "SQLite ODBC driver for n8n"

**What I Asked AI:**
- "How do I access a SQLite database from n8n running in Docker?"
- "What's the correct Docker volume mount syntax for Windows paths?"
- "Are there alternatives to SQLite that n8n can access more easily?"

**Suggestions I Rejected & Why:**
- Mounting SQLite via Docker volumes: rejected because of complexity and potential permission issues between Windows and Linux filesystems
- Creating a separate REST API for the database: rejected because it added unnecessary layers and time constraints
- Using ODBC drivers: rejected because setup would be fragile and environment-dependent

**How I Got Unstuck:**
- Decided to move the `persons` table to **Convex**, a serverless backend platform
- Convex provides:
  - A managed cloud database
  - HTTP API endpoints that n8n can easily query
  - Automatic schema management and type safety
- The n8n workflow now makes a simple HTTP POST request:
  ```
  POST https://adept-akita-540.convex.cloud/api/query
  Request: { function: "people:findMatches", params: {...} }
  Response: Matching person records
  ```
- This completely eliminated the file system path problem and Docker complexity

(Sometimes the best solution to a complex infrastructure problem is to shift the architecture entirely. Serverless solutions like Convex are simpler than managing Docker volumes and local databases.)

---

## 6. Architecture

### Data Flow

```
Source CSVs
    ↓
[Excel Cleaning & Normalization]
    ↓
Python Ingestion Pipeline
    ├─ Database Schema Creation
    ├─ Data Validation
    ├─ Duplicate Detection
    └─ Entity Resolution
    ↓
SQLite Database (people.db)
    ├─ persons (master table)
    ├─ naukri_applicants
    ├─ gig_workers
    └─ cbnexus_contacts
    ↓
Convex (Cloud Backend) ← n8n Workflows Access
    ↓
[Optional] Audio App (Flask)
```

### Key Design Decisions

1. **Master-Detail Pattern:** Single `persons` table references multiple source-specific tables
2. **Local SQLite + Cloud Convex:** Local development with SQLite; cloud sync via Convex for distributed workflows (n8n)
3. **Duplicate Detection:** Multi-stage approach combining phone/email matching and manual fuzzy matching

---

## 7. Usage

### Run the Complete Pipeline
```bash
python src/ingest.py
```

### Check Database Contents
```bash
python src/check_db.py
```

### Verify Duplicates
```bash
python src/check_duplicates.py
```

### Create SQL Views
```bash
python src/create_view.py
```

### Run n8n Workflows
1. Navigate to n8n UI: `http://localhost:5678`
2. Import workflow: `n8n workflow/Duplicate detection.json`
3. Execute workflow

### Use the Audio App
```bash
cd audioapp
pip install -r requirements.txt
streamlit run app.py
# Access at http://localhost:8501
```

**Features:**
- Two-tab interface: 📝 Submit Audio + 🎵 View Recordings
- Record or upload audio with automatic quality analysis
- View all submissions with playable audio and metrics
- Automatic person linking via phone number

---

## 8. Task 2: n8n Automation (CSV Duplicate Detection)

### Workflow Overview

The n8n automation implements: **CSV Input → Database Check → Duplicate Detection → Email Alert**

**What it does:**
1. Reads a test CSV file from the local filesystem
2. Normalizes the data (name, email, phone)
3. Queries the Convex backend (cloud copy of master persons table)
4. Matches incoming records against database using matching rules
5. Classifies each record as: **DUPLICATE**, **WARNING**, or **NEW**
6. Sends email alerts for DUPLICATE and WARNING records

### Matching Logic

The workflow uses the following rules to classify incoming records:

| Match Type | Fields Matched | Action |
|-----------|----------------|--------|
| **Email** | Email only | DUPLICATE |
| **Email + Phone** | Email AND Phone match | DUPLICATE |
| **Name + Email** | Name AND Email match | DUPLICATE |
| **Name + Phone** | Name AND Phone match | DUPLICATE |
| **Name + Email + Phone** | All three fields match | DUPLICATE |
| **Name only** | Name matches only | WARNING |
| **Phone only** | Phone matches only | WARNING |
| **No match** | None of the above | NEW |

**Key design decision:** Email is treated as a strong unique identifier. If email matches, it's classified as DUPLICATE regardless of name mismatch.

### Test CSV

**Location:** `data/incoming/test.csv`

**Example data:**
```
Full name,Email,Phone
Tanvi Gupta,tanvi.gupta31@example.com,9000000254
John Doe,john.doe@example.com,9000000999
```

### n8n Workflow Architecture

**Nodes:**
1. **Manual Trigger** - Start the workflow
2. **Read/Write Files from Disk** - Load test.csv
3. **Extract from File** - Parse CSV into JSON rows
4. **Code Node 1 (Normalize)** - Extract fields: name, email, phone
5. **HTTP Request** - Query Convex backend
6. **Merge** - Combine original data with Convex response
7. **Code Node 2 (Match Logic)** - Apply matching rules
8. **Switch / If Routing** - Conditional logic for alerts
9. **Gmail Nodes** - Send email notifications

### Convex Backend Integration

**Why Convex?**
- Local SQLite database runs on Windows host
- n8n runs inside Docker container (Linux)
- Convex provides HTTP-accessible copy of master persons table

**Convex Details:**
- **URL:** https://adept-akita-540.convex.cloud
- **Function:** `people:findMatches`
- **Input:** name, email, phone
- **Output:** Array of matching person records

### Running the Workflow

1. **Start n8n in Docker:**
   ```bash
   docker run -d --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n n8nio/n8n:latest
   ```

2. **Access n8n UI:** `http://localhost:5678`

3. **Import workflow:** `n8n workflow/Duplicate detection.json`

4. **Execute workflow:** Click "Execute Workflow" button

### Final Results

**Task 1:**
- 101 total source records
- 60 unique persons identified
- 15 persons in all 3 sources

**Task 2:**
- ✅ CSV ingestion from filesystem
- ✅ Real-time database matching via Convex API
- ✅ 3-tier classification (DUPLICATE/WARNING/NEW)
- ✅ Email alerting for matches
- ✅ Workflow exported as JSON