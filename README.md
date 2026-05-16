# Campus Care Portal - Setup & Configuration Guide

## Prerequisites
- Python 3.8+
- MySQL Server (running)
- pip package manager

## Installation Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. MySQL Database Setup
```bash
# Connect to MySQL
mysql -u root -p

# Copy and run the entire content of database.sql
# Or use: mysql -u root -p campus_care < database.sql
```

### 3. Configuration
The app currently uses these MySQL credentials (UPDATE in app.py):
- **Host**: localhost
- **User**: root
- **Password**: Kuntal@2006 (CHANGE THIS!)
- **Database**: campus_care

⚠️ **Security Warning**: These credentials are hardcoded. For production, use environment variables:

```python
# Option 1: Use .env file
from dotenv import load_dotenv
import os

load_dotenv()
def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME', 'campus_care')
    )
```

Create `.env`:
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=campus_care
```

## Running the Application

```bash
python app.py
```

The application will run on: **http://localhost:5000**

## Default Login Credentials

| Role  | Username | Password  |
|-------|----------|-----------|
| Admin | admin    | admin123  |
| Doctor| dr_sharma| doctor123 |
| Doctor| dr_patel | doctor123 |
| Doctor| dr_mehta | doctor123 |
| Patient| (any roll no) | (no password needed) |

## Features

### Patient Portal
- Submit health complaints (no login required)
- Track case status using roll number
- Select assigned doctor
- View prescription and doctor notes

### Doctor Dashboard
- View assigned patients
- Update patient status (Pending → Medicine → Appointment → Discharged)
- Add prescription notes
- Track statistics

### Admin Panel
- Manage doctors (add/remove)
- View system statistics
- Track patient cases
- Monitor all activities

## File Structure

```
campus_care/
├── app.py                      # Main Flask application
├── database.sql                # Database schema & seed data
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── static/
│   ├── style_base.css
│   ├── style_admin.css
│   ├── style_doctor.css
│   ├── style_ind.css
│   ├── style_patient.css
│   └── style_status.css
└── templates/
    ├── index.html              # Login page
    ├── patient_dashboard.html
    ├── doctor_dashboard.html
    ├── admin_dashboard.html
    ├── patient_status.html
    └── success.html
```

## Database Schema

### Doctor Table
- id (INT, Primary Key)
- username (VARCHAR, Unique)
- password (VARCHAR, hashed)
- specialization (VARCHAR)

### Patient Table
- id (INT, Primary Key)
- roll_no (VARCHAR)
- name (VARCHAR)
- year (INT)
- disease (VARCHAR)
- status (VARCHAR) - Pending | Medicine | Appointment | Discharged
- doctor_name (VARCHAR, Foreign Key)
- prescription (TEXT)
- submitted_at (TIMESTAMP)

### Admin Table
- id (INT, Primary Key)
- username (VARCHAR, Unique)
- password (VARCHAR, hashed)

## Troubleshooting

### MySQL Connection Error
```
Error: "Can't connect to MySQL server"
```
**Solution:**
1. Ensure MySQL is running: `mysql -u root -p`
2. Check credentials in app.py
3. Verify database exists: `SHOW DATABASES;`

### Database Not Found
```
Error: "Unknown database 'campus_care'"
```
**Solution:** Run database.sql first:
```bash
mysql -u root -p < database.sql
```

### Password Hash Error
```
Error: "Invalid credentials"
```
**Solution:** Regenerate password hashes:
```bash
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('doctor123'))"
```

## Password Reset

To reset a doctor's password to "doctor123":
```bash
python -c "
from werkzeug.security import generate_password_hash
hash = generate_password_hash('doctor123')
print(f\"UPDATE Doctor SET password = '{hash}' WHERE username = 'dr_sharma';\")
"
```

Then execute the SQL in MySQL.

## Security Recommendations

1. **Change default credentials** in database.sql before production
2. **Use environment variables** for database credentials
3. **Enable HTTPS** when deployed
4. **Add CSRF protection** for production
5. **Use strong session keys** - generate a new one:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
6. **Restrict IP access** to database
7. **Add rate limiting** to login endpoint
8. **Implement logging** for audit trail

## Development Tips

- Enable debug mode: `app.run(debug=True)` (already enabled)
- Check app logs for detailed error messages
- Use Firefox DevTools or Chrome DevTools for frontend debugging
- Test database queries directly in MySQL before adding to app

## Support

For issues or questions, check:
1. Database connection settings
2. MySQL is running and credentials are correct
3. All tables are created with `database.sql`
4. Dependencies are installed: `pip list | grep -i flask`
