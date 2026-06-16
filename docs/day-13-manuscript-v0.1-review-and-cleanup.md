# Day 13 — Manuscript v0.1 Review and Cleanup

Paper title: **Reliability-Aware Self-Healing Data Pipelines: Automated Failure Detection, Root-Cause Classification, and Policy-Constrained Recovery**

Date: 2026-06-15

## Day 13 Objective

Day 13 reviews `docs/manuscript-v0.1.md` as a complete research paper draft. The goal is to identify repetition, overclaiming risk, weak sections, missing evidence, figure-placement needs, and the exact cleanup plan for `manuscript-v0.2.md`.

Day 13 is intentionally a review and cleanup day. It should not add broad new claims. The manuscript already has the core argument. The next improvement is precision.

---

# Executive Review

## Current Manuscript Status

`manuscript-v0.1.md` is a valid first full draft. It has the required research-paper structure:

- Title
- Abstract
- Keywords
- Introduction
- Related Work
- Methodology
- Results
- Discussion
- Threats to Validity
- Conclusion and Future Work
- References
- Appendices

The paper is no longer just notes. It is now a continuous manuscript.

## Current Quality Assessment

| Area | Current status | Required action |
|---|---|---|
| Structure | Strong | Keep section order |
| Core argument | Strong | Preserve and tighten |
| Abstract | Good but slightly long | Tighten and sharpen |
| Introduction | Good but repetitive | Reduce overlap with Methodology |
| Related Work | Useful but citation-light | Add peer-reviewed sources |
| Methodology | Strongest section | Keep strict recovery definition |
| Results | Good but needs exact figure insertion | Insert figure references and paths |
| Discussion | Good but repetitive | Remove repeated explanation |
| Threats to Validity | Strong | Keep direct and honest |
| References | Weak | Convert to formal citation style |
| Figures | Missing from manuscript body | Add figure placeholders |
| Baselines | High risk | Remove/qualify unless baseline data exists |

## Overall Verdict

The manuscript is credible as a v0.1 draft, but it is not submission-ready.

The biggest risks are:

1. The 100% detection and classification results may look unrealistic if not repeatedly qualified as synthetic and controlled.
2. The paper mentions baseline comparison against alert-only and static-rule approaches, but unless raw baseline results exist, those claims must be softened.
3. The references section currently relies too heavily on documentation and arXiv-style references.
4. Runtime results are mentioned but not quantified.
5. Figures are described but not embedded or placed in the manuscript.

---

# Core Argument Check

The paper’s central argument is strong:

> Self-healing data pipelines should not be evaluated only by whether they detect failures or attempt automated repairs. They should be evaluated as policy-constrained reliability-control systems where detection, diagnosis, remediation approval, execution, and post-recovery validation are measured separately.

This argument should stay. Everything in v0.2 should support it.

## What Works

The manuscript clearly explains that:

- task-level pipeline success is insufficient,
- detection does not equal recovery,
- policy constraints are safety features,
- verified recovery is stricter than attempted remediation,
- escalation can be a valid outcome,
- synthetic results should be interpreted conservatively.

## What Needs Tightening

The same argument appears too many times. It currently appears in:

- Abstract
- Introduction
- Methodology
- Results
- Discussion
- Conclusion

For v0.2, keep the idea but reduce repetition:

- Introduce it once in the Introduction.
- Define it formally in Methodology.
- Report it in Results.
- Interpret it in Discussion.
- Summarize it briefly in Conclusion.

---

# Section-by-Section Review

## Title

Current title:

**Reliability-Aware Self-Healing Data Pipelines: Automated Failure Detection, Root-Cause Classification, and Policy-Constrained Recovery**

### Assessment

The title is strong and specific. Keep it.

### Reason

It communicates:

- domain: data pipelines,
- system type: self-healing,
- technical functions: detection and classification,
- differentiator: policy-constrained recovery.

No title change is needed for v0.2.

---

## Abstract Review

### Current Strength

The abstract clearly covers:

- problem,
- existing tool limitation,
- proposed framework,
- experiment size,
- results,
- main interpretation.

### Current Weakness

The abstract is a little dense. It also lists too many failure examples in one sentence.

### v0.2 Cleanup Action

Shorten the abstract to approximately 175–225 words.

### Recommended v0.2 Abstract

