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
