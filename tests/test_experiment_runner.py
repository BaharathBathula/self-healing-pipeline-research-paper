"""Tests for reproducible dataframe experiment execution."""

from pathlib import Path

import pandas as pd
import pytest

from src.data_generator import DatasetConfig, generate_orders
from src.experiment_runner import (
    DEFAULT_FAILURE_TYPES,
    DEFAULT_SEVERITIES,
    run_dataframe_experiment,
    run_dataframe_trial,
    save_experiment_results,
)


@pytest.fixture
def baseline_dataframe() -> pd.DataFrame:
    """Create deterministic baseline order data."""

    return generate_orders(
        DatasetConfig(
            row_count=100,
            random_seed=42,
        )
    )


def test_healthy_control_trial(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """A healthy trial must be recorded correctly."""

    result = run_dataframe_trial(
        baseline_dataframe=baseline_dataframe,
        failure_type="healthy_control",
        severity="low",
        repetition=1,
        random_seed=43,
    )

    assert result.injected_failure_type == "healthy_control"
    assert result.failure_detected is False
    assert result.detected_failure_category == "healthy_control"
    assert result.detection_correct is True
    assert result.predicted_root_cause == "healthy_control"
    assert result.classification_correct is True
    assert result.cycle_status == "healthy"
    assert result.recovery_verified is True
    assert result.runtime_milliseconds >= 0


def test_duplicate_trial_records_verified_recovery(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Duplicate trials must record successful automatic recovery."""

    result = run_dataframe_trial(
        baseline_dataframe=baseline_dataframe,
        failure_type="duplicate_generation",
        severity="medium",
        repetition=1,
        random_seed=100,
    )

    assert result.failure_detected is True
    assert result.detection_correct is True
    assert result.classification_correct is True
    assert result.remediation_action == "deduplicate_keep_first"
    assert result.remediation_executed is True
    assert result.cycle_status == "recovered"
    assert result.recovery_verified is True
    assert result.output_record_count == 100


def test_schema_trial_records_human_gate(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Schema drift must be recorded as awaiting approval."""

    result = run_dataframe_trial(
        baseline_dataframe=baseline_dataframe,
        failure_type="schema_drift",
        severity="medium",
        repetition=1,
        random_seed=101,
    )

    assert result.detection_correct is True
    assert result.classification_correct is True
    assert result.remediation_action == "quarantine_and_alert"
    assert result.remediation_executed is False
    assert result.human_approval_required is True
    assert result.cycle_status == "awaiting_human_approval"
    assert result.recovery_verified is False


def test_source_trial_records_retry_schedule(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Source failure must be classified and scheduled for recovery."""

    result = run_dataframe_trial(
        baseline_dataframe=baseline_dataframe,
        failure_type="source_failure",
        severity="high",
        repetition=1,
        random_seed=102,
    )

    assert result.detection_correct is True
    assert result.classification_correct is True
    assert (
        result.remediation_action
        == "retry_with_exponential_backoff"
    )
    assert result.remediation_executed is True
    assert result.cycle_status == "recovery_scheduled"
    assert result.recovery_verified is False


def test_transformation_trial_records_verified_recovery(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Semantic defects must be repaired and recorded."""

    result = run_dataframe_trial(
        baseline_dataframe=baseline_dataframe,
        failure_type="transformation_logic_error",
        severity="high",
        repetition=1,
        random_seed=103,
    )

    assert result.detection_correct is True
    assert result.classification_correct is True
    assert result.remediation_action == "recompute_derived_totals"
    assert result.remediation_executed is True
    assert result.cycle_status == "recovered"
    assert result.recovery_verified is True


def test_low_freshness_false_negative_is_recorded(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Sub-threshold freshness defects must remain measurable."""

    result = run_dataframe_trial(
        baseline_dataframe=baseline_dataframe,
        failure_type="freshness_violation",
        severity="low",
        repetition=1,
        random_seed=104,
    )

    assert result.injected_failure_type == "freshness_violation"
    assert result.failure_detected is False
    assert result.detected_failure_category == "healthy_control"
    assert result.detection_correct is False
    assert result.classification_correct is False


def test_complete_experiment_matrix_size(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """The default matrix must include all scenarios and repetitions."""

    results = run_dataframe_experiment(
        baseline_dataframe=baseline_dataframe,
        repetitions=2,
        initial_seed=42,
    )

    expected_scenarios = (
        1
        + (len(DEFAULT_FAILURE_TYPES) - 1)
        * len(DEFAULT_SEVERITIES)
    )

    assert len(results) == expected_scenarios * 2
    assert results["trial_id"].is_unique
    assert set(results["injected_failure_type"]) == set(
        DEFAULT_FAILURE_TYPES
    )


def test_experiment_result_columns(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Experiment output must contain analysis-ready metrics."""

    results = run_dataframe_experiment(
        baseline_dataframe=baseline_dataframe,
        failure_types=[
            "healthy_control",
            "duplicate_generation",
        ],
        severities=["medium"],
        repetitions=1,
    )

    required_columns = {
        "trial_id",
        "repetition",
        "random_seed",
        "injected_failure_type",
        "injected_severity",
        "failure_detected",
        "detection_correct",
        "predicted_root_cause",
        "classification_correct",
        "classification_confidence",
        "remediation_action",
        "remediation_executed",
        "human_approval_required",
        "cycle_status",
        "recovery_verified",
        "input_record_count",
        "output_record_count",
        "quarantined_record_count",
        "runtime_milliseconds",
    }

    assert required_columns.issubset(results.columns)


def test_experiment_is_reproducible_except_runtime(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Identical configuration must reproduce all non-timing fields."""

    first = run_dataframe_experiment(
        baseline_dataframe=baseline_dataframe,
        failure_types=[
            "duplicate_generation",
            "transformation_logic_error",
        ],
        severities=["medium"],
        repetitions=3,
        initial_seed=77,
    )

    second = run_dataframe_experiment(
        baseline_dataframe=baseline_dataframe,
        failure_types=[
            "duplicate_generation",
            "transformation_logic_error",
        ],
        severities=["medium"],
        repetitions=3,
        initial_seed=77,
    )

    pd.testing.assert_frame_equal(
        first.drop(columns=["runtime_milliseconds"]),
        second.drop(columns=["runtime_milliseconds"]),
    )


def test_csv_results_are_persisted(
    baseline_dataframe: pd.DataFrame,
    tmp_path: Path,
) -> None:
    """Experiment results must save and reload as CSV."""

    results = run_dataframe_experiment(
        baseline_dataframe=baseline_dataframe,
        failure_types=["healthy_control"],
        repetitions=1,
    )

    output = tmp_path / "results.csv"

    saved_path = save_experiment_results(
        results=results,
        output_path=output,
    )

    reloaded = pd.read_csv(saved_path)

    assert saved_path == output
    assert output.exists()
    assert len(reloaded) == len(results)
    assert set(reloaded.columns) == set(results.columns)


def test_parquet_results_are_persisted(
    baseline_dataframe: pd.DataFrame,
    tmp_path: Path,
) -> None:
    """Experiment results must save and reload as Parquet."""

    results = run_dataframe_experiment(
        baseline_dataframe=baseline_dataframe,
        failure_types=["duplicate_generation"],
        severities=["high"],
        repetitions=1,
    )

    output = tmp_path / "results.parquet"

    saved_path = save_experiment_results(
        results=results,
        output_path=output,
    )

    reloaded = pd.read_parquet(saved_path)

    assert saved_path == output
    assert output.exists()
    assert len(reloaded) == len(results)


def test_invalid_failure_type_is_rejected(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Unsupported failure types must fail validation."""

    with pytest.raises(
        ValueError,
        match="failure_type must be one of",
    ):
        run_dataframe_trial(
            baseline_dataframe=baseline_dataframe,
            failure_type="unsupported",
            severity="low",
            repetition=1,
            random_seed=42,
        )


def test_invalid_severity_is_rejected(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Unsupported severities must fail validation."""

    with pytest.raises(
        ValueError,
        match="severity must be one of",
    ):
        run_dataframe_trial(
            baseline_dataframe=baseline_dataframe,
            failure_type="duplicate_generation",
            severity="critical",
            repetition=1,
            random_seed=42,
        )


def test_zero_repetitions_are_rejected(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Experiments require at least one repetition."""

    with pytest.raises(
        ValueError,
        match="repetitions must be at least 1",
    ):
        run_dataframe_experiment(
            baseline_dataframe=baseline_dataframe,
            repetitions=0,
        )


def test_empty_baseline_is_rejected(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Trials cannot execute against an empty baseline."""

    with pytest.raises(
        ValueError,
        match="baseline_dataframe must contain",
    ):
        run_dataframe_trial(
            baseline_dataframe=baseline_dataframe.iloc[0:0],
            failure_type="healthy_control",
            severity="low",
            repetition=1,
            random_seed=42,
        )


def test_invalid_repetition_number_is_rejected(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Trial repetition numbering must begin at one."""

    with pytest.raises(
        ValueError,
        match="repetition must be at least 1",
    ):
        run_dataframe_trial(
            baseline_dataframe=baseline_dataframe,
            failure_type="healthy_control",
            severity="low",
            repetition=0,
            random_seed=42,
        )


def test_empty_results_cannot_be_saved(
    tmp_path: Path,
) -> None:
    """Empty experiment tables must not be persisted."""

    with pytest.raises(
        ValueError,
        match="results must contain",
    ):
        save_experiment_results(
            results=pd.DataFrame(),
            output_path=tmp_path / "empty.csv",
        )


def test_unsupported_output_extension_is_rejected(
    baseline_dataframe: pd.DataFrame,
    tmp_path: Path,
) -> None:
    """Only CSV and Parquet outputs are supported."""

    results = run_dataframe_experiment(
        baseline_dataframe=baseline_dataframe,
        failure_types=["healthy_control"],
        repetitions=1,
    )

    with pytest.raises(
        ValueError,
        match="must end with .csv or .parquet",
    ):
        save_experiment_results(
            results=results,
            output_path=tmp_path / "results.json",
        )
