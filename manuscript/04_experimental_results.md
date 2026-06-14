# 4. Experimental Results

## 4.1 Trial Accounting
The completed experiment produced 780 trial records across dataframe and output-artifact domains. The dataframe domain contributed 660 trials, comprising 630 injected scenario trials and 30 healthy controls. The artifact domain contributed 120 trials, comprising 90 output-corruption trials and 30 healthy controls.

After applying the predefined detector thresholds during analysis, 690 trials were treated as true failures. The remaining 90 trials consisted of 60 healthy controls and 30 freshness boundary controls. The boundary controls were the low-severity freshness trials in which the injected 30-minute delay remained below the configured 60-minute freshness threshold.

The true-failure population consisted of 600 dataframe failures and 90 artifact failures. The dataframe failures covered schema drift, missing-value spikes, duplicate generation, above-threshold freshness violations, volume anomalies, transformation logic errors, and source failures. The artifact failures covered output-artifact corruption at three injected-severity levels.

All 780 raw records remained in the analysis dataset. The boundary-control correction changed only the derived expected condition for the 30 sub-threshold freshness trials; it did not remove trials or alter raw detector, classification, policy, remediation, or runtime values.

The final evaluation denominators were therefore:

* 780 trials for detection and classification performance;
* 690 true failure trials for automatic-action initiation and overall verified recovery;
* 360 directly executed, locally verifiable remediation trials for direct-action recovery; and
* 90 non-failure trials for false-positive evaluation.

## 4.2 Detection and Classification Performance
The system correctly detected and classified all 780 analyzed trials. Detection accuracy was 1.000, with a two-sided 95% confidence interval from 0.9951 to 1.0000. Classification accuracy was also 1.000, with the same confidence interval.

The detection confusion matrix contained 690 true positives and 90 true negatives, with no false positives and no false negatives. Sensitivity and specificity were therefore both 1.000 for the controlled experimental dataset.

The 90 true-negative trials consisted of 60 healthy controls and 30 freshness boundary controls. The boundary-control trials were not treated as missed failures because their 30-minute injected delay remained below the configured 60-minute detection threshold.

Classification evaluation used the injected root-cause category as the expected class for true failures. Healthy controls and freshness boundary controls used `healthy_control` as the expected analysis class. Under this derived evaluation labeling, all trials were assigned the expected root-cause class.

Figure 1 presents detection and classification accuracy by scenario. Figure 4 presents the classification confusion matrix. Both figures show complete separation among the deterministic failure conditions represented in the experiment.

These results demonstrate internal correctness under the implemented synthetic scenarios and predefined thresholds. They do not establish equivalent performance for unseen, ambiguous, compound, or production failures because all evaluated conditions were generated using known deterministic injection mechanisms.

## 4.3 Policy-Controlled Execution Outcomes
Among the 690 true failure trials, the policy engine authorized and initiated an automatic response in 510 trials, corresponding to an automatic-action initiation rate of 0.7391. The two-sided 95% confidence interval was 0.7051 to 0.7705.

The 510 initiated actions consisted of two distinct outcome types. Direct, state-changing remediations were executed in 360 trials covering duplicate generation, missing-value spikes, transformation logic errors, and output-artifact corruption. The remaining 150 trials covered source failures and above-threshold freshness violations, for which the system generated retry or refresh schedules.

The remaining 180 failure trials, representing 26.09% of the true-failure population, were intentionally withheld from automatic execution. These trials comprised schema-drift and volume-anomaly scenarios. Their configured policies required human approval, so the system returned an approval-pending state rather than modifying data or downstream publication state.

The results demonstrate that the policy layer did not equate successful detection with unrestricted autonomous action. Although all 690 true failures were detected and classified correctly, only actions explicitly authorized by the runtime policy were initiated automatically.

