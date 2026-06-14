"""Reproducible experiment execution for output-artifact corruption."""

from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter_ns
from typing import Literal, Sequence

import numpy as np
import pandas as pd

from src.output_failure import (
    calculate_sha256,
    inject_output_corruption,
)
from src.self_healing import run_artifact_self_healing_cycle


ArtifactCondition = Literal[
    "healthy_control",
    "output_artifact_corruption",
]

Severity = Literal["low", "medium", "high"]

DEFAULT_ARTIFACT_CONDITIONS: tuple[ArtifactCondition, ...] = (
    "healthy_control",
    "output_artifact_corruption",
)

DEFAULT_SEVERITIES: tuple[Severity, ...] = (
    "low",
    "medium",
    "high",
)


@dataclass(frozen=True)
class ArtifactExperimentTrialResult:
    """Metrics produced by one output-artifact trial."""

    trial_id: str
    repetition: int
    random_seed: int
    injected_failure_type: str
    injected_severity: str
    expected_root_cause: str
    failure_detected: bool
    detected_failure_category: str
    detection_correct: bool
    predicted_root_cause: str
    classification_correct: bool
    classification_confidence: float
    remediation_action: str
    remediation_executed: bool
    cycle_status: str
    recovery_verified: bool
    original_size_bytes: int
    observed_size_bytes: int
    regenerated_size_bytes: int
    checksum_restored: bool
    runtime_milliseconds: float

    def to_dict(self) -> dict[str, object]:
        """Convert trial metrics into a serializable dictionary."""

        return asdict(self)


def _validate_condition(
    condition: str,
) -> ArtifactCondition:
    """Validate and return a supported artifact condition."""

    if condition not in DEFAULT_ARTIFACT_CONDITIONS:
        raise ValueError(
            "condition must be one of: "
            + ", ".join(DEFAULT_ARTIFACT_CONDITIONS)
        )

    return condition  # type: ignore[return-value]


def _validate_severity(
    severity: str,
) -> Severity:
    """Validate and return a supported severity."""

    if severity not in DEFAULT_SEVERITIES:
        raise ValueError(
            "severity must be one of: "
            + ", ".join(DEFAULT_SEVERITIES)
        )

    return severity  # type: ignore[return-value]


def _generate_artifact_bytes(
    *,
    size_bytes: int,
    random_seed: int,
) -> bytes:
    """Generate deterministic binary artifact content."""

    if size_bytes < 2:
        raise ValueError(
            "artifact_size_bytes must be at least 2"
        )

    random_generator = np.random.default_rng(
        random_seed
    )

    values = random_generator.integers(
        low=0,
        high=256,
        size=size_bytes,
        dtype=np.uint8,
    )

    return values.tobytes()


