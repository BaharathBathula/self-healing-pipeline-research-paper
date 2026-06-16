# Day 7 — Results, Discussion, and Validity Draft

Paper title: **Reliability-Aware Self-Healing Data Pipelines: Automated Failure Detection, Root-Cause Classification, and Policy-Constrained Recovery**

Date: 2026-06-15

## Day 7 Objective

Day 7 converts the experimental outputs generated during Days 5–6 into manuscript-ready research interpretation. The goal is not to add new claims. The goal is to state the results accurately, explain what they mean, identify limitations, and prepare the paper for a credible Results and Discussion section.

## Corrected Experiment Summary

| Metric | Corrected value |
|---|---:|
| Total trials | 780 |
| Injected failure trials | 690 |
| Healthy control trials | 60 |
| Boundary-control trials | 30 |
| Failure detection accuracy | 100% |
| Root-cause classification accuracy | 100% |
| Verified recovery rate across injected failures | 52.17% |

These numbers should be reported conservatively. Detection and classification performance can be described as perfect within the current synthetic experiment configuration. Recovery performance must not be described as perfect. The key finding is that the framework reliably detects and classifies injected failures, while recovery success depends on whether the remediation is policy-approved, executable, and verifiable.

## 4. Results — Manuscript Draft

The experimental evaluation produced 780 total trial records spanning injected failures, healthy controls, and boundary-control scenarios. Of these, 690 trials corresponded to injected data-pipeline failure conditions, 60 trials represented healthy-control executions, and 30 trials represented boundary-control conditions. The experiment design therefore evaluates both positive failure cases and non-failure controls rather than measuring the detector only on failure-positive examples.

Across the evaluated trial set, the self-healing control plane achieved 100% failure detection accuracy and 100% root-cause classification accuracy under the current synthetic failure model. This result indicates that the implemented detector and classifier were able to consistently identify the presence of injected failures and assign the expected failure category when the failure type was represented in the experiment configuration. The result should be interpreted as evidence of internal consistency and technical feasibility, not as evidence that the model will generalize without degradation to arbitrary enterprise production environments.

Verified recovery was achieved in 52.17% of injected failure trials. This result is intentionally lower than detection and classification accuracy because recovery is subject to additional constraints. A failure may be detected and correctly classified while still not be automatically remediated if the policy layer rejects the action, the remediation registry does not contain a safe recovery procedure, the recovery action cannot be verified, or the failure requires human escalation. For a reliability-oriented system, this distinction is important: unsafe automation is not counted as success merely because the system attempted a repair.

The figure set generated for the paper supports four complementary views of the experiment. Figure 1 reports detection and root-cause classification accuracy by injected scenario. Figure 2 reports verified recovery rates by failure scenario. Figure 3 reports runtime distribution for the self-healing cycle. Figure 4 presents the root-cause classification confusion matrix. Together, these figures separate observability performance, diagnostic performance, remediation performance, and runtime behavior.

The strongest empirical result is the separation between high observability/diagnosis accuracy and partial verified recovery. The system does not simply maximize automation. Instead, the recovery stage is governed by policy constraints and post-recovery validation. This supports the central claim that self-healing data pipelines should be evaluated as controlled reliability systems rather than as unrestricted remediation scripts.

## 5. Discussion — Manuscript Draft

The experimental results suggest that policy-constrained self-healing is best understood as a staged reliability-control process. Detection, diagnosis, remediation selection, execution, validation, rollback, and escalation are distinct responsibilities. Treating these stages separately avoids the common mistake of evaluating self-healing systems only by whether an automated action was attempted.

The 100% detection and classification results demonstrate that the current implementation can reliably recognize the injected failure scenarios used in the experiment. However, these results should not be overstated. The failures are synthetic, the taxonomy is predefined, and the classifier is evaluated against known categories. The appropriate interpretation is that the framework is technically coherent and reproducible under controlled conditions.

The lower verified recovery rate is not a weakness by itself. It reflects the system design choice to enforce policy approval and post-recovery validation. In enterprise data pipelines, an automated remediation that corrupts downstream data, violates governance rules, or masks a serious source-system problem is worse than a controlled escalation. Therefore, the framework counts only verified recovery as successful recovery. Attempts that are rejected, escalated, rolled back, or unverifiable are treated separately from successful self-healing.

