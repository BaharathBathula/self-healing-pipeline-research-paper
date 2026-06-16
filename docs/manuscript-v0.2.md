# Reliability-Aware Self-Healing Data Pipelines: Automated Failure Detection, Root-Cause Classification, and Policy-Constrained Recovery

## Abstract

Reliable data pipelines support analytics, machine learning, compliance reporting, and operational decision-making, but failures such as schema drift, data-quality degradation, freshness violations, transformation defects, and corrupted outputs often require more than task-level retries or alerting. Existing systems provide workflow orchestration, data-quality validation, observability, incident response, and policy enforcement, but these capabilities are commonly evaluated as separate functions rather than as an end-to-end recovery lifecycle. This paper presents a reliability-aware self-healing control plane for data pipelines that separates failure detection, root-cause classification, policy-constrained remediation, execution, post-recovery validation, rollback or escalation, and incident evidence preservation. A reproducible synthetic experiment with 780 trials evaluates the framework across injected failures, healthy controls, and boundary controls. Under the current controlled experiment configuration, the framework achieved 100% failure detection accuracy and 100% root-cause classification accuracy, while verified recovery was achieved in 52.17% of injected failure trials. The mean self-healing cycle runtime was 12.609 ms, with a median of 10.609 ms and p95 of 26.666 ms. The results show that self-healing data pipelines should be evaluated using separate metrics for detection, diagnosis, and verified recovery because accurate detection does not guarantee safe or validated remediation.

## Keywords

self-healing data pipelines; data reliability; data observability; root-cause classification; policy-constrained automation; failure injection; verified recovery

---

## 1. Introduction

Enterprise data platforms increasingly depend on pipelines that ingest, transform, validate, and deliver data across distributed systems. These pipelines support analytics, machine learning, regulatory reporting, customer-facing applications, and operational decision-making. As organizations increase the number of data sources, transformation layers, quality checks, and downstream consumers, pipeline reliability becomes harder to maintain through manual monitoring and incident response alone.

Data-pipeline failures can arise from schema drift, missing-value spikes, duplicate records, freshness violations, unexpected volume changes, transformation defects, source-system failures, corrupted outputs, and unknown failure modes. These failures may not always appear as simple task crashes. A pipeline can complete successfully while producing stale, incomplete, duplicated, or semantically invalid data. As a result, pipeline reliability requires more than workflow execution status. It requires detection, diagnosis, recovery decisioning, validation, and evidence preservation.

Existing data-engineering systems address important parts of this problem. Workflow orchestration tools schedule and execute pipeline tasks, data-quality frameworks validate assumptions about data, observability tools expose anomalies and operational signals, incident-management workflows coordinate response, and policy-as-code systems provide guardrails for automated decisions. However, these capabilities are often evaluated separately. Detection accuracy does not prove recovery safety. A successful retry does not prove that the underlying data issue was resolved. A remediation action does not prove that the recovered pipeline state is valid.

This paper presents a policy-constrained self-healing control plane for data-pipeline failures. The framework evaluates self-healing as a staged lifecycle from failure detection to policy-approved and post-validated recovery. This design separates observability, diagnosis, and recovery outcomes so that the system is not rewarded for unsafe or unverifiable automation.

The key design principle is that automated recovery must be constrained by policy and validation. In production data environments, unrestricted remediation may create more risk than the original failure. For example, automatically dropping columns, rewriting outputs, backfilling stale data, or suppressing failed quality checks may violate governance rules or corrupt downstream data products. Therefore, this framework counts recovery as successful only when the remediation is approved, executed, and verified. Failures that are detected and classified but cannot be safely repaired are escalated rather than counted as successful self-healing.

The experimental evaluation uses a reproducible synthetic data-pipeline environment with controlled failure injection. The current experiment includes 780 total trials: 690 injected failure trials, 60 healthy-control trials, and 30 boundary-control trials. Under the current synthetic experiment configuration, the framework achieved 100% failure detection accuracy and 100% root-cause classification accuracy. Verified recovery was achieved in 52.17% of injected failure trials. This separation between detection/classification performance and verified recovery performance is central to the paper's argument: self-healing data pipelines should be evaluated across multiple reliability stages, not only by whether a failure was detected or an automated action was attempted.

