# Day 10 — Methodology and Experimental Design Draft

Paper title: **Reliability-Aware Self-Healing Data Pipelines: Automated Failure Detection, Root-Cause Classification, and Policy-Constrained Recovery**

Date: 2026-06-15

## Day 10 Objective

Day 10 turns the implementation and experiment setup into a formal **Methodology and Experimental Design** section. This section must make the paper credible to reviewers by explaining what was evaluated, how trials were produced, what metrics were computed, how recovery success was defined, and what the experiment does **not** prove.

The methodology must stay aligned with the corrected Day 7 numbers:

| Item | Value |
|---|---:|
| Total trials | 780 |
| Injected failure trials | 690 |
| Healthy control trials | 60 |
| Boundary-control trials | 30 |
| Detection accuracy | 100% |
| Root-cause classification accuracy | 100% |
| Verified recovery rate across injected failures | 52.17% |

The most important methodological principle is that **verified recovery is not the same as attempted remediation**. Recovery is counted only when the action is policy-approved, executed, and validated after execution.

---

# 3. Methodology and Experimental Design — Manuscript Draft

## 3.1 Overview

This study evaluates a policy-constrained self-healing control plane for data-pipeline failures. The framework is designed to model self-healing as a sequence of measurable reliability stages rather than as a single automated repair action. Each trial passes through failure injection or control setup, telemetry collection, failure detection, root-cause classification, remediation selection, policy evaluation, remediation execution, post-recovery validation, and evidence preservation.

The experimental goal is to determine whether the proposed framework can detect injected data-pipeline failures, classify their likely root causes, and safely recover when remediation is available, policy-approved, executable, and verifiable. The experiment therefore separates detection performance, diagnostic performance, and recovery performance. This separation is necessary because a pipeline failure can be detected and classified correctly while still requiring escalation if automated recovery is unsafe or unverifiable.

The current evaluation uses a reproducible synthetic data-pipeline environment with controlled failure injection. The experiment includes injected failure trials, healthy-control trials, and boundary-control trials. Injected failure trials test the system under known failure conditions. Healthy controls test whether the system avoids reporting failures when no failure is present. Boundary controls test whether the system behaves conservatively near decision thresholds rather than over-triggering remediation.

## 3.2 System Architecture

The proposed system is organized as a reliability-control plane layered above a data-pipeline execution environment. The control plane contains the following stages:

1. **Pipeline execution layer.**  
   Executes synthetic data-pipeline workloads and produces observable outputs.

2. **Failure-injection layer.**  
   Introduces controlled data-pipeline failures such as schema drift, missing-value spikes, duplicate generation, freshness violations, unexpected volume changes, transformation failures, source-system failures, partial or corrupted outputs, and unknown failure conditions.

3. **Telemetry layer.**  
   Captures signals from pipeline execution, data outputs, and validation results. These signals are used by the detection and classification stages.

4. **Failure-detection layer.**  
   Determines whether a pipeline execution represents a failed state, a healthy state, or a boundary-control condition.

5. **Root-cause classification layer.**  
   Maps detected failures to the expected failure taxonomy used in the experiment.

6. **Remediation registry.**  
   Stores available remediation actions for known failure classes. The registry separates failures that have supported recovery procedures from failures that require escalation.

7. **Policy-evaluation layer.**  
   Determines whether a proposed remediation is allowed under safety and governance constraints. A remediation may be rejected even when the failure is correctly detected and classified.

8. **Recovery-execution layer.**  
   Executes the approved remediation action when one is available and policy-approved.

9. **Post-recovery validation layer.**  
   Checks whether the recovered pipeline state satisfies expected correctness and health conditions after remediation.

10. **Rollback, escalation, and evidence layer.**  
    Rolls back unsafe or failed remediation attempts, escalates unresolved cases, and preserves incident evidence for auditability and analysis.

This architecture intentionally prevents the system from treating all detected failures as candidates for automatic repair. A recovery action is considered successful only when it passes policy evaluation and post-recovery validation.

## 3.3 Failure Taxonomy

The experiment uses a predefined data-pipeline failure taxonomy. The taxonomy is based on common reliability problems in data pipelines where task-level success does not necessarily imply data correctness.

The evaluated failure categories are:

