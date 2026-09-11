# PDF Attendance Scraper

A Python tool to extract structured attendance data from PDF reports and import it into a database.

## Features

- Extracts employee information (ID, name, branch, department)
- Parses attendance records with dates, times, and status
- Outputs structured JSON ready for database import
- Includes SQLite database schema and import script
- Handles complex table layouts with split rows

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
# Dependencies are already installed via uv
uv sync
```

## Usage

### 1. Extract Data from PDF

```bash
# Use default PDF file
uv run main.py

# Or specify a custom PDF file
uv run main.py path/to/your/attendance.pdf
```

**Output Files:**
- `[filename]_structured.json` - Complete data with metadata
- `[filename]_db_ready.json` - Simplified format for database import

### 2. Import to Database

```bash
# Import to SQLite database
uv run import_to_db.py

# Or specify custom files
uv run import_to_db.py path/to/data.json path/to/database.db
```

### 3. Query the Database

```bash
# Open SQLite database
sqlite3 attendance.db

# Run sample queries
sqlite> SELECT * FROM employees LIMIT 10;
sqlite> SELECT * FROM attendance_records WHERE status = 'A';
```

## Database Schema

### Employees Table

| Column        | Type         | Description              |
|---------------|--------------|--------------------------|
| id            | INTEGER      | Primary key              |
| employee_id   | VARCHAR(20)  | Unique employee ID       |
| employee_name | VARCHAR(100) | Employee name            |
| branch        | VARCHAR(100) | Branch location          |
| department    | VARCHAR(200) | Department name          |
| created_at    | TIMESTAMP    | Record creation time     |
| updated_at    | TIMESTAMP    | Last update time         |

### Attendance Records Table

| Column          | Type         | Description                    |
|-----------------|--------------|--------------------------------|
| id              | INTEGER      | Primary key                    |
| employee_id     | VARCHAR(20)  | Foreign key to employees       |
| employee_name   | VARCHAR(100) | Employee name                  |
| branch          | VARCHAR(100) | Branch location                |
| department      | VARCHAR(200) | Department name                |
| attendance_date | VARCHAR(20)  | Date of attendance             |
| in_time         | VARCHAR(10)  | Check-in time                  |
| out_time        | VARCHAR(10)  | Check-out time                 |
| total_hours     | VARCHAR(10)  | Total hours worked             |
| break_time      | VARCHAR(10)  | Break duration                 |
| overtime_hours  | VARCHAR(10)  | Overtime hours                 |
| status          | VARCHAR(10)  | Attendance status (see below)  |
| shift_timing    | VARCHAR(50)  | Shift timing info              |
| created_at      | TIMESTAMP    | Record creation time           |

## Status Codes

| Code | Description                     |
|------|---------------------------------|
| A    | Absent                          |
| HD   | Half Day                        |
| E    | Early/Late (incomplete)         |
| LH   | Less Hours                      |
| P    | Present (full day)              |
| W    | Weekly Off                      |
| H    | Holiday                         |
| PH   | Present On Holiday              |
| PW   | Present On WeekOff Day          |
| PHW  | Present On Holiday & WeekOff Day|
| CL   | Casual Leave                    |
| HCL  | Half Casual Leave               |

## Sample Queries

```sql
-- Get all employees
SELECT * FROM employees;

-- Get attendance for a specific employee
SELECT * FROM attendance_records
WHERE employee_id = 'DS2001'
ORDER BY attendance_date;

-- Get all absent records
SELECT employee_name, attendance_date
FROM attendance_records
WHERE status = 'A';

-- Count attendance by status
SELECT status, COUNT(*) as count
FROM attendance_records
GROUP BY status
ORDER BY count DESC;

-- Employee attendance summary
SELECT
    employee_id,
    employee_name,
    COUNT(*) as total_days,
    SUM(CASE WHEN status = 'A' THEN 1 ELSE 0 END) as absent_days,
    SUM(CASE WHEN status = 'HD' THEN 1 ELSE 0 END) as half_days,
    SUM(CASE WHEN status = 'E' THEN 1 ELSE 0 END) as early_late
FROM attendance_records
GROUP BY employee_id, employee_name
ORDER BY employee_name;

-- Get employees with high absence rate
SELECT
    employee_id,
    employee_name,
    COUNT(*) as total_days,
    SUM(CASE WHEN status = 'A' THEN 1 ELSE 0 END) as absent_days,
    ROUND(SUM(CASE WHEN status = 'A' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as absence_rate
FROM attendance_records
GROUP BY employee_id, employee_name
HAVING absence_rate > 10
ORDER BY absence_rate DESC;
```

## JSON Output Format

### Database-Ready Format (`_db_ready.json`)

```json
{
  "employees": [
    {
      "employee_id": "DS2001",
      "employee_name": "NIHARIKA ROY",
      "branch": "MAYNAGURI",
      "department": "D.El.Ed. PART-I SESSION-2025-27"
    }
  ],
  "attendance": [
    {
      "employee_id": "DS2001",
      "employee_name": "NIHARIKA ROY",
      "branch": "MAYNAGURI",
      "department": "D.El.Ed. PART-I SESSION-2025-27",
      "attendance_date": "12-May-2026",
      "in_time": "10:36:00",
      "out_time": "16:00:00",
      "total_hours": "04:24",
      "break_time": "",
      "overtime_hours": "00:00",
      "status": "HD",
      "shift_timing": "10:00 To 16:00"
    }
  ]
}
```

## Files

- `main.py` - PDF extraction script
- `import_to_db.py` - Database import script
- `schema.sql` - SQLite database schema
- `debug.py` - Debug utility for table inspection

## Requirements

- Python 3.10+
- pdfplumber (automatically installed via uv)

## Example Results

From the sample PDF:
- **78 employees** extracted
- **421 attendance records** parsed
- **Attendance breakdown:**
  - Half Day (HD): 229 records
  - Absent (A): 76 records
  - Early/Late (E): 67 records
  - Less Hours (LH): 49 records

## Integration with Other Databases

The JSON output can be easily imported into other databases:

### PostgreSQL

```python
import psycopg2
import json

with open('data_db_ready.json') as f:
    data = json.load(f)

conn = psycopg2.connect("dbname=attendance user=postgres")
cur = conn.cursor()

for emp in data['employees']:
    cur.execute(
        "INSERT INTO employees (employee_id, employee_name, branch, department) VALUES (%s, %s, %s, %s)",
        (emp['employee_id'], emp['employee_name'], emp['branch'], emp['department'])
    )
```

### MySQL

```python
import mysql.connector
import json

with open('data_db_ready.json') as f:
    data = json.load(f)

conn = mysql.connector.connect(host='localhost', database='attendance', user='root')
cur = conn.cursor()

for emp in data['employees']:
    cur.execute(
        "INSERT INTO employees (employee_id, employee_name, branch, department) VALUES (%s, %s, %s, %s)",
        (emp['employee_id'], emp['employee_name'], emp['branch'], emp['department'])
    )
```

### MongoDB

```python
from pymongo import MongoClient
import json

with open('data_db_ready.json') as f:
    data = json.load(f)

client = MongoClient('mongodb://localhost:27017/')
db = client['attendance']

db.employees.insert_many(data['employees'])
db.attendance.insert_many(data['attendance'])
```

## License

MIT
