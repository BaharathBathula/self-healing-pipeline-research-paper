"""Tests for integrity-related root-cause classification."""

from pathlib import Path

import pandas as pd
import pytest

from src.classifier import classify_root_cause
from src.data_generator import DatasetConfig, generate_orders
from src.integrity_detector import (
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


@pytest.mark.parametrize(
    "severity",
    ["low", "medium", "high"],
)
def test_transformation_failure_classification(
    baseline_dataframe: pd.DataFrame,
    severity: str,
) -> None:
    """Semantic transformation defects must be classified correctly."""

    injected = inject_transformation_logic_error(
        baseline_dataframe,
        severity,
        random_seed=12,
    )

    detection = detect_transformation_integrity(
        injected.dataframe
    )

    result = classify_root_cause(detection)

    assert (
        result.predicted_root_cause
        == "transformation_logic_error"
    )
    assert result.confidence >= 0.90
    assert result.unknown_classification is False
    assert (
        result.supporting_evidence[
            "transformation_error_count"
        ]
        == injected.affected_record_count
    )
    assert (
        result.supporting_evidence[
            "transformation_error_rate"
        ]
        > 0
    )


@pytest.mark.parametrize(
    "severity",
    ["low", "medium", "high"],
)
def test_output_corruption_classification(
    tmp_path: Path,
    severity: str,
) -> None:
    """Checksum failures must classify as output corruption."""

    source = tmp_path / "source.bin"
    source.write_bytes(bytes(range(256)) * 10)

    expected_checksum = calculate_sha256(source)
    corrupted = tmp_path / f"corrupted-{severity}.bin"

    inject_output_corruption(
        source_path=source,
        destination_path=corrupted,
        severity=severity,
    )

    detection = detect_output_artifact_integrity(
        artifact_path=corrupted,
        expected_sha256=expected_checksum,
    )

    result = classify_root_cause(detection)

    assert (
        result.predicted_root_cause
        == "output_artifact_corruption"
    )
    assert result.confidence == 1.0
    assert result.unknown_classification is False
    assert (
        result.supporting_evidence["checksum_match"]
        is False
    )
    assert "observed_sha256" in result.supporting_evidence
    assert "expected_sha256" in result.supporting_evidence


def test_missing_artifact_classification(
    tmp_path: Path,
) -> None:
    """Missing artifacts must classify as output corruption."""

    missing = tmp_path / "missing.bin"

    detection = detect_output_artifact_integrity(
        artifact_path=missing,
        expected_sha256="0" * 64,
    )

    result = classify_root_cause(detection)

    assert (
        result.predicted_root_cause
        == "output_artifact_corruption"
    )
    assert result.confidence == 1.0
    assert (
        result.supporting_evidence["integrity_error_type"]
        == "FileNotFoundError"
    )


def test_healthy_transformation_remains_healthy(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """A valid transformation must remain classified as healthy."""

    detection = detect_transformation_integrity(
        baseline_dataframe
    )

    result = classify_root_cause(detection)

    assert result.predicted_root_cause == "healthy_control"
    assert result.confidence == 1.0
    assert result.unknown_classification is False


def test_valid_artifact_remains_healthy(
    tmp_path: Path,
) -> None:
    """A valid output artifact must remain classified as healthy."""

    artifact = tmp_path / "valid.bin"
    artifact.write_bytes(b"valid-pipeline-output")

    checksum = calculate_sha256(artifact)

    detection = detect_output_artifact_integrity(
        artifact_path=artifact,
        expected_sha256=checksum,
    )

    result = classify_root_cause(detection)

    assert result.predicted_root_cause == "healthy_control"
    assert result.confidence == 1.0
    assert result.unknown_classification is False


def test_integrity_classification_is_serializable(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Integrity classification must support evidence persistence."""

    injected = inject_transformation_logic_error(
        baseline_dataframe,
        "medium",
    )

    detection = detect_transformation_integrity(
        injected.dataframe
    )

    result = classify_root_cause(detection)
    serialized = result.to_dict()

    assert (
        serialized["predicted_root_cause"]
        == "transformation_logic_error"
    )
    assert isinstance(
        serialized["supporting_evidence"],
        dict,
    )
    assert isinstance(
        serialized["alternative_causes"],
        list,
    )
