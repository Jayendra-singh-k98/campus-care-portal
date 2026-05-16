DROP TABLE IF EXISTS Patient;

CREATE TABLE Patient (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    roll_no      VARCHAR(20)   NOT NULL,
    name         VARCHAR(100)  NOT NULL,
    year         INT           NOT NULL,
    disease      VARCHAR(200)  NOT NULL,
    status       VARCHAR(50)   DEFAULT 'Pending',
    doctor_name  VARCHAR(100),
    prescription TEXT,
    submitted_at TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (doctor_name) REFERENCES Doctor(username) ON DELETE SET NULL
);

DESCRIBE Patient;
