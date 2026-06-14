"""Run the complete reproducible self-healing experiment matrix."""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from src.artifact_experiment_runner import run_artifact_experiment
from src.data_generator import DatasetConfig, generate_orders
from src.experiment_runner import (
    run_dataframe_experiment,
    save_experiment_results,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "experiments"
    / "raw_results"
)
DEFAULT_ARTIFACT_DIRECTORY = (
    PROJECT_ROOT
    / "experiments"
    / "artifact_trials"
)


def _git_commit() -> str:
    """Return the current Git commit when available."""

    try:
        result = subprocess.run(
            [
                "git",
                "rev-parse",
                "HEAD",
            ],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (
        FileNotFoundError,
        subprocess.CalledProcessError,
    ):
        return "unavailable"

    return result.stdout.strip()


def _parse_arguments() -> argparse.Namespace:
    """Parse command-line experiment configuration."""

    parser = argparse.ArgumentParser(
        description=(
            "Run repeated dataframe and output-artifact "
            "self-healing experiments."
        )
    )

    parser.add_argument(
        "--row-count",
        type=int,
        default=10_000,
        help="Number of synthetic baseline records.",
    )

    parser.add_argument(
        "--repetitions",
        type=int,
        default=30,
        help="Repeated trials per scenario.",
    )

    parser.add_argument(
        "--initial-seed",
        type=int,
        default=42,
        help="Initial deterministic random seed.",
    )

    parser.add_argument(
        "--artifact-size-bytes",
        type=int,
        default=4_096,
        help="Size of each generated output artifact.",
    )

    parser.add_argument(
        "--output-directory",
        type=Path,
        default=DEFAULT_OUTPUT_DIRECTORY,
        help="Directory for raw CSV, Parquet, and metadata.",
    )

    parser.add_argument(
        "--artifact-directory",
        type=Path,
        default=DEFAULT_ARTIFACT_DIRECTORY,
        help="Directory for per-trial artifact files.",
    )

    return parser.parse_args()


def _validate_arguments(arguments: argparse.Namespace) -> None:
    """Validate experiment command-line arguments."""

    if arguments.row_count < 1:
        raise ValueError(
            "row-count must be at least 1"
        )

    if arguments.repetitions < 1:
        raise ValueError(
            "repetitions must be at least 1"
        )

    if arguments.artifact_size_bytes < 2:
        raise ValueError(
            "artifact-size-bytes must be at least 2"
        )


def _experiment_metadata(
    *,
    arguments: argparse.Namespace,
    dataframe_results: pd.DataFrame,
    artifact_results: pd.DataFrame,
    started_at: datetime,
    completed_at: datetime,
) -> dict[str, Any]:
    """Create reproducibility metadata for the experiment run."""

    return {
        "experiment_name": (
            "reliability_aware_self_healing_pipeline"
        ),
        "started_at_utc": started_at.isoformat(),
        "completed_at_utc": completed_at.isoformat(),
        "duration_seconds": round(
            (
                completed_at - started_at
            ).total_seconds(),
            6,
        ),
        "configuration": {
            "row_count": arguments.row_count,
            "repetitions": arguments.repetitions,
            "initial_seed": arguments.initial_seed,
            "artifact_size_bytes": (
                arguments.artifact_size_bytes
            ),
        },
        "trial_counts": {
            "dataframe_trials": len(dataframe_results),
            "artifact_trials": len(artifact_results),
            "combined_trials": (
                len(dataframe_results)
                + len(artifact_results)
            ),
        },
        "environment": {
            "python_version": sys.version,
            "python_executable": sys.executable,
            "platform": platform.platform(),
            "pandas_version": pd.__version__,
            "git_commit": _git_commit(),
        },
    }


def main() -> int:
    """Run the full experiment and save all raw evidence."""

    arguments = _parse_arguments()
    _validate_arguments(arguments)

    output_directory = arguments.output_directory.resolve()
    artifact_directory = arguments.artifact_directory.resolve()

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    artifact_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    started_at = datetime.now(timezone.utc)

    baseline_dataframe = generate_orders(
        DatasetConfig(
            row_count=arguments.row_count,
            random_seed=arguments.initial_seed,
        )
    )

    dataframe_results = run_dataframe_experiment(
        baseline_dataframe=baseline_dataframe,
        repetitions=arguments.repetitions,
        initial_seed=arguments.initial_seed,
    )

    dataframe_results.insert(
        0,
        "experiment_domain",
        "dataframe",
    )

    artifact_results = run_artifact_experiment(
        work_directory=artifact_directory,
        repetitions=arguments.repetitions,
        initial_seed=arguments.initial_seed,
        artifact_size_bytes=(
            arguments.artifact_size_bytes
        ),
        dataframe=baseline_dataframe,
    )

    artifact_results.insert(
        0,
        "experiment_domain",
        "artifact",
    )

    dataframe_csv = (
        output_directory
        / "dataframe_experiment_results.csv"
    )

    dataframe_parquet = (
        output_directory
        / "dataframe_experiment_results.parquet"
    )

    artifact_csv = (
        output_directory
        / "artifact_experiment_results.csv"
    )

    artifact_parquet = (
        output_directory
        / "artifact_experiment_results.parquet"
    )

    save_experiment_results(
        results=dataframe_results,
        output_path=dataframe_csv,
    )

    save_experiment_results(
        results=dataframe_results,
        output_path=dataframe_parquet,
    )

    save_experiment_results(
        results=artifact_results,
        output_path=artifact_csv,
    )

    save_experiment_results(
        results=artifact_results,
        output_path=artifact_parquet,
    )

    combined_results = pd.concat(
        [
            dataframe_results,
            artifact_results,
        ],
        ignore_index=True,
        sort=False,
    )

    combined_csv = (
        output_directory
        / "combined_experiment_results.csv"
    )

    combined_parquet = (
        output_directory
        / "combined_experiment_results.parquet"
    )

    save_experiment_results(
        results=combined_results,
        output_path=combined_csv,
    )

    save_experiment_results(
        results=combined_results,
        output_path=combined_parquet,
    )

    completed_at = datetime.now(timezone.utc)

    metadata = _experiment_metadata(
        arguments=arguments,
        dataframe_results=dataframe_results,
        artifact_results=artifact_results,
        started_at=started_at,
        completed_at=completed_at,
    )

    metadata_path = (
        output_directory
        / "experiment_metadata.json"
    )

    metadata_path.write_text(
        json.dumps(
            metadata,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    print(
        "Experiment completed successfully."
    )

    print(
        f"Dataframe trials: {len(dataframe_results)}"
    )

    print(
        f"Artifact trials: {len(artifact_results)}"
    )

    print(
        f"Combined trials: {len(combined_results)}"
    )

    print(
        f"Results directory: {output_directory}"
    )

    print(
        f"Metadata file: {metadata_path}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
