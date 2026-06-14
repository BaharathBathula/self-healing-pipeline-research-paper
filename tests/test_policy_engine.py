"""Tests for remediation policy evaluation."""

from pathlib import Path

import pytest
import yaml

from src.classifier import ClassificationResult
from src.policy_engine import (
    PolicyConfigurationError,
    evaluate_remediation_policy,
    load_policy_configuration,
)


def classification(
    root_cause: str,
    *,
    unknown: bool = False,
) -> ClassificationResult:
    """Create a classification result for policy tests."""

    return ClassificationResult(
        predicted_root_cause=root_cause,
        confidence=0.95,
        alternative_causes=[],
        supporting_evidence={},
        unknown_classification=unknown,
    )


def test_policy_configuration_loads() -> None:
    """The default policy file must load successfully."""

    configuration = load_policy_configuration()

    assert configuration["version"] == "1.0"
    assert len(configuration["policies"]) == 8


@pytest.mark.parametrize(
    ("root_cause", "severity", "expected_action"),
    [
        (
            "source_failure",
            "high",
            "retry_with_exponential_backoff",
        ),
        (
            "missing_value_spike",
            "medium",
            "quarantine_invalid_rows",
        ),
        (
            "duplicate_generation",
            "low",
            "deduplicate_keep_first",
        ),
        (
            "freshness_violation",
            "high",
            "retry_source_refresh",
        ),
    ],
)
def test_automatic_policies_are_authorized(
    root_cause: str,
    severity: str,
    expected_action: str,
) -> None:
    """Approved automatic policies must not require human approval."""

    decision = evaluate_remediation_policy(
        classification=classification(root_cause),
        severity=severity,
    )

    assert decision.action == expected_action
    assert decision.automatic is True
    assert decision.requires_human_approval is False
    assert decision.permitted is True


@pytest.mark.parametrize(
    ("root_cause", "expected_action"),
    [
        ("schema_drift", "quarantine_and_alert"),
        ("volume_anomaly", "hold_and_alert"),
        (
            "unknown_failure",
            "escalate_for_manual_review",
        ),
    ],
)
def test_manual_policies_require_approval(
    root_cause: str,
    expected_action: str,
) -> None:
    """Restricted policies must require human authorization."""

    decision = evaluate_remediation_policy(
        classification=classification(
            root_cause,
            unknown=root_cause == "unknown_failure",
        ),
        severity="medium",
    )

    assert decision.action == expected_action
    assert decision.requires_human_approval is True
    assert decision.permitted is True


def test_healthy_control_continues_pipeline() -> None:
    """Healthy executions must be allowed to continue."""

    decision = evaluate_remediation_policy(
        classification=classification("healthy_control"),
        severity="none",
    )

    assert decision.action == "continue_pipeline"
    assert decision.automatic is True
    assert decision.requires_human_approval is False
    assert decision.permitted is True


def test_unconfigured_cause_uses_unknown_fallback() -> None:
    """Unrecognized classifications must use the safe fallback."""

    decision = evaluate_remediation_policy(
        classification=classification(
            "unrecognized_root_cause"
        ),
        severity="high",
    )

    assert decision.root_cause == "unknown_failure"
    assert decision.action == "escalate_for_manual_review"
    assert decision.requires_human_approval is True


def test_invalid_severity_is_not_permitted() -> None:
    """A severity outside policy constraints must be denied."""

    decision = evaluate_remediation_policy(
        classification=classification(
            "duplicate_generation"
        ),
        severity="critical",
    )

    assert decision.permitted is False
    assert "not permitted" in decision.rationale


def test_unknown_classification_forces_approval() -> None:
    """Ambiguous classifications must never auto-execute."""

    decision = evaluate_remediation_policy(
        classification=classification(
            "source_failure",
            unknown=True,
        ),
        severity="high",
    )

    assert decision.automatic is True
    assert decision.requires_human_approval is True


def test_policy_parameters_are_returned() -> None:
    """Action parameters must be included in the decision."""

    decision = evaluate_remediation_policy(
        classification=classification("source_failure"),
        severity="high",
    )

    assert decision.parameters["maximum_retries"] == 3
    assert decision.parameters["backoff_multiplier"] == 2


def test_policy_decision_is_serializable() -> None:
    """Policy decisions must support evidence persistence."""

    decision = evaluate_remediation_policy(
        classification=classification(
            "duplicate_generation"
        ),
        severity="medium",
    )

    serialized = decision.to_dict()

    assert serialized["root_cause"] == "duplicate_generation"
    assert serialized["action"] == "deduplicate_keep_first"
    assert isinstance(serialized["parameters"], dict)


def test_missing_policy_file_raises_error(
    tmp_path: Path,
) -> None:
    """Missing configuration files must fail safely."""

    missing_path = tmp_path / "missing.yaml"

    with pytest.raises(
        PolicyConfigurationError,
        match="does not exist",
    ):
        load_policy_configuration(missing_path)


def test_invalid_yaml_raises_error(
    tmp_path: Path,
) -> None:
    """Malformed YAML must raise a configuration error."""

    invalid_path = tmp_path / "invalid.yaml"
    invalid_path.write_text(
        "policies: [invalid",
        encoding="utf-8",
    )

    with pytest.raises(
        PolicyConfigurationError,
        match="Invalid YAML",
    ):
        load_policy_configuration(invalid_path)


def test_missing_required_section_raises_error(
    tmp_path: Path,
) -> None:
    """Incomplete configuration must fail validation."""

    invalid_path = tmp_path / "incomplete.yaml"
    invalid_path.write_text(
        yaml.safe_dump(
            {
                "version": "1.0",
                "policies": {},
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        PolicyConfigurationError,
        match="Missing policy sections",
    ):
        load_policy_configuration(invalid_path)


def test_missing_policy_fields_raise_error(
    tmp_path: Path,
) -> None:
    """Policies missing mandatory fields must be rejected."""

    invalid_path = tmp_path / "missing-fields.yaml"

    configuration = {
        "version": "1.0",
        "global_constraints": {},
        "policies": {
            "duplicate_generation": {
                "action": "deduplicate_keep_first",
            },
            "unknown_failure": {
                "action": "escalate_for_manual_review",
                "automatic": False,
                "allowed_severities": [
                    "low",
                    "medium",
                    "high",
                ],
            },
        },
    }

    invalid_path.write_text(
        yaml.safe_dump(configuration),
        encoding="utf-8",
    )

    with pytest.raises(
        PolicyConfigurationError,
        match="missing fields",
    ):
        evaluate_remediation_policy(
            classification=classification(
                "duplicate_generation"
            ),
            severity="medium",
            policy_path=invalid_path,
        )
