"""Tests for structured pipeline telemetry records."""

import json
from pathlib import Path

import pandas as pd
import pytest

from src.data_generator import DatasetConfig, generate_orders
from src.telemetry import (
    append_telemetry_record,
    create_telemetry_record,
)


def test_create_telemetry_record_for_successful_run() -> None:
    """Successful pipeline execution should produce complete telemetry."""

    input_dataframe = generate_orders(
        DatasetConfig(
            row_count=100,
            random_seed=42,
        )
    )

    output_dataframe = input_dataframe.copy()

    record = create_telemetry_record(
        experiment_id="EXP-001",
        pipeline_status="successful",
        input_dataframe=input_dataframe,
        output_dataframe=output_dataframe,
        execution_duration_ms=125.4567,
    )

    assert record.experiment_id == "EXP-001"
    assert record.pipeline_status == "successful"
    assert record.input_record_count == 100
    assert record.output_record_count == 100
    assert record.rejected_record_count == 0
    assert record.execution_duration_ms == 125.457
    assert record.retry_count == 0
    assert record.exception_type is None
    assert record.exception_message is None
    assert record.quality_metrics["composite_quality_score"] == 1.0
    assert "order_id" in record.schema_columns
    assert record.telemetry_id
    assert record.recorded_at


def test_telemetry_records_rejected_rows() -> None:
    """Input-output count differences must appear as rejected records."""

    input_dataframe = generate_orders(
        DatasetConfig(
            row_count=10,
            random_seed=10,
        )
    )

    output_dataframe = input_dataframe.iloc[:7].copy()

    record = create_telemetry_record(
        experiment_id="EXP-002",
        pipeline_status="degraded",
        input_dataframe=input_dataframe,
        output_dataframe=output_dataframe,
        execution_duration_ms=50,
    )

    assert record.input_record_count == 10
    assert record.output_record_count == 7
    assert record.rejected_record_count == 3


def test_telemetry_records_exception_details() -> None:
    """Failure telemetry must preserve exception type and message."""

    dataframe = generate_orders(
        DatasetConfig(row_count=5)
    )

    error = ValueError("Injected schema failure")

    record = create_telemetry_record(
        experiment_id="EXP-003",
        pipeline_status="failed",
        input_dataframe=dataframe,
        output_dataframe=dataframe,
        execution_duration_ms=20,
        retry_count=2,
        exception=error,
    )

    assert record.pipeline_status == "failed"
    assert record.retry_count == 2
    assert record.exception_type == "ValueError"
    assert record.exception_message == "Injected schema failure"


def test_negative_execution_duration_raises_error() -> None:
    """Execution duration cannot be negative."""

    dataframe = generate_orders(
        DatasetConfig(row_count=5)
    )

    with pytest.raises(
        ValueError,
        match="execution_duration_ms cannot be negative",
    ):
        create_telemetry_record(
            experiment_id="EXP-004",
            pipeline_status="successful",
            input_dataframe=dataframe,
            output_dataframe=dataframe,
            execution_duration_ms=-1,
        )


def test_append_telemetry_record_creates_jsonl_file(
    tmp_path: Path,
) -> None:
    """Telemetry must be appended as valid JSON Lines records."""

    dataframe = generate_orders(
        DatasetConfig(
            row_count=10,
            random_seed=55,
        )
    )

    record = create_telemetry_record(
        experiment_id="EXP-005",
        pipeline_status="successful",
        input_dataframe=dataframe,
        output_dataframe=dataframe,
        execution_duration_ms=75,
    )

    output_path = tmp_path / "telemetry.jsonl"

    saved_path = append_telemetry_record(
        record,
        output_path=output_path,
    )

    assert saved_path.exists()

    lines = saved_path.read_text(
        encoding="utf-8",
    ).strip().splitlines()

    assert len(lines) == 1

    restored = json.loads(lines[0])

    assert restored["experiment_id"] == "EXP-005"
    assert restored["pipeline_status"] == "successful"
    assert restored["quality_metrics"]["record_count"] == 10


def test_append_telemetry_preserves_multiple_records(
    tmp_path: Path,
) -> None:
    """Appending must not overwrite earlier telemetry evidence."""

    dataframe = generate_orders(
        DatasetConfig(row_count=3)
    )

    output_path = tmp_path / "telemetry.jsonl"

    for experiment_id in ["EXP-A", "EXP-B"]:
        record = create_telemetry_record(
            experiment_id=experiment_id,
            pipeline_status="successful",
            input_dataframe=dataframe,
            output_dataframe=dataframe,
            execution_duration_ms=10,
        )

        append_telemetry_record(
            record,
            output_path=output_path,
        )

    lines = output_path.read_text(
        encoding="utf-8",
    ).strip().splitlines()

    assert len(lines) == 2

    restored_records = [
        json.loads(line)
        for line in lines
    ]

    assert restored_records[0]["experiment_id"] == "EXP-A"
    assert restored_records[1]["experiment_id"] == "EXP-B"