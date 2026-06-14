"""Tests for evidence-weighted root-cause classification."""

import pytest

from src.classifier import classify_root_cause
from src.data_generator import DatasetConfig, generate_orders
from src.detector import DetectionResult, detect_failure
from src.failure_injection import (
    inject_duplicate_generation,
    inject_freshness_violation,
    inject_missing_value_spike,
    inject_schema_drift,
    inject_volume_anomaly,
)
from src.source_failure import SimulatedTimeoutError


@pytest.fixture
def baseline_dataframe():
    """Create deterministic healthy data."""

    return generate_orders(
        DatasetConfig(
            row_count=100,
            random_seed=42,
        )
    )


def test_healthy_control_is_classified_correctly(
    baseline_dataframe,
) -> None:
    """Healthy detector output must remain healthy."""

    detection = detect_failure(
        observed_dataframe=baseline_dataframe,
        baseline_dataframe=baseline_dataframe,
    )

    result = classify_root_cause(detection)

    assert result.predicted_root_cause == "healthy_control"
    assert result.confidence == 1.0
    assert result.unknown_classification is False


@pytest.mark.parametrize(
    "severity",
    ["low", "medium", "high"],
)
def test_schema_drift_classification(
    baseline_dataframe,
    severity: str,
) -> None:
    """Schema failures must be classified as schema drift."""

    injected = inject_schema_drift(
        baseline_dataframe,
        severity,
    )

    detection = detect_failure(
        observed_dataframe=injected.dataframe,
        baseline_dataframe=baseline_dataframe,
    )

    result = classify_root_cause(detection)

    assert result.predicted_root_cause == "schema_drift"
    assert result.confidence >= 0.90


def test_duplicate_generation_classification(
    baseline_dataframe,
) -> None:
    """Duplicate signals must map to duplicate generation."""

    injected = inject_duplicate_generation(
        baseline_dataframe,
        "medium",
    )

    detection = detect_failure(
        observed_dataframe=injected.dataframe,
        baseline_dataframe=baseline_dataframe,
    )

    result = classify_root_cause(detection)

    assert result.predicted_root_cause == "duplicate_generation"
    assert result.confidence >= 0.90
    assert "duplicate_rate" in result.supporting_evidence


def test_missing_value_classification(
    baseline_dataframe,
) -> None:
    """Null-rate evidence must map to missing-value failure."""

    injected = inject_missing_value_spike(
        baseline_dataframe,
        "medium",
    )

    detection = detect_failure(
        observed_dataframe=injected.dataframe,
        baseline_dataframe=baseline_dataframe,
    )

    result = classify_root_cause(detection)

    assert result.predicted_root_cause == "missing_value_spike"
    assert result.confidence >= 0.90


def test_freshness_classification(
    baseline_dataframe,
) -> None:
    """Stale-record evidence must map to freshness violation."""

    injected = inject_freshness_violation(
        baseline_dataframe,
        "high",
    )

    detection = detect_failure(
        observed_dataframe=injected.dataframe,
        baseline_dataframe=baseline_dataframe,
    )

    result = classify_root_cause(detection)

    assert result.predicted_root_cause == "freshness_violation"
    assert result.confidence >= 0.90


def test_volume_anomaly_classification(
    baseline_dataframe,
) -> None:
    """Large volume deviation must map to volume anomaly."""

    injected = inject_volume_anomaly(
        baseline_dataframe,
        "high",
        direction="decrease",
    )

    detection = detect_failure(
        observed_dataframe=injected.dataframe,
        baseline_dataframe=baseline_dataframe,
    )

    result = classify_root_cause(detection)

    assert result.predicted_root_cause == "volume_anomaly"
    assert result.confidence >= 0.90


def test_source_failure_classification(
    baseline_dataframe,
) -> None:
    """Controlled source exceptions must map to source failure."""

    detection = detect_failure(
        observed_dataframe=baseline_dataframe,
        baseline_dataframe=baseline_dataframe,
        exception=SimulatedTimeoutError(
            "Source request exceeded the configured timeout"
        ),
    )

    result = classify_root_cause(detection)

    assert result.predicted_root_cause == "source_failure"
    assert result.confidence == 1.0


def test_unknown_exception_classification(
    baseline_dataframe,
) -> None:
    """Unexpected exceptions must remain unknown."""

    detection = detect_failure(
        observed_dataframe=baseline_dataframe,
        baseline_dataframe=baseline_dataframe,
        exception=RuntimeError("Unexpected internal error"),
    )

    result = classify_root_cause(detection)

    assert result.predicted_root_cause == "unknown_failure"
    assert result.unknown_classification is True


def test_conflicting_evidence_becomes_unknown() -> None:
    """Closely competing root causes must be escalated."""

    detection = DetectionResult(
        failure_detected=True,
        detected_failure_category="duplicate_generation",
        confidence=0.80,
        severity="medium",
        triggering_signals={
            "duplicate_rate": 0.10,
            "required_field_null_rate": 0.15,
        },
    )

    result = classify_root_cause(detection)

    assert result.predicted_root_cause == "unknown_failure"
    assert result.confidence == 0.50
    assert result.unknown_classification is True
    assert "conflicting_causes" in result.supporting_evidence


def test_alternative_causes_are_preserved() -> None:
    """Secondary causes must be available for audit evidence."""

    detection = DetectionResult(
        failure_detected=True,
        detected_failure_category="volume_anomaly",
        confidence=0.80,
        severity="medium",
        triggering_signals={
            "volume_deviation_rate": 0.40,
            "duplicate_rate": 0.05,
        },
    )

    result = classify_root_cause(detection)

    assert len(result.alternative_causes) >= 1
    assert result.alternative_causes[0]["cause"] in {
        "duplicate_generation",
        "volume_anomaly",
    }


def test_classification_result_is_serializable(
    baseline_dataframe,
) -> None:
    """Classification output must support evidence storage."""

    detection = detect_failure(
        observed_dataframe=baseline_dataframe,
        baseline_dataframe=baseline_dataframe,
    )

    result = classify_root_cause(detection)
    serialized = result.to_dict()

    assert serialized["predicted_root_cause"] == "healthy_control"
    assert isinstance(serialized["supporting_evidence"], dict)
    assert isinstance(serialized["alternative_causes"], list)