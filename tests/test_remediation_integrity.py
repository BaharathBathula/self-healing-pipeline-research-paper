"""Tests for integrity-failure remediation execution."""

from pathlib import Path

import pandas as pd
import pytest

from src.data_generator import DatasetConfig, generate_orders
from src.output_failure import (
    calculate_sha256,
    inject_output_corruption,
)
from src.policy_engine import PolicyDecision
from src.remediation import (
    RemediationExecutionError,
    execute_remediation,
)
from src.transformation_failure import (
    inject_transformation_logic_error,
    transformation_error_mask,
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


def policy_decision(
    *,
    root_cause: str,
    action: str,
    parameters: dict,
) -> PolicyDecision:
    """Create an authorized automatic policy decision."""

    return PolicyDecision(
        root_cause=root_cause,
        severity="high",
        action=action,
        automatic=True,
        requires_human_approval=False,
        permitted=True,
        parameters=parameters,
        rationale="Authorized automatic remediation.",
    )


@pytest.mark.parametrize(
    "severity",
    ["low", "medium", "high"],
)
def test_transformation_totals_are_recomputed(
    baseline_dataframe: pd.DataFrame,
    severity: str,
) -> None:
    """Semantic total defects must be repaired completely."""

    injected = inject_transformation_logic_error(
        baseline_dataframe,
        severity,
        random_seed=14,
    )

    decision = policy_decision(
        root_cause="transformation_logic_error",
        action="recompute_derived_totals",
        parameters={
            "target_column": "order_total_local",
            "source_columns": [
                "quantity",
                "unit_price",
            ],
            "rounding_precision": 2,
        },
    )

    result = execute_remediation(
        decision=decision,
        dataframe=injected.dataframe,
    )

    assert result.executed is True
    assert result.status == "completed"
    assert result.action == "recompute_derived_totals"
    assert (
        result.evidence["repaired_record_count"]
        == injected.affected_record_count
    )
    assert transformation_error_mask(
        result.output_dataframe
    ).sum() == 0


def test_recomputation_preserves_row_count(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Transformation repair must not add or remove records."""

    injected = inject_transformation_logic_error(
        baseline_dataframe,
        "high",
    )

    decision = policy_decision(
        root_cause="transformation_logic_error",
        action="recompute_derived_totals",
        parameters={
            "target_column": "order_total_local",
            "source_columns": [
                "quantity",
                "unit_price",
            ],
            "rounding_precision": 2,
        },
    )

    result = execute_remediation(
        decision=decision,
        dataframe=injected.dataframe,
    )

    assert len(result.output_dataframe) == len(
        baseline_dataframe
    )


def test_recomputation_requires_source_columns(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Missing trusted source columns must fail safely."""

    invalid = baseline_dataframe.drop(
        columns=["unit_price"]
    )

    decision = policy_decision(
        root_cause="transformation_logic_error",
        action="recompute_derived_totals",
        parameters={
            "target_column": "order_total_local",
            "source_columns": [
                "quantity",
                "unit_price",
            ],
            "rounding_precision": 2,
        },
    )

    with pytest.raises(
        RemediationExecutionError,
        match="columns are missing",
    ):
        execute_remediation(
            decision=decision,
            dataframe=invalid,
        )


def test_recomputation_rejects_null_sources(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Null trusted inputs must prevent automatic recomputation."""

    invalid = baseline_dataframe.copy()
    invalid.loc[0, "quantity"] = None

    decision = policy_decision(
        root_cause="transformation_logic_error",
        action="recompute_derived_totals",
        parameters={
            "target_column": "order_total_local",
            "source_columns": [
                "quantity",
                "unit_price",
            ],
            "rounding_precision": 2,
        },
    )

    with pytest.raises(
        RemediationExecutionError,
        match="null or non-numeric",
    ):
        execute_remediation(
            decision=decision,
            dataframe=invalid,
        )


def test_corrupted_artifact_is_regenerated(
    baseline_dataframe: pd.DataFrame,
    tmp_path: Path,
) -> None:
    """A corrupted artifact must be restored from a trusted source."""

    trusted = tmp_path / "trusted.bin"
    trusted.write_bytes(bytes(range(256)) * 8)

    corrupted = tmp_path / "corrupted.bin"

    inject_output_corruption(
        source_path=trusted,
        destination_path=corrupted,
        severity="high",
    )

    assert calculate_sha256(trusted) != calculate_sha256(
        corrupted
    )

    decision = policy_decision(
        root_cause="output_artifact_corruption",
        action="regenerate_output_artifact",
        parameters={
            "verify_checksum_after_regeneration": True,
            "preserve_corrupted_artifact": True,
        },
    )

    result = execute_remediation(
        decision=decision,
        dataframe=baseline_dataframe,
        artifact_source_path=trusted,
        artifact_destination_path=corrupted,
    )

    assert result.executed is True
    assert result.status == "completed"
    assert result.action == "regenerate_output_artifact"
    assert calculate_sha256(trusted) == calculate_sha256(
        corrupted
    )
    assert result.evidence["checksum_verified"] is True
    assert (
        result.evidence["source_sha256"]
        == result.evidence["regenerated_sha256"]
    )


def test_artifact_regeneration_preserves_dataframe(
    baseline_dataframe: pd.DataFrame,
    tmp_path: Path,
) -> None:
    """Artifact repair must not mutate pipeline records."""

    trusted = tmp_path / "trusted.bin"
    trusted.write_bytes(b"trusted-output")

    regenerated = tmp_path / "regenerated.bin"

    decision = policy_decision(
        root_cause="output_artifact_corruption",
        action="regenerate_output_artifact",
        parameters={
            "verify_checksum_after_regeneration": True,
        },
    )

    result = execute_remediation(
        decision=decision,
        dataframe=baseline_dataframe,
        artifact_source_path=trusted,
        artifact_destination_path=regenerated,
    )

    pd.testing.assert_frame_equal(
        result.output_dataframe,
        baseline_dataframe,
    )


def test_artifact_regeneration_requires_source_path(
    baseline_dataframe: pd.DataFrame,
    tmp_path: Path,
) -> None:
    """Artifact repair must require a trusted source path."""

    decision = policy_decision(
        root_cause="output_artifact_corruption",
        action="regenerate_output_artifact",
        parameters={},
    )

    with pytest.raises(
        RemediationExecutionError,
        match="artifact_source_path is required",
    ):
        execute_remediation(
            decision=decision,
            dataframe=baseline_dataframe,
            artifact_destination_path=(
                tmp_path / "regenerated.bin"
            ),
        )


def test_artifact_regeneration_requires_destination_path(
    baseline_dataframe: pd.DataFrame,
    tmp_path: Path,
) -> None:
    """Artifact repair must require an output destination."""

    trusted = tmp_path / "trusted.bin"
    trusted.write_bytes(b"trusted-output")

    decision = policy_decision(
        root_cause="output_artifact_corruption",
        action="regenerate_output_artifact",
        parameters={},
    )

    with pytest.raises(
        RemediationExecutionError,
        match="artifact_destination_path is required",
    ):
        execute_remediation(
            decision=decision,
            dataframe=baseline_dataframe,
            artifact_source_path=trusted,
        )


def test_missing_trusted_artifact_fails(
    baseline_dataframe: pd.DataFrame,
    tmp_path: Path,
) -> None:
    """A missing trusted artifact must block regeneration."""

    decision = policy_decision(
        root_cause="output_artifact_corruption",
        action="regenerate_output_artifact",
        parameters={},
    )

    with pytest.raises(
        RemediationExecutionError,
        match="Trusted source artifact does not exist",
    ):
        execute_remediation(
            decision=decision,
            dataframe=baseline_dataframe,
            artifact_source_path=tmp_path / "missing.bin",
            artifact_destination_path=tmp_path / "output.bin",
        )


def test_integrity_remediation_result_is_serializable(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Integrity remediation evidence must be serializable."""

    injected = inject_transformation_logic_error(
        baseline_dataframe,
        "medium",
    )

    decision = policy_decision(
        root_cause="transformation_logic_error",
        action="recompute_derived_totals",
        parameters={
            "target_column": "order_total_local",
            "source_columns": [
                "quantity",
                "unit_price",
            ],
            "rounding_precision": 2,
        },
    )

    result = execute_remediation(
        decision=decision,
        dataframe=injected.dataframe,
    )

    serialized = result.to_dict()

    assert serialized["executed"] is True
    assert serialized["action"] == "recompute_derived_totals"
    assert isinstance(serialized["evidence"], dict)
    assert "output_dataframe" not in serialized
