"""Integrity detection for semantic transformations and output artifacts."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from src.detector import DetectionResult
from src.output_failure import calculate_sha256
from src.transformation_failure import transformation_error_mask


@dataclass(frozen=True)
class IntegrityThresholds:
    """Thresholds used for semantic and artifact integrity detection."""

    transformation_error_rate: float = 0.01


def _severity_from_ratio(ratio: float) -> str:
    """Map an integrity-failure ratio to severity."""

    if ratio >= 0.50:
        return "high"

    if ratio >= 0.20:
        return "medium"

    return "low"


def detect_transformation_integrity(
    dataframe: pd.DataFrame,
    *,
    thresholds: IntegrityThresholds = IntegrityThresholds(),
) -> DetectionResult:
    """Detect semantic violations in derived order totals."""

    error_mask = transformation_error_mask(dataframe)

    error_count = int(error_mask.sum())
    record_count = len(dataframe)

    error_rate = (
        error_count / record_count
        if record_count > 0
        else 0.0
    )

    signals: dict[str, Any] = {
        "transformation_error_count": error_count,
        "transformation_error_rate": round(
            error_rate,
            6,
        ),
        "validated_rule": (
            "order_total_local = quantity * unit_price"
        ),
    }

    if error_rate >= thresholds.transformation_error_rate:
        confidence = min(
            0.99,
            0.80 + error_rate,
        )

        return DetectionResult(
            failure_detected=True,
            detected_failure_category=(
                "transformation_logic_error"
            ),
            confidence=round(confidence, 3),
            severity=_severity_from_ratio(error_rate),
            triggering_signals=signals,
        )

    return DetectionResult(
        failure_detected=False,
        detected_failure_category="healthy_control",
        confidence=0.99,
        severity="none",
        triggering_signals=signals,
    )


def detect_output_artifact_integrity(
    *,
    artifact_path: Path | str,
    expected_sha256: str,
) -> DetectionResult:
    """Detect output corruption using an expected SHA-256 checksum."""

    path = Path(artifact_path)

    signals: dict[str, Any] = {
        "artifact_path": str(path),
        "expected_sha256": expected_sha256,
    }

    try:
        observed_sha256 = calculate_sha256(path)
    except (FileNotFoundError, OSError) as error:
        signals["integrity_error_type"] = type(error).__name__
        signals["integrity_error_message"] = str(error)

        return DetectionResult(
            failure_detected=True,
            detected_failure_category=(
                "output_artifact_corruption"
            ),
            confidence=0.99,
            severity="high",
            triggering_signals=signals,
        )

    signals["observed_sha256"] = observed_sha256
    signals["checksum_match"] = (
        observed_sha256 == expected_sha256
    )
    signals["artifact_size_bytes"] = path.stat().st_size

    if observed_sha256 != expected_sha256:
        return DetectionResult(
            failure_detected=True,
            detected_failure_category=(
                "output_artifact_corruption"
            ),
            confidence=0.99,
            severity="high",
            triggering_signals=signals,
        )

    return DetectionResult(
        failure_detected=False,
        detected_failure_category="healthy_control",
        confidence=0.99,
        severity="none",
        triggering_signals=signals,
    )
