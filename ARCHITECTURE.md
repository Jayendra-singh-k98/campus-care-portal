# Campus Care Portal - Architecture & MySQL Connection Flow

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        USER BROWSERS (Frontend)                         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐  │
│  │  Patient Portal  │  │  Doctor Portal   │  │   Admin Panel        │  │
│  │  (index.html)    │  │ (doctor_dash..)  │  │ (admin_dashboard)    │  │
│  └────────┬─────────┘  └────────┬─────────┘  └──────────┬───────────┘  │
└───────────┼──────────────────────┼──────────────────────┼──────────────┘
            │ HTTP POST/GET        │                      │
            │ HTML Forms           │                      │
┌───────────▼──────────────────────▼──────────────────────▼──────────────┐
│                         FLASK APPLICATION (app.py)                     │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Routes:                                                         │  │
│  │  • /login              (POST)  → Process credentials            │  │
│  │  • /patient_dashboard  (GET)   → Render patient portal          │  │
│  │  • /submit_patient     (POST)  → Insert complaint               │  │
│  │  • /doctor_dashboard   (GET)   → Fetch & render patients        │  │
│  │  • /update_status      (POST)  → Update patient status          │  │
│  │  • /admin_dashboard    (GET)   → Fetch stats & doctors          │  │
│  │  • /check_status       (GET/POST) → Query patient records       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Session Management:                                             │  │
│  │  • Stores user_role (patient/doctor/admin)                       │  │
│  │  • Maintains authentication state                                │  │
│  │  • Role-based access control                                     │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  PyMySQL Connector: get_db_connection()                          │  │
│  │  ├─ host: localhost                                              │  │
│  │  ├─ user: root                                                   │  │
│  │  ├─ password: Kuntal@2006 (CHANGE FOR PRODUCTION)               │  │
│  │  └─ database: campus_care                                        │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└───────────┬──────────────────────────────────────────────────────────────┘
            │ MySQL Protocol
            │ SQL Queries (SELECT, INSERT, UPDATE)
┌───────────▼──────────────────────────────────────────────────────────────┐
│                          MYSQL DATABASE                                  │
│  ┌─────────────────────┐  ┌──────────────────┐  ┌─────────────────────┐ │
│  │   Doctor Table      │  │  Patient Table   │  │   Admin Table       │ │
│  ├─────────────────────┤  ├──────────────────┤  ├─────────────────────┤ │
│  │ id (PK)             │  │ id (PK)          │  │ id (PK)             │ │
│  │ username (UNIQUE)   │  │ roll_no          │  │ username (UNIQUE)   │ │
│  │ password (hashed)   │  │ name             │  │ password (hashed)   │ │
│  │ specialization      │  │ year             │  │                     │ │
│  │                     │  │ disease          │  │                     │ │
│  │                     │  │ status           │  │                     │ │
│  │                     │  │ doctor_name (FK) │  │                     │ │
│  │                     │  │ prescription      │  │                     │ │
│  │                     │  │ submitted_at      │  │                     │ │
│  └─────────────────────┘  └──────────────────┘  └─────────────────────┘ │
│                                                                           │
│  Database: campus_care                                                   │
│  Port: 3306 (default MySQL)                                              │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Examples

### 1. Patient Complaint Submission Flow

```
Patient fills form               HTML Form Input
    ↓
Clicks "Submit Complaint"        Browser Event
    ↓
Form POSTs to /submit_patient    HTTP POST
    ↓
Flask receives request            request.form parsing
    ↓
Extracts: roll_no, name, year, disease, doctor
    ↓
Calls get_db_connection()         PyMySQL → MySQL
    ↓
Checks duplicate case             SELECT query
    ↓
Inserts into Patient table        INSERT query
    ↓
conn.commit()                     Database persists
    ↓
Renders success.html              Return page to browser
```

### 2. Doctor Dashboard Load Flow

```
Doctor visits /doctor_dashboard  GET request
    ↓
@login_required decorator        Session check
    ↓
Session['user_role'] == 'doctor'  ✓ Authorized
    ↓
Calls get_db_connection()         Connect to MySQL
    ↓
SELECT * FROM Patient WHERE doctor_name = ?
    ↓
Fetches matching patients        cursor.fetchall()
    ↓
Calculates statistics            Count by status
    ↓
Renders doctor_dashboard.html     Jinja2 template
    ↓
Displays: patient list, stats    Browser renders page
```

### 3. Patient Status Check Flow

