-- Database schema for attendance management system
-- Generated from PDF attendance data extraction

-- Drop tables if they exist (for clean re-creation)
DROP TABLE IF EXISTS attendance_records;
DROP TABLE IF EXISTS employees;

-- Employees table
CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id VARCHAR(20) UNIQUE NOT NULL,
    employee_name VARCHAR(100) NOT NULL,
    branch VARCHAR(100),
    department VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on employee_id for faster lookups
CREATE INDEX idx_employee_id ON employees(employee_id);

-- Attendance records table
CREATE TABLE attendance_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id VARCHAR(20) NOT NULL,
    employee_name VARCHAR(100) NOT NULL,
    branch VARCHAR(100),
    department VARCHAR(200),
    attendance_date VARCHAR(20) NOT NULL,
    in_time VARCHAR(10),
    out_time VARCHAR(10),
    total_hours VARCHAR(10),
    break_time VARCHAR(10),
    overtime_hours VARCHAR(10),
    status VARCHAR(10),
    shift_timing VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

-- Create indexes for better query performance
CREATE INDEX idx_attendance_employee_id ON attendance_records(employee_id);
CREATE INDEX idx_attendance_date ON attendance_records(attendance_date);
CREATE INDEX idx_attendance_status ON attendance_records(status);

-- Status codes reference (for documentation):
-- A = Absent
-- HD = Half Day
-- E = Early/Late (incomplete attendance)
-- LH = Less Hours
-- P = Present (full day)
-- W = Weekly Off
-- H = Holiday
-- PH = Present On Holiday
-- PW = Present On WeekOff Day
-- PHW = Present On Holiday & WeekOff Day
-- CL = Casual Leave
-- HCL = Half Casual Leave
