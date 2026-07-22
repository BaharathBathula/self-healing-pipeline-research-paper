# Reliability-Aware Self-Healing Data Pipeline Framework

## Canonical Research Implementation

This repository is the canonical implementation, experiment, and reproducibility repository for:

**Reliability-Aware Self-Healing Data Pipelines: Automated Failure Detection, Root-Cause Classification, and Policy-Constrained Recovery**

It contains the source code, controlled synthetic experiments, policies, remediation registry, analysis scripts, figures, manuscript materials, and preserved author-generated reference results associated with the research.

## Research Scope

The framework evaluates a policy-constrained reliability-control process for data pipelines consisting of:

1. telemetry collection;
2. failure detection;
3. root-cause classification;
4. remediation selection;
5. policy authorization;
6. remediation execution;
7. post-recovery validation;
8. rollback or human escalation; and
9. incident-evidence preservation.

A remediation attempt is not classified as verified recovery merely because an action was selected or executed. Recovery must also satisfy the configured policy and pass post-recovery validation.

## Implemented Capabilities

- Reproducible synthetic dataset generation
- Controlled failure injection
- Multi-signal failure detection
- Evidence-weighted root-cause classification
- Policy-constrained remediation evaluation
- Remediation execution
- Post-recovery validation
- Rollback and human-escalation paths
- Incident-evidence generation
- Statistical experiment analysis
- Figure and table generation
- Claim-to-artifact traceability

## Evaluated Scenario Categories

The controlled synthetic evaluation includes:

- healthy controls;
- schema drift;
- missing-value spikes;
- duplicate-record generation;
- freshness violations;
- unexpected volume changes;
- transformation-logic failures;
- source-system failures;
- partial-output conditions;
- output-artifact corruption;
- unsupported or unknown failures; and
- low-severity boundary controls.

## Author-Generated Experimental Results

The preserved controlled synthetic evaluation contains 780 unique trials:

- 690 actual injected-failure trials;
- 60 healthy controls; and
- 30 low-severity freshness boundary controls.

Within this specific controlled configuration:

- failure detection: 690 of 690 actual failure trials;
- root-cause classification: 690 of 690 actual failure trials;
- false positives: 0 of 90 healthy and boundary-control trials;
- verified recovery: 360 of 690 actual failure trials; and
- verified-recovery rate: 52.17%.

These results are author-generated. They do not establish equivalent production performance, commercial deployment, customer outcomes, broad adoption, or field-level significance.

## Versioned Reference Results

Exact preserved copies of the trial-level and derived result files are located at:

```text
reproducibility/reference-results/2026-06-14/
```

That directory contains:

- `combined_experiment_results.csv`
- `scenario_summary.csv`
- `classification_confusion_matrix.csv`
- `SHA256_MANIFEST.txt`
- an evidence-status README

Generated experiment directories remain excluded by default so experiments may be rerun without silently modifying the preserved reference-results package.

## Reproducibility Position

The repository includes:

- a Dockerfile;
- dependency specifications;
- versioned source code;
- experiment runners;
- analysis scripts;
- test files;
- policy configurations;
- remediation definitions; and
- preserved reference results.

Independent reproduction has not yet been completed. External evaluators must execute the framework in their own environment and report their results separately.

## Project Structure

```text
implementation/
├── src/
├── tests/
├── data/
├── experiments/
├── policies/
├── remediation_registry/
├── telemetry/
├── incident_evidence/
├── scripts/
├── figures/
├── manuscript/
├── paper-ieee-access-working/
├── reproducibility/
└── docs/
```

## Relationship to the Showcase Repository

The separate repository:

```text
BaharathBathula/self-healing-data-pipeline-framework
```

is a conceptual and presentation-oriented prototype.

It is not the canonical implementation used to generate the research-paper results. The source code, experiment history, reference results, and manuscript evidence for the controlled study are maintained in this repository.

## Evidence Limitations

- The current evaluation uses synthetic data and controlled failure injection.
- No production-deployment claim is made.
- No customer-result claim is made.
- No broad-industry-adoption claim is made.
- The results have not yet been independently replicated.
- Originality and comparative significance remain subject to prior-art analysis and independent expert evaluation.
- Negative findings, unsupported scenarios, and limitations must remain preserved.

## Research Integrity

- Raw and derived results must remain traceable to versioned artifacts.
- Synthetic findings must always be identified as synthetic.
- Attempted remediation must not be reported as verified recovery.
- Unsuccessful trials must not be removed merely because they weaken a claim.
- Any excluded trial must have a documented technical reason.
- Future corrections must be made transparently through Git commits.

## Current Status

Author-generated implementation and controlled synthetic evaluation completed.

Independent replication, external operational validation, and prior-art evaluation are pending.

## Independent Replication Quick Start

A dedicated external-evaluator procedure is available at:

```text
docs/independent-replication-guide.md
```

The historical controlled experiment must be evaluated from source commit:

```text
e6052e25b4579ef6698b73c1d7c64b50d547e212
```

Recommended environment:

- Python 3.12.2
- dependencies from `requirements-lock.txt`
- dependency-lock SHA-256:
  `6C7C3B4E5C644EEF0DFE7FB42333D52AC97E706BC83E3065D00E0B4C2F30670A`

From a detached checkout of the historical source commit, an evaluator should
create an isolated environment, install the locked dependencies, and explicitly
place the repository root on `PYTHONPATH`:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
$env:PYTHONPATH = (Get-Location).Path
```

Run the automated tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Run the controlled experiment:

```powershell
.\.venv\Scripts\python.exe `
    scripts\run_experiments.py `
    --row-count 10000 `
    --repetitions 30 `
    --initial-seed 42 `
    --artifact-size-bytes 4096 `
    --output-directory <EVALUATOR_OUTPUT_DIRECTORY> `
    --artifact-directory <EVALUATOR_ARTIFACT_DIRECTORY>
```

Expected trial population:

- 660 dataframe trials;
- 120 artifact trials;
- 780 combined trials; and
- 780 unique trial identifiers.

Preserved reference combined CSV SHA-256:

```text
ACFD05D8F3CD0DA5A63274ABBA94C58101454A8DE891E52E127124C34D2AFB4A
```

Use:

```text
scripts/compare_reproduction_results.py
```

to compare an evaluator-generated combined CSV against the preserved reference.
The utility excludes only `runtime_milliseconds` from deterministic equality.

External evidence must be stored separately under:

```text
reproducibility/independent-replication/
```

A rerun must not be described as independent unless the external evaluator
performed it without author control and documented identity, environment,
commands, results, hashes, deviations, failures, and negative findings.

## Author

**Baharath Bathula**
