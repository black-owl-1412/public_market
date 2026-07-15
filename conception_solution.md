# Conception de la solution — Module de collecte des Appels d'Offres

## 1. Données extraites par consultation

Pour chaque appel d'offres, les champs suivants sont collectés :

| Champ | Description |
|---|---|
| Référence | Numéro de référence de la consultation |
| Type de procédure | Ex. Appel d'offres ouvert, Concours architectural |
| Catégorie | Travaux, Fournitures, ou Services |
| Objet | Description complète de la prestation |
| Acheteur public | Entité publique à l'origine de la consultation |
| Lieu d'exécution | Ville ou région concernée |
| Date de publication | Date de mise en ligne de l'avis |
| Date limite | Date et heure limites de remise des plis |
| Statut | Annulé, Résultat définitif, etc. lorsque applicable |
| Lien | URL de la fiche complète sur le portail |

### Exemple

> **Référence** : 15/2026/DPBM — **Catégorie** : Services
> **Objet** : Le gardiennage et la sécurité des tribunaux de première instance de Fkih Ben Salah, Souk Sebt, Kasbat Tadla...
> **Acheteur** : Direction Provinciale de la Justice Beni Mellal — **Lieu** : Beni Mellal
> **Date limite** : 13/08/2026 11:00

## 2. Données extraites par lot

Chaque consultation peut être découpée en un ou plusieurs lots. Pour chaque lot, les informations suivantes sont également collectées :

| Champ | Description |
|---|---|
| Intitulé du lot | Désignation du lot |
| Catégorie / description | Détail de l'objet du lot |
| **Montant estimatif (Dhs TTC)** | Estimation budgétaire de l'acheteur pour ce lot |
| Caution provisoire | Montant de garantie exigé pour soumissionner |
| Qualifications / agréments | Exigences imposées aux soumissionnaires |
| Réservé PME | Indique si le lot est réservé aux petites et moyennes entreprises |

### Exemple

| Lot | Estimation (Dhs TTC) | Caution provisoire |
|---|---|---|
| Réfrigérateur et cuisinière | 2 151 480,00 | 32 000,00 DH |
| Matériels et ustensiles de cuisine | 1 090 605,00 | 17 000,00 DH |

Le montant estimatif, en particulier, constitue une donnée à forte valeur ajoutée : il permet de comparer le budget prévisionnel de l'administration à un futur montant d'attribution.

## 3. Résultats de la démonstration

Un test a été mené sur un échantillon de 1 500 appels d'offres, répartis à parts égales entre 2024, 2025 et 2026 (500 par année).

| Résultat | Volume |
|---|---|
| Consultations collectées | 1 500 |
| Lots correspondants collectés | 2 659 |
| Couverture du montant estimatif | 100 % des consultations |
| Temps total de traitement | environ 11 minutes |

Ces 1 500 consultations couvrent l'ensemble des catégories (Travaux, Fournitures, Services) et plusieurs dizaines d'acheteurs publics différents.

## 4. Volume global disponible

Le portail recense environ **99 900 appels d'offres** publiés depuis 2024, ce qui correspond en pratique à l'historique complet disponible sur cette section du site. Sur la base du temps mesuré lors de la démonstration, la collecte de l'ensemble de ce volume est estimée à une dizaine d'heures de traitement.

## 5. Limites identifiées

- Le résultat d'attribution des appels d'offres (entreprise gagnante, montant final) n'est pas publié de façon structurée par le portail ; seule l'estimation ex-ante de l'acheteur est disponible de façon fiable.
- Le statut (annulé, résultat définitif) n'est renseigné que pour une minorité de consultations, la majorité de l'échantillon actuel étant encore en cours.

## 6. Rattachement à l'entrepôt de données (ETL)

La collecte réalisée correspond à la phase **Extract** de la chaîne ETL prévue par le projet. Les données sont aujourd'hui produites au format CSV, une forme intermédiaire qui reste à transformer puis charger dans l'entrepôt de données.

Les champs déjà collectés correspondent directement aux axes d'analyse prévus dans le modèle en étoile :

| Table cible | Champs déjà disponibles |
|---|---|
| Dim_Date | Date de publication, date limite |
| Dim_Organisme | Acheteur public |
| Dim_Categorie | Catégorie (Travaux / Fournitures / Services) |
| Dim_Region | Lieu d'exécution |
| Fact_Marches | Référence, montant estimatif, caution provisoire |

Le travail de **Transform** restant à effectuer avant chargement porte essentiellement sur :

- la conversion des montants du format texte français (« 2 151 480,00 ») vers un type numérique ;
- la séparation de la date et de l'heure pour les champs comme la date limite ;
- la normalisation des noms d'acheteurs et de lieux, afin qu'un même organisme ou une même ville soit toujours rattaché à la même clé de dimension ;
- la déduplication des consultations déjà chargées lors d'une exécution précédente.

Le format des données collectées ayant été pensé dès le départ pour correspondre à ce modèle, le travail de transformation restant est limité et ne remet pas en cause la structure choisie.
