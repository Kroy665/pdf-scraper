import pdfplumber
import sys
import json
from pathlib import Path
from datetime import datetime
import re


def parse_attendance_table(table, branch="", department=""):
    """
    Parse attendance table and extract structured records.

    Args:
        table: List of table rows
        branch: Branch name
        department: Department name

    Returns:
        List of attendance records
    """
    attendance_records = []
    current_employee = {}

    def safe_str(val):
        """Safely convert value to string, handling None."""
        return val.strip() if val and isinstance(val, str) else ""

    i = 0
    while i < len(table):
        row = table[i]

        if not row or len(row) < 9:
            i += 1
            continue

        emp_id = safe_str(row[0])
        emp_name = safe_str(row[1])
        attn_date = safe_str(row[2])
        in_time = safe_str(row[3])
        out_time = safe_str(row[4])
        total_hrs = safe_str(row[5])
        break_time = safe_str(row[6])
        os_hrs = safe_str(row[7])
        status = safe_str(row[8])

        # Check if this is branch info
        if emp_id and "Branch" in emp_id:
            branch = emp_id.replace("Branch :", "").strip()
            i += 1
            continue

        # Check if this is department info
        if emp_id and "Department" in emp_id:
            department = emp_id.replace("Department :", "").strip()
            i += 1
            continue

        # Check if this is a new employee row (has employee ID like DS2001, E6001, etc. and a name)
        # Employee IDs typically start with letters followed by numbers
        if emp_id and emp_name and (emp_id.startswith("DS") or emp_id.startswith("E6")):
            current_employee = {
                "employee_id": emp_id,
                "employee_name": emp_name,
                "branch": branch,
                "department": department
            }
            i += 1
            continue

        # Skip header rows
        if emp_id == "Emp ID" or (emp_id and "W =" in emp_id):
            i += 1
            continue

        # Process attendance data - could be a DAY row or a standalone date row
        if attn_date and current_employee:
            shift_timing = ""

            # If this row starts with "DAY", it has shift timing
            if emp_id == "DAY":
                shift_timing = emp_name

            # Check if in_time or out_time are in the next row
            if i + 1 < len(table):
                next_row = table[i + 1]
                if next_row and len(next_row) > 4:
                    # Check for in_time
                    if not in_time:
                        potential_in_time = safe_str(next_row[3])
                        if potential_in_time and ":" in potential_in_time:
                            in_time = potential_in_time

                    # Check for out_time
                    if not out_time:
                        potential_out_time = safe_str(next_row[4])
                        if potential_out_time and ":" in potential_out_time:
                            out_time = potential_out_time

            # Create attendance record
            record = {
                "employee_id": current_employee.get("employee_id", ""),
                "employee_name": current_employee.get("employee_name", ""),
                "branch": current_employee.get("branch", branch),
                "department": current_employee.get("department", department),
                "attendance_date": attn_date,
                "in_time": in_time,
                "out_time": out_time,
                "total_hours": total_hrs,
                "break_time": break_time,
                "overtime_hours": os_hrs,
                "status": status,
                "shift_timing": shift_timing
            }

            attendance_records.append(record)

        i += 1

    return attendance_records


def scrape_pdf(pdf_path):
    """
    Scrape attendance data from PDF and output structured JSON for database.

    Args:
        pdf_path: Path to the PDF file
    """
    print(f"Opening PDF: {pdf_path}")
    print("=" * 80)

    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"Total pages: {len(pdf.pages)}\n")

            all_attendance_records = []
            current_branch = ""
            current_department = ""

            for page_num, page in enumerate(pdf.pages, start=1):
                print(f"Processing Page {page_num}/{len(pdf.pages)}...", end=" ")

                # Extract text to find branch/department info
                text = page.extract_text() or ""

                # Try to extract branch from text
                branch_match = re.search(r'Branch\s*:\s*([^\n]+)', text)
                if branch_match:
                    current_branch = branch_match.group(1).strip()

                # Try to extract department from text
                dept_match = re.search(r'Department\s*:\s*([^\n]+)', text)
                if dept_match:
                    current_department = dept_match.group(1).strip()

                # Extract tables
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        records = parse_attendance_table(table, current_branch, current_department)
                        all_attendance_records.extend(records)
                        print(f"Extracted {len(records)} records", end=" ")

                print()

            # Create structured output
            output_data = {
                "metadata": {
                    "source_file": str(pdf_path),
                    "total_pages": len(pdf.pages),
                    "extraction_date": datetime.now().isoformat(),
                    "total_records": len(all_attendance_records)
                },
                "employees": [],
                "attendance_records": all_attendance_records
            }

            # Extract unique employees
            unique_employees = {}
            for record in all_attendance_records:
                emp_id = record["employee_id"]
                if emp_id and emp_id not in unique_employees:
                    unique_employees[emp_id] = {
                        "employee_id": emp_id,
                        "employee_name": record["employee_name"],
                        "branch": record["branch"],
                        "department": record["department"]
                    }

            output_data["employees"] = list(unique_employees.values())

            # Summary
            print(f"\n{'='*80}")
            print("SUMMARY")
            print(f"{'='*80}")
            print(f"Total pages processed: {len(pdf.pages)}")
            print(f"Total employees found: {len(output_data['employees'])}")
            print(f"Total attendance records: {len(all_attendance_records)}")

            # Save to JSON file
            output_file = Path(pdf_path).stem + "_structured.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)

            print(f"\nStructured data saved to: {output_file}")

            # Also create a simplified database-ready format
            db_format = {
                "employees": output_data["employees"],
                "attendance": all_attendance_records
            }

            db_output_file = Path(pdf_path).stem + "_db_ready.json"
            with open(db_output_file, "w", encoding="utf-8") as f:
                json.dump(db_format, f, indent=2, ensure_ascii=False)

            print(f"Database-ready format saved to: {db_output_file}")

            return True

    except FileNotFoundError:
        print(f"Error: PDF file not found at {pdf_path}")
        return False
    except Exception as e:
        print(f"Error processing PDF: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    # Default PDF path (relative to script location)
    default_pdf = Path(__file__).parent.parent / "D.EL.ED merged.pdf"

    # Check if PDF path is provided as argument
    if len(sys.argv) > 1:
        pdf_path = Path(sys.argv[1])
    else:
        pdf_path = default_pdf

    if not pdf_path.exists():
        print(f"Error: PDF file not found at {pdf_path}")
        print(f"\nUsage: python main.py [path_to_pdf]")
        print(f"Default: {default_pdf}")
        sys.exit(1)

    success = scrape_pdf(pdf_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
