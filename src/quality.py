"""Data-quality measurements used for telemetry and failure detection."""

from dataclasses import asdict, dataclass

import pandas as pd


@dataclass(frozen=True)
class QualityMetrics:
    """Measured quality characteristics for one dataset."""

    record_count: int
    null_rate: float
    duplicate_rate: float
    completeness_score: float
    uniqueness_score: float
    validity_score: float
    composite_quality_score: float

    def to_dict(self) -> dict[str, int | float]:
        """Convert metrics into a serializable dictionary."""

        return asdict(self)


def _safe_ratio(numerator: int | float, denominator: int | float) -> float:
    """Return a ratio safely when the denominator may be zero."""

    if denominator == 0:
        return 0.0

    return float(numerator / denominator)


def calculate_null_rate(dataframe: pd.DataFrame) -> float:
    """Calculate the fraction of cells containing null values."""

    total_cells = dataframe.shape[0] * dataframe.shape[1]

    if total_cells == 0:
        return 0.0

    null_cells = int(dataframe.isna().sum().sum())

    return _safe_ratio(null_cells, total_cells)


def calculate_duplicate_rate(
    dataframe: pd.DataFrame,
    key_column: str = "order_id",
) -> float:
    """Calculate duplicate frequency for a business-key column.

    Args:
        dataframe: Dataset being evaluated.
        key_column: Column used to identify duplicate records.

    Raises:
        ValueError: If the requested key column does not exist.
    """

    if key_column not in dataframe.columns:
        raise ValueError(f"Missing duplicate key column: {key_column}")

    if dataframe.empty:
        return 0.0

    duplicate_count = int(
        dataframe.duplicated(
            subset=[key_column],
            keep="first",
        ).sum()
    )

    return _safe_ratio(duplicate_count, len(dataframe))


def calculate_validity_score(dataframe: pd.DataFrame) -> float:
    """Calculate the fraction of records satisfying core business rules."""

    if dataframe.empty:
        return 1.0

    required_columns = {
        "order_id",
        "customer_id",
        "quantity",
        "unit_price",
        "exchange_rate",
        "currency",
        "payment_status",
    }

    missing_columns = required_columns.difference(dataframe.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(
            f"Cannot calculate validity; missing columns: {missing}"
        )

    valid_currency_values = {"USD", "EUR", "GBP", "CAD"}
    valid_payment_statuses = {"approved", "pending", "declined"}

    valid_rows = (
        dataframe["order_id"].notna()
        & dataframe["customer_id"].notna()
        & dataframe["quantity"].gt(0)
        & dataframe["unit_price"].ge(0)
        & dataframe["exchange_rate"].gt(0)
        & dataframe["currency"].isin(valid_currency_values)
        & dataframe["payment_status"].isin(valid_payment_statuses)
    )

    return float(valid_rows.mean())


def calculate_quality_metrics(
    dataframe: pd.DataFrame,
    key_column: str = "order_id",
) -> QualityMetrics:
    """Calculate the complete quality-measurement record."""

    null_rate = calculate_null_rate(dataframe)
    duplicate_rate = calculate_duplicate_rate(
        dataframe,
        key_column=key_column,
    )
    validity_score = calculate_validity_score(dataframe)

    completeness_score = max(0.0, 1.0 - null_rate)
    uniqueness_score = max(0.0, 1.0 - duplicate_rate)

    composite_quality_score = (
        completeness_score * 0.35
        + uniqueness_score * 0.25
        + validity_score * 0.40
    )

    return QualityMetrics(
        record_count=len(dataframe),
        null_rate=round(null_rate, 6),
        duplicate_rate=round(duplicate_rate, 6),
        completeness_score=round(completeness_score, 6),
        uniqueness_score=round(uniqueness_score, 6),
        validity_score=round(validity_score, 6),
        composite_quality_score=round(
            composite_quality_score,
            6,
        ),
    )