import csv
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from fetch import fetch
from parser import extract_ao_lots, extract_ao_nbr_lots, extract_ao_single_estimation
from constants import AO_LOTS_URL

WORKERS = 10

FIELDNAMES = [
    "ref_consultation",
    "org_acronyme",
    "reference",
    "lot_numero",
    "lot_intitule",
    "categorie",
    "description",
    "estimation_ttc",
    "caution_provisoire",
    "qualifications",
    "agrements",
    "variante",
    "reserve_pme",
]


def fetch_lots(consultation):
    ref_consultation = consultation["ref_consultation"]
    org_acronyme = consultation["org_acronyme"]

    detail_html = fetch(consultation["url"])
    nbr_lots = extract_ao_nbr_lots(detail_html)

    if nbr_lots and nbr_lots > 1:
        lots_url = AO_LOTS_URL.format(ref_consultation=ref_consultation, org_acronyme=org_acronyme)
        lots_html = fetch(lots_url)
        lots = extract_ao_lots(lots_html)
    else:
        lots = [extract_ao_single_estimation(detail_html)]
        if lots[0]["categorie"] is None:
            lots[0]["categorie"] = consultation["categorie"]

    for lot in lots:
        lot["ref_consultation"] = ref_consultation
        lot["org_acronyme"] = org_acronyme
        lot["reference"] = consultation["reference"]

    return lots


with open("data/ao.csv", encoding="utf8", newline="") as f:
    consultations = list(csv.DictReader(f))

start_time = time.time()
all_lots = []
done = 0

with ThreadPoolExecutor(max_workers=WORKERS) as executor:
    futures = {executor.submit(fetch_lots, c): c for c in consultations}

    for future in as_completed(futures):
        consultation = futures[future]
        done += 1
        lots = future.result()
        all_lots.extend(lots)
        print(f"[{done}/{len(consultations)}] {consultation['ref_consultation']} -> {len(lots)} lot(s)")

elapsed = time.time() - start_time

print()
print("Total lots:", len(all_lots))
print(f"Elapsed: {elapsed:.1f}s")

all_lots.sort(key=lambda lot: (lot["ref_consultation"], lot["lot_numero"]))

with open("data/ao_lots.csv", "w", encoding="utf8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    writer.writeheader()
    writer.writerows(all_lots)
