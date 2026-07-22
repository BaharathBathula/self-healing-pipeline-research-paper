"""Compare an independent reproduction with the preserved reference CSV."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd


ALIGNMENT_KEY = "trial_id"
NONDETERMINISTIC_COLUMNS = {"runtime_milliseconds"}
OUTCOME_COLUMNS = (
    "failure_detected",
    "detection_correct",
    "classification_correct",
    "remediation_executed",
    "human_approval_required",
    "cycle_status",
    "recovery_verified",
    "checksum_restored",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compare a reproduced combined experiment CSV against the "
            "preserved reference result."
        )
    )
    parser.add_argument(
        "--reference",
        type=Path,
        required=True,
        help="Path to the preserved reference combined CSV.",
    )
    parser.add_argument(
        "--reproduced",
        type=Path,
        required=True,
        help="Path to the reproduced combined CSV.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        required=True,
        help="Path for the text comparison report.",
    )
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def normalized_value(value: Any) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, bool):
        return str(value)
    return str(value)


def value_counts_as_text(series: pd.Series) -> dict[str, int]:
    normalized = series.map(normalized_value)
    counts = normalized.value_counts(dropna=False).sort_index()
    return {str(key): int(value) for key, value in counts.items()}


def runtime_statistics(series: pd.Series) -> dict[str, float]:
    numeric = pd.to_numeric(series, errors="coerce").dropna()
    if numeric.empty:
        return {}
    return {
        "count": float(numeric.count()),
        "minimum": float(numeric.min()),
        "mean": float(numeric.mean()),
        "median": float(numeric.median()),
        "maximum": float(numeric.max()),
    }


def main() -> int:
    args = parse_args()
    reference_path = args.reference.resolve()
    reproduced_path = args.reproduced.resolve()
    report_path = args.report.resolve()

    for path in (reference_path, reproduced_path):
        if not path.is_file():
            raise FileNotFoundError(f"CSV was not found: {path}")

    reference = pd.read_csv(reference_path)
    reproduced = pd.read_csv(reproduced_path)

    lines: list[str] = []
    failures: list[str] = []

    def section(title: str) -> None:
        lines.append("")
        lines.append("=" * 72)
        lines.append(title)
        lines.append("=" * 72)

    section("FILE IDENTITY")
    lines.append(f"Reference: {reference_path}")
    lines.append(f"Reference size: {reference_path.stat().st_size}")
    lines.append(f"Reference SHA256: {sha256(reference_path)}")
    lines.append(f"Reproduced: {reproduced_path}")
    lines.append(f"Reproduced size: {reproduced_path.stat().st_size}")
    lines.append(f"Reproduced SHA256: {sha256(reproduced_path)}")

    section("SCHEMA VALIDATION")
    exact_column_order = list(reference.columns) == list(reproduced.columns)
    lines.append(f"Reference columns: {len(reference.columns)}")
    lines.append(f"Reproduced columns: {len(reproduced.columns)}")
    lines.append(f"Exact column order match: {exact_column_order}")

    if not exact_column_order:
        failures.append("Column order or schema differs.")

    if ALIGNMENT_KEY not in reference.columns:
        failures.append(f"Reference is missing alignment key: {ALIGNMENT_KEY}")
    if ALIGNMENT_KEY not in reproduced.columns:
        failures.append(f"Reproduction is missing alignment key: {ALIGNMENT_KEY}")

    section("TRIAL POPULATION")
    reference_duplicates = int(reference[ALIGNMENT_KEY].duplicated().sum())
    reproduced_duplicates = int(reproduced[ALIGNMENT_KEY].duplicated().sum())

    reference_ids = set(reference[ALIGNMENT_KEY].astype(str))
    reproduced_ids = set(reproduced[ALIGNMENT_KEY].astype(str))

    missing_ids = sorted(reference_ids - reproduced_ids)
    unexpected_ids = sorted(reproduced_ids - reference_ids)

    lines.append(f"Reference rows: {len(reference)}")
    lines.append(f"Reproduced rows: {len(reproduced)}")
    lines.append(f"Reference duplicate trial IDs: {reference_duplicates}")
    lines.append(f"Reproduced duplicate trial IDs: {reproduced_duplicates}")
    lines.append(f"Missing trial IDs from reproduction: {len(missing_ids)}")
    lines.append(f"Unexpected reproduced trial IDs: {len(unexpected_ids)}")
    lines.append(
        "Exact trial population match: "
        f"{not missing_ids and not unexpected_ids and reference_duplicates == 0 and reproduced_duplicates == 0}"
    )

    if len(reference) != 780 or len(reproduced) != 780:
        failures.append("Expected 780 rows in each CSV.")
    if reference_duplicates or reproduced_duplicates:
        failures.append("Duplicate trial identifiers were found.")
    if missing_ids or unexpected_ids:
        failures.append("Trial populations differ.")

    reference_indexed = reference.set_index(ALIGNMENT_KEY).sort_index()
    reproduced_indexed = reproduced.set_index(ALIGNMENT_KEY).sort_index()

    deterministic_columns = [
        column
        for column in reference.columns
        if column not in NONDETERMINISTIC_COLUMNS
        and column != ALIGNMENT_KEY
    ]

    section("DETERMINISTIC FIELD COMPARISON")
    lines.append(
        "Excluded nondeterministic columns: "
        + ", ".join(sorted(NONDETERMINISTIC_COLUMNS))
    )
    lines.append(
        f"Alignment key excluded from value columns: {ALIGNMENT_KEY}"
    )
    lines.append(
        f"Deterministic columns compared: {len(deterministic_columns)}"
    )

    total_mismatches = 0
    mismatching_columns = 0

    if (
        not missing_ids
        and not unexpected_ids
        and exact_column_order
        and reference_duplicates == 0
        and reproduced_duplicates == 0
    ):
        for column in deterministic_columns:
            reference_values = reference_indexed[column].map(normalized_value)
            reproduced_values = reproduced_indexed[column].map(
                normalized_value
            )
            mismatch_count = int(
                (reference_values != reproduced_values).sum()
            )
            lines.append(f"{column}: {mismatch_count} mismatches")
            total_mismatches += mismatch_count
            if mismatch_count:
                mismatching_columns += 1
    else:
        failures.append(
            "Deterministic comparison could not be completed safely."
        )

    lines.append(f"Columns with mismatches: {mismatching_columns}")
    lines.append(
        f"Total deterministic cell mismatches: {total_mismatches}"
    )
    exact_deterministic_match = (
        total_mismatches == 0
        and not missing_ids
        and not unexpected_ids
        and exact_column_order
        and reference_duplicates == 0
        and reproduced_duplicates == 0
    )
    lines.append(
        f"Exact deterministic-result match: {exact_deterministic_match}"
    )

    if total_mismatches:
        failures.append("Deterministic field mismatches were found.")

    section("RUNTIME COMPARISON")
    if "runtime_milliseconds" in reference.columns:
        lines.append(
            "Reference runtime statistics: "
            + json.dumps(
                runtime_statistics(reference["runtime_milliseconds"]),
                sort_keys=True,
            )
        )
        lines.append(
            "Reproduced runtime statistics: "
            + json.dumps(
                runtime_statistics(reproduced["runtime_milliseconds"]),
                sort_keys=True,
            )
        )
    else:
        lines.append("runtime_milliseconds is not present.")
    lines.append(
        "Runtime values are recorded but are not required to match exactly."
    )

    section("OUTCOME DISTRIBUTION CHECK")
    for column in OUTCOME_COLUMNS:
        if column not in reference.columns or column not in reproduced.columns:
            lines.append(f"{column}: unavailable")
            continue

        reference_counts = value_counts_as_text(reference[column])
        reproduced_counts = value_counts_as_text(reproduced[column])
        match = reference_counts == reproduced_counts

        lines.append(f"{column}:")
        lines.append(
            "  Reference: "
            + json.dumps(reference_counts, sort_keys=True)
        )
        lines.append(
            "  Reproduced: "
            + json.dumps(reproduced_counts, sort_keys=True)
        )
        lines.append(f"  Match: {match}")

        if not match:
            failures.append(f"Outcome distribution differs: {column}")

    section("FINAL DETERMINATION")
    if failures:
        lines.append("FAIL: The reproduction does not match the reference.")
        for failure in failures:
            lines.append(f"- {failure}")
        exit_code = 1
    else:
        lines.append(
            "PASS: The reproduction contains the same trial population "
            "and identical deterministic results."
        )
        lines.append(
            "Full CSV hashes may differ because runtime measurements are "
            "excluded from deterministic equality."
        )
        exit_code = 0

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\n".join(lines))
    print(f"\nReport written to: {report_path}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())