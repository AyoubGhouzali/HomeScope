# DVF multi-row legal transaction audit

> This is an inspection artifact, not a cleaned dataset. No price-per-m²
> value is calculated here.



## Source and schema

- Input: `data/raw/dvf_63_2025.csv.gz`
- SHA-256: `15618a54d7d739cdfd5a55f89bbbd4828674de14eaed32b06ab3c8109dd65241`
- Raw rows: **48,208**
- Distinct source `id_mutation` groups: **16,723**
- Legal transaction units (`id_mutation`, `numero_disposition`): **16,841**
- Source IDs containing multiple dispositions: **114**
- Legal units with multiple rows: **10,443**
- Rows belonging to multi-row legal units: **41,810**
- Required retained columns present: **34/34**
- Missing required columns: none
- Additional source columns retained by the raw file: `ancien_code_commune`, `ancien_nom_commune`, `ancien_id_parcelle`, `numero_volume`, `code_nature_culture_speciale`, `nature_culture_speciale`

The audit reads every source column and does not rewrite or reduce the raw file. Following the DGFiP notice, the operational legal transaction unit is the pair `(id_mutation, numero_disposition)`, because each disposition is a legal analysis unit carrying a declared value. The geolocated `id_mutation` remains parent metadata.

## Group structure

| Rows per legal unit | Legal transaction units |
| --- | --- |
| 1 | 6398 |
| 2 | 4060 |
| 3 | 2885 |
| 4 | 1382 |
| 5–9 | 1621 |
| 10–24 | 408 |
| 25+ | 87 |

A legal unit is marked unusually large when it has more than **17** rows (the greater of 10 and the rounded-up 99th percentile).

| Condition | Legal transaction units | Share |
| --- | --- | --- |
| Value repeated across rows | 10391 | 61.7% |
| Conflicting non-null values | 0 | 0.0% |
| Missing transaction value | 82 | 0.5% |
| Repeated residential signature | 1147 | 6.8% |
| Multiple primary dwelling signatures | 669 | 4.0% |
| Mixed house and apartment | 41 | 0.2% |
| Residential and commercial premises | 303 | 1.8% |
| Parent id_mutation contains multiple dispositions | 232 | 1.4% |
| Multiple parcels | 5366 | 31.9% |
| Multiple addresses | 4714 | 28.0% |
| Multiple communes | 330 | 2.0% |
| Repeated land segment | 2582 | 15.3% |
| Land only | 5880 | 34.9% |
| Unusually large group | 159 | 0.9% |

## Initial observations

- `valeur_fonciere` is commonly copied onto several rows in one disposition. The audit exposes one `transaction_value` only when the legal unit has exactly one distinct non-null value; it never sums row values.
- A source `id_mutation` can contain several dispositions. Those dispositions are audited independently and are never merged merely because their date and value match.
- A residential row may be expanded across land-use or lot rows. A residential signature therefore includes parcel, full address, local type, built surface, rooms, and all five lot number/surface pairs.
- Repeated signatures remain explicitly flagged. They are evidence of row expansion, but the flattened extract alone cannot prove that two otherwise identical units are the same property.
- Dependencies may accompany a dwelling without representing another dwelling. Commercial premises and multiple distinct dwelling signatures make a disposition unsuitable for a simple residential €/m² calculation.
- Land segments can also repeat once per local. Future terrain totals must first deduplicate parcel, culture code/name, and terrain surface combinations.

## Cleaning decision matrix

| Situation | Provisional rule |
| --- | --- |
| Transaction count | Count distinct (id_mutation, numero_disposition) pairs, never raw rows or id_mutation alone. |
| One distinct non-null transaction value | Use that value once for the disposition; never sum repeated row values. |
| Parent ID with several dispositions | Audit and count each disposition separately; retain id_mutation only as source grouping metadata. |
| Conflicting or missing transaction values | Quarantine from price analysis pending review. |
| One dwelling plus dependencies | Keep as a candidate; dependencies do not contribute built surface. |
| Repeated dwelling signature | Do not sum surfaces; inspect or conservatively exclude until identity is resolved. |
| Multiple dwellings or mixed house/apartment | Exclude from the simple comparable-sale dataset or model separately. |
| Residential plus commercial premises | Exclude from residential €/m² calculations. |
| Terrain surface | Deduplicate land signatures before aggregation; never use terrain in the built €/m² denominator. |
| price_per_m2 | Do not calculate until the mutation rules are reviewed and accepted. |

## Representative legal transaction units

Samples are selected deterministically by group size, `id_mutation`, and `numero_disposition`. Every raw row and every required retained field is shown for each selected legal unit.

### Apartment with dependencies

| id_mutation | numero_disposition | row_count | parent_disposition_count | parcel_count | commune_count | address_count | coordinate_count | distinct_value_count | transaction_value | house_row_count | apartment_row_count | dependency_row_count | commercial_row_count | distinct_residential_signature_count | terrain_row_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-804984 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 56900 | 0 | 1 | 1 | 0 | 1 | 0 |
| 2025-804985 | 1 | 2 | 1 | 1 | 1 | 2 | 1 | 1 | 70000 | 0 | 1 | 1 | 0 | 1 | 0 |
| 2025-804989 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 94000 | 0 | 1 | 1 | 0 | 1 | 0 |

#### `2025-804984` / disposition `1` — raw rows

| id_mutation | date_mutation | nature_mutation | valeur_fonciere | code_departement | code_commune | nom_commune | code_postal | adresse_numero | adresse_suffixe | adresse_nom_voie | adresse_code_voie | longitude | latitude | code_type_local | type_local | surface_reelle_bati | nombre_pieces_principales | surface_terrain | numero_disposition | id_parcelle | nombre_lots | lot1_numero | lot1_surface_carrez | lot2_numero | lot2_surface_carrez | lot3_numero | lot3_surface_carrez | lot4_numero | lot4_surface_carrez | lot5_numero | lot5_surface_carrez | code_nature_culture | nature_culture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-804984 | 2025-01-06 | Vente | 56900 | 63 | 63113 | Clermont-Ferrand | 63000 | 27 |  | RUE RAYNAUD | 3755 | 3.089528 | 45.769765 | 2 | Appartement | 23 | 1 |  | 1 | 63113000HS0266 | 1 | 15 | 22.65 |  |  |  |  |  |  |  |  |  |  |
| 2025-804984 | 2025-01-06 | Vente | 56900 | 63 | 63113 | Clermont-Ferrand | 63000 | 27 |  | RUE RAYNAUD | 3755 | 3.089528 | 45.769765 | 3 | Dépendance |  | 0 |  | 1 | 63113000HS0266 | 1 | 46 |  |  |  |  |  |  |  |  |  |  |  |

#### `2025-804985` / disposition `1` — raw rows

| id_mutation | date_mutation | nature_mutation | valeur_fonciere | code_departement | code_commune | nom_commune | code_postal | adresse_numero | adresse_suffixe | adresse_nom_voie | adresse_code_voie | longitude | latitude | code_type_local | type_local | surface_reelle_bati | nombre_pieces_principales | surface_terrain | numero_disposition | id_parcelle | nombre_lots | lot1_numero | lot1_surface_carrez | lot2_numero | lot2_surface_carrez | lot3_numero | lot3_surface_carrez | lot4_numero | lot4_surface_carrez | lot5_numero | lot5_surface_carrez | code_nature_culture | nature_culture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-804985 | 2025-01-06 | Vente | 70000 | 63 | 63113 | Clermont-Ferrand | 63100 | 5 |  | AV BARBIER DAUBREE | 0370 | 3.091965 | 45.787616 | 2 | Appartement | 31 | 1 |  | 1 | 63113000LR0772 | 1 | 102 | 30.98 |  |  |  |  |  |  |  |  |  |  |
| 2025-804985 | 2025-01-06 | Vente | 70000 | 63 | 63113 | Clermont-Ferrand | 63100 | 16 | B | RUE DU BAS CHAMPFLOUR | 0415 | 3.091965 | 45.787616 | 3 | Dépendance |  | 0 |  | 1 | 63113000LR0772 | 1 | 46 |  |  |  |  |  |  |  |  |  |  |  |

#### `2025-804989` / disposition `1` — raw rows

| id_mutation | date_mutation | nature_mutation | valeur_fonciere | code_departement | code_commune | nom_commune | code_postal | adresse_numero | adresse_suffixe | adresse_nom_voie | adresse_code_voie | longitude | latitude | code_type_local | type_local | surface_reelle_bati | nombre_pieces_principales | surface_terrain | numero_disposition | id_parcelle | nombre_lots | lot1_numero | lot1_surface_carrez | lot2_numero | lot2_surface_carrez | lot3_numero | lot3_surface_carrez | lot4_numero | lot4_surface_carrez | lot5_numero | lot5_surface_carrez | code_nature_culture | nature_culture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-804989 | 2025-01-07 | Vente | 94000 | 63 | 63113 | Clermont-Ferrand | 63000 | 42 |  | AV LEON BLUM | 2635 | 3.0944 | 45.769863 | 3 | Dépendance |  | 0 |  | 1 | 63113000EW0213 | 1 | 149 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-804989 | 2025-01-07 | Vente | 94000 | 63 | 63113 | Clermont-Ferrand | 63000 | 42 |  | AV LEON BLUM | 2635 | 3.0944 | 45.769863 | 2 | Appartement | 29 | 2 |  | 1 | 63113000EW0213 | 1 | 114 | 28.6 |  |  |  |  |  |  |  |  |  |  |

### House repeated across expanded rows

| id_mutation | numero_disposition | row_count | parent_disposition_count | parcel_count | commune_count | address_count | coordinate_count | distinct_value_count | transaction_value | house_row_count | apartment_row_count | dependency_row_count | commercial_row_count | distinct_residential_signature_count | terrain_row_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-805028 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 289000 | 2 | 0 | 0 | 0 | 1 | 2 |
| 2025-805036 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 170000 | 2 | 0 | 0 | 0 | 1 | 2 |
| 2025-805071 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 208000 | 2 | 0 | 0 | 0 | 1 | 2 |

#### `2025-805028` / disposition `1` — raw rows