| Failure category | Description | Expected system behavior |
|---|---|---|
| Schema drift | Input schema differs from expected structure | Detect structural mismatch, classify schema drift, remediate only if policy permits |
| Missing-value spike | Null or missing values exceed expected threshold | Detect quality degradation, classify missing-value issue, validate recovered output |
| Duplicate-record generation | Duplicate records appear above expected tolerance | Detect duplicate spike, classify duplicate failure, remediate or escalate |
| Data-freshness violation | Data is stale or late relative to expected timing | Detect freshness issue, classify freshness violation, recover or escalate |
| Unexpected volume change | Row count or volume deviates from expected range | Detect abnormal volume, classify volume anomaly |
| Transformation-logic failure | Transformation produces invalid or inconsistent outputs | Detect downstream invalid state, classify transformation failure |
| Source-system failure | Upstream source is unavailable or returns invalid data | Detect source-related failure, classify source-system issue, escalate if unsafe |
| Partial or corrupted output | Output is incomplete or malformed | Detect output corruption, classify corruption or partial output |
| Unknown failure | Failure does not map cleanly to supported classes | Detect abnormal state where possible, avoid unsafe recovery, escalate |
| Healthy control | No failure is injected | Avoid false-positive detection |
| Boundary control | Near-threshold or ambiguous condition | Avoid aggressive remediation unless confidence and policy allow it |

The taxonomy supports deterministic evaluation because each injected trial has a known expected failure category. However, this also limits external validity. Real production failures may be overlapping, delayed, partially observable, or semantically ambiguous.

## 3.4 Trial Design

Each experiment trial represents one pipeline execution under a defined scenario. A scenario is defined by the experiment domain, injected failure type, severity or control condition, and expected outcome. The trial-level record preserves the injected condition, observed detection outcome, predicted root cause, recovery decision, policy decision, validation result, and runtime information.

The current experiment contains 780 total trials:

- 690 injected failure trials
- 60 healthy-control trials
- 30 boundary-control trials

Injected failure trials are used to evaluate detection, root-cause classification, and verified recovery. Healthy controls are used to evaluate whether the framework avoids false alarms when no failure is present. Boundary controls are used to evaluate whether the framework behaves conservatively under near-threshold or ambiguous conditions.

The trial design intentionally includes non-failure controls. Without healthy and boundary controls, the experiment would only test whether the system detects known failures; it would not test whether the system avoids unnecessary intervention.

## 3.5 Experimental Procedure

Each trial follows the same procedure:

1. **Initialize trial configuration.**  
   The trial is assigned an experiment domain, failure type or control condition, severity level, and expected outcome.

2. **Execute pipeline workload.**  
   A synthetic data-pipeline workload is executed using the trial configuration.

3. **Inject failure or control condition.**  
   For injected failure trials, a controlled fault is introduced. For healthy-control trials, no fault is injected. For boundary-control trials, the input is configured near a decision threshold.

4. **Collect telemetry and validation signals.**  
   The framework records execution state, data-quality signals, structural signals, volume/freshness indicators, and any derived validation outputs.

5. **Perform failure detection.**  
   The detection layer determines whether the trial represents a failure condition.

6. **Perform root-cause classification.**  
   If a failure is detected, the classifier assigns the expected root-cause category.

7. **Select candidate remediation.**  
   The system checks whether a remediation action exists for the classified failure type.

8. **Evaluate policy constraints.**  
   The policy layer approves or rejects the proposed remediation based on predefined safety and governance constraints.

9. **Execute remediation when allowed.**  
   If a remediation is available and approved, the recovery-execution layer performs the remediation.

10. **Validate recovered state.**  
    The system checks whether post-recovery output satisfies expected validation conditions.

11. **Record recovery outcome.**  
    A recovery is counted as verified only if the remediation was approved, executed, and validated.

12. **Preserve incident evidence.**  
    The trial record is preserved for downstream analysis, figure generation, and reproducibility.

## 3.6 Experimental Domains

The research objective is framed around comparing three operational strategies:

1. **Alert-only monitoring with operator-executed recovery**
2. **Static rule-based automated recovery**
3. **Policy-constrained self-healing recovery**

The current methodology supports this comparison by treating experiment domain as a trial-level attribute. However, the manuscript must only report domain-level comparisons that are actually present in the preserved raw results. If a baseline is not yet fully implemented or evaluated, it should be described as planned or future comparison rather than claimed as completed.

This is a potential reviewer risk. If the paper claims comparison against alert-only and static-rule baselines, the raw results must include comparable trials for those baselines. Otherwise, the paper should frame the current contribution as an evaluation of the policy-constrained control plane and reserve full baseline comparison for future work.

## 3.7 Metrics

The experiment reports separate metrics for detection, classification, recovery, and runtime. The metrics are separated because they answer different reliability questions.

### 3.7.1 Detection Accuracy

Detection accuracy measures whether the framework correctly identifies the presence or absence of a failure condition.