Reliable data pipelines support analytics, machine learning, compliance reporting, and operational decision-making, but failures such as schema drift, data-quality degradation, freshness violations, transformation defects, and corrupted outputs often require more than task-level retries or alerting. Existing systems provide workflow orchestration, data-quality validation, observability, incident response, and policy enforcement, but these capabilities are commonly evaluated as separate functions rather than as an end-to-end recovery lifecycle. This paper presents a reliability-aware self-healing control plane for data pipelines that separates failure detection, root-cause classification, policy-constrained remediation, execution, post-recovery validation, rollback or escalation, and incident evidence preservation. A reproducible synthetic experiment with 780 trials evaluates the framework across injected failures, healthy controls, and boundary controls. Under the current controlled experiment configuration, the framework achieved 100% failure detection accuracy and 100% root-cause classification accuracy, while verified recovery was achieved in 52.17% of injected failure trials. The results show that self-healing data pipelines should be evaluated using separate metrics for detection, diagnosis, and verified recovery because accurate detection does not guarantee safe or validated remediation.

---

## Keywords Review

### Current Strength

The current keywords are relevant.

### Current Weakness

There are too many. Most venues prefer 5–8.

### v0.2 Cleanup Action

Use 7 keywords:

- self-healing data pipelines
- data reliability
- data observability
- root-cause classification
- policy-constrained automation
- failure injection
- verified recovery

---

## Introduction Review

### Current Strength

The Introduction is strong. It explains the problem, gap, approach, results, and contributions.

### Current Weakness

It overlaps heavily with the Methodology section. The Introduction currently explains too much about the staged lifecycle.

### v0.2 Cleanup Action

Reduce technical architecture detail in the Introduction. Keep only enough to position the paper.

### Keep

Keep this logic:

1. Data pipelines are operationally critical.
2. Pipeline failures can occur even when jobs do not crash.
3. Existing tools solve parts of the problem.
4. The paper proposes policy-constrained self-healing.
5. The experiment evaluates detection, classification, and verified recovery separately.

### Cut or Compress

Compress this sentence group:

> The framework models self-healing as a staged lifecycle: failure injection, telemetry collection, failure detection, root-cause classification, remediation selection, policy approval, recovery execution, post-recovery validation, rollback or escalation, and incident evidence preservation.

In the Introduction, replace with:

> The framework evaluates self-healing as a staged lifecycle from failure detection to policy-approved and post-validated recovery.

Save the full stage list for Methodology.

---

## Contributions Review

### Current Strength

The five contributions are solid.

### Current Weakness

Contribution 5 is too operational and sounds like a repository feature rather than a research contribution.

### v0.2 Cleanup Action

Revise contribution 5.

Current:

> Publication-ready reproducibility artifacts, including experiment outputs, derived result summaries, figure-generation scripts, and documentation.

Better:

> A reproducibility package that preserves trial-level outputs, derived summaries, figure-generation scripts, and documentation for independent inspection and extension.

This sounds more research-oriented.

---

## Related Work Review

### Current Strength

The Related Work section is well organized by category.

### Current Weakness

It still reads like a tool survey in places. It needs more research framing and fewer documentation-only references.

### v0.2 Cleanup Action

Add stronger peer-reviewed citations for:

1. Data observability
2. Data quality in pipelines
3. AIOps/root-cause analysis
4. Autonomic/self-healing systems
5. Data pipeline reliability

### Keep Documentation References Only For Tools

Documentation references are acceptable when describing specific tools such as Airflow, Great Expectations, dbt, Delta Lake, Google Cloud, and OPA. But the research argument should not depend only on documentation.

### Related Work Rewrite Direction

Each subsection should follow this pattern:

1. What the area contributes.
2. Why it is relevant.
3. What it does not fully solve.
4. How this paper differs.

---

## Methodology Review

### Current Strength

Methodology is the strongest section. It has:

- architecture,
- taxonomy,
- trial design,
- procedure,
- metrics,
- strict recovery definition,
- reproducibility scope,
- assumptions.

### Current Weakness

It is a little long, but that is acceptable for v0.1. In v0.2, it should be slightly tightened.

### v0.2 Cleanup Action

Keep the strict recovery success definition exactly. This is one of the paper’s strongest contributions.

### Do Not Remove

Do not remove this idea:

> Recovery is successful only when the remediation is policy-approved, executed successfully, and validated after execution.

### Add in v0.2

Add a concise methodology table:

| Stage | Input | Output | Metric or evidence |
|---|---|---|---|
| Failure injection | Scenario configuration | Injected condition | Trial metadata |
| Detection | Telemetry signals | Failure/no-failure decision | Detection accuracy |
| Classification | Detected failure | Root-cause label | Classification accuracy |
| Policy evaluation | Candidate remediation | Approved/rejected decision | Policy outcome |
| Recovery execution | Approved remediation | Execution result | Recovery attempt status |
| Validation | Recovered output | Pass/fail validation | Verified recovery |
| Evidence preservation | Trial record | Reproducibility artifact | Raw/derived results |

This will make the methodology clearer.

---

## Results Review

### Current Strength

The Results section correctly reports the corrected numbers.

### Current Weakness

Figures are described but not inserted. Runtime is discussed without exact runtime statistics.

