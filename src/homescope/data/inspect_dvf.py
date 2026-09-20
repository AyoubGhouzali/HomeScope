"""Audit the legal transaction structure of a geolocated DVF extract.

This module deliberately does not create a cleaned dataset or calculate a price
per square metre. It describes how rows repeat within the legal transaction
unit ``(id_mutation, numero_disposition)`` so that cleaning rules can be
reviewed before they are implemented.
"""

from __future__ import annotations

import argparse
import hashlib
import math
from collections import OrderedDict
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import pandas as pd


DEFAULT_INPUT = Path("data/raw/dvf_63_2025.csv.gz")
DEFAULT_REPORT = Path("reports/dvf_mutation_audit_63_2025.md")

REQUIRED_COLUMNS = [
    "id_mutation",
    "date_mutation",
    "nature_mutation",
    "valeur_fonciere",
    "code_departement",
    "code_commune",
    "nom_commune",
    "code_postal",
    "adresse_numero",
    "adresse_suffixe",
    "adresse_nom_voie",
    "adresse_code_voie",
    "longitude",
    "latitude",
    "code_type_local",
    "type_local",
    "surface_reelle_bati",
    "nombre_pieces_principales",
    "surface_terrain",
    "numero_disposition",
    "id_parcelle",
    "nombre_lots",
    "lot1_numero",
    "lot1_surface_carrez",
    "lot2_numero",
    "lot2_surface_carrez",
    "lot3_numero",
    "lot3_surface_carrez",
    "lot4_numero",
    "lot4_surface_carrez",
    "lot5_numero",
    "lot5_surface_carrez",
    "code_nature_culture",
    "nature_culture",
]

ADDRESS_SIGNATURE_COLUMNS = [
    "adresse_numero",
    "adresse_suffixe",
    "adresse_nom_voie",
    "adresse_code_voie",
]
COORDINATE_SIGNATURE_COLUMNS = ["longitude", "latitude"]
LOT_SIGNATURE_COLUMNS = [
    "lot1_numero",
    "lot1_surface_carrez",
    "lot2_numero",
    "lot2_surface_carrez",
    "lot3_numero",
    "lot3_surface_carrez",
    "lot4_numero",
    "lot4_surface_carrez",
    "lot5_numero",
    "lot5_surface_carrez",
]
RESIDENTIAL_SIGNATURE_COLUMNS = [
    "id_parcelle",
    *ADDRESS_SIGNATURE_COLUMNS,
    "code_type_local",
    "surface_reelle_bati",
    "nombre_pieces_principales",
    *LOT_SIGNATURE_COLUMNS,
]
LAND_SIGNATURE_COLUMNS = [
    "id_parcelle",
    "code_nature_culture",
    "nature_culture",
    "surface_terrain",
]

LOCAL_TYPE_NAMES = {
    1: "house_row_count",
    2: "apartment_row_count",
    3: "dependency_row_count",
    4: "commercial_row_count",
}

TRANSACTION_KEY_COLUMNS = ["id_mutation", "numero_disposition"]

SUMMARY_COLUMNS = [
    "row_count",
    "parent_disposition_count",
    "parcel_count",
    "commune_count",
    "address_count",
    "coordinate_count",
    "non_null_value_count",
    "distinct_value_count",
    "transaction_value",
    "house_row_count",
    "apartment_row_count",
    "dependency_row_count",
    "commercial_row_count",
    "residential_row_count",
    "distinct_residential_signature_count",
    "terrain_row_count",
    "distinct_land_segment_count",
]


class SchemaError(ValueError):
    """Raised when a DVF input is missing a required audit column."""


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit repeated rows within geolocated DVF dispositions."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Raw DVF CSV or CSV.GZ file (default: {DEFAULT_INPUT}).",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT,
        help=f"Markdown report to create (default: {DEFAULT_REPORT}).",
    )
    parser.add_argument(
        "--samples-per-case",
        type=positive_int,
        default=3,
        help="Number of deterministic mutation examples per case (default: 3).",
    )
    return parser.parse_args(argv)


