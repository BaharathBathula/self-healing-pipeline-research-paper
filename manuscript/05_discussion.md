# 5. Discussion

## 5.1 Interpretation of the Main Findings
The evaluation produced three main findings.

First, the implemented detector and classifier were internally consistent across the controlled experiment. All 780 analyzed trials were assigned the expected detection state and root-cause class, yielding 100% detection and classification accuracy. This result indicates that the deterministic rules correctly recognized the failure mechanisms represented in the synthetic benchmark. It should not be interpreted as evidence that the system will achieve the same accuracy for unseen, ambiguous, compound, or production failures.

Second, the policy layer materially constrained autonomous behavior. Although all 690 true failures were detected and classified correctly, automatic actions were initiated in only 510 trials, or 73.91% of the failure population. The remaining 180 trials were deliberately routed to human approval because their configured actions were considered unsuitable for unrestricted execution. This separation between recognition and authorization is central to the proposed design: correct diagnosis did not automatically grant permission to modify data or downstream state.

Third, verified recovery depended on both technical remediation capability and the availability of a local verification mechanism. Recovery was verified in 360 of 690 true failures, producing an overall recovery rate of 52.17%. However, all 360 directly executed and locally verifiable remediations succeeded, producing a direct-action recovery rate of 100%. The difference between these two rates was caused by 150 retry-scheduling trials that required external confirmation and 180 approval-controlled trials that were intentionally not executed.

The runtime results indicate that the implemented control loop operated with low latency in the experimental environment. The median trial runtime was 10.61 milliseconds, and the 95th-percentile runtime was 26.67 milliseconds. These values show that the additional stages of classification, policy evaluation, remediation handling, and verification were computationally modest for the 10,000-row synthetic workload. They do not establish production throughput, distributed performance, or comparative efficiency against other systems.

Taken together, the findings support a narrower conclusion than unrestricted “self-healing.” The implementation demonstrated reliable closed-loop handling for known deterministic failure classes, policy-based restriction of autonomous actions, and explicit verification of supported direct remediations. Its strongest contribution is therefore not universal automatic recovery, but controlled autonomy with auditable boundaries between detection, authorization, execution, and verification.

## 5.2 Policy-Constrained Autonomy
The experiment shows that self-healing should not be defined solely as automatic execution after failure detection. A more defensible interpretation is policy-constrained autonomy, in which the system separates diagnosis from authorization and applies different response modes according to operational risk.

This distinction was visible in the experimental outcomes. All 690 true failures were detected and classified correctly, but only 510 resulted in an initiated automatic action. The other 180 failures were routed to human approval. These approval-controlled cases were not detection failures or remediation-engine failures; they were deliberate policy outcomes.

Schema drift and volume anomalies illustrate why this boundary matters. Both conditions can affect large portions of a dataset or alter assumptions used by downstream consumers. Automatically applying a schema mapping, deleting unexpected fields, or publishing data after a major volume deviation can create more harm than the original incident. Requiring approval in these cases reduces automation coverage, but it also limits the system’s authority to perform potentially irreversible or business-sensitive changes.

The 73.91% automatic-action initiation rate should therefore not be optimized in isolation. A higher rate could be achieved simply by marking additional actions as automatic, but that would not necessarily improve system quality. It could instead increase the risk of incorrect remediation, silent data loss, unsupported schema evolution, or downstream inconsistency.

The policy layer also provides an auditable explanation for non-execution. Each action is associated with a configured root cause, severity range, automatic-execution flag, and approval requirement. This makes it possible to distinguish between three materially different outcomes: an action executed automatically, an action scheduled for deferred execution, and an action withheld pending human review.

This separation is particularly important for enterprise data systems, where operational correctness includes governance, traceability, and controlled change management. A system that recovers more incidents automatically but cannot explain why an action was authorized may be less trustworthy than a system with lower automation coverage and explicit policy boundaries.

The results therefore suggest that automation coverage and policy compliance should be reported as separate dimensions. The objective of a policy-constrained self-healing system is not to maximize autonomous action in every scenario. It is to maximize safe, verifiable automation while preserving human control over actions whose operational risk exceeds the system’s delegated authority.

