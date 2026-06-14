"""Tests for reproducible source-system failure simulation."""

import pandas as pd
import pytest

from src.data_generator import DatasetConfig, generate_orders
from src.source_failure import (
    SimulatedAuthenticationError,
    SimulatedConnectionError,
    SimulatedRateLimitError,
    SimulatedTimeoutError,
    simulate_source_failure,
)


@pytest.fixture
def source_dataframe() -> pd.DataFrame:
    """Create deterministic source data for failure tests."""

    return generate_orders(
        DatasetConfig(
            row_count=100,
            random_seed=42,
        )
    )


def test_timeout_failure_raises_expected_error(
    source_dataframe: pd.DataFrame,
) -> None:
    """Timeout simulation must raise a controlled timeout exception."""

    with pytest.raises(
        SimulatedTimeoutError,
        match="exceeded the configured timeout",
    ):
        simulate_source_failure(
            source_dataframe,
            "timeout",
        )


def test_connection_refused_raises_expected_error(
    source_dataframe: pd.DataFrame,
) -> None:
    """Connection refusal must raise a controlled connection exception."""

    with pytest.raises(
        SimulatedConnectionError,
        match="refused the connection",
    ):
        simulate_source_failure(
            source_dataframe,
            "connection_refused",
        )


def test_authentication_failure_raises_expected_error(
    source_dataframe: pd.DataFrame,
) -> None:
    """Authentication simulation must preserve the correct failure type."""

    with pytest.raises(
        SimulatedAuthenticationError,
        match="authentication failed",
    ):
        simulate_source_failure(
            source_dataframe,
            "authentication_failure",
        )


def test_rate_limit_failure_raises_expected_error(
    source_dataframe: pd.DataFrame,
) -> None:
    """Rate-limit simulation must raise a controlled exception."""

    with pytest.raises(
        SimulatedRateLimitError,
        match="rate limit exceeded",
    ):
        simulate_source_failure(
            source_dataframe,
            "rate_limit",
        )


def test_partial_response_returns_expected_fraction(
    source_dataframe: pd.DataFrame,
) -> None:
    """Partial response must return the configured fraction."""

    result = simulate_source_failure(
        source_dataframe,
        "partial_response",
        partial_fraction=0.25,
    )

    assert result.failure_type == "partial_response"
    assert result.expected_record_count == 100
    assert result.received_record_count == 25
    assert len(result.dataframe) == 25
    assert result.partial_response is True


def test_partial_response_preserves_original_dataframe(
    source_dataframe: pd.DataFrame,
) -> None:
    """Simulation must not modify the original source dataset."""

    original = source_dataframe.copy(deep=True)

    simulate_source_failure(
        source_dataframe,
        "partial_response",
        partial_fraction=0.50,
    )

    pd.testing.assert_frame_equal(
        source_dataframe,
        original,
    )


@pytest.mark.parametrize(
    "partial_fraction",
    [0, 1, -0.10, 1.10],
)
def test_invalid_partial_fraction_raises_error(
    source_dataframe: pd.DataFrame,
    partial_fraction: float,
) -> None:
    """Partial-response fractions must remain between zero and one."""

    with pytest.raises(
        ValueError,
        match="partial_fraction must be greater than 0 and less than 1",
    ):
        simulate_source_failure(
            source_dataframe,
            "partial_response",
            partial_fraction=partial_fraction,
        )


def test_unsupported_failure_type_raises_error(
    source_dataframe: pd.DataFrame,
) -> None:
    """Unknown source failure types must be rejected."""

    with pytest.raises(
        ValueError,
        match="Unsupported source failure type",
    ):
        simulate_source_failure(
            source_dataframe,
            "database_corruption",  # type: ignore[arg-type]
        )
