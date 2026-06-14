"""Generate publication-ready figures from experiment results."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_RAW_RESULTS = (
    PROJECT_ROOT
    / "experiments"
    / "raw_results"
    / "combined_experiment_results.csv"
)

DEFAULT_SCENARIO_SUMMARY = (
    PROJECT_ROOT
    / "experiments"
    / "derived_results"
    / "scenario_summary.csv"
)

DEFAULT_CLASSIFICATION_CONFUSION = (
    PROJECT_ROOT
    / "experiments"
    / "derived_results"
    / "classification_confusion_matrix.csv"
)

DEFAULT_OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "figures"
)


def _parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description=(
            "Generate publication-ready experiment figures."
        )
    )

    parser.add_argument(
        "--raw-results",
        type=Path,
        default=DEFAULT_RAW_RESULTS,
        help="Combined raw experiment CSV.",
    )

    parser.add_argument(
        "--scenario-summary",
        type=Path,
        default=DEFAULT_SCENARIO_SUMMARY,
        help="Scenario-level summary CSV.",
    )

    parser.add_argument(
        "--classification-confusion",
        type=Path,
        default=DEFAULT_CLASSIFICATION_CONFUSION,
        help="Classification confusion-matrix CSV.",
    )

    parser.add_argument(
        "--output-directory",
        type=Path,
        default=DEFAULT_OUTPUT_DIRECTORY,
        help="Directory for generated PNG and PDF figures.",
    )

    return parser.parse_args()


def _require_file(path: Path) -> None:
    """Raise a clear error when an input file is missing."""

    if not path.exists():
        raise FileNotFoundError(
            f"Required input file does not exist: {path}"
        )


def _scenario_label(
    failure_type: str,
    severity: str,
) -> str:
    """Create a compact plot label."""

    readable_failure = failure_type.replace("_", " ")

    if failure_type == "healthy_control":
        return "healthy control"

    return f"{readable_failure}\n({severity})"


def _save_figure(
    figure: plt.Figure,
    output_directory: Path,
    filename_stem: str,
) -> None:
    """Save one figure as both PNG and PDF."""

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    figure.tight_layout()

    figure.savefig(
        output_directory / f"{filename_stem}.png",
        dpi=300,
        bbox_inches="tight",
    )

    figure.savefig(
        output_directory / f"{filename_stem}.pdf",
        bbox_inches="tight",
    )

    plt.close(figure)


def plot_accuracy_by_scenario(
    scenario_summary: pd.DataFrame,
    output_directory: Path,
) -> None:
    """Plot detection and classification accuracy per scenario."""

    ordered = scenario_summary.sort_values(
        [
            "experiment_domain",
            "injected_failure_type",
            "injected_severity",
        ]
    ).reset_index(drop=True)

    labels = [
        _scenario_label(
            row["injected_failure_type"],
            row["injected_severity"],
        )
        for _, row in ordered.iterrows()
    ]

    x_positions = np.arange(len(ordered))
    bar_width = 0.38

    figure, axis = plt.subplots(
        figsize=(18, 8)
    )

    axis.bar(
        x_positions - bar_width / 2,
        ordered["detection_accuracy_rate"],
        width=bar_width,
        label="Detection accuracy",
    )

    axis.bar(
        x_positions + bar_width / 2,
        ordered["classification_accuracy_rate"],
        width=bar_width,
        label="Classification accuracy",
    )

    axis.set_ylim(0.0, 1.05)
    axis.set_ylabel("Accuracy")
    axis.set_xlabel("Injected scenario")
    axis.set_title(
        "Detection and Root-Cause Classification Accuracy by Scenario"
    )

    axis.set_xticks(x_positions)
    axis.set_xticklabels(
        labels,
        rotation=60,
        ha="right",
    )

    axis.legend()
    axis.grid(
        axis="y",
        alpha=0.3,
    )

    _save_figure(
        figure,
        output_directory,
        "figure_1_accuracy_by_scenario",
    )


def plot_recovery_outcomes(
    scenario_summary: pd.DataFrame,
    output_directory: Path,
) -> None:
    """Plot verified recovery rates for injected failures."""

    failures = scenario_summary.loc[
        scenario_summary["injected_failure_type"]
        != "healthy_control"
    ].copy()

    failures = failures.sort_values(
        [
            "experiment_domain",
            "injected_failure_type",
            "injected_severity",
        ]
    ).reset_index(drop=True)

    labels = [
        _scenario_label(
            row["injected_failure_type"],
            row["injected_severity"],
        )
        for _, row in failures.iterrows()
    ]

    x_positions = np.arange(len(failures))

    figure, axis = plt.subplots(
        figsize=(18, 8)
    )

    axis.bar(
        x_positions,
        failures["verified_recovery_rate"],
    )

    axis.set_ylim(0.0, 1.05)
    axis.set_ylabel("Verified recovery rate")
    axis.set_xlabel("Injected failure scenario")
    axis.set_title(
        "Verified Recovery Outcomes by Failure Scenario"
    )

    axis.set_xticks(x_positions)
    axis.set_xticklabels(
        labels,
        rotation=60,
        ha="right",
    )

    axis.grid(
        axis="y",
        alpha=0.3,
    )

    _save_figure(
        figure,
        output_directory,
        "figure_2_recovery_by_scenario",
    )


def plot_runtime_distribution(
    raw_results: pd.DataFrame,
    output_directory: Path,
) -> None:
    """Plot runtime distributions by experiment domain."""

    domains = sorted(
        raw_results["experiment_domain"]
        .dropna()
        .unique()
        .tolist()
    )

    runtime_values = [
        raw_results.loc[
            raw_results["experiment_domain"] == domain,
            "runtime_milliseconds",
        ].astype(float)
        for domain in domains
    ]

    figure, axis = plt.subplots(
        figsize=(9, 7)
    )

    axis.boxplot(
        runtime_values,
        tick_labels=domains,
        showfliers=True,
    )

    axis.set_ylabel("Runtime (milliseconds)")
    axis.set_xlabel("Experiment domain")
    axis.set_title(
        "Self-Healing Cycle Runtime Distribution"
    )

    axis.grid(
        axis="y",
        alpha=0.3,
    )

    _save_figure(
        figure,
        output_directory,
        "figure_3_runtime_distribution",
    )


def plot_classification_confusion_matrix(
    confusion: pd.DataFrame,
    output_directory: Path,
) -> None:
    """Plot the root-cause classification confusion matrix."""

    expected_column = "expected_root_cause"

    if expected_column not in confusion.columns:
        raise ValueError(
            "Confusion matrix is missing expected_root_cause"
        )

    matrix = confusion.set_index(expected_column)

    numeric_matrix = matrix.apply(
        pd.to_numeric,
        errors="coerce",
    ).fillna(0)

    figure, axis = plt.subplots(
        figsize=(12, 10)
    )

    image = axis.imshow(
        numeric_matrix.to_numpy(),
        aspect="auto",
    )

    axis.set_xticks(
        np.arange(len(numeric_matrix.columns))
    )

    axis.set_xticklabels(
        [
            column.replace("_", " ")
            for column in numeric_matrix.columns
        ],
        rotation=55,
        ha="right",
    )

    axis.set_yticks(
        np.arange(len(numeric_matrix.index))
    )

    axis.set_yticklabels(
        [
            index.replace("_", " ")
            for index in numeric_matrix.index
        ]
    )

    axis.set_xlabel("Predicted root cause")
    axis.set_ylabel("Injected root cause")
    axis.set_title(
        "Root-Cause Classification Confusion Matrix"
    )

    for row_index in range(
        numeric_matrix.shape[0]
    ):
        for column_index in range(
            numeric_matrix.shape[1]
        ):
            value = int(
                numeric_matrix.iloc[
                    row_index,
                    column_index,
                ]
            )

            if value > 0:
                axis.text(
                    column_index,
                    row_index,
                    str(value),
                    ha="center",
                    va="center",
                )

    figure.colorbar(
        image,
        ax=axis,
        label="Trial count",
    )

    _save_figure(
        figure,
        output_directory,
        "figure_4_classification_confusion_matrix",
    )


def main() -> int:
    """Generate all publication figures."""

    arguments = _parse_arguments()

    raw_results_path = arguments.raw_results.resolve()
    scenario_summary_path = (
        arguments.scenario_summary.resolve()
    )
    confusion_path = (
        arguments.classification_confusion.resolve()
    )
    output_directory = (
        arguments.output_directory.resolve()
    )

    for path in (
        raw_results_path,
        scenario_summary_path,
        confusion_path,
    ):
        _require_file(path)

    raw_results = pd.read_csv(
        raw_results_path
    )

    scenario_summary = pd.read_csv(
        scenario_summary_path
    )

    confusion = pd.read_csv(
        confusion_path
    )

    plot_accuracy_by_scenario(
        scenario_summary,
        output_directory,
    )

    plot_recovery_outcomes(
        scenario_summary,
        output_directory,
    )

    plot_runtime_distribution(
        raw_results,
        output_directory,
    )

    plot_classification_confusion_matrix(
        confusion,
        output_directory,
    )

    generated_files = sorted(
        output_directory.glob("figure_*")
    )

    print("Figure generation completed successfully.")
    print(f"Figures generated: {len(generated_files)}")
    print(f"Output directory: {output_directory}")

    for path in generated_files:
        print(path.name)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