| id_mutation | date_mutation | nature_mutation | valeur_fonciere | code_departement | code_commune | nom_commune | code_postal | adresse_numero | adresse_suffixe | adresse_nom_voie | adresse_code_voie | longitude | latitude | code_type_local | type_local | surface_reelle_bati | nombre_pieces_principales | surface_terrain | numero_disposition | id_parcelle | nombre_lots | lot1_numero | lot1_surface_carrez | lot2_numero | lot2_surface_carrez | lot3_numero | lot3_surface_carrez | lot4_numero | lot4_surface_carrez | lot5_numero | lot5_surface_carrez | code_nature_culture | nature_culture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-805028 | 2025-01-06 | Vente | 289000 | 63 | 63425 | Tallende | 63450 | 7 |  | ALL DES COTEAUX | 0068 | 3.126862 | 45.674789 | 1 | Maison | 110 | 4 | 499 | 1 | 63425000AA0368 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-805028 | 2025-01-06 | Vente | 289000 | 63 | 63425 | Tallende | 63450 | 7 |  | ALL DES COTEAUX | 0068 | 3.126862 | 45.674789 | 1 | Maison | 110 | 4 | 500 | 1 | 63425000AA0368 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |

#### `2025-805036` / disposition `1` — raw rows

| id_mutation | date_mutation | nature_mutation | valeur_fonciere | code_departement | code_commune | nom_commune | code_postal | adresse_numero | adresse_suffixe | adresse_nom_voie | adresse_code_voie | longitude | latitude | code_type_local | type_local | surface_reelle_bati | nombre_pieces_principales | surface_terrain | numero_disposition | id_parcelle | nombre_lots | lot1_numero | lot1_surface_carrez | lot2_numero | lot2_surface_carrez | lot3_numero | lot3_surface_carrez | lot4_numero | lot4_surface_carrez | lot5_numero | lot5_surface_carrez | code_nature_culture | nature_culture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-805036 | 2025-01-09 | Vente | 170000 | 63 | 63265 | Orléat | 63190 | 4 |  | RUE DES LILAS | 0098 | 3.466299 | 45.871092 | 1 | Maison | 101 | 5 | 885 | 1 | 63265000AT0044 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-805036 | 2025-01-09 | Vente | 170000 | 63 | 63265 | Orléat | 63190 | 4 |  | RUE DES LILAS | 0098 | 3.466299 | 45.871092 | 1 | Maison | 101 | 5 | 800 | 1 | 63265000AT0044 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |

#### `2025-805071` / disposition `1` — raw rows

| id_mutation | date_mutation | nature_mutation | valeur_fonciere | code_departement | code_commune | nom_commune | code_postal | adresse_numero | adresse_suffixe | adresse_nom_voie | adresse_code_voie | longitude | latitude | code_type_local | type_local | surface_reelle_bati | nombre_pieces_principales | surface_terrain | numero_disposition | id_parcelle | nombre_lots | lot1_numero | lot1_surface_carrez | lot2_numero | lot2_surface_carrez | lot3_numero | lot3_surface_carrez | lot4_numero | lot4_surface_carrez | lot5_numero | lot5_surface_carrez | code_nature_culture | nature_culture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-805071 | 2025-01-03 | Vente | 208000 | 63 | 63234 | Montaigut-le-Blanc | 63320 | 10 |  | RUE D EVIAN | 0100 | 3.087226 | 45.586422 | 1 | Maison | 91 | 3 | 400 | 1 | 63234000AE0700 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-805071 | 2025-01-03 | Vente | 208000 | 63 | 63234 | Montaigut-le-Blanc | 63320 | 10 |  | RUE D EVIAN | 0100 | 3.087226 | 45.586422 | 1 | Maison | 91 | 3 | 940 | 1 | 63234000AE0700 | 0 |  |  |  |  |  |  |  |  |  |  | J | jardins |

### Multiple primary dwellings

| id_mutation | numero_disposition | row_count | parent_disposition_count | parcel_count | commune_count | address_count | coordinate_count | distinct_value_count | transaction_value | house_row_count | apartment_row_count | dependency_row_count | commercial_row_count | distinct_residential_signature_count | terrain_row_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-805334 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 75000 | 0 | 2 | 0 | 0 | 2 | 2 |
| 2025-805490 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 79000 | 0 | 2 | 0 | 0 | 2 | 0 |
| 2025-805716 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 128460 | 0 | 2 | 0 | 0 | 2 | 0 |

#### `2025-805334` / disposition `1` — raw rows

| id_mutation | date_mutation | nature_mutation | valeur_fonciere | code_departement | code_commune | nom_commune | code_postal | adresse_numero | adresse_suffixe | adresse_nom_voie | adresse_code_voie | longitude | latitude | code_type_local | type_local | surface_reelle_bati | nombre_pieces_principales | surface_terrain | numero_disposition | id_parcelle | nombre_lots | lot1_numero | lot1_surface_carrez | lot2_numero | lot2_surface_carrez | lot3_numero | lot3_surface_carrez | lot4_numero | lot4_surface_carrez | lot5_numero | lot5_surface_carrez | code_nature_culture | nature_culture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-805334 | 2025-01-21 | Vente | 75000 | 63 | 63014 | Aubière | 63170 | 9 |  | RUE PASCAL | 0760 | 3.110281 | 45.751517 | 2 | Appartement | 27 | 2 | 37 | 1 | 63014000AT0127 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-805334 | 2025-01-21 | Vente | 75000 | 63 | 63014 | Aubière | 63170 | 9 |  | RUE PASCAL | 0760 | 3.110281 | 45.751517 | 2 | Appartement | 27 | 1 | 37 | 1 | 63014000AT0127 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |

#### `2025-805490` / disposition `1` — raw rows

| id_mutation | date_mutation | nature_mutation | valeur_fonciere | code_departement | code_commune | nom_commune | code_postal | adresse_numero | adresse_suffixe | adresse_nom_voie | adresse_code_voie | longitude | latitude | code_type_local | type_local | surface_reelle_bati | nombre_pieces_principales | surface_terrain | numero_disposition | id_parcelle | nombre_lots | lot1_numero | lot1_surface_carrez | lot2_numero | lot2_surface_carrez | lot3_numero | lot3_surface_carrez | lot4_numero | lot4_surface_carrez | lot5_numero | lot5_surface_carrez | code_nature_culture | nature_culture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-805490 | 2025-01-13 | Vente | 79000 | 63 | 63300 | Riom | 63200 | 10 |  | RUE VICTOR BASCH | 1450 | 3.111454 | 45.89439 | 2 | Appartement | 27 | 1 |  | 1 | 63300000BX0020 | 1 | 1 | 27.7 |  |  |  |  |  |  |  |  |  |  |
| 2025-805490 | 2025-01-13 | Vente | 79000 | 63 | 63300 | Riom | 63200 | 10 |  | RUE VICTOR BASCH | 1450 | 3.111454 | 45.89439 | 2 | Appartement | 23 | 1 |  | 1 | 63300000BX0020 | 1 | 2 | 24.2 |  |  |  |  |  |  |  |  |  |  |

#### `2025-805716` / disposition `1` — raw rows

| id_mutation | date_mutation | nature_mutation | valeur_fonciere | code_departement | code_commune | nom_commune | code_postal | adresse_numero | adresse_suffixe | adresse_nom_voie | adresse_code_voie | longitude | latitude | code_type_local | type_local | surface_reelle_bati | nombre_pieces_principales | surface_terrain | numero_disposition | id_parcelle | nombre_lots | lot1_numero | lot1_surface_carrez | lot2_numero | lot2_surface_carrez | lot3_numero | lot3_surface_carrez | lot4_numero | lot4_surface_carrez | lot5_numero | lot5_surface_carrez | code_nature_culture | nature_culture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-805716 | 2025-02-04 | Vente | 128460 | 63 | 63113 | Clermont-Ferrand | 63000 | 8 |  | PL MICHEL DE L HOSPITAL | 2910 | 3.089713 | 45.777044 | 2 | Appartement | 28 | 1 |  | 1 | 63113000IM0162 | 1 | 14 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-805716 | 2025-02-04 | Vente | 128460 | 63 | 63113 | Clermont-Ferrand | 63000 | 8 |  | PL MICHEL DE L HOSPITAL | 2910 | 3.089713 | 45.777044 | 2 | Appartement | 24 | 1 |  | 1 | 63113000IM0162 | 1 | 15 |  |  |  |  |  |  |  |  |  |  |  |

### Mixed house and apartment

| id_mutation | numero_disposition | row_count | parent_disposition_count | parcel_count | commune_count | address_count | coordinate_count | distinct_value_count | transaction_value | house_row_count | apartment_row_count | dependency_row_count | commercial_row_count | distinct_residential_signature_count | terrain_row_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-806620 | 1 | 2 | 1 | 2 | 1 | 2 | 2 | 1 | 256047 | 1 | 1 | 0 | 0 | 2 | 2 |
| 2025-813556 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 188000 | 1 | 1 | 0 | 0 | 2 | 2 |
| 2025-814434 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 220000 | 1 | 1 | 0 | 0 | 2 | 2 |

#### `2025-806620` / disposition `1` — raw rows

| id_mutation | date_mutation | nature_mutation | valeur_fonciere | code_departement | code_commune | nom_commune | code_postal | adresse_numero | adresse_suffixe | adresse_nom_voie | adresse_code_voie | longitude | latitude | code_type_local | type_local | surface_reelle_bati | nombre_pieces_principales | surface_terrain | numero_disposition | id_parcelle | nombre_lots | lot1_numero | lot1_surface_carrez | lot2_numero | lot2_surface_carrez | lot3_numero | lot3_surface_carrez | lot4_numero | lot4_surface_carrez | lot5_numero | lot5_surface_carrez | code_nature_culture | nature_culture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-806620 | 2025-02-25 | Vente | 256047 | 63 | 63124 | Cournon-d'Auvergne | 63800 | 4 | B | RUE ANNET FARNOUX | 0020 | 3.19987 | 45.741583 | 2 | Appartement | 32 | 1 | 106 | 1 | 63124000BT0124 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-806620 | 2025-02-25 | Vente | 256047 | 63 | 63124 | Cournon-d'Auvergne | 63800 | 4 |  | RUE ANNET FARNOUX | 0020 | 3.199738 | 45.741594 | 1 | Maison | 105 | 3 | 48 | 1 | 63124000BT0125 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |

#### `2025-813556` / disposition `1` — raw rows

