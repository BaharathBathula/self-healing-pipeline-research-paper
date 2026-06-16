# Day 20 — Manuscript v0.4 Quality Edits Summary

Paper title: **Reliability-Aware Self-Healing Data Pipelines: Automated Failure Detection, Root-Cause Classification, and Policy-Constrained Recovery**

Date: 2026-06-15

## Day 20 Objective

Day 20 creates `docs/manuscript-v0.4.md` with final quality edits before LaTeX conversion.

This day focuses on targeted improvement, not broad rewriting. The goal is to make the manuscript cleaner, more defensible, and ready for Day 21 IEEE-style LaTeX conversion.

---

## Files Created

```text
docs/manuscript-v0.4.md
docs/references-v0.4.bib
docs/day-20-manuscript-v0.4-quality-edits-summary.md
```

---

## What Changed From v0.3 to v0.4

### 1. Added Stronger Data Observability and Monitoring References

The Related Work section now adds stronger monitoring/data-quality references:

- Auto-Validate-by-History for recurring production data-pipeline validation.
- Evaluating Data Quality Tools for comparative data-quality tooling discussion.

These strengthen the previously thin observability/data-quality monitoring subsection.

### 2. Added Monitoring References in the Introduction

The Introduction now states that recent work on recurring data-pipeline validation and comparative tool evaluation reinforces the need for automated monitoring and validation.

### 3. Expanded Section 2.3 Data Observability and Monitoring

Section 2.3 now explains:

- monitoring and observability signals,
- recurring data-pipeline validation,
- historical execution statistics for data-quality issue detection,
- data-quality tool capabilities and tradeoffs,
- why monitoring still does not equal governed recovery.

### 4. Added Section 3.10 Implementation Summary

The Methodology section now includes a short implementation summary covering:

- trial configuration,
- deterministic experiment control plane,
- observed data and artifact metadata,
- detection outcome representation,
- root-cause classification representation,
- remediation registry/action fields,
- policy-related outcome fields,
- post-recovery verification.

This addresses the Day 18 audit concern that the implementation was not described enough.

### 5. Added Recovery Variation Paragraph

Section 4.3 now explains why recovery varies by failure scenario:

- some scenarios have supported policy-approved remediations,
- others are unsupported, unsafe, unverifiable, or intentionally escalated,
- lower recovery is not necessarily detection or classification failure.

### 6. Reduced Discussion Repetition

Section 5.1 and Section 5.2 were tightened to avoid repeating Results too heavily.

### 7. Added Section 6.7 Synthetic Data and Failure Taxonomy Bias

Threats to Validity now directly addresses:

- predefined synthetic taxonomy,
- possible detector/classifier advantage,
- why 100% accuracy should not be generalized,
- need for real incidents or independently constructed failure scenarios.

### 8. Updated References

Two new references were added:

```text
[13] Auto-Validate by-History
[14] Evaluating Data Quality Tools
```

A new BibTeX file was also created:

```text
docs/references-v0.4.bib
```

---

## Current v0.4 Status

`manuscript-v0.4.md` is the strongest Markdown manuscript so far.

It is ready for Day 21 LaTeX conversion.

It is still not submission-ready because venue formatting, figure handling, and final citation style are not done.

---

## Remaining Risks

1. The experiment is still synthetic-only.
2. There is still no true alert-only or static-rule baseline comparison.
3. The 100% detection/classification results still require careful qualification.
4. arXiv references may need venue-specific replacement or supplementation later.
5. Markdown figures must be converted to LaTeX figure environments.
6. The reference list must be integrated into BibTeX during LaTeX conversion.

---

## Day 21 Handoff

Day 21 should create the IEEE-style LaTeX paper package.

Recommended structure:

```text
paper/
├── main.tex
├── references.bib
├── sections/
│   ├── 01_introduction.tex
│   ├── 02_related_work.tex
│   ├── 03_methodology.tex
│   ├── 04_results.tex
│   ├── 05_discussion.tex
│   ├── 06_threats_to_validity.tex
│   └── 07_conclusion.tex
└── figures/
    ├── figure_1_accuracy_by_scenario.pdf
    ├── figure_2_recovery_by_scenario.pdf
    ├── figure_3_runtime_distribution.pdf
    └── figure_4_classification_confusion_matrix.pdf
```

Day 21 should not add new research claims. It should convert the approved v0.4 manuscript into LaTeX.
