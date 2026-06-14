"""Generate publication-ready statistical tables from experiment results."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.experiment_analysis import (
    build_analysis_tables,
    save_analysis_tables,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_INPUT_PATH = (
    PROJECT_ROOT
    / "experiments"
    / "raw_results"
    / "combined_experiment_results.csv"
)

DEFAULT_OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "experiments"
    / "derived_results"
)


def _parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description=(
            "Generate statistical analysis tables from "
            "self-healing experiment results."
        )
    )

    parser.add_argument(
        "--input-path",
        type=Path,
        default=DEFAULT_INPUT_PATH,
        help="Combined experiment CSV or Parquet file.",
    )

    parser.add_argument(
        "--output-directory",
        type=Path,
        default=DEFAULT_OUTPUT_DIRECTORY,
        help="Directory for derived analysis tables.",
    )

    return parser.parse_args()


def _load_results(path: Path) -> pd.DataFrame:
    """Load experiment results from CSV or Parquet."""

    if not path.exists():
        raise FileNotFoundError(
            f"Experiment result file does not exist: {path}"
        )

    suffix = path.suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(path)

    if suffix == ".parquet":
        return pd.read_parquet(path)

    raise ValueError(
        "input-path must end with .csv or .parquet"
    )


def _safe_number(value: Any) -> Any:
    """Convert pandas and NumPy scalars for JSON output."""

    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        return value.item()

    return value


def _summary_payload(
    overall_summary: pd.DataFrame,
) -> dict[str, Any]:
    """Create a compact machine-readable summary."""

    row = overall_summary.iloc[0].to_dict()

    selected_metrics = {
        "total_trials": row["total_trials"],
        "failure_trials": row["failure_trials"],
        "healthy_trials": row["healthy_trials"],
        "failure_types": row["failure_types"],
        "detection_accuracy_rate": row[
            "detection_accuracy_rate"
        ],
        "detection_accuracy_ci95_lower": row[
            "detection_accuracy_ci95_lower"
        ],
        "detection_accuracy_ci95_upper": row[
            "detection_accuracy_ci95_upper"
        ],
        "classification_accuracy_rate": row[
            "classification_accuracy_rate"
        ],
        "classification_accuracy_ci95_lower": row[
            "classification_accuracy_ci95_lower"
        ],
        "classification_accuracy_ci95_upper": row[
            "classification_accuracy_ci95_upper"
        ],
        "verified_recovery_all_failures_rate": row[
            "verified_recovery_all_failures_rate"
        ],
        "verified_recovery_direct_actions_rate": row[
            "verified_recovery_direct_actions_rate"
        ],
        "false_positive_count": row[
            "false_positive_count"
        ],
        "false_positive_rate": row[
            "false_positive_rate"
        ],
        "false_negative_count": row[
            "false_negative_count"
        ],
        "false_negative_rate": row[
            "false_negative_rate"
        ],
        "median_runtime_ms": row[
            "median_runtime_ms"
        ],
        "p95_runtime_ms": row[
            "p95_runtime_ms"
        ],
    }

    return {
        key: _safe_number(value)
        for key, value in selected_metrics.items()
    }


def main() -> int:
    """Generate and persist all analysis outputs."""

    arguments = _parse_arguments()

    input_path = arguments.input_path.resolve()
    output_directory = (
        arguments.output_directory.resolve()
    )

    results = _load_results(input_path)

    tables = build_analysis_tables(results)

    saved_paths = save_analysis_tables(
        tables=tables,
        output_directory=output_directory,
    )

    summary = _summary_payload(
        tables["overall_summary"]
    )

    summary_path = (
        output_directory
        / "analysis_summary.json"
    )

    summary_path.write_text(
        json.dumps(
            summary,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    print("Analysis completed successfully.")
    print(f"Input trials: {len(results)}")
    print(f"Analysis tables: {len(saved_paths)}")
    print(f"Output directory: {output_directory}")
    print(
        "Detection accuracy: "
        f"{summary['detection_accuracy_rate']:.4f}"
    )
    print(
        "Classification accuracy: "
        f"{summary['classification_accuracy_rate']:.4f}"
    )
    print(
        "Verified recovery across all failures: "
        f"{summary['verified_recovery_all_failures_rate']:.4f}"
    )
    print(
        "Verified recovery for directly executed actions: "
        f"{summary['verified_recovery_direct_actions_rate']:.4f}"
    )
    print(
        f"False positives: {summary['false_positive_count']}"
    )
    print(
        f"False negatives: {summary['false_negative_count']}"
    )
    print(
        f"Summary file: {summary_path}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