This paper makes the following contributions:

1. A staged self-healing control-plane architecture for data pipelines that separates failure detection, root-cause classification, remediation selection, policy approval, execution, validation, rollback, escalation, and evidence preservation.
2. A reproducible controlled failure-injection experiment with injected failure trials, healthy controls, and boundary controls.
3. A policy-constrained recovery model that prevents unsafe automation by requiring recovery actions to satisfy policy approval and post-recovery validation.
4. Separate reliability metrics for detection, diagnosis, and recovery, avoiding the misleading assumption that detection success implies recovery success.
5. A reproducibility package that preserves trial-level outputs, derived summaries, figure-generation scripts, and documentation for independent inspection and extension.

The remainder of this paper is organized as follows. Section 2 reviews related work in workflow orchestration, data-quality validation, observability, AIOps, autonomic computing, and policy-as-code. Section 3 describes the proposed self-healing control-plane architecture and experimental methodology. Section 4 presents experimental results across detection, classification, recovery, and runtime behavior. Section 5 discusses implications of the results. Section 6 describes threats to validity. Section 7 concludes with future research directions for policy-constrained self-healing data pipelines.

---

## 2. Related Work

Modern data platforms rely on a combination of workflow orchestration, data-quality validation, monitoring, incident management, and governance controls. Each area contributes to pipeline reliability, but existing approaches often treat detection, diagnosis, remediation, and validation as separate operational concerns. This paper builds on these areas while focusing on a narrower problem: how to evaluate policy-constrained self-healing for data-pipeline failures.

### 2.1 Workflow Orchestration

Workflow orchestration systems such as Apache Airflow provide an execution model for defining, scheduling, monitoring, and debugging batch-oriented workflows. Orchestration systems represent workflows as directed acyclic graphs, support task dependencies, scheduling, retry logic, operational metadata, and interfaces for monitoring and troubleshooting. This makes workflow orchestration a central component of modern data engineering systems.

However, orchestration is not equivalent to self-healing. A workflow engine can rerun a failed task, execute a callback, or expose logs, but it does not automatically determine whether a failure is caused by schema drift, missing-value spikes, freshness violations, duplicate generation, source-system outages, or transformation defects. It also does not inherently decide whether a remediation is safe under governance policy or whether the pipeline has been validated after repair. Therefore, orchestration platforms provide the execution substrate, while this paper focuses on the reliability-control layer above orchestration.

### 2.2 Data-Quality Validation and Data Testing

Data-quality frameworks and platform-native rule systems improve pipeline reliability by formalizing expectations about data. Tools such as Great Expectations define expectations that specify the state to which data should conform and validate batches against those expectations. dbt data tests express assertions about models and sources, returning failing records when assumptions are violated. Platform-native data-quality systems can support rule-based validation, monitoring, alerting, and quality scores. Table formats and storage systems may also enforce integrity constraints at write time.

These approaches are highly relevant because they provide structured ways to detect invalid data states. However, validation and constraint enforcement primarily answer whether data satisfies specified rules. They do not by themselves determine the root cause of a failure, select a policy-approved remediation, execute that remediation, verify post-recovery health, and preserve incident evidence. Data-quality validation is a necessary signal source for self-healing, but it is not a complete self-healing control plane.

### 2.3 Data Observability and Monitoring

Monitoring and observability systems collect signals about system state and pipeline behavior. In data systems, relevant observability signals include freshness, volume, schema stability, distribution drift, null-rate changes, duplicate rates, failed transformations, and downstream validation results. These signals help operators determine what is broken and why a pipeline may no longer be trustworthy.

The limitation is that observability commonly improves visibility and alerting but does not guarantee controlled recovery. A data observability system may identify that a table is stale or that a schema changed unexpectedly, but recovery still often depends on human operators, manually encoded runbooks, or ad hoc retries. This paper treats observability as the detection layer of a broader self-healing lifecycle rather than as the full solution.

### 2.4 AIOps and Root-Cause Analysis

AIOps research addresses anomaly detection, event correlation, root-cause analysis, incident management, and automated operations in complex IT systems. Prior work shows strong interest in failure-related tasks such as anomaly detection and root-cause analysis. Other work has explored extracting root-cause knowledge from incident investigations and converting historical incident evidence into reusable knowledge for future incidents.

