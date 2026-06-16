# Day 16 — References Upgrade and Citation Cleanup

Paper title: **Reliability-Aware Self-Healing Data Pipelines: Automated Failure Detection, Root-Cause Classification, and Policy-Constrained Recovery**

Date: 2026-06-15

## Day 16 Objective

Day 16 upgrades the weakest remaining part of the manuscript: **References and Related Work credibility**.

`manuscript-v0.2.md` is structurally strong, but the reference base is still too documentation-heavy. Documentation is useful for explaining tools, but it is not enough to support a research paper. Day 16 separates references into:

1. scholarly references that support the research argument,
2. official documentation references that describe tools,
3. references to remove, verify, or demote,
4. citation-placement guidance for `manuscript-v0.3.md`.

---

## Executive Decision

The paper should use this rule:

> Use peer-reviewed or research references to support claims about reliability, data quality, self-healing, AIOps, and production pipeline complexity. Use official documentation only when describing specific tools.

This means:

- Airflow docs can support what a DAG does.
- dbt docs can support what dbt data tests do.
- Great Expectations docs can support what Expectations are.
- OPA docs can support policy-decision architecture.
- They should **not** be the main evidence for the paper's research gap or novelty.

---

# 1. Current Reference Audit

The current v0.2 references are useful but uneven.

| Current ref | Type | Keep? | Action |
|---|---|---:|---|
| Apache Airflow Documentation | Official docs | Yes | Keep only for tool description |
| Great Expectations Documentation | Official docs | Yes | Keep only for validation tool description |
| dbt Documentation | Official docs | Yes | Keep only for data test description |
| Google Cloud Auto Data Quality | Official docs | Maybe | Use only if directly discussed |
| Delta Lake Constraints | Official docs | Maybe | Use only if directly discussed |
| Google SRE Monitoring Distributed Systems | Official book/docs | Yes | Keep for monitoring/observability framing |
| Open Policy Agent Documentation | Official docs | Yes | Keep for policy-as-code architecture |
| Notaro et al., AIOps mapping | Research | Yes | Strengthen AIOps subsection |
| Saha and Hoi, RCA from incidents | Research | Yes | Strengthen RCA subsection |
| Foidl et al., Data Pipeline Quality | Research | Yes | Strengthen data-pipeline quality motivation |
| Kephart and Chess, Autonomic Computing | Research | Yes | Anchor self-healing/autonomic framing |

---

# 2. Stronger Reference Set for v0.3

## Core Scholarly References

Use these as the primary academic foundation.

### R1 — Autonomic Computing

**Kephart, J. O., and Chess, D. M.**  
“The Vision of Autonomic Computing.” *Computer*, 36(1), 41–50, 2003.  
DOI: `10.1109/MC.2003.1160055`

Use for:

- autonomic computing,
- self-healing systems,
- policy-guided self-management.

Manuscript placement:

- Section 2.5 Autonomic Computing and Self-Healing Systems
- Introduction if the paper briefly references the self-healing lineage

### R2 — AIOps Survey / Mapping

**Notaro, P., Cardoso, J., and Gerndt, M.**  
“A Systematic Mapping Study in AIOps.” arXiv:2012.09108, 2020.

Use for:

- AIOps as an area,
- anomaly detection and root-cause analysis,
- positioning diagnosis as an operations research area.

Manuscript placement:

- Section 2.4 AIOps and Root-Cause Analysis

### R3 — Root-Cause Analysis from Incident Knowledge

**Saha, A., and Hoi, S. C. H.**  
“Mining Root Cause Knowledge from Cloud Service Incident Investigations for AIOps.” arXiv:2204.11598, 2022.

Use for:

- incident knowledge,
- RCA evidence,
- structured root-cause knowledge from historical incidents.

Manuscript placement:

- Section 2.4 AIOps and Root-Cause Analysis

### R4 — Data Pipeline Quality

