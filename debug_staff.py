import pdfplumber
import json

pdf_path = '/Users/koushikroy/personal/pdf_scrape/D.El.Ed STAFF ATTENDANCE 11.05.2026 TO 16.05.2026.pdf'

with pdfplumber.open(pdf_path) as pdf:
    print(f"Total pages: {len(pdf.pages)}\n")

    for page_num in range(min(2, len(pdf.pages))):
        page = pdf.pages[page_num]
        print(f"\n{'='*80}")
        print(f"PAGE {page_num + 1}")
        print(f"{'='*80}")

        # Get text
        text = page.extract_text()
        print("\nText preview (first 800 chars):")
        print(text[:800] if text else "No text")

        # Get tables
        tables = page.extract_tables()
        if tables:
            print(f"\n\nFound {len(tables)} table(s)")
            for table_idx, table in enumerate(tables):
                print(f"\nTable {table_idx + 1} - Total rows: {len(table)}")
                print("\nFirst 25 rows:")
                for i, row in enumerate(table[:25]):
                    print(f"{i}: {row}")
        else:
            print("\nNo tables found")
