-- Fix: Add missing submitted_at column to Patient table

ALTER TABLE Patient 
ADD COLUMN submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
AFTER prescription;

-- Verify the change
DESCRIBE Patient;