**Foidl, H., Golendukhina, V., Ramler, R., and Felderer, M.**  
“Data Pipeline Quality: Influencing Factors, Root Causes of Data-related Issues, and Processing Problem Areas for Developers.” arXiv:2309.07067, 2023.

Use for:

- data-pipeline quality motivation,
- root causes of data-related issues,
- showing the field recognizes pipeline unreliability.

Manuscript placement:

- Introduction
- Section 2.2 Data-Quality Validation and Data Testing
- Section 2.7 Research Gap

### R5 — Hidden Technical Debt in ML/Data Systems

**Sculley, D., Holt, G., Golovin, D., Davydov, E., Phillips, T., Ebner, D., Chaudhary, V., Young, M., Crespo, J.-F., and Dennison, D.**  
“Hidden Technical Debt in Machine Learning Systems.” *Advances in Neural Information Processing Systems*, 2015.

Use for:

- pipeline jungles,
- data dependencies,
- system-level maintenance risk,
- why data pipelines need more than ad hoc repair.

Manuscript placement:

- Introduction
- Related Work
- Discussion

### R6 — Production ML Pipeline Complexity

**Xin, D., Miao, H., Parameswaran, A., and Polyzotis, N.**  
“Production Machine Learning Pipelines: Empirical Analysis and Optimization Opportunities.” arXiv:2103.16007, 2021.

Use for:

- production pipelines are complex,
- reproducibility and robustness concerns,
- pipeline architecture and repeated components.

Manuscript placement:

- Introduction
- Related Work
- Threats to Validity

### R7 — Workflow-as-Code / Airflow Challenges

**Yasmin, J., Wang, J., Tian, Y., and Adams, B.**  
“An Empirical Study of Developers' Challenges in Implementing Workflows as Code: A Case Study on Apache Airflow.” arXiv:2406.00180, 2024.

Use for:

- workflow orchestration challenges,
- Airflow-related developer obstacles,
- why orchestration alone does not solve reliability.

Manuscript placement:

- Section 2.1 Workflow Orchestration

---

## Official Documentation References

Use these only to explain tools.

### D1 — Apache Airflow Documentation

**Apache Airflow Documentation.**  
“Dags — Airflow Documentation.”

Use for:

- DAGs,
- tasks,
- dependencies,
- scheduling,
- workflow execution.

Do not use for:

- research novelty,
- self-healing claims.

### D2 — Great Expectations Documentation

**Great Expectations Documentation.**  
“Try GX Core.”

Use for:

- expectations as data-conformance definitions,
- data validation framing.

Do not use for:

- research gap claims.

### D3 — dbt Documentation

**dbt Labs Documentation.**  
“Add data tests to your DAG.”

Use for:

- data tests as assertions,
- failing rows,
- generic tests.

Do not use for:

- broad claims about data reliability research.

### D4 — Open Policy Agent Documentation

**Open Policy Agent Documentation.**  
“Open Policy Agent.”

Use for:

- policy-as-code,
- policy decision decoupling,
- Rego / policy engine framing.

Do not use for:

- proving self-healing novelty.

### D5 — Google SRE Book

**Google Site Reliability Engineering Book.**  
“Monitoring Distributed Systems.”

Use for:

- monitoring/observability framing,
- alerting and operational signals.

Do not use for:

- data-pipeline-specific recovery claims.

---

# 3. References to Remove, Verify, or Demote

## Remove or Demote Unless Directly Discussed

### Google Cloud Auto Data Quality

Keep only if the paper specifically discusses Google Cloud's data quality capabilities.

Otherwise remove from v0.3 references.

### Delta Lake Constraints

Keep only if the paper specifically discusses Delta Lake table constraints.

Otherwise remove from v0.3 references.

## Candidate References to Verify Later

These are useful but should be verified before final submission:

1. Breck et al., “Data Validation for Machine Learning.”
2. Schelter et al., “Automating Large-Scale Data Quality Verification.”
3. Polyzotis et al., “Data Management Challenges in Production Machine Learning.”

