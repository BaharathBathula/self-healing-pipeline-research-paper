"""Evidence-weighted root-cause classification for pipeline incidents."""

from dataclasses import asdict, dataclass
from typing import Any

from src.detector import DetectionResult


@dataclass(frozen=True)
class ClassificationResult:
    """Root-cause prediction with confidence and supporting evidence."""

    predicted_root_cause: str
    confidence: float
    alternative_causes: list[dict[str, float]]
    supporting_evidence: dict[str, Any]
    unknown_classification: bool

    def to_dict(self) -> dict[str, Any]:
        """Convert the classification result into a serializable dictionary."""

        return asdict(self)


def _normalize_scores(
    scores: dict[str, float],
) -> list[tuple[str, float]]:
    """Return candidate scores ordered from highest to lowest."""

    bounded_scores = {
        cause: min(1.0, max(0.0, score))
        for cause, score in scores.items()
    }

    return sorted(
        bounded_scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )


def classify_root_cause(
    detection: DetectionResult,
) -> ClassificationResult:
    """Classify the probable root cause using detector evidence.

    The classifier is deterministic and explainable. It assigns evidence
    weights to candidate causes and returns the strongest supported cause.

    Args:
        detection: Failure-detector output.

    Returns:
        Root-cause classification result.
    """

    signals = detection.triggering_signals
    scores: dict[str, float] = {
        "schema_drift": 0.0,
        "missing_value_spike": 0.0,
        "duplicate_generation": 0.0,
        "freshness_violation": 0.0,
        "volume_anomaly": 0.0,
        "source_failure": 0.0,
        "unknown_failure": 0.0,
        "healthy_control": 0.0,
    }

    supporting_evidence: dict[str, Any] = {}

    if not detection.failure_detected:
        scores["healthy_control"] = 0.99
        supporting_evidence["detector_status"] = "healthy"

    exception_type = signals.get("exception_type")

    if exception_type:
        supporting_evidence["exception_type"] = exception_type

        source_exception_names = {
            "SimulatedTimeoutError",
            "SimulatedConnectionError",
            "SimulatedAuthenticationError",
            "SimulatedRateLimitError",
        }

        if exception_type in source_exception_names:
            scores["source_failure"] += 0.99
        else:
            scores["unknown_failure"] += 0.60

    missing_columns = signals.get(
        "missing_required_columns",
        [],
    )

    incompatible_types = signals.get(
        "incompatible_column_types",
        [],
    )

    if missing_columns:
        scores["schema_drift"] += min(
            0.90,
            0.70 + 0.05 * len(missing_columns),
        )
        supporting_evidence["missing_required_columns"] = missing_columns

    if incompatible_types:
        scores["schema_drift"] += min(
            0.95,
            0.75 + 0.05 * len(incompatible_types),
        )
        supporting_evidence["incompatible_column_types"] = (
            incompatible_types
        )

    duplicate_rate = float(
        signals.get("duplicate_rate", 0.0)
    )

    if duplicate_rate > 0:
        scores["duplicate_generation"] += min(
            0.98,
            0.70 + duplicate_rate,
        )
        supporting_evidence["duplicate_rate"] = duplicate_rate

    null_rate = float(
        signals.get("required_field_null_rate", 0.0)
    )

    if null_rate > 0:
        scores["missing_value_spike"] += min(
            0.98,
            0.65 + null_rate,
        )
        supporting_evidence["required_field_null_rate"] = null_rate

    stale_record_rate = float(
        signals.get("stale_record_rate", 0.0)
    )

    maximum_delay = float(
        signals.get(
            "maximum_freshness_delay_minutes",
            0.0,
        )
    )

    if stale_record_rate > 0:
        delay_component = min(
            0.15,
            maximum_delay / 10_000,
        )

        scores["freshness_violation"] += min(
            0.98,
            0.70 + stale_record_rate + delay_component,
        )

        supporting_evidence["stale_record_rate"] = stale_record_rate
        supporting_evidence[
            "maximum_freshness_delay_minutes"
        ] = maximum_delay

    volume_deviation = float(
        signals.get("volume_deviation_rate", 0.0)
    )

    if volume_deviation > 0:
        scores["volume_anomaly"] += min(
            0.97,
            0.65 + volume_deviation,
        )
        supporting_evidence["volume_deviation_rate"] = (
            volume_deviation
        )

    detected_category = detection.detected_failure_category

    if detected_category in scores:
        scores[detected_category] += 0.20
        supporting_evidence["detector_category"] = detected_category

    ranked_scores = _normalize_scores(scores)

    predicted_cause, confidence = ranked_scores[0]

    alternatives = [
        {
            "cause": cause,
            "confidence": round(score, 3),
        }
        for cause, score in ranked_scores[1:4]
        if score > 0
    ]

    conflicting_causes = [
        cause
        for cause, score in ranked_scores
        if score >= 0.70
    ]

    if len(conflicting_causes) > 1:
        supporting_evidence["conflicting_causes"] = (
            conflicting_causes
        )

        top_score = ranked_scores[0][1]
        second_score = ranked_scores[1][1]
        score_gap = top_score - second_score

        supporting_evidence["classification_score_gap"] = round(
            score_gap,
            3,
        )

        if score_gap <= 0.25:
            predicted_cause = "unknown_failure"
            confidence = 0.50

    if confidence < 0.60:
        predicted_cause = "unknown_failure"
        confidence = max(confidence, 0.50)

    unknown_classification = (
        predicted_cause == "unknown_failure"
    )

    return ClassificationResult(
        predicted_root_cause=predicted_cause,
        confidence=round(confidence, 3),
        alternative_causes=alternatives,
        supporting_evidence=supporting_evidence,
        unknown_classification=unknown_classification,
    )