| id_mutation | date_mutation | nature_mutation | valeur_fonciere | code_departement | code_commune | nom_commune | code_postal | adresse_numero | adresse_suffixe | adresse_nom_voie | adresse_code_voie | longitude | latitude | code_type_local | type_local | surface_reelle_bati | nombre_pieces_principales | surface_terrain | numero_disposition | id_parcelle | nombre_lots | lot1_numero | lot1_surface_carrez | lot2_numero | lot2_surface_carrez | lot3_numero | lot3_surface_carrez | lot4_numero | lot4_surface_carrez | lot5_numero | lot5_surface_carrez | code_nature_culture | nature_culture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-813556 | 2025-07-03 | Vente | 188000 | 63 | 63178 | Issoire | 63500 | 2 |  | RUE DE LA FERRONNERIE | 0710 | 3.24868 | 45.542492 | 1 | Maison | 87 | 4 | 69 | 1 | 63178000AC0179 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-813556 | 2025-07-03 | Vente | 188000 | 63 | 63178 | Issoire | 63500 | 2 |  | RUE DE LA FERRONNERIE | 0710 | 3.24868 | 45.542492 | 2 | Appartement | 37 | 1 | 69 | 1 | 63178000AC0179 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |

#### `2025-814434` / disposition `1` — raw rows

| id_mutation | date_mutation | nature_mutation | valeur_fonciere | code_departement | code_commune | nom_commune | code_postal | adresse_numero | adresse_suffixe | adresse_nom_voie | adresse_code_voie | longitude | latitude | code_type_local | type_local | surface_reelle_bati | nombre_pieces_principales | surface_terrain | numero_disposition | id_parcelle | nombre_lots | lot1_numero | lot1_surface_carrez | lot2_numero | lot2_surface_carrez | lot3_numero | lot3_surface_carrez | lot4_numero | lot4_surface_carrez | lot5_numero | lot5_surface_carrez | code_nature_culture | nature_culture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-814434 | 2025-07-23 | Vente | 220000 | 63 | 63457 | Vic-le-Comte | 63270 | 591 |  | RUE LUCIEN JARRIGE | 0164 | 3.250506 | 45.642542 | 1 | Maison | 110 | 4 | 731 | 1 | 63457000AI0307 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-814434 | 2025-07-23 | Vente | 220000 | 63 | 63457 | Vic-le-Comte | 63270 | 591 |  | RUE LUCIEN JARRIGE | 0164 | 3.250506 | 45.642542 | 2 | Appartement | 42 | 2 | 731 | 1 | 63457000AI0307 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |

### Residential and commercial premises

| id_mutation | numero_disposition | row_count | parent_disposition_count | parcel_count | commune_count | address_count | coordinate_count | distinct_value_count | transaction_value | house_row_count | apartment_row_count | dependency_row_count | commercial_row_count | distinct_residential_signature_count | terrain_row_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-805070 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 100000 | 1 | 0 | 0 | 1 | 1 | 2 |
| 2025-805078 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 289770 | 1 | 0 | 0 | 1 | 1 | 2 |
| 2025-805812 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 90000 | 1 | 0 | 0 | 1 | 1 | 2 |

#### `2025-805070` / disposition `1` — raw rows

| id_mutation | date_mutation | nature_mutation | valeur_fonciere | code_departement | code_commune | nom_commune | code_postal | adresse_numero | adresse_suffixe | adresse_nom_voie | adresse_code_voie | longitude | latitude | code_type_local | type_local | surface_reelle_bati | nombre_pieces_principales | surface_terrain | numero_disposition | id_parcelle | nombre_lots | lot1_numero | lot1_surface_carrez | lot2_numero | lot2_surface_carrez | lot3_numero | lot3_surface_carrez | lot4_numero | lot4_surface_carrez | lot5_numero | lot5_surface_carrez | code_nature_culture | nature_culture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-805070 | 2025-01-09 | Vente | 100000 | 63 | 63165 | Giat | 63620 | 1 |  | RTE DE ST AVIT | 0050 | 2.467293 | 45.803481 | 1 | Maison | 220 | 8 | 529 | 1 | 63165000AC0099 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-805070 | 2025-01-09 | Vente | 100000 | 63 | 63165 | Giat | 63620 | 1 |  | RTE DE ST AVIT | 0050 | 2.467293 | 45.803481 | 4 | Local industriel. commercial ou assimilé | 170 | 0 | 529 | 1 | 63165000AC0099 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |

#### `2025-805078` / disposition `1` — raw rows

| id_mutation | date_mutation | nature_mutation | valeur_fonciere | code_departement | code_commune | nom_commune | code_postal | adresse_numero | adresse_suffixe | adresse_nom_voie | adresse_code_voie | longitude | latitude | code_type_local | type_local | surface_reelle_bati | nombre_pieces_principales | surface_terrain | numero_disposition | id_parcelle | nombre_lots | lot1_numero | lot1_surface_carrez | lot2_numero | lot2_surface_carrez | lot3_numero | lot3_surface_carrez | lot4_numero | lot4_surface_carrez | lot5_numero | lot5_surface_carrez | code_nature_culture | nature_culture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-805078 | 2025-01-06 | Vente | 289770 | 63 | 63124 | Cournon-d'Auvergne | 63800 | 20 |  | IMP FREDERIC CHOPIN | 0435 | 3.204781 | 45.731605 | 4 | Local industriel. commercial ou assimilé |  | 0 | 1102 | 1 | 63124000BP0313 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-805078 | 2025-01-06 | Vente | 289770 | 63 | 63124 | Cournon-d'Auvergne | 63800 | 20 |  | IMP FREDERIC CHOPIN | 0435 | 3.204781 | 45.731605 | 1 | Maison | 147 | 5 | 1102 | 1 | 63124000BP0313 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |

#### `2025-805812` / disposition `1` — raw rows

| id_mutation | date_mutation | nature_mutation | valeur_fonciere | code_departement | code_commune | nom_commune | code_postal | adresse_numero | adresse_suffixe | adresse_nom_voie | adresse_code_voie | longitude | latitude | code_type_local | type_local | surface_reelle_bati | nombre_pieces_principales | surface_terrain | numero_disposition | id_parcelle | nombre_lots | lot1_numero | lot1_surface_carrez | lot2_numero | lot2_surface_carrez | lot3_numero | lot3_surface_carrez | lot4_numero | lot4_surface_carrez | lot5_numero | lot5_surface_carrez | code_nature_culture | nature_culture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-805812 | 2025-01-29 | Vente | 90000 | 63 | 63352 | Saint-Germain-Lembron | 63340 | 17 |  | RUE DES CLAVELIERS | 0032 | 3.238519 | 45.458368 | 4 | Local industriel. commercial ou assimilé | 32 | 0 | 35 | 1 | 63352000AA0158 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-805812 | 2025-01-29 | Vente | 90000 | 63 | 63352 | Saint-Germain-Lembron | 63340 | 17 |  | RUE DES CLAVELIERS | 0032 | 3.238519 | 45.458368 | 1 | Maison | 50 | 3 | 35 | 1 | 63352000AA0158 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |

### Parent ID with multiple dispositions

| id_mutation | numero_disposition | row_count | parent_disposition_count | parcel_count | commune_count | address_count | coordinate_count | distinct_value_count | transaction_value | house_row_count | apartment_row_count | dependency_row_count | commercial_row_count | distinct_residential_signature_count | terrain_row_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-805989 | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 380 | 0 | 0 | 0 | 0 | 0 | 1 |
| 2025-805989 | 2 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 380 | 0 | 0 | 0 | 0 | 0 | 1 |
| 2025-806255 | 2 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 150 | 0 | 0 | 0 | 0 | 0 | 1 |

#### `2025-805989` / disposition `1` — raw rows

| id_mutation | date_mutation | nature_mutation | valeur_fonciere | code_departement | code_commune | nom_commune | code_postal | adresse_numero | adresse_suffixe | adresse_nom_voie | adresse_code_voie | longitude | latitude | code_type_local | type_local | surface_reelle_bati | nombre_pieces_principales | surface_terrain | numero_disposition | id_parcelle | nombre_lots | lot1_numero | lot1_surface_carrez | lot2_numero | lot2_surface_carrez | lot3_numero | lot3_surface_carrez | lot4_numero | lot4_surface_carrez | lot5_numero | lot5_surface_carrez | code_nature_culture | nature_culture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-805989 | 2025-02-04 | Echange | 380 | 63 | 63345 | Saint-Genès-Champanelle | 63122 |  |  | MANSON | B274 | 3.012094 | 45.74533 |  |  |  |  | 224 | 1 | 63345000BE0089 | 0 |  |  |  |  |  |  |  |  |  |  | J | jardins |

#### `2025-805989` / disposition `2` — raw rows

| id_mutation | date_mutation | nature_mutation | valeur_fonciere | code_departement | code_commune | nom_commune | code_postal | adresse_numero | adresse_suffixe | adresse_nom_voie | adresse_code_voie | longitude | latitude | code_type_local | type_local | surface_reelle_bati | nombre_pieces_principales | surface_terrain | numero_disposition | id_parcelle | nombre_lots | lot1_numero | lot1_surface_carrez | lot2_numero | lot2_surface_carrez | lot3_numero | lot3_surface_carrez | lot4_numero | lot4_surface_carrez | lot5_numero | lot5_surface_carrez | code_nature_culture | nature_culture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-805989 | 2025-02-04 | Echange | 380 | 63 | 63345 | Saint-Genès-Champanelle | 63122 |  |  | MANSON | B274 | 3.012248 | 45.745374 |  |  |  |  | 222 | 2 | 63345000BE0344 | 0 |  |  |  |  |  |  |  |  |  |  | J | jardins |

#### `2025-806255` / disposition `2` — raw rows

| id_mutation | date_mutation | nature_mutation | valeur_fonciere | code_departement | code_commune | nom_commune | code_postal | adresse_numero | adresse_suffixe | adresse_nom_voie | adresse_code_voie | longitude | latitude | code_type_local | type_local | surface_reelle_bati | nombre_pieces_principales | surface_terrain | numero_disposition | id_parcelle | nombre_lots | lot1_numero | lot1_surface_carrez | lot2_numero | lot2_surface_carrez | lot3_numero | lot3_surface_carrez | lot4_numero | lot4_surface_carrez | lot5_numero | lot5_surface_carrez | code_nature_culture | nature_culture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-806255 | 2025-02-05 | Echange | 150 | 63 | 63439 | Usson | 63490 |  |  | USSON | B071 | 3.340857 | 45.528278 |  |  |  |  | 24 | 2 | 634390000E0657 | 0 |  |  |  |  |  |  |  |  |  |  | L | landes |