Do not add them to the final manuscript until bibliographic details are verified.

---

# 4. Citation Placement Plan for manuscript-v0.3.md

## Introduction

Add citations to the motivation paragraph:

Recommended citation support:

- Foidl et al. for data-pipeline quality and root causes.
- Sculley et al. for pipeline jungles and system-level maintenance risk.
- Xin et al. for production pipeline complexity.

Suggested sentence:

> Prior work has shown that data pipelines are central to modern data-driven systems but remain vulnerable to quality, processing, and maintenance problems, including data dependencies, pipeline jungles, and complex production pipeline structures [R4, R5, R6].

## Related Work — Workflow Orchestration

Use:

- D1 Airflow docs
- R7 Airflow empirical study

Suggested sentence:

> Airflow DAGs define schedules, tasks, dependencies, callbacks, and operational workflow details, but the DAG abstraction is primarily concerned with task execution order rather than the semantics of data repair [D1]. Empirical work on Airflow-related questions also shows that developers face workflow definition and execution challenges in practice [R7].

## Related Work — Data Quality Validation

Use:

- D2 Great Expectations docs
- D3 dbt docs
- R4 Data Pipeline Quality
- R5 Hidden Technical Debt

Suggested sentence:

> Data-quality tools provide assertion and expectation mechanisms for identifying invalid data states [D2, D3], while research on pipeline quality and technical debt shows that data issues and pipeline jungles remain broader engineering problems [R4, R5].

## Related Work — Observability and Monitoring

Use:

- D5 Google SRE monitoring
- R5 Sculley et al.

Suggested sentence:

> Monitoring and observability provide operational visibility, but monitoring alone does not determine whether an automated remediation is safe, policy-approved, or validated after execution [D5, R5].

## Related Work — AIOps and RCA

Use:

- R2 Notaro et al.
- R3 Saha and Hoi

Suggested sentence:

> AIOps research has placed substantial attention on failure-related tasks such as anomaly detection and root-cause analysis [R2], and incident-investigation work shows how root-cause knowledge can be mined from historical operational evidence [R3].

## Related Work — Autonomic Computing

Use:

- R1 Kephart and Chess

Suggested sentence:

> The autonomic computing vision motivates self-managing systems guided by high-level goals and policies, but it does not by itself provide a data-pipeline-specific evaluation framework for policy-constrained verified recovery [R1].

## Related Work — Policy-as-Code

Use:

- D4 Open Policy Agent docs

Suggested sentence:

> OPA decouples policy decision-making from enforcement and provides a declarative policy language and APIs for offloading policy decisions from software systems [D4].

---

# 5. Proposed v0.3 References List

Use this cleaner reference list for `manuscript-v0.3.md`.

```text
[1] J. O. Kephart and D. M. Chess, "The Vision of Autonomic Computing," Computer, vol. 36, no. 1, pp. 41–50, 2003, doi: 10.1109/MC.2003.1160055.

[2] P. Notaro, J. Cardoso, and M. Gerndt, "A Systematic Mapping Study in AIOps," arXiv:2012.09108, 2020.

[3] A. Saha and S. C. H. Hoi, "Mining Root Cause Knowledge from Cloud Service Incident Investigations for AIOps," arXiv:2204.11598, 2022.

[4] H. Foidl, V. Golendukhina, R. Ramler, and M. Felderer, "Data Pipeline Quality: Influencing Factors, Root Causes of Data-related Issues, and Processing Problem Areas for Developers," arXiv:2309.07067, 2023.

[5] D. Sculley, G. Holt, D. Golovin, E. Davydov, T. Phillips, D. Ebner, V. Chaudhary, M. Young, J.-F. Crespo, and D. Dennison, "Hidden Technical Debt in Machine Learning Systems," in Advances in Neural Information Processing Systems, 2015.

[6] D. Xin, H. Miao, A. Parameswaran, and N. Polyzotis, "Production Machine Learning Pipelines: Empirical Analysis and Optimization Opportunities," arXiv:2103.16007, 2021.

[7] J. Yasmin, J. Wang, Y. Tian, and B. Adams, "An Empirical Study of Developers' Challenges in Implementing Workflows as Code: A Case Study on Apache Airflow," arXiv:2406.00180, 2024.

[8] Apache Airflow Documentation, "Dags — Airflow Documentation," Apache Software Foundation, accessed Jun. 15, 2026.

[9] Great Expectations Documentation, "Try GX Core," Great Expectations, accessed Jun. 15, 2026.

[10] dbt Labs Documentation, "Add data tests to your DAG," dbt Labs, accessed Jun. 15, 2026.

[11] Open Policy Agent Documentation, "Open Policy Agent," Open Policy Agent, accessed Jun. 15, 2026.

[12] Google Site Reliability Engineering Book, "Monitoring Distributed Systems," Google, accessed Jun. 15, 2026.
```

