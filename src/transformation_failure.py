"""Controlled transformation-logic failure injection for experiments."""

from dataclasses import asdict, dataclass
from typing import Any, Literal

import numpy as np
import pandas as pd


Severity = Literal["low", "medium", "high"]

_REQUIRED_COLUMNS = {
    "quantity",
    "unit_price",
    "order_total_local",
}

_SEVERITY_FRACTIONS: dict[Severity, float] = {
    "low": 0.05,
    "medium": 0.20,
    "high": 0.50,
}


@dataclass(frozen=True)
class TransformationFailureResult:
    """Result produced by a controlled transformation defect."""

    dataframe: pd.DataFrame
    failure_type: str
    severity: Severity
    affected_record_count: int
    affected_indices: list[int]
    metadata: dict[str, Any]

    def evidence(self) -> dict[str, Any]:
        """Return serializable failure-injection evidence."""

        result = asdict(self)
        result.pop("dataframe")
        return result


def _validate_input(dataframe: pd.DataFrame) -> None:
    """Validate columns required for transformation experiments."""

    missing_columns = sorted(
        _REQUIRED_COLUMNS.difference(dataframe.columns)
    )

    if missing_columns:
        raise ValueError(
            "Transformation failure injection requires columns: "
            + ", ".join(missing_columns)
        )

    if dataframe.empty:
        raise ValueError(
            "Transformation failure injection requires non-empty data"
        )


def _affected_count(
    row_count: int,
    severity: Severity,
) -> int:
    """Calculate a deterministic non-zero affected-record count."""

    if severity not in _SEVERITY_FRACTIONS:
        raise ValueError(
            "severity must be one of: low, medium, high"
        )

    return max(
        1,
        int(round(row_count * _SEVERITY_FRACTIONS[severity])),
    )


def expected_local_total(
    dataframe: pd.DataFrame,
) -> pd.Series:
    """Calculate the expected local order total."""

    return (
        pd.to_numeric(
            dataframe["quantity"],
            errors="coerce",
        )
        * pd.to_numeric(
            dataframe["unit_price"],
            errors="coerce",
        )
    ).round(2)


def transformation_error_mask(
    dataframe: pd.DataFrame,
    *,
    absolute_tolerance: float = 0.01,
) -> pd.Series:
    """Identify rows that violate the expected transformation rule."""

    _validate_input(dataframe)

    expected = expected_local_total(dataframe)

    observed = pd.to_numeric(
        dataframe["order_total_local"],
        errors="coerce",
    )

    valid = np.isclose(
        observed,
        expected,
        atol=absolute_tolerance,
        rtol=0.0,
        equal_nan=False,
    )

    return pd.Series(
        ~valid,
        index=dataframe.index,
        dtype=bool,
    )


def inject_transformation_logic_error(
    dataframe: pd.DataFrame,
    severity: Severity,
    *,
    random_seed: int = 42,
) -> TransformationFailureResult:
    """Inject deterministic semantic defects into derived totals.

    Low severity applies a five-percent inflation.
    Medium severity applies a twenty-five-percent reduction.
    High severity converts affected totals to negative values.
    """

    _validate_input(dataframe)

    count = _affected_count(
        len(dataframe),
        severity,
    )

    random_generator = np.random.default_rng(
        random_seed
    )

    selected_positions = np.sort(
        random_generator.choice(
            len(dataframe),
            size=count,
            replace=False,
        )
    )

    corrupted = dataframe.copy(deep=True)

    selected_index = corrupted.index[
        selected_positions
    ]

    original_values = pd.to_numeric(
        corrupted.loc[
            selected_index,
            "order_total_local",
        ],
        errors="coerce",
    )

    if severity == "low":
        corrupted_values = (
            original_values * 1.05
        ).round(2)
        defect_rule = "inflate_local_total_by_5_percent"

    elif severity == "medium":
        corrupted_values = (
            original_values * 0.75
        ).round(2)
        defect_rule = "reduce_local_total_by_25_percent"

    else:
        corrupted_values = (
            -original_values.abs()
        ).round(2)
        defect_rule = "convert_local_total_to_negative"

    corrupted.loc[
        selected_index,
        "order_total_local",
    ] = corrupted_values

    affected_indices = [
        int(index)
        if isinstance(index, (int, np.integer))
        else int(position)
        for position, index in zip(
            selected_positions,
            selected_index,
        )
    ]

    detected_count = int(
        transformation_error_mask(corrupted).sum()
    )

    return TransformationFailureResult(
        dataframe=corrupted,
        failure_type="transformation_logic_error",
        severity=severity,
        affected_record_count=count,
        affected_indices=affected_indices,
        metadata={
            "random_seed": random_seed,
            "affected_fraction": _SEVERITY_FRACTIONS[
                severity
            ],
            "defect_rule": defect_rule,
            "expected_rule": (
                "order_total_local = quantity * unit_price"
            ),
            "detected_error_count": detected_count,
        },
    )