### Multiple geographies within one disposition

| id_mutation | numero_disposition | row_count | parent_disposition_count | parcel_count | commune_count | address_count | coordinate_count | distinct_value_count | transaction_value | house_row_count | apartment_row_count | dependency_row_count | commercial_row_count | distinct_residential_signature_count | terrain_row_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-804970 | 1 | 2 | 1 | 2 | 1 | 2 | 2 | 1 | 93270 | 0 | 0 | 0 | 0 | 0 | 2 |
| 2025-804981 | 1 | 2 | 1 | 2 | 1 | 2 | 2 | 1 | 800 | 0 | 0 | 0 | 0 | 0 | 2 |
| 2025-804985 | 1 | 2 | 1 | 1 | 1 | 2 | 1 | 1 | 70000 | 0 | 1 | 1 | 0 | 1 | 0 |

#### `2025-804970` / disposition `1` — raw rows

| id_mutation | date_mutation | nature_mutation | valeur_fonciere | code_departement | code_commune | nom_commune | code_postal | adresse_numero | adresse_suffixe | adresse_nom_voie | adresse_code_voie | longitude | latitude | code_type_local | type_local | surface_reelle_bati | nombre_pieces_principales | surface_terrain | numero_disposition | id_parcelle | nombre_lots | lot1_numero | lot1_surface_carrez | lot2_numero | lot2_surface_carrez | lot3_numero | lot3_surface_carrez | lot4_numero | lot4_surface_carrez | lot5_numero | lot5_surface_carrez | code_nature_culture | nature_culture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-804970 | 2025-01-02 | Vente | 93270 | 63 | 63032 | Beaumont | 63110 | 194 |  | RUE DE MONTPOLY | 0510 | 3.077366 | 45.751236 |  |  |  |  | 271 | 1 | 63032000BB0571 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-804970 | 2025-01-02 | Vente | 93270 | 63 | 63032 | Beaumont | 63110 |  |  | LA VERRE | B062 | 3.077221 | 45.751149 |  |  |  |  | 62 | 1 | 63032000BB0573 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |

#### `2025-804981` / disposition `1` — raw rows

| id_mutation | date_mutation | nature_mutation | valeur_fonciere | code_departement | code_commune | nom_commune | code_postal | adresse_numero | adresse_suffixe | adresse_nom_voie | adresse_code_voie | longitude | latitude | code_type_local | type_local | surface_reelle_bati | nombre_pieces_principales | surface_terrain | numero_disposition | id_parcelle | nombre_lots | lot1_numero | lot1_surface_carrez | lot2_numero | lot2_surface_carrez | lot3_numero | lot3_surface_carrez | lot4_numero | lot4_surface_carrez | lot5_numero | lot5_surface_carrez | code_nature_culture | nature_culture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-804981 | 2025-01-10 | Vente | 800 | 63 | 63076 | Chambon-sur-Dolore | 63980 |  |  | LES TERTRES | B229 | 3.602636 | 45.481673 |  |  |  |  | 4900 | 1 | 63076000ZI0049 | 0 |  |  |  |  |  |  |  |  |  |  | P | prés |
| 2025-804981 | 2025-01-10 | Vente | 800 | 63 | 63076 | Chambon-sur-Dolore | 63980 |  |  | SOUS LE BOIS | B218 | 3.600992 | 45.482015 |  |  |  |  | 700 | 1 | 63076000ZI0058 | 0 |  |  |  |  |  |  |  |  |  |  | P | prés |

#### `2025-804985` / disposition `1` — raw rows

| id_mutation | date_mutation | nature_mutation | valeur_fonciere | code_departement | code_commune | nom_commune | code_postal | adresse_numero | adresse_suffixe | adresse_nom_voie | adresse_code_voie | longitude | latitude | code_type_local | type_local | surface_reelle_bati | nombre_pieces_principales | surface_terrain | numero_disposition | id_parcelle | nombre_lots | lot1_numero | lot1_surface_carrez | lot2_numero | lot2_surface_carrez | lot3_numero | lot3_surface_carrez | lot4_numero | lot4_surface_carrez | lot5_numero | lot5_surface_carrez | code_nature_culture | nature_culture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-804985 | 2025-01-06 | Vente | 70000 | 63 | 63113 | Clermont-Ferrand | 63100 | 5 |  | AV BARBIER DAUBREE | 0370 | 3.091965 | 45.787616 | 2 | Appartement | 31 | 1 |  | 1 | 63113000LR0772 | 1 | 102 | 30.98 |  |  |  |  |  |  |  |  |  |  |
| 2025-804985 | 2025-01-06 | Vente | 70000 | 63 | 63113 | Clermont-Ferrand | 63100 | 16 | B | RUE DU BAS CHAMPFLOUR | 0415 | 3.091965 | 45.787616 | 3 | Dépendance |  | 0 |  | 1 | 63113000LR0772 | 1 | 46 |  |  |  |  |  |  |  |  |  |  |  |

### Land-only mutation

| id_mutation | numero_disposition | row_count | parent_disposition_count | parcel_count | commune_count | address_count | coordinate_count | distinct_value_count | transaction_value | house_row_count | apartment_row_count | dependency_row_count | commercial_row_count | distinct_residential_signature_count | terrain_row_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-804962 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 250 | 0 | 0 | 0 | 0 | 0 | 1 |
| 2025-804963 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 220 | 0 | 0 | 0 | 0 | 0 | 1 |
| 2025-804965 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 25000 | 0 | 0 | 0 | 0 | 0 | 1 |

#### `2025-804962` / disposition `1` — raw rows

| id_mutation | date_mutation | nature_mutation | valeur_fonciere | code_departement | code_commune | nom_commune | code_postal | adresse_numero | adresse_suffixe | adresse_nom_voie | adresse_code_voie | longitude | latitude | code_type_local | type_local | surface_reelle_bati | nombre_pieces_principales | surface_terrain | numero_disposition | id_parcelle | nombre_lots | lot1_numero | lot1_surface_carrez | lot2_numero | lot2_surface_carrez | lot3_numero | lot3_surface_carrez | lot4_numero | lot4_surface_carrez | lot5_numero | lot5_surface_carrez | code_nature_culture | nature_culture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-804962 | 2025-01-08 | Vente | 250 | 63 | 63324 | Saint-Bonnet-le-Chastel | 63630 |  |  | LACHON | B075 | 3.656022 | 45.485476 |  |  |  |  | 3590 | 1 | 633240000A0063 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |

#### `2025-804963` / disposition `1` — raw rows

| id_mutation | date_mutation | nature_mutation | valeur_fonciere | code_departement | code_commune | nom_commune | code_postal | adresse_numero | adresse_suffixe | adresse_nom_voie | adresse_code_voie | longitude | latitude | code_type_local | type_local | surface_reelle_bati | nombre_pieces_principales | surface_terrain | numero_disposition | id_parcelle | nombre_lots | lot1_numero | lot1_surface_carrez | lot2_numero | lot2_surface_carrez | lot3_numero | lot3_surface_carrez | lot4_numero | lot4_surface_carrez | lot5_numero | lot5_surface_carrez | code_nature_culture | nature_culture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-804963 | 2025-01-08 | Vente | 220 | 63 | 63139 | Dore-l'Église | 63220 |  |  | LES NARSSAIRAS | B376 | 3.767386 | 45.389789 |  |  |  |  | 1114 | 1 | 63139000ZX0047 | 0 |  |  |  |  |  |  |  |  |  |  | P | prés |

#### `2025-804965` / disposition `2` — raw rows

| id_mutation | date_mutation | nature_mutation | valeur_fonciere | code_departement | code_commune | nom_commune | code_postal | adresse_numero | adresse_suffixe | adresse_nom_voie | adresse_code_voie | longitude | latitude | code_type_local | type_local | surface_reelle_bati | nombre_pieces_principales | surface_terrain | numero_disposition | id_parcelle | nombre_lots | lot1_numero | lot1_surface_carrez | lot2_numero | lot2_surface_carrez | lot3_numero | lot3_surface_carrez | lot4_numero | lot4_surface_carrez | lot5_numero | lot5_surface_carrez | code_nature_culture | nature_culture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-804965 | 2025-01-03 | Vente | 25000 | 63 | 63300 | Riom | 63200 |  |  | LES MARTRES DE MADARGUE | B058 | 3.091577 | 45.90624 |  |  |  |  | 376 | 2 | 63300000ZB1012 | 0 |  |  |  |  |  |  |  |  |  |  | T | terres |

### Missing transaction value

| id_mutation | numero_disposition | row_count | parent_disposition_count | parcel_count | commune_count | address_count | coordinate_count | distinct_value_count | transaction_value | house_row_count | apartment_row_count | dependency_row_count | commercial_row_count | distinct_residential_signature_count | terrain_row_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-805986 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 |  | 0 | 0 | 0 | 0 | 0 | 1 |
| 2025-806345 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 |  | 0 | 0 | 0 | 0 | 0 | 1 |
| 2025-806412 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 |  | 0 | 0 | 0 | 0 | 0 | 1 |

#### `2025-805986` / disposition `1` — raw rows

| id_mutation | date_mutation | nature_mutation | valeur_fonciere | code_departement | code_commune | nom_commune | code_postal | adresse_numero | adresse_suffixe | adresse_nom_voie | adresse_code_voie | longitude | latitude | code_type_local | type_local | surface_reelle_bati | nombre_pieces_principales | surface_terrain | numero_disposition | id_parcelle | nombre_lots | lot1_numero | lot1_surface_carrez | lot2_numero | lot2_surface_carrez | lot3_numero | lot3_surface_carrez | lot4_numero | lot4_surface_carrez | lot5_numero | lot5_surface_carrez | code_nature_culture | nature_culture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-805986 | 2025-01-08 | Vente |  | 63 | 63073 | Chadeleuf | 63320 |  |  | LE MONTEL | B026 | 3.193273 | 45.587681 |  |  |  |  | 11190 | 1 | 63073000ZC0051 | 0 |  |  |  |  |  |  |  |  |  |  | PA | pâtures |

#### `2025-806345` / disposition `1` — raw rows