This literature is important because it motivates automated diagnosis under operational complexity. However, much AIOps research focuses on infrastructure, services, logs, microservices, or cloud operations rather than data-pipeline-specific failure modes. Even when AIOps approaches support root-cause analysis, they do not necessarily implement policy-constrained remediation for data pipelines or evaluate recovery success using post-recovery validation. This paper contributes to the data-engineering reliability setting by connecting root-cause classification to governed remediation outcomes.

### 2.5 Autonomic Computing and Self-Healing Systems

Autonomic computing introduced the vision of systems that manage themselves through self-configuration, self-healing, self-optimization, and self-protection. This vision is directly relevant to data-pipeline reliability because pipeline failures increasingly exceed the capacity of manual operators to inspect, diagnose, and repair at scale. The autonomic-computing framing also emphasizes policies and high-level goals, which aligns with the need for governed recovery rather than unrestricted automation.

The gap is that autonomic computing is a broad systems paradigm. It does not specify a reproducible evaluation framework for data-pipeline failure detection, root-cause classification, policy approval, remediation execution, and post-recovery validation. This paper operationalizes the self-healing concept for data pipelines and evaluates each stage separately.

### 2.6 Policy-as-Code and Governance

Policy-as-code systems such as Open Policy Agent decouple policy decision-making from policy enforcement. This design is relevant to self-healing pipelines because automated remediation must not be allowed to perform unsafe changes simply because a failure was detected.

However, policy engines are decision components, not complete self-healing systems. They can approve, deny, or structure decisions, but they do not generate telemetry, diagnose pipeline failures, execute repairs, validate recovered state, or preserve incident evidence. This paper uses the policy-as-code idea as part of a larger reliability-control architecture.

### 2.7 Research Gap

Existing literature and systems provide strong building blocks for pipeline reliability: workflow orchestration executes tasks, data-quality frameworks validate expectations, observability platforms detect anomalies, AIOps methods support diagnosis, autonomic computing motivates self-management, and policy-as-code provides decision guardrails. The unresolved gap is the lack of an end-to-end, reproducible evaluation framework for data pipelines that measures the full lifecycle from injected failure to detection, classification, policy-constrained remediation, validation, rollback or escalation, and incident evidence.

This gap matters because real enterprise data pipelines cannot be safely repaired by unrestricted automation. A failure may be detected correctly and classified accurately while still requiring human escalation because the remediation is unsafe, unavailable, unverifiable, or governance-sensitive. Therefore, a credible self-healing system must distinguish between detection success, classification success, attempted remediation, policy-approved remediation, executed remediation, and verified recovery.

---

## 3. Methodology and Experimental Design

### 3.1 Overview

This study evaluates a policy-constrained self-healing control plane for data-pipeline failures. The framework is designed to model self-healing as a sequence of measurable reliability stages rather than as a single automated repair action. Each trial passes through failure injection or control setup, telemetry collection, failure detection, root-cause classification, remediation selection, policy evaluation, remediation execution, post-recovery validation, and evidence preservation.

The experimental goal is to determine whether the proposed framework can detect injected data-pipeline failures, classify their likely root causes, and safely recover when remediation is available, policy-approved, executable, and verifiable. The experiment therefore separates detection performance, diagnostic performance, and recovery performance. This separation is necessary because a pipeline failure can be detected and classified correctly while still requiring escalation if automated recovery is unsafe or unverifiable.

The current evaluation uses a reproducible synthetic data-pipeline environment with controlled failure injection. The experiment includes injected failure trials, healthy-control trials, and boundary-control trials. Injected failure trials test the system under known failure conditions. Healthy controls test whether the system avoids reporting failures when no failure is present. Boundary controls test whether the system behaves conservatively near decision thresholds rather than over-triggering remediation.

### 3.2 System Architecture

The proposed system is organized as a reliability-control plane layered above a data-pipeline execution environment. The control plane contains the following stages.

