"""Reproducible experiment execution for dataframe failure scenarios."""

from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter_ns
from typing import Iterable, Literal, Sequence

import pandas as pd

from src.failure_injection import (
    inject_duplicate_generation,
    inject_freshness_violation,
    inject_missing_value_spike,
    inject_schema_drift,
    inject_volume_anomaly,
)
from src.self_healing import run_dataframe_self_healing_cycle
from src.source_failure import SimulatedTimeoutError
from src.transformation_failure import (
    inject_transformation_logic_error,
)


FailureType = Literal[
    "healthy_control",
    "source_failure",
    "schema_drift",
    "missing_value_spike",
    "duplicate_generation",
    "freshness_violation",
    "volume_anomaly",
    "transformation_logic_error",
]

Severity = Literal["low", "medium", "high"]

DEFAULT_FAILURE_TYPES: tuple[FailureType, ...] = (
    "healthy_control",
    "source_failure",
    "schema_drift",
    "missing_value_spike",
    "duplicate_generation",
    "freshness_violation",
    "volume_anomaly",
    "transformation_logic_error",
)

DEFAULT_SEVERITIES: tuple[Severity, ...] = (
    "low",
    "medium",
    "high",
)


@dataclass(frozen=True)
class ExperimentTrialResult:
    """Metrics and evidence produced by one experimental trial."""

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
    human_approval_required: bool
    cycle_status: str
    recovery_verified: bool
    input_record_count: int
    output_record_count: int
    quarantined_record_count: int
    runtime_milliseconds: float

    def to_dict(self) -> dict[str, object]:
        """Convert trial metrics into a serializable dictionary."""

        return asdict(self)


def _validate_failure_type(
    failure_type: str,
) -> FailureType:
    """Validate and return a supported failure type."""

    if failure_type not in DEFAULT_FAILURE_TYPES:
        raise ValueError(
            "failure_type must be one of: "
            + ", ".join(DEFAULT_FAILURE_TYPES)
        )

    return failure_type  # type: ignore[return-value]


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


def _inject_dataframe_failure(
    *,
    baseline_dataframe: pd.DataFrame,
    failure_type: FailureType,
    severity: Severity,
    random_seed: int,
) -> tuple[pd.DataFrame, Exception | None, str]:
    """Create the observed dataset and exception for one trial."""

    baseline = baseline_dataframe.copy(deep=True)

    if failure_type == "healthy_control":
        return baseline, None, "standard"

    if failure_type == "source_failure":
        return (
            baseline,
            SimulatedTimeoutError(
                "Controlled source timeout for experiment"
            ),
            "standard",
        )

    if failure_type == "schema_drift":
        injected = inject_schema_drift(
            baseline,
            severity,
        )
        return injected.dataframe, None, "standard"

    if failure_type == "missing_value_spike":
        injected = inject_missing_value_spike(
            baseline,
            severity,
        )
        return injected.dataframe, None, "standard"

    if failure_type == "duplicate_generation":
        injected = inject_duplicate_generation(
            baseline,
            severity,
        )
        return injected.dataframe, None, "standard"

    if failure_type == "freshness_violation":
        injected = inject_freshness_violation(
            baseline,
            severity,
        )
        return injected.dataframe, None, "standard"

    if failure_type == "volume_anomaly":
        injected = inject_volume_anomaly(
            baseline,
            severity,
            direction="decrease",
        )
        return injected.dataframe, None, "standard"

    if failure_type == "transformation_logic_error":
        injected = inject_transformation_logic_error(
            baseline,
            severity,
            random_seed=random_seed,
        )
        return injected.dataframe, None, "transformation"

    raise AssertionError(
        f"Unhandled failure type: {failure_type}"
    )


