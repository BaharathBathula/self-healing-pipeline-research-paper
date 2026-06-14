"""End-to-end orchestration for policy-constrained self-healing cycles."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import pandas as pd

from src.classifier import (
    ClassificationResult,
    classify_root_cause,
)
from src.detector import DetectionResult, detect_failure
from src.integrity_detector import (
    detect_output_artifact_integrity,
    detect_transformation_integrity,
)
from src.pipeline import REQUIRED_COLUMNS
from src.policy_engine import (
    DEFAULT_POLICY_PATH,
    PolicyDecision,
    evaluate_remediation_policy,
)
from src.remediation import (
    RemediationExecutionResult,
    execute_remediation,
)


DetectionMode = Literal["standard", "transformation"]


@dataclass(frozen=True)
class SelfHealingCycleResult:
    """Complete evidence produced by one self-healing cycle."""

    detection: DetectionResult
    classification: ClassificationResult
    policy_decision: PolicyDecision
    remediation: RemediationExecutionResult
    cycle_status: str
    recovery_verified: bool
    verification_evidence: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Convert the complete cycle into serializable evidence."""

        return {
            "detection": self.detection.to_dict(),
            "classification": self.classification.to_dict(),
            "policy_decision": self.policy_decision.to_dict(),
            "remediation": self.remediation.to_dict(),
            "cycle_status": self.cycle_status,
            "recovery_verified": self.recovery_verified,
            "verification_evidence": self.verification_evidence,
        }


def _cycle_status(
    *,
    detection: DetectionResult,
    remediation: RemediationExecutionResult,
    recovery_verified: bool,
) -> str:
    """Derive the terminal state of a self-healing cycle."""

    if not detection.failure_detected:
        return "healthy"

    if remediation.status == "pending_human_approval":
        return "awaiting_human_approval"

    if remediation.status == "blocked_by_policy":
        return "blocked_by_policy"

    if remediation.status == "retry_scheduled":
        return "recovery_scheduled"

    if remediation.executed and recovery_verified:
        return "recovered"

    if remediation.executed:
        return "recovery_unverified"

    return "not_recovered"


def _verify_dataframe_recovery(
    *,
    root_cause: str,
    remediation: RemediationExecutionResult,
) -> tuple[bool, dict[str, Any]]:
    """Verify deterministic dataframe remediations."""

    output = remediation.output_dataframe
    evidence: dict[str, Any] = {
        "root_cause": root_cause,
        "remediation_status": remediation.status,
        "output_record_count": len(output),
    }

    if root_cause == "healthy_control":
        evidence["verification_rule"] = "no_failure_detected"
        return True, evidence

    if root_cause == "duplicate_generation":
        if "order_id" not in output.columns:
            evidence["verification_rule"] = "order_id_uniqueness"
            evidence["duplicate_count"] = None
            return False, evidence

        duplicate_count = int(
            output.duplicated(
                subset=["order_id"],
                keep="first",
            ).sum()
        )

        evidence["verification_rule"] = "order_id_uniqueness"
        evidence["duplicate_count"] = duplicate_count

        return duplicate_count == 0, evidence

    if root_cause == "missing_value_spike":
        required_columns_present = [
            column
            for column in REQUIRED_COLUMNS
            if column in output.columns
        ]

        if not required_columns_present:
            evidence["verification_rule"] = (
                "required_field_completeness"
            )
            evidence["remaining_invalid_record_count"] = None
            return False, evidence

        remaining_invalid_count = int(
            output[
                required_columns_present
            ].isna().any(axis=1).sum()
        )

        evidence["verification_rule"] = (
            "required_field_completeness"
        )
        evidence["remaining_invalid_record_count"] = (
            remaining_invalid_count
        )
        evidence["quarantined_record_count"] = len(
            remediation.quarantined_dataframe
        )

        return remaining_invalid_count == 0, evidence

    if root_cause == "transformation_logic_error":
        verification = detect_transformation_integrity(
            output
        )

        remaining_error_count = int(
            verification.triggering_signals.get(
                "transformation_error_count",
                0,
            )
        )

        evidence["verification_rule"] = (
            "derived_total_semantic_integrity"
        )
        evidence["remaining_transformation_error_count"] = (
            remaining_error_count
        )

        return not verification.failure_detected, evidence

    evidence["verification_rule"] = (
        "requires_external_or_deferred_verification"
    )

    return False, evidence


