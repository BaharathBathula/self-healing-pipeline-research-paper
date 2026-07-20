# Two-Repository Governance

## Repositories

### Framework Repository

Repository:

`BaharathBathula/self-healing-data-pipeline-framework`

This is an actively supported public-facing framework repository.

Its responsibilities include:

- installation and quick-start workflows;
- demonstrations and practical examples;
- public architecture documentation;
- reusable framework interfaces;
- deployment examples;
- future product-oriented releases;
- external contributions;
- pilot integrations; and
- practical-use and adoption evidence.

### Research Repository

Repository:

`BaharathBathula/self-healing-pipeline-research-paper`

This is an actively supported research, experimentation, and reproducibility repository.

Its responsibilities include:

- controlled failure injection;
- reference detection and classification logic;
- policy-constrained remediation;
- post-recovery validation;
- experiment runners;
- statistical analysis;
- preserved author-generated reference results;
- research-manuscript materials;
- independent-replication support; and
- technical evidence preservation.

## Current Implementation Relationship

The repositories are related by research purpose and framework concept, but
they are not currently identical codebases.

The framework repository contains a lighter public-facing implementation and
supporting demonstration materials.

The research repository contains the deeper implementation used for the
controlled synthetic experiments and preserved research results.

No claim should be made that a framework release reproduces the research
results unless that release has been tested against the same experiment
configuration and documented through a version-mapping record.

## Source-of-Truth Rules

The research repository is the source of truth for:

- preserved experimental results;
- research metric definitions;
- experiment configurations;
- recovery-verification criteria;
- manuscript claims; and
- replication evidence.

The framework repository is the source of truth for:

- public framework packaging;
- installation guidance;
- examples and demonstrations;
- public deployment interfaces;
- framework releases; and
- external-use documentation.

## Migration Rules

Research capabilities may be incorporated into the framework repository only
through documented changes.

Each migration should record:

1. research repository commit;
2. framework repository commit;
3. modules or capabilities transferred;
4. behavioral differences;
5. tests performed;
6. experiment or validation results;
7. known limitations; and
8. release or version identifier.

Files must not be copied between repositories without documenting their
origin and purpose.

## Result-Claim Rules

Research results must remain tied to the exact research commit, dependency
environment, experiment configuration, and preserved result artifacts that
generated them.

Framework documentation must not attribute research performance to a
framework release unless that release independently reproduces the result.

A selected or executed remediation must not be described as verified recovery
unless post-recovery validation confirms restoration.

## Support Status

Both repositories are actively supported.

Neither repository is abandoned, archived, deprecated, or merely historical.

Their different responsibilities are intentional and must remain clearly
documented.
