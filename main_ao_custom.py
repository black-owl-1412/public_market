import argparse
import csv
import os
import time
from datetime import datetime

from fetch_ao import fetch_ao_search_range
from parser import extract_ao_records

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

OUTPUT_DIR = "data/custom"


def parse_iso_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid ISO date (expected YYYY-MM-DD)")


parser = argparse.ArgumentParser(description="Scrape AO published between two dates (date de mise en ligne).")
parser.add_argument("start_date", type=parse_iso_date, help="start date, ISO format YYYY-MM-DD")
parser.add_argument("end_date", type=parse_iso_date, help="end date, ISO format YYYY-MM-DD")
args = parser.parse_args()

if args.start_date > args.end_date:
    parser.error("start_date must not be after end_date")

date_start = args.start_date.strftime("%d/%m/%Y")
date_end = args.end_date.strftime("%d/%m/%Y")

start_time = time.time()
records_by_ref = {}

for page_num, html in enumerate(fetch_ao_search_range(date_start, date_end), start=1):

    print(f"Downloading page {page_num}")

    records = extract_ao_records(html)

    for record in records:
        records_by_ref[record["ref_consultation"]] = record

elapsed = time.time() - start_time

print()
print("Total unique consultations:", len(records_by_ref))
print(f"Elapsed: {elapsed:.1f}s")

sorted_records = sorted(records_by_ref.values(), key=lambda r: r["ref_consultation"])

os.makedirs(OUTPUT_DIR, exist_ok=True)

filename = f"from_{args.start_date.date().isoformat()}_to_{args.end_date.date().isoformat()}.csv"
output_path = os.path.join(OUTPUT_DIR, filename)

with open(output_path, "w", encoding="utf8", newline="") as f:

    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    writer.writeheader()
    writer.writerows(sorted_records)

print(f"Written to {output_path}")
