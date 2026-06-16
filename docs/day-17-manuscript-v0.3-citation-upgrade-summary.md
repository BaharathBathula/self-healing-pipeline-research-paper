# Day 17 — Manuscript v0.3 Citation Upgrade Summary

Paper title: **Reliability-Aware Self-Healing Data Pipelines: Automated Failure Detection, Root-Cause Classification, and Policy-Constrained Recovery**

Date: 2026-06-15

## Day 17 Objective

Day 17 creates `docs/manuscript-v0.3.md` by upgrading the citation quality and rewriting the Related Work section.

The focus is credibility, not new claims.

---

## What Changed From v0.2 to v0.3

1. Added stronger citation support in the Introduction.
2. Rewrote the Related Work section to read less like a tool catalog.
3. Used research references for research claims.
4. Kept official documentation references only for tool descriptions.
5. Removed documentation-heavy references that were not directly used.
6. Added citation numbers throughout Related Work.
7. Preserved the Day 14 runtime statistics.
8. Preserved safer baseline wording.
9. Preserved figure links and artifact traceability.
10. Preserved the conservative interpretation of 100% detection/classification.

---

## Major Citation Improvements

### Introduction

The Introduction now cites:

- data-pipeline quality and root causes,
- hidden technical debt,
- production ML pipeline complexity.

### Related Work

The Related Work section now cites:

- Airflow docs and Airflow empirical workflow challenges,
- Great Expectations and dbt documentation for validation tooling,
- data-pipeline quality research,
- Google SRE monitoring,
- AIOps mapping research,
- root-cause knowledge mining,
- autonomic computing,
- Open Policy Agent documentation.

---

## References Removed or Demoted

The following references were removed from the main v0.3 reference list because they were not directly discussed in the manuscript:

- Google Cloud Auto Data Quality
- Delta Lake Constraints

They can be reintroduced later only if the manuscript explicitly discusses those systems.

---

## Current v0.3 Status

`manuscript-v0.3.md` is stronger than v0.2 because it now has a credible Related Work foundation.

However, it is still not final submission-ready.

Remaining work:

1. Check citation formatting against the target venue.
2. Add 2–3 stronger data observability references.
3. Verify whether arXiv references are acceptable for the target venue.
4. Convert markdown figures into final submission format.
5. Run a final overclaiming audit.
6. Decide target journal/conference formatting.

---

## Day 18 Handoff

Day 18 should focus on **final research-paper quality audit before venue formatting**.

Recommended Day 18 output:

```text
docs/day-18-manuscript-quality-audit.md
```

Day 18 should check:

1. Whether every claim has evidence.
2. Whether every citation is used correctly.
3. Whether figures are placed correctly.
4. Whether the paper still overclaims anything.
5. Whether the paper is ready for target-venue formatting.
