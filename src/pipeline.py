"""Baseline order-processing pipeline used by all experiment approaches."""

from dataclasses import dataclass
from pathlib import Path

import duckdb
import pandas as pd

from src.config import PROCESSED_DATA_DIR, ensure_runtime_directories


REQUIRED_COLUMNS = {
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
}


@dataclass(frozen=True)
class PipelineResult:
    """Summary of a completed pipeline execution."""

    input_path: Path
    output_path: Path
    input_record_count: int
    output_record_count: int
    rejected_record_count: int
    status: str


def validate_input_schema(dataframe: pd.DataFrame) -> None:
    """Verify that all required source columns are present.

    Args:
        dataframe: Input order dataset.

    Raises:
        ValueError: If one or more required columns are missing.
    """

    missing_columns = REQUIRED_COLUMNS.difference(dataframe.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns: {missing}")


def run_pipeline(
    input_path: Path,
    output_path: Path | None = None,
) -> PipelineResult:
    """Run the baseline transformation pipeline.

    The pipeline:

    1. Reads the source Parquet dataset.
    2. Validates the required schema.
    3. Rejects records with invalid quantities, prices, or exchange rates.
    4. Recalculates local and USD order totals using DuckDB.
    5. Writes a validated Parquet output.

    Args:
        input_path: Source Parquet dataset.
        output_path: Optional processed output destination.

    Returns:
        A summary of the pipeline execution.

    Raises:
        FileNotFoundError: If the input file does not exist.
        ValueError: If schema validation fails.
    """

    if not input_path.exists():
        raise FileNotFoundError(f"Input file does not exist: {input_path}")

    ensure_runtime_directories()

    destination = output_path or (
        PROCESSED_DATA_DIR / "orders_processed.parquet"
    )
    destination.parent.mkdir(parents=True, exist_ok=True)

    source_dataframe = pd.read_parquet(input_path)
    validate_input_schema(source_dataframe)

    input_record_count = len(source_dataframe)

    connection = duckdb.connect(database=":memory:")

    try:
        connection.register("source_orders", source_dataframe)

        processed_dataframe = connection.execute(
            """
            SELECT
                order_id,
                customer_id,
                event_timestamp,
                product_id,
                quantity,
                ROUND(unit_price, 2) AS unit_price,
                currency,
                exchange_rate,
                payment_status,
                region,
                source_system,
                ROUND(quantity * unit_price, 2) AS order_total_local,
                ROUND(
                    quantity * unit_price * exchange_rate,
                    2
                ) AS order_total_usd
            FROM source_orders
            WHERE quantity > 0
              AND unit_price >= 0
              AND exchange_rate > 0
              AND order_id IS NOT NULL
              AND customer_id IS NOT NULL
            ORDER BY order_id
            """
        ).fetch_df()
    finally:
        connection.close()

    output_record_count = len(processed_dataframe)
    rejected_record_count = (
        input_record_count - output_record_count
    )

    processed_dataframe.to_parquet(
        destination,
        index=False,
        engine="pyarrow",
    )

    return PipelineResult(
        input_path=input_path,
        output_path=destination,
        input_record_count=input_record_count,
        output_record_count=output_record_count,
        rejected_record_count=rejected_record_count,
        status="successful",
    )