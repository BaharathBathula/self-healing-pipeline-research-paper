"""Tests for shared project configuration."""

from pathlib import Path

from src.config import (
    DATA_DIR,
    FIGURES_DIR,
    INCIDENT_EVIDENCE_DIR,
    PROJECT_ROOT,
    RAW_RESULTS_DIR,
    TELEMETRY_DIR,
    ensure_runtime_directories,
)


def test_project_root_is_valid_directory() -> None:
    """Confirm the calculated repository root exists."""

    assert PROJECT_ROOT.exists()
    assert PROJECT_ROOT.is_dir()
    assert (PROJECT_ROOT / "src").exists()
    assert (PROJECT_ROOT / "tests").exists()


def test_configured_paths_are_inside_project_root() -> None:
    """Ensure generated artifacts remain inside the repository."""

    configured_paths = [
        DATA_DIR,
        RAW_RESULTS_DIR,
        TELEMETRY_DIR,
        INCIDENT_EVIDENCE_DIR,
        FIGURES_DIR,
    ]

    for path in configured_paths:
        assert isinstance(path, Path)
        assert PROJECT_ROOT in path.parents


def test_ensure_runtime_directories() -> None:
    """Confirm runtime directories can be created safely."""

    ensure_runtime_directories()

    assert DATA_DIR.exists()
    assert RAW_RESULTS_DIR.exists()
    assert TELEMETRY_DIR.exists()
    assert INCIDENT_EVIDENCE_DIR.exists()
    assert FIGURES_DIR.exists()