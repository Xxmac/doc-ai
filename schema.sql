-- PostgreSQL Schema for Hospital Appointment System

CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE doctors (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    department_id INT REFERENCES departments(id),
    is_available BOOLEAN DEFAULT TRUE,
    time_slot TIMESTAMP
);

CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    patient_name TEXT,
    doctor_id INT REFERENCES doctors(id),
    time_slot TIMESTAMP,
    status TEXT CHECK (status IN ('scheduled', 'cancelled', 'completed')) DEFAULT 'scheduled'
);