```
Patient enters roll_no           Search form
    ↓
POSTs to /check_status           HTTP POST
    ↓
Flask receives roll_no            Form parsing
    ↓
Calls get_db_connection()         Connect to MySQL
    ↓
SELECT * FROM Patient WHERE roll_no = ?
    ↓
Returns all records for that roll_no
    ↓
Renders patient_status.html       Show all cases
    ↓
Displays: condition, status, prescription
```

---

## Database Connection Points

### Direct MySQL Access (app.py)

```python
# 1. Doctor Login Verification
cursor.execute('SELECT * FROM Doctor WHERE username = %s', (username,))
doctor = cursor.fetchone()  # Returns: (id, username, password_hash, specialization)

# 2. Patient Submission
cursor.execute(
    'INSERT INTO Patient (roll_no, name, year, disease, status, doctor_name) '
    'VALUES (%s, %s, %s, %s, %s, %s)',
    (roll_no, name, year, disease, 'Pending', doctor)
)
conn.commit()  # Persist to database

# 3. Doctor's Patient List
cursor.execute(
    'SELECT * FROM Patient WHERE doctor_name = %s ORDER BY submitted_at DESC',
    (doctor_name,)
)
patients = cursor.fetchall()  # List of all patient records

# 4. Update Patient Status
cursor.execute(
    'UPDATE Patient SET status = %s, prescription = %s WHERE roll_no = %s',
    (status, prescription, roll_no)
)
conn.commit()

# 5. Admin Doctor Management
cursor.execute('SELECT * FROM Doctor ORDER BY specialization, username')
doctors = cursor.fetchall()

cursor.execute(
    'INSERT INTO Doctor (username, password, specialization) VALUES (%s, %s, %s)',
    (username, password_hash, specialization)
)
```

---

## Frontend → MySQL Connection Validation

### All HTML Forms → Flask Routes → MySQL

| Form | Route | Query | Table |
|------|-------|-------|-------|
| Login Form | `/login` | SELECT username, password | Doctor/Admin |
| Patient Complaint | `/submit_patient` | INSERT INTO Patient | Patient |
| Status Update (Doctor) | `/update_status` | UPDATE Patient | Patient |
| Add Doctor (Admin) | `/admin/add_doctor` | INSERT INTO Doctor | Doctor |
| Delete Doctor (Admin) | `/admin/delete_doctor` | DELETE FROM Doctor | Doctor |
| Status Check (Public) | `/check_status` | SELECT FROM Patient | Patient |

---

## Authentication Flow

```
┌──────────────────┐
│  Login Page      │
│  (index.html)    │
└────────┬─────────┘
         │ POST /login (role, username, password)
         ▼
┌──────────────────────────────────┐
│  Flask /login Route              │
├──────────────────────────────────┤
│ 1. Extract: role, username, pass │
│ 2. Get DB connection             │
│ 3. IF role == 'doctor':          │
│    - Query: SELECT * FROM Doctor │
│    - Check: password hash match  │
│    - IF match: create session    │
│ 4. IF role == 'admin':           │
│    - Query: SELECT * FROM Admin  │
│    - Check: password hash match  │
│    - IF match: create session    │
│ 5. IF role == 'patient':         │
│    - No password check needed    │
│    - Create session directly     │
└────────┬─────────────────────────┘
         │
         ▼
    ┌─ Redirect ─┐
    │            │
Patient      Doctor        Admin
Dashboard    Dashboard     Dashboard
```

---

## Environment Variables (For Production)

```python
# Currently hardcoded in app.py line 16:
password="Kuntal@2006"

# Should be moved to environment variables:
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD'),  # From .env file
        database=os.getenv('DB_NAME', 'campus_care')
    )
```

---

## Security Considerations

1. **Password Hashing**: ✓ Using werkzeug.security.generate_password_hash
2. **SQL Injection Prevention**: ✓ Using parameterized queries with %s
3. **Session Management**: ✓ Flask sessions with secret_key
4. **Role-Based Access**: ✓ @login_required decorators checking role
5. **Database Credentials**: ⚠️ Currently hardcoded - move to .env

---

## Connection Status: ✓ FULLY INTEGRATED

✓ Frontend HTML forms send data to Flask routes
✓ Flask routes use PyMySQL to query MySQL database
✓ Query results are rendered back to frontend templates
✓ All CRUD operations (Create, Read, Update, Delete) working
✓ Session management maintaining user state
✓ Role-based authorization protecting routes

**The MySQL-Frontend connection is fully functional and operational.**