### v0.2 Cleanup Action

Add figure placeholders directly in the Results section.

Recommended figure placement:

After Section 4.2 Detection and Root-Cause Classification:

```markdown
![Figure 1. Detection and root-cause classification accuracy by injected scenario.](../figures/figure_1_accuracy_by_scenario.png)
```

After Section 4.3 Verified Recovery:

```markdown
![Figure 2. Verified recovery rate by failure scenario.](../figures/figure_2_recovery_by_scenario.png)
```

After Section 4.4 Runtime Behavior:

```markdown
![Figure 3. Self-healing cycle runtime distribution.](../figures/figure_3_runtime_distribution.png)
```

After the classification discussion or as part of Section 4.2:

```markdown
![Figure 4. Root-cause classification confusion matrix.](../figures/figure_4_classification_confusion_matrix.png)
```

### Runtime Problem

The manuscript says runtime is measured but does not report:

- median runtime,
- mean runtime,
- min/max,
- p95,
- domain-level breakdown.

This is a weakness. Day 14 or Day 15 should compute runtime statistics from `combined_experiment_results.csv`.

---

## Discussion Review

### Current Strength

The Discussion section is conceptually strong.

### Current Weakness

It repeats Results too much. Discussion should interpret, not restate.

### v0.2 Cleanup Action

Reduce repeated statements about 100% detection and 52.17% recovery. Focus on implications:

- safety over automation,
- escalation as valid,
- auditability,
- conservative recovery metrics,
- enterprise reliability design.

### Recommended Discussion Structure for v0.2

1. Detection and diagnosis are necessary but insufficient.
2. Policy constraints prevent unsafe automation.
3. Escalation and rollback are valid reliability outcomes.
4. Verified recovery is a better metric than attempted remediation.
5. Enterprise systems need evidence-preserving remediation.

---

## Threats to Validity Review

### Current Strength

This section is honest and reviewer-friendly.

### Current Weakness

The baseline risk subsection may be too direct for final paper unless written carefully.

### v0.2 Cleanup Action

Keep baseline risk, but phrase it academically.

Current direction:

> If the final manuscript claims empirical comparison against alert-only or static-rule baselines, the preserved raw results must include comparable baseline trials.

Better final wording:

> Claims involving baseline comparison are limited to experiment domains represented in the preserved trial records. Broader comparison against alert-only or static-rule systems remains future work unless evaluated under identical scenarios and metrics.

This is safer.

---

## Conclusion Review

### Current Strength

Conclusion restates the main contribution clearly.

### Current Weakness

It repeats the experiment numbers again. That is acceptable, but keep it shorter.

### v0.2 Cleanup Action

Keep conclusion to 3 paragraphs:

1. What was proposed.
2. What was found.
3. What future work remains.

---

# Overclaiming Audit

## Overclaim Risk 1: 100% Detection and Classification

### Problem

100% accuracy can look suspicious.

### Required Qualifier

Always write:

> under the current controlled synthetic experiment configuration

Do not write:

> the framework detects all data-pipeline failures

## Overclaim Risk 2: Baseline Comparison

### Problem

The project objective mentions alert-only monitoring and static rule-based automation. But unless raw baseline trials exist, the manuscript cannot claim empirical superiority.

### Required Fix

In v0.2, revise baseline language to:

> The methodology is compatible with baseline comparison, but this manuscript reports only domains represented in the preserved experiment outputs.

## Overclaim Risk 3: Production Readiness

### Problem

The manuscript may sound close to production.

### Required Fix

Keep this boundary:

> The experiment demonstrates feasibility and reproducibility under controlled conditions, not production generalization.

## Overclaim Risk 4: Novelty

### Problem

Self-healing, policy-as-code, AIOps, and observability already exist.

### Required Fix

Claim:

> measurable integration of policy-constrained verified recovery for data pipelines

Do not claim:

> first self-healing data pipeline system

---

# Duplicate Cleanup Plan

## Duplicate A: Detection Is Not Recovery

Appears too often.

### v0.2 Placement

- Introduction: one sentence
- Methodology: formal definition
- Discussion: interpretation

Remove extra repetition in Results and Conclusion.

## Duplicate B: Experiment Counts

Appears in Abstract, Introduction, Methodology, Results, Conclusion.

### v0.2 Placement

- Abstract: one sentence
- Introduction: one sentence
- Results: full table
- Conclusion: one concise sentence

Do not repeat full counts in Methodology unless needed.

## Duplicate C: Failure Taxonomy

Appears in Introduction and Methodology.

### v0.2 Placement

- Introduction: examples only
- Methodology: full table
- Appendix: full list only if needed

## Duplicate D: Policy-Constrained Recovery

Appears everywhere.

### v0.2 Placement

- Introduction: motivation
- Methodology: strict definition
- Discussion: implications