def run_dataframe_trial(
    *,
    baseline_dataframe: pd.DataFrame,
    failure_type: FailureType,
    severity: Severity,
    repetition: int,
    random_seed: int,
) -> ExperimentTrialResult:
    """Execute one reproducible self-healing experiment trial."""

    validated_failure_type = _validate_failure_type(
        failure_type
    )
    validated_severity = _validate_severity(severity)

    if baseline_dataframe.empty:
        raise ValueError(
            "baseline_dataframe must contain at least one record"
        )

    if repetition < 1:
        raise ValueError(
            "repetition must be at least 1"
        )

    observed_dataframe, exception, detection_mode = (
        _inject_dataframe_failure(
            baseline_dataframe=baseline_dataframe,
            failure_type=validated_failure_type,
            severity=validated_severity,
            random_seed=random_seed,
        )
    )

    start_time = perf_counter_ns()

    cycle = run_dataframe_self_healing_cycle(
        observed_dataframe=observed_dataframe,
        baseline_dataframe=baseline_dataframe,
        exception=exception,
        detection_mode=detection_mode,
    )

    elapsed_nanoseconds = perf_counter_ns() - start_time
    runtime_milliseconds = elapsed_nanoseconds / 1_000_000

    expected_root_cause = validated_failure_type

    detection_correct = (
        cycle.detection.detected_failure_category
        == expected_root_cause
    )

    classification_correct = (
        cycle.classification.predicted_root_cause
        == expected_root_cause
    )

    trial_id = (
        f"{validated_failure_type}-"
        f"{validated_severity}-"
        f"r{repetition:03d}-"
        f"s{random_seed}"
    )

    return ExperimentTrialResult(
        trial_id=trial_id,
        repetition=repetition,
        random_seed=random_seed,
        injected_failure_type=validated_failure_type,
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
        human_approval_required=(
            cycle.policy_decision.requires_human_approval
        ),
        cycle_status=cycle.cycle_status,
        recovery_verified=cycle.recovery_verified,
        input_record_count=len(observed_dataframe),
        output_record_count=len(
            cycle.remediation.output_dataframe
        ),
        quarantined_record_count=len(
            cycle.remediation.quarantined_dataframe
        ),
        runtime_milliseconds=round(
            runtime_milliseconds,
            6,
        ),
    )


def run_dataframe_experiment(
    *,
    baseline_dataframe: pd.DataFrame,
    failure_types: Sequence[FailureType] = DEFAULT_FAILURE_TYPES,
    severities: Sequence[Severity] = DEFAULT_SEVERITIES,
    repetitions: int = 10,
    initial_seed: int = 42,
) -> pd.DataFrame:
    """Execute a complete repeated dataframe experiment matrix."""

    if repetitions < 1:
        raise ValueError(
            "repetitions must be at least 1"
        )

    validated_failure_types = [
        _validate_failure_type(failure_type)
        for failure_type in failure_types
    ]

    validated_severities = [
        _validate_severity(severity)
        for severity in severities
    ]

    trial_results: list[dict[str, object]] = []

    for failure_index, failure_type in enumerate(
        validated_failure_types
    ):
        trial_severities: Iterable[Severity]

        if failure_type == "healthy_control":
            trial_severities = ("low",)
        else:
            trial_severities = validated_severities

        for severity_index, severity in enumerate(
            trial_severities
        ):
            for repetition in range(1, repetitions + 1):
                random_seed = (
                    initial_seed
                    + failure_index * 10_000
                    + severity_index * 1_000
                    + repetition
                )

                result = run_dataframe_trial(
                    baseline_dataframe=baseline_dataframe,
                    failure_type=failure_type,
                    severity=severity,
                    repetition=repetition,
                    random_seed=random_seed,
                )

                trial_results.append(result.to_dict())

    return pd.DataFrame(trial_results)


def save_experiment_results(
    *,
    results: pd.DataFrame,
    output_path: Path | str,
) -> Path:
    """Persist experimental results as CSV or Parquet."""

    if results.empty:
        raise ValueError(
            "results must contain at least one trial"
        )

    path = Path(output_path)
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    suffix = path.suffix.lower()

    if suffix == ".csv":
        results.to_csv(
            path,
            index=False,
        )
    elif suffix == ".parquet":
        results.to_parquet(
            path,
            index=False,
        )
    else:
        raise ValueError(
            "output_path must end with .csv or .parquet"
        )

    return path