| id_mutation | date_mutation | nature_mutation | valeur_fonciere | code_departement | code_commune | nom_commune | code_postal | adresse_numero | adresse_suffixe | adresse_nom_voie | adresse_code_voie | longitude | latitude | code_type_local | type_local | surface_reelle_bati | nombre_pieces_principales | surface_terrain | numero_disposition | id_parcelle | nombre_lots | lot1_numero | lot1_surface_carrez | lot2_numero | lot2_surface_carrez | lot3_numero | lot3_surface_carrez | lot4_numero | lot4_surface_carrez | lot5_numero | lot5_surface_carrez | code_nature_culture | nature_culture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-806345 | 2025-01-30 | Vente |  | 63 | 63207 | Marat | 63480 |  |  | LE GRIPPEL | B081 | 3.699429 | 45.674573 |  |  |  |  | 2434 | 1 | 63207000AE0047 | 0 |  |  |  |  |  |  |  |  |  |  | P | prés |

#### `2025-806412` / disposition `1` — raw rows

| id_mutation | date_mutation | nature_mutation | valeur_fonciere | code_departement | code_commune | nom_commune | code_postal | adresse_numero | adresse_suffixe | adresse_nom_voie | adresse_code_voie | longitude | latitude | code_type_local | type_local | surface_reelle_bati | nombre_pieces_principales | surface_terrain | numero_disposition | id_parcelle | nombre_lots | lot1_numero | lot1_surface_carrez | lot2_numero | lot2_surface_carrez | lot3_numero | lot3_surface_carrez | lot4_numero | lot4_surface_carrez | lot5_numero | lot5_surface_carrez | code_nature_culture | nature_culture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-806412 | 2025-02-17 | Vente |  | 63 | 63014 | Aubière | 63170 |  |  | ALL BEL AIR | 0068 | 3.103932 | 45.754224 |  |  |  |  | 861 | 1 | 63014000BB0169 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |

### Unusually large mutation

| id_mutation | numero_disposition | row_count | parent_disposition_count | parcel_count | commune_count | address_count | coordinate_count | distinct_value_count | transaction_value | house_row_count | apartment_row_count | dependency_row_count | commercial_row_count | distinct_residential_signature_count | terrain_row_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-821650 | 1 | 153 | 1 | 1 | 1 | 4 | 1 | 0 |  | 0 | 48 | 105 | 0 | 48 | 0 |
| 2025-809217 | 1 | 141 | 1 | 134 | 3 | 26 | 134 | 1 | 35000 | 0 | 0 | 0 | 0 | 0 | 141 |
| 2025-821070 | 1 | 120 | 1 | 1 | 1 | 1 | 1 | 1 | 1458000 | 0 | 118 | 0 | 2 | 30 | 120 |

#### `2025-821650` / disposition `1` — raw rows

| id_mutation | date_mutation | nature_mutation | valeur_fonciere | code_departement | code_commune | nom_commune | code_postal | adresse_numero | adresse_suffixe | adresse_nom_voie | adresse_code_voie | longitude | latitude | code_type_local | type_local | surface_reelle_bati | nombre_pieces_principales | surface_terrain | numero_disposition | id_parcelle | nombre_lots | lot1_numero | lot1_surface_carrez | lot2_numero | lot2_surface_carrez | lot3_numero | lot3_surface_carrez | lot4_numero | lot4_surface_carrez | lot5_numero | lot5_surface_carrez | code_nature_culture | nature_culture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 2 | Appartement | 81 | 4 |  | 1 | 63075000AE0750 | 2 | 114 |  | 90 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 2 | Appartement | 35 | 1 |  | 1 | 63075000AE0750 | 2 | 113 |  | 89 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 2 | Appartement | 53 | 2 |  | 1 | 63075000AE0750 | 2 | 112 |  | 88 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 8 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 2 | Appartement | 80 | 4 |  | 1 | 63075000AE0750 | 2 | 64 |  | 72 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 8 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 2 | Appartement | 77 | 4 |  | 1 | 63075000AE0750 | 2 | 63 |  | 71 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 8 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 2 | Appartement | 80 | 4 |  | 1 | 63075000AE0750 | 2 | 66 |  | 74 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 8 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 2 | Appartement | 77 | 4 |  | 1 | 63075000AE0750 | 2 | 65 |  | 73 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 8 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 2 | Appartement | 80 | 4 |  | 1 | 63075000AE0750 | 2 | 68 |  | 76 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 8 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 2 | Appartement | 77 | 4 |  | 1 | 63075000AE0750 | 2 | 67 |  | 75 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 8 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 2 | Appartement | 80 | 4 |  | 1 | 63075000AE0750 | 2 | 70 |  | 78 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 8 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 2 | Appartement | 77 | 4 |  | 1 | 63075000AE0750 | 2 | 69 |  | 77 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 2 |  | AV VALERY GISCARD D ESTAING | 0530 | 3.063203 | 45.776435 | 2 | Appartement | 76 | 4 |  | 1 | 63075000AE0750 | 2 | 117 |  | 141 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 2 |  | AV VALERY GISCARD D ESTAING | 0530 | 3.063203 | 45.776435 | 2 | Appartement | 76 | 4 |  | 1 | 63075000AE0750 | 2 | 118 |  | 142 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 2 |  | AV VALERY GISCARD D ESTAING | 0530 | 3.063203 | 45.776435 | 2 | Appartement | 63 | 3 |  | 1 | 63075000AE0750 | 2 | 119 |  | 143 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 2 |  | AV VALERY GISCARD D ESTAING | 0530 | 3.063203 | 45.776435 | 2 | Appartement | 89 | 5 |  | 1 | 63075000AE0750 | 2 | 120 |  | 144 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 2 |  | AV VALERY GISCARD D ESTAING | 0530 | 3.063203 | 45.776435 | 2 | Appartement | 76 | 4 |  | 1 | 63075000AE0750 | 2 | 121 |  | 145 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 2 |  | AV VALERY GISCARD D ESTAING | 0530 | 3.063203 | 45.776435 | 2 | Appartement | 76 | 4 |  | 1 | 63075000AE0750 | 2 | 122 |  | 146 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 2 |  | AV VALERY GISCARD D ESTAING | 0530 | 3.063203 | 45.776435 | 2 | Appartement | 63 | 3 |  | 1 | 63075000AE0750 | 2 | 123 |  | 147 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 2 |  | AV VALERY GISCARD D ESTAING | 0530 | 3.063203 | 45.776435 | 2 | Appartement | 89 | 5 |  | 1 | 63075000AE0750 | 2 | 124 |  | 148 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 2 |  | AV VALERY GISCARD D ESTAING | 0530 | 3.063203 | 45.776435 | 2 | Appartement | 76 | 4 |  | 1 | 63075000AE0750 | 2 | 126 |  | 150 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 2 |  | AV VALERY GISCARD D ESTAING | 0530 | 3.063203 | 45.776435 | 2 | Appartement | 76 | 4 |  | 1 | 63075000AE0750 | 2 | 125 |  | 149 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 2 |  | AV VALERY GISCARD D ESTAING | 0530 | 3.063203 | 45.776435 | 2 | Appartement | 63 | 3 |  | 1 | 63075000AE0750 | 2 | 127 |  | 151 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 2 |  | AV VALERY GISCARD D ESTAING | 0530 | 3.063203 | 45.776435 | 2 | Appartement | 89 | 5 |  | 1 | 63075000AE0750 | 2 | 128 |  | 152 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 2 |  | AV VALERY GISCARD D ESTAING | 0530 | 3.063203 | 45.776435 | 2 | Appartement | 76 | 4 |  | 1 | 63075000AE0750 | 2 | 130 |  | 154 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 2 |  | AV VALERY GISCARD D ESTAING | 0530 | 3.063203 | 45.776435 | 2 | Appartement | 76 | 4 |  | 1 | 63075000AE0750 | 2 | 129 |  | 153 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 2 |  | AV VALERY GISCARD D ESTAING | 0530 | 3.063203 | 45.776435 | 2 | Appartement | 63 | 3 |  | 1 | 63075000AE0750 | 2 | 131 |  | 155 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 2 |  | AV VALERY GISCARD D ESTAING | 0530 | 3.063203 | 45.776435 | 2 | Appartement | 89 | 5 |  | 1 | 63075000AE0750 | 2 | 132 |  | 156 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 2 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 3 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 3 | 29 |  | 41 |  | 51 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 3 | 29 |  | 41 |  | 51 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 3 | 29 |  | 41 |  | 51 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 2 |  | AV VALERY GISCARD D ESTAING | 0530 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 130 |  | 154 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 8 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 69 |  | 77 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 3 | 37 |  | 49 |  | 61 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 3 | 37 |  | 49 |  | 61 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 2 |  | AV VALERY GISCARD D ESTAING | 0530 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 125 |  | 149 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 2 |  | AV VALERY GISCARD D ESTAING | 0530 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 127 |  | 151 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 3 | 27 |  | 39 |  | 53 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 3 | 27 |  | 39 |  | 53 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 105 |  | 81 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 3 | 34 |  | 46 |  | 58 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 3 | 34 |  | 46 |  | 58 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 106 |  | 82 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 2 |  | AV VALERY GISCARD D ESTAING | 0530 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 119 |  | 143 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 3 | 36 |  | 48 |  | 62 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 3 | 36 |  | 48 |  | 62 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 3 | 36 |  | 48 |  | 62 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 3 | 38 |  | 50 |  | 60 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 3 | 38 |  | 50 |  | 60 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 3 | 38 |  | 50 |  | 60 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 8 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 64 |  | 72 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 2 |  | AV VALERY GISCARD D ESTAING | 0530 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 128 |  | 152 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 8 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 68 |  | 76 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 3 | 30 |  | 42 |  | 56 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 3 | 30 |  | 42 |  | 56 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 3 | 30 |  | 42 |  | 56 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 2 |  | AV VALERY GISCARD D ESTAING | 0530 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 117 |  | 141 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 112 |  | 88 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 8 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 66 |  | 74 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 3 | 35 |  | 47 |  | 57 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 2 | Appartement | 81 | 4 |  | 1 | 63075000AE0750 | 2 | 105 |  | 81 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 2 | Appartement | 35 | 1 |  | 1 | 63075000AE0750 | 2 | 104 |  | 80 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 92 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 93 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 94 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 95 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 96 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 97 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 98 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 99 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 100 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 101 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 102 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 8 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 65 |  | 73 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 8 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 63 |  | 71 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 110 |  | 86 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 2 |  | AV VALERY GISCARD D ESTAING | 0530 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 118 |  | 142 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 108 |  | 84 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 2 |  | AV VALERY GISCARD D ESTAING | 0530 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 124 |  | 148 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 2 |  | AV VALERY GISCARD D ESTAING | 0530 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 123 |  | 147 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 2 |  | AV VALERY GISCARD D ESTAING | 0530 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 129 |  | 153 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 103 |  | 79 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 3 | 35 |  | 47 |  | 57 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 3 | 35 |  | 47 |  | 57 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 3 | 31 |  | 43 |  | 55 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 3 | 31 |  | 43 |  | 55 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 104 |  | 80 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 111 |  | 87 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 2 | Appartement | 53 | 2 |  | 1 | 63075000AE0750 | 2 | 103 |  | 79 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 2 | Appartement | 81 | 4 |  | 1 | 63075000AE0750 | 2 | 108 |  | 84 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 2 | Appartement | 35 | 1 |  | 1 | 63075000AE0750 | 2 | 107 |  | 83 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 2 | Appartement | 53 | 2 |  | 1 | 63075000AE0750 | 2 | 106 |  | 82 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 2 | Appartement | 81 | 4 |  | 1 | 63075000AE0750 | 2 | 111 |  | 87 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 2 | Appartement | 35 | 1 |  | 1 | 63075000AE0750 | 2 | 110 |  | 86 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 2 | Appartement | 53 | 2 |  | 1 | 63075000AE0750 | 2 | 109 |  | 85 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 2 | Appartement | 52 | 2 |  | 1 | 63075000AE0750 | 3 | 36 |  | 48 |  | 62 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 2 | Appartement | 35 | 1 |  | 1 | 63075000AE0750 | 3 | 37 |  | 49 |  | 61 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 2 | Appartement | 82 | 4 |  | 1 | 63075000AE0750 | 3 | 38 |  | 50 |  | 60 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 91 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 22 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 113 |  | 89 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 2 |  | AV VALERY GISCARD D ESTAING | 0530 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 121 |  | 145 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 2 |  | AV VALERY GISCARD D ESTAING | 0530 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 122 |  | 146 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 8 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 70 |  | 78 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 109 |  | 85 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 3 | 28 |  | 40 |  | 52 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 3 | 28 |  | 40 |  | 52 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 2 |  | AV VALERY GISCARD D ESTAING | 0530 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 132 |  | 156 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 2 |  | AV VALERY GISCARD D ESTAING | 0530 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 120 |  | 144 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 114 |  | 90 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 3 | 32 |  | 44 |  | 54 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 2 | Appartement | 52 | 2 |  | 1 | 63075000AE0750 | 3 | 33 |  | 45 |  | 59 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 2 | Appartement | 82 | 4 |  | 1 | 63075000AE0750 | 3 | 32 |  | 44 |  | 54 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 2 | Appartement | 35 | 1 |  | 1 | 63075000AE0750 | 3 | 31 |  | 43 |  | 55 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 2 | Appartement | 52 | 2 |  | 1 | 63075000AE0750 | 3 | 30 |  | 42 |  | 56 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 2 | Appartement | 82 | 4 |  | 1 | 63075000AE0750 | 3 | 29 |  | 41 |  | 51 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 2 | Appartement | 35 | 1 |  | 1 | 63075000AE0750 | 3 | 28 |  | 40 |  | 52 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 2 | Appartement | 52 | 2 |  | 1 | 63075000AE0750 | 3 | 27 |  | 39 |  | 53 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 26 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 25 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 24 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 23 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 21 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 4 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 5 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 6 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 7 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 8 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 9 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 10 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 11 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 12 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 13 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 14 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 15 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 16 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 17 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 18 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 19 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 1 | 20 |  |  |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 3 | 32 |  | 44 |  | 54 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 3 | 32 |  | 44 |  | 54 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 2 |  | AV VALERY GISCARD D ESTAING | 0530 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 131 |  | 155 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 2 |  | AV VALERY GISCARD D ESTAING | 0530 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 126 |  | 150 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 6 | B | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 107 |  | 83 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 8 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 2 | 67 |  | 75 |  |  |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 3 | 33 |  | 45 |  | 59 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 3 | 33 |  | 45 |  | 59 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 3 | Dépendance |  | 0 |  | 1 | 63075000AE0750 | 3 | 33 |  | 45 |  | 59 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 2 | Appartement | 82 | 4 |  | 1 | 63075000AE0750 | 3 | 35 |  | 47 |  | 57 |  |  |  |  |  |  |  |
| 2025-821650 | 2025-12-19 | Vente |  | 63 | 63075 | Chamalières | 63400 | 10 |  | AV DE VILLARS | 1450 | 3.063203 | 45.776435 | 2 | Appartement | 35 | 1 |  | 1 | 63075000AE0750 | 3 | 34 |  | 46 |  | 58 |  |  |  |  |  |  |  |

