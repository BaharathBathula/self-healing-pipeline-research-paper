# Day 8 — Related Work and Research Gap Draft

Paper title: **Reliability-Aware Self-Healing Data Pipelines: Automated Failure Detection, Root-Cause Classification, and Policy-Constrained Recovery**

Date: 2026-06-15

## Day 8 Objective

Day 8 positions the paper against existing work in data observability, data-quality validation, workflow orchestration, AIOps, autonomic computing, and policy-as-code. The purpose is to show that this work is not merely another monitoring tool or orchestration wrapper. The defensible research gap is the lack of a reproducible, policy-constrained, experimentally evaluated control plane that connects failure detection, root-cause classification, remediation decisioning, execution, post-recovery validation, rollback/escalation, and incident evidence for data pipelines.

## Core Positioning

Existing systems solve important parts of the data-reliability problem, but they usually stop at one of the following boundaries:

1. They detect or validate data-quality failures but do not provide controlled recovery.
2. They orchestrate workflow retries but do not reason deeply about data-specific root causes.
3. They support incident analysis but do not execute policy-constrained pipeline remediation.
4. They enforce policies but do not evaluate end-to-end self-healing outcomes.
5. They discuss self-healing/autonomic computing broadly but are not specialized to measurable data-pipeline failure recovery.

This paper addresses the intersection of these areas by evaluating self-healing data pipelines as a staged reliability-control process.

## Related Work — Manuscript Draft

### 2. Related Work

Modern data platforms rely on a combination of workflow orchestration, data-quality validation, monitoring, incident management, and governance controls. Each area contributes to pipeline reliability, but existing approaches often treat detection, diagnosis, remediation, and validation as separate operational concerns. This paper builds on these areas while focusing on a narrower problem: how to evaluate policy-constrained self-healing for data-pipeline failures.

#### 2.1 Workflow Orchestration

Workflow orchestration systems such as Apache Airflow provide an execution model for defining, scheduling, monitoring, and debugging batch-oriented workflows. Airflow represents workflows as DAGs, supports task dependencies, scheduling, retry logic, operational metadata, and a web interface for monitoring and troubleshooting. This makes workflow orchestration a central component of modern data engineering systems.

However, orchestration is not equivalent to self-healing. A workflow engine can rerun a failed task, execute a callback, or expose logs, but it does not automatically determine whether a failure is caused by schema drift, missing-value spikes, freshness violations, duplicate generation, source-system outages, or transformation defects. It also does not inherently decide whether a remediation is safe under governance policy or whether the pipeline has been validated after repair. Therefore, orchestration platforms provide the execution substrate, while this paper focuses on the reliability-control layer above orchestration.

#### 2.2 Data-Quality Validation and Data Testing

Data-quality frameworks and platform-native rule systems improve pipeline reliability by formalizing expectations about data. Great Expectations defines Expectations that specify the state to which data should conform and validates batches against those expectations. dbt data tests similarly express assertions about models and sources, returning failing records when assumptions are violated. Google Cloud Knowledge Catalog auto data quality supports rule-based validation, monitoring, alerting, and quality scores for supported table types. Delta Lake constraints enforce integrity rules such as `NOT NULL` and `CHECK` constraints at write time.

These approaches are highly relevant because they provide structured ways to detect invalid data states. However, validation and constraint enforcement primarily answer whether data satisfies specified rules. They do not by themselves determine the root cause of a failure, select a policy-approved remediation, execute that remediation, verify post-recovery health, and preserve incident evidence. In other words, data-quality validation is a necessary signal source for self-healing, but it is not a complete self-healing control plane.

#### 2.3 Data Observability and Monitoring

Monitoring and observability systems collect signals about system state and pipeline behavior. Site Reliability Engineering literature distinguishes between symptoms and causes, emphasizing that monitoring should answer both what is broken and why. It also highlights latency, traffic, errors, and saturation as core service-monitoring signals. In data systems, analogous observability signals include freshness, volume, schema stability, distribution drift, null-rate changes, duplicate rates, and failed transformations.

The limitation is that observability commonly improves visibility and alerting but does not guarantee controlled recovery. A data observability system may identify that a table is stale or that a schema changed unexpectedly, but recovery still often depends on human operators, manually encoded runbooks, or ad hoc retries. This paper treats observability as the detection layer of a broader self-healing lifecycle rather than as the full solution.

#### 2.4 AIOps and Root-Cause Analysis

AIOps research addresses anomaly detection, event correlation, root-cause analysis, incident management, and automated operations in complex IT systems. Prior work shows strong interest in failure-related tasks such as anomaly detection and root-cause analysis. Other work has explored extracting root-cause knowledge from incident investigations and converting historical incident evidence into reusable knowledge for future incidents.