## 5.3 Detection and Classification Performance
The 100% detection and classification results demonstrate that the implemented rules were fully aligned with the controlled failure model. Every true failure produced the expected detection outcome, and every healthy or boundary-control trial produced the expected non-failure outcome. The classifier also mapped each detected condition to the expected root-cause category.

This result is useful as an implementation-validation finding. It confirms that the detector, classifier, experiment runner, and derived-analysis logic were internally consistent across 780 repeated trials. It also shows that the policy engine received stable root-cause inputs rather than being evaluated under noisy or ambiguous classifications.

However, perfect performance in this setting should not be treated as evidence of general diagnostic robustness. The failure injections were deterministic, isolated, and constructed around signals that the detector was explicitly designed to recognize. Schema changes, null-rate increases, duplicate records, timestamp delays, volume reductions, transformation defects, source exceptions, and checksum mismatches each produced comparatively distinct evidence patterns.

The benchmark did not include overlapping incidents, gradual degradation, conflicting signals, previously unseen failure types, or adversarial inputs. In production systems, a single incident may simultaneously produce freshness delay, record-count deviation, missing values, and downstream transformation errors. Under those conditions, deterministic single-label classification may become less reliable.

The source-failure results also require careful interpretation. Low-, medium-, and high-severity source trials all used the same simulated timeout exception. The perfect classification rate across those strata therefore demonstrates repeatability under the same failure mechanism, not sensitivity to increasing source-failure intensity.

Similarly, severity labels were scenario-specific. A high-severity schema change, high-severity artifact truncation, and high-severity transformation defect represented different technical mutations. The results support within-scenario consistency but do not imply that severity values were calibrated on a common operational-risk scale.

The freshness boundary-control analysis further shows that detection performance depends on the relationship between injected conditions and configured thresholds. The 30-minute delay correctly remained below the 60-minute threshold, while the 180-minute and 1,440-minute delays triggered freshness detection. This indicates consistent threshold enforcement, but it also highlights that reported accuracy can be distorted when expected labels are not aligned with the detector’s formal decision rule.

Future evaluation should therefore extend beyond deterministic known-answer scenarios. Useful additions include compound failures, threshold-adjacent perturbations, noisy telemetry, unseen schema mutations, alternative source exceptions, and datasets with naturally occurring quality defects. These experiments would test whether the classifier remains reliable when failure evidence is incomplete, overlapping, or inconsistent.

## 5.4 Recovery Verification and Operational Boundaries
The recovery results show why remediation execution and recovery verification must be treated as separate stages.

A remediation action can be selected and executed without proving that the original failure condition has been removed. The implementation addressed this by applying condition-specific verification after each supported direct remediation. Duplicate recovery required restored uniqueness of `order_id`; missing-value recovery required complete required fields in the retained output; transformation recovery required semantic integrity of derived totals; and artifact recovery required checksum equivalence with the trusted source.

All 360 directly executed and locally verifiable remediations passed these checks. This provides stronger evidence than reporting action completion alone because the recovery metric was based on the resulting state rather than on whether a remediation function returned successfully.

The 100% direct-action recovery rate nevertheless has a limited scope. The verification rules were deterministic and closely matched the injected failure mechanisms. Deduplication was tested against injected duplicate identifiers, null quarantine against injected nulls in required fields, transformation repair against known arithmetic corruption, and artifact regeneration against deterministic truncation. These results do not establish successful recovery from more complex defects such as partial corruption, semantically valid but incorrect values, inconsistent cross-table relationships, or downstream contract violations.

The 150 retry-scheduling trials illustrate a second operational boundary. For source failures and above-threshold freshness violations, the system generated retry schedules but did not interact with a real upstream service. Treating those trials as recovered would have overstated the evidence. The experiment therefore counted them as automatic-action initiations but assigned no verified recovery.

The 180 approval-controlled trials illustrate a third boundary. Schema-drift and volume-anomaly incidents were detected and classified, but the system intentionally stopped before remediation. This behavior preserved governance constraints but left final recovery dependent on a human decision and a subsequent execution path that was outside the experiment.

