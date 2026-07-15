import re
import sqlite3

import pandas as pd

DB_PATH = "data/marches.db"

AMOUNT_RE = re.compile(r"[^0-9,.\s]")


def parse_amount(value):
    if pd.isna(value):
        return None

    text = str(value).replace("\xa0", " ")
    text = AMOUNT_RE.sub("", text)
    text = text.replace(" ", "")

    if not text:
        return None

    # decimal separator is a comma; "." (when present) is only ever
    # a thousands separator (e.g. "35.409.600,00" vs "2 151 480,00")
    if "," in text:
        text = text.replace(".", "").replace(",", ".")

    try:
        return float(text)
    except ValueError:
        return None


def parse_bool(value):
    if pd.isna(value):
        return None
    return {"Oui": True, "Non": False}.get(str(value).strip())


def blank_dash_to_na(series):
    return series.replace("-", pd.NA)


# --- Marches (one row per consultation) ---------------------------------

ao = pd.read_csv("data/ao.csv", dtype={"ref_consultation": str})

ao["date_publication"] = pd.to_datetime(ao["date_publication"], format="%d/%m/%Y", errors="coerce")
ao["date_limite"] = pd.to_datetime(ao["date_limite"], format="%d/%m/%Y %H:%M", errors="coerce")

ao["statut"] = ao["statut"].fillna("")
ao["est_annule"] = ao["statut"].str.contains("Annulé")
ao["resultat_definitif"] = ao["statut"].str.contains("Résultat définitif")
ao["statut"] = blank_dash_to_na(ao["statut"].replace("", pd.NA))

for col in ("objet", "acheteur", "lieu_execution"):
    ao[col] = ao[col].str.strip()

# --- Lots (one row per lot) ----------------------------------------------

lots = pd.read_csv("data/ao_lots.csv", dtype={"ref_consultation": str, "lot_numero": str})

lots["estimation_ttc"] = lots["estimation_ttc"].apply(parse_amount)
lots["caution_provisoire"] = lots["caution_provisoire"].apply(parse_amount)
lots["variante"] = lots["variante"].apply(parse_bool)
lots["reserve_pme"] = lots["reserve_pme"].apply(parse_bool)
lots["lot_numero"] = pd.to_numeric(lots["lot_numero"], errors="coerce").astype("Int64")

for col in ("lot_intitule", "description", "qualifications", "agrements"):
    lots[col] = blank_dash_to_na(lots[col])

# lots.reference duplicates marches.reference (same consultation) - dropped to avoid redundancy
lots = lots.drop(columns=["reference"])

# --- Derived aggregates back onto marches --------------------------------

lot_stats = lots.groupby("ref_consultation").agg(
    nombre_lots=("lot_numero", "count"),
    estimation_totale_ttc=("estimation_ttc", "sum"),
)

ao = ao.merge(lot_stats, on="ref_consultation", how="left")
ao["nombre_lots"] = ao["nombre_lots"].fillna(0).astype(int)

# --- Persist to SQLite and CSV --------------------------------------------

conn = sqlite3.connect(DB_PATH)
ao.to_sql("marches", conn, if_exists="replace", index=False)
lots.to_sql("lots", conn, if_exists="replace", index=False)
conn.close()

ao.to_csv("data/marches_clean.csv", index=False)
lots.to_csv("data/lots_clean.csv", index=False)

print(f"marches: {len(ao)} rows")
print(f"lots: {len(lots)} rows")
print(f"written to {DB_PATH}, data/marches_clean.csv, data/lots_clean.csv")

# --- Per-year CSV exports --------------------------------------------------

for year in (2024, 2025, 2026):
    year_ao = ao[ao["date_publication"].dt.year == year]
    year_lots = lots[lots["ref_consultation"].isin(year_ao["ref_consultation"])]

    year_ao.to_csv(f"data/marches_{year}.csv", index=False)
    year_lots.to_csv(f"data/lots_{year}.csv", index=False)

    print(f"{year}: {len(year_ao)} marches, {len(year_lots)} lots")