| Stage | Input | Output | Metric or evidence |
|---|---|---|---|
| Pipeline execution | Synthetic workload configuration | Pipeline output and execution state | Trial record |
| Failure injection | Scenario and severity configuration | Injected failure or control condition | Trial metadata |
| Telemetry collection | Pipeline outputs and execution state | Data-quality, structural, freshness, and runtime signals | Raw result fields |
| Failure detection | Telemetry signals | Failure or non-failure decision | Detection accuracy |
| Root-cause classification | Detected failure | Predicted root-cause label | Classification accuracy |
| Remediation selection | Predicted root cause | Candidate remediation action | Remediation action field |
| Policy evaluation | Candidate remediation | Approved, rejected, or human-approval-required decision | Policy/recovery status fields |
| Recovery execution | Approved remediation | Execution result | Remediation executed field |
| Post-recovery validation | Recovered pipeline output | Validated or non-validated recovery outcome | Recovery verified field |
| Rollback, escalation, and evidence | Trial outcome | Incident record and preserved evidence | Raw and derived artifacts |

This architecture intentionally prevents the system from treating all detected failures as candidates for automatic repair. A recovery action is considered successful only when it passes policy evaluation and post-recovery validation.

### 3.3 Failure Taxonomy

The experiment uses a predefined data-pipeline failure taxonomy. The taxonomy is based on common reliability problems in data pipelines where task-level success does not necessarily imply data correctness.

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

### 3.4 Trial Design

Each experiment trial represents one pipeline execution under a defined scenario. A scenario is defined by the experiment domain, injected failure type, severity or control condition, and expected outcome. The trial-level record preserves the injected condition, observed detection outcome, predicted root cause, recovery decision, policy decision, validation result, and runtime information.

The current experiment contains 780 total trials.

| Trial type | Count |
|---|---:|
| Injected failure trials | 690 |
| Healthy-control trials | 60 |
| Boundary-control trials | 30 |
| Total trials | 780 |

Injected failure trials are used to evaluate detection, root-cause classification, and verified recovery. Healthy controls are used to evaluate whether the framework avoids false alarms when no failure is present. Boundary controls are used to evaluate whether the framework behaves conservatively under near-threshold or ambiguous conditions.

The experiment domains represented in the preserved trial records are `artifact` and `dataframe`. These domains represent evaluated implementation contexts, not alert-only or static-rule baseline comparisons. Although the broader research objective supports comparison with alert-only and static-rule approaches, the current manuscript reports only experiment domains represented in the preserved trial records. Full baseline comparison remains future work unless comparable baseline trials are added under identical failure scenarios and metrics.

### 3.5 Experimental Procedure

Each trial follows a consistent procedure. The trial is first assigned an experiment domain, failure type or control condition, severity level, and expected outcome. A synthetic data-pipeline workload is then executed using the trial configuration. For injected failure trials, a controlled fault is introduced. For healthy-control trials, no fault is injected. For boundary-control trials, the input is configured near a decision threshold.

The framework records execution state, data-quality signals, structural signals, volume and freshness indicators, and derived validation outputs. The detection layer determines whether the trial represents a failure condition. If a failure is detected, the classifier assigns the expected root-cause category. The system then checks whether a remediation action exists for the classified failure type. If a candidate remediation exists, the policy layer approves or rejects the proposed action based on predefined safety and governance constraints.

If the remediation is available and policy-approved, the recovery-execution layer performs the remediation. The system then validates whether the post-recovery output satisfies expected correctness and health conditions. A recovery is counted as verified only if the remediation was approved, executed, and validated. The trial record is preserved for downstream analysis, figure generation, and reproducibility.

### 3.6 Metrics

The experiment reports separate metrics for detection, classification, recovery, and runtime. The metrics are separated because they answer different reliability questions.

**Detection accuracy** measures whether the framework correctly identifies the presence or absence of a failure condition.

```text
Detection Accuracy = Correct Detection Decisions / Total Detection Decisions
```

For injected failure trials, detection is successful when the system marks the trial as failed. For healthy-control trials, detection is successful when the system does not mark the trial as failed. For boundary controls, detection behavior is interpreted based on the expected boundary outcome defined by the trial configuration.

**Root-cause classification accuracy** measures whether the predicted root-cause category matches the injected failure category.

```text
Classification Accuracy = Correct Root-Cause Predictions / Classified Injected Failure Trials
```

