"""Generate reproducible synthetic order data for pipeline experiments."""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import DEFAULT_RANDOM_SEED, RAW_DATA_DIR, ensure_runtime_directories


@dataclass(frozen=True)
class DatasetConfig:
    """Configuration for synthetic dataset generation."""

    row_count: int = 10_000
    random_seed: int = DEFAULT_RANDOM_SEED
    reference_time: str = "2026-01-01T00:00:00Z"


CURRENCIES = np.array(["USD", "EUR", "GBP", "CAD"])
REGIONS = np.array(["north_america", "europe", "asia_pacific"])
PAYMENT_STATUSES = np.array(["approved", "pending", "declined"])
SOURCE_SYSTEMS = np.array(["web", "mobile", "partner_api"])

EXCHANGE_RATES = {
    "USD": 1.00,
    "EUR": 1.08,
    "GBP": 1.27,
    "CAD": 0.74,
}


def generate_orders(config: DatasetConfig = DatasetConfig()) -> pd.DataFrame:
    """Generate a deterministic synthetic order dataset.

    Args:
        config: Dataset generation parameters.

    Returns:
        A pandas DataFrame containing synthetic order records.

    Raises:
        ValueError: If row_count is less than one.
    """

    if config.row_count < 1:
        raise ValueError("row_count must be greater than zero")

    rng = np.random.default_rng(config.random_seed)
    row_count = config.row_count

    currencies = rng.choice(
        CURRENCIES,
        size=row_count,
        p=[0.55, 0.20, 0.15, 0.10],
    )

    reference_time = pd.Timestamp(config.reference_time)
    seconds_back = rng.integers(
        low=0,
        high=7 * 24 * 60 * 60,
        size=row_count,
    )

    event_timestamps = reference_time - pd.to_timedelta(
        seconds_back,
        unit="s",
    )

    unit_prices = np.round(
        rng.uniform(5.00, 500.00, size=row_count),
        2,
    )

    quantities = rng.integers(
        low=1,
        high=11,
        size=row_count,
    )

    dataframe = pd.DataFrame(
        {
            "order_id": [
                f"ORD{index:08d}"
                for index in range(1, row_count + 1)
            ],
            "customer_id": [
                f"CUST{value:07d}"
                for value in rng.integers(
                    low=1,
                    high=max(2, row_count // 2),
                    size=row_count,
                )
            ],
            "event_timestamp": event_timestamps,
            "product_id": [
                f"PROD{value:05d}"
                for value in rng.integers(
                    low=1,
                    high=1001,
                    size=row_count,
                )
            ],
            "quantity": quantities,
            "unit_price": unit_prices,
            "currency": currencies,
            "exchange_rate": [
                EXCHANGE_RATES[currency]
                for currency in currencies
            ],
            "payment_status": rng.choice(
                PAYMENT_STATUSES,
                size=row_count,
                p=[0.90, 0.05, 0.05],
            ),
            "region": rng.choice(
                REGIONS,
                size=row_count,
                p=[0.55, 0.25, 0.20],
            ),
            "source_system": rng.choice(
                SOURCE_SYSTEMS,
                size=row_count,
                p=[0.60, 0.30, 0.10],
            ),
        }
    )

    dataframe["order_total_local"] = np.round(
        dataframe["quantity"] * dataframe["unit_price"],
        2,
    )

    dataframe["order_total_usd"] = np.round(
        dataframe["order_total_local"] * dataframe["exchange_rate"],
        2,
    )

    return dataframe


def save_orders(
    dataframe: pd.DataFrame,
    output_path: Path | None = None,
) -> Path:
    """Save synthetic orders as a Parquet file.

    Args:
        dataframe: Dataset to save.
        output_path: Optional destination path.

    Returns:
        Path to the written Parquet file.
    """

    ensure_runtime_directories()

    destination = output_path or RAW_DATA_DIR / "orders_baseline.parquet"
    destination.parent.mkdir(parents=True, exist_ok=True)

    dataframe.to_parquet(
        destination,
        index=False,
        engine="pyarrow",
    )

    return destination