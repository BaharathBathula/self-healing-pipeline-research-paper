# Day 14 — Runtime Statistics and Artifact Traceability

Paper title: **Reliability-Aware Self-Healing Data Pipelines: Automated Failure Detection, Root-Cause Classification, and Policy-Constrained Recovery**

Date: 2026-06-15

## Day 14 Objective

Day 14 strengthens the evidence layer before creating `manuscript-v0.2.md`.

The goal is to verify:

1. runtime statistics,
2. artifact-to-claim traceability,
3. baseline-domain evidence,
4. figure file paths,
5. manuscript edits required before v0.2.

This day is intentionally evidence-focused. The manuscript should not claim runtime or baseline results unless the corresponding artifacts exist and can be traced.

---

## Important Finding

The GitHub-accessible repository currently exposes the figure-generation script, but the expected raw result CSV, derived result CSVs, and figure image files were not accessible through the GitHub connector at the expected paths.

That means exact runtime statistics should **not** be inserted into the paper yet unless they are computed locally from the raw experiment file.

Expected raw and derived inputs:

```text
experiments/raw_results/combined_experiment_results.csv
experiments/derived_results/scenario_summary.csv
experiments/derived_results/classification_confusion_matrix.csv
```

Expected figure output directory:

```text
figures/
```

Expected figure files:

```text
figures/figure_1_accuracy_by_scenario.png
figures/figure_2_recovery_by_scenario.png
figures/figure_3_runtime_distribution.png
figures/figure_4_classification_confusion_matrix.png
```

---

# 1. Runtime Statistics Status

## Current Status

Runtime statistics are **not yet manuscript-ready** from the GitHub-accessible evidence layer.

Reason:

- The figure-generation script expects `combined_experiment_results.csv`.
- The runtime distribution uses the `runtime_milliseconds` column.
- The expected raw CSV was not accessible from GitHub at the expected path.
- Therefore, mean, median, min, max, and p95 runtime should not be fabricated.

## Required Runtime Summary Table

After running the local helper script, the paper should include a table like this:

| Metric | Value |
|---|---:|
| Runtime record count | TBD |
| Mean runtime milliseconds | TBD |
| Median runtime milliseconds | TBD |
| Minimum runtime milliseconds | TBD |
| Maximum runtime milliseconds | TBD |
| p95 runtime milliseconds | TBD |

## Required Runtime-by-Domain Table

After running the local helper script, include:

| Experiment domain | Trial count | Mean ms | Median ms | p95 ms |
|---|---:|---:|---:|---:|
| TBD | TBD | TBD | TBD | TBD |

## Manuscript Rule

Do not write:

> The framework has low runtime overhead.

Unless concrete runtime statistics support it.

Safer wording for now:

> Runtime was recorded at the trial level and summarized by experiment domain. Exact runtime statistics should be reported from the preserved raw results before submission.

---

# 2. Local Runtime Computation Helper

Save the helper script as:

```text
scripts/day14_runtime_traceability.py
```

Then run:

```powershell
cd C:\Research\self-healing-pipeline-research-paper\implementation
python scripts/day14_runtime_traceability.py
```

The helper script checks:

- raw result file existence,
- derived result file existence,
- runtime statistics,
- runtime by experiment domain,
- baseline domain names,
- expected figure paths,
- artifact-to-claim mapping.

---

# 3. Artifact-to-Claim Traceability Table

| Paper claim | Required artifact | Status | Action |
|---|---|---|---|
| Total trials = 780 | `experiments/raw_results/combined_experiment_results.csv` | Not GitHub-verified | Verify locally and commit or document exclusion |
| Injected failures = 690 | `combined_experiment_results.csv` or derived summary | Not GitHub-verified | Verify locally |
| Healthy controls = 60 | `combined_experiment_results.csv` or derived summary | Not GitHub-verified | Verify locally |
| Boundary controls = 30 | `combined_experiment_results.csv` or derived summary | Not GitHub-verified | Verify locally |
| Detection accuracy = 100% | `experiments/derived_results/scenario_summary.csv` | Not GitHub-verified | Verify locally |
| Classification accuracy = 100% | `scenario_summary.csv` and `classification_confusion_matrix.csv` | Not GitHub-verified | Verify locally |
| Verified recovery = 52.17% | `scenario_summary.csv` or raw trial-level recovery column | Not GitHub-verified | Verify locally |
| Runtime distribution | `combined_experiment_results.csv` column `runtime_milliseconds` | Not GitHub-verified | Compute locally |
| Figure 1 | `figures/figure_1_accuracy_by_scenario.png` | Not GitHub-verified | Commit figure or regenerate locally |
| Figure 2 | `figures/figure_2_recovery_by_scenario.png` | Not GitHub-verified | Commit figure or regenerate locally |
| Figure 3 | `figures/figure_3_runtime_distribution.png` | Not GitHub-verified | Commit figure or regenerate locally |
| Figure 4 | `figures/figure_4_classification_confusion_matrix.png` | Not GitHub-verified | Commit figure or regenerate locally |
| Figure-generation reproducibility | `scripts/generate_figures.py` | GitHub-verified | Keep |

---

# 4. Baseline-Domain Check

## Why This Matters

The paper objective mentions comparison against:

1. alert-only monitoring with operator-executed recovery,
2. static rule-based automated recovery,
3. policy-constrained self-healing recovery.

That creates a reviewer risk.

If the raw results do not contain comparable baseline trials, the paper must not claim that the policy-constrained system empirically outperformed alert-only or static-rule baselines.