**Verified recovery rate** measures the percentage of injected failure trials that are safely recovered.

```text
Verified Recovery Rate = Verified Recoveries / Injected Failure Trials
```

A trial is counted as a verified recovery only if all of the following are true: the failure is detected, the root cause is classified, a remediation action is available, the remediation is policy-approved, the remediation executes successfully, and post-recovery validation passes.

**Runtime** measures the operational cost of the self-healing cycle. Runtime is tracked separately from accuracy and recovery because a system can be accurate but operationally impractical if the detection-to-validation cycle is too slow.

### 3.7 Recovery Success Definition

The paper uses a strict recovery success definition. Recovery is successful only when the system restores the pipeline to a validated healthy state after an approved remediation.

The following are not counted as successful recovery: detecting a failure without remediation, classifying a root cause without remediation, selecting a remediation that policy rejects, executing a remediation without post-recovery validation, executing a remediation that validation fails, escalating a failure to a human operator, rolling back an unsafe remediation, or suppressing an alert or bypassing validation.

This definition prevents the experiment from overstating self-healing performance. It also makes the verified recovery rate more credible than a larger but weaker automation-attempt rate.

### 3.8 Reproducibility Artifacts

The repository is organized to support reproducibility. The experiment artifacts include implementation code, experiment configurations, raw trial records, derived result summaries, policies, remediation registry artifacts, telemetry records, incident evidence, scripts, figures, and documentation.

The figure-generation workflow uses three primary derived inputs: combined raw experiment results, scenario-level summaries, and a classification confusion matrix. The generated publication figures include detection and root-cause classification accuracy by scenario, verified recovery outcomes by failure scenario, self-healing cycle runtime distribution, and root-cause classification confusion matrix.

The analysis is intended to remain reproducible from preserved trial-level results. Final claims should be traceable to raw or derived experiment outputs.

### 3.9 Assumptions and Scope

The current methodology depends on several assumptions. The synthetic failure taxonomy is assumed to represent meaningful data-pipeline failure classes. Injected failures are assumed to produce observable signals that the detector can evaluate. Expected root-cause labels are known for injected failure trials. Recovery actions are available only for a subset of failure types. Policy constraints may intentionally block remediation. Post-recovery validation is required before recovery is counted as successful.

The scope is intentionally limited. The current experiment does not prove that the framework will achieve the same detection, classification, or recovery performance on real enterprise incidents. It demonstrates feasibility and reproducibility under controlled synthetic conditions.

---

## 4. Results

### 4.1 Experiment Summary

The experimental evaluation produced 780 total trial records spanning injected failures, healthy controls, and boundary-control scenarios. Of these, 690 trials corresponded to injected data-pipeline failure conditions, 60 trials represented healthy-control executions, and 30 trials represented boundary-control conditions. The experiment design therefore evaluates both positive failure cases and non-failure controls rather than measuring the detector only on failure-positive examples.

| Metric | Value |
|---|---:|
| Total trials | 780 |
| Injected failure trials | 690 |
| Healthy control trials | 60 |
| Boundary-control trials | 30 |
| Failure detection accuracy | 100% |
| Root-cause classification accuracy | 100% |
| Verified recovery rate across injected failures | 52.17% |

These numbers should be interpreted conservatively. Detection and classification performance can be described as perfect within the current synthetic experiment configuration. Recovery performance must not be described as perfect. The key finding is that the framework reliably detects and classifies injected failures under the evaluated conditions, while recovery success depends on whether the remediation is policy-approved, executable, and verifiable.

### 4.2 Detection and Root-Cause Classification

Across the evaluated trial set, the self-healing control plane achieved 100% failure detection accuracy and 100% root-cause classification accuracy under the current synthetic failure model. This result indicates that the implemented detector and classifier were able to consistently identify the presence of injected failures and assign the expected failure category when the failure type was represented in the experiment configuration.

This result should be interpreted as evidence of internal consistency and technical feasibility, not as evidence that the model will generalize without degradation to arbitrary enterprise production environments. The failures are synthetic, the taxonomy is predefined, and the classifier is evaluated against known categories.

![Figure 1. Detection and root-cause classification accuracy by injected scenario.](../figures/figure_1_accuracy_by_scenario.png)

