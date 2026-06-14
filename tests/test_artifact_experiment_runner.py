"""Tests for reproducible output-artifact experiment execution."""

from pathlib import Path

import pandas as pd
import pytest

from src.artifact_experiment_runner import (
    DEFAULT_ARTIFACT_CONDITIONS,
    DEFAULT_SEVERITIES,
    run_artifact_experiment,
    run_artifact_trial,
)
from src.data_generator import DatasetConfig, generate_orders


@pytest.fixture
def baseline_dataframe() -> pd.DataFrame:
    """Create deterministic baseline order data."""

    return generate_orders(
        DatasetConfig(
            row_count=100,
            random_seed=42,
        )
    )


def test_healthy_artifact_trial(
    baseline_dataframe: pd.DataFrame,
    tmp_path: Path,
) -> None:
    """A valid artifact must be recorded as healthy."""

    result = run_artifact_trial(
        work_directory=tmp_path,
        condition="healthy_control",
        severity="low",
        repetition=1,
        random_seed=43,
        artifact_size_bytes=1_024,
        dataframe=baseline_dataframe,
    )

    assert result.injected_failure_type == "healthy_control"
    assert result.failure_detected is False
    assert result.detected_failure_category == "healthy_control"
    assert result.detection_correct is True
    assert result.predicted_root_cause == "healthy_control"
    assert result.classification_correct is True
    assert result.remediation_action == "continue_pipeline"
    assert result.remediation_executed is True
    assert result.cycle_status == "healthy"
    assert result.recovery_verified is True
    assert result.checksum_restored is True
    assert result.original_size_bytes == 1_024
    assert result.observed_size_bytes == 1_024
    assert result.regenerated_size_bytes == 1_024
    assert result.runtime_milliseconds >= 0


@pytest.mark.parametrize(
    ("severity", "expected_observed_size"),
    [
        ("low", 972),
        ("medium", 716),
        ("high", 307),
    ],
)
def test_corruption_trial_is_recovered(
    baseline_dataframe: pd.DataFrame,
    tmp_path: Path,
    severity: str,
    expected_observed_size: int,
) -> None:
    """Corrupted artifacts must be detected and regenerated."""

    result = run_artifact_trial(
        work_directory=tmp_path,
        condition="output_artifact_corruption",
        severity=severity,
        repetition=1,
        random_seed=100,
        artifact_size_bytes=1_024,
        dataframe=baseline_dataframe,
    )

    assert result.failure_detected is True
    assert (
        result.detected_failure_category
        == "output_artifact_corruption"
    )
    assert result.detection_correct is True
    assert (
        result.predicted_root_cause
        == "output_artifact_corruption"
    )
    assert result.classification_correct is True
    assert (
        result.remediation_action
        == "regenerate_output_artifact"
    )
    assert result.remediation_executed is True
    assert result.cycle_status == "recovered"
    assert result.recovery_verified is True
    assert result.checksum_restored is True
    assert result.original_size_bytes == 1_024
    assert result.observed_size_bytes == expected_observed_size
    assert result.regenerated_size_bytes == 1_024


def test_artifact_trial_creates_isolated_directory(
    tmp_path: Path,
) -> None:
    """Each trial must write artifacts into its own directory."""

    result = run_artifact_trial(
        work_directory=tmp_path,
        condition="output_artifact_corruption",
        severity="medium",
        repetition=2,
        random_seed=88,
        artifact_size_bytes=512,
    )

    trial_directory = tmp_path / result.trial_id

    assert trial_directory.exists()
    assert (trial_directory / "trusted-output.bin").exists()
    assert (trial_directory / "observed-output.bin").exists()
    assert (trial_directory / "regenerated-output.bin").exists()


def test_complete_artifact_matrix_size(
    tmp_path: Path,
) -> None:
    """The default artifact matrix must include every scenario."""

    results = run_artifact_experiment(
        work_directory=tmp_path,
        repetitions=2,
        initial_seed=42,
        artifact_size_bytes=512,
    )

    expected_scenarios = (
        1
        + (len(DEFAULT_ARTIFACT_CONDITIONS) - 1)
        * len(DEFAULT_SEVERITIES)
    )

    assert len(results) == expected_scenarios * 2
    assert results["trial_id"].is_unique
    assert set(results["injected_failure_type"]) == set(
        DEFAULT_ARTIFACT_CONDITIONS
    )


