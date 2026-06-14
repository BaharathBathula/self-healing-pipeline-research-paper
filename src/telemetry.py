"""Structured telemetry records for pipeline executions."""

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
import json
import uuid

import pandas as pd

from src.config import TELEMETRY_DIR, ensure_runtime_directories
from src.quality import QualityMetrics, calculate_quality_metrics


@dataclass(frozen=True)
class TelemetryRecord:
    """Operational and data-quality signals from one pipeline execution."""

    telemetry_id: str
    experiment_id: str
    recorded_at: str
    pipeline_status: str
    input_record_count: int
    output_record_count: int
    rejected_record_count: int
    execution_duration_ms: float
    retry_count: int
    exception_type: str | None
    exception_message: str | None
    quality_metrics: dict[str, int | float]
    schema_columns: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Convert the telemetry record into a serializable dictionary."""

        return asdict(self)


def create_telemetry_record(
    *,
    experiment_id: str,
    pipeline_status: str,
    input_dataframe: pd.DataFrame,
    output_dataframe: pd.DataFrame,
    execution_duration_ms: float,
    retry_count: int = 0,
    exception: Exception | None = None,
) -> TelemetryRecord:
    """Create a telemetry record from one pipeline execution."""

    if execution_duration_ms < 0:
        raise ValueError("execution_duration_ms cannot be negative")

    quality_metrics: QualityMetrics = calculate_quality_metrics(
        output_dataframe
    )

    return TelemetryRecord(
        telemetry_id=str(uuid.uuid4()),
        experiment_id=experiment_id,
        recorded_at=datetime.now(UTC).isoformat(),
        pipeline_status=pipeline_status,
        input_record_count=len(input_dataframe),
        output_record_count=len(output_dataframe),
        rejected_record_count=(
            len(input_dataframe) - len(output_dataframe)
        ),
        execution_duration_ms=round(execution_duration_ms, 3),
        retry_count=retry_count,
        exception_type=(
            type(exception).__name__
            if exception is not None
            else None
        ),
        exception_message=(
            str(exception)
            if exception is not None
            else None
        ),
        quality_metrics=quality_metrics.to_dict(),
        schema_columns=list(output_dataframe.columns),
    )


def append_telemetry_record(
    record: TelemetryRecord,
    output_path: Path | None = None,
) -> Path:
    """Append a telemetry record to an immutable JSON Lines file."""

    ensure_runtime_directories()

    destination = output_path or TELEMETRY_DIR / "telemetry.jsonl"
    destination.parent.mkdir(parents=True, exist_ok=True)

    with destination.open(
        mode="a",
        encoding="utf-8",
    ) as file:
        file.write(
            json.dumps(
                record.to_dict(),
                sort_keys=True,
            )
        )
        file.write("\n")

    return destination