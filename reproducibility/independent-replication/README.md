# Independent Replication Evidence

This directory is reserved for evidence produced by external evaluators.

Do not place author-operated reruns in this directory. Author-operated records
belong under:

`reproducibility/author-reproductions/`

## Directory Naming

Use:

```text
YYYY-MM-DD-evaluator-slug/
```

Example:

```text
2026-08-05-jane-doe/
```

## Minimum Contents

Each evaluator directory should contain:

- completed evaluator attestation;
- environment and dependency record;
- exact command transcript;
- automated-test output;
- experiment output;
- generated metadata;
- reproduced combined CSV;
- deterministic comparison report;
- SHA-256 manifest;
- deviations and negative findings; and
- evaluator signature date.

## Provenance Rule

Evidence must identify who generated it, when it was generated, the exact
source commit, the environment, and whether the author assisted during
execution.

A result must not be called independent merely because it is stored here.
Independence depends on how the work was actually performed and documented.

## Canonical Guide

See:

`docs/independent-replication-guide.md`