**Figure 1. Detection and root-cause classification accuracy by injected scenario.** The figure compares detection accuracy and classification accuracy across the evaluated scenario taxonomy.

![Figure 4. Root-cause classification confusion matrix.](../figures/figure_4_classification_confusion_matrix.png)

**Figure 4. Root-cause classification confusion matrix.** The figure compares injected root-cause labels against predicted root-cause labels.

### 4.3 Verified Recovery

Verified recovery was achieved in 52.17% of injected failure trials. This result is intentionally lower than detection and classification accuracy because recovery is subject to additional constraints. A failure may be detected and correctly classified while still not being automatically remediated if the policy layer rejects the action, the remediation registry does not contain a safe recovery procedure, the recovery action cannot be verified, or the failure requires human escalation.

For a reliability-oriented system, this distinction is important: unsafe automation is not counted as success merely because the system attempted a repair. Recovery is counted as successful only when the remediation is approved, executed, and validated.

![Figure 2. Verified recovery rate by failure scenario.](../figures/figure_2_recovery_by_scenario.png)

**Figure 2. Verified recovery rate by failure scenario.** The figure reports the proportion of injected failure trials that resulted in verified recovery.

### 4.4 Runtime Behavior

Runtime was recorded at the trial level using the `runtime_milliseconds` field. Across 780 runtime records, the mean self-healing cycle runtime was 12.609 ms, the median runtime was 10.609 ms, the minimum runtime was 5.476 ms, the maximum runtime was 33.879 ms, and the p95 runtime was 26.666 ms.

| Runtime metric | Value |
|---|---:|
| Runtime record count | 780 |
| Mean runtime milliseconds | 12.609 |
| Median runtime milliseconds | 10.609 |
| Minimum runtime milliseconds | 5.476 |
| Maximum runtime milliseconds | 33.879 |
| p95 runtime milliseconds | 26.666 |

Runtime varied by experiment domain. The `artifact` domain contained 120 trials with a mean runtime of 8.043 ms, median runtime of 8.289 ms, and p95 runtime of 9.230 ms. The `dataframe` domain contained 660 trials with a mean runtime of 13.439 ms, median runtime of 11.298 ms, and p95 runtime of 27.022 ms.

| Experiment domain | Trial count | Mean ms | Median ms | p95 ms |
|---|---:|---:|---:|---:|
| artifact | 120 | 8.043 | 8.289 | 9.230 |
| dataframe | 660 | 13.439 | 11.298 | 27.022 |

Runtime should not be used as a primary success metric in isolation. Instead, it should be interpreted alongside detection, classification, recovery, policy, and validation outcomes.

![Figure 3. Self-healing cycle runtime distribution.](../figures/figure_3_runtime_distribution.png)

**Figure 3. Self-healing cycle runtime distribution.** The figure summarizes runtime behavior across experiment domains.

### 4.5 Artifact Availability

The runtime and figure-generation evidence layer was verified through the Day 14 artifact traceability check. The raw combined results, scenario summary, classification confusion matrix, and all expected PNG/PDF figures were present locally during verification.

| Artifact | Path | Status |
|---|---|---|
| Raw combined results | `experiments/raw_results/combined_experiment_results.csv` | Found |
| Scenario summary | `experiments/derived_results/scenario_summary.csv` | Found |
| Classification confusion matrix | `experiments/derived_results/classification_confusion_matrix.csv` | Found |
| Figure 1 PNG | `figures/figure_1_accuracy_by_scenario.png` | Found |
| Figure 2 PNG | `figures/figure_2_recovery_by_scenario.png` | Found |
| Figure 3 PNG | `figures/figure_3_runtime_distribution.png` | Found |
| Figure 4 PNG | `figures/figure_4_classification_confusion_matrix.png` | Found |

---

## 5. Discussion

### 5.1 Detection and Diagnosis Are Necessary but Insufficient

The experimental results support the view that policy-constrained self-healing should be understood as a staged reliability-control process. Detection, diagnosis, remediation selection, execution, validation, rollback, and escalation are distinct responsibilities. Treating these stages separately avoids the common mistake of evaluating self-healing systems only by whether an automated action was attempted.