## Required Check

Run the helper script and inspect unique values in:

```text
experiment_domain
```

Possible expected values might include:

```text
alert_only
static_rule
policy_constrained
```

or similar names.

## Manuscript Rule

If only policy-constrained trials exist, write:

> The current evaluation focuses on the policy-constrained self-healing control plane. Full comparison against alert-only and static-rule baselines remains future work.

If all three domains exist with comparable trials, then baseline comparison can be added to Results.

---

# 5. Figure Path Verification

## Expected Figure Paths

| Figure | Expected path | Manuscript insertion location |
|---|---|---|
| Figure 1 | `figures/figure_1_accuracy_by_scenario.png` | After Section 4.2 |
| Figure 2 | `figures/figure_2_recovery_by_scenario.png` | After Section 4.3 |
| Figure 3 | `figures/figure_3_runtime_distribution.png` | After Section 4.4 |
| Figure 4 | `figures/figure_4_classification_confusion_matrix.png` | After Section 4.2 or after classification paragraph |

## Markdown Insertions for v0.2

Use these paths from `docs/manuscript-v0.2.md`:

```markdown
![Figure 1. Detection and root-cause classification accuracy by injected scenario.](../figures/figure_1_accuracy_by_scenario.png)

![Figure 4. Root-cause classification confusion matrix.](../figures/figure_4_classification_confusion_matrix.png)

![Figure 2. Verified recovery rate by failure scenario.](../figures/figure_2_recovery_by_scenario.png)

![Figure 3. Self-healing cycle runtime distribution.](../figures/figure_3_runtime_distribution.png)
```

---

# 6. Evidence Gaps Before Manuscript v0.2

## Gap 1: Runtime Statistics

The manuscript currently says runtime was measured but does not report exact values.

Required before v0.2:

- mean runtime,
- median runtime,
- min runtime,
- max runtime,
- p95 runtime,
- runtime by experiment domain.

## Gap 2: Artifact Availability

The paper claims reproducibility. The repository should make the reproducibility artifacts visible or clearly document why some are excluded.

Required before v0.2:

- confirm whether raw and derived CSV files are committed,
- confirm whether figure files are committed,
- if not committed, add a reproducibility note explaining how to regenerate them.

## Gap 3: Baseline Claims

The paper should not imply completed baseline comparison unless raw results contain baseline domains.

Required before v0.2:

- inspect unique `experiment_domain` values,
- decide whether baseline comparison is supported or future work.

## Gap 4: Figure Integration

The manuscript references figures but does not embed them.

Required before v0.2:

- insert markdown image links,
- verify relative paths from `docs/`.

---

# 7. Recommended Reproducibility Policy

Use this rule:

> Commit derived summaries and publication figures. Commit raw synthetic trial outputs if file size is reasonable. If raw files are too large, provide a generation script and a reproducibility note explaining how to recreate them.

For this project, the raw CSV is likely small enough to commit unless it contains sensitive information. Since the data is synthetic, there is no obvious privacy reason to exclude it.

---

# 8. Day 14 Local Verification Commands

Run these from the repo root:

```powershell
cd C:\Research\self-healing-pipeline-research-paper\implementation

Test-Path experiments\raw_results\combined_experiment_results.csv
Test-Path experiments\derived_results\scenario_summary.csv
Test-Path experiments\derived_results\classification_confusion_matrix.csv

Get-ChildItem figures\figure_* | Select-Object Name, Length

python scripts\day14_runtime_traceability.py
```

If the files exist locally but are not committed, run:

```powershell
git status --short
```

Then decide whether to commit them.

---

# 9. Manuscript v0.2 Edits Enabled by Day 14

After local verification, v0.2 should include:

1. A runtime statistics table.
2. A runtime-by-domain table if multiple domains exist.
3. Embedded figure links.
4. A claim-to-artifact traceability table in Appendix B.
5. Safer baseline wording based on actual domains.

---

# 10. Recommended Text for Manuscript v0.2

## Runtime Placeholder Until Stats Are Computed

Use this if runtime stats are still missing:

> Runtime was recorded at the trial level using the `runtime_milliseconds` field. The runtime distribution is visualized in Figure 3. Exact summary statistics should be computed from the preserved raw results before submission.

## Runtime Text After Stats Are Computed

Use this once exact values are available:

> Across all trial records with valid runtime measurements, the mean self-healing cycle runtime was `<MEAN>` ms, the median runtime was `<MEDIAN>` ms, and the p95 runtime was `<P95>` ms. Runtime varied by experiment domain, as shown in Figure 3.

## Baseline-Safe Text

Use this unless baseline trials are verified:

> Although the broader research objective supports comparison with alert-only and static-rule approaches, the current manuscript reports only experiment domains represented in the preserved trial records. Full baseline comparison remains future work unless comparable baseline trials are present in the raw results.

---

# Day 14 Completion Checklist

- [x] Expected runtime source identified.
- [x] Runtime statistic requirements defined.
- [x] Runtime computation helper prepared.
- [x] Artifact-to-claim traceability table prepared.
- [x] Baseline-domain check defined.
- [x] Figure path verification plan prepared.
- [x] Evidence gaps before v0.2 documented.
- [x] Manuscript v0.2 edit requirements defined.
- [x] Day 15 handoff defined.

---

# Day 15 Handoff

Day 15 should use the Day 14 verification results to create `docs/manuscript-v0.2.md`.

Do not create v0.2 until the local helper script is run or the runtime/statistics gap is explicitly marked as pending.
