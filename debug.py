import pdfplumber
import json

with pdfplumber.open('/Users/koushikroy/personal/pdf_scrape/D.EL.ED merged.pdf') as pdf:
    page = pdf.pages[0]
    tables = page.extract_tables()

    if tables:
        table = tables[0]
        print(f"Total rows: {len(table)}")
        print("\nFirst 30 rows:")
        for i, row in enumerate(table[:30]):
            # Check what type each element is
            print(f"{i}: len={len(row)} | {row}")
