# Author-Generated Reference Results — June 14, 2026

## Purpose

This directory preserves an exact, versioned copy of the author-generated
experimental results associated with the controlled synthetic evaluation of
the Reliability-Aware Self-Healing Data Pipeline Framework.

These files were generated on June 14, 2026 and added to version control on
July 20, 2026 for reproducibility, provenance, and independent technical
review.

They must not be interpreted as production telemetry, customer results,
independent replication, commercial deployment, or evidence of broad
industry adoption.

## Included Files

- `combined_experiment_results.csv` — trial-level results
- `scenario_summary.csv` — derived scenario-level statistics
- `classification_confusion_matrix.csv` — derived classification matrix
- `SHA256_MANIFEST.txt` — integrity hashes for the preserved files

## Experimental Population

The trial-level file contains 780 unique controlled synthetic trials:

- 690 injected-failure trials
- 60 healthy controls
- 30 low-severity freshness boundary controls

The low-severity freshness boundary controls use the injected scenario label
`freshness_violation` in the raw file, but the injected magnitude remains
below the detector threshold. For analysis, those 30 trials are treated as
boundary controls rather than actual failures.

## Author-Generated Findings

Within the controlled synthetic configuration:

- Failure detection: 690 of 690 actual failure trials
- Root-cause classification: 690 of 690 actual failure trials
- False positives: 0 of 90 healthy and boundary-control trials
- Verified recovery: 360 of 690 actual failure trials
- Verified-recovery rate: 52.17%

These figures describe only the preserved synthetic configuration. They do
not establish equivalent performance in production or other environments.

## Verified-Recovery Definition

A failure is counted as verified recovery only when the workflow records that:

1. the failure was detected;
2. the root cause was classified;
3. a remediation was available;
4. the remediation was permitted under policy;
5. execution completed; and
6. post-recovery validation confirmed restoration.

Scheduled recovery or pending human approval is not counted as verified
recovery.

## Evidence Status

These results are author-generated and have not yet been independently
replicated. Independent evaluators must run the versioned implementation and
report their own results separately.

The original result files remain preserved without substantive modification.