def test_artifact_experiment_columns(
    tmp_path: Path,
) -> None:
    """Experiment output must contain analysis-ready fields."""

    results = run_artifact_experiment(
        work_directory=tmp_path,
        conditions=[
            "healthy_control",
            "output_artifact_corruption",
        ],
        severities=["high"],
        repetitions=1,
        artifact_size_bytes=512,
    )

    required_columns = {
        "trial_id",
        "repetition",
        "random_seed",
        "injected_failure_type",
        "injected_severity",
        "expected_root_cause",
        "failure_detected",
        "detected_failure_category",
        "detection_correct",
        "predicted_root_cause",
        "classification_correct",
        "classification_confidence",
        "remediation_action",
        "remediation_executed",
        "cycle_status",
        "recovery_verified",
        "original_size_bytes",
        "observed_size_bytes",
        "regenerated_size_bytes",
        "checksum_restored",
        "runtime_milliseconds",
    }

    assert required_columns.issubset(results.columns)


def test_artifact_experiment_is_reproducible_except_runtime(
    tmp_path: Path,
) -> None:
    """Identical configuration must reproduce all non-timing fields."""

    first_directory = tmp_path / "first"
    second_directory = tmp_path / "second"

    first = run_artifact_experiment(
        work_directory=first_directory,
        conditions=["output_artifact_corruption"],
        severities=["medium"],
        repetitions=3,
        initial_seed=77,
        artifact_size_bytes=512,
    )

    second = run_artifact_experiment(
        work_directory=second_directory,
        conditions=["output_artifact_corruption"],
        severities=["medium"],
        repetitions=3,
        initial_seed=77,
        artifact_size_bytes=512,
    )

    pd.testing.assert_frame_equal(
        first.drop(columns=["runtime_milliseconds"]),
        second.drop(columns=["runtime_milliseconds"]),
    )


def test_different_seeds_produce_different_artifacts(
    tmp_path: Path,
) -> None:
    """Different seeds must produce different trusted artifacts."""

    first = run_artifact_trial(
        work_directory=tmp_path / "first",
        condition="healthy_control",
        severity="low",
        repetition=1,
        random_seed=10,
        artifact_size_bytes=512,
    )

    second = run_artifact_trial(
        work_directory=tmp_path / "second",
        condition="healthy_control",
        severity="low",
        repetition=1,
        random_seed=11,
        artifact_size_bytes=512,
    )

    first_bytes = (
        tmp_path
        / "first"
        / first.trial_id
        / "trusted-output.bin"
    ).read_bytes()

    second_bytes = (
        tmp_path
        / "second"
        / second.trial_id
        / "trusted-output.bin"
    ).read_bytes()

    assert first_bytes != second_bytes


def test_trial_result_is_serializable(
    tmp_path: Path,
) -> None:
    """Artifact trial output must convert to a dictionary."""

    result = run_artifact_trial(
        work_directory=tmp_path,
        condition="output_artifact_corruption",
        severity="high",
        repetition=1,
        random_seed=55,
        artifact_size_bytes=512,
    )

    serialized = result.to_dict()

    assert (
        serialized["injected_failure_type"]
        == "output_artifact_corruption"
    )
    assert serialized["recovery_verified"] is True
    assert serialized["checksum_restored"] is True


def test_invalid_condition_is_rejected(
    tmp_path: Path,
) -> None:
    """Unsupported artifact conditions must fail validation."""

    with pytest.raises(
        ValueError,
        match="condition must be one of",
    ):
        run_artifact_trial(
            work_directory=tmp_path,
            condition="unsupported",
            severity="low",
            repetition=1,
            random_seed=42,
        )


def test_invalid_severity_is_rejected(
    tmp_path: Path,
) -> None:
    """Unsupported severities must fail validation."""

    with pytest.raises(
        ValueError,
        match="severity must be one of",
    ):
        run_artifact_trial(
            work_directory=tmp_path,
            condition="output_artifact_corruption",
            severity="critical",
            repetition=1,
            random_seed=42,
        )


def test_invalid_repetition_is_rejected(
    tmp_path: Path,
) -> None:
    """Trial repetition numbering must begin at one."""

    with pytest.raises(
        ValueError,
        match="repetition must be at least 1",
    ):
        run_artifact_trial(
            work_directory=tmp_path,
            condition="healthy_control",
            severity="low",
            repetition=0,
            random_seed=42,
        )


def test_zero_repetitions_are_rejected(
    tmp_path: Path,
) -> None:
    """Artifact experiments require at least one repetition."""

    with pytest.raises(
        ValueError,
        match="repetitions must be at least 1",
    ):
        run_artifact_experiment(
            work_directory=tmp_path,
            repetitions=0,
        )


@pytest.mark.parametrize(
    "artifact_size_bytes",
    [0, 1],
)
def test_artifact_size_must_be_at_least_two(
    tmp_path: Path,
    artifact_size_bytes: int,
) -> None:
    """Artifact generation must reject unusable sizes."""

    with pytest.raises(
        ValueError,
        match="artifact_size_bytes must be at least 2",
    ):
        run_artifact_trial(
            work_directory=tmp_path,
            condition="healthy_control",
            severity="low",
            repetition=1,
            random_seed=42,
            artifact_size_bytes=artifact_size_bytes,
        )
