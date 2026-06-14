"""Statistical analysis utilities for self-healing experiment results."""

from __future__ import annotations

from math import sqrt
from pathlib import Path
from statistics import NormalDist
from typing import Iterable

import numpy as np
import pandas as pd


_REQUIRED_COLUMNS = {
    "experiment_domain",
    "trial_id",
    "injected_failure_type",
    "injected_severity",
    "failure_detected",
    "detection_correct",
    "predicted_root_cause",
    "classification_correct",
    "remediation_executed",
    "cycle_status",
    "recovery_verified",
    "runtime_milliseconds",
}

_HEALTHY_LABEL = "healthy_control"


def _coerce_boolean(series: pd.Series) -> pd.Series:
    """Convert common persisted boolean representations to bool."""

    if pd.api.types.is_bool_dtype(series):
        return series.fillna(False).astype(bool)

    normalized = (
        series.astype("string")
        .str.strip()
        .str.lower()
    )

    mapping = {
        "true": True,
        "false": False,
        "1": True,
        "0": False,
        "yes": True,
        "no": False,
    }

    converted = normalized.map(mapping)

    if converted.isna().any():
        invalid_values = sorted(
            normalized[converted.isna()]
            .dropna()
            .unique()
            .tolist()
        )

        raise ValueError(
            "Boolean column contains unsupported values: "
            + ", ".join(invalid_values)
        )

    return converted.astype(bool)


def validate_experiment_results(
    results: pd.DataFrame,
) -> None:
    """Validate the minimum schema required for analysis."""

    if results.empty:
        raise ValueError(
            "Experiment results must contain at least one trial"
        )

    missing_columns = sorted(
        _REQUIRED_COLUMNS.difference(results.columns)
    )

    if missing_columns:
        raise ValueError(
            "Experiment results are missing required columns: "
            + ", ".join(missing_columns)
        )

    if results["trial_id"].isna().any():
        raise ValueError(
            "Experiment results contain missing trial identifiers"
        )

    if results["trial_id"].duplicated().any():
        raise ValueError(
            "Experiment results contain duplicate trial identifiers"
        )


def normalize_experiment_results(
    results: pd.DataFrame,
) -> pd.DataFrame:
    """Return an analysis-ready copy of raw experiment results."""

    validate_experiment_results(results)

    normalized = results.copy()

    boolean_columns = [
        "failure_detected",
        "detection_correct",
        "classification_correct",
        "remediation_executed",
        "recovery_verified",
    ]

    for column in boolean_columns:
        normalized[column] = _coerce_boolean(
            normalized[column]
        )

    normalized["runtime_milliseconds"] = pd.to_numeric(
        normalized["runtime_milliseconds"],
        errors="raise",
    )

    normalized["is_failure_trial"] = (
        normalized["injected_failure_type"]
        != _HEALTHY_LABEL
    )

    normalized["is_healthy_trial"] = (
        ~normalized["is_failure_trial"]
    )

    normalized["false_positive"] = (
        normalized["is_healthy_trial"]
        & normalized["failure_detected"]
    )

    normalized["false_negative"] = (
        normalized["is_failure_trial"]
        & ~normalized["failure_detected"]
    )

    normalized["human_approval_required"] = (
        normalized.get(
            "human_approval_required",
            pd.Series(
                False,
                index=normalized.index,
            ),
        )
        .fillna(False)
    )

    normalized["human_approval_required"] = _coerce_boolean(
        normalized["human_approval_required"]
    )

    return normalized


def wilson_score_interval(
    successes: int,
    total: int,
    *,
    confidence_level: float = 0.95,
) -> tuple[float, float]:
    """Calculate a two-sided Wilson score confidence interval."""

    if total < 1:
        return (float("nan"), float("nan"))

    if successes < 0 or successes > total:
        raise ValueError(
            "successes must be between zero and total"
        )

    if not 0 < confidence_level < 1:
        raise ValueError(
            "confidence_level must be between zero and one"
        )

    alpha = 1.0 - confidence_level
    z_score = NormalDist().inv_cdf(
        1.0 - alpha / 2.0
    )

    proportion = successes / total
    denominator = 1.0 + (z_score**2 / total)

    center = (
        proportion
        + z_score**2 / (2.0 * total)
    ) / denominator

    margin = (
        z_score
        * sqrt(
            (
                proportion
                * (1.0 - proportion)
                / total
            )
            + (
                z_score**2
                / (4.0 * total**2)
            )
        )
        / denominator
    )

    return (
        max(0.0, center - margin),
        min(1.0, center + margin),
    )


