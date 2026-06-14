

"""Tests for multi-signal pipeline failure detection."""

import pandas as pd
import pytest

from src.data_generator import DatasetConfig, generate_orders
from src.detector import DetectionThresholds, detect_failure
from src.failure_injection import (
    inject_duplicate_generation,
    inject_freshness_violation,
    inject_missing_value_spike,
    inject_schema_drift,
    inject_volume_anomaly,
)
from src.source_failure import SimulatedTimeoutError


@pytest.fixture
def baseline_dataframe() -> pd.DataFrame:
    """Create a deterministic healthy baseline dataset."""

    return generate_orders(
        DatasetConfig(
            row_count=100,
            random_seed=42,
        )
    )


def test_healthy_dataset_is_not_flagged(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Healthy data must not generate an incident."""

    result = detect_failure(
        observed_dataframe=baseline_dataframe.copy(),
        baseline_dataframe=baseline_dataframe,
    )

    assert result.failure_detected is False
    assert result.detected_failure_category == "healthy_control"
    assert result.severity == "none"


@pytest.mark.parametrize("severity", ["low", "medium", "high"])
def test_schema_drift_is_detected(
    baseline_dataframe: pd.DataFrame,
    severity: str,
) -> None:
    """All schema-drift levels must be detected."""

    injected = inject_schema_drift(
        baseline_dataframe,
        severity,
    )

    result = detect_failure(
        observed_dataframe=injected.dataframe,
        baseline_dataframe=baseline_dataframe,
    )

    assert result.failure_detected is True
    assert result.detected_failure_category == "schema_drift"


@pytest.mark.parametrize("severity", ["low", "medium", "high"])
def test_duplicate_generation_is_detected(
    baseline_dataframe: pd.DataFrame,
    severity: str,
) -> None:
    """Duplicate records must be detected."""

    injected = inject_duplicate_generation(
        baseline_dataframe,
        severity,
    )

    result = detect_failure(
        observed_dataframe=injected.dataframe,
        baseline_dataframe=baseline_dataframe,
    )

    assert result.failure_detected is True
    assert result.detected_failure_category == "duplicate_generation"


@pytest.mark.parametrize("severity", ["low", "medium", "high"])
def test_missing_value_spike_is_detected(
    baseline_dataframe: pd.DataFrame,
    severity: str,
) -> None:
    """Required-field null spikes must be detected."""

    injected = inject_missing_value_spike(
        baseline_dataframe,
        severity,
    )

    result = detect_failure(
        observed_dataframe=injected.dataframe,
        baseline_dataframe=baseline_dataframe,
    )

    assert result.failure_detected is True
    assert result.detected_failure_category == "missing_value_spike"


@pytest.mark.parametrize("severity", ["medium", "high"])
def test_freshness_violation_is_detected(
    baseline_dataframe: pd.DataFrame,
    severity: str,
) -> None:
    """Stale data beyond the default threshold must be detected."""

    injected = inject_freshness_violation(
        baseline_dataframe,
        severity,
    )

    result = detect_failure(
        observed_dataframe=injected.dataframe,
        baseline_dataframe=baseline_dataframe,
    )

    assert result.failure_detected is True
    assert result.detected_failure_category == "freshness_violation"


def test_low_freshness_uses_configured_threshold(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """A custom threshold must detect a low freshness delay."""

    injected = inject_freshness_violation(
        baseline_dataframe,
        "low",
    )

    default_result = detect_failure(
        observed_dataframe=injected.dataframe,
        baseline_dataframe=baseline_dataframe,
    )

    custom_result = detect_failure(
        observed_dataframe=injected.dataframe,
        baseline_dataframe=baseline_dataframe,
        thresholds=DetectionThresholds(
            freshness_delay_minutes=15,
        ),
    )

    assert default_result.detected_failure_category == "healthy_control"
    assert custom_result.detected_failure_category == "freshness_violation"


@pytest.mark.parametrize("severity", ["low", "medium", "high"])
def test_volume_decrease_is_detected(
    baseline_dataframe: pd.DataFrame,
    severity: str,
) -> None:
    """Abnormal input-volume decreases must be detected."""

    injected = inject_volume_anomaly(
        baseline_dataframe,
        severity,
        direction="decrease",
    )

    result = detect_failure(
        observed_dataframe=injected.dataframe,
        baseline_dataframe=baseline_dataframe,
    )

    assert result.failure_detected is True
    assert result.detected_failure_category == "volume_anomaly"


def test_source_exception_is_detected(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Source exceptions must map to source failure."""

    result = detect_failure(
        observed_dataframe=baseline_dataframe,
        baseline_dataframe=baseline_dataframe,
        exception=SimulatedTimeoutError(
            "Source request exceeded the configured timeout"
        ),
    )

    assert result.failure_detected is True
    assert result.detected_failure_category == "source_failure"
    assert result.confidence == 0.99


def test_unknown_exception_is_escalated(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Unexpected exceptions must become unknown failures."""

    result = detect_failure(
        observed_dataframe=baseline_dataframe,
        baseline_dataframe=baseline_dataframe,
        exception=RuntimeError("Unexpected internal failure"),
    )

    assert result.failure_detected is True
    assert result.detected_failure_category == "unknown_failure"
    assert result.confidence == 0.60


def test_schema_detection_has_precedence(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Schema drift must be identified before duplicate anomalies."""

    schema_data = inject_schema_drift(
        baseline_dataframe,
        "medium",
    ).dataframe

    duplicated = pd.concat(
        [schema_data, schema_data.iloc[:20]],
        ignore_index=True,
    )

    result = detect_failure(
        observed_dataframe=duplicated,
        baseline_dataframe=baseline_dataframe,
    )

    assert result.detected_failure_category == "schema_drift"


def test_detection_result_is_serializable(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Detection output must convert to a dictionary."""

    result = detect_failure(
        observed_dataframe=baseline_dataframe,
        baseline_dataframe=baseline_dataframe,
    )

    serialized = result.to_dict()

    assert serialized["failure_detected"] is False
    assert serialized["detected_failure_category"] == "healthy_control"
    assert isinstance(serialized["triggering_signals"], dict)