def run_artifact_trial(
    *,
    work_directory: Path | str,
    condition: ArtifactCondition,
    severity: Severity,
    repetition: int,
    random_seed: int,
    artifact_size_bytes: int = 4_096,
    dataframe: pd.DataFrame | None = None,
) -> ArtifactExperimentTrialResult:
    """Execute one reproducible output-artifact experiment trial."""

    validated_condition = _validate_condition(condition)
    validated_severity = _validate_severity(severity)

    if repetition < 1:
        raise ValueError(
            "repetition must be at least 1"
        )

    work_path = Path(work_directory)
    work_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    trial_id = (
        f"artifact-{validated_condition}-"
        f"{validated_severity}-"
        f"r{repetition:03d}-"
        f"s{random_seed}"
    )

    trial_directory = work_path / trial_id
    trial_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    trusted_path = trial_directory / "trusted-output.bin"
    observed_path = trial_directory / "observed-output.bin"
    regenerated_path = trial_directory / "regenerated-output.bin"

    artifact_bytes = _generate_artifact_bytes(
        size_bytes=artifact_size_bytes,
        random_seed=random_seed,
    )

    trusted_path.write_bytes(artifact_bytes)
    expected_checksum = calculate_sha256(trusted_path)

    if validated_condition == "healthy_control":
        observed_path.write_bytes(artifact_bytes)
    else:
        inject_output_corruption(
            source_path=trusted_path,
            destination_path=observed_path,
            severity=validated_severity,
        )

    observed_size_bytes = observed_path.stat().st_size

    start_time = perf_counter_ns()

    cycle = run_artifact_self_healing_cycle(
        artifact_path=observed_path,
        expected_sha256=expected_checksum,
        trusted_source_path=trusted_path,
        regenerated_destination_path=regenerated_path,
        dataframe=dataframe,
    )

    elapsed_nanoseconds = perf_counter_ns() - start_time
    runtime_milliseconds = elapsed_nanoseconds / 1_000_000

    expected_root_cause = validated_condition

    detection_correct = (
        cycle.detection.detected_failure_category
        == expected_root_cause
    )

    classification_correct = (
        cycle.classification.predicted_root_cause
        == expected_root_cause
    )

    final_artifact_path = (
        regenerated_path
        if regenerated_path.exists()
        else observed_path
    )

    regenerated_size_bytes = final_artifact_path.stat().st_size

    checksum_restored = (
        calculate_sha256(final_artifact_path)
        == expected_checksum
    )

    return ArtifactExperimentTrialResult(
        trial_id=trial_id,
        repetition=repetition,
        random_seed=random_seed,
        injected_failure_type=validated_condition,
        injected_severity=validated_severity,
        expected_root_cause=expected_root_cause,
        failure_detected=cycle.detection.failure_detected,
        detected_failure_category=(
            cycle.detection.detected_failure_category
        ),
        detection_correct=detection_correct,
        predicted_root_cause=(
            cycle.classification.predicted_root_cause
        ),
        classification_correct=classification_correct,
        classification_confidence=(
            cycle.classification.confidence
        ),
        remediation_action=cycle.policy_decision.action,
        remediation_executed=cycle.remediation.executed,
        cycle_status=cycle.cycle_status,
        recovery_verified=cycle.recovery_verified,
        original_size_bytes=trusted_path.stat().st_size,
        observed_size_bytes=observed_size_bytes,
        regenerated_size_bytes=regenerated_size_bytes,
        checksum_restored=checksum_restored,
        runtime_milliseconds=round(
            runtime_milliseconds,
            6,
        ),
    )


def run_artifact_experiment(
    *,
    work_directory: Path | str,
    conditions: Sequence[
        ArtifactCondition
    ] = DEFAULT_ARTIFACT_CONDITIONS,
    severities: Sequence[Severity] = DEFAULT_SEVERITIES,
    repetitions: int = 10,
    initial_seed: int = 42,
    artifact_size_bytes: int = 4_096,
    dataframe: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Execute a repeated output-artifact experiment matrix."""

    if repetitions < 1:
        raise ValueError(
            "repetitions must be at least 1"
        )

    validated_conditions = [
        _validate_condition(condition)
        for condition in conditions
    ]

    validated_severities = [
        _validate_severity(severity)
        for severity in severities
    ]

    trial_results: list[dict[str, object]] = []

    for condition_index, condition in enumerate(
        validated_conditions
    ):
        trial_severities: Sequence[Severity]

        if condition == "healthy_control":
            trial_severities = ("low",)
        else:
            trial_severities = validated_severities

        for severity_index, severity in enumerate(
            trial_severities
        ):
            for repetition in range(1, repetitions + 1):
                random_seed = (
                    initial_seed
                    + condition_index * 10_000
                    + severity_index * 1_000
                    + repetition
                )

                result = run_artifact_trial(
                    work_directory=work_directory,
                    condition=condition,
                    severity=severity,
                    repetition=repetition,
                    random_seed=random_seed,
                    artifact_size_bytes=artifact_size_bytes,
                    dataframe=dataframe,
                )

                trial_results.append(result.to_dict())

    return pd.DataFrame(trial_results)
