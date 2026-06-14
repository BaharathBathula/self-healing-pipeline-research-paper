"""Tests for controlled failure injection."""

import pandas as pd
import pytest

from src.data_generator import DatasetConfig, generate_orders
from src.failure_injection import (
    apply_failure_injection,
    inject_duplicate_generation,
    inject_freshness_violation,
    inject_missing_value_spike,
    inject_schema_drift,
    inject_volume_anomaly,
)


@pytest.fixture
def baseline_dataframe() -> pd.DataFrame:
    """Create a deterministic baseline dataset for injection tests."""

    return generate_orders(
        DatasetConfig(
            row_count=100,
            random_seed=42,
        )
    )


def test_schema_drift_low_renames_column(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Low schema drift must rename source_system."""

    result = inject_schema_drift(
        baseline_dataframe,
        "low",
    )

    assert result.failure_category == "schema_drift"
    assert result.severity == "low"
    assert "source_system" not in result.dataframe.columns
    assert "source_system_v2" in result.dataframe.columns
    assert "source_system" in baseline_dataframe.columns


def test_schema_drift_medium_removes_required_column(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Medium schema drift must remove customer_id."""

    result = inject_schema_drift(
        baseline_dataframe,
        "medium",
    )

    assert "customer_id" not in result.dataframe.columns
    assert result.affected_record_count == 100


def test_schema_drift_high_changes_quantity_type(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """High schema drift must create incompatible quantity values."""

    result = inject_schema_drift(
        baseline_dataframe,
        "high",
    )

    assert pd.api.types.is_string_dtype(
        result.dataframe["quantity"]
    )
    assert result.dataframe["quantity"].str.startswith("Q-").all()


@pytest.mark.parametrize(
    ("severity", "expected_count"),
    [
        ("low", 10),
        ("medium", 25),
        ("high", 50),
    ],
)
def test_missing_value_spike_affects_expected_rows(
    baseline_dataframe: pd.DataFrame,
    severity: str,
    expected_count: int,
) -> None:
    """Null injection must follow the configured severity fraction."""

    result = inject_missing_value_spike(
        baseline_dataframe,
        severity,  # type: ignore[arg-type]
    )

    assert result.affected_record_count == expected_count
    assert result.dataframe["customer_id"].isna().sum() == expected_count
    assert baseline_dataframe["customer_id"].isna().sum() == 0


@pytest.mark.parametrize(
    ("severity", "expected_duplicates"),
    [
        ("low", 10),
        ("medium", 25),
        ("high", 50),
    ],
)
def test_duplicate_generation_adds_expected_records(
    baseline_dataframe: pd.DataFrame,
    severity: str,
    expected_duplicates: int,
) -> None:
    """Duplicate injection must append repeated business keys."""

    result = inject_duplicate_generation(
        baseline_dataframe,
        severity,  # type: ignore[arg-type]
    )

    duplicate_count = result.dataframe.duplicated(
        subset=["order_id"],
        keep="first",
    ).sum()

    assert result.affected_record_count == expected_duplicates
    assert duplicate_count == expected_duplicates
    assert len(result.dataframe) == 100 + expected_duplicates


@pytest.mark.parametrize(
    ("severity", "delay_minutes"),
    [
        ("low", 30),
        ("medium", 180),
        ("high", 1_440),
    ],
)
def test_freshness_violation_applies_expected_delay(
    baseline_dataframe: pd.DataFrame,
    severity: str,
    delay_minutes: int,
) -> None:
    """Freshness injection must move selected timestamps backward."""

    result = inject_freshness_violation(
        baseline_dataframe,
        severity,  # type: ignore[arg-type]
    )

    affected_count = result.affected_record_count

    original = pd.to_datetime(
        baseline_dataframe.loc[
            : affected_count - 1,
            "event_timestamp",
        ],
        utc=True,
    )

    modified = pd.to_datetime(
        result.dataframe.loc[
            : affected_count - 1,
            "event_timestamp",
        ],
        utc=True,
    )

    expected_difference = pd.Timedelta(
        minutes=delay_minutes,
    )

    assert ((original - modified) == expected_difference).all()


def test_volume_decrease_reduces_dataset(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """High volume decrease must retain only ten percent."""

    result = inject_volume_anomaly(
        baseline_dataframe,
        "high",
        direction="decrease",
    )

    assert len(result.dataframe) == 10
    assert result.affected_record_count == 90


def test_volume_increase_preserves_unique_order_ids(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Volume increase must not accidentally create duplicate IDs."""

    result = inject_volume_anomaly(
        baseline_dataframe,
        "medium",
        direction="increase",
    )

    assert len(result.dataframe) == 300
    assert result.dataframe["order_id"].is_unique
    assert result.affected_record_count == 200


def test_original_dataframe_is_not_modified(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Failure injection must preserve the baseline dataset."""

    original = baseline_dataframe.copy(deep=True)

    inject_missing_value_spike(
        baseline_dataframe,
        "high",
    )

    pd.testing.assert_frame_equal(
        baseline_dataframe,
        original,
    )


def test_dispatch_interface_returns_expected_failure(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Common dispatch function must call the correct injector."""

    result = apply_failure_injection(
        baseline_dataframe,
        failure_category="duplicate_generation",
        severity="low",
    )

    assert result.failure_category == "duplicate_generation"
    assert result.severity == "low"


def test_invalid_severity_raises_error(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Unsupported severity values must be rejected."""

    with pytest.raises(
        ValueError,
        match="severity must be one of",
    ):
        inject_missing_value_spike(
            baseline_dataframe,
            "critical",  # type: ignore[arg-type]
        )


def test_unknown_failure_category_raises_error(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """The dispatcher must reject unsupported failure categories."""

    with pytest.raises(
        ValueError,
        match="Unsupported failure category",
    ):
        apply_failure_injection(
            baseline_dataframe,
            failure_category="unknown_test_failure",
            severity="low",
        )


def test_invalid_volume_direction_raises_error(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Volume injection must reject unsupported directions."""

    with pytest.raises(
        ValueError,
        match="direction must be decrease or increase",
    ):
        inject_volume_anomaly(
            baseline_dataframe,
            "low",
            direction="sideways",  # type: ignore[arg-type]
        )