For injected failure trials, detection is successful when the system marks the trial as failed. For healthy-control trials, detection is successful when the system does not mark the trial as failed. For boundary controls, detection behavior is interpreted based on the expected boundary outcome defined by the trial configuration.

A generic detection accuracy definition is:

```text
Detection Accuracy = Correct Detection Decisions / Total Detection Decisions
```

The current experiment reports 100% detection accuracy under the synthetic experiment configuration.

### 3.7.2 Root-Cause Classification Accuracy

Root-cause classification accuracy measures whether the predicted root-cause category matches the injected failure category.

```text
Classification Accuracy = Correct Root-Cause Predictions / Classified Injected Failure Trials
```

The current experiment reports 100% root-cause classification accuracy under the evaluated failure taxonomy. This result should be interpreted as performance under controlled synthetic conditions, not as proof of generalization to all production incidents.

### 3.7.3 Verified Recovery Rate

Verified recovery rate measures the percentage of injected failure trials that are safely recovered.

```text
Verified Recovery Rate = Verified Recoveries / Injected Failure Trials
```

A trial is counted as a verified recovery only if all of the following are true:

1. The failure is detected.
2. The root cause is classified.
3. A remediation action is available.
4. The remediation is policy-approved.
5. The remediation executes successfully.
6. Post-recovery validation passes.

The current experiment reports a 52.17% verified recovery rate across injected failures. This lower recovery rate is expected because not every detected and classified failure should be automatically repaired. Some failures are safer to escalate than to remediate automatically.

### 3.7.4 Runtime

Runtime measures the operational cost of the self-healing cycle. Runtime is tracked separately from accuracy and recovery because a system can be accurate but operationally impractical if the detection-to-validation cycle is too slow.

Runtime is reported in milliseconds at the trial level and summarized by experiment domain.

### 3.7.5 Escalation and Non-Recovery Outcomes

The experiment should preserve non-recovery outcomes rather than discarding them. A trial that is detected and classified but not recovered is still informative. Non-recovery may occur because:

- no remediation exists in the registry,
- policy rejects the remediation,
- execution fails,
- post-recovery validation fails,
- rollback is triggered,
- the failure is unknown or unsafe,
- human escalation is required.

These cases should not be hidden because they are central to the argument that self-healing systems must be safety-constrained.

## 3.8 Recovery Success Definition

The paper uses a strict recovery success definition. Recovery is successful only when the system restores the pipeline to a validated healthy state after an approved remediation.

The following are **not** counted as successful recovery:

- detecting a failure without remediation,
- classifying a root cause without remediation,
- selecting a remediation that policy rejects,
- executing a remediation without post-recovery validation,
- executing a remediation that validation fails,
- escalating a failure to a human operator,
- rolling back an unsafe remediation,
- suppressing an alert or bypassing validation.

This definition prevents the experiment from overstating self-healing performance. It also makes the 52.17% verified recovery rate more credible than a larger but weaker automation-attempt rate.

## 3.9 Reproducibility Artifacts

The repository is organized to support reproducibility. The experiment artifacts include implementation code, experiment configurations, raw trial records, derived result summaries, policies, remediation registry artifacts, telemetry records, incident evidence, scripts, figures, and documentation.

The figure-generation workflow uses three primary derived inputs:

- `experiments/raw_results/combined_experiment_results.csv`
- `experiments/derived_results/scenario_summary.csv`
- `experiments/derived_results/classification_confusion_matrix.csv`

The generated publication figures include:

1. Detection and root-cause classification accuracy by scenario
2. Verified recovery outcomes by failure scenario
3. Self-healing cycle runtime distribution
4. Root-cause classification confusion matrix

The analysis should remain reproducible from preserved trial-level results. Final claims should be traceable to raw or derived experiment outputs.

## 3.10 Data Preservation and Research Integrity

The experiment design requires preserving unsuccessful trials. Failed recoveries, rejected remediations, rollbacks, escalations, and ambiguous cases should not be removed merely because they weaken the headline result.

This is important for research credibility. A self-healing paper that reports only successful remediations would overstate reliability and hide exactly the cases that matter most for safety. The current methodology therefore treats non-recovery outcomes as first-class results.

## 3.11 Assumptions and Scope

The current methodology depends on the following assumptions:

1. The synthetic failure taxonomy represents meaningful data-pipeline failure classes.
2. Injected failures produce observable signals that the detector can evaluate.
3. Expected root-cause labels are known for injected failure trials.
4. Recovery actions are available only for a subset of failure types.
5. Policy constraints may intentionally block remediation.
6. Post-recovery validation is required before recovery is counted as successful.
7. Synthetic experiments are useful for feasibility evaluation but do not prove production generalization.

