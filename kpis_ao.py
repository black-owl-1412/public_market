import pandas as pd

pd.set_option("display.width", 120)
pd.set_option("display.max_colwidth", 60)

marches = pd.read_csv("data/marches_clean.csv", parse_dates=["date_publication", "date_limite"])
lots = pd.read_csv("data/lots_clean.csv")

print("=" * 80)
print("1. VOLUME & BUDGET GLOBAL")
print("=" * 80)
print("Nombre de marches:", len(marches))
print("Nombre de lots:", len(lots))
print("Budget total estime (somme lots):", lots["estimation_ttc"].sum())
print("Budget median par marche:", marches["estimation_totale_ttc"].median())
print("Budget moyen par marche:", marches["estimation_totale_ttc"].mean())
print("Budget median par lot:", lots["estimation_ttc"].median())

print()
print("=" * 80)
print("2. CONCENTRATION BUDGETAIRE (top 5 marches)")
print("=" * 80)
top5 = marches.nlargest(5, "estimation_totale_ttc")
print(top5[["ref_consultation", "acheteur", "categorie", "lieu_execution", "estimation_totale_ttc"]])
total = marches["estimation_totale_ttc"].sum()
print(f"Part du budget total pour les 5 plus gros marches: {top5['estimation_totale_ttc'].sum() / total * 100:.1f}%")

print()
print("=" * 80)
print("3. REPARTITION PAR CATEGORIE")
print("=" * 80)
cat = marches.groupby("categorie").agg(
    nb=("ref_consultation", "count"),
    budget_total=("estimation_totale_ttc", "sum"),
    budget_median=("estimation_totale_ttc", "median"),
)
cat["part_budget_%"] = (cat["budget_total"] / cat["budget_total"].sum() * 100).round(1)
print(cat)

print()
print("=" * 80)
print("4. TOP ACHETEURS")
print("=" * 80)
print("--- par montant ---")
print(marches.groupby("acheteur")["estimation_totale_ttc"].sum().sort_values(ascending=False).head(10))
print("--- par nombre ---")
print(marches.groupby("acheteur")["ref_consultation"].count().sort_values(ascending=False).head(10))

print()
print("=" * 80)
print("5. REPARTITION GEOGRAPHIQUE")
print("=" * 80)
geo = marches.groupby("lieu_execution").agg(
    nb=("ref_consultation", "count"),
    budget_total=("estimation_totale_ttc", "sum"),
).sort_values("budget_total", ascending=False)
print(geo.head(10))

print()
print("=" * 80)
print("6. DELAIS (publication -> limite)")
print("=" * 80)
marches["delai_jours"] = (marches["date_limite"] - marches["date_publication"]).dt.days
print("Delai moyen (jours):", marches["delai_jours"].mean())
print("Delai median (jours):", marches["delai_jours"].median())
print("--- par categorie ---")
print(marches.groupby("categorie")["delai_jours"].mean())
print("--- par type de procedure ---")
print(marches.groupby("type_procedure")["delai_jours"].mean())

print()
print("=" * 80)
print("7. STRUCTURE DES LOTS")
print("=" * 80)
print(marches["nombre_lots"].value_counts().sort_index())
print(f"Part mono-lot: {(marches['nombre_lots'] <= 1).mean() * 100:.1f}%")

print()
print("=" * 80)
print("8. CAUTION PROVISOIRE / ESTIMATION")
print("=" * 80)
lots_valid = lots[lots["estimation_ttc"] > 0]
ratio = lots_valid["caution_provisoire"] / lots_valid["estimation_ttc"] * 100
print("Ratio moyen (%):", ratio.mean())
print("Ratio median (%):", ratio.median())

print()
print("=" * 80)
print("9. RESERVE PME")
print("=" * 80)
print(lots["reserve_pme"].value_counts())
pme_montant = lots.groupby("reserve_pme")["estimation_ttc"].sum()
print(f"Part des lots reserves PME (nombre): {lots['reserve_pme'].mean() * 100:.1f}%")
print(f"Part du budget reserve PME: {pme_montant[True] / pme_montant.sum() * 100:.1f}%")

print()
print("=" * 80)
print("10. ANNULATIONS ET RESULTATS DEFINITIFS")
print("=" * 80)
print("Taux annulation (%):", marches["est_annule"].mean() * 100)
print("Taux resultat_definitif (%):", marches["resultat_definitif"].mean() * 100)

print()
print("=" * 80)
print("11. TYPE DE PROCEDURE")
print("=" * 80)
print(marches["type_procedure"].value_counts())
print((marches["type_procedure"].value_counts(normalize=True) * 100).round(1))
