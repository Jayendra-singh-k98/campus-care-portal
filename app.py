import os
from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
from functools import wraps
from dotenv import load_dotenv

# Load local .env in development (ignored in production platforms where env vars are set)
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'campus_care_secret_key_change_in_production')


# ─── DB 

def get_db_connection():
    try:
        return pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'campus_care'),
            port=int(os.getenv('DB_PORT', 3306)),
            charset='utf8mb4',
            connect_timeout=5
        )
    except pymysql.err.OperationalError as err:
        app.logger.exception('Database connection failed')
        # Raise a higher-level error that Flask can handle and render a friendly page
        raise RuntimeError(
            'Database connection failed: check DB_HOST, DB_USER, DB_PASSWORD, and DB_NAME.'
        ) from err


# ─── Auth Decorator ──────────────────────────────────────────────────────────

def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_role' not in session:
                flash('Please login to continue.', 'error')
                return redirect(url_for('home'))
            if role and session['user_role'] != role:
                flash('Unauthorized access.', 'error')
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.route('/')
def home():
    # Redirect already-logged-in users
    if 'user_role' in session:
        role = session['user_role']
        if role == 'doctor':
            return redirect(url_for('doctor_dashboard'))
        elif role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif role == 'patient':
            return redirect(url_for('patient_dashboard'))
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    role     = request.form.get('role', '').strip()
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    conn   = get_db_connection()
    cursor = conn.cursor()

    if role == 'patient':
        cursor.execute('SELECT * FROM Doctor ORDER BY specialization, username')
        doctors = cursor.fetchall()
        conn.close()
        session['user_role']         = 'patient'
        session['patient_username']  = username
        return redirect(url_for('patient_dashboard'))

    elif role == 'doctor':
        cursor.execute('SELECT * FROM Doctor WHERE username = %s', (username,))
        doctor = cursor.fetchone()
        conn.close()
        if doctor and check_password_hash(doctor[2], password):
            session['user_role']             = 'doctor'
            session['doctor_name']           = doctor[1]
            session['doctor_specialization'] = doctor[3]
            return redirect(url_for('doctor_dashboard'))
        flash('Invalid doctor credentials. Please try again.', 'error')
        return redirect(url_for('home'))

    elif role == 'admin':
        cursor.execute('SELECT * FROM Admin WHERE username = %s', (username,))
        admin = cursor.fetchone()
        conn.close()
        if admin and check_password_hash(admin[2], password):
            session['user_role']  = 'admin'
            session['admin_name'] = admin[1]
            return redirect(url_for('admin_dashboard'))
        flash('Invalid admin credentials.', 'error')
        return redirect(url_for('home'))

    conn.close()
    flash('Please select a valid role.', 'error')
    return redirect(url_for('home'))


@app.route('/submit_patient', methods=['POST'])
def submit_patient():
    roll_no = request.form['roll_no'].strip()
    name    = request.form['name'].strip()
    year    = request.form['year']
    disease = request.form['disease'].strip()
    doctor  = request.form['doctor']

    conn   = get_db_connection()
    cursor = conn.cursor()

    # Prevent duplicate active cases
    cursor.execute(
        "SELECT * FROM Patient WHERE roll_no = %s AND status NOT IN ('Discharged')",
        (roll_no,)
    )
    existing = cursor.fetchone()
    if existing:
        conn.close()
        flash(
            f'Roll No {roll_no} already has an active case '
            f'(Status: {existing[5]}). Wait for it to be resolved.',
            'warning'
        )

    cursor.execute(
        'INSERT INTO Patient (roll_no, name, year, disease, status, doctor_name) '
        'VALUES (%s, %s, %s, %s, %s, %s)',
        (roll_no, name, year, disease, 'Pending', doctor)
    )
    conn.commit()
    conn.close()
    return render_template('success.html', roll_no=roll_no, name=name, doctor=doctor)


@app.route('/patient_dashboard')
@login_required(role='patient')
def patient_dashboard():
    conn   = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Doctor ORDER BY specialization, username')
    doctors = cursor.fetchall()
    conn.close()
    username = session.get('patient_username', '')
    return render_template('patient_dashboard.html', doctors=doctors, username=username)


