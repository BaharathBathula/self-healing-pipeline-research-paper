"""Tests for semantic and output-artifact integrity detection."""

from pathlib import Path

import pandas as pd
import pytest

from src.data_generator import DatasetConfig, generate_orders
from src.integrity_detector import (
    IntegrityThresholds,
    detect_output_artifact_integrity,
    detect_transformation_integrity,
)
from src.output_failure import (
    calculate_sha256,
    inject_output_corruption,
)
from src.transformation_failure import (
    inject_transformation_logic_error,
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


def test_healthy_transformation_is_not_flagged(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Valid derived totals must remain healthy."""

    result = detect_transformation_integrity(
        baseline_dataframe
    )

    assert result.failure_detected is False
    assert result.detected_failure_category == "healthy_control"
    assert result.confidence == 0.99
    assert result.severity == "none"
    assert (
        result.triggering_signals["transformation_error_count"]
        == 0
    )


@pytest.mark.parametrize(
    ("severity", "expected_error_rate", "expected_severity"),
    [
        ("low", 0.05, "low"),
        ("medium", 0.20, "medium"),
        ("high", 0.50, "high"),
    ],
)
def test_transformation_failures_are_detected(
    baseline_dataframe: pd.DataFrame,
    severity: str,
    expected_error_rate: float,
    expected_severity: str,
) -> None:
    """Injected semantic defects must be detected at every level."""

    injected = inject_transformation_logic_error(
        baseline_dataframe,
        severity,
        random_seed=9,
    )

    result = detect_transformation_integrity(
        injected.dataframe
    )

    assert result.failure_detected is True
    assert (
        result.detected_failure_category
        == "transformation_logic_error"
    )
    assert result.severity == expected_severity
    assert (
        result.triggering_signals["transformation_error_rate"]
        == expected_error_rate
    )
    assert (
        result.triggering_signals["transformation_error_count"]
        == injected.affected_record_count
    )


def test_custom_threshold_can_ignore_small_error_rate(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Threshold configuration must control detection sensitivity."""

    injected = inject_transformation_logic_error(
        baseline_dataframe,
        "low",
        random_seed=5,
    )

    result = detect_transformation_integrity(
        injected.dataframe,
        thresholds=IntegrityThresholds(
            transformation_error_rate=0.10,
        ),
    )

    assert result.failure_detected is False
    assert result.detected_failure_category == "healthy_control"


def test_matching_artifact_checksum_is_healthy(
    tmp_path: Path,
) -> None:
    """A matching checksum must pass integrity validation."""

    artifact = tmp_path / "artifact.bin"
    artifact.write_bytes(bytes(range(128)) * 8)

    expected_checksum = calculate_sha256(artifact)

    result = detect_output_artifact_integrity(
        artifact_path=artifact,
        expected_sha256=expected_checksum,
    )

    assert result.failure_detected is False
    assert result.detected_failure_category == "healthy_control"
    assert result.triggering_signals["checksum_match"] is True
    assert (
        result.triggering_signals["observed_sha256"]
        == expected_checksum
    )


@pytest.mark.parametrize(
    "severity",
    ["low", "medium", "high"],
)
def test_corrupted_artifact_is_detected(
    tmp_path: Path,
    severity: str,
) -> None:
    """Every truncation severity must cause checksum failure."""

    source = tmp_path / "source.bin"
    source.write_bytes(bytes(range(256)) * 10)

    expected_checksum = calculate_sha256(source)
    corrupted = tmp_path / f"corrupted-{severity}.bin"

    inject_output_corruption(
        source_path=source,
        destination_path=corrupted,
        severity=severity,
    )

    result = detect_output_artifact_integrity(
        artifact_path=corrupted,
        expected_sha256=expected_checksum,
    )

    assert result.failure_detected is True
    assert (
        result.detected_failure_category
        == "output_artifact_corruption"
    )
    assert result.confidence == 0.99
    assert result.severity == "high"
    assert result.triggering_signals["checksum_match"] is False
    assert (
        result.triggering_signals["observed_sha256"]
        != expected_checksum
    )


def test_missing_artifact_is_detected(
    tmp_path: Path,
) -> None:
    """A missing output artifact must be treated as corruption."""

    missing = tmp_path / "missing.bin"

    result = detect_output_artifact_integrity(
        artifact_path=missing,
        expected_sha256="0" * 64,
    )

    assert result.failure_detected is True
    assert (
        result.detected_failure_category
        == "output_artifact_corruption"
    )
    assert result.severity == "high"
    assert (
        result.triggering_signals["integrity_error_type"]
        == "FileNotFoundError"
    )


def test_artifact_detection_records_file_size(
    tmp_path: Path,
) -> None:
    """Artifact size must be preserved as detection evidence."""

    artifact = tmp_path / "artifact.bin"
    artifact.write_bytes(b"pipeline-artifact")

    expected_checksum = calculate_sha256(artifact)

    result = detect_output_artifact_integrity(
        artifact_path=artifact,
        expected_sha256=expected_checksum,
    )

    assert (
        result.triggering_signals["artifact_size_bytes"]
        == artifact.stat().st_size
    )


def test_transformation_detection_result_is_serializable(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Transformation detection output must support evidence storage."""

    injected = inject_transformation_logic_error(
        baseline_dataframe,
        "medium",
    )

    result = detect_transformation_integrity(
        injected.dataframe
    )

    serialized = result.to_dict()

    assert serialized["failure_detected"] is True
    assert (
        serialized["detected_failure_category"]
        == "transformation_logic_error"
    )
    assert isinstance(serialized["triggering_signals"], dict)


def test_artifact_detection_result_is_serializable(
    tmp_path: Path,
) -> None:
    """Artifact integrity output must support evidence storage."""

    artifact = tmp_path / "artifact.bin"
    artifact.write_bytes(b"valid-output")

    checksum = calculate_sha256(artifact)

    result = detect_output_artifact_integrity(
        artifact_path=artifact,
        expected_sha256=checksum,
    )

    serialized = result.to_dict()

    assert serialized["failure_detected"] is False
    assert serialized["detected_failure_category"] == "healthy_control"
    assert isinstance(serialized["triggering_signals"], dict)
