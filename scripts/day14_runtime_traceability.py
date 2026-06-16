"""Day 14 runtime statistics and artifact traceability helper.

Run from the repository root:

    python scripts/day14_runtime_traceability.py

This script does not modify files. It prints evidence checks that can be used
to update manuscript-v0.2.md.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd


def _repo_root() -> Path:
    """Return the repository root when the script is run from scripts/."""
    script_path = Path(__file__).resolve()
    if script_path.parent.name == "scripts":
        return script_path.parents[1]
    return Path.cwd().resolve()


def _status(path: Path) -> str:
    return "FOUND" if path.exists() else "MISSING"


def _markdown_table(rows: list[list[object]], headers: list[str]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(item) for item in row) + " |")
    return "\n".join(lines)


def main() -> int:
    root = _repo_root()

    raw_results = root / "experiments" / "raw_results" / "combined_experiment_results.csv"
    scenario_summary = root / "experiments" / "derived_results" / "scenario_summary.csv"
    confusion_matrix = root / "experiments" / "derived_results" / "classification_confusion_matrix.csv"

    expected_figures = [
        root / "figures" / "figure_1_accuracy_by_scenario.png",
        root / "figures" / "figure_2_recovery_by_scenario.png",
        root / "figures" / "figure_3_runtime_distribution.png",
        root / "figures" / "figure_4_classification_confusion_matrix.png",
        root / "figures" / "figure_1_accuracy_by_scenario.pdf",
        root / "figures" / "figure_2_recovery_by_scenario.pdf",
        root / "figures" / "figure_3_runtime_distribution.pdf",
        root / "figures" / "figure_4_classification_confusion_matrix.pdf",
    ]

    print("# Day 14 Runtime and Artifact Traceability Report\n")
    print(f"Repository root: `{root}`\n")

    artifact_rows = [
        ["Raw combined results", raw_results.relative_to(root), _status(raw_results)],
        ["Scenario summary", scenario_summary.relative_to(root), _status(scenario_summary)],
        ["Classification confusion matrix", confusion_matrix.relative_to(root), _status(confusion_matrix)],
    ]

    print("## Required CSV Artifacts\n")
    print(_markdown_table(artifact_rows, ["Artifact", "Path", "Status"]))
    print()

    print("## Figure Artifacts\n")
    figure_rows = []
    for path in expected_figures:
        size = path.stat().st_size if path.exists() else ""
        figure_rows.append([path.name, path.relative_to(root), _status(path), size])
    print(_markdown_table(figure_rows, ["Figure", "Path", "Status", "Bytes"]))
    print()

    if not raw_results.exists():
        print("## Runtime Statistics\n")
        print("Runtime statistics could not be computed because the raw results CSV is missing.")
        print()
        print("Expected file:")
        print(f"`{raw_results}`")
        return 1

    df = pd.read_csv(raw_results)

    print("## Raw Result Columns\n")
    print(", ".join(f"`{column}`" for column in df.columns))
    print()

    if "runtime_milliseconds" not in df.columns:
        print("## Runtime Statistics\n")
        print("Runtime statistics could not be computed because `runtime_milliseconds` is missing.")
        return 1

    runtime = pd.to_numeric(df["runtime_milliseconds"], errors="coerce").dropna()

    if runtime.empty:
        print("## Runtime Statistics\n")
        print("Runtime statistics could not be computed because no valid runtime values were found.")
        return 1

    summary_rows = [
        ["Runtime record count", int(runtime.count())],
        ["Mean runtime milliseconds", round(float(runtime.mean()), 3)],
        ["Median runtime milliseconds", round(float(runtime.median()), 3)],
        ["Minimum runtime milliseconds", round(float(runtime.min()), 3)],
        ["Maximum runtime milliseconds", round(float(runtime.max()), 3)],
        ["p95 runtime milliseconds", round(float(runtime.quantile(0.95)), 3)],
    ]

    print("## Runtime Summary\n")
    print(_markdown_table(summary_rows, ["Metric", "Value"]))
    print()

    if "experiment_domain" in df.columns:
        domain_rows = []
        grouped = df.assign(
            runtime_milliseconds=pd.to_numeric(
                df["runtime_milliseconds"],
                errors="coerce",
            )
        ).dropna(subset=["runtime_milliseconds"]).groupby("experiment_domain")

        for domain, group in grouped:
            series = group["runtime_milliseconds"]
            domain_rows.append(
                [
                    domain,
                    int(series.count()),
                    round(float(series.mean()), 3),
                    round(float(series.median()), 3),
                    round(float(series.quantile(0.95)), 3),
                ]
            )

        print("## Runtime by Experiment Domain\n")
        print(_markdown_table(domain_rows, ["Experiment domain", "Count", "Mean ms", "Median ms", "p95 ms"]))
        print()

        domains = sorted(str(value) for value in df["experiment_domain"].dropna().unique())
        print("## Experiment Domains\n")
        for domain in domains:
            print(f"- {domain}")
        print()

        baseline_terms = ["alert", "static", "rule", "baseline", "operator", "policy"]
        matching_domains = [
            domain for domain in domains
            if any(term in domain.lower() for term in baseline_terms)
        ]

        print("## Baseline-Domain Check\n")
        if matching_domains:
            print("Domains that may represent baseline or policy conditions:")
            for domain in matching_domains:
                print(f"- {domain}")
        else:
            print("No obvious baseline or policy-domain names were detected from `experiment_domain`.")
        print()
    else:
        print("## Experiment Domains\n")
        print("Column `experiment_domain` was not found. Baseline-domain check could not be performed.")
        print()

    traceability_rows = [
        ["Trial count", "combined_experiment_results.csv", _status(raw_results)],
        ["Runtime distribution", "combined_experiment_results.csv / runtime_milliseconds", _status(raw_results)],
        ["Scenario-level accuracy", "scenario_summary.csv", _status(scenario_summary)],
        ["Classification matrix", "classification_confusion_matrix.csv", _status(confusion_matrix)],
        ["Figures", "figures/figure_*", "FOUND" if all(path.exists() for path in expected_figures[:4]) else "INCOMPLETE"],
    ]

    print("## Claim-to-Artifact Traceability\n")
    print(_markdown_table(traceability_rows, ["Claim area", "Artifact", "Status"]))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
