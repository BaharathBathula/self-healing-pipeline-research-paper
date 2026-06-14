"""Policy evaluation for controlled pipeline remediation."""

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

from src.classifier import ClassificationResult


DEFAULT_POLICY_PATH = (
    Path(__file__).resolve().parents[1]
    / "policies"
    / "remediation_policies.yaml"
)


class PolicyConfigurationError(RuntimeError):
    """Raised when remediation policy configuration is invalid."""


@dataclass(frozen=True)
class PolicyDecision:
    """Result of evaluating an incident against remediation policy."""

    root_cause: str
    severity: str
    action: str
    automatic: bool
    requires_human_approval: bool
    permitted: bool
    parameters: dict[str, Any]
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        """Convert the decision into a serializable dictionary."""

        return asdict(self)


def load_policy_configuration(
    policy_path: Path | str = DEFAULT_POLICY_PATH,
) -> dict[str, Any]:
    """Load and validate remediation policy configuration."""

    path = Path(policy_path)

    if not path.exists():
        raise PolicyConfigurationError(
            f"Policy file does not exist: {path}"
        )

    try:
        with path.open(
            "r",
            encoding="utf-8-sig",
        ) as policy_file:
            configuration = yaml.safe_load(policy_file)
    except yaml.YAMLError as error:
        raise PolicyConfigurationError(
            f"Invalid YAML policy configuration: {error}"
        ) from error

    if not isinstance(configuration, dict):
        raise PolicyConfigurationError(
            "Policy configuration must be a dictionary"
        )

    required_sections = {
        "version",
        "global_constraints",
        "policies",
    }

    missing_sections = required_sections.difference(
        configuration
    )

    if missing_sections:
        raise PolicyConfigurationError(
            "Missing policy sections: "
            + ", ".join(sorted(missing_sections))
        )

    policies = configuration["policies"]

    if not isinstance(policies, dict) or not policies:
        raise PolicyConfigurationError(
            "Policy configuration must contain policies"
        )

    return configuration


def evaluate_remediation_policy(
    *,
    classification: ClassificationResult,
    severity: str,
    policy_path: Path | str = DEFAULT_POLICY_PATH,
) -> PolicyDecision:
    """Evaluate a classified incident against remediation policy."""

    configuration = load_policy_configuration(
        policy_path
    )

    root_cause = classification.predicted_root_cause
    policies = configuration["policies"]

    if root_cause not in policies:
        root_cause = "unknown_failure"

    if root_cause not in policies:
        raise PolicyConfigurationError(
            "No unknown_failure fallback policy is configured"
        )

    policy = policies[root_cause]

    required_fields = {
        "action",
        "automatic",
        "allowed_severities",
    }

    missing_fields = required_fields.difference(policy)

    if missing_fields:
        raise PolicyConfigurationError(
            f"Policy '{root_cause}' is missing fields: "
            + ", ".join(sorted(missing_fields))
        )

    action = str(policy["action"])
    automatic = bool(policy["automatic"])
    allowed_severities = set(
        policy["allowed_severities"]
    )
    parameters = dict(
        policy.get("parameters", {})
    )

    severity_permitted = severity in allowed_severities

    global_constraints = configuration[
        "global_constraints"
    ]

    approval_causes = set(
        global_constraints.get(
            "require_human_approval_for",
            [],
        )
    )

    requires_human_approval = (
        root_cause in approval_causes
        or not automatic
        or classification.unknown_classification
    )

    permitted = severity_permitted

    if not severity_permitted:
        rationale = (
            f"Severity '{severity}' is not permitted for "
            f"policy '{root_cause}'."
        )
    elif requires_human_approval:
        rationale = (
            f"Action '{action}' requires human approval "
            f"for root cause '{root_cause}'."
        )
    else:
        rationale = (
            f"Action '{action}' is authorized for automatic "
            f"execution for root cause '{root_cause}'."
        )

    return PolicyDecision(
        root_cause=root_cause,
        severity=severity,
        action=action,
        automatic=automatic,
        requires_human_approval=requires_human_approval,
        permitted=permitted,
        parameters=parameters,
        rationale=rationale,
    )
