"""Tests for controlled output-artifact corruption."""

from pathlib import Path

import pytest

from src.output_failure import (
    calculate_sha256,
    inject_output_corruption,
    verify_artifact_integrity,
)


@pytest.fixture
def source_artifact(tmp_path: Path) -> Path:
    """Create a deterministic binary artifact."""

    source = tmp_path / "source.bin"
    source.write_bytes(bytes(range(256)) * 20)

    return source


@pytest.mark.parametrize(
    ("severity", "expected_fraction"),
    [
        ("low", 0.95),
        ("medium", 0.70),
        ("high", 0.30),
    ],
)
def test_severity_controls_retained_size(
    source_artifact: Path,
    tmp_path: Path,
    severity: str,
    expected_fraction: float,
) -> None:
    """Severity must deterministically control truncation volume."""

    destination = tmp_path / f"corrupted-{severity}.bin"

    result = inject_output_corruption(
        source_path=source_artifact,
        destination_path=destination,
        severity=severity,
    )

    expected_size = int(
        result.original_size_bytes * expected_fraction
    )

    assert result.retained_fraction == expected_fraction
    assert result.corrupted_size_bytes == expected_size
    assert destination.stat().st_size == expected_size
    assert result.corrupted_size_bytes < result.original_size_bytes


def test_corruption_changes_checksum(
    source_artifact: Path,
    tmp_path: Path,
) -> None:
    """A corrupted artifact must not retain the original checksum."""

    destination = tmp_path / "corrupted.bin"

    result = inject_output_corruption(
        source_path=source_artifact,
        destination_path=destination,
        severity="medium",
    )

    assert result.original_sha256 != result.corrupted_sha256
    assert result.metadata["integrity_check_passed"] is False
    assert verify_artifact_integrity(
        destination,
        result.original_sha256,
    ) is False


def test_source_artifact_is_preserved(
    source_artifact: Path,
    tmp_path: Path,
) -> None:
    """Corruption must never modify the source artifact."""

    original_bytes = source_artifact.read_bytes()
    original_checksum = calculate_sha256(source_artifact)

    inject_output_corruption(
        source_path=source_artifact,
        destination_path=tmp_path / "corrupted.bin",
        severity="high",
    )

    assert source_artifact.read_bytes() == original_bytes
    assert calculate_sha256(source_artifact) == original_checksum


def test_corrupted_copy_is_prefix_of_source(
    source_artifact: Path,
    tmp_path: Path,
) -> None:
    """Deterministic truncation must preserve only a source prefix."""

    destination = tmp_path / "corrupted.bin"

    inject_output_corruption(
        source_path=source_artifact,
        destination_path=destination,
        severity="low",
    )

    source_bytes = source_artifact.read_bytes()
    corrupted_bytes = destination.read_bytes()

    assert corrupted_bytes == source_bytes[: len(corrupted_bytes)]


def test_destination_directory_is_created(
    source_artifact: Path,
    tmp_path: Path,
) -> None:
    """Nested output directories must be created automatically."""

    destination = (
        tmp_path
        / "nested"
        / "artifacts"
        / "corrupted.bin"
    )

    inject_output_corruption(
        source_path=source_artifact,
        destination_path=destination,
        severity="medium",
    )

    assert destination.exists()
    assert destination.is_file()


def test_corruption_is_reproducible(
    source_artifact: Path,
    tmp_path: Path,
) -> None:
    """Identical source and severity must produce identical bytes."""

    first_path = tmp_path / "first.bin"
    second_path = tmp_path / "second.bin"

    first = inject_output_corruption(
        source_path=source_artifact,
        destination_path=first_path,
        severity="high",
    )

    second = inject_output_corruption(
        source_path=source_artifact,
        destination_path=second_path,
        severity="high",
    )

    assert first.corrupted_sha256 == second.corrupted_sha256
    assert first_path.read_bytes() == second_path.read_bytes()


def test_result_is_serializable(
    source_artifact: Path,
    tmp_path: Path,
) -> None:
    """Corruption evidence must convert to a dictionary."""

    result = inject_output_corruption(
        source_path=source_artifact,
        destination_path=tmp_path / "corrupted.bin",
        severity="low",
    )

    serialized = result.to_dict()

    assert (
        serialized["failure_type"]
        == "output_artifact_corruption"
    )
    assert serialized["severity"] == "low"
    assert isinstance(serialized["metadata"], dict)
    assert serialized["metadata"]["source_preserved"] is True


def test_checksum_verification_accepts_expected_hash(
    source_artifact: Path,
) -> None:
    """Integrity verification must accept a matching checksum."""

    expected = calculate_sha256(source_artifact)

    assert verify_artifact_integrity(
        source_artifact,
        expected,
    ) is True


def test_missing_artifact_checksum_raises_error(
    tmp_path: Path,
) -> None:
    """Checksum calculation must fail for missing artifacts."""

    with pytest.raises(
        FileNotFoundError,
        match="Artifact does not exist",
    ):
        calculate_sha256(tmp_path / "missing.bin")


def test_missing_source_raises_error(
    tmp_path: Path,
) -> None:
    """Failure injection must reject a missing source."""

    with pytest.raises(
        FileNotFoundError,
        match="Source artifact does not exist",
    ):
        inject_output_corruption(
            source_path=tmp_path / "missing.bin",
            destination_path=tmp_path / "corrupted.bin",
            severity="low",
        )


def test_directory_source_raises_error(
    tmp_path: Path,
) -> None:
    """Failure injection must reject directory sources."""

    source_directory = tmp_path / "source-directory"
    source_directory.mkdir()

    with pytest.raises(
        ValueError,
        match="must be a file",
    ):
        inject_output_corruption(
            source_path=source_directory,
            destination_path=tmp_path / "corrupted.bin",
            severity="medium",
        )


def test_empty_source_raises_error(
    tmp_path: Path,
) -> None:
    """Empty artifacts cannot be truncated meaningfully."""

    source = tmp_path / "empty.bin"
    source.write_bytes(b"")

    with pytest.raises(
        ValueError,
        match="non-empty artifact",
    ):
        inject_output_corruption(
            source_path=source,
            destination_path=tmp_path / "corrupted.bin",
            severity="high",
        )


def test_invalid_severity_raises_error(
    source_artifact: Path,
    tmp_path: Path,
) -> None:
    """Unsupported severity values must be rejected."""

    with pytest.raises(
        ValueError,
        match="severity must be one of",
    ):
        inject_output_corruption(
            source_path=source_artifact,
            destination_path=tmp_path / "corrupted.bin",
            severity="critical",
        )


def test_one_byte_artifact_is_rejected(
    tmp_path: Path,
) -> None:
    """A one-byte artifact cannot be truncated while retaining data."""

    source = tmp_path / "one-byte.bin"
    source.write_bytes(b"x")

    with pytest.raises(
        ValueError,
        match="at least two bytes",
    ):
        inject_output_corruption(
            source_path=source,
            destination_path=tmp_path / "corrupted.bin",
            severity="low",
        )
