"""Deterministic execution of policy-authorized remediation actions."""

from dataclasses import asdict, dataclass, field
from typing import Any

import pandas as pd

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


def execute_remediation(
    *,
    decision: PolicyDecision,
    dataframe: pd.DataFrame,
) -> RemediationExecutionResult:
    """Execute a remediation action under policy constraints.

    The executor never performs real network retries or sleeps. Retry
    policies produce a deterministic schedule for the experiment runner.
    """

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