def run_dataframe_self_healing_cycle(
    *,
    observed_dataframe: pd.DataFrame,
    baseline_dataframe: pd.DataFrame,
    exception: Exception | None = None,
    detection_mode: DetectionMode = "standard",
    policy_path: Path | str = DEFAULT_POLICY_PATH,
) -> SelfHealingCycleResult:
    """Run detection through remediation for a dataframe incident."""

    if detection_mode == "standard":
        detection = detect_failure(
            observed_dataframe=observed_dataframe,
            baseline_dataframe=baseline_dataframe,
            exception=exception,
        )
    elif detection_mode == "transformation":
        if exception is not None:
            detection = detect_failure(
                observed_dataframe=observed_dataframe,
                baseline_dataframe=baseline_dataframe,
                exception=exception,
            )
        else:
            detection = detect_transformation_integrity(
                observed_dataframe
            )
    else:
        raise ValueError(
            "detection_mode must be 'standard' or 'transformation'"
        )

    classification = classify_root_cause(detection)

    policy_decision = evaluate_remediation_policy(
        classification=classification,
        severity=detection.severity,
        policy_path=policy_path,
    )

    remediation = execute_remediation(
        decision=policy_decision,
        dataframe=observed_dataframe,
    )

    recovery_verified, verification_evidence = (
        _verify_dataframe_recovery(
            root_cause=classification.predicted_root_cause,
            remediation=remediation,
        )
    )

    status = _cycle_status(
        detection=detection,
        remediation=remediation,
        recovery_verified=recovery_verified,
    )

    return SelfHealingCycleResult(
        detection=detection,
        classification=classification,
        policy_decision=policy_decision,
        remediation=remediation,
        cycle_status=status,
        recovery_verified=recovery_verified,
        verification_evidence=verification_evidence,
    )


def run_artifact_self_healing_cycle(
    *,
    artifact_path: Path | str,
    expected_sha256: str,
    trusted_source_path: Path | str,
    regenerated_destination_path: Path | str,
    dataframe: pd.DataFrame | None = None,
    policy_path: Path | str = DEFAULT_POLICY_PATH,
) -> SelfHealingCycleResult:
    """Run detection through verified recovery for an output artifact."""

    working_dataframe = (
        dataframe.copy()
        if dataframe is not None
        else pd.DataFrame()
    )

    detection = detect_output_artifact_integrity(
        artifact_path=artifact_path,
        expected_sha256=expected_sha256,
    )

    classification = classify_root_cause(detection)

    policy_decision = evaluate_remediation_policy(
        classification=classification,
        severity=detection.severity,
        policy_path=policy_path,
    )

    remediation = execute_remediation(
        decision=policy_decision,
        dataframe=working_dataframe,
        artifact_source_path=trusted_source_path,
        artifact_destination_path=regenerated_destination_path,
    )

    verification_evidence: dict[str, Any] = {
        "verification_rule": "sha256_integrity",
        "regenerated_destination_path": str(
            regenerated_destination_path
        ),
    }

    if detection.failure_detected and remediation.executed:
        verification = detect_output_artifact_integrity(
            artifact_path=regenerated_destination_path,
            expected_sha256=expected_sha256,
        )

        recovery_verified = not verification.failure_detected

        verification_evidence[
            "post_recovery_checksum_match"
        ] = verification.triggering_signals.get(
            "checksum_match",
            False,
        )
    elif not detection.failure_detected:
        recovery_verified = True
        verification_evidence[
            "post_recovery_checksum_match"
        ] = True
    else:
        recovery_verified = False
        verification_evidence[
            "post_recovery_checksum_match"
        ] = False

    status = _cycle_status(
        detection=detection,
        remediation=remediation,
        recovery_verified=recovery_verified,
    )

    return SelfHealingCycleResult(
        detection=detection,
        classification=classification,
        policy_decision=policy_decision,
        remediation=remediation,
        cycle_status=status,
        recovery_verified=recovery_verified,
        verification_evidence=verification_evidence,
    )
