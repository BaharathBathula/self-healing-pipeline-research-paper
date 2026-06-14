"""
Multi-signal failure detection for experimental data pipelines."""

from dataclasses import asdict, dataclass
from typing import Any

import pandas as pd

from src.pipeline import REQUIRED_COLUMNS
from src.source_failure import SimulatedSourceError


@dataclass(frozen=True)
class DetectionResult:
    """Outcome produced by the failure detector."""

    failure_detected: bool
    detected_failure_category: str
    confidence: float
    severity: str
    triggering_signals: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Convert the detection result into a serializable dictionary."""

        return asdict(self)


@dataclass(frozen=True)
class DetectionThresholds:
    """Thresholds used by the deterministic failure detector."""

    missing_value_rate: float = 0.05
    duplicate_rate: float = 0.01
    volume_deviation_rate: float = 0.30
    freshness_delay_minutes: float = 60.0


def _severity_from_ratio(ratio: float) -> str:
    """Map an observed anomaly ratio to a severity level."""

    if ratio >= 0.50:
        return "high"

    if ratio >= 0.20:
        return "medium"

    return "low"


def _calculate_required_field_null_rate(
    dataframe: pd.DataFrame,
) -> float:
    """Return the highest null rate among required fields."""

    required_columns_present = [
        column
        for column in REQUIRED_COLUMNS
        if column in dataframe.columns
    ]

    if not required_columns_present or dataframe.empty:
        return 0.0

    per_column_null_rates = (
        dataframe[required_columns_present]
        .isna()
        .mean()
    )

    return float(per_column_null_rates.max())


def _calculate_duplicate_rate(
    dataframe: pd.DataFrame,
) -> float:
    """Calculate duplicate frequency using order_id."""

    if "order_id" not in dataframe.columns or dataframe.empty:
        return 0.0

    duplicate_count = int(
        dataframe.duplicated(
            subset=["order_id"],
            keep="first",
        ).sum()
    )

    return duplicate_count / len(dataframe)


def detect_failure(
    *,
    observed_dataframe: pd.DataFrame,
    baseline_dataframe: pd.DataFrame,
    exception: Exception | None = None,
    thresholds: DetectionThresholds = DetectionThresholds(),
) -> DetectionResult:
    """Detect failures using operational and data-quality signals."""

    signals: dict[str, Any] = {}

    if exception is not None:
        signals["exception_type"] = type(exception).__name__
        signals["exception_message"] = str(exception)

        if isinstance(exception, SimulatedSourceError):
            return DetectionResult(
                failure_detected=True,
                detected_failure_category="source_failure",
                confidence=0.99,
                severity="high",
                triggering_signals=signals,
            )

        return DetectionResult(
            failure_detected=True,
            detected_failure_category="unknown_failure",
            confidence=0.60,
            severity="medium",
            triggering_signals=signals,
        )

    missing_columns = sorted(
        REQUIRED_COLUMNS.difference(
            observed_dataframe.columns
        )
    )

    signals["missing_required_columns"] = missing_columns

    incompatible_types: list[str] = []

    common_columns = set(
        baseline_dataframe.columns
    ).intersection(
        observed_dataframe.columns
    )

    for column in sorted(common_columns):
        baseline_dtype = str(
            baseline_dataframe[column].dtype
        )
        observed_dtype = str(
            observed_dataframe[column].dtype
        )

        if baseline_dtype != observed_dtype:
            incompatible_types.append(
                f"{column}: {baseline_dtype} -> {observed_dtype}"
            )

    signals["incompatible_column_types"] = incompatible_types

    if missing_columns or incompatible_types:
        anomaly_count = (
            len(missing_columns)
            + len(incompatible_types)
        )

        severity = (
            "high"
            if incompatible_types
            else "medium"
        )

        confidence = min(
            0.99,
            0.85 + anomaly_count * 0.04,
        )

        return DetectionResult(
            failure_detected=True,
            detected_failure_category="schema_drift",
            confidence=round(confidence, 3),
            severity=severity,
            triggering_signals=signals,
        )

    duplicate_rate = _calculate_duplicate_rate(
        observed_dataframe
    )

    signals["duplicate_rate"] = round(
        duplicate_rate,
        6,
    )

    if duplicate_rate >= thresholds.duplicate_rate:
        return DetectionResult(
            failure_detected=True,
            detected_failure_category="duplicate_generation",
            confidence=0.96,
            severity=_severity_from_ratio(
                duplicate_rate
            ),
            triggering_signals=signals,
        )

    missing_value_rate = (
        _calculate_required_field_null_rate(
            observed_dataframe
        )
    )

    signals["required_field_null_rate"] = round(
        missing_value_rate,
        6,
    )

    if missing_value_rate >= thresholds.missing_value_rate:
        return DetectionResult(
            failure_detected=True,
            detected_failure_category="missing_value_spike",
            confidence=0.94,
            severity=_severity_from_ratio(
                missing_value_rate
            ),
            triggering_signals=signals,
        )

    if (
        "order_id" in observed_dataframe.columns
        and "order_id" in baseline_dataframe.columns
        and "event_timestamp" in observed_dataframe.columns
        and "event_timestamp" in baseline_dataframe.columns
        and not observed_dataframe.empty
        and not baseline_dataframe.empty
    ):
        baseline_times = baseline_dataframe[
            ["order_id", "event_timestamp"]
        ].rename(
            columns={
                "event_timestamp": "baseline_timestamp",
            }
        )

        observed_times = observed_dataframe[
            ["order_id", "event_timestamp"]
        ].rename(
            columns={
                "event_timestamp": "observed_timestamp",
            }
        )

        matched_times = observed_times.merge(
            baseline_times,
            on="order_id",
            how="inner",
        )

        if not matched_times.empty:
            matched_times["baseline_timestamp"] = pd.to_datetime(
                matched_times["baseline_timestamp"],
                utc=True,
            )

            matched_times["observed_timestamp"] = pd.to_datetime(
                matched_times["observed_timestamp"],
                utc=True,
            )

            delays_minutes = (
                matched_times["baseline_timestamp"]
                - matched_times["observed_timestamp"]
            ).dt.total_seconds() / 60

            stale_records = delays_minutes.ge(
                thresholds.freshness_delay_minutes
            )

            stale_record_rate = float(
                stale_records.mean()
            )

            maximum_delay_minutes = max(
                0.0,
                float(delays_minutes.max()),
            )

            signals["stale_record_rate"] = round(
                stale_record_rate,
                6,
            )

            signals["maximum_freshness_delay_minutes"] = round(
                maximum_delay_minutes,
                3,
            )

            if stale_record_rate > 0:
                return DetectionResult(
                    failure_detected=True,
                    detected_failure_category="freshness_violation",
                    confidence=0.92,
                    severity=_severity_from_ratio(
                        stale_record_rate
                    ),
                    triggering_signals=signals,
                )

    baseline_count = len(baseline_dataframe)
    observed_count = len(observed_dataframe)

    if baseline_count > 0:
        volume_deviation_rate = abs(
            observed_count - baseline_count
        ) / baseline_count
    else:
        volume_deviation_rate = 0.0

    signals["baseline_record_count"] = baseline_count
    signals["observed_record_count"] = observed_count
    signals["volume_deviation_rate"] = round(
        volume_deviation_rate,
        6,
    )

    if volume_deviation_rate >= thresholds.volume_deviation_rate:
        return DetectionResult(
            failure_detected=True,
            detected_failure_category="volume_anomaly",
            confidence=0.90,
            severity=_severity_from_ratio(
                volume_deviation_rate
            ),
            triggering_signals=signals,
        )

    return DetectionResult(
        failure_detected=False,
        detected_failure_category="healthy_control",
        confidence=0.99,
        severity="none",
        triggering_signals=signals,
    )