def validate_schema(columns: Iterable[str]) -> tuple[list[str], list[str]]:
    actual = list(columns)
    missing = [column for column in REQUIRED_COLUMNS if column not in actual]
    unexpected = [column for column in actual if column not in REQUIRED_COLUMNS]
    if missing:
        raise SchemaError(
            "DVF input is missing required columns: " + ", ".join(missing)
        )
    return missing, unexpected


def load_dvf(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"DVF input not found: {path}")
    frame = pd.read_csv(path, low_memory=False)
    validate_schema(frame.columns)
    return frame


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _distinct_row_count(
    frame: pd.DataFrame,
    signature_columns: Sequence[str],
    mask: pd.Series | None = None,
) -> pd.Series:
    if mask is None:
        mask = frame.loc[:, signature_columns].notna().any(axis=1)
    subset = frame.loc[
        mask, [*TRANSACTION_KEY_COLUMNS, *signature_columns]
    ].drop_duplicates()
    if subset.empty:
        return pd.Series(dtype="int64")
    return subset.groupby(TRANSACTION_KEY_COLUMNS, dropna=False).size()


def build_transaction_summary(frame: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Return one audit row per legal transaction unit and the size threshold.

    The operational legal unit is ``(id_mutation, numero_disposition)``. The
    DGFiP notice defines a disposition as the legal analysis unit carrying a
    declared value, while ``id_mutation`` is a derived geolocated-DVF grouping
    identifier.
    """

    validate_schema(frame.columns)
    grouped = frame.groupby(TRANSACTION_KEY_COLUMNS, sort=True, dropna=False)
    summary = grouped.agg(
        row_count=("id_mutation", "size"),
        parcel_count=("id_parcelle", "nunique"),
        commune_count=("code_commune", "nunique"),
        non_null_value_count=("valeur_fonciere", "count"),
        distinct_value_count=("valeur_fonciere", "nunique"),
        first_value=("valeur_fonciere", "first"),
        terrain_row_count=("nature_culture", "count"),
    )

    parent_disposition_counts = frame.groupby(
        "id_mutation", dropna=False
    )["numero_disposition"].nunique(dropna=False)
    summary["parent_disposition_count"] = summary.index.get_level_values(
        "id_mutation"
    ).map(parent_disposition_counts)

    summary["address_count"] = _distinct_row_count(
        frame, ADDRESS_SIGNATURE_COLUMNS
    ).reindex(summary.index, fill_value=0)
    summary["coordinate_count"] = _distinct_row_count(
        frame, COORDINATE_SIGNATURE_COLUMNS
    ).reindex(summary.index, fill_value=0)

    local_codes = pd.to_numeric(frame["code_type_local"], errors="coerce")
    for code, column in LOCAL_TYPE_NAMES.items():
        summary[column] = (
            local_codes.eq(code)
            .groupby(
                [frame[column] for column in TRANSACTION_KEY_COLUMNS],
                dropna=False,
            )
            .sum()
            .reindex(summary.index, fill_value=0)
            .astype("int64")
        )

    summary["residential_row_count"] = (
        summary["house_row_count"] + summary["apartment_row_count"]
    )
    residential_mask = local_codes.isin([1, 2])
    summary["distinct_residential_signature_count"] = _distinct_row_count(
        frame, RESIDENTIAL_SIGNATURE_COLUMNS, residential_mask
    ).reindex(summary.index, fill_value=0)

    terrain_mask = frame["nature_culture"].notna()
    summary["distinct_land_segment_count"] = _distinct_row_count(
        frame, LAND_SIGNATURE_COLUMNS, terrain_mask
    ).reindex(summary.index, fill_value=0)

    summary["transaction_value"] = summary["first_value"].where(
        summary["distinct_value_count"].eq(1)
    )
    summary = summary.drop(columns="first_value")

    group_q99 = summary["row_count"].quantile(0.99)
    large_group_threshold = max(10, int(math.ceil(group_q99)))

    summary["flag_repeated_value"] = summary["non_null_value_count"].gt(
        summary["distinct_value_count"]
    )
    summary["flag_conflicting_values"] = summary["distinct_value_count"].gt(1)
    summary["flag_missing_value"] = summary["non_null_value_count"].eq(0)
    summary["flag_repeated_residential_signature"] = summary[
        "residential_row_count"
    ].gt(summary["distinct_residential_signature_count"])
    summary["flag_multiple_primary_dwellings"] = summary[
        "distinct_residential_signature_count"
    ].gt(1)
    summary["flag_mixed_house_apartment"] = summary["house_row_count"].gt(
        0
    ) & summary["apartment_row_count"].gt(0)
    summary["flag_residential_commercial"] = summary[
        "residential_row_count"
    ].gt(0) & summary["commercial_row_count"].gt(0)
    summary["flag_parent_multiple_dispositions"] = summary[
        "parent_disposition_count"
    ].gt(1)
    summary["flag_multiple_parcels"] = summary["parcel_count"].gt(1)
    summary["flag_multiple_communes"] = summary["commune_count"].gt(1)
    summary["flag_multiple_addresses"] = summary["address_count"].gt(1)
    summary["flag_multiple_coordinates"] = summary["coordinate_count"].gt(1)
    summary["flag_repeated_land_segment"] = summary["terrain_row_count"].gt(
        summary["distinct_land_segment_count"]
    )
    summary["flag_land_only"] = summary["terrain_row_count"].gt(0) & summary[
        "residential_row_count"
    ].eq(0) & summary["commercial_row_count"].eq(0)
    summary["flag_unusually_large"] = summary["row_count"].gt(
        large_group_threshold
    )

    ordered_columns = SUMMARY_COLUMNS + [
        column for column in summary.columns if column.startswith("flag_")
    ]
    return summary.loc[:, ordered_columns], large_group_threshold


def build_case_masks(summary: pd.DataFrame) -> "OrderedDict[str, pd.Series]":
    return OrderedDict(
        [
            (
                "Apartment with dependencies",
                summary["apartment_row_count"].gt(0)
                & summary["house_row_count"].eq(0)
                & summary["dependency_row_count"].gt(0),
            ),
            (
                "House repeated across expanded rows",
                summary["house_row_count"].gt(0)
                & summary["flag_repeated_residential_signature"]
                & summary["terrain_row_count"].gt(0),
            ),
            (
                "Multiple primary dwellings",
                summary["flag_multiple_primary_dwellings"],
            ),
            ("Mixed house and apartment", summary["flag_mixed_house_apartment"]),
            (
                "Residential and commercial premises",
                summary["flag_residential_commercial"],
            ),
            (
                "Parent ID with multiple dispositions",
                summary["flag_parent_multiple_dispositions"],
            ),
            (
                "Multiple geographies within one disposition",
                summary["flag_multiple_parcels"]
                | summary["flag_multiple_addresses"]
                | summary["flag_multiple_communes"],
            ),
            ("Land-only mutation", summary["flag_land_only"]),
            ("Missing transaction value", summary["flag_missing_value"]),
            ("Unusually large mutation", summary["flag_unusually_large"]),
        ]
    )


def select_representative_groups(
    summary: pd.DataFrame, samples_per_case: int
) -> "OrderedDict[str, list[object]]":
    if samples_per_case < 1:
        raise ValueError("samples_per_case must be at least 1")

    selected: "OrderedDict[str, list[object]]" = OrderedDict()
    for case_name, mask in build_case_masks(summary).items():
        candidates = summary.loc[mask].copy()
        ascending = case_name != "Unusually large mutation"
        candidates["_id_sort"] = candidates.index.map(
            lambda key: "|".join(str(part) for part in key)
        )
        candidates = candidates.sort_values(
            ["row_count", "_id_sort"],
            ascending=[ascending, True],
            kind="stable",
        )
        selected[case_name] = candidates.head(samples_per_case).index.tolist()
    return selected


def _format_cell(value: object) -> str:
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return str(value).replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def dataframe_to_markdown(frame: pd.DataFrame) -> str:
    columns = [str(column) for column in frame.columns]
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    rows = []
    for values in frame.itertuples(index=False, name=None):
        rows.append("| " + " | ".join(_format_cell(value) for value in values) + " |")
    return "\n".join([header, separator, *rows])


def _count_table(summary: pd.DataFrame, flags: Mapping[str, str]) -> pd.DataFrame:
    total = len(summary)
    rows = []
    for column, label in flags.items():
        count = int(summary[column].sum())
        rows.append(
            {
                "Condition": label,
                "Legal transaction units": count,
                "Share": f"{(100 * count / total):.1f}%" if total else "0.0%",
            }
        )
    return pd.DataFrame(rows)


def _group_size_bands(summary: pd.DataFrame) -> pd.DataFrame:
    sizes = summary["row_count"]
    bands = OrderedDict(
        [
            ("1", sizes.eq(1)),
            ("2", sizes.eq(2)),
            ("3", sizes.eq(3)),
            ("4", sizes.eq(4)),
            ("5–9", sizes.between(5, 9)),
            ("10–24", sizes.between(10, 24)),
            ("25+", sizes.ge(25)),
        ]
    )
    return pd.DataFrame(
        {
            "Rows per legal unit": list(bands),
            "Legal transaction units": [
                int(value.sum()) for value in bands.values()
            ],
        }
    )


def render_report(
    frame: pd.DataFrame,
    summary: pd.DataFrame,
    input_path: Path,
    input_sha256: str,
    unexpected_columns: Sequence[str],
    samples_per_case: int,
    large_group_threshold: int,
) -> str:
    selections = select_representative_groups(summary, samples_per_case)
    multi_group_count = int(summary["row_count"].gt(1).sum())
    multi_row_count = int(summary.loc[summary["row_count"].gt(1), "row_count"].sum())
    source_id_count = frame["id_mutation"].nunique(dropna=False)
    parent_disposition_counts = frame.groupby("id_mutation", dropna=False)[
        "numero_disposition"
    ].nunique(dropna=False)
    multi_disposition_id_count = int(parent_disposition_counts.gt(1).sum())

    flag_labels = OrderedDict(
        [
            ("flag_repeated_value", "Value repeated across rows"),
            ("flag_conflicting_values", "Conflicting non-null values"),
            ("flag_missing_value", "Missing transaction value"),
            ("flag_repeated_residential_signature", "Repeated residential signature"),
            ("flag_multiple_primary_dwellings", "Multiple primary dwelling signatures"),
            ("flag_mixed_house_apartment", "Mixed house and apartment"),
            ("flag_residential_commercial", "Residential and commercial premises"),
            (
                "flag_parent_multiple_dispositions",
                "Parent id_mutation contains multiple dispositions",
            ),
            ("flag_multiple_parcels", "Multiple parcels"),
            ("flag_multiple_addresses", "Multiple addresses"),
            ("flag_multiple_communes", "Multiple communes"),
            ("flag_repeated_land_segment", "Repeated land segment"),
            ("flag_land_only", "Land only"),
            ("flag_unusually_large", "Unusually large group"),
        ]
    )

    lines = [
        "# DVF multi-row legal transaction audit",
        "",
        "> This is an inspection artifact, not a cleaned dataset. No price-per-m²",
        "> value is calculated here.",
        "",
        "## Source and schema",
        "",
        f"- Input: `{input_path.as_posix()}`",
        f"- SHA-256: `{input_sha256}`",
        f"- Raw rows: **{len(frame):,}**",
        f"- Distinct source `id_mutation` groups: **{source_id_count:,}**",
        f"- Legal transaction units (`id_mutation`, `numero_disposition`): **{len(summary):,}**",
        f"- Source IDs containing multiple dispositions: **{multi_disposition_id_count:,}**",
        f"- Legal units with multiple rows: **{multi_group_count:,}**",
        f"- Rows belonging to multi-row legal units: **{multi_row_count:,}**",
        f"- Required retained columns present: **{len(REQUIRED_COLUMNS)}/{len(REQUIRED_COLUMNS)}**",
        "- Missing required columns: none",
        "- Additional source columns retained by the raw file: "
        + (", ".join(f"`{column}`" for column in unexpected_columns) or "none"),
        "",
        "The audit reads every source column and does not rewrite or reduce the raw file. "
        "Following the DGFiP notice, the operational legal transaction unit is the pair "
        "`(id_mutation, numero_disposition)`, because each disposition is a legal analysis "
        "unit carrying a declared value. The geolocated `id_mutation` remains parent metadata.",
        "",
        "## Group structure",
        "",
        dataframe_to_markdown(_group_size_bands(summary)),
        "",
        f"A legal unit is marked unusually large when it has more than **{large_group_threshold}** rows "
        "(the greater of 10 and the rounded-up 99th percentile).",
        "",
        dataframe_to_markdown(_count_table(summary, flag_labels)),
        "",
        "## Initial observations",
        "",
        "- `valeur_fonciere` is commonly copied onto several rows in one disposition. "
        "The audit exposes one `transaction_value` only when the legal unit has exactly one distinct non-null value; it never sums row values.",
        "- A source `id_mutation` can contain several dispositions. Those dispositions are "
        "audited independently and are never merged merely because their date and value match.",
        "- A residential row may be expanded across land-use or lot rows. "
        "A residential signature therefore includes parcel, full address, local type, built surface, rooms, and all five lot number/surface pairs.",
        "- Repeated signatures remain explicitly flagged. They are evidence of row expansion, "
        "but the flattened extract alone cannot prove that two otherwise identical units are the same property.",
        "- Dependencies may accompany a dwelling without representing another dwelling. "
        "Commercial premises and multiple distinct dwelling signatures make a disposition unsuitable for a simple residential €/m² calculation.",
        "- Land segments can also repeat once per local. Future terrain totals must first deduplicate "
        "parcel, culture code/name, and terrain surface combinations.",
        "",
        "## Cleaning decision matrix",
        "",
        dataframe_to_markdown(
            pd.DataFrame(
                [
                    {
                        "Situation": "Transaction count",
                        "Provisional rule": "Count distinct (id_mutation, numero_disposition) pairs, never raw rows or id_mutation alone.",
                    },
                    {
                        "Situation": "One distinct non-null transaction value",
                        "Provisional rule": "Use that value once for the disposition; never sum repeated row values.",
                    },
                    {
                        "Situation": "Parent ID with several dispositions",
                        "Provisional rule": "Audit and count each disposition separately; retain id_mutation only as source grouping metadata.",
                    },
                    {
                        "Situation": "Conflicting or missing transaction values",
                        "Provisional rule": "Quarantine from price analysis pending review.",
                    },
                    {
                        "Situation": "One dwelling plus dependencies",
                        "Provisional rule": "Keep as a candidate; dependencies do not contribute built surface.",
                    },
                    {
                        "Situation": "Repeated dwelling signature",
                        "Provisional rule": "Do not sum surfaces; inspect or conservatively exclude until identity is resolved.",
                    },
                    {
                        "Situation": "Multiple dwellings or mixed house/apartment",
                        "Provisional rule": "Exclude from the simple comparable-sale dataset or model separately.",
                    },
                    {
                        "Situation": "Residential plus commercial premises",
                        "Provisional rule": "Exclude from residential €/m² calculations.",
                    },
                    {
                        "Situation": "Terrain surface",
                        "Provisional rule": "Deduplicate land signatures before aggregation; never use terrain in the built €/m² denominator.",
                    },
                    {
                        "Situation": "price_per_m2",
                        "Provisional rule": "Do not calculate until the mutation rules are reviewed and accepted.",
                    },
                ]
            )
        ),
        "",
        "## Representative legal transaction units",
        "",
        "Samples are selected deterministically by group size, `id_mutation`, and "
        "`numero_disposition`. Every raw row and every required retained field is shown "
        "for each selected legal unit.",
        "",
    ]

    summary_display_columns = [
        "row_count",
        "parent_disposition_count",
        "parcel_count",
        "commune_count",
        "address_count",
        "coordinate_count",
        "distinct_value_count",
        "transaction_value",
        "house_row_count",
        "apartment_row_count",
        "dependency_row_count",
        "commercial_row_count",
        "distinct_residential_signature_count",
        "terrain_row_count",
    ]

    for case_name, transaction_keys in selections.items():
        lines.extend([f"### {case_name}", ""])
        if not transaction_keys:
            lines.extend(["No matching legal unit was found in this extract.", ""])
            continue

        case_summary = summary.loc[
            transaction_keys, summary_display_columns
        ].reset_index()
        lines.extend([dataframe_to_markdown(case_summary), ""])
        for mutation_id, disposition_number in transaction_keys:
            id_mask = (
                frame["id_mutation"].isna()
                if pd.isna(mutation_id)
                else frame["id_mutation"].eq(mutation_id)
            )
            disposition_mask = (
                frame["numero_disposition"].isna()
                if pd.isna(disposition_number)
                else frame["numero_disposition"].eq(disposition_number)
            )
            raw_group = frame.loc[id_mask & disposition_mask, REQUIRED_COLUMNS]
            lines.extend(
                [
                    f"#### `{_format_cell(mutation_id)}` / disposition "
                    f"`{_format_cell(disposition_number)}` — raw rows",
                    "",
                    dataframe_to_markdown(raw_group),
                    "",
                ]
            )

    lines.extend(
        [
            "## References",
            "",
            "- [Geolocated DVF dataset and field schema](https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres-geolocalisees/)",
            "- [DGFiP DVF dataset and descriptive notice](https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres/)",
            "- [Geolocated DVF transformation source](https://github.com/datagouv/dvf/blob/master/improve-csv.js)",
            "- [Cerema: mutations, parcels, and locals](https://doc-datafoncier.cerema.fr/doc/dv3f/disposition_parcelle/iddispopar?v=1)",
            "- [Cerema: valeur foncière](https://doc-datafoncier.cerema.fr/doc/dv3f/disposition/valeurfonc)",
            "",
        ]
    )
    return "\n".join(lines)


def run_audit(
    input_path: Path, report_path: Path, samples_per_case: int = 3
) -> pd.DataFrame:
    if input_path.resolve() == report_path.resolve():
        raise ValueError("The report path must not overwrite the DVF input file.")
    frame = load_dvf(input_path)
    _, unexpected = validate_schema(frame.columns)
    summary, large_group_threshold = build_transaction_summary(frame)
    report = render_report(
        frame=frame,
        summary=summary,
        input_path=input_path,
        input_sha256=sha256_file(input_path),
        unexpected_columns=unexpected,
        samples_per_case=samples_per_case,
        large_group_threshold=large_group_threshold,
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    return summary


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        summary = run_audit(args.input, args.report, args.samples_per_case)
    except (FileNotFoundError, SchemaError, ValueError, pd.errors.ParserError) as exc:
        print(f"Audit failed: {exc}")
        return 1

    multi_groups = int(summary["row_count"].gt(1).sum())
    print(
        f"Audited {len(summary):,} legal transaction units; "
        f"{multi_groups:,} have multiple rows."
    )
    print(f"Report written to: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
