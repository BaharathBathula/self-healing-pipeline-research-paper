"""Deterministic execution of policy-authorized remediation actions."""

from dataclasses import asdict, dataclass, field
from pathlib import Path
from shutil import copy2
from typing import Any

import pandas as pd

from src.output_failure import calculate_sha256
from src.pipeline import REQUIRED_COLUMNS
from src.policy_engine import PolicyDecision


class RemediationExecutionError(RuntimeError):
    """Raised when a remediation action cannot be executed safely."""


@dataclass
class RemediationExecutionResult:
    """Outcome of a remediation execution attempt."""

    action: str
    executed: bool
    status: str
    output_dataframe: pd.DataFrame
    quarantined_dataframe: pd.DataFrame = field(
        default_factory=pd.DataFrame
    )
    retry_schedule_seconds: list[int] = field(
        default_factory=list
    )
    human_approval_required: bool = False
    message: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert execution metadata into a serializable dictionary."""

        result = asdict(self)
        result["output_record_count"] = len(
            self.output_dataframe
        )
        result["quarantined_record_count"] = len(
            self.quarantined_dataframe
        )

        result.pop("output_dataframe")
        result.pop("quarantined_dataframe")

        return result


def _build_retry_schedule(
    *,
    maximum_retries: int,
    initial_delay_seconds: int,
    backoff_multiplier: int,
) -> list[int]:
    """Create a deterministic exponential-backoff schedule."""

    if maximum_retries < 0:
        raise RemediationExecutionError(
            "maximum_retries cannot be negative"
        )

    if initial_delay_seconds < 0:
        raise RemediationExecutionError(
            "initial_delay_seconds cannot be negative"
        )

    if backoff_multiplier < 1:
        raise RemediationExecutionError(
            "backoff_multiplier must be at least 1"
        )

    return [
        initial_delay_seconds
        * (backoff_multiplier ** retry_number)
        for retry_number in range(maximum_retries)
    ]


def _execute_deduplication(
    dataframe: pd.DataFrame,
    parameters: dict[str, Any],
) -> RemediationExecutionResult:
    """Remove duplicate records using configured business keys."""

    key_columns = list(
        parameters.get("key_columns", ["order_id"])
    )

    missing_keys = [
        column
        for column in key_columns
        if column not in dataframe.columns
    ]

    if missing_keys:
        raise RemediationExecutionError(
            "Cannot deduplicate because key columns are missing: "
            + ", ".join(missing_keys)
        )

    deduplicated = dataframe.drop_duplicates(
        subset=key_columns,
        keep="first",
    ).reset_index(drop=True)

    removed_count = len(dataframe) - len(deduplicated)

    return RemediationExecutionResult(
        action="deduplicate_keep_first",
        executed=True,
        status="completed",
        output_dataframe=deduplicated,
        message=(
            f"Removed {removed_count} duplicate records."
        ),
        evidence={
            "input_record_count": len(dataframe),
            "output_record_count": len(deduplicated),
            "removed_duplicate_count": removed_count,
            "key_columns": key_columns,
        },
    )


def _execute_null_quarantine(
    dataframe: pd.DataFrame,
) -> RemediationExecutionResult:
    """Separate records containing nulls in required fields."""

    required_columns_present = [
        column
        for column in REQUIRED_COLUMNS
        if column in dataframe.columns
    ]

    if not required_columns_present:
        raise RemediationExecutionError(
            "No required columns are present for null quarantine"
        )

    invalid_mask = dataframe[
        required_columns_present
    ].isna().any(axis=1)

    quarantined = dataframe.loc[
        invalid_mask
    ].copy().reset_index(drop=True)

    valid = dataframe.loc[
        ~invalid_mask
    ].copy().reset_index(drop=True)

    return RemediationExecutionResult(
        action="quarantine_invalid_rows",
        executed=True,
        status="completed",
        output_dataframe=valid,
        quarantined_dataframe=quarantined,
        message=(
            f"Quarantined {len(quarantined)} invalid records."
        ),
        evidence={
            "input_record_count": len(dataframe),
            "valid_record_count": len(valid),
            "quarantined_record_count": len(quarantined),
            "validated_columns": required_columns_present,
        },
    )


def _execute_recompute_derived_totals(
    dataframe: pd.DataFrame,
    parameters: dict[str, Any],
) -> RemediationExecutionResult:
    """Recompute a derived total from trusted source columns."""

    target_column = str(
        parameters.get(
            "target_column",
            "order_total_local",
        )
    )

    source_columns = list(
        parameters.get(
            "source_columns",
            ["quantity", "unit_price"],
        )
    )

    rounding_precision = int(
        parameters.get(
            "rounding_precision",
            2,
        )
    )

    required_columns = set(
        source_columns + [target_column]
    )

    missing_columns = sorted(
        required_columns.difference(
            dataframe.columns
        )
    )

    if missing_columns:
        raise RemediationExecutionError(
            "Cannot recompute derived totals because columns are missing: "
            + ", ".join(missing_columns)
        )

    if len(source_columns) != 2:
        raise RemediationExecutionError(
            "Derived-total remediation requires exactly two source columns"
        )

    repaired = dataframe.copy(deep=True)

    first_source = pd.to_numeric(
        repaired[source_columns[0]],
        errors="coerce",
    )

    second_source = pd.to_numeric(
        repaired[source_columns[1]],
        errors="coerce",
    )

    if first_source.isna().any() or second_source.isna().any():
        raise RemediationExecutionError(
            "Cannot recompute derived totals from null or non-numeric source values"
        )

    original_values = pd.to_numeric(
        repaired[target_column],
        errors="coerce",
    )

    recomputed_values = (
        first_source * second_source
    ).round(rounding_precision)

    changed_mask = (
        original_values.isna()
        | original_values.ne(recomputed_values)
    )

    repaired.loc[
        :,
        target_column,
    ] = recomputed_values

    repaired_count = int(changed_mask.sum())

    return RemediationExecutionResult(
        action="recompute_derived_totals",
        executed=True,
        status="completed",
        output_dataframe=repaired,
        message=(
            f"Recomputed {repaired_count} derived values "
            f"in '{target_column}'."
        ),
        evidence={
            "target_column": target_column,
            "source_columns": source_columns,
            "rounding_precision": rounding_precision,
            "repaired_record_count": repaired_count,
            "input_record_count": len(dataframe),
            "output_record_count": len(repaired),
        },
    )


def _execute_regenerate_output_artifact(
    *,
    dataframe: pd.DataFrame,
    parameters: dict[str, Any],
    artifact_source_path: Path | str | None,
    artifact_destination_path: Path | str | None,
) -> RemediationExecutionResult:
    """Regenerate a corrupted artifact from a trusted source artifact."""

    if artifact_source_path is None:
        raise RemediationExecutionError(
            "artifact_source_path is required for artifact regeneration"
        )

    if artifact_destination_path is None:
        raise RemediationExecutionError(
            "artifact_destination_path is required for artifact regeneration"
        )

    source = Path(artifact_source_path)
    destination = Path(artifact_destination_path)

    if not source.exists() or not source.is_file():
        raise RemediationExecutionError(
            f"Trusted source artifact does not exist: {source}"
        )

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    copy2(source, destination)

    source_checksum = calculate_sha256(source)
    regenerated_checksum = calculate_sha256(destination)

    verification_required = bool(
        parameters.get(
            "verify_checksum_after_regeneration",
            True,
        )
    )

    checksum_verified = (
        source_checksum == regenerated_checksum
    )

    if verification_required and not checksum_verified:
        raise RemediationExecutionError(
            "Regenerated artifact failed checksum verification"
        )

    return RemediationExecutionResult(
        action="regenerate_output_artifact",
        executed=True,
        status="completed",
        output_dataframe=dataframe.copy(),
        message="Regenerated and verified the output artifact.",
        evidence={
            "source_artifact_path": str(source.resolve()),
            "regenerated_artifact_path": str(
                destination.resolve()
            ),
            "source_sha256": source_checksum,
            "regenerated_sha256": regenerated_checksum,
            "checksum_verified": checksum_verified,
            "regenerated_size_bytes": destination.stat().st_size,
        },
    )


def execute_remediation(
    *,
    decision: PolicyDecision,
    dataframe: pd.DataFrame,
    artifact_source_path: Path | str | None = None,
    artifact_destination_path: Path | str | None = None,
) -> RemediationExecutionResult:
    """Execute a remediation action under policy constraints."""

    working_dataframe = dataframe.copy()

    if not decision.permitted:
        return RemediationExecutionResult(
            action=decision.action,
            executed=False,
            status="blocked_by_policy",
            output_dataframe=working_dataframe,
            human_approval_required=(
                decision.requires_human_approval
            ),
            message=decision.rationale,
            evidence={
                "root_cause": decision.root_cause,
                "severity": decision.severity,
            },
        )

    if decision.requires_human_approval:
        return RemediationExecutionResult(
            action=decision.action,
            executed=False,
            status="pending_human_approval",
            output_dataframe=working_dataframe,
            human_approval_required=True,
            message=decision.rationale,
            evidence={
                "root_cause": decision.root_cause,
                "severity": decision.severity,
            },
        )

    if decision.action == "continue_pipeline":
        return RemediationExecutionResult(
            action=decision.action,
            executed=True,
            status="completed",
            output_dataframe=working_dataframe,
            message="Healthy pipeline execution continued.",
            evidence={
                "record_count": len(working_dataframe),
            },
        )

    if decision.action == "deduplicate_keep_first":
        return _execute_deduplication(
            working_dataframe,
            decision.parameters,
        )

    if decision.action == "quarantine_invalid_rows":
        return _execute_null_quarantine(
            working_dataframe
        )

    if decision.action == "recompute_derived_totals":
        return _execute_recompute_derived_totals(
            working_dataframe,
            decision.parameters,
        )

    if decision.action == "regenerate_output_artifact":
        return _execute_regenerate_output_artifact(
            dataframe=working_dataframe,
            parameters=decision.parameters,
            artifact_source_path=artifact_source_path,
            artifact_destination_path=artifact_destination_path,
        )

    if decision.action == "retry_with_exponential_backoff":
        schedule = _build_retry_schedule(
            maximum_retries=int(
                decision.parameters.get(
                    "maximum_retries",
                    3,
                )
            ),
            initial_delay_seconds=int(
                decision.parameters.get(
                    "initial_delay_seconds",
                    1,
                )
            ),
            backoff_multiplier=int(
                decision.parameters.get(
                    "backoff_multiplier",
                    2,
                )
            ),
        )

        return RemediationExecutionResult(
            action=decision.action,
            executed=True,
            status="retry_scheduled",
            output_dataframe=working_dataframe,
            retry_schedule_seconds=schedule,
            message=(
                f"Scheduled {len(schedule)} source retries."
            ),
            evidence={
                "retry_count": len(schedule),
                "retry_schedule_seconds": schedule,
            },
        )

    if decision.action == "retry_source_refresh":
        maximum_retries = int(
            decision.parameters.get(
                "maximum_retries",
                2,
            )
        )

        schedule = _build_retry_schedule(
            maximum_retries=maximum_retries,
            initial_delay_seconds=1,
            backoff_multiplier=2,
        )

        return RemediationExecutionResult(
            action=decision.action,
            executed=True,
            status="retry_scheduled",
            output_dataframe=working_dataframe,
            retry_schedule_seconds=schedule,
            message=(
                f"Scheduled {len(schedule)} source refresh attempts."
            ),
            evidence={
                "retry_count": len(schedule),
                "retry_schedule_seconds": schedule,
            },
        )

    raise RemediationExecutionError(
        f"Unsupported automatic remediation action: "
        f"{decision.action}"
    )
