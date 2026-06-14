"""Tests for experiment statistical analysis utilities."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.experiment_analysis import (
    build_analysis_tables,
    classification_confusion_matrix,
    detection_confusion_matrix,
    normalize_experiment_results,
    runtime_summary,
    save_analysis_tables,
    summarize_by_scenario,
    summarize_overall,
    validate_experiment_results,
    wilson_score_interval,
)


@pytest.fixture
def sample_results() -> pd.DataFrame:
    """Create a compact deterministic experiment result table."""

    return pd.DataFrame(
        [
            {
                "experiment_domain": "dataframe",
                "trial_id": "healthy-1",
                "injected_failure_type": "healthy_control",
                "injected_severity": "low",
                "failure_detected": False,
                "detected_failure_category": "healthy_control",
                "detection_correct": True,
                "predicted_root_cause": "healthy_control",
                "classification_correct": True,
                "classification_confidence": 0.99,
                "remediation_executed": True,
                "human_approval_required": False,
                "cycle_status": "healthy",
                "recovery_verified": True,
                "runtime_milliseconds": 1.0,
            },
            {
                "experiment_domain": "dataframe",
                "trial_id": "duplicate-1",
                "injected_failure_type": "duplicate_generation",
                "injected_severity": "medium",
                "failure_detected": True,
                "detected_failure_category": "duplicate_generation",
                "detection_correct": True,
                "predicted_root_cause": "duplicate_generation",
                "classification_correct": True,
                "classification_confidence": 0.96,
                "remediation_executed": True,
                "human_approval_required": False,
                "cycle_status": "recovered",
                "recovery_verified": True,
                "runtime_milliseconds": 2.0,
            },
            {
                "experiment_domain": "dataframe",
                "trial_id": "freshness-1",
                "injected_failure_type": "freshness_violation",
                "injected_severity": "low",
                "failure_detected": False,
                "detected_failure_category": "healthy_control",
                "detection_correct": False,
                "predicted_root_cause": "healthy_control",
                "classification_correct": False,
                "classification_confidence": 0.99,
                "remediation_executed": True,
                "human_approval_required": False,
                "cycle_status": "healthy",
                "recovery_verified": True,
                "runtime_milliseconds": 3.0,
            },
            {
                "experiment_domain": "dataframe",
                "trial_id": "schema-1",
                "injected_failure_type": "schema_drift",
                "injected_severity": "high",
                "failure_detected": True,
                "detected_failure_category": "schema_drift",
                "detection_correct": True,
                "predicted_root_cause": "schema_drift",
                "classification_correct": True,
                "classification_confidence": 0.99,
                "remediation_executed": False,
                "human_approval_required": True,
                "cycle_status": "awaiting_human_approval",
                "recovery_verified": False,
                "runtime_milliseconds": 4.0,
            },
            {
                "experiment_domain": "artifact",
                "trial_id": "artifact-1",
                "injected_failure_type": "output_artifact_corruption",
                "injected_severity": "high",
                "failure_detected": True,
                "detected_failure_category": "output_artifact_corruption",
                "detection_correct": True,
                "predicted_root_cause": "output_artifact_corruption",
                "classification_correct": True,
                "classification_confidence": 1.0,
                "remediation_executed": True,
                "human_approval_required": False,
                "cycle_status": "recovered",
                "recovery_verified": True,
                "runtime_milliseconds": 5.0,
            },
        ]
    )


def test_validate_experiment_results_accepts_valid_data(
    sample_results: pd.DataFrame,
) -> None:
    """A complete unique result table must pass validation."""

    validate_experiment_results(sample_results)


def test_normalization_adds_analysis_flags(
    sample_results: pd.DataFrame,
) -> None:
    """Normalization must add failure and error indicators."""

    normalized = normalize_experiment_results(sample_results)

    assert normalized["is_failure_trial"].sum() == 3
    assert normalized["is_healthy_trial"].sum() == 2
    assert normalized["is_boundary_control"].sum() == 1
    assert normalized["false_positive"].sum() == 0
    assert normalized["false_negative"].sum() == 0

    boundary = normalized.loc[
        normalized["is_boundary_control"]
    ].iloc[0]

    assert (
        boundary["analysis_condition"]
        == "freshness_boundary_control"
    )
    assert (
        boundary["expected_root_cause_for_analysis"]
        == "healthy_control"
    )
    assert boundary["evaluation_detection_correct"]
    assert boundary["evaluation_classification_correct"]


def test_string_booleans_are_normalized(
    sample_results: pd.DataFrame,
) -> None:
    """Persisted string booleans must become actual booleans."""

    data = sample_results.copy()

    for column in [
        "failure_detected",
        "detection_correct",
        "classification_correct",
        "remediation_executed",
        "human_approval_required",
        "recovery_verified",
    ]:
        data[column] = data[column].map(
            {
                True: "true",
                False: "false",
            }
        )

    normalized = normalize_experiment_results(data)

    assert normalized["failure_detected"].dtype == bool
    assert normalized["recovery_verified"].dtype == bool
    assert normalized["false_negative"].sum() == 0


def test_wilson_interval_for_perfect_result() -> None:
    """A perfect result must have an upper bound of one."""

    lower, upper = wilson_score_interval(
        10,
        10,
    )

    assert 0 < lower < 1
    assert upper == pytest.approx(1.0)


def test_wilson_interval_for_zero_result() -> None:
    """A zero-success result must have a lower bound of zero."""

    lower, upper = wilson_score_interval(
        0,
        10,
    )

    assert lower == pytest.approx(0.0)
    assert 0 < upper < 1


def test_wilson_interval_for_empty_sample() -> None:
    """An empty sample must return undefined bounds."""

    lower, upper = wilson_score_interval(
        0,
        0,
    )

    assert np.isnan(lower)
    assert np.isnan(upper)


def test_overall_summary_metrics(
    sample_results: pd.DataFrame,
) -> None:
    """Overall metrics must match the controlled sample."""

    summary = summarize_overall(sample_results).iloc[0]

    assert summary["total_trials"] == 5
    assert summary["failure_trials"] == 3
    assert summary["healthy_trials"] == 1
    assert summary["boundary_control_trials"] == 1
    assert summary["non_failure_trials"] == 2
    assert summary["experiment_domains"] == 2
    assert summary["failure_types"] == 3
    assert summary["detection_accuracy_successes"] == 5
    assert summary["detection_accuracy_trials"] == 5
    assert summary["detection_accuracy_rate"] == pytest.approx(
        1.0
    )
    assert summary["classification_accuracy_rate"] == pytest.approx(
        1.0
    )
    assert summary["false_positive_count"] == 0
    assert summary["false_negative_count"] == 0
    assert summary["false_negative_rate"] == pytest.approx(
        0.0
    )
    assert summary["median_runtime_ms"] == pytest.approx(
        3.0
    )


def test_scenario_summary_has_one_row_per_scenario(
    sample_results: pd.DataFrame,
) -> None:
    """Scenario aggregation must preserve distinct conditions."""

    summary = summarize_by_scenario(sample_results)

    assert len(summary) == 5
    assert set(
        summary["injected_failure_type"]
    ) == set(
        sample_results["injected_failure_type"]
    )

    freshness = summary.loc[
        summary["injected_failure_type"]
        == "freshness_violation"
    ].iloc[0]

    assert freshness["detection_accuracy_rate"] == pytest.approx(
        1.0
    )
    assert freshness["classification_accuracy_rate"] == pytest.approx(
        1.0
    )
    assert freshness["false_negatives"] == 0
    assert (
        freshness["analysis_condition"]
        == "freshness_boundary_control"
    )


def test_classification_confusion_matrix(
    sample_results: pd.DataFrame,
) -> None:
    """Classification confusion counts must reflect predictions."""

    confusion = classification_confusion_matrix(
        sample_results
    )

    healthy_row = confusion.loc[
        confusion["expected_root_cause"]
        == "healthy_control"
    ].iloc[0]

    assert healthy_row["healthy_control"] == 2

    duplicate_row = confusion.loc[
        confusion["expected_root_cause"]
        == "duplicate_generation"
    ].iloc[0]

    assert duplicate_row["duplicate_generation"] == 1


def test_detection_confusion_counts(
    sample_results: pd.DataFrame,
) -> None:
    """Binary detection counts must match the sample."""

    confusion = detection_confusion_matrix(
        sample_results
    ).iloc[0]

    assert confusion["true_positive"] == 3
    assert confusion["true_negative"] == 2
    assert confusion["false_positive"] == 0
    assert confusion["false_negative"] == 0
    assert confusion["sensitivity"] == pytest.approx(
        1.0
    )
    assert confusion["specificity"] == pytest.approx(
        1.0
    )


def test_runtime_summary_by_domain(
    sample_results: pd.DataFrame,
) -> None:
    """Runtime aggregation must create one row per domain."""

    summary = runtime_summary(sample_results)

    assert set(summary["experiment_domain"]) == {
        "artifact",
        "dataframe",
    }

    artifact = summary.loc[
        summary["experiment_domain"] == "artifact"
    ].iloc[0]

    assert artifact["trials"] == 1
    assert artifact["median_runtime_ms"] == pytest.approx(
        5.0
    )


def test_build_analysis_tables(
    sample_results: pd.DataFrame,
) -> None:
    """The analysis bundle must contain every required table."""

    tables = build_analysis_tables(sample_results)

    assert set(tables) == {
        "overall_summary",
        "scenario_summary",
        "classification_confusion_matrix",
        "detection_confusion_matrix",
        "runtime_summary",
    }

    assert all(
        not table.empty
        for table in tables.values()
    )


def test_analysis_tables_are_saved(
    sample_results: pd.DataFrame,
    tmp_path: Path,
) -> None:
    """Every analysis table must be persisted as CSV."""

    tables = build_analysis_tables(sample_results)

    saved_paths = save_analysis_tables(
        tables=tables,
        output_directory=tmp_path,
    )

    assert len(saved_paths) == 5
    assert all(path.exists() for path in saved_paths)

    reloaded = pd.read_csv(
        tmp_path / "overall_summary.csv"
    )

    assert reloaded.iloc[0]["total_trials"] == 5


def test_missing_columns_raise_error(
    sample_results: pd.DataFrame,
) -> None:
    """Analysis must reject incomplete experiment schemas."""

    invalid = sample_results.drop(
        columns=["runtime_milliseconds"]
    )

    with pytest.raises(
        ValueError,
        match="missing required columns",
    ):
        validate_experiment_results(invalid)


def test_duplicate_trial_ids_raise_error(
    sample_results: pd.DataFrame,
) -> None:
    """Duplicate trial identifiers must be rejected."""

    invalid = pd.concat(
        [
            sample_results,
            sample_results.iloc[[0]],
        ],
        ignore_index=True,
    )

    with pytest.raises(
        ValueError,
        match="duplicate trial identifiers",
    ):
        validate_experiment_results(invalid)


def test_invalid_boolean_values_raise_error(
    sample_results: pd.DataFrame,
) -> None:
    """Unsupported persisted boolean values must fail normalization."""

    invalid = sample_results.copy()
    invalid["failure_detected"] = (
        invalid["failure_detected"].astype(object)
    )
    invalid.loc[0, "failure_detected"] = "maybe"

    with pytest.raises(
        ValueError,
        match="unsupported values",
    ):
        normalize_experiment_results(invalid)


def test_invalid_wilson_success_count_raises_error() -> None:
    """Success counts outside the sample range must fail."""

    with pytest.raises(
        ValueError,
        match="successes must be between",
    ):
        wilson_score_interval(
            11,
            10,
        )


def test_invalid_confidence_level_raises_error() -> None:
    """Confidence levels must lie strictly between zero and one."""

    with pytest.raises(
        ValueError,
        match="confidence_level must be between",
    ):
        wilson_score_interval(
            5,
            10,
            confidence_level=1.0,
        )


def test_empty_tables_cannot_be_saved(
    tmp_path: Path,
) -> None:
    """At least one analysis table is required."""

    with pytest.raises(
        ValueError,
        match="At least one analysis table",
    ):
        save_analysis_tables(
            tables={},
            output_directory=tmp_path,
        )


def test_empty_analysis_table_cannot_be_saved(
    tmp_path: Path,
) -> None:
    """Empty individual tables must be rejected."""

    with pytest.raises(
        ValueError,
        match="is empty",
    ):
        save_analysis_tables(
            tables={
                "empty": pd.DataFrame(),
            },
            output_directory=tmp_path,
        )
