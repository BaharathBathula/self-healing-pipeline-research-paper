"""Tests for the baseline order-processing pipeline."""

from pathlib import Path

import pandas as pd
import pytest

from src.data_generator import DatasetConfig, generate_orders, save_orders
from src.pipeline import run_pipeline, validate_input_schema


def test_pipeline_processes_valid_dataset(tmp_path: Path) -> None:
    """A valid dataset should process without rejected records."""

    dataframe = generate_orders(
        DatasetConfig(
            row_count=100,
            random_seed=42,
        )
    )

    input_path = save_orders(
        dataframe,
        tmp_path / "input.parquet",
    )
    output_path = tmp_path / "output.parquet"

    result = run_pipeline(
        input_path=input_path,
        output_path=output_path,
    )

    assert result.status == "successful"
    assert result.input_record_count == 100
    assert result.output_record_count == 100
    assert result.rejected_record_count == 0
    assert output_path.exists()


def test_pipeline_recalculates_order_totals(tmp_path: Path) -> None:
    """Pipeline output totals must match quantity, price, and exchange rate."""

    dataframe = generate_orders(
        DatasetConfig(
            row_count=50,
            random_seed=100,
        )
    )

    input_path = save_orders(
        dataframe,
        tmp_path / "input.parquet",
    )
    output_path = tmp_path / "output.parquet"

    run_pipeline(
        input_path=input_path,
        output_path=output_path,
    )

    processed = pd.read_parquet(output_path)

    expected_local = (
        processed["quantity"] * processed["unit_price"]
    ).round(2)

    expected_usd = (
        expected_local * processed["exchange_rate"]
    ).round(2)

    pd.testing.assert_series_equal(
        processed["order_total_local"],
        expected_local,
        check_names=False,
    )

    pd.testing.assert_series_equal(
        processed["order_total_usd"],
        expected_usd,
        check_names=False,
    )


def test_pipeline_rejects_invalid_records(tmp_path: Path) -> None:
    """Invalid quantities and prices must not reach processed output."""

    dataframe = generate_orders(
        DatasetConfig(
            row_count=20,
            random_seed=123,
        )
    )

    dataframe.loc[0, "quantity"] = 0
    dataframe.loc[1, "unit_price"] = -10
    dataframe.loc[2, "exchange_rate"] = 0

    input_path = save_orders(
        dataframe,
        tmp_path / "invalid_input.parquet",
    )
    output_path = tmp_path / "output.parquet"

    result = run_pipeline(
        input_path=input_path,
        output_path=output_path,
    )

    assert result.input_record_count == 20
    assert result.output_record_count == 17
    assert result.rejected_record_count == 3


def test_pipeline_output_is_sorted_by_order_id(tmp_path: Path) -> None:
    """Processed output must have deterministic ordering."""

    dataframe = generate_orders(
        DatasetConfig(
            row_count=30,
            random_seed=77,
        )
    ).sample(frac=1, random_state=10)

    input_path = save_orders(
        dataframe,
        tmp_path / "shuffled_input.parquet",
    )
    output_path = tmp_path / "output.parquet"

    run_pipeline(
        input_path=input_path,
        output_path=output_path,
    )

    processed = pd.read_parquet(output_path)

    assert processed["order_id"].tolist() == sorted(
        processed["order_id"].tolist()
    )


def test_missing_required_column_raises_error() -> None:
    """Schema validation must reject missing required columns."""

    dataframe = generate_orders(
        DatasetConfig(row_count=10)
    ).drop(columns=["customer_id"])

    with pytest.raises(
        ValueError,
        match="Missing required columns: customer_id",
    ):
        validate_input_schema(dataframe)


def test_missing_input_file_raises_error(tmp_path: Path) -> None:
    """Pipeline must fail clearly when the source file is absent."""

    missing_path = tmp_path / "missing.parquet"

    with pytest.raises(
        FileNotFoundError,
        match="Input file does not exist",
    ):
        run_pipeline(missing_path)