The 100% detection and classification results demonstrate that the current implementation can reliably recognize the injected failure scenarios used in the experiment. However, these results should not be overstated. The appropriate interpretation is that the framework is technically coherent and reproducible under controlled synthetic conditions.

### 5.2 Policy Constraints Are a Reliability Feature

The lower verified recovery rate is not a weakness by itself. It reflects the system design choice to enforce policy approval and post-recovery validation. In enterprise data pipelines, an automated remediation that corrupts downstream data, violates governance rules, or masks a serious source-system problem is worse than a controlled escalation.

Therefore, the framework counts only verified recovery as successful recovery. Attempts that are rejected, escalated, rolled back, or unverifiable are treated separately from successful self-healing. This makes the recovery metric more conservative and more useful than a metric that counts every automated remediation attempt as success.

### 5.3 Escalation Is a Valid Safety Outcome

A mature self-healing system should not attempt to repair every detected failure. Some failures are ambiguous, governance-sensitive, unsupported by the remediation registry, or unsafe to repair automatically. In those cases, escalation is a valid reliability outcome. The system preserves evidence and avoids unsafe action rather than forcing automation.

This distinction is especially important for regulated or high-dependence data environments. Data platforms used for insurance, finance, healthcare, compliance reporting, or operational analytics often require traceability and defensible control points. In such environments, self-healing cannot be judged purely by speed or automation rate. It must also preserve evidence, enforce guardrails, and make failure-handling decisions auditable.

### 5.4 Runtime Interpretation

The runtime results show that the evaluated self-healing cycle executed within millisecond-scale runtimes in the current synthetic environment. However, these results should be interpreted cautiously. The experiment does not prove that equivalent runtimes would hold for large production datasets, distributed infrastructure, external systems, or human-approval workflows. Runtime evidence is useful for feasibility, but production latency must be evaluated separately under realistic operational conditions.

### 5.5 Design Implications

The results support a narrower but stronger contribution: a reproducible experimental framework for evaluating data-pipeline self-healing as a policy-constrained control plane. The contribution is not that every pipeline failure can be repaired automatically. The contribution is that failure detection, root-cause classification, safe remediation selection, validation, and escalation can be represented as measurable stages with separate outcomes.

Future self-healing data systems should separate detection, diagnosis, and recovery metrics; preserve failed recovery attempts; enforce policy constraints; validate recovered state; and maintain incident evidence. These design principles make self-healing safer and more auditable than unrestricted remediation automation.

---

## 6. Threats to Validity

### 6.1 Internal Validity

The experiment uses controlled failure injection. This improves reproducibility but may simplify the relationship between injected failures and observable telemetry. A detector may perform better in this environment than in a production system where failures are noisy, overlapping, delayed, or partially observable.

### 6.2 Construct Validity

The metrics separate detection accuracy, root-cause classification accuracy, and verified recovery rate. This is appropriate for the paper's research objective, but these metrics do not capture every operational concern. For example, they do not fully measure operator trust, downstream business impact, long-term model drift, or the cost of false escalation.

### 6.3 External Validity

The results should be generalized carefully. The experiment currently evaluates a predefined taxonomy of failure conditions. Real-world data platforms may include infrastructure failures, vendor API instability, semantic data-quality defects, access-control issues, cross-system contract changes, and cascading downstream failures that are not fully represented in the current test set.

### 6.4 Runtime Validity

Runtime results were measured in the current synthetic experiment environment. These runtime measurements provide evidence about the local experimental setup, but they do not establish production latency under distributed workloads, large-scale datasets, external storage systems, network calls, or manual approval steps. Runtime claims should therefore remain limited to the preserved experimental records.

### 6.5 Conclusion Validity

The experiment provides evidence that the framework works under the current controlled setup. It does not prove superiority over mature observability products or enterprise incident-management workflows. Future experiments should compare the policy-constrained framework against alert-only monitoring and static rule-based automation using identical failure scenarios and operational metrics.

### 6.6 Baseline Comparison Scope

Claims involving baseline comparison are limited to experiment domains represented in the preserved trial records. The current preserved domains are `artifact` and `dataframe`; they do not constitute alert-only or static-rule baseline domains. Broader comparison against alert-only or static-rule systems remains future work unless evaluated under identical scenarios and metrics.