The automatic-action initiation rate should not be interpreted as an automatic recovery rate. Of the 510 initiated actions, 150 produced deferred retry schedules without end-to-end confirmation of recovery. Only the 360 direct remediations were locally verifiable within the experimental environment.

## 4.4 Verified Recovery Performance
Verified recovery was achieved in 360 of the 690 true failure trials, producing an overall verified-recovery rate of 0.5217. The two-sided 95% confidence interval ranged from 0.4844 to 0.5588.

All 360 directly executed, locally verifiable remediation trials recovered successfully. The direct-action recovery rate was therefore 1.000, with a 95% confidence interval from 0.9894 to 1.0000.

The verified direct recoveries were distributed evenly across four failure categories:

* 90 duplicate-generation trials recovered through deduplication;
* 90 missing-value-spike trials recovered through invalid-record quarantine;
* 90 transformation-logic-error trials recovered through recomputation of derived totals; and
* 90 output-artifact-corruption trials recovered through artifact regeneration and checksum verification.

No verified recovery was recorded for the 150 retry-scheduling trials. These consisted of 90 source-failure trials and 60 above-threshold freshness-violation trials. The system initiated retry or refresh schedules, but the experimental environment did not include an external source capable of confirming successful subsequent retrieval.

No verified recovery was recorded for the 180 approval-controlled trials. These consisted of 90 schema-drift trials and 90 volume-anomaly trials. Their actions were intentionally withheld pending human approval.

The difference between the 52.17% overall recovery rate and the 100% direct-action recovery rate reflects the policy and verification boundaries of the experiment rather than failed execution of the implemented direct remediations. Figure 2 presents verified recovery by scenario.

## 4.5 Runtime Performance
Runtime was measured for all 780 experimental trials. The median end-to-end trial runtime was 10.61 milliseconds, the mean runtime was 12.61 milliseconds, and the 95th-percentile runtime was 26.67 milliseconds.

The difference between the median and mean indicates a right-skewed runtime distribution in which a smaller number of slower trials increased the average. Figure 3 presents the full runtime distribution across the combined dataframe and artifact experiment domains.

These measurements include the local execution of failure injection, detection, classification, policy evaluation, remediation handling, recovery verification, and result construction for each trial. They do not represent only detector latency.

The runtime results were obtained using the 10,000-row synthetic dataframe and 4,096-byte artifact under a local Windows 11 Python environment. They should therefore be interpreted as implementation-level latency measurements for the controlled experiment rather than as production throughput, distributed-system performance, or cloud-scale service-level guarantees.

No comparative runtime baseline was implemented. Consequently, the results establish the observed latency profile of the proposed system but do not demonstrate runtime superiority over alert-only, static-rule, or alternative self-healing approaches.

## 4.6 Scenario-Level Results
Scenario-level analysis showed that detection and classification performance remained perfect across all evaluated experiment domains, failure categories, severity settings, healthy controls, and freshness boundary controls.

Verified recovery differed by failure category because the system applied different policy and verification paths.

Duplicate-generation trials achieved verified recovery in all 90 cases. The remediation executor removed duplicate records using `order_id` as the uniqueness key, and verification confirmed that no duplicate identifiers remained.

Missing-value-spike trials achieved verified recovery in all 90 cases. Invalid rows were quarantined, valid rows were retained, and verification confirmed that the retained output contained no remaining null values in required fields.

Transformation-logic-error trials achieved verified recovery in all 90 cases. Derived totals were recomputed, and the remediated outputs passed the transformation-integrity detector.

Output-artifact-corruption trials achieved verified recovery in all 90 cases. The corrupted artifact was regenerated from a trusted source, and SHA-256 verification confirmed integrity after regeneration.

Source-failure trials produced retry schedules in all 90 cases but recorded no verified recovery because no external source interaction was executed after scheduling.

The 60 above-threshold freshness-violation trials also produced refresh schedules but recorded no verified recovery because successful source refresh could not be confirmed within the local experiment.