The overall verified-recovery rate of 52.17% should therefore be interpreted as an end-to-end evidence rate under the implemented control boundaries, not as the success rate of the remediation code. It combines direct technical recovery, deferred external actions, and intentionally withheld actions within one denominator.

For operational deployment, additional recovery states would be useful. These could distinguish `action_completed`, `recovery_verified_locally`, `recovery_pending_external_confirmation`, `awaiting_human_approval`, `post-approval_recovery_verified`, and `recovery_failed`. Such state separation would reduce ambiguity in service-level reporting and prevent scheduled or pending actions from being presented as completed recovery.

## 5.5 Freshness Boundary-Control Interpretation
The freshness boundary-control correction is methodologically important because it changed the interpretation of 30 trials without changing the underlying experiment.

The detector’s freshness threshold was fixed at 60 minutes. The low-severity injection delayed 10% of timestamps by 30 minutes, while the medium- and high-severity injections delayed 25% and 50% of timestamps by 180 and 1,440 minutes respectively. Under the implemented decision rule, the low-severity condition was sub-threshold and the other two conditions were true freshness violations.

The initial analysis treated all injected freshness scenarios as expected failures because they shared the same injected-failure label. This created 30 apparent false negatives even though the detector behaved consistently with its configured threshold. The later derived-analysis correction aligned the expected outcome with the formal decision rule and reclassified the low-severity trials as boundary controls.

This distinction matters because an experiment’s injected scenario name is not sufficient to determine the expected detector outcome. Expected labels must be derived from the actual perturbation value and the detector’s threshold semantics. Otherwise, sub-threshold controls may be incorrectly counted as detection failures, while threshold-insensitive detectors may appear more accurate than they are.

The correction improved detection and classification accuracy from 96.15% to 100% and changed the true-failure denominator from 720 to 690. These numerical changes are substantial, so the correction must remain transparent. The raw records were preserved, and the analysis retained both the original injected label and the derived boundary-control label to maintain traceability.

The main weakness is that the expected boundary outcome was not preregistered before execution. The correction is technically justified by the predefined 60-minute threshold, but it still involved post-execution researcher judgment. This creates a risk that similar reclassifications could be used selectively to improve results if the analytical rule were not clearly documented.

Future experiments should define three explicit freshness conditions before execution: below threshold, exactly at threshold, and above threshold. Each condition should have a preregistered expected detection result. Equivalent boundary tests should also be created for missing-value, duplicate, and volume thresholds.

The broader implication is that threshold-boundary controls are not secondary test cases. They are necessary evidence that a detector distinguishes acceptable variation from operational failure. A system that detects every perturbation may appear sensitive, but it may also generate excessive false positives by ignoring configured tolerances. Reliable detection requires both failure sensitivity and correct non-failure behavior near decision boundaries.

## 5.6 Practical Implications
The results have several practical implications for teams designing self-healing data systems.

First, remediation policy should be implemented as an explicit control layer rather than embedded implicitly inside detection or execution code. The experiment showed that the same correctly classified incident can lead to automatic execution, deferred retry, or human approval depending on policy. Keeping these decisions separate improves auditability and makes changes to operational authority easier to review.

Second, teams should report automation coverage and verified recovery separately. A system may initiate many actions without proving that failures were removed. In this experiment, 510 automatic actions were initiated, but only 360 recoveries were locally verified. Combining these outcomes into one “self-healing success rate” would materially overstate system effectiveness.

Third, every remediation should have a failure-specific verification rule. Generic success signals, such as a function completing without exception, are insufficient. Verification should test the condition that originally defined the failure. For example, deduplication should be followed by a uniqueness check, transformation repair by semantic validation, and artifact recovery by integrity verification.

Fourth, human approval should be treated as a designed terminal state rather than as an implementation gap. Schema and volume incidents may require business context that is unavailable to an automated system. The system should preserve evidence, prevent unsafe downstream action, and provide operators with a clear rationale for the approval request.

Fifth, retry-based remediations require asynchronous lifecycle tracking. Scheduling a retry is only an intermediate step. A production implementation should record whether the retry started, whether the upstream dependency recovered, whether data was retrieved completely, and whether the downstream pipeline returned to a valid state.

