"""Tests for the synthetic order dataset generator."""

import pandas as pd
import pytest

from src.data_generator import DatasetConfig, generate_orders, save_orders


EXPECTED_COLUMNS = [
    "order_id",
    "customer_id",
    "event_timestamp",
    "product_id",
    "quantity",
    "unit_price",
    "currency",
    "exchange_rate",
    "payment_status",
    "region",
    "source_system",
    "order_total_local",
    "order_total_usd",
]


def test_generate_orders_returns_expected_shape() -> None:
    """Confirm the requested number of rows and columns are generated."""

    dataframe = generate_orders(
        DatasetConfig(
            row_count=100,
            random_seed=42,
        )
    )

    assert dataframe.shape == (100, len(EXPECTED_COLUMNS))
    assert list(dataframe.columns) == EXPECTED_COLUMNS


def test_generate_orders_is_reproducible() -> None:
    """The same seed and configuration must produce identical data."""

    config = DatasetConfig(
        row_count=50,
        random_seed=123,
    )

    first = generate_orders(config)
    second = generate_orders(config)

    pd.testing.assert_frame_equal(first, second)


def test_order_ids_are_unique() -> None:
    """Every generated order must have a unique identifier."""

    dataframe = generate_orders(
        DatasetConfig(row_count=1_000)
    )

    assert dataframe["order_id"].is_unique
    assert dataframe["order_id"].notna().all()


def test_order_total_calculations_are_correct() -> None:
    """Validate local and USD order-total calculations."""

    dataframe = generate_orders(
        DatasetConfig(row_count=200)
    )

    expected_local = (
        dataframe["quantity"] * dataframe["unit_price"]
    ).round(2)

    expected_usd = (
        expected_local * dataframe["exchange_rate"]
    ).round(2)

    pd.testing.assert_series_equal(
        dataframe["order_total_local"],
        expected_local,
        check_names=False,
    )

    pd.testing.assert_series_equal(
        dataframe["order_total_usd"],
        expected_usd,
        check_names=False,
    )


def test_invalid_row_count_raises_error() -> None:
    """Reject dataset configurations with no rows."""

    with pytest.raises(
        ValueError,
        match="row_count must be greater than zero",
    ):
        generate_orders(
            DatasetConfig(row_count=0)
        )


def test_save_orders_creates_readable_parquet_file(tmp_path) -> None:
    """Confirm generated data can be saved and read without modification."""

    dataframe = generate_orders(
        DatasetConfig(
            row_count=25,
            random_seed=99,
        )
    )

    output_path = tmp_path / "orders_test.parquet"
    saved_path = save_orders(
        dataframe,
        output_path,
    )

    assert saved_path.exists()

    restored = pd.read_parquet(saved_path)

    pd.testing.assert_frame_equal(
        dataframe,
        restored,
    )