def _proportion_metrics(
    values: Iterable[bool],
    *,
    prefix: str,
) -> dict[str, float | int]:
    """Create count, rate, and Wilson interval metrics."""

    boolean_values = pd.Series(
        list(values),
        dtype=bool,
    )

    total = int(len(boolean_values))
    successes = int(boolean_values.sum())

    if total == 0:
        rate = float("nan")
    else:
        rate = successes / total

    lower, upper = wilson_score_interval(
        successes,
        total,
    )

    return {
        f"{prefix}_successes": successes,
        f"{prefix}_trials": total,
        f"{prefix}_rate": rate,
        f"{prefix}_ci95_lower": lower,
        f"{prefix}_ci95_upper": upper,
    }


def summarize_overall(
    results: pd.DataFrame,
) -> pd.DataFrame:
    """Create one publication-ready overall summary row."""

    data = normalize_experiment_results(results)

    failure_trials = data.loc[
        data["is_failure_trial"]
    ]

    healthy_trials = data.loc[
        data["is_healthy_trial"]
    ]

    directly_executed = failure_trials.loc[
        failure_trials["remediation_executed"]
        & (
            failure_trials["cycle_status"]
            != "recovery_scheduled"
        )
    ]

    row: dict[str, object] = {
        "total_trials": len(data),
        "failure_trials": len(failure_trials),
        "healthy_trials": len(healthy_trials),
        "experiment_domains": int(
            data["experiment_domain"].nunique()
        ),
        "failure_types": int(
            failure_trials[
                "injected_failure_type"
            ].nunique()
        ),
        "median_runtime_ms": float(
            data["runtime_milliseconds"].median()
        ),
        "p95_runtime_ms": float(
            data["runtime_milliseconds"].quantile(0.95)
        ),
        "mean_runtime_ms": float(
            data["runtime_milliseconds"].mean()
        ),
    }

    row.update(
        _proportion_metrics(
            data["detection_correct"],
            prefix="detection_accuracy",
        )
    )

    row.update(
        _proportion_metrics(
            data["classification_correct"],
            prefix="classification_accuracy",
        )
    )

    row.update(
        _proportion_metrics(
            failure_trials["remediation_executed"],
            prefix="automatic_action",
        )
    )

    row.update(
        _proportion_metrics(
            failure_trials["recovery_verified"],
            prefix="verified_recovery_all_failures",
        )
    )

    row.update(
        _proportion_metrics(
            directly_executed["recovery_verified"],
            prefix="verified_recovery_direct_actions",
        )
    )

    false_positive_count = int(
        healthy_trials["false_positive"].sum()
    )

    false_negative_count = int(
        failure_trials["false_negative"].sum()
    )

    row["false_positive_count"] = false_positive_count
    row["false_positive_rate"] = (
        false_positive_count / len(healthy_trials)
        if len(healthy_trials)
        else float("nan")
    )

    row["false_negative_count"] = false_negative_count
    row["false_negative_rate"] = (
        false_negative_count / len(failure_trials)
        if len(failure_trials)
        else float("nan")
    )

    return pd.DataFrame([row])


def summarize_by_scenario(
    results: pd.DataFrame,
) -> pd.DataFrame:
    """Summarize performance by domain, failure type, and severity."""

    data = normalize_experiment_results(results)

    group_columns = [
        "experiment_domain",
        "injected_failure_type",
        "injected_severity",
    ]

    rows: list[dict[str, object]] = []

    for group_values, group in data.groupby(
        group_columns,
        dropna=False,
        sort=True,
    ):
        domain, failure_type, severity = group_values

        row: dict[str, object] = {
            "experiment_domain": domain,
            "injected_failure_type": failure_type,
            "injected_severity": severity,
            "trials": len(group),
            "failures_detected": int(
                group["failure_detected"].sum()
            ),
            "false_positives": int(
                group["false_positive"].sum()
            ),
            "false_negatives": int(
                group["false_negative"].sum()
            ),
            "median_runtime_ms": float(
                group["runtime_milliseconds"].median()
            ),
            "p95_runtime_ms": float(
                group[
                    "runtime_milliseconds"
                ].quantile(0.95)
            ),
            "mean_classification_confidence": float(
                pd.to_numeric(
                    group["classification_confidence"],
                    errors="coerce",
                ).mean()
            ),
            "dominant_cycle_status": str(
                group["cycle_status"]
                .mode()
                .iloc[0]
            ),
        }

        row.update(
            _proportion_metrics(
                group["detection_correct"],
                prefix="detection_accuracy",
            )
        )

        row.update(
            _proportion_metrics(
                group["classification_correct"],
                prefix="classification_accuracy",
            )
        )

        row.update(
            _proportion_metrics(
                group["recovery_verified"],
                prefix="verified_recovery",
            )
        )

        rows.append(row)

    return pd.DataFrame(rows)


