# Independent Replication Guide

## Purpose

This guide enables an external engineer or researcher to reproduce the
historical controlled synthetic experiment in a separate environment.

A completed run is independent only when the evaluator performs the work
without author control, preserves their own evidence, reports deviations and
negative findings, and signs their own technical statement.

This guide does not establish production effectiveness, commercial impact,
industry adoption, or major significance.

## Versions Under Evaluation

Repository:

`BaharathBathula/self-healing-pipeline-research-paper`

Historical experiment source commit:

`e6052e25b4579ef6698b73c1d7c64b50d547e212`

Commit subject:

`Add full reproducible experiment execution script`

Reference results are preserved on the current main branch under:

`reproducibility/reference-results/2026-06-14/`

## Expected Environment

The author-operated reproduction used:

- Windows 11, 64-bit
- Python 3.12.2
- pandas 3.0.3
- pytest 9.1.0
- exact dependencies from `requirements-lock.txt`

Dependency-lock SHA-256:

`6C7C3B4E5C644EEF0DFE7FB42333D52AC97E706BC83E3065D00E0B4C2F30670A`

An evaluator may use another operating system or compatible Python 3.12
environment, but every deviation must be documented.

## Independence Requirements

The evaluator should record:

- full name, title, organization, and technical qualifications;
- any relationship to the author;
- whether compensation was provided;
- operating system, hardware, Python version, and package versions;
- exact Git commit;
- exact commands;
- test results;
- experiment outputs;
- file hashes;
- comparison results;
- deviations, warnings, failures, and negative findings; and
- signature date.

The evaluator must not state that the project is production-proven or broadly
adopted based only on this experiment.

## Windows PowerShell Procedure

### 1. Clone the current repository

```powershell
git clone https://github.com/BaharathBathula/self-healing-pipeline-research-paper.git
cd self-healing-pipeline-research-paper
git fetch --all --tags --prune
```

Keep this current-main clone because it contains the reference results,
comparison utility, and evaluator templates.

### 2. Create a detached worktree for the historical source

Run this from the current-main clone:

```powershell
git worktree add `
    ..\self-healing-pipeline-independent-run `
    e6052e25b4579ef6698b73c1d7c64b50d547e212

cd ..\self-healing-pipeline-independent-run
git rev-parse HEAD
git status --short --branch
```

The reported commit must be:

```text
e6052e25b4579ef6698b73c1d7c64b50d547e212
```

### 3. Create an isolated Python environment

```powershell
py -3.12 -m venv .venv

.\.venv\Scripts\python.exe `
    -m pip install `
    --upgrade pip

.\.venv\Scripts\python.exe `
    -m pip install `
    -r requirements-lock.txt

.\.venv\Scripts\python.exe -m pip check

.\.venv\Scripts\python.exe `
    -m pip freeze |
    Set-Content `
        -LiteralPath evaluator-pip-freeze.txt `
        -Encoding utf8
```

Record the exact Python version:

```powershell
.\.venv\Scripts\python.exe --version
```

### 4. Set the import path explicitly

The historical runner imports the top-level `src` package. Direct execution can
fail with `ModuleNotFoundError: No module named 'src'` unless the repository
root is on `PYTHONPATH`.

Run:

```powershell
$env:PYTHONPATH = (Get-Location).Path

.\.venv\Scripts\python.exe `
    -c "import src; print('SRC_IMPORT_OK')"
```

Expected output:

```text
SRC_IMPORT_OK
```

Do not modify source files to bypass this requirement. Record any alternative
installation method as a deviation.

### 5. Run the automated tests

```powershell
.\.venv\Scripts\python.exe `
    -m pytest `
    -q
```

Historical expectation:

- 241 tests collected
- 241 tests passed
- 0 failures

A different result must be preserved and reported rather than hidden.

### 6. Create an output location outside the Git worktree