---

# 6. Related Work Rewrite Guidance for v0.3

The Related Work section should be rewritten to sound less like a tool catalog and more like a research argument.

Use this structure inside each subsection:

1. What the area contributes.
2. Why it matters for data-pipeline reliability.
3. What limitation remains.
4. How this paper addresses that limitation.

Example:

> Workflow orchestration systems provide task scheduling, dependency management, retries, and operational execution models. These capabilities are essential for data-pipeline execution, but they do not determine whether a data-specific recovery action is safe, policy-approved, or post-validated. This paper therefore treats orchestration as the execution substrate and evaluates self-healing as a separate reliability-control process.

---

# 7. Required v0.3 Edits

`manuscript-v0.3.md` should make these edits:

1. Replace the current references list with the proposed v0.3 list.
2. Remove Google Cloud Auto Data Quality unless explicitly discussed.
3. Remove Delta Lake Constraints unless explicitly discussed.
4. Add citations to the Introduction motivation paragraph.
5. Add citations to every Related Work subsection.
6. Rewrite Related Work to avoid sounding like a tool survey.
7. Keep documentation references only for describing tools.
8. Use scholarly references for research motivation and gap.
9. Add citation placeholders to Methods only where necessary.
10. Keep Results citation-light because Results should cite artifacts, not external papers.

---

# 8. Risk Audit After Reference Upgrade

## Risk 1: Documentation-Heavy Paper

Status: reduced, but not fully fixed until v0.3.

Fix:

Use R1–R7 as the main research foundation.

## Risk 2: Weak Data Observability Literature

Status: still a gap.

Fix:

Day 17 should add 2–3 more sources specifically about data observability or data quality monitoring if the target venue expects deeper related work.

## Risk 3: Citation Style Inconsistency

Status: present.

Fix:

Choose one style before submission:

- IEEE numbered references,
- ACM author-year,
- APA,
- journal-specific style.

For now, keep IEEE numbered style because it fits technical papers.

## Risk 4: Unverified Candidate References

Status: avoid adding them until verified.

Fix:

Keep Breck, Schelter, and Polyzotis as Day 17 candidates.

---

# 9. Day 16 Completion Checklist

- [x] Current references audited.
- [x] Documentation references separated from scholarly references.
- [x] Stronger scholarly reference set created.
- [x] Weak references marked for removal or demotion.
- [x] Citation placement plan created.
- [x] v0.3 references list drafted.
- [x] Related Work rewrite guidance created.
- [x] v0.3 edit checklist created.
- [x] Remaining reference risks identified.
- [x] Day 17 handoff defined.

---

# Day 17 Handoff

Day 17 should create `docs/manuscript-v0.3.md`.

The main Day 17 task is to rewrite the Introduction citation support and Related Work section using the Day 16 reference upgrade.

Day 17 should not add new experiment claims. It should only improve citations, source credibility, and related-work positioning.