Sixth, threshold-based detectors should include explicit boundary tests. Below-threshold conditions, exact-threshold conditions, and above-threshold conditions should be evaluated separately. This reduces false-positive risk and prevents analytical confusion about whether a perturbation should count as a failure.

Seventh, severity labels should correspond to measurable technical differences. The source-failure experiment used identical timeout behavior for all three severity labels, so those labels did not represent increasing failure intensity. In operational systems, severity should be linked to observable dimensions such as outage duration, retry exhaustion, affected sources, data-loss risk, or downstream impact.

Finally, evidence capture should be designed alongside remediation logic. Each cycle should preserve the detected signals, classification, policy decision, execution outcome, approval state, verification evidence, and final status. Without this evidence chain, an automated recovery system may be difficult to trust, investigate, or govern even when its remediation actions are technically correct.

## 5.7 Limitations and Future Research
The findings are constrained by the controlled nature of the evaluation and should not be generalized beyond the implemented evidence.

The first limitation is the use of a synthetic 10,000-row order dataset. Synthetic data enabled repeatable injection, exact expected outcomes, and deterministic verification, but it did not reproduce the scale, heterogeneity, governance requirements, or dependency structure of enterprise data platforms. Future work should evaluate the framework using larger datasets, multiple schemas, cross-table relationships, and real operational traces.

The second limitation is the absence of quantitative baselines. Alert-only monitoring and static-rule remediation were discussed as conceptual reference points but were not implemented. Future studies should compare the proposed system against at least three alternatives: alert-only detection, fixed remediation rules without policy constraints, and policy-constrained remediation without post-action verification. This would isolate the contribution of policy gating and recovery verification.

The third limitation is the deterministic and isolated failure model. Each trial contained one predefined failure category with a known injection mechanism. Real incidents may be compound, progressive, intermittent, or ambiguous. Future experiments should include combinations such as schema drift with missing values, source failure followed by freshness degradation, and transformation defects combined with output corruption.

The fourth limitation is incomplete external-system validation. Source-failure and freshness actions generated retry schedules but did not interact with a real upstream dependency. Future work should integrate controllable source services that can fail, recover, return partial data, or exhaust retry budgets. Recovery should then be verified through complete end-to-end pipeline execution.

The fifth limitation is that approval-controlled scenarios stopped at the human-approval boundary. Future evaluation should measure approval latency, operator decisions, post-approval execution, rejection outcomes, and final recovery. This would provide a more complete view of human-in-the-loop operational performance.

The sixth limitation is the scenario-specific severity model. Most scenarios used measurable technical differences, but source-failure severity labels mapped to the same timeout exception. Future work should define source-failure severity using distinct outage durations, retry exhaustion levels, affected endpoints, response corruption, and downstream impact.

The seventh limitation is the narrow volume experiment. Only decreasing-volume anomalies were executed, despite implementation support for increasing-volume conditions. Future experiments should include both directions and distinguish expected business growth from duplicate ingestion, replay, and source amplification.

The eighth limitation concerns threshold evaluation. Only one explicit sub-threshold boundary condition was analyzed after execution. Future studies should preregister below-threshold, threshold-equal, and above-threshold cases for every detector threshold and evaluate both sensitivity and false-positive behavior.

The ninth limitation is the local execution environment. Runtime measurements were collected on Windows 11 in a Python virtual environment using one dataset size and no concurrent workload. Future performance evaluation should include containerized execution, multiple hardware profiles, larger datasets, concurrency, distributed processing, and cloud orchestration.

The tenth limitation is that the remediation registry was not part of the executed runtime path. Future implementation work should repair and validate the registry schema, integrate it with the policy engine, and test registry-defined timeouts, rollback requirements, validation checks, and approval constraints. These controls should not be claimed until they are exercised in repeatable experiments.

The next research phase should prioritize stronger evidence over additional feature breadth. The most valuable extensions are comparative baselines, compound failures, real external-service recovery, human-approval completion, and preregistered threshold-boundary tests. Adding more remediation actions without these controls would increase implementation scope but would not materially strengthen the scientific validity of the study.
