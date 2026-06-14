"""Tests for policy-authorized remediation execution."""

import pandas as pd
import pytest

from src.data_generator import DatasetConfig, generate_orders
from src.policy_engine import PolicyDecision
from src.remediation import (
    RemediationExecutionError,
    execute_remediation,
)


@pytest.fixture
def baseline_dataframe() -> pd.DataFrame:
    """Create deterministic baseline data."""

    return generate_orders(
        DatasetConfig(
            row_count=100,
            random_seed=42,
        )
    )


def decision(
    *,
    root_cause: str,
    severity: str,
    action: str,
    automatic: bool = True,
    requires_human_approval: bool = False,
    permitted: bool = True,
    parameters: dict | None = None,
) -> PolicyDecision:
    """Create a policy decision for executor tests."""

    return PolicyDecision(
        root_cause=root_cause,
        severity=severity,
        action=action,
        automatic=automatic,
        requires_human_approval=requires_human_approval,
        permitted=permitted,
        parameters=parameters or {},
        rationale="Test policy decision.",
    )


def test_healthy_pipeline_continues(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Healthy data must pass through unchanged."""

    result = execute_remediation(
        decision=decision(
            root_cause="healthy_control",
            severity="none",
            action="continue_pipeline",
        ),
        dataframe=baseline_dataframe,
    )

    assert result.executed is True
    assert result.status == "completed"
    assert len(result.output_dataframe) == len(
        baseline_dataframe
    )
    pd.testing.assert_frame_equal(
        result.output_dataframe,
        baseline_dataframe,
    )


def test_duplicate_records_are_removed(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Duplicate remediation must preserve the first record."""

    duplicated = pd.concat(
        [
            baseline_dataframe,
            baseline_dataframe.iloc[:10],
        ],
        ignore_index=True,
    )

    result = execute_remediation(
        decision=decision(
            root_cause="duplicate_generation",
            severity="medium",
            action="deduplicate_keep_first",
            parameters={
                "key_columns": ["order_id"],
            },
        ),
        dataframe=duplicated,
    )

    assert result.executed is True
    assert result.status == "completed"
    assert len(result.output_dataframe) == 100
    assert result.evidence["removed_duplicate_count"] == 10
    assert (
        result.output_dataframe["order_id"]
        .duplicated()
        .sum()
        == 0
    )


def test_invalid_rows_are_quarantined(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Rows containing required-field nulls must be separated."""

    corrupted = baseline_dataframe.copy()
    corrupted.loc[:4, "customer_id"] = None
    corrupted.loc[5:9, "quantity"] = None

    result = execute_remediation(
        decision=decision(
            root_cause="missing_value_spike",
            severity="medium",
            action="quarantine_invalid_rows",
        ),
        dataframe=corrupted,
    )

    assert result.executed is True
    assert result.status == "completed"
    assert len(result.quarantined_dataframe) == 10
    assert len(result.output_dataframe) == 90
    assert result.evidence["quarantined_record_count"] == 10


def test_source_failure_creates_retry_schedule(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Source remediation must produce exponential backoff."""

    result = execute_remediation(
        decision=decision(
            root_cause="source_failure",
            severity="high",
            action="retry_with_exponential_backoff",
            parameters={
                "maximum_retries": 3,
                "initial_delay_seconds": 1,
                "backoff_multiplier": 2,
            },
        ),
        dataframe=baseline_dataframe,
    )

    assert result.executed is True
    assert result.status == "retry_scheduled"
    assert result.retry_schedule_seconds == [1, 2, 4]


def test_freshness_failure_creates_refresh_schedule(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Freshness remediation must schedule source refreshes."""

    result = execute_remediation(
        decision=decision(
            root_cause="freshness_violation",
            severity="high",
            action="retry_source_refresh",
            parameters={
                "maximum_retries": 2,
            },
        ),
        dataframe=baseline_dataframe,
    )

    assert result.executed is True
    assert result.status == "retry_scheduled"
    assert result.retry_schedule_seconds == [1, 2]


@pytest.mark.parametrize(
    ("root_cause", "action"),
    [
        ("schema_drift", "quarantine_and_alert"),
        ("volume_anomaly", "hold_and_alert"),
        (
            "unknown_failure",
            "escalate_for_manual_review",
        ),
    ],
)
def test_manual_actions_are_not_executed(
    baseline_dataframe: pd.DataFrame,
    root_cause: str,
    action: str,
) -> None:
    """Human-gated actions must remain pending."""

    result = execute_remediation(
        decision=decision(
            root_cause=root_cause,
            severity="medium",
            action=action,
            automatic=False,
            requires_human_approval=True,
        ),
        dataframe=baseline_dataframe,
    )

    assert result.executed is False
    assert result.status == "pending_human_approval"
    assert result.human_approval_required is True
    assert len(result.output_dataframe) == len(
        baseline_dataframe
    )


def test_denied_policy_is_blocked(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """A non-permitted action must never execute."""

    result = execute_remediation(
        decision=decision(
            root_cause="duplicate_generation",
            severity="critical",
            action="deduplicate_keep_first",
            permitted=False,
        ),
        dataframe=baseline_dataframe,
    )

    assert result.executed is False
    assert result.status == "blocked_by_policy"


def test_deduplication_requires_configured_keys(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Missing business keys must fail safely."""

    with pytest.raises(
        RemediationExecutionError,
        match="key columns are missing",
    ):
        execute_remediation(
            decision=decision(
                root_cause="duplicate_generation",
                severity="medium",
                action="deduplicate_keep_first",
                parameters={
                    "key_columns": ["missing_key"],
                },
            ),
            dataframe=baseline_dataframe,
        )


def test_null_quarantine_requires_required_columns() -> None:
    """Quarantine must fail when no required columns exist."""

    dataframe = pd.DataFrame(
        {
            "unrelated_column": [1, 2, 3],
        }
    )

    with pytest.raises(
        RemediationExecutionError,
        match="No required columns",
    ):
        execute_remediation(
            decision=decision(
                root_cause="missing_value_spike",
                severity="medium",
                action="quarantine_invalid_rows",
            ),
            dataframe=dataframe,
        )


def test_invalid_retry_configuration_fails(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Unsafe retry configuration must be rejected."""

    with pytest.raises(
        RemediationExecutionError,
        match="backoff_multiplier",
    ):
        execute_remediation(
            decision=decision(
                root_cause="source_failure",
                severity="high",
                action="retry_with_exponential_backoff",
                parameters={
                    "maximum_retries": 3,
                    "initial_delay_seconds": 1,
                    "backoff_multiplier": 0,
                },
            ),
            dataframe=baseline_dataframe,
        )


def test_unsupported_automatic_action_fails(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Unknown automatic actions must not execute silently."""

    with pytest.raises(
        RemediationExecutionError,
        match="Unsupported automatic remediation action",
    ):
        execute_remediation(
            decision=decision(
                root_cause="source_failure",
                severity="high",
                action="unsupported_action",
            ),
            dataframe=baseline_dataframe,
        )


def test_execution_result_is_serializable(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Execution metadata must support evidence persistence."""

    result = execute_remediation(
        decision=decision(
            root_cause="healthy_control",
            severity="none",
            action="continue_pipeline",
        ),
        dataframe=baseline_dataframe,
    )

    serialized = result.to_dict()

    assert serialized["action"] == "continue_pipeline"
    assert serialized["executed"] is True
    assert serialized["output_record_count"] == 100
    assert serialized["quarantined_record_count"] == 0
    assert "output_dataframe" not in serialized
    assert "quarantined_dataframe" not in serialized
