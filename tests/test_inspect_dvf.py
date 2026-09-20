from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from homescope.data.inspect_dvf import (  # noqa: E402
    REQUIRED_COLUMNS,
    SchemaError,
    build_transaction_summary,
    render_report,
    run_audit,
    select_representative_groups,
    validate_schema,
)


def make_row(mutation_id: str, **overrides: object) -> dict[str, object]:
    row: dict[str, object] = {column: None for column in REQUIRED_COLUMNS}
    row.update(
        {
            "id_mutation": mutation_id,
            "date_mutation": "2025-01-10",
            "nature_mutation": "Vente",
            "valeur_fonciere": 200_000.0,
            "code_departement": "63",
            "code_commune": "63000",
            "nom_commune": "Test-sur-Dore",
            "code_postal": "63000",
            "adresse_numero": 1,
            "adresse_nom_voie": "RUE DU TEST",
            "adresse_code_voie": "0001",
            "longitude": 3.0,
            "latitude": 45.0,
            "numero_disposition": 1,
            "id_parcelle": "63000000AA0001",
            "nombre_lots": 0,
        }
    )
    row.update(overrides)
    return row


@pytest.fixture()
def synthetic_dvf() -> pd.DataFrame:
    rows = [
        make_row(
            "apt-dep",
            code_type_local=2,
            type_local="Appartement",
            surface_reelle_bati=50.0,
            nombre_pieces_principales=2,
            nombre_lots=1,
            lot1_numero="10",
            lot1_surface_carrez=49.0,
        ),
        make_row(
            "apt-dep",
            code_type_local=3,
            type_local="Dépendance",
            nombre_lots=1,
            lot1_numero="11",
        ),
        make_row(
            "house-expanded",
            code_type_local=1,
            type_local="Maison",
            surface_reelle_bati=100.0,
            nombre_pieces_principales=4,
            code_nature_culture="S",
            nature_culture="sols",
            surface_terrain=300.0,
        ),
        make_row(
            "house-expanded",
            code_type_local=1,
            type_local="Maison",
            surface_reelle_bati=100.0,
            nombre_pieces_principales=4,
            code_nature_culture="J",
            nature_culture="jardins",
            surface_terrain=200.0,
        ),
        make_row(
            "conflict",
            valeur_fonciere=100_000.0,
            code_type_local=1,
            type_local="Maison",
            surface_reelle_bati=80.0,
        ),
        make_row(
            "conflict",
            valeur_fonciere=120_000.0,
            code_type_local=3,
            type_local="Dépendance",
        ),
        make_row(
            "mixed",
            code_type_local=1,
            type_local="Maison",
            surface_reelle_bati=70.0,
        ),
        make_row(
            "mixed",
            code_type_local=2,
            type_local="Appartement",
            surface_reelle_bati=45.0,
            id_parcelle="63000000AA0002",
            adresse_numero=2,
            longitude=3.01,
        ),
        make_row(
            "mixed",
            code_type_local=4,
            type_local="Local industriel. commercial ou assimilé",
            surface_reelle_bati=30.0,
            id_parcelle="63000000AA0002",
            adresse_numero=2,
            longitude=3.01,
        ),
        make_row(
            "land-only",
            valeur_fonciere=None,
            code_nature_culture="T",
            nature_culture="terres",
            surface_terrain=500.0,
            adresse_numero=None,
        ),
        make_row(
            "land-only",
            valeur_fonciere=None,
            code_nature_culture="P",
            nature_culture="prés",
            surface_terrain=700.0,
            id_parcelle="63000000AA0003",
            code_commune="63001",
            nom_commune="Autre-sur-Dore",
            adresse_numero=None,
            adresse_nom_voie="LE BOURG",
            longitude=3.02,
        ),
        # Same source ID and value, but distinct legal dispositions.
        make_row(
            "split-dispositions",
            numero_disposition=1,
            valeur_fonciere=13_440.0,
            code_type_local=2,
            type_local="Appartement",
            surface_reelle_bati=75.0,
        ),
        make_row(
            "split-dispositions",
            numero_disposition=2,
            valeur_fonciere=13_440.0,
            code_type_local=4,
            type_local="Local industriel. commercial ou assimilé",
            surface_reelle_bati=110.0,
        ),
    ]
    return pd.DataFrame(rows, columns=REQUIRED_COLUMNS)


