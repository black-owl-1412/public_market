import csv
import time

from fetch_ao import fetch_ao_search_year
from parser import extract_ao_records

YEARS = [2024, 2025, 2026]
MAX_RECORDS_PER_YEAR = 500

FIELDNAMES = [
    "ref_consultation",
    "org_acronyme",
    "reference",
    "type_procedure",
    "type_procedure_abbrev",
    "categorie",
    "objet",
    "acheteur",
    "lieu_execution",
    "date_publication",
    "date_limite",
    "statut",
    "url",
]

start_time = time.time()
records_by_ref = {}

for year in YEARS:
    for page_num, html in enumerate(fetch_ao_search_year(year, max_records=MAX_RECORDS_PER_YEAR), start=1):

        print(f"[{year}] Downloading page {page_num}")

        records = extract_ao_records(html)

        for record in records:
            records_by_ref[record["ref_consultation"]] = record

elapsed = time.time() - start_time

print()
print("Total unique consultations:", len(records_by_ref))
print(f"Elapsed: {elapsed:.1f}s")

sorted_records = sorted(records_by_ref.values(), key=lambda r: r["ref_consultation"])

with open("data/ao.csv", "w", encoding="utf8", newline="") as f:

    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    writer.writeheader()
    writer.writerows(sorted_records)