The scope is intentionally limited. The current experiment does not prove that the framework will achieve the same detection, classification, or recovery performance on real enterprise incidents. It demonstrates feasibility and reproducibility under controlled conditions.

## 3.12 Methodological Limitations

The methodology has several limitations that should be disclosed clearly.

First, the evaluation uses synthetic failure injection. This improves control and reproducibility, but it may simplify real-world complexity. Production failures can be overlapping, intermittent, delayed, or caused by external systems not represented in the current taxonomy.

Second, the root-cause taxonomy is predefined. Classification accuracy is therefore measured against known categories. This does not prove performance on novel or ambiguous failures.

Third, the current experiment reports strong detection and classification performance. These results must not be generalized beyond the synthetic setup unless future work evaluates real incident data or more diverse failure conditions.

Fourth, verified recovery is constrained by available remediations and policies. A lower recovery rate does not necessarily mean detection or diagnosis failed. It may mean the system correctly avoided unsafe automation.

Fifth, if baseline comparisons are claimed, each baseline must be evaluated under the same failure scenarios and metrics. Otherwise, baseline comparison should be framed as future work.

## 3.13 Reviewer-Facing Methodology Summary

The methodology evaluates a staged self-healing control plane under controlled failure-injection conditions. Each trial has a known expected condition, produces telemetry and validation signals, and is evaluated for detection, classification, policy decisioning, recovery execution, and post-recovery validation. The experiment includes injected failures and controls to avoid evaluating only positive failure cases. Metrics are reported separately so that the paper does not confuse accurate detection with safe recovery.

The strict recovery definition is the most important methodological choice. Verified recovery requires policy approval, successful execution, and post-recovery validation. This makes the recovery metric conservative and defensible.

---

# Methodology Checklist for Final Paper

Before submitting the paper, verify that the methodology section includes:

- [x] System architecture stages
- [x] Failure taxonomy
- [x] Trial counts
- [x] Healthy-control definition
- [x] Boundary-control definition
- [x] Trial procedure
- [x] Detection metric
- [x] Classification metric
- [x] Verified recovery metric
- [x] Runtime metric
- [x] Recovery success definition
- [x] Non-recovery outcomes
- [x] Reproducibility artifacts
- [x] Assumptions
- [x] Methodological limitations
- [x] Baseline-comparison warning

---

# Strong Methodology Paragraph for Final Manuscript

The experiment evaluates policy-constrained self-healing as a staged control-plane lifecycle rather than as a single automated remediation step. Each trial begins with a configured pipeline execution, followed by controlled failure injection or a control condition, telemetry collection, failure detection, root-cause classification, remediation selection, policy evaluation, recovery execution, post-recovery validation, and evidence preservation. The evaluation includes 780 total trials, consisting of 690 injected failure trials, 60 healthy-control trials, and 30 boundary-control trials. Detection accuracy, root-cause classification accuracy, and verified recovery rate are reported as separate metrics because each measures a different stage of reliability. Recovery is counted as verified only when the remediation is policy-approved, executed successfully, and validated after execution.

---

# Claims the Methodology Supports

The methodology supports these claims:

1. The experiment is reproducible under controlled synthetic conditions.
2. The framework evaluates self-healing as a multi-stage reliability process.
3. The trial design includes failure and non-failure conditions.
4. Detection, classification, and recovery are measured separately.
5. Verified recovery is conservatively defined.
6. Non-recovery outcomes are meaningful, not discarded.

# Claims the Methodology Does Not Support Yet

The methodology does not yet support these claims:

1. The framework is production-proven.
2. The framework generalizes to every enterprise data-pipeline failure.
3. The framework outperforms commercial observability products.
4. The framework eliminates human operators.
5. The 100% detection/classification results will hold in real-world incidents.
6. Baseline systems were outperformed unless comparable baseline trials exist in the raw results.

---

# Day 10 Completion Checklist

- [x] Methodology section drafted.
- [x] System architecture described.
- [x] Failure taxonomy defined.
- [x] Trial design documented.
- [x] Experimental procedure written.
- [x] Metrics and formulas defined.
- [x] Recovery success definition clarified.
- [x] Reproducibility artifacts described.
- [x] Assumptions and limitations documented.
- [x] Baseline-comparison risk called out.
- [x] Day 11 handoff defined.

---

# Day 11 Handoff

Day 11 should focus on assembling the first complete paper draft structure. The goal is to combine the Introduction, Related Work, Methodology, Results, Discussion, Threats to Validity, and Conclusion into one coherent manuscript outline. Day 11 should also identify duplicate paragraphs across Day 7, Day 8, Day 9, and Day 10 so the final paper does not repeat itself.
