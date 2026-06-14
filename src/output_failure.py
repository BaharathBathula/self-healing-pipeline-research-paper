"""Controlled output-artifact corruption for pipeline experiments."""

from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Literal


Severity = Literal["low", "medium", "high"]

_RETAINED_FRACTIONS: dict[Severity, float] = {
    "low": 0.95,
    "medium": 0.70,
    "high": 0.30,
}


@dataclass(frozen=True)
class OutputCorruptionResult:
    """Evidence produced by controlled artifact corruption."""

    source_path: str
    corrupted_path: str
    failure_type: str
    severity: Severity
    original_size_bytes: int
    corrupted_size_bytes: int
    original_sha256: str
    corrupted_sha256: str
    retained_fraction: float
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Convert corruption evidence into a serializable dictionary."""

        return asdict(self)


def calculate_sha256(path: Path | str) -> str:
    """Calculate a SHA-256 checksum for a file."""

    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Artifact does not exist: {file_path}"
        )

    digest = sha256()

    with file_path.open("rb") as artifact:
        for chunk in iter(
            lambda: artifact.read(65_536),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def verify_artifact_integrity(
    path: Path | str,
    expected_sha256: str,
) -> bool:
    """Return whether an artifact matches an expected checksum."""

    return calculate_sha256(path) == expected_sha256


def inject_output_corruption(
    *,
    source_path: Path | str,
    destination_path: Path | str,
    severity: Severity,
) -> OutputCorruptionResult:
    """Create a reproducibly truncated copy of an output artifact.

    The source artifact is never modified. Severity controls the fraction
    of bytes retained in the corrupted copy.
    """

    source = Path(source_path)
    destination = Path(destination_path)

    if severity not in _RETAINED_FRACTIONS:
        raise ValueError(
            "severity must be one of: low, medium, high"
        )

    if not source.exists():
        raise FileNotFoundError(
            f"Source artifact does not exist: {source}"
        )

    if not source.is_file():
        raise ValueError(
            f"Source artifact must be a file: {source}"
        )

    source_bytes = source.read_bytes()

    if not source_bytes:
        raise ValueError(
            "Output corruption requires a non-empty artifact"
        )

    if len(source_bytes) < 2:
        raise ValueError(
            "Output corruption requires an artifact of at least two bytes"
        )

    retained_fraction = _RETAINED_FRACTIONS[severity]

    retained_byte_count = max(
        1,
        int(len(source_bytes) * retained_fraction),
    )

    if retained_byte_count >= len(source_bytes):
        retained_byte_count = len(source_bytes) - 1

    corrupted_bytes = source_bytes[:retained_byte_count]

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination.write_bytes(corrupted_bytes)

    original_checksum = calculate_sha256(source)
    corrupted_checksum = calculate_sha256(destination)

    return OutputCorruptionResult(
        source_path=str(source.resolve()),
        corrupted_path=str(destination.resolve()),
        failure_type="output_artifact_corruption",
        severity=severity,
        original_size_bytes=len(source_bytes),
        corrupted_size_bytes=len(corrupted_bytes),
        original_sha256=original_checksum,
        corrupted_sha256=corrupted_checksum,
        retained_fraction=retained_fraction,
        metadata={
            "corruption_method": "deterministic_truncation",
            "bytes_removed": (
                len(source_bytes) - len(corrupted_bytes)
            ),
            "source_preserved": True,
            "integrity_check_passed": (
                original_checksum == corrupted_checksum
            ),
        },
    )

