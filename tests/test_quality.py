"""Tests for data-quality measurements."""

import pandas as pd
import pytest

from src.data_generator import DatasetConfig, generate_orders
from src.quality import (
    calculate_duplicate_rate,
    calculate_null_rate,
    calculate_quality_metrics,
    calculate_validity_score,
)


def test_clean_dataset_has_perfect_quality_scores() -> None:
    """A valid generated dataset should score 1.0 on core quality metrics."""

    dataframe = generate_orders(
        DatasetConfig(
            row_count=100,
            random_seed=42,
        )
    )

    metrics = calculate_quality_metrics(dataframe)

    assert metrics.record_count == 100
    assert metrics.null_rate == 0.0
    assert metrics.duplicate_rate == 0.0
    assert metrics.completeness_score == 1.0
    assert metrics.uniqueness_score == 1.0
    assert metrics.validity_score == 1.0
    assert metrics.composite_quality_score == 1.0


def test_null_rate_is_calculated_correctly() -> None:
    """Null rate must reflect null cells divided by total cells."""

    dataframe = pd.DataFrame(
        {
            "a": [1, None],
            "b": [None, 2],
        }
    )

    assert calculate_null_rate(dataframe) == 0.5


def test_duplicate_rate_is_calculated_by_business_key() -> None:
    """Duplicate rate must count repeated business keys after the first."""

    dataframe = pd.DataFrame(
        {
            "order_id": ["A", "A", "B", "C", "C"],
        }
    )

    assert calculate_duplicate_rate(dataframe) == 0.4


def test_invalid_business_values_reduce_validity_score() -> None:
    """Invalid quantities, currencies, and statuses must reduce validity."""

    dataframe = generate_orders(
        DatasetConfig(
            row_count=4,
            random_seed=10,
        )
    )

    dataframe.loc[0, "quantity"] = 0
    dataframe.loc[1, "currency"] = "INVALID"
    dataframe.loc[2, "payment_status"] = "unknown"

    validity_score = calculate_validity_score(dataframe)

    assert validity_score == 0.25


def test_quality_metrics_detect_degradation() -> None:
    """Injected nulls and duplicates must lower the composite score."""

    dataframe = generate_orders(
        DatasetConfig(
            row_count=10,
            random_seed=20,
        )
    )

    dataframe.loc[0, "customer_id"] = None
    dataframe.loc[1, "order_id"] = dataframe.loc[0, "order_id"]

    metrics = calculate_quality_metrics(dataframe)

    assert metrics.null_rate > 0
    assert metrics.duplicate_rate == 0.1
    assert metrics.completeness_score < 1.0
    assert metrics.uniqueness_score == 0.9
    assert metrics.composite_quality_score < 1.0


def test_missing_duplicate_key_raises_error() -> None:
    """Duplicate measurement must reject an absent business-key column."""

    dataframe = pd.DataFrame(
        {
            "customer_id": ["A", "B"],
        }
    )

    with pytest.raises(
        ValueError,
        match="Missing duplicate key column: order_id",
    ):
        calculate_duplicate_rate(dataframe)


def test_missing_validity_columns_raise_error() -> None:
    """Validity measurement requires all core business-rule columns."""

    dataframe = pd.DataFrame(
        {
            "order_id": ["A"],
        }
    )

    with pytest.raises(
        ValueError,
        match="Cannot calculate validity; missing columns",
    ):
        calculate_validity_score(dataframe)


def test_empty_dataset_returns_safe_quality_values() -> None:
    """An empty but correctly structured dataset must not divide by zero."""

    dataframe = generate_orders(
        DatasetConfig(row_count=1)
    ).iloc[0:0]

    metrics = calculate_quality_metrics(dataframe)

    assert metrics.record_count == 0
    assert metrics.null_rate == 0.0
    assert metrics.duplicate_rate == 0.0
    assert metrics.validity_score == 1.0