def classification_confusion_matrix(
    results: pd.DataFrame,
) -> pd.DataFrame:
    """Create a root-cause classification confusion matrix."""

    data = normalize_experiment_results(results)

    confusion = pd.crosstab(
        data["injected_failure_type"],
        data["predicted_root_cause"],
        rownames=["expected_root_cause"],
        colnames=["predicted_root_cause"],
        dropna=False,
    )

    return confusion.reset_index()


def detection_confusion_matrix(
    results: pd.DataFrame,
) -> pd.DataFrame:
    """Create binary failure-detection confusion counts."""

    data = normalize_experiment_results(results)

    expected_failure = data[
        "is_failure_trial"
    ]

    observed_failure = data[
        "failure_detected"
    ]

    true_positive = int(
        (expected_failure & observed_failure).sum()
    )

    true_negative = int(
        (~expected_failure & ~observed_failure).sum()
    )

    false_positive = int(
        (~expected_failure & observed_failure).sum()
    )

    false_negative = int(
        (expected_failure & ~observed_failure).sum()
    )

    return pd.DataFrame(
        [
            {
                "true_positive": true_positive,
                "true_negative": true_negative,
                "false_positive": false_positive,
                "false_negative": false_negative,
                "sensitivity": (
                    true_positive
                    / (true_positive + false_negative)
                    if true_positive + false_negative
                    else float("nan")
                ),
                "specificity": (
                    true_negative
                    / (true_negative + false_positive)
                    if true_negative + false_positive
                    else float("nan")
                ),
            }
        ]
    )


def runtime_summary(
    results: pd.DataFrame,
) -> pd.DataFrame:
    """Summarize runtime distributions by experiment domain."""

    data = normalize_experiment_results(results)

    rows: list[dict[str, object]] = []

    for domain, group in data.groupby(
        "experiment_domain",
        sort=True,
    ):
        runtime = group[
            "runtime_milliseconds"
        ]

        rows.append(
            {
                "experiment_domain": domain,
                "trials": len(group),
                "minimum_runtime_ms": float(
                    runtime.min()
                ),
                "median_runtime_ms": float(
                    runtime.median()
                ),
                "mean_runtime_ms": float(
                    runtime.mean()
                ),
                "p95_runtime_ms": float(
                    runtime.quantile(0.95)
                ),
                "maximum_runtime_ms": float(
                    runtime.max()
                ),
                "standard_deviation_ms": float(
                    runtime.std(ddof=1)
                ),
            }
        )

    return pd.DataFrame(rows)


def build_analysis_tables(
    results: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Build all publication-oriented analysis tables."""

    return {
        "overall_summary": summarize_overall(results),
        "scenario_summary": summarize_by_scenario(results),
        "classification_confusion_matrix": (
            classification_confusion_matrix(results)
        ),
        "detection_confusion_matrix": (
            detection_confusion_matrix(results)
        ),
        "runtime_summary": runtime_summary(results),
    }


def save_analysis_tables(
    *,
    tables: dict[str, pd.DataFrame],
    output_directory: Path | str,
) -> list[Path]:
    """Save each analysis table as a CSV file."""

    if not tables:
        raise ValueError(
            "At least one analysis table is required"
        )

    output_path = Path(output_directory)
    output_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    saved_paths: list[Path] = []

    for table_name, table in tables.items():
        if table.empty:
            raise ValueError(
                f"Analysis table '{table_name}' is empty"
            )

        destination = (
            output_path
            / f"{table_name}.csv"
        )

        table.to_csv(
            destination,
            index=False,
        )

        saved_paths.append(destination)

    return saved_paths
