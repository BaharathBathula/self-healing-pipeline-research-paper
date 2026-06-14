"""Controlled input-data failure injection for reproducible experiments."""

from dataclasses import dataclass
from math import ceil
from typing import Any, Literal

import pandas as pd


Severity = Literal["low", "medium", "high"]
VolumeDirection = Literal["decrease", "increase"]


@dataclass(frozen=True)
class FailureInjectionResult:
    """Result of applying a controlled failure to a dataset."""

    dataframe: pd.DataFrame
    failure_category: str
    severity: Severity
    affected_record_count: int
    metadata: dict[str, Any]


SEVERITY_FRACTIONS: dict[Severity, float] = {
    "low": 0.10,
    "medium": 0.25,
    "high": 0.50,
}


def _validate_severity(severity: str) -> Severity:
    """Validate and return a supported severity value."""

    if severity not in SEVERITY_FRACTIONS:
        raise ValueError(
            "severity must be one of: low, medium, high"
        )

    return severity  # type: ignore[return-value]


def _affected_count(
    dataframe: pd.DataFrame,
    severity: Severity,
) -> int:
    """Calculate how many rows should be modified."""

    if dataframe.empty:
        return 0

    return min(
        len(dataframe),
        max(
            1,
            ceil(
                len(dataframe)
                * SEVERITY_FRACTIONS[severity]
            ),
        ),
    )


def inject_schema_drift(
    dataframe: pd.DataFrame,
    severity: Severity,
) -> FailureInjectionResult:
    """Inject a deterministic schema incompatibility.

    Low severity:
        Rename source_system.

    Medium severity:
        Remove customer_id.

    High severity:
        Convert quantity into incompatible string values.
    """

    validated_severity = _validate_severity(severity)
    modified = dataframe.copy(deep=True)

    if validated_severity == "low":
        if "source_system" not in modified.columns:
            raise ValueError(
                "source_system column is required"
            )

        modified = modified.rename(
            columns={
                "source_system": "source_system_v2",
            }
        )
        mutation = "renamed source_system to source_system_v2"

    elif validated_severity == "medium":
        if "customer_id" not in modified.columns:
            raise ValueError(
                "customer_id column is required"
            )

        modified = modified.drop(
            columns=["customer_id"]
        )
        mutation = "removed customer_id"

    else:
        if "quantity" not in modified.columns:
            raise ValueError(
                "quantity column is required"
            )

        modified["quantity"] = (
            "Q-" + modified["quantity"].astype(str)
        )
        mutation = "converted quantity to incompatible strings"

    return FailureInjectionResult(
        dataframe=modified,
        failure_category="schema_drift",
        severity=validated_severity,
        affected_record_count=len(modified),
        metadata={
            "mutation": mutation,
            "original_columns": list(dataframe.columns),
            "modified_columns": list(modified.columns),
        },
    )


def inject_missing_value_spike(
    dataframe: pd.DataFrame,
    severity: Severity,
    column: str = "customer_id",
) -> FailureInjectionResult:
    """Replace a controlled fraction of a required field with nulls."""

    validated_severity = _validate_severity(severity)

    if column not in dataframe.columns:
        raise ValueError(
            f"Missing target column: {column}"
        )

    modified = dataframe.copy(deep=True)
    affected_count = _affected_count(
        modified,
        validated_severity,
    )

    affected_indices = modified.index[:affected_count]
    modified.loc[affected_indices, column] = None

    return FailureInjectionResult(
        dataframe=modified,
        failure_category="missing_value_spike",
        severity=validated_severity,
        affected_record_count=affected_count,
        metadata={
            "target_column": column,
            "injected_null_fraction": (
                affected_count / len(modified)
                if len(modified) > 0
                else 0.0
            ),
        },
    )