This literature is important because it motivates automated diagnosis under operational complexity. However, much AIOps research focuses on infrastructure, services, logs, microservices, or cloud operations rather than data-pipeline-specific failure modes. Even when AIOps approaches support root-cause analysis, they do not necessarily implement policy-constrained remediation for data pipelines or evaluate recovery success using post-recovery validation. This paper contributes to the data-engineering reliability setting by connecting root-cause classification to governed remediation outcomes.

#### 2.5 Autonomic Computing and Self-Healing Systems

Autonomic computing introduced the vision of systems that manage themselves through self-configuration, self-healing, self-optimization, and self-protection. This vision is directly relevant to data-pipeline reliability because pipeline failures increasingly exceed the capacity of manual operators to inspect, diagnose, and repair at scale. The autonomic-computing framing also emphasizes policies and high-level goals, which aligns with the need for governed recovery rather than unrestricted automation.

The gap is that autonomic computing is a broad systems paradigm. It does not specify a reproducible evaluation framework for data-pipeline failure detection, root-cause classification, policy approval, remediation execution, and post-recovery validation. This paper operationalizes the self-healing concept for data pipelines and evaluates each stage separately.

#### 2.6 Policy-as-Code and Governance

Policy-as-code systems such as Open Policy Agent decouple policy decision-making from policy enforcement. OPA provides a declarative policy language and APIs that allow applications and infrastructure systems to query policy decisions over structured inputs. This design is relevant to self-healing pipelines because automated remediation must not be allowed to perform unsafe changes simply because a failure was detected.

However, policy engines are decision components, not complete self-healing systems. They can approve, deny, or structure decisions, but they do not generate telemetry, diagnose pipeline failures, execute repairs, validate recovered state, or preserve incident evidence. This paper uses the policy-as-code idea as part of a larger reliability-control architecture.

## Research Gap

Existing literature and systems provide strong building blocks for pipeline reliability: workflow orchestration executes tasks, data-quality frameworks validate expectations, observability platforms detect anomalies, AIOps methods support diagnosis, autonomic computing motivates self-management, and policy-as-code provides decision guardrails. The unresolved gap is the lack of an end-to-end, reproducible evaluation framework for data pipelines that measures the full lifecycle from injected failure to detection, classification, policy-constrained remediation, validation, rollback or escalation, and incident evidence.

This gap matters because real enterprise data pipelines cannot be safely repaired by unrestricted automation. A failure may be detected correctly and classified accurately while still requiring human escalation because the remediation is unsafe, unavailable, unverifiable, or governance-sensitive. Therefore, a credible self-healing system must distinguish between detection success, classification success, attempted remediation, policy-approved remediation, executed remediation, and verified recovery.

This paper addresses that gap by modeling self-healing as a staged control plane rather than as a single automated action. The experiment reports separate metrics for failure detection, root-cause classification, and verified recovery. This separation is essential because a high detection score alone does not prove that a system can safely restore pipeline health. Similarly, a high automation rate without validation may indicate unsafe behavior rather than reliability improvement.

## Gap Matrix

| Related area | What it provides | What remains missing | How this paper differs |
|---|---|---|---|
| Workflow orchestration | DAG execution, scheduling, retries, logs, callbacks | Data-specific diagnosis, governed remediation, post-recovery validation | Adds a reliability-control layer above workflow execution |
| Data-quality validation | Rule checks, expectations, test failures, constraint enforcement | Root-cause classification and automated recovery workflow | Treats validation results as signals within a larger self-healing lifecycle |
| Observability and monitoring | Signals, alerts, symptoms, dashboards | Controlled repair and recovery verification | Measures recovery, not only visibility |
| AIOps/RCA | Anomaly detection, correlation, root-cause analysis | Data-pipeline-specific policy-constrained remediation | Connects diagnosis to governed recovery outcomes |
| Autonomic computing | General self-healing concept and policy-driven self-management | Domain-specific reproducible evaluation for data pipelines | Operationalizes self-healing for pipeline failure scenarios |
| Policy-as-code | Externalized policy decisions and enforcement guardrails | Detection, diagnosis, execution, validation, evidence | Uses policy as one stage in an end-to-end control plane |

## Strong Novelty Claim

The strongest defensible novelty claim is:

> This work presents and evaluates a reproducible policy-constrained self-healing control plane for data pipelines, separating failure detection, root-cause classification, remediation decisioning, execution, and post-recovery validation into measurable stages.

This is stronger than claiming:

> This work is the first self-healing data pipeline system.

The second claim is risky and likely false because self-healing, remediation automation, observability, data testing, and autonomic computing all exist in different forms. The paper should avoid broad “first-ever” language and instead claim a specific measurable contribution.

## Contribution Statement for the Paper

This paper makes the following contributions:

1. It defines a staged control-plane architecture for self-healing data pipelines, covering failure detection, root-cause classification, policy-constrained remediation, validation, rollback, escalation, and incident evidence.
2. It implements a reproducible experimental framework with injected data-pipeline failure scenarios, healthy controls, and boundary controls.
3. It reports separate metrics for detection accuracy, classification accuracy, and verified recovery, avoiding the misleading assumption that detection success equals recovery success.
4. It demonstrates that policy-constrained recovery produces a more realistic self-healing evaluation because unsafe, unavailable, or unverifiable remediations are not counted as successful recovery.
5. It provides reusable experiment artifacts, figures, and validity analysis to support reproducibility.

## Safe Claims for the Manuscript

The manuscript can safely claim that:

- Existing tools address important parts of data reliability but do not usually evaluate the complete detection-to-verified-recovery lifecycle.
- Workflow orchestration is necessary but insufficient for self-healing.
- Data-quality validation is a signal source, not a complete recovery framework.
- Observability improves visibility but does not automatically guarantee governed repair.
- AIOps motivates automated diagnosis, but data-pipeline remediation requires domain-specific controls.
- Policy-as-code supports remediation guardrails, but policy engines alone do not execute the full lifecycle.
- The paper’s main contribution is the measurable integration of these stages for data pipelines.

## Claims to Avoid

The manuscript should avoid claiming that:

- No one has studied self-healing systems before.
- No existing tool supports remediation.
- Observability platforms are irrelevant.
- Workflow orchestration is weak or obsolete.
- AIOps does not handle root-cause analysis.
- Policy engines are novel by themselves.
- The framework is production-proven.
- The current synthetic experiments prove universal generalization.

## Suggested Related Work Paragraph for Final Paper

Prior work in workflow orchestration, data-quality validation, monitoring, AIOps, autonomic computing, and policy-as-code provides important building blocks for reliable data systems. Workflow engines such as Apache Airflow provide task scheduling and execution semantics, but orchestration alone does not determine whether a data-specific remediation is safe or validated. Data-quality tools such as Great Expectations, dbt tests, platform-native rule systems, and Delta Lake constraints formalize expectations and detect invalid states, but they typically stop short of governed recovery. Monitoring and SRE practices emphasize symptom and cause analysis, while AIOps research advances anomaly detection and root-cause analysis for complex operational systems. Autonomic computing provides the broader vision of self-managing systems, and policy-as-code systems such as OPA provide externalized decision guardrails. This paper builds on these ideas but focuses on the missing end-to-end evaluation layer: a policy-constrained self-healing control plane for data pipelines that separately measures detection, classification, and verified recovery.

## References

[1] Apache Airflow Documentation. “What is Airflow?” Apache Software Foundation. https://airflow.apache.org/docs/apache-airflow/stable/index.html

[2] Great Expectations Documentation. “Try GX Core.” Great Expectations. https://docs.greatexpectations.io/docs/core/introduction/try_gx/

[3] dbt Documentation. “Add data tests to your DAG.” dbt Labs. https://docs.getdbt.com/docs/build/data-tests

[4] Google Cloud Documentation. “Auto data quality overview.” Google Cloud Knowledge Catalog. https://docs.cloud.google.com/dataplex/docs/auto-data-quality-overview

[5] Delta Lake Documentation. “Constraints.” Delta Lake. https://docs.delta.io/delta-constraints/

[6] Google Site Reliability Engineering Book. “Monitoring Distributed Systems.” Google. https://sre.google/sre-book/monitoring-distributed-systems/

[7] Open Policy Agent Documentation. “Open Policy Agent.” https://www.openpolicyagent.org/docs/

[8] Notaro, P., Cardoso, J., and Gerndt, M. “A Systematic Mapping Study in AIOps.” arXiv:2012.09108, 2020.

[9] Saha, A., and Hoi, S. C. H. “Mining Root Cause Knowledge from Cloud Service Incident Investigations for AIOps.” arXiv:2204.11598, 2022.

[10] Foidl, H., Golendukhina, V., Ramler, R., and Felderer, M. “Data Pipeline Quality: Influencing Factors, Root Causes of Data-related Issues, and Processing Problem Areas for Developers.” arXiv:2309.07067, 2023.

[11] Kephart, J. O., and Chess, D. M. “The Vision of Autonomic Computing.” IEEE Computer, 2003.

## Day 8 Completion Checklist

- [x] Related work categories defined.
- [x] Research gap drafted.
- [x] Gap matrix drafted.
- [x] Safe novelty claim defined.
- [x] Unsafe claims identified.
- [x] Contribution statement drafted.
- [x] References collected.
- [x] Day 9 handoff defined.

## Day 9 Handoff

Day 9 should focus on the **Introduction and Contributions** section. The paper now has the ingredients needed for a strong introduction: the operational problem, the limitation of existing tools, the research gap, the proposed policy-constrained control plane, and the corrected experimental results. Day 9 should produce a manuscript-ready introduction that does not overclaim generalization.
