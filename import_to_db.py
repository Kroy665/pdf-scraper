#!/usr/bin/env python3
"""
Import attendance data from JSON to SQLite database
"""
import json
import sqlite3
import sys
from pathlib import Path


def import_to_sqlite(json_file, db_file="attendance.db"):
    """
    Import JSON data to SQLite database

    Args:
        json_file: Path to the JSON file with attendance data
        db_file: Path to the SQLite database file (default: attendance.db)
    """
    print(f"Loading data from: {json_file}")

    # Load JSON data
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Found {len(data['employees'])} employees")
    print(f"Found {len(data['attendance'])} attendance records")

    # Connect to database
    print(f"\nConnecting to database: {db_file}")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Read and execute schema
    schema_file = Path(__file__).parent / "schema.sql"
    if schema_file.exists():
        print("Creating database schema...")
        with open(schema_file, 'r') as f:
            schema = f.read()
            cursor.executescript(schema)
    else:
        print("Warning: schema.sql not found, assuming tables exist")

    # Insert employees
    print("\nInserting employees...")
    for emp in data['employees']:
        cursor.execute("""
            INSERT OR REPLACE INTO employees (employee_id, employee_name, branch, department)
            VALUES (?, ?, ?, ?)
        """, (
            emp['employee_id'],
            emp['employee_name'],
            emp['branch'],
            emp['department']
        ))

    print(f"Inserted {len(data['employees'])} employees")

    # Insert attendance records
    print("\nInserting attendance records...")
    for record in data['attendance']:
        cursor.execute("""
            INSERT INTO attendance_records (
                employee_id, employee_name, branch, department,
                attendance_date, in_time, out_time, total_hours,
                break_time, overtime_hours, status, shift_timing
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record['employee_id'],
            record['employee_name'],
            record['branch'],
            record['department'],
            record['attendance_date'],
            record['in_time'],
            record['out_time'],
            record['total_hours'],
            record['break_time'],
            record['overtime_hours'],
            record['status'],
            record['shift_timing']
        ))

    print(f"Inserted {len(data['attendance'])} attendance records")

    # Commit and close
    conn.commit()
    conn.close()

    print(f"\n✓ Data successfully imported to: {db_file}")

    # Print some sample queries
    print("\n" + "=" * 80)
    print("SAMPLE SQL QUERIES")
    print("=" * 80)
    print("\n1. Get all employees:")
    print("   SELECT * FROM employees;")
    print("\n2. Get attendance for a specific employee:")
    print("   SELECT * FROM attendance_records WHERE employee_id = 'DS2001';")
    print("\n3. Get all absent records:")
    print("   SELECT * FROM attendance_records WHERE status = 'A';")
    print("\n4. Count attendance by status:")
    print("   SELECT status, COUNT(*) as count FROM attendance_records GROUP BY status;")
    print("\n5. Get employee attendance summary:")
    print("""   SELECT
       employee_id,
       employee_name,
       COUNT(*) as total_days,
       SUM(CASE WHEN status = 'A' THEN 1 ELSE 0 END) as absent_days,
       SUM(CASE WHEN status = 'HD' THEN 1 ELSE 0 END) as half_days
   FROM attendance_records
   GROUP BY employee_id, employee_name;""")


def main():
    # Default JSON file
    default_json = Path(__file__).parent.parent / "D.EL.ED merged_db_ready.json"

    # Check if JSON file is provided as argument
    if len(sys.argv) > 1:
        json_file = Path(sys.argv[1])
    else:
        json_file = default_json

    if not json_file.exists():
        print(f"Error: JSON file not found at {json_file}")
        print(f"\nUsage: python import_to_db.py [json_file] [db_file]")
        sys.exit(1)

    # Get database file
    db_file = sys.argv[2] if len(sys.argv) > 2 else "attendance.db"

    import_to_sqlite(json_file, db_file)


if __name__ == "__main__":
    main()