@app.route('/check_status', methods=['GET', 'POST'])
def check_status():
    records  = None
    roll_no  = None
    if request.method == 'POST':
        roll_no = request.form.get('roll_no', '').strip()
        conn    = get_db_connection()
        cursor  = conn.cursor()
        cursor.execute(
            'SELECT * FROM Patient WHERE roll_no = %s ORDER BY submitted_at DESC',
            (roll_no,)
        )
        records = cursor.fetchall()
        conn.close()
    return render_template('patient_status.html', records=records, roll_no=roll_no)


@app.route('/doctor_dashboard')
@login_required(role='doctor')
def doctor_dashboard():
    doctor_name    = session['doctor_name']
    specialization = session.get('doctor_specialization', '')

    conn   = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM Patient WHERE doctor_name = %s ORDER BY submitted_at DESC',
        (doctor_name,)
    )
    patients = cursor.fetchall()
    conn.close()

    stats = {
        'total':       len(patients),
        'pending':     sum(1 for p in patients if p[5] == 'Pending'),
        'medicine':    sum(1 for p in patients if p[5] == 'Medicine'),
        'appointment': sum(1 for p in patients if p[5] == 'Appointment'),
        'discharged':  sum(1 for p in patients if p[5] == 'Discharged'),
    }

    return render_template(
        'doctor_dashboard.html',
        patients=patients,
        doctor_name=doctor_name,
        specialization=specialization,
        stats=stats
    )


@app.route('/update_status', methods=['POST'])
@login_required(role='doctor')
def update_status():
    roll_no      = request.form['roll_no']
    status       = request.form['status']
    prescription = request.form.get('prescription', '').strip()

    conn   = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE Patient SET status = %s, prescription = %s WHERE roll_no = %s',
        (status, prescription, roll_no)
    )
    conn.commit()
    conn.close()
    return redirect(url_for('doctor_dashboard'))


# ─── Admin ───────────────────────────────────────────────────────────────────

@app.route('/admin_dashboard')
@login_required(role='admin')
def admin_dashboard():
    conn   = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Doctor ORDER BY specialization, username')
    doctors = cursor.fetchall()

    cursor.execute('SELECT COUNT(*) FROM Patient')
    total_patients = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Patient WHERE status = 'Pending'")
    pending = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Patient WHERE status = 'Medicine'")
    medicine = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Patient WHERE status = 'Appointment'")
    appointment = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Patient WHERE status = 'Discharged'")
    discharged = cursor.fetchone()[0]

    conn.close()

    stats = {
        'total_patients': total_patients,
        'total_doctors':  len(doctors),
        'pending':        pending,
        'medicine':       medicine,
        'appointment':    appointment,
        'discharged':     discharged,
    }
    return render_template('admin_dashboard.html', doctors=doctors, stats=stats)


@app.route('/admin/add_doctor', methods=['POST'])
@login_required(role='admin')
def add_doctor():
    username       = request.form['username'].strip()
    password       = generate_password_hash(request.form['password'])
    specialization = request.form['specialization'].strip()

    conn   = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO Doctor (username, password, specialization) VALUES (%s, %s, %s)',
            (username, password, specialization)
        )
        conn.commit()
        flash(f'Dr. {username} added successfully!', 'success')
    except pymysql.err.IntegrityError:
        flash(f'Username "{username}" already exists.', 'error')
    finally:
        conn.close()
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/delete_doctor/<int:doctor_id>', methods=['POST'])
@login_required(role='admin')
def delete_doctor(doctor_id):
    conn   = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Doctor WHERE id = %s', (doctor_id,))
    conn.commit()
    conn.close()
    flash('Doctor removed successfully.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')
    app.run(host='0.0.0.0', port=port, debug=debug)


# --- Error handlers ---------------------------------------------------------
@app.errorhandler(RuntimeError)
def handle_runtime_error(error):
    # Show a friendly message for runtime errors (e.g. DB connection problems)
    message = str(error)
    return render_template('error.html', message=message), 503


@app.errorhandler(500)
def handle_internal_error(error):
    # Generic 500 handler to avoid exposing internals in production
    app.logger.exception('Internal server error')
    return render_template('error.html', message='Internal server error.'), 500