## Duplicate E: References to Existing Tools

Related Work should carry the detailed comparison. Introduction should only summarize the gap.

---

# Figure Insertion Plan

## Required Figure Files

Expected figure paths:

```text
figures/figure_1_accuracy_by_scenario.png
figures/figure_2_recovery_by_scenario.png
figures/figure_3_runtime_distribution.png
figures/figure_4_classification_confusion_matrix.png
```

## Insert Locations

| Figure | Insert after | Purpose |
|---|---|---|
| Figure 1 | Section 4.2 | Detection and classification accuracy |
| Figure 4 | Section 4.2 | Classification confusion matrix |
| Figure 2 | Section 4.3 | Verified recovery by scenario |
| Figure 3 | Section 4.4 | Runtime distribution |

## Caption Style

Use this format:

```markdown
**Figure 1. Detection and root-cause classification accuracy by injected scenario.**
```

Then one explanatory sentence.

---

# Weak Sections Requiring Day 14–16 Work

## Weak Section 1: References

Current references are acceptable for v0.1 but weak for submission.

### Required Work

Add formal citations from:

- IEEE/ACM/Springer papers on autonomic computing
- AIOps systematic mapping
- data pipeline quality studies
- data observability or data quality research
- workflow reliability literature

## Weak Section 2: Runtime Results

Runtime is mentioned but not quantified.

### Required Work

Compute:

- mean runtime
- median runtime
- min runtime
- max runtime
- p95 runtime
- runtime by experiment domain

## Weak Section 3: Baseline Scope

Baseline language is risky.

### Required Work

Check raw results. If baseline domains exist, report them. If not, remove empirical baseline comparison language.

## Weak Section 4: Figure Integration

Figures exist but are not inserted in manuscript v0.1.

### Required Work

Insert markdown image links in v0.2.

## Weak Section 5: Methodology-to-Artifact Traceability

The paper says results are reproducible, but it should explicitly map metrics to files.

### Required Work

Add a table:

| Claim | Artifact |
|---|---|
| Trial count | combined_experiment_results.csv |
| Scenario recovery | scenario_summary.csv |
| Classification matrix | classification_confusion_matrix.csv |
| Figures | scripts/generate_figures.py and figures directory |

---

# Manuscript v0.2 Action Plan

## v0.2 Goal

Create a cleaner, more submission-like manuscript with:

- tightened abstract,
- reduced repetition,
- figure placeholders inserted,
- safer baseline language,
- methodology stage table,
- artifact traceability table,
- cleaner conclusion.

## v0.2 File

Create:

```text
docs/manuscript-v0.2.md
```

## v0.2 Required Edits

1. Replace abstract with tightened version.
2. Reduce Introduction architecture detail.
3. Replace Contribution 5 with stronger reproducibility language.
4. Add methodology stage table.
5. Add figure links in Results.
6. Add artifact traceability table.
7. Soften baseline comparison language.
8. Shorten Discussion.
9. Tighten Conclusion.
10. Keep Appendix C as internal only or remove from final paper.

---

# Recommended Day 14 Task

Day 14 should focus on **runtime statistics and artifact traceability**.

Why Day 14 should not immediately create v0.2:

The manuscript still lacks exact runtime statistics and artifact-to-claim traceability. Creating v0.2 before fixing those will produce another polished but incomplete draft.

Day 14 should compute or document:

- runtime summary statistics,
- metric-to-artifact mapping,
- whether baseline domains exist in raw results,
- exact figure paths and file sizes.

Then Day 15 should create `manuscript-v0.2.md`.

---

# Day 13 Completion Checklist

- [x] Manuscript v0.1 reviewed.
- [x] Abstract cleanup prepared.
- [x] Keyword cleanup prepared.
- [x] Introduction repetition identified.
- [x] Contribution wording improved.
- [x] Related Work weakness identified.
- [x] Methodology improvement table proposed.
- [x] Results figure-placement plan created.
- [x] Runtime-statistics gap identified.
- [x] Discussion cleanup plan created.
- [x] Threats to Validity refinement prepared.
- [x] Conclusion cleanup plan created.
- [x] Overclaiming audit completed.
- [x] Duplicate cleanup plan completed.
- [x] v0.2 action plan created.
- [x] Day 14 handoff defined.

---

# Day 14 Handoff

Day 14 should focus on **runtime statistics and artifact traceability**. The goal is to strengthen the evidence layer before producing `manuscript-v0.2.md`.

Day 14 outputs should include:

1. Runtime summary table.
2. Artifact-to-claim traceability table.
3. Baseline-domain check.
4. Figure path verification.
5. A short file called `docs/day-14-runtime-and-artifact-traceability.md`.

Only after Day 14 should `manuscript-v0.2.md` be created.