This distinction is especially important for regulated or high-dependence data environments. Data platforms used for insurance, finance, healthcare, compliance reporting, or operational analytics often require traceability and defensible control points. In such environments, self-healing cannot be judged purely by speed or automation rate. It must also preserve evidence, enforce guardrails, and make failure-handling decisions auditable.

The current results therefore support a narrower but stronger contribution: a reproducible experimental framework for evaluating data-pipeline self-healing as a policy-constrained control plane. The contribution is not that every pipeline failure can be repaired automatically. The contribution is that failure detection, root-cause classification, safe remediation selection, validation, and escalation can be represented as measurable stages with separate outcomes.

## Claims We Can Make

1. The framework implements a staged self-healing control plane for data-pipeline failures.
2. The experiment design includes injected failures, healthy controls, and boundary controls.
3. The current synthetic experiments produced 780 trial records.
4. Detection and root-cause classification achieved 100% accuracy within the current synthetic experiment configuration.
5. Verified recovery across injected failures was 52.17%, showing that recovery is constrained by policy approval, remediation availability, execution feasibility, and validation.
6. The framework separates detection success from remediation success, which is important for safe enterprise automation.
7. The generated figures provide publication-ready visual evidence for accuracy, recovery, runtime, and confusion-matrix behavior.

## Claims We Must Not Make Yet

1. The system is production-proven.
2. The framework generalizes to all enterprise data-pipeline failures.
3. The 100% detection/classification result will hold on real-world production incidents.
4. The framework outperforms commercial observability platforms.
5. The framework eliminates the need for human operators.
6. The framework guarantees safe recovery for unknown failures.
7. The recovery rate is a failure of the architecture; the correct interpretation is policy-constrained verified recovery.

## Threats to Validity

### Internal Validity

The experiment uses controlled failure injection. This improves reproducibility but may simplify the relationship between injected failures and observable telemetry. A detector may perform better in this environment than in a production system where failures are noisy, overlapping, delayed, or partially observable.

### Construct Validity

The metrics separate detection accuracy, root-cause classification accuracy, and verified recovery rate. This is appropriate for the paper's research objective, but these metrics do not capture every operational concern. For example, they do not fully measure operator trust, downstream business impact, long-term model drift, or the cost of false escalation.

### External Validity

The results should be generalized carefully. The experiment currently evaluates a predefined taxonomy of failure conditions. Real-world data platforms may include infrastructure failures, vendor API instability, semantic data-quality defects, access-control issues, cross-system contract changes, and cascading downstream failures that are not fully represented in the current test set.

### Conclusion Validity

The experiment provides strong evidence that the framework works under the current controlled setup. It does not yet prove superiority over mature observability products or enterprise incident-management workflows. Future experiments should compare the policy-constrained framework against alert-only monitoring and static rule-based automation using identical failure scenarios and operational metrics.

## Figure Captions for Manuscript

**Figure 1. Detection and root-cause classification accuracy by injected scenario.** The figure compares detection accuracy and classification accuracy across the evaluated scenario taxonomy. Under the current synthetic experiment configuration, both metrics reached 100% across the evaluated scenarios.

**Figure 2. Verified recovery rate by failure scenario.** The figure reports the proportion of injected failure trials that resulted in verified recovery. The recovery rate is expected to be lower than detection accuracy because remediation is subject to policy approval, execution success, and post-recovery validation.

**Figure 3. Self-healing cycle runtime distribution.** The figure summarizes runtime behavior across experiment domains. Runtime is reported separately from accuracy and recovery because an operational self-healing system must be both reliable and practical to execute.

**Figure 4. Root-cause classification confusion matrix.** The figure compares injected root-cause labels against predicted root-cause labels. The current matrix supports the claim that the classifier correctly mapped the evaluated synthetic failures to their expected categories.

## Day 7 Completion Checklist

- [x] Corrected experiment summary preserved.
- [x] Results section drafted.
- [x] Discussion section drafted.
- [x] Threats to validity drafted.
- [x] Defensible claims separated from unsafe claims.
- [x] Figure captions drafted.
- [x] Day 8 handoff defined.

## Day 8 Handoff

Day 8 should focus on the **Related Work and Research Gap** section. The goal is to position the paper against data observability, data-quality monitoring, workflow orchestration, incident response, and autonomous/self-healing systems. Day 8 must be careful not to claim novelty only because the implementation exists. The research gap should be framed around measurable, policy-constrained recovery for data pipelines, not generic monitoring or generic automation.
