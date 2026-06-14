"""Tests for transformation-logic failure injection."""

import pandas as pd
import pytest

from src.data_generator import DatasetConfig, generate_orders
from src.transformation_failure import (
    expected_local_total,
    inject_transformation_logic_error,
    transformation_error_mask,
)


@pytest.fixture
def baseline_dataframe() -> pd.DataFrame:
    """Create deterministic baseline order data."""

    return generate_orders(
        DatasetConfig(
            row_count=100,
            random_seed=42,
        )
    )


def test_baseline_transformation_rule_is_valid(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Healthy baseline rows must satisfy the transformation rule."""

    error_mask = transformation_error_mask(
        baseline_dataframe
    )

    assert error_mask.sum() == 0


@pytest.mark.parametrize(
    ("severity", "expected_count"),
    [
        ("low", 5),
        ("medium", 20),
        ("high", 50),
    ],
)
def test_severity_controls_affected_record_count(
    baseline_dataframe: pd.DataFrame,
    severity: str,
    expected_count: int,
) -> None:
    """Severity must deterministically control defect volume."""

    result = inject_transformation_logic_error(
        baseline_dataframe,
        severity,
        random_seed=7,
    )

    assert result.affected_record_count == expected_count
    assert len(result.affected_indices) == expected_count
    assert (
        transformation_error_mask(
            result.dataframe
        ).sum()
        == expected_count
    )
    assert (
        result.metadata["detected_error_count"]
        == expected_count
    )


def test_low_severity_inflates_selected_totals(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Low severity must apply a five-percent inflation."""

    result = inject_transformation_logic_error(
        baseline_dataframe,
        "low",
        random_seed=3,
    )

    selected = result.affected_indices

    original = baseline_dataframe.loc[
        selected,
        "order_total_local",
    ]

    corrupted = result.dataframe.loc[
        selected,
        "order_total_local",
    ]

    expected = (original * 1.05).round(2)

    pd.testing.assert_series_equal(
        corrupted.reset_index(drop=True),
        expected.reset_index(drop=True),
        check_names=False,
    )


def test_medium_severity_reduces_selected_totals(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Medium severity must reduce selected totals by 25 percent."""

    result = inject_transformation_logic_error(
        baseline_dataframe,
        "medium",
        random_seed=3,
    )

    selected = result.affected_indices

    original = baseline_dataframe.loc[
        selected,
        "order_total_local",
    ]

    corrupted = result.dataframe.loc[
        selected,
        "order_total_local",
    ]

    expected = (original * 0.75).round(2)

    pd.testing.assert_series_equal(
        corrupted.reset_index(drop=True),
        expected.reset_index(drop=True),
        check_names=False,
    )


def test_high_severity_creates_negative_totals(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """High severity must convert selected totals to negatives."""

    result = inject_transformation_logic_error(
        baseline_dataframe,
        "high",
        random_seed=3,
    )

    selected = result.affected_indices

    assert (
        result.dataframe.loc[
            selected,
            "order_total_local",
        ]
        < 0
    ).all()


def test_injection_is_reproducible(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Identical seeds must produce identical defects."""

    first = inject_transformation_logic_error(
        baseline_dataframe,
        "medium",
        random_seed=99,
    )

    second = inject_transformation_logic_error(
        baseline_dataframe,
        "medium",
        random_seed=99,
    )

    assert first.affected_indices == second.affected_indices

    pd.testing.assert_frame_equal(
        first.dataframe,
        second.dataframe,
    )


def test_different_seeds_change_selected_records(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Different seeds should select different record subsets."""

    first = inject_transformation_logic_error(
        baseline_dataframe,
        "medium",
        random_seed=10,
    )

    second = inject_transformation_logic_error(
        baseline_dataframe,
        "medium",
        random_seed=11,
    )

    assert first.affected_indices != second.affected_indices


def test_original_dataframe_is_not_modified(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Failure injection must not mutate the input dataset."""

    original = baseline_dataframe.copy(deep=True)

    inject_transformation_logic_error(
        baseline_dataframe,
        "high",
        random_seed=4,
    )

    pd.testing.assert_frame_equal(
        baseline_dataframe,
        original,
    )


def test_expected_total_calculation(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Expected totals must equal quantity multiplied by unit price."""

    calculated = expected_local_total(
        baseline_dataframe
    )

    expected = (
        baseline_dataframe["quantity"]
        * baseline_dataframe["unit_price"]
    ).round(2)

    pd.testing.assert_series_equal(
        calculated,
        expected,
        check_names=False,
    )


def test_evidence_excludes_dataframe(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Serialized injection evidence must exclude raw data."""

    result = inject_transformation_logic_error(
        baseline_dataframe,
        "low",
    )

    evidence = result.evidence()

    assert "dataframe" not in evidence
    assert (
        evidence["failure_type"]
        == "transformation_logic_error"
    )
    assert evidence["severity"] == "low"
    assert isinstance(evidence["metadata"], dict)


def test_missing_required_columns_raise_error(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Missing transformation inputs must fail validation."""

    invalid = baseline_dataframe.drop(
        columns=["quantity"]
    )

    with pytest.raises(
        ValueError,
        match="requires columns",
    ):
        inject_transformation_logic_error(
            invalid,
            "low",
        )


def test_empty_dataframe_raises_error(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Empty datasets cannot receive a transformation defect."""

    empty = baseline_dataframe.iloc[0:0].copy()

    with pytest.raises(
        ValueError,
        match="non-empty data",
    ):
        inject_transformation_logic_error(
            empty,
            "low",
        )


def test_invalid_severity_raises_error(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Unsupported severity values must be rejected."""

    with pytest.raises(
        ValueError,
        match="severity must be one of",
    ):
        inject_transformation_logic_error(
            baseline_dataframe,
            "critical",
        )


def test_single_row_dataset_affects_one_record(
    baseline_dataframe: pd.DataFrame,
) -> None:
    """Small datasets must still receive one controlled defect."""

    single_row = baseline_dataframe.iloc[:1].copy()

    result = inject_transformation_logic_error(
        single_row,
        "low",
    )

    assert result.affected_record_count == 1
    assert transformation_error_mask(
        result.dataframe
    ).sum() == 1