def test_schema_validation_reports_missing_and_allows_additional_columns() -> None:
    with pytest.raises(SchemaError, match="latitude"):
        validate_schema([column for column in REQUIRED_COLUMNS if column != "latitude"])

    missing, unexpected = validate_schema([*REQUIRED_COLUMNS, "source_extra"])
    assert missing == []
    assert unexpected == ["source_extra"]


def test_summary_does_not_sum_repeated_prices_or_surfaces(
    synthetic_dvf: pd.DataFrame,
) -> None:
    summary, threshold = build_transaction_summary(synthetic_dvf)

    apartment = summary.loc[("apt-dep", 1)]
    assert apartment["row_count"] == 2
    assert apartment["transaction_value"] == 200_000.0
    assert apartment["distinct_value_count"] == 1
    assert bool(apartment["flag_repeated_value"])
    assert apartment["distinct_residential_signature_count"] == 1

    house = summary.loc[("house-expanded", 1)]
    assert house["residential_row_count"] == 2
    assert house["distinct_residential_signature_count"] == 1
    assert bool(house["flag_repeated_residential_signature"])
    assert house["terrain_row_count"] == 2
    assert house["distinct_land_segment_count"] == 2
    assert threshold == 10


def test_conflicts_and_complex_groups_are_flagged(synthetic_dvf: pd.DataFrame) -> None:
    summary, _ = build_transaction_summary(synthetic_dvf)

    conflict = summary.loc[("conflict", 1)]
    assert conflict["distinct_value_count"] == 2
    assert pd.isna(conflict["transaction_value"])
    assert bool(conflict["flag_conflicting_values"])

    mixed = summary.loc[("mixed", 1)]
    assert bool(mixed["flag_multiple_primary_dwellings"])
    assert bool(mixed["flag_mixed_house_apartment"])
    assert bool(mixed["flag_residential_commercial"])
    assert bool(mixed["flag_multiple_parcels"])
    assert bool(mixed["flag_multiple_addresses"])

    land = summary.loc[("land-only", 1)]
    assert bool(land["flag_land_only"])
    assert bool(land["flag_missing_value"])
    assert bool(land["flag_multiple_communes"])


def test_dispositions_are_separate_legal_units(synthetic_dvf: pd.DataFrame) -> None:
    summary, _ = build_transaction_summary(synthetic_dvf)

    apartment = summary.loc[("split-dispositions", 1)]
    commercial = summary.loc[("split-dispositions", 2)]
    assert len(summary) == 7
    assert apartment["apartment_row_count"] == 1
    assert apartment["commercial_row_count"] == 0
    assert commercial["apartment_row_count"] == 0
    assert commercial["commercial_row_count"] == 1
    assert bool(apartment["flag_parent_multiple_dispositions"])
    assert bool(commercial["flag_parent_multiple_dispositions"])
    assert not bool(apartment["flag_residential_commercial"])


def test_selection_is_deterministic(synthetic_dvf: pd.DataFrame) -> None:
    summary, _ = build_transaction_summary(synthetic_dvf)
    first = select_representative_groups(summary, samples_per_case=2)
    second = select_representative_groups(summary, samples_per_case=2)

    assert first == second
    assert first["Apartment with dependencies"] == [("apt-dep", 1)]
    assert first["House repeated across expanded rows"] == [("house-expanded", 1)]


def test_report_contains_raw_groups_and_provisional_rules(
    synthetic_dvf: pd.DataFrame,
) -> None:
    summary, threshold = build_transaction_summary(synthetic_dvf)
    report = render_report(
        frame=synthetic_dvf,
        summary=summary,
        input_path=Path("data/raw/synthetic.csv.gz"),
        input_sha256="abc123",
        unexpected_columns=[],
        samples_per_case=1,
        large_group_threshold=threshold,
    )

    assert "# DVF multi-row legal transaction audit" in report
    assert "`apt-dep` / disposition `1` — raw rows" in report
    assert "(`id_mutation`, `numero_disposition`)" in report
    assert "never sum repeated row values" in report
    assert "price_per_m2" in report
    assert "49" in report


def test_audit_refuses_to_overwrite_its_input(tmp_path: Path) -> None:
    input_path = tmp_path / "dvf.csv"
    with pytest.raises(ValueError, match="must not overwrite"):
        run_audit(input_path, input_path)