---

## 7. Conclusion and Future Work

This paper presented a reliability-aware self-healing control plane for data pipelines. The framework models self-healing as a staged process involving failure detection, root-cause classification, policy-constrained remediation, execution, post-recovery validation, rollback or escalation, and evidence preservation. The experimental evaluation used a reproducible synthetic failure-injection setup with 780 total trials, including injected failures, healthy controls, and boundary controls.

Under the current controlled experiment configuration, the framework achieved 100% failure detection accuracy and 100% root-cause classification accuracy, while verified recovery was achieved in 52.17% of injected failure trials. Runtime was measured across 780 records, with a mean of 12.609 ms, median of 10.609 ms, and p95 of 26.666 ms. These results support feasibility under controlled conditions, while also showing that detection and diagnosis should not be treated as equivalent to verified recovery.

The results support the view that self-healing data pipelines should be evaluated as governed reliability-control systems rather than unrestricted automation scripts. Future work should evaluate the framework on real production incidents, expand the failure taxonomy, compare against alert-only and static-rule baselines under identical scenarios, incorporate probabilistic or learning-based root-cause models, and study the operational tradeoffs between automation, escalation, safety, and recovery latency.

---

## References

[1] Apache Airflow Documentation. “What is Airflow?” Apache Software Foundation.

[2] Great Expectations Documentation. “Try GX Core.” Great Expectations.

[3] dbt Documentation. “Add data tests to your DAG.” dbt Labs.

[4] Google Cloud Documentation. “Auto data quality overview.” Google Cloud Knowledge Catalog.

[5] Delta Lake Documentation. “Constraints.” Delta Lake.

[6] Google Site Reliability Engineering Book. “Monitoring Distributed Systems.” Google.

[7] Open Policy Agent Documentation. “Open Policy Agent.”

[8] Notaro, P., Cardoso, J., and Gerndt, M. “A Systematic Mapping Study in AIOps.” arXiv:2012.09108, 2020.

[9] Saha, A., and Hoi, S. C. H. “Mining Root Cause Knowledge from Cloud Service Incident Investigations for AIOps.” arXiv:2204.11598, 2022.

[10] Foidl, H., Golendukhina, V., Ramler, R., and Felderer, M. “Data Pipeline Quality: Influencing Factors, Root Causes of Data-related Issues, and Processing Problem Areas for Developers.” arXiv:2309.07067, 2023.

[11] Kephart, J. O., and Chess, D. M. “The Vision of Autonomic Computing.” IEEE Computer, 2003.

---

## Appendix A: Failure Taxonomy

The experiment uses the following failure and control categories: schema drift, missing-value spike, duplicate-record generation, data-freshness violation, unexpected volume change, transformation-logic failure, source-system failure, partial or corrupted output, unknown failure, healthy control, and boundary control.

---

## Appendix B: Claim-to-Artifact Traceability

| Claim area | Artifact | Status |
|---|---|---|
| Total trial count | `experiments/raw_results/combined_experiment_results.csv` | Verified locally |
| Runtime distribution | `experiments/raw_results/combined_experiment_results.csv` / `runtime_milliseconds` | Verified locally |
| Scenario-level detection and recovery | `experiments/derived_results/scenario_summary.csv` | Verified locally |
| Classification matrix | `experiments/derived_results/classification_confusion_matrix.csv` | Verified locally |
| Figure generation | `scripts/generate_figures.py` | Present |
| Publication figures | `figures/figure_*` | Verified locally |

---

## Appendix C: Reproducibility Notes

The preserved trial records include the following columns:

```text
experiment_domain, trial_id, repetition, random_seed, injected_failure_type,
injected_severity, expected_root_cause, failure_detected,
detected_failure_category, detection_correct, predicted_root_cause,
classification_correct, classification_confidence, remediation_action,
remediation_executed, human_approval_required, cycle_status,
recovery_verified, input_record_count, output_record_count,
quarantined_record_count, runtime_milliseconds, original_size_bytes,
observed_size_bytes, regenerated_size_bytes, checksum_restored
```

These fields support traceability from trial-level configuration to detection, classification, remediation, recovery, and runtime outcomes.
