# Marchés Publics — Collecte des Appels d'Offres

Scraper et pipeline de traitement pour les appels d'offres (AO) publiés sur
[marchespublics.gov.ma](https://www.marchespublics.gov.ma), le portail
marocain des marchés publics.

Le projet couvre uniquement la section **Appels d'Offres** du portail (pas
les Bons de Commande / avis d'achat).

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Pipeline

Les scripts se lancent dans cet ordre, chacun consommant la sortie du
précédent.

### 1. Collecte du listing — `main_ao.py`

Récupère 500 AO par année (2024, 2025, 2026) via le moteur de recherche du
portail, et écrit `data/ao.csv` (une ligne par consultation : référence,
objet, acheteur, catégorie, dates, lieu d'exécution, etc.).

```bash
python3 main_ao.py
```

### 2. Collecte personnalisée par période — `main_ao_custom.py`

Récupère **tous** les AO publiés entre deux dates données (pas de plafond),
sans passer par l'échantillonnage par année du script précédent.

```bash
python3 main_ao_custom.py 2025-01-01 2025-01-15
```

Arguments : `start_date` et `end_date`, obligatoires, au format ISO
(`YYYY-MM-DD`). Écrit `data/custom/from_<start>_to_<end>.csv`.

### 3. Enrichissement par lot — `main_ao_lots.py`

Pour chaque consultation de `data/ao.csv`, récupère le détail des lots
(catégorie, description, **montant estimatif**, caution provisoire,
qualifications, agréments, réservation PME) et écrit `data/ao_lots.csv`.
Fonctionne en parallèle (10 workers par défaut).

```bash
python3 main_ao_lots.py
```

### 4. Nettoyage et structuration — `transform_ao.py`

Lit `data/ao.csv` et `data/ao_lots.csv`, nettoie les types (dates au format
ISO, montants convertis en nombres, booléens, valeurs vides normalisées) et
écrit :

- `data/marches.db` — base SQLite avec les tables `marches` et `lots`
- `data/marches_clean.csv`, `data/lots_clean.csv` — mêmes données en CSV
- `data/marches_<année>.csv`, `data/lots_<année>.csv` — un jeu de fichiers
  par année (2024, 2025, 2026)

```bash
python3 transform_ao.py
```

### 5. Indicateurs (KPIs) — `kpis_ao.py`

Calcule et affiche les indicateurs clés (budget total, répartition par
catégorie, top acheteurs, répartition géographique, délais de réponse,
structure des lots, réservation PME, etc.) à partir des fichiers nettoyés.

```bash
python3 kpis_ao.py
```

## Structure des données

| Fichier | Contenu |
|---|---|
| `data/ao.csv` | Listing brut, une ligne par consultation |
| `data/ao_lots.csv` | Détail brut, une ligne par lot |
| `data/marches_clean.csv` / `data/lots_clean.csv` | Versions nettoyées et typées |
| `data/marches.db` | Mêmes données, tables SQL (`marches`, `lots`) |
| `data/custom/*.csv` | Extractions ponctuelles par période personnalisée |

## Documentation complémentaire

- [`conception_solution.md`](conception_solution.md) — architecture de la
  solution et lien avec l'entrepôt de données (ETL)
- [`presentation_kpis.md`](presentation_kpis.md) — indicateurs calculés sur
  l'échantillon collecté
- [`problems.txt`](problems.txt) — limites et incohérences constatées dans
  les données du portail