#### `2025-809217` / disposition `1` — raw rows

| id_mutation | date_mutation | nature_mutation | valeur_fonciere | code_departement | code_commune | nom_commune | code_postal | adresse_numero | adresse_suffixe | adresse_nom_voie | adresse_code_voie | longitude | latitude | code_type_local | type_local | surface_reelle_bati | nombre_pieces_principales | surface_terrain | numero_disposition | id_parcelle | nombre_lots | lot1_numero | lot1_surface_carrez | lot2_numero | lot2_surface_carrez | lot3_numero | lot3_surface_carrez | lot4_numero | lot4_surface_carrez | lot5_numero | lot5_surface_carrez | code_nature_culture | nature_culture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | SUQUET DU CURE | B222 | 2.943626 | 45.572017 |  |  |  |  | 132 | 1 | 63247000AN0500 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | SUQUET DU CURE | B222 | 2.943678 | 45.572002 |  |  |  |  | 180 | 1 | 63247000AN0501 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | SUQUET DU CURE | B222 | 2.943877 | 45.571934 |  |  |  |  | 289 | 1 | 63247000AN0505 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | SUQUET DU CURE | B222 | 2.944185 | 45.571847 |  |  |  |  | 997 | 1 | 63247000AN0509 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LES PINEROUNES | B159 | 2.931459 | 45.566636 |  |  |  |  | 1340 | 1 | 63247000AT0061 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LES PINEROUNES | B159 | 2.931138 | 45.566669 |  |  |  |  | 1595 | 1 | 63247000AT0062 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LES PINEROUNES | B159 | 2.930889 | 45.566471 |  |  |  |  | 700 | 1 | 63247000AT0064 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LES PINEROUNES | B159 | 2.928423 | 45.565659 |  |  |  |  | 3523 | 1 | 63247000AT0077 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LES BOUVES | B012 | 2.922698 | 45.564274 |  |  |  |  | 556 | 1 | 63247000AT0112 | 0 |  |  |  |  |  |  |  |  |  |  | BF | futaies feuillues |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LES BOUVES | B012 | 2.922705 | 45.564414 |  |  |  |  | 275 | 1 | 63247000AT0113 | 0 |  |  |  |  |  |  |  |  |  |  | BF | futaies feuillues |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LES BOUVES | B012 | 2.922709 | 45.564507 |  |  |  |  | 268 | 1 | 63247000AT0114 | 0 |  |  |  |  |  |  |  |  |  |  | BF | futaies feuillues |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LES BOUVES | B012 | 2.922719 | 45.564651 |  |  |  |  | 370 | 1 | 63247000AT0115 | 0 |  |  |  |  |  |  |  |  |  |  | BF | futaies feuillues |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LES BOUVES | B012 | 2.922764 | 45.565297 |  |  |  |  | 126 | 1 | 63247000AT0126 | 0 |  |  |  |  |  |  |  |  |  |  | BF | futaies feuillues |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LES BOUVES | B012 | 2.92297 | 45.565387 |  |  |  |  | 150 | 1 | 63247000AT0128 | 0 |  |  |  |  |  |  |  |  |  |  | BF | futaies feuillues |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LES BOUVES | B012 | 2.922752 | 45.565641 |  |  |  |  | 260 | 1 | 63247000AT0130 | 0 |  |  |  |  |  |  |  |  |  |  | BF | futaies feuillues |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LES BOUVES | B012 | 2.92226 | 45.564605 |  |  |  |  | 480 | 1 | 63247000AT0149 | 0 |  |  |  |  |  |  |  |  |  |  | BF | futaies feuillues |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LES BOUVES | B012 | 2.92221 | 45.564482 |  |  |  |  | 255 | 1 | 63247000AT0150 | 0 |  |  |  |  |  |  |  |  |  |  | BF | futaies feuillues |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | PIERREBINES | B158 | 2.924247 | 45.564234 |  |  |  |  | 1935 | 1 | 63247000AT0156 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | PIERREBINES | B158 | 2.924337 | 45.563784 |  |  |  |  | 1435 | 1 | 63247000AT0157 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | PIERREBINES | B158 | 2.926087 | 45.564335 |  |  |  |  | 1775 | 1 | 63247000AT0159 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | PIERREBINES | B158 | 2.925688 | 45.564861 |  |  |  |  | 670 | 1 | 63247000AT0161 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | PIERREBINES | B158 | 2.925281 | 45.564781 |  |  |  |  | 3870 | 1 | 63247000AT0162 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | PIERREBINES | B158 | 2.929068 | 45.564059 |  |  |  |  | 3245 | 1 | 63247000AT0173 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LES FONTELS | B087 | 2.936002 | 45.583719 |  |  |  |  | 1820 | 1 | 63247000ZI0050 | 0 |  |  |  |  |  |  |  |  |  |  | PA | pâtures |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | PRE CLOS | B182 | 2.947006 | 45.575283 |  |  |  |  | 185 | 1 | 63247000ZM0064 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | CHASTREIX | B039 | 2.947845 | 45.564564 |  |  |  |  | 10320 | 1 | 63247000ZR0037 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | CHASTREIX | B039 | 2.947689 | 45.565747 |  |  |  |  | 4340 | 1 | 63247000ZR0040 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | CHASTREIX | B039 | 2.947778 | 45.566027 |  |  |  |  | 810 | 1 | 63247000ZR0041 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | CHAMP PRADEL | B029 | 2.94832 | 45.568622 |  |  |  |  | 835 | 1 | 63247000ZR0053 | 0 |  |  |  |  |  |  |  |  |  |  | PA | pâtures |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | CHAMP PRADEL | B029 | 2.94832 | 45.568622 |  |  |  |  | 835 | 1 | 63247000ZR0053 | 0 |  |  |  |  |  |  |  |  |  |  | J | jardins |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | CHAMP PRADEL | B029 | 2.949616 | 45.569631 |  |  |  |  | 13970 | 1 | 63247000ZR0060 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LA TOURLE | B229 | 2.948968 | 45.568538 |  |  |  |  | 1640 | 1 | 63247000ZR0061 | 0 |  |  |  |  |  |  |  |  |  |  | PA | pâtures |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LA TOURLE | B229 | 2.949823 | 45.56897 |  |  |  |  | 1850 | 1 | 63247000ZR0062 | 0 |  |  |  |  |  |  |  |  |  |  | PA | pâtures |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | CHARRIERE | B034 | 2.951581 | 45.569444 |  |  |  |  | 1930 | 1 | 63247000ZR0068 | 0 |  |  |  |  |  |  |  |  |  |  | PA | pâtures |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LATEIRE | B119 | 2.964622 | 45.568499 |  |  |  |  | 2400 | 1 | 63247000ZR0106 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LATEIRE | B119 | 2.963851 | 45.568385 |  |  |  |  | 5670 | 1 | 63247000ZR0108 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LATEIRE | B119 | 2.963659 | 45.568113 |  |  |  |  | 450 | 1 | 63247000ZR0110 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LATEIRE | B119 | 2.963484 | 45.568821 |  |  |  |  | 1100 | 1 | 63247000ZR0111 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LATEIRE | B119 | 2.963136 | 45.5687 |  |  |  |  | 680 | 1 | 63247000ZR0112 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LATEIRE | B119 | 2.962973 | 45.568263 |  |  |  |  | 1980 | 1 | 63247000ZR0114 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LATEIRE | B119 | 2.96177 | 45.569072 |  |  |  |  | 372 | 1 | 63247000ZR0118 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LATEIRE | B119 | 2.962295 | 45.568841 |  |  |  |  | 1340 | 1 | 63247000ZR0120 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | BOIS DE GROIRE | B010 | 2.96226 | 45.568478 |  |  |  |  | 800 | 1 | 63247000ZR0122 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | BOIS DE GROIRE | B010 | 2.96185 | 45.56823 |  |  |  |  | 1390 | 1 | 63247000ZR0124 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | BOIS DE GROIRE | B010 | 2.961939 | 45.567958 |  |  |  |  | 1590 | 1 | 63247000ZR0125 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | BOIS DE GROIRE | B010 | 2.962453 | 45.567988 |  |  |  |  | 1130 | 1 | 63247000ZR0128 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | BOIS DE GROIRE | B010 | 2.962807 | 45.567942 |  |  |  |  | 1150 | 1 | 63247000ZR0129 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | BOIS DE GROIRE | B010 | 2.962812 | 45.567462 |  |  |  |  | 8140 | 1 | 63247000ZR0130 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | BOIS DE GROIRE | B010 | 2.962592 | 45.566924 |  |  |  |  | 295 | 1 | 63247000ZR0138 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | BOIS DE GROIRE | B010 | 2.96214 | 45.566448 |  |  |  |  | 770 | 1 | 63247000ZR0141 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | BOIS DE GROIRE | B010 | 2.96204 | 45.567364 |  |  |  |  | 585 | 1 | 63247000ZR0145 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | BOIS DE GROIRE | B010 | 2.961959 | 45.567425 |  |  |  |  | 530 | 1 | 63247000ZR0146 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | BOIS DE GROIRE | B010 | 2.961206 | 45.567465 |  |  |  |  | 3845 | 1 | 63247000ZR0152 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | BOIS DE GROIRE | B010 | 2.960313 | 45.567152 |  |  |  |  | 740 | 1 | 63247000ZR0158 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | BOIS DE GROIRE | B010 | 2.960118 | 45.566623 |  |  |  |  | 447 | 1 | 63247000ZR0160 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | BOIS DE GROIRE | B010 | 2.960397 | 45.568177 |  |  |  |  | 735 | 1 | 63247000ZR0166 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | BOIS DE GROIRE | B010 | 2.961184 | 45.568967 |  |  |  |  | 440 | 1 | 63247000ZR0168 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | BOIS DE GROIRE | B010 | 2.96073 | 45.568953 |  |  |  |  | 1160 | 1 | 63247000ZR0170 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | BOIS DE GROIRE | B010 | 2.960106 | 45.568809 |  |  |  |  | 540 | 1 | 63247000ZR0173 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | BOIS DE GROIRE | B010 | 2.96005 | 45.568463 |  |  |  |  | 1530 | 1 | 63247000ZR0174 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | BOIS DE GROIRE | B010 | 2.959694 | 45.566678 |  |  |  |  | 383 | 1 | 63247000ZR0177 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | BOIS DE GROIRE | B010 | 2.958995 | 45.567362 |  |  |  |  | 355 | 1 | 63247000ZR0180 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | BOIS DE GROIRE | B010 | 2.957724 | 45.567304 |  |  |  |  | 3035 | 1 | 63247000ZR0193 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | BOIS DE GROIRE | B010 | 2.957836 | 45.566856 |  |  |  |  | 300 | 1 | 63247000ZR0194 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | BOIS DE GROIRE | B010 | 2.957521 | 45.567385 |  |  |  |  | 915 | 1 | 63247000ZR0197 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | BOIS DE GROIRE | B010 | 2.956693 | 45.56667 |  |  |  |  | 1135 | 1 | 63247000ZR0205 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | BOIS DE GROIRE | B010 | 2.954377 | 45.567087 |  |  |  |  | 600 | 1 | 63247000ZR0216 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | BOIS DE GROIRE | B010 | 2.953433 | 45.567999 |  |  |  |  | 1310 | 1 | 63247000ZR0219 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | BOIS DE GROIRE | B010 | 2.953321 | 45.56798 |  |  |  |  | 1260 | 1 | 63247000ZR0220 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | BOIS DE GROIRE | B010 | 2.952816 | 45.566998 |  |  |  |  | 3280 | 1 | 63247000ZR0225 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | BOIS DE GROIRE | B010 | 2.952081 | 45.568145 |  |  |  |  | 2730 | 1 | 63247000ZR0227 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | BOIS DE GROIRE | B010 | 2.952586 | 45.567766 |  |  |  |  | 3025 | 1 | 63247000ZR0229 | 0 |  |  |  |  |  |  |  |  |  |  | BF | futaies feuillues |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | CHAMP BARON | B024 | 2.952564 | 45.567226 |  |  |  |  | 185 | 1 | 63247000ZR0230 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | CHAMP BARON | B024 | 2.952403 | 45.567135 |  |  |  |  | 1310 | 1 | 63247000ZR0232 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | CHAMP BARON | B024 | 2.951302 | 45.567426 |  |  |  |  | 187 | 1 | 63247000ZR0237 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | CHAMP BARON | B024 | 2.951961 | 45.566118 |  |  |  |  | 1100 | 1 | 63247000ZR0241 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | CHAMP BARON | B024 | 2.95147 | 45.566731 |  |  |  |  | 1490 | 1 | 63247000ZR0242 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | CHAMP BARON | B024 | 2.951224 | 45.566437 |  |  |  |  | 600 | 1 | 63247000ZR0246 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | CHAMP BARON | B024 | 2.950637 | 45.566369 |  |  |  |  | 5430 | 1 | 63247000ZR0247 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | CHAMP BARON | B024 | 2.949743 | 45.565302 |  |  |  |  | 1320 | 1 | 63247000ZR0251 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | CHASSAIGNE | B037 | 2.949223 | 45.564092 |  |  |  |  | 685 | 1 | 63247000ZR0263 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | CHASSAIGNE | B037 | 2.94903 | 45.56438 |  |  |  |  | 930 | 1 | 63247000ZR0264 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | CHASSAIGNE | B037 | 2.949574 | 45.564394 |  |  |  |  | 1035 | 1 | 63247000ZR0265 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | CHASSAIGNE | B037 | 2.948692 | 45.564838 |  |  |  |  | 3390 | 1 | 63247000ZR0268 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | CHAMP BARON | B024 | 2.948441 | 45.565166 |  |  |  |  | 240 | 1 | 63247000ZR0269 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | CHAMP BARON | B024 | 2.949147 | 45.565457 |  |  |  |  | 6765 | 1 | 63247000ZR0272 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | CHAMP BARON | B024 | 2.949191 | 45.565791 |  |  |  |  | 1533 | 1 | 63247000ZR0273 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | CHAMP BARON | B024 | 2.949884 | 45.566537 |  |  |  |  | 555 | 1 | 63247000ZR0278 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | CHAMP BARON | B024 | 2.951059 | 45.567143 |  |  |  |  | 1730 | 1 | 63247000ZR0281 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | CHAMP BARON | B024 | 2.950418 | 45.56749 |  |  |  |  | 1976 | 1 | 63247000ZR0282 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | CHAMP BARON | B024 | 2.950248 | 45.567278 |  |  |  |  | 590 | 1 | 63247000ZR0283 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | CHAMP BARON | B024 | 2.949132 | 45.56759 |  |  |  |  | 438 | 1 | 63247000ZR0287 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | CHAMP BARON | B024 | 2.950002 | 45.568009 |  |  |  |  | 830 | 1 | 63247000ZR0291 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | CHAMP BARON | B024 | 2.950465 | 45.568249 |  |  |  |  | 1000 | 1 | 63247000ZR0293 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | CHAMP BARON | B024 | 2.950347 | 45.567881 |  |  |  |  | 2150 | 1 | 63247000ZR0294 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | CHAMP BARON | B024 | 2.950927 | 45.568229 |  |  |  |  | 2735 | 1 | 63247000ZR0296 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | CHAMP BARON | B024 | 2.951443 | 45.568529 |  |  |  |  | 5760 | 1 | 63247000ZR0297 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | CHAMP BARON | B024 | 2.951302 | 45.56899 |  |  |  |  | 691 | 1 | 63247000ZR0298 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | PLAT | B166 | 2.952176 | 45.569026 |  |  |  |  | 1550 | 1 | 63247000ZR0301 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | PLAT | B166 | 2.952681 | 45.569235 |  |  |  |  | 3890 | 1 | 63247000ZR0303 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LA BOSSE | B273 | 2.952998 | 45.56862 |  |  |  |  | 1140 | 1 | 63247000ZR0304 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LA BOSSE | B273 | 2.953462 | 45.568898 |  |  |  |  | 810 | 1 | 63247000ZR0307 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | PLAT | B166 | 2.953273 | 45.569447 |  |  |  |  | 660 | 1 | 63247000ZR0309 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LA BOSSE | B273 | 2.953856 | 45.569195 |  |  |  |  | 1335 | 1 | 63247000ZR0312 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LA PLAINE | B163 | 2.954991 | 45.56941 |  |  |  |  | 6570 | 1 | 63247000ZR0318 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LA PLAINE | B163 | 2.955236 | 45.569134 |  |  |  |  | 2980 | 1 | 63247000ZR0321 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LA PLAINE | B163 | 2.955674 | 45.569028 |  |  |  |  | 576 | 1 | 63247000ZR0329 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LA PLAINE | B163 | 2.956572 | 45.569336 |  |  |  |  | 945 | 1 | 63247000ZR0332 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LA PLAINE | B163 | 2.958392 | 45.567987 |  |  |  |  | 605 | 1 | 63247000ZR0337 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LA PLAINE | B163 | 2.958635 | 45.567895 |  |  |  |  | 275 | 1 | 63247000ZR0338 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LA PLAINE | B163 | 2.958956 | 45.568081 |  |  |  |  | 4593 | 1 | 63247000ZR0339 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LA PLAINE | B163 | 2.95846 | 45.568553 |  |  |  |  | 1960 | 1 | 63247000ZR0340 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LA PLAINE | B163 | 2.958675 | 45.569245 |  |  |  |  | 1440 | 1 | 63247000ZR0344 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LA PLAINE | B163 | 2.958585 | 45.56953 |  |  |  |  | 220 | 1 | 63247000ZR0345 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LA PLAINE | B163 | 2.957537 | 45.569718 |  |  |  |  | 1800 | 1 | 63247000ZR0348 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LA PLAINE | B163 | 2.956499 | 45.569704 |  |  |  |  | 225 | 1 | 63247000ZR0352 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LA PLAINE | B163 | 2.956415 | 45.569842 |  |  |  |  | 840 | 1 | 63247000ZR0354 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LE TARTARET | B224 | 2.939192 | 45.573429 |  |  |  |  | 1640 | 1 | 63247000ZT0023 | 0 |  |  |  |  |  |  |  |  |  |  | BF | futaies feuillues |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | SUR LE LAC | B112 | 2.93253 | 45.567744 |  |  |  |  | 1540 | 1 | 63247000ZT0029 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | SUR LE LAC | B112 | 2.930487 | 45.567177 |  |  |  |  | 4570 | 1 | 63247000ZT0033 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LES SARERES | B207 | 2.932197 | 45.570867 |  |  |  |  | 11000 | 1 | 63247000ZT0054 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LES SARERES | B207 | 2.931821 | 45.572323 |  |  |  |  | 4370 | 1 | 63247000ZT0072 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LES BERNADES | B007 | 2.930502 | 45.580201 |  |  |  |  | 7240 | 1 | 63247000ZV0006 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LABERNADE | B109 | 2.936237 | 45.582518 |  |  |  |  | 4955 | 1 | 63247000ZV0013 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LABERNADE | B109 | 2.936237 | 45.582518 |  |  |  |  | 1310 | 1 | 63247000ZV0013 | 0 |  |  |  |  |  |  |  |  |  |  | PA | pâtures |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LABERNADE | B109 | 2.936237 | 45.582518 |  |  |  |  | 1355 | 1 | 63247000ZV0013 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LABERNADE | B109 | 2.940925 | 45.577609 |  |  |  |  | 3810 | 1 | 63247000ZV0018 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LES COTES | B055 | 2.936206 | 45.576677 |  |  |  |  | 4905 | 1 | 63247000ZV0058 | 0 |  |  |  |  |  |  |  |  |  |  | PA | pâtures |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | LES COTES | B055 | 2.936206 | 45.576677 |  |  |  |  | 4905 | 1 | 63247000ZV0058 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | PINIERE DE ZANAT | B160 | 2.936193 | 45.577862 |  |  |  |  | 3600 | 1 | 63247000ZV0070 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | PINIERE DE ZANAT | B160 | 2.935872 | 45.578131 |  |  |  |  | 4490 | 1 | 63247000ZV0071 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | PINIERE DE ZANAT | B160 | 2.935872 | 45.578131 |  |  |  |  | 1470 | 1 | 63247000ZV0071 | 0 |  |  |  |  |  |  |  |  |  |  | PA | pâtures |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | PINIERE DE ZANAT | B160 | 2.935308 | 45.578234 |  |  |  |  | 5890 | 1 | 63247000ZV0072 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | PINIERE DE ZANAT | B160 | 2.934458 | 45.578782 |  |  |  |  | 3240 | 1 | 63247000ZV0076 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | PINIERE DE ZANAT | B160 | 2.934228 | 45.579451 |  |  |  |  | 10490 | 1 | 63247000ZV0077 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | PINIERE DE ZANAT | B160 | 2.933189 | 45.578472 |  |  |  |  | 12620 | 1 | 63247000ZV0084 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | PINIERE DE ZANAT | B160 | 2.933189 | 45.578472 |  |  |  |  | 870 | 1 | 63247000ZV0084 | 0 |  |  |  |  |  |  |  |  |  |  | CA | carrières |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63247 | Murol | 63790 |  |  | PINIERE DE ZANAT | B160 | 2.931918 | 45.578399 |  |  |  |  | 3850 | 1 | 63247000ZV0088 | 0 |  |  |  |  |  |  |  |  |  |  | BR | futaies résineuses |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63335 | Saint-Diéry | 63320 |  |  | TRONCO | B093 | 3.007409 | 45.562513 |  |  |  |  | 20220 | 1 | 63335000ZC0003 | 0 |  |  |  |  |  |  |  |  |  |  | PA | pâtures |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63335 | Saint-Diéry | 63320 |  |  | TRONCO | B093 | 3.007409 | 45.562513 |  |  |  |  | 8120 | 1 | 63335000ZC0003 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |
| 2025-809217 | 2025-03-31 | Vente | 35000 | 63 | 63401 | Saint-Victor-la-Rivière | 63790 |  |  | GOUZAINDE | B116 | 2.925772 | 45.554636 |  |  |  |  | 5253 | 1 | 63401000ZY0005 | 0 |  |  |  |  |  |  |  |  |  |  | BT | taillis simples |

