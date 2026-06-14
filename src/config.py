"""Shared configuration and filesystem paths for the research implementation."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
FIXTURES_DIR = DATA_DIR / "fixtures"

EXPERIMENTS_DIR = PROJECT_ROOT / "experiments"
EXPERIMENT_CONFIG_DIR = EXPERIMENTS_DIR / "configs"
RAW_RESULTS_DIR = EXPERIMENTS_DIR / "raw_results"
DERIVED_RESULTS_DIR = EXPERIMENTS_DIR / "derived_results"

POLICIES_DIR = PROJECT_ROOT / "policies"
REMEDIATION_REGISTRY_DIR = PROJECT_ROOT / "remediation_registry"
TELEMETRY_DIR = PROJECT_ROOT / "telemetry"
INCIDENT_EVIDENCE_DIR = PROJECT_ROOT / "incident_evidence"
FIGURES_DIR = PROJECT_ROOT / "figures"

DEFAULT_RANDOM_SEED = 42


def ensure_runtime_directories() -> None:
    """Create directories used for generated research artifacts."""

    runtime_directories = [
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        FIXTURES_DIR,
        RAW_RESULTS_DIR,
        DERIVED_RESULTS_DIR,
        TELEMETRY_DIR,
        INCIDENT_EVIDENCE_DIR,
        FIGURES_DIR,
    ]

    for directory in runtime_directories:
        directory.mkdir(parents=True, exist_ok=True)