```powershell
$runRoot = Join-Path `
    (Split-Path (Get-Location).Path -Parent) `
    "self-healing-pipeline-independent-output"

$rawResults = Join-Path $runRoot "raw-results"
$artifactTrials = Join-Path $runRoot "artifact-trials"

New-Item `
    -ItemType Directory `
    -Force `
    -Path $rawResults, $artifactTrials |
    Out-Null
```

### 7. Run the complete historical experiment

```powershell
.\.venv\Scripts\python.exe `
    scripts\run_experiments.py `
    --row-count 10000 `
    --repetitions 30 `
    --initial-seed 42 `
    --artifact-size-bytes 4096 `
    --output-directory $rawResults `
    --artifact-directory $artifactTrials
```

Expected trial population:

- dataframe trials: 660
- artifact trials: 120
- combined trials: 780
- unique trial identifiers: 780

Expected metadata configuration:

- row count: 10,000
- repetitions: 30
- initial seed: 42
- artifact size: 4,096 bytes
- Git commit:
  `e6052e25b4579ef6698b73c1d7c64b50d547e212`

### 8. Compare the reproduced CSV against the preserved reference

Run this from the historical worktree after the experiment completes:

```powershell
$mainClone = Join-Path `
    (Split-Path (Get-Location).Path -Parent) `
    "self-healing-pipeline-research-paper"

$referenceCsv = Join-Path `
    $mainClone `
    "reproducibility\reference-results\2026-06-14\combined_experiment_results.csv"

$reproducedCsv = Join-Path `
    $rawResults `
    "combined_experiment_results.csv"

$comparisonReport = Join-Path `
    $runRoot `
    "deterministic-comparison-report.txt"

.\.venv\Scripts\python.exe `
    (Join-Path $mainClone "scripts\compare_reproduction_results.py") `
    --reference $referenceCsv `
    --reproduced $reproducedCsv `
    --report $comparisonReport
```

The comparison utility:

- checks exact schema order;
- checks 780 rows and unique trial identifiers;
- treats `trial_id` as the alignment key;
- excludes only `runtime_milliseconds` from value equality;
- compares 24 deterministic fields;
- reports runtime statistics separately;
- reports outcome distributions; and
- exits nonzero when deterministic mismatches exist.

Reference combined CSV SHA-256:

`ACFD05D8F3CD0DA5A63274ABBA94C58101454A8DE891E52E127124C34D2AFB4A`

A reproduced full-file hash is expected to differ when runtime measurements
differ. The deterministic comparison, not full-file identity, is the
substantive reproducibility test.

### 9. Preserve evaluator evidence

At minimum preserve:

- `evaluator-pip-freeze.txt`
- complete test output
- complete experiment output
- `experiment_metadata.json`
- reproduced `combined_experiment_results.csv`
- deterministic comparison report
- SHA-256 hashes for all submitted files
- completed evaluator attestation
- all warnings, failures, and deviations

Use this naming convention:

```text
reproducibility/independent-replication/
YYYY-MM-DD-evaluator-slug/
```

Do not place evaluator evidence under `author-reproductions`.

## Expected Controlled Outcomes

Under the historical controlled synthetic interpretation:

- 690 of 690 actual failures are detected;
- 690 of 690 actual failures are classified correctly;
- 0 false positives occur among 90 healthy and boundary controls;
- 360 of 690 actual failures reach verified recovery;
- 180 trials await human approval;
- 150 trials schedule recovery;
- 360 trials reach the recovered cycle state; and
- 120 artifact trials restore their checksum.

Thirty low-severity freshness trials are boundary controls. They carry the
injected scenario label `freshness_violation`, but remain below the detector
threshold.

## Claim Boundaries

A successful independent run can support:

- executability of the historical source;
- dependency reproducibility;
- automated-test reproducibility;
- trial-population reproducibility; and
- deterministic-result reproducibility.

It does not alone establish:

- production effectiveness;
- external adoption;
- customer impact;
- comparative superiority;
- commercial value;
- broad industry significance; or
- equivalent behavior under unseen, compound, ambiguous, or production
  failures.