#### `2025-821070` / disposition `1` — raw rows

| id_mutation | date_mutation | nature_mutation | valeur_fonciere | code_departement | code_commune | nom_commune | code_postal | adresse_numero | adresse_suffixe | adresse_nom_voie | adresse_code_voie | longitude | latitude | code_type_local | type_local | surface_reelle_bati | nombre_pieces_principales | surface_terrain | numero_disposition | id_parcelle | nombre_lots | lot1_numero | lot1_surface_carrez | lot2_numero | lot2_surface_carrez | lot3_numero | lot3_surface_carrez | lot4_numero | lot4_surface_carrez | lot5_numero | lot5_surface_carrez | code_nature_culture | nature_culture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 21 | 1 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 25 | 1 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 36 | 2 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 36 | 2 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 23 | 1 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 36 | 2 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 28 | 1 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 32 | 2 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 32 | 2 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 18 | 1 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 32 | 2 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 28 | 1 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 79 | 3 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 98 | 4 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 60 | 2 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 76 | 3 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 79 | 3 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 98 | 4 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 60 | 2 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 18 | 1 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 36 | 2 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 76 | 3 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 23 | 1 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 36 | 2 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 36 | 2 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 25 | 1 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 75 | 3 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 4 | Local industriel. commercial ou assimilé | 46 | 0 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 26 | 1 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 32 | 2 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 32 | 2 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 32 | 2 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 23 | 0 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 30 | 1 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 18 | 1 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 21 | 1 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 43 | 2 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 28 | 0 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 29 | 0 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 36 | 2 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 25 | 1 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 23 | 0 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 21 | 1 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 30 | 1 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 26 | 1 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 28 | 1 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 32 | 2 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 32 | 2 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 32 | 2 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 18 | 1 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 36 | 2 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 23 | 1 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 36 | 2 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 36 | 2 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 25 | 1 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 23 | 1 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 30 | 1 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 32 | 1 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 38 | 1 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 38 | 1 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 33 | 1 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 24 | 0 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 26 | 1 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 30 | 1 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 43 | 2 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 28 | 2 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 42 | 2 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 25 | 1 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 27 | 1 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 23 | 1 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 22 | 1 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 33 | 1 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 25 | 1 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 46 | 2 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 23 | 1 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 35 | 2 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 32 | 1 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 33 | 1 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 26 | 1 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 30 | 1 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 21 | 1 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 23 | 1 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 26 | 1 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 28 | 1 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 32 | 2 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 32 | 2 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 32 | 2 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 36 | 2 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 23 | 1 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 36 | 2 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 22 | 1 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 44 | 2 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 168 | 4 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 75 | 3 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 4 | Local industriel. commercial ou assimilé | 46 | 0 | 930 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | S | sols |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 44 | 2 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 168 | 4 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 43 | 2 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 28 | 0 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 29 | 0 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 32 | 1 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 38 | 1 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 38 | 1 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 33 | 1 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 24 | 0 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 26 | 1 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 30 | 1 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 43 | 2 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 28 | 2 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 42 | 2 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 25 | 1 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 27 | 1 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 23 | 1 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 33 | 1 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 25 | 1 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 46 | 2 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 23 | 1 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 35 | 2 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 32 | 1 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |
| 2025-821070 | 2025-12-26 | Vente | 1458000 | 63 | 63430 | Thiers | 63300 | 20 |  | AV DE CIZOLLES | 0620 | 3.53748 | 45.846359 | 2 | Appartement | 33 | 1 | 7989 | 1 | 63430000BE0259 | 0 |  |  |  |  |  |  |  |  |  |  | AG | terrains d'agrément |

## References

- [Geolocated DVF dataset and field schema](https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres-geolocalisees/)
- [DGFiP DVF dataset and descriptive notice](https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres/)
- [Geolocated DVF transformation source](https://github.com/datagouv/dvf/blob/master/improve-csv.js)
- [Cerema: mutations, parcels, and locals](https://doc-datafoncier.cerema.fr/doc/dv3f/disposition_parcelle/iddispopar?v=1)
- [Cerema: valeur foncière](https://doc-datafoncier.cerema.fr/doc/dv3f/disposition/valeurfonc)