def inject_duplicate_generation(
    dataframe: pd.DataFrame,
    severity: Severity,
) -> FailureInjectionResult:
    """Append a controlled number of duplicate business records."""

    validated_severity = _validate_severity(severity)
    modified = dataframe.copy(deep=True)

    duplicate_count = _affected_count(
        modified,
        validated_severity,
    )

    duplicated_rows = modified.iloc[
        :duplicate_count
    ].copy()

    modified = pd.concat(
        [modified, duplicated_rows],
        ignore_index=True,
    )

    return FailureInjectionResult(
        dataframe=modified,
        failure_category="duplicate_generation",
        severity=validated_severity,
        affected_record_count=duplicate_count,
        metadata={
            "original_record_count": len(dataframe),
            "modified_record_count": len(modified),
            "duplicate_records_added": duplicate_count,
        },
    )


def inject_freshness_violation(
    dataframe: pd.DataFrame,
    severity: Severity,
    timestamp_column: str = "event_timestamp",
) -> FailureInjectionResult:
    """Make part of the dataset artificially stale."""

    validated_severity = _validate_severity(severity)

    if timestamp_column not in dataframe.columns:
        raise ValueError(
            f"Missing timestamp column: {timestamp_column}"
        )

    modified = dataframe.copy(deep=True)
    modified[timestamp_column] = pd.to_datetime(
        modified[timestamp_column],
        utc=True,
    )

    affected_count = _affected_count(
        modified,
        validated_severity,
    )

    delay_minutes = {
        "low": 30,
        "medium": 180,
        "high": 1_440,
    }[validated_severity]

    affected_indices = modified.index[:affected_count]

    modified.loc[
        affected_indices,
        timestamp_column,
    ] = (
        modified.loc[
            affected_indices,
            timestamp_column,
        ]
        - pd.Timedelta(minutes=delay_minutes)
    )

    return FailureInjectionResult(
        dataframe=modified,
        failure_category="freshness_violation",
        severity=validated_severity,
        affected_record_count=affected_count,
        metadata={
            "timestamp_column": timestamp_column,
            "delay_minutes": delay_minutes,
        },
    )


def inject_volume_anomaly(
    dataframe: pd.DataFrame,
    severity: Severity,
    direction: VolumeDirection = "decrease",
) -> FailureInjectionResult:
    """Create an abnormal decrease or increase in input volume."""

    validated_severity = _validate_severity(severity)

    if direction not in {"decrease", "increase"}:
        raise ValueError(
            "direction must be decrease or increase"
        )

    original_count = len(dataframe)

    if direction == "decrease":
        retained_fraction = {
            "low": 0.50,
            "medium": 0.20,
            "high": 0.10,
        }[validated_severity]

        retained_count = max(
            1,
            int(original_count * retained_fraction),
        )

        modified = dataframe.iloc[
            :retained_count
        ].copy()

        affected_count = original_count - retained_count

    else:
        multiplier = {
            "low": 2,
            "medium": 3,
            "high": 5,
        }[validated_severity]

        copies = []

        for copy_number in range(multiplier):
            copy = dataframe.copy(deep=True)

            if copy_number > 0:
                copy["order_id"] = (
                    copy["order_id"].astype(str)
                    + f"-VOL{copy_number}"
                )

            copies.append(copy)

        modified = pd.concat(
            copies,
            ignore_index=True,
        )

        affected_count = len(modified) - original_count

    return FailureInjectionResult(
        dataframe=modified,
        failure_category="volume_anomaly",
        severity=validated_severity,
        affected_record_count=affected_count,
        metadata={
            "direction": direction,
            "original_record_count": original_count,
            "modified_record_count": len(modified),
        },
    )


def apply_failure_injection(
    dataframe: pd.DataFrame,
    failure_category: str,
    severity: Severity,
    **kwargs: Any,
) -> FailureInjectionResult:
    """Apply a supported failure using a common dispatch interface."""

    injectors = {
        "schema_drift": inject_schema_drift,
        "missing_value_spike": inject_missing_value_spike,
        "duplicate_generation": inject_duplicate_generation,
        "freshness_violation": inject_freshness_violation,
        "volume_anomaly": inject_volume_anomaly,
    }

    injector = injectors.get(failure_category)

    if injector is None:
        supported = ", ".join(sorted(injectors))
        raise ValueError(
            f"Unsupported failure category: "
            f"{failure_category}. Supported: {supported}"
        )

    return injector(
        dataframe,
        severity,
        **kwargs,
    )