Schema-drift and volume-anomaly trials recorded no automatic execution or verified recovery. Each category contributed 90 trials and was intentionally routed to a human-approval state according to the runtime policy.

The 30 low-severity freshness boundary controls remained healthy under the configured threshold and therefore recorded successful non-failure handling rather than failure recovery. Scenario-level recovery values should therefore be interpreted in conjunction with each category’s authorized policy path and available verification mechanism, not as a single measure of detector quality.

## 4.7 Freshness Boundary-Control Analysis
The freshness scenarios produced two analytically distinct outcomes because the detector threshold was fixed at 60 minutes.

The low-severity freshness injection introduced a 30-minute delay. All 30 corresponding trials remained below the configured threshold and were therefore classified as non-failure boundary controls. They produced no false positives and were assigned `healthy_control` as the expected analysis class.

The medium- and high-severity freshness injections exceeded the configured threshold. These 60 trials were detected and classified correctly as freshness violations. In each case, the policy engine authorized a source-refresh retry schedule.

None of the 60 above-threshold freshness failures was counted as a verified recovery. The experiment confirmed that the system selected and initiated the configured retry action, but it did not simulate a subsequent successful refresh from an external source.

The initial analysis had treated all 90 injected freshness trials as true failures. Under that interpretation, the 30 sub-threshold trials appeared as false negatives. After comparing the injected delay with the predefined detector threshold, the low-severity condition was reclassified in the derived analysis as `freshness_boundary_control`.

This correction changed the derived detection and classification metrics from 96.15% to 100%, reduced the true-failure denominator from 720 to 690, and preserved all 780 raw trial records. No detector logic, threshold, injection value, or raw result was changed.

The boundary-control result demonstrates correct threshold behavior within the implemented design, but the post-execution nature of the analytical correction remains a limitation. Future evaluations should preregister expected outcomes for all sub-threshold, threshold-equal, and above-threshold conditions before running the experiment.

## 4.8 Evaluation Limitations
The reported results should be interpreted within the limits of the controlled experimental design.

First, the 100% detection and classification rates were obtained from deterministic synthetic failure injections whose mechanisms were known to the implementation. These results demonstrate correctness for the evaluated scenarios but do not establish equivalent performance for previously unseen, ambiguous, compound, or adversarial failures.

Second, the experiment evaluated only the policy-constrained implementation. Alert-only monitoring and static-rule remediation were not implemented as quantitative baselines. The study therefore cannot claim comparative improvements in accuracy, recovery, or runtime over those approaches.

Third, the 52.17% overall verified-recovery rate reflects both technical capability and deliberate policy restrictions. A total of 180 failures required human approval, and 150 failures produced retry schedules that could not be verified without an external source system. These outcomes should not be interpreted as failed execution of the direct remediation functions.

Fourth, all directly executed and locally verifiable remediations recovered successfully. However, these actions were evaluated using deterministic verification rules closely aligned with the injected conditions. Additional testing is required to assess partial recovery, unintended data loss, downstream semantic correctness, and recovery under mixed failure conditions.

Fifth, the runtime measurements were collected using a 10,000-row dataframe and a small controlled artifact in a local Windows environment. The results do not establish behavior under larger datasets, concurrent workloads, distributed processing, network latency, cloud infrastructure, or production orchestration systems.

Sixth, schema-drift and volume-anomaly scenarios ended at the human-approval boundary. The evaluation did not measure approval latency, operator decision quality, post-approval execution, or final recovery for those cases.

Seventh, the Dockerfile and remediation-registry artifacts were not part of the executed experiment. The reported evidence therefore does not validate containerized reproducibility or registry-enforced rollback, timeout, and validation controls.

Finally, the freshness boundary-control correction was made after inspecting the completed experiment. Although the correction followed the predefined 60-minute threshold and preserved all raw records, it was not preregistered. Future studies should define expected outcomes for below-threshold, threshold-equal, and above-threshold conditions before execution.
