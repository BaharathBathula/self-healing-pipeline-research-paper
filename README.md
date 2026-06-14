# Policy-Constrained Self-Healing Data Pipeline Research

This repository contains the implementation, experiments, datasets, policies, and reproducibility artifacts for the research paper:

**Reliability-Aware Self-Healing Data Pipelines: Automated Failure Detection, Root-Cause Classification, and Policy-Constrained Recovery**

## Research Objective

The project evaluates whether a policy-constrained self-healing control plane can improve data-pipeline failure detection and recovery while reducing unsafe remediation compared with:

1. Alert-only monitoring with operator-executed recovery
2. Static rule-based automated recovery
3. Policy-constrained self-healing recovery

## Core Capabilities

* Synthetic data-pipeline execution
* Controlled failure injection
* Multi-signal failure detection
* Root-cause classification
* Policy-based remediation approval
* Automated recovery execution
* Post-recovery validation
* Rollback and human escalation
* Immutable incident evidence
* Reproducible experiment analysis

## Planned Failure Categories

* Schema drift
* Missing-value spike
* Duplicate-record generation
* Data-freshness violation
* Unexpected volume change
* Transformation-logic failure
* Source-system failure
* Partial or corrupted output
* Unknown failure
* Healthy control runs

## Project Structure

```text
implementation/
├── src/
├── tests/
├── data/
│   ├── raw/
│   ├── processed/
│   └── fixtures/
├── experiments/
│   ├── configs/
│   ├── raw_results/
│   ├── derived_results/
│   └── experiment_schema.json
├── policies/
├── remediation_registry/
├── telemetry/
├── incident_evidence/
├── notebooks/
├── scripts/
├── figures/
└── docs/
```

## Research Integrity

All final experimental results will be generated from preserved raw trial records.

Unsuccessful trials will not be removed solely because they weaken the research hypotheses. Any excluded trial must include a documented technical reason.

## Status

Research design completed. Implementation in progress.
