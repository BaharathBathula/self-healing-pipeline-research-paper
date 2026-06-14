"""End-to-end tests for policy-constrained self-healing cycles."""

from pathlib import Path

import pandas as pd
import pytest

from src.data_generator import DatasetConfig, generate_orders
from src.failure_injection import (
    inject_duplicate_generation,
    inject_missing_value_spike,
    inject_schema_drift,
)
from src.output_failure import (
    calculate_sha256,
    inject_output_corruption,
)
from src.self_healing import (
    run_artifact_self_healing_cycle,
    run_dataframe_self_healing_cycle,
)
from src.source_failure import SimulatedTimeoutError
from src.transformation_failure import (
    inject_transformation_logic_error,
    transformation_error_mask,
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


def test_healthy_dataframe_cycle(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Healthy input must pass through the entire cycle unchanged."""

    result = run_dataframe_self_healing_cycle(
        observed_dataframe=baseline_dataframe,
        baseline_dataframe=baseline_dataframe,
    )

    assert result.detection.failure_detected is False
    assert (
        result.classification.predicted_root_cause
        == "healthy_control"
    )
    assert result.policy_decision.action == "continue_pipeline"
    assert result.remediation.executed is True
    assert result.cycle_status == "healthy"
    assert result.recovery_verified is True

    pd.testing.assert_frame_equal(
        result.remediation.output_dataframe,
        baseline_dataframe,
    )


def test_duplicate_failure_is_detected_and_recovered(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Duplicate records must be removed and recovery verified."""

    injected = inject_duplicate_generation(
        baseline_dataframe,
        "medium",
    )

    result = run_dataframe_self_healing_cycle(
        observed_dataframe=injected.dataframe,
        baseline_dataframe=baseline_dataframe,
    )

    assert (
        result.detection.detected_failure_category
        == "duplicate_generation"
    )
    assert (
        result.classification.predicted_root_cause
        == "duplicate_generation"
    )
    assert (
        result.policy_decision.action
        == "deduplicate_keep_first"
    )
    assert result.remediation.executed is True
    assert result.cycle_status == "recovered"
    assert result.recovery_verified is True
    assert (
        result.remediation.output_dataframe["order_id"]
        .duplicated()
        .sum()
        == 0
    )


def test_missing_values_are_quarantined_and_recovery_verified(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Invalid rows must be quarantined and valid rows preserved."""

    injected = inject_missing_value_spike(
        baseline_dataframe,
        "medium",
    )

    result = run_dataframe_self_healing_cycle(
        observed_dataframe=injected.dataframe,
        baseline_dataframe=baseline_dataframe,
    )

    assert (
        result.classification.predicted_root_cause
        == "missing_value_spike"
    )
    assert (
        result.policy_decision.action
        == "quarantine_invalid_rows"
    )
    assert result.cycle_status == "recovered"
    assert result.recovery_verified is True
    assert len(result.remediation.quarantined_dataframe) > 0
    assert (
        result.verification_evidence[
            "remaining_invalid_record_count"
        ]
        == 0
    )


@pytest.mark.parametrize(
    "severity",
    ["low", "medium", "high"],
)
def test_transformation_failure_is_repaired_end_to_end(
    baseline_dataframe: pd.DataFrame,
    severity: str,
) -> None:
    """Semantic total defects must be detected and repaired."""

    injected = inject_transformation_logic_error(
        baseline_dataframe,
        severity,
        random_seed=21,
    )

    result = run_dataframe_self_healing_cycle(
        observed_dataframe=injected.dataframe,
        baseline_dataframe=baseline_dataframe,
        detection_mode="transformation",
    )

    assert (
        result.detection.detected_failure_category
        == "transformation_logic_error"
    )
    assert (
        result.classification.predicted_root_cause
        == "transformation_logic_error"
    )
    assert (
        result.policy_decision.action
        == "recompute_derived_totals"
    )
    assert result.remediation.executed is True
    assert result.cycle_status == "recovered"
    assert result.recovery_verified is True
    assert (
        transformation_error_mask(
            result.remediation.output_dataframe
        ).sum()
        == 0
    )


def test_schema_drift_waits_for_human_approval(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Human-gated schema remediation must never auto-execute."""

    injected = inject_schema_drift(
        baseline_dataframe,
        "medium",
    )

    result = run_dataframe_self_healing_cycle(
        observed_dataframe=injected.dataframe,
        baseline_dataframe=baseline_dataframe,
    )

    assert (
        result.classification.predicted_root_cause
        == "schema_drift"
    )
    assert result.policy_decision.requires_human_approval is True
    assert result.remediation.executed is False
    assert (
        result.remediation.status
        == "pending_human_approval"
    )
    assert (
        result.cycle_status
        == "awaiting_human_approval"
    )
    assert result.recovery_verified is False


def test_source_failure_schedules_recovery(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Source exceptions must schedule controlled retries."""

    result = run_dataframe_self_healing_cycle(
        observed_dataframe=baseline_dataframe,
        baseline_dataframe=baseline_dataframe,
        exception=SimulatedTimeoutError(
            "Source request exceeded timeout"
        ),
    )

    assert (
        result.classification.predicted_root_cause
        == "source_failure"
    )
    assert (
        result.policy_decision.action
        == "retry_with_exponential_backoff"
    )
    assert result.remediation.executed is True
    assert result.remediation.status == "retry_scheduled"
    assert result.remediation.retry_schedule_seconds == [
        1,
        2,
        4,
    ]
    assert result.cycle_status == "recovery_scheduled"
    assert result.recovery_verified is False


@pytest.mark.parametrize(
    "severity",
    ["low", "medium", "high"],
)
def test_corrupted_artifact_is_recovered_end_to_end(
    baseline_dataframe: pd.DataFrame,
    tmp_path: Path,
    severity: str,
) -> None:
    """Corrupted output artifacts must be regenerated and verified."""

    trusted = tmp_path / "trusted.bin"
    trusted.write_bytes(bytes(range(256)) * 10)

    corrupted = tmp_path / f"corrupted-{severity}.bin"

    inject_output_corruption(
        source_path=trusted,
        destination_path=corrupted,
        severity=severity,
    )

    expected_checksum = calculate_sha256(trusted)

    result = run_artifact_self_healing_cycle(
        artifact_path=corrupted,
        expected_sha256=expected_checksum,
        trusted_source_path=trusted,
        regenerated_destination_path=corrupted,
        dataframe=baseline_dataframe,
    )

    assert (
        result.detection.detected_failure_category
        == "output_artifact_corruption"
    )
    assert (
        result.classification.predicted_root_cause
        == "output_artifact_corruption"
    )
    assert (
        result.policy_decision.action
        == "regenerate_output_artifact"
    )
    assert result.remediation.executed is True
    assert result.cycle_status == "recovered"
    assert result.recovery_verified is True
    assert calculate_sha256(corrupted) == expected_checksum
    assert (
        result.verification_evidence[
            "post_recovery_checksum_match"
        ]
        is True
    )


def test_healthy_artifact_cycle(
    baseline_dataframe: pd.DataFrame,
    tmp_path: Path,
) -> None:
    """A valid artifact must remain healthy."""

    artifact = tmp_path / "valid.bin"
    artifact.write_bytes(b"valid-pipeline-artifact")

    checksum = calculate_sha256(artifact)

    result = run_artifact_self_healing_cycle(
        artifact_path=artifact,
        expected_sha256=checksum,
        trusted_source_path=artifact,
        regenerated_destination_path=artifact,
        dataframe=baseline_dataframe,
    )

    assert result.detection.failure_detected is False
    assert (
        result.classification.predicted_root_cause
        == "healthy_control"
    )
    assert result.cycle_status == "healthy"
    assert result.recovery_verified is True


def test_invalid_detection_mode_raises_error(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Unsupported detector modes must fail explicitly."""

    with pytest.raises(
        ValueError,
        match="detection_mode must be",
    ):
        run_dataframe_self_healing_cycle(
            observed_dataframe=baseline_dataframe,
            baseline_dataframe=baseline_dataframe,
            detection_mode="unsupported",
        )


def test_cycle_result_is_serializable(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Complete cycle evidence must serialize without raw dataframes."""

    result = run_dataframe_self_healing_cycle(
        observed_dataframe=baseline_dataframe,
        baseline_dataframe=baseline_dataframe,
    )

    serialized = result.to_dict()

    assert serialized["cycle_status"] == "healthy"
    assert serialized["recovery_verified"] is True
    assert isinstance(serialized["detection"], dict)
    assert isinstance(serialized["classification"], dict)
    assert isinstance(serialized["policy_decision"], dict)
    assert isinstance(serialized["remediation"], dict)
    assert isinstance(
        serialized["verification_evidence"],
        dict,
    )
    assert (
        "output_dataframe"
        not in serialized["remediation"]
    )
