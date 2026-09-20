## 1. Format du dataset

Le fichier utilisé est :

```text
data/raw/dvf_63_2025.csv.gz
```

C’est un fichier :

- CSV compressé avec gzip ;
- encodé en UTF-8 ;
- séparé par des virgules ;
- lisible directement avec pandas, sans le décompresser.

```python
import pandas as pd

df = pd.read_csv(
    "data/raw/dvf_63_2025.csv.gz",
    dtype={
        "code_departement": "string",
        "code_commune": "string",
        "code_postal": "string",
        "adresse_code_voie": "string",
        "id_parcelle": "string",
    },
    parse_dates=["date_mutation"],
    low_memory=False,
)
```

## 2. Que représente une ligne ?

Une ligne ne représente pas forcément une vente complète.

La structure est plutôt :

```text
id_mutation
└── numero_disposition      ← unité juridique de transaction
    ├── logement
    ├── dépendance
    ├── lot de copropriété
    ├── parcelle
    └── type de terrain
```

Notre identifiant de transaction est donc :

```python
transaction_key = ["id_mutation", "numero_disposition"]
```

Plusieurs lignes peuvent partager la même valeur foncière. Il ne faut jamais les additionner directement.

### Exemple visuel

```text
id_mutation = 2025-804964
└── disposition 1 — valeur foncière : 51 000 €
    ├── ligne 1 : Appartement, 31 m²
    ├── ligne 2 : Dépendance
    └── ligne 3 : Dépendance
```

Ces trois lignes représentent une seule transaction juridique :

```text
Clé : (2025-804964, 1)
Prix : 51 000 € pris une seule fois
Surface principale : 31 m²
Prix/m² : 51 000 ÷ 31 ≈ 1 645 €/m²
```

Un même `id_mutation` peut aussi contenir plusieurs dispositions :

```text
id_mutation = 2025-810587
├── disposition 1 : Appartement
└── disposition 2 : Local commercial
```

Cela représente deux transactions juridiques distinctes :

```text
(2025-810587, 1)
(2025-810587, 2)
```

La hiérarchie à retenir est donc :

```text
id_mutation
    ↓
numero_disposition
    ↓
une ou plusieurs lignes décrivant les biens vendus
```

## 3. Colonnes principales

| Catégorie | Colonnes | Utilisation |
|---|---|---|
| Transaction | `id_mutation`, `numero_disposition` | Identifier la transaction juridique |
| Date | `date_mutation` | Année, mois, évolution des prix |
| Type de transaction | `nature_mutation` | Vente, VEFA, échange, adjudication… |
| Prix | `valeur_fonciere` | Prix déclaré pour la disposition |
| Localisation | `code_departement`, `code_commune`, `nom_commune`, `code_postal` | Statistiques départementales et communales |
| Adresse | `adresse_numero`, `adresse_suffixe`, `adresse_nom_voie`, `adresse_code_voie` | Affichage et recherche d’adresse |
| Parcelle | `id_parcelle` | Relier les lignes cadastrales |
| Coordonnées | `longitude`, `latitude` | Carte et recherche de transactions proches |
| Type de bien | `code_type_local`, `type_local` | Maison, appartement, dépendance ou commerce |
| Caractéristiques | `surface_reelle_bati`, `nombre_pieces_principales` | Calcul du prix au m² et estimation |
| Terrain | `surface_terrain`, `code_nature_culture`, `nature_culture` | Surface et nature cadastrale du terrain |
| Copropriété | `nombre_lots`, `lot1_*` à `lot5_*` | Identifier les lots et surfaces Carrez |

## 4. Codes des locaux

| Code | Type |
|---:|---|
| 1 | Maison |
| 2 | Appartement |
| 3 | Dépendance |
| 4 | Local industriel ou commercial |

Une dépendance peut être un garage, une cave ou un parking. Elle accompagne souvent un logement, mais ne doit pas être comptée comme un second logement.

## 5. Surfaces

### `surface_reelle_bati`

Surface intérieure du local, mesurée au sol. C’est généralement la surface à utiliser pour le prix au m².

### `lot1_surface_carrez` à `lot5_surface_carrez`

Surfaces Carrez déclarées pour les lots de copropriété. Elles sont surtout utiles pour les appartements.

### `surface_terrain`

Surface cadastrale du terrain. Elle ne doit pas être utilisée comme dénominateur du prix au m² bâti.

## 6. Calcul d’un prix au m²

Pour une transaction simple :

```text
price_per_m2 =
valeur_fonciere unique
÷
surface_reelle_bati d’un seul logement
```

Avant ce calcul, il faut vérifier que la disposition contient :

- exactement une maison ou un appartement identifiable ;
- une seule valeur foncière ;
- aucune propriété commerciale ;
- une surface bâtie valide ;
- éventuellement des dépendances, mais sans ajouter leur surface.

Les ventes contenant plusieurs logements doivent être exclues ou traitées séparément.

## 7. Utilisation dans HomeScope

### Vue France

Regrouper les transactions nettoyées par :

```text
année + département/commune + maison/appartement
```

Puis calculer médiane, moyenne, quartiles et nombre de transactions.

### Exploration locale

Utiliser `latitude` et `longitude` pour trouver les transactions dans un rayon de 500 m ou 1 km.

Attention : ces coordonnées représentent généralement le centre de la parcelle, pas précisément l’entrée du logement.

### Estimation immobilière

Utiliser comme variables :

- type de logement ;
- surface bâtie ;
- nombre de pièces ;
- surface du terrain ;
- latitude et longitude ;
- commune et code postal ;
- date de vente ;
- statistiques des ventes voisines.

Le prix cible sera `valeur_fonciere`, uniquement après avoir sélectionné les transactions simples et fiables.

Les exemples réels et les cas problématiques sont visibles dans le [rapport d’audit](C:/Users/ayoub/Desktop/HomeScope/reports/dvf_mutation_audit_63_2025.md).
