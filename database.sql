-- ─────────────────────────────────────────────────────
--  Campus Care Portal — Database Schema
-- ─────────────────────────────────────────────────────

CREATE DATABASE IF NOT EXISTS campus_care;
USE campus_care;

-- ─── Doctor ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS Doctor (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    username       VARCHAR(100)  NOT NULL UNIQUE,
    password       VARCHAR(255)  NOT NULL,           -- bcrypt/werkzeug hash
    specialization VARCHAR(100)  NOT NULL
);

-- ─── Patient ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS Patient (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    roll_no      VARCHAR(20)   NOT NULL,
    name         VARCHAR(100)  NOT NULL,
    year         INT           NOT NULL,
    disease      VARCHAR(200)  NOT NULL,
    status       VARCHAR(50)   DEFAULT 'Pending',    -- Pending | Medicine | Appointment | Discharged
    doctor_name  VARCHAR(100),
    prescription TEXT,
    submitted_at TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (doctor_name) REFERENCES Doctor(username) ON DELETE SET NULL
);

-- ─── Admin ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS Admin (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100)  NOT NULL UNIQUE,
    password VARCHAR(255)  NOT NULL                  -- bcrypt/werkzeug hash
);

-- ─────────────────────────────────────────────────────
--  Seed Data
--  Passwords below are werkzeug hashes of 'doctor123'
--  and 'admin123' respectively.
--  Generate fresh hashes with:
--    python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('doctor123'))"
-- ─────────────────────────────────────────────────────

INSERT IGNORE INTO Doctor (username, password, specialization) VALUES
('dr_sharma',  'scrypt:32768:8:1$K3zXtseyXzmsO1qo$4ea0deb65fbd6b40245a715735339f250fc132195b2fb6d79e1e4ddcf52bd843fea429bc1d0e62066af0bc0efbcd2f1747726cceebc819bf789c947a288ada0f', 'General Medicine'),
('dr_patel',   'scrypt:32768:8:1$K3zXtseyXzmsO1qo$4ea0deb65fbd6b40245a715735339f250fc132195b2fb6d79e1e4ddcf52bd843fea429bc1d0e62066af0bc0efbcd2f1747726cceebc819bf789c947a288ada0f', 'Orthopedics'),
('dr_mehta',   'scrypt:32768:8:1$K3zXtseyXzmsO1qo$4ea0deb65fbd6b40245a715735339f250fc132195b2fb6d79e1e4ddcf52bd843fea429bc1d0e62066af0bc0efbcd2f1747726cceebc819bf789c947a288ada0f', 'Dermatology');

INSERT IGNORE INTO Admin (username, password) VALUES
('admin', 'scrypt:32768:8:1$TjSqpO5Nsn1geD2b$a1447cbf7a96fa591f2648d5ab42b847cf9a13c9c041cdc89b4683c522ac4e83b8c46652c47629520416402c15923a49c2ba3fd87c841aecf7510367ebf309d2');