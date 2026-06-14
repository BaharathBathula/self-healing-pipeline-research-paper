
from dataclasses import dataclass
from typing import Literal

import pandas as pd


SourceFailureType = Literal[
    "timeout",
    "connection_refused",
    "authentication_failure",
    "rate_limit",
    "partial_response",
]


class SimulatedSourceError(RuntimeError):
    """Base exception for controlled source-system failures."""


class SimulatedTimeoutError(SimulatedSourceError):
    """Controlled source timeout."""


class SimulatedConnectionError(SimulatedSourceError):
    """Controlled source connection refusal."""


class SimulatedAuthenticationError(SimulatedSourceError):
    """Controlled source authentication failure."""


class SimulatedRateLimitError(SimulatedSourceError):
    """Controlled source rate-limit response."""


@dataclass(frozen=True)
class SourceFailureResult:
    """Result of a source-system failure simulation."""

    dataframe: pd.DataFrame
    failure_type: SourceFailureType
    expected_record_count: int
    received_record_count: int
    partial_response: bool


def simulate_source_failure(
    dataframe: pd.DataFrame,
    failure_type: SourceFailureType,
    partial_fraction: float = 0.50,
) -> SourceFailureResult:
    """Simulate a deterministic source-system failure."""

    supported_failures = {
        "timeout",
        "connection_refused",
        "authentication_failure",
        "rate_limit",
        "partial_response",
    }

    if failure_type not in supported_failures:
        raise ValueError(
            f"Unsupported source failure type: {failure_type}"
        )

    if not 0 < partial_fraction < 1:
        raise ValueError(
            "partial_fraction must be greater than 0 and less than 1"
        )

    if failure_type == "timeout":
        raise SimulatedTimeoutError(
            "Source request exceeded the configured timeout"
        )

    if failure_type == "connection_refused":
        raise SimulatedConnectionError(
            "Source system refused the connection"
        )

    if failure_type == "authentication_failure":
        raise SimulatedAuthenticationError(
            "Source authentication failed"
        )

    if failure_type == "rate_limit":
        raise SimulatedRateLimitError(
            "Source rate limit exceeded"
        )

    expected_record_count = len(dataframe)

    received_record_count = max(
        1,
        int(expected_record_count * partial_fraction),
    )

    partial_dataframe = dataframe.iloc[
        :received_record_count
    ].copy()

    return SourceFailureResult(
        dataframe=partial_dataframe,
        failure_type="partial_response",
        expected_record_count=expected_record_count,
        received_record_count=received_record_count,
        partial_response=True,
    )