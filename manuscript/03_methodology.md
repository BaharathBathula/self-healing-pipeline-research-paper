# 3. Methodology

## 3.1 Research Design

This study used a controlled, repeated-experiment design to evaluate a policy-constrained self-healing data pipeline under deterministic failure conditions. The objective was to measure whether the implemented system could detect operational failures, classify their root causes, apply policy restrictions, execute authorized remediation actions, and verify post-remediation recovery.

The evaluation examined one implemented policy-constrained system. Alert-only monitoring and static-rule remediation were identified during the research design as relevant conceptual baselines, but they were not implemented as experimental comparators. Accordingly, the reported results describe the behavior of the proposed system and do not establish comparative superiority over alternative approaches.

The experiment comprised 780 trials across two execution domains: dataframe-processing failures and output-artifact integrity failures. Each experimental scenario was repeated 30 times using deterministic seed progression from an initial random seed of 42. The final dataset contained 690 true failure trials, 60 healthy-control trials, and 30 sub-threshold freshness boundary-control trials. Raw trial records were preserved, while analysis-specific labels were derived separately to distinguish true failures from intentionally sub-threshold perturbations.

## 3.2 System Architecture

The implemented system followed a closed-loop control architecture consisting of detection, classification, policy evaluation, remediation execution, and post-action verification. A pipeline execution produced observable dataframe or artifact state. The detector evaluated this state using deterministic quality, integrity, freshness, volume, exception, and checksum signals. The classifier then mapped the detected condition to a predefined root-cause category.

The classified condition and detected severity were submitted to a YAML-configured policy engine. The policy engine determined the authorized action, whether the severity was permitted, and whether human approval was required. Actions requiring approval were not executed automatically. This control boundary was used for schema-drift and volume-anomaly scenarios, while supported low-risk remediations were authorized for automatic execution.

Authorized actions were executed by the remediation component. Implemented dataframe actions included duplicate removal, invalid-record quarantine, and recomputation of derived totals. Artifact recovery regenerated a corrupted output from a trusted source. Source-retry and freshness-refresh actions produced deterministic retry schedules rather than simulating successful external system recovery.

After execution, a verification stage evaluated the resulting state. Duplicate recovery required uniqueness of the order identifier, missing-value recovery required completeness of required fields in the retained output, transformation recovery required semantic consistency of derived totals, and artifact recovery required a successful SHA-256 checksum comparison. Retry scheduling was not treated as verified recovery because no external source system was available to confirm a successful retry.

The runtime control path loaded `policies/remediation_policies.yaml`. Although the repository also contained a remediation-registry file, that registry was not loaded by the executed system and therefore was not treated as part of the experimental control path.

## 3.3 Synthetic Dataset

The dataframe experiments used a synthetic order-processing dataset containing 10,000 records and 13 columns. The schema represented a simplified transactional pipeline with order, customer, product, timestamp, quantity, price, currency, exchange-rate, payment-status, region, source-system, and derived-total attributes.

The columns were:

- `order_id`
- `customer_id`
- `event_timestamp`
- `product_id`
- `quantity`
- `unit_price`
- `currency`
- `exchange_rate`
- `payment_status`
- `region`
- `source_system`
- `order_total_local`
- `order_total_usd`

The dataset was generated deterministically using the experiment seed and persisted in Parquet format. pandas was used for dataframe orchestration, failure injection, experiment execution, and result persistence. The reference processing pipeline loaded the Parquet dataset into pandas, registered the dataframe with an in-memory DuckDB connection, executed SQL-based validation and transformation logic, and wrote the validated output as Parquet using PyArrow.

The synthetic design provided a controlled baseline in which injected changes could be measured against known expected structure, record counts, timestamps, and derived values. It was intended for reproducible systems evaluation rather than for estimating production failure prevalence or real-world business impact.

## 3.4 Failure Model and Experimental Matrix
The failure model covered eight root-cause categories across dataframe and output-artifact domains: schema drift, missing-value spike, duplicate generation, freshness violation, volume anomaly, transformation logic error, source failure, and output-artifact corruption.

The dataframe domain evaluated seven failure categories. Each category was exercised at low, medium, and high injected-severity settings, with 30 repetitions per setting. This produced 630 injected dataframe trials. An additional 30 dataframe healthy-control trials were executed, resulting in 660 dataframe trials.

The artifact domain evaluated output-artifact corruption at three severity settings with 30 repetitions per setting, producing 90 corruption trials. An additional 30 artifact healthy-control trials were included, resulting in 120 artifact trials.

The complete experiment contained 780 trials: 660 dataframe-domain trials and 120 artifact-domain trials. The analysis classified 690 trials as true failures, 60 as healthy controls, and 30 as sub-threshold freshness boundary controls.

Failure injections were deterministic for a given experiment seed and repetition. Severity labels represented controlled perturbation levels within each scenario rather than a universal cross-scenario severity scale. Therefore, severity comparisons were interpreted within each failure category.

The study evaluated one implemented policy-constrained system. Alert-only monitoring and static-rule remediation were retained as conceptual reference points but were not implemented as quantitative experimental baselines.


## 3.5 Detection, Classification, and Policy Control
The detector used deterministic rules over observed dataframe state, baseline state, raised exceptions, transformation-integrity signals, and output-artifact checksums. The configured dataframe thresholds were a missing-value rate of 5%, a duplicate rate of 1%, a volume-deviation rate of 30%, and a freshness delay of 60 minutes.

Detected signals were converted into a structured result containing the failure-detected flag, severity, triggering signals, and supporting evidence. A deterministic classifier then assigned one of the supported root-cause categories. Conditions that did not map to a supported category were assigned to an unknown-failure fallback.

The policy engine loaded its runtime configuration from `policies/remediation_policies.yaml`. For each classified incident, it evaluated the root cause, detected severity, configured action, automatic-execution flag, permitted severities, and global approval constraints.

A permitted action was not necessarily executed automatically. Human approval was required when the root cause was explicitly listed as approval-controlled, when the policy was marked non-automatic, or when classification was unknown. In the reported experiment, schema-drift and volume-anomaly actions were intentionally withheld from automatic execution.

The runtime policy file governed the reported experiment. The separate remediation-registry file was not loaded by the executed control path and was therefore excluded from claims about policy enforcement, rollback, timeout, or validation behavior.

## 3.6 Remediation and Recovery Verification
The remediation executor operated on a copy of the observed dataframe or, for artifact recovery, on a trusted source artifact. It returned a structured result containing the selected action, execution status, resulting dataframe, quarantined records, retry schedule, human-approval requirement, and supporting evidence.

Supported direct dataframe remediations included removing duplicate records while retaining the first occurrence of each `order_id`, quarantining rows containing null values in required fields, and recomputing derived order totals from quantity and unit price. Output-artifact remediation regenerated the corrupted artifact from a trusted source.

Source-failure and freshness-remediation actions generated deterministic exponential-backoff retry schedules. These actions were classified as initiated automatic actions, but they were not counted as verified recovery because the experiment did not include an external source system capable of confirming that a scheduled retry later succeeded.

Actions requiring human approval returned a `pending_human_approval` status and were not executed. This behavior preserved the distinction between detecting a failure, selecting a policy response, and authorizing autonomous remediation.

Recovery verification was performed independently from action execution. Duplicate recovery required zero remaining duplicate `order_id` values. Missing-value recovery required zero remaining invalid records in the retained output, while quarantined records were recorded separately. Transformation recovery required the remediated dataframe to pass the transformation-integrity detector. Artifact recovery required the regenerated artifact to match the expected SHA-256 checksum.

Conditions requiring external or deferred verification returned an unverified result. Consequently, retry scheduling, pending human approval, and unsupported external recovery paths were not counted as successful recovery. The evaluation therefore reported automatic-action initiation and verified recovery as separate metrics.

## 3.7 Experimental Procedure and Reproducibility
The reported experiment was executed in a local Python virtual environment on Windows 11 using Python 3.12.2. The dependency set was captured in `requirements-lock.txt`, including pandas 3.0.3, DuckDB 1.5.3, PyArrow 24.0.0, NumPy 2.4.6, SciPy 1.17.1, Matplotlib 3.11.0, and pytest 9.1.0.

The experiment runner generated a deterministic 10,000-row synthetic dataframe using an initial random seed of 42. Each scenario was repeated 30 times. Dataframe and artifact trials were executed separately and then combined into one analysis dataset. The output-artifact scenarios used a 4,096-byte controlled artifact.

The experiment produced 660 dataframe trials and 120 artifact trials. Raw results were persisted in CSV and Parquet formats, while experiment metadata was stored separately in JSON. The metadata recorded execution timestamps, trial counts, Python and pandas versions, operating-system information, seed configuration, and the source-control commit associated with the run.

Raw experimental records were treated as immutable after execution. Subsequent corrections affected only derived analysis labels and summary calculations. In particular, the original low-severity freshness records retained their injected-failure labels, while the analysis layer assigned them a separate boundary-control condition because the injected delay did not exceed the configured detection threshold.

Derived outputs were generated through a dedicated analysis script and included overall summaries, scenario-level summaries, runtime statistics, detection and classification confusion matrices, and publication figures. This separation between raw trials and derived analysis reduced the risk of silently altering experimental evidence during post-processing.

The repository included a Dockerfile for reproducibility support, but the reported experiment was not executed inside a container. Docker was installed on the host system, but the Docker engine was unavailable during validation. Therefore, the reported environment is the native Windows Python virtual environment rather than a containerized runtime.

## 3.8 Evaluation Metrics and Statistical Analysis
The evaluation used separate metrics for detection, classification, policy-controlled execution, verified recovery, and runtime performance.

Detection accuracy was calculated across all 780 trials using the derived analysis condition as the expected detection state. True failures were expected to produce a detected-failure result, while healthy controls and freshness boundary controls were expected to remain non-failures. False positives represented non-failure trials incorrectly detected as failures, and false negatives represented true failure trials not detected.

Classification accuracy was also calculated across all 780 trials. For true failures, the expected class was the injected root-cause category. Healthy and boundary-control trials were assigned the expected analysis class `healthy_control`.

Automatic-action initiation was calculated only over the 690 true failure trials. A trial was counted as an initiated automatic action when the policy engine authorized an action and the remediation executor either completed a direct action or produced a retry schedule. Pending human-approval outcomes were not counted as initiated automatic actions.

Verified recovery across all failures used the 690 true failure trials as its denominator. A trial was counted as recovered only when a post-remediation verification rule confirmed that the failure condition had been removed. Retry schedules, pending human approval, and externally unverifiable actions were assigned a recovery value of zero.

Verified recovery for directly executed actions used only the 360 trials in which a direct, state-changing remediation was executed and could be evaluated locally. This metric excluded retry scheduling and approval-controlled actions.

Runtime performance was summarized using the median, mean, and 95th-percentile execution time in milliseconds. Because the study evaluated one implemented system rather than multiple comparative baselines, runtime analysis was descriptive and was not used to claim statistically significant superiority over another approach.

For proportion-based metrics, the analysis reported the observed rate together with a two-sided 95% confidence interval. Scenario-level summaries were grouped by experiment domain, injected failure type, injected severity, and derived analysis condition. All metrics were computed from preserved raw trial records through the derived-analysis pipeline.

## 3.9 Freshness Boundary-Control Treatment
The freshness detector used a configured threshold of 60 minutes. The low-severity freshness injection introduced a 30-minute delay, which remained below this threshold and therefore was not expected to trigger a freshness failure. The medium- and high-severity freshness injections exceeded the threshold and remained classified as true failure scenarios.

The raw experiment records originally retained `freshness_violation` as the injected scenario label for all three severity levels. During post-execution analysis, the low-severity condition was identified as a threshold-boundary case rather than a detector false negative. The 30 corresponding trials were therefore assigned the derived analysis condition `freshness_boundary_control`, with `healthy_control` as the expected analysis class.

This correction was applied only within the derived-analysis layer. No raw trial records, detector thresholds, injected timestamps, classifications, or execution outcomes were modified. The original injected failure type and severity remained available for traceability.

The boundary-control trials were included in the total trial count and in the non-failure denominator used to calculate false-positive performance. They were excluded from the true-failure denominator used for automatic-action and verified-recovery metrics.

This analytical treatment was introduced after inspection of the completed experiment rather than being preregistered. It is reported explicitly to distinguish a correction of the expected condition from removal of an unfavorable experimental result. The correction reflects the system’s predefined 60-minute freshness threshold: a 30-minute delay cannot consistently be described as a detector miss when the configured policy defines it as sub-threshold.

## 3.10 Threats to Validity
Several limitations affect the interpretation and generalizability of the evaluation.

First, the study used a synthetic 10,000-row order dataset rather than production data. This enabled deterministic failure injection and repeatable validation, but it did not reproduce the full diversity, scale, governance constraints, or operational dependencies of enterprise data platforms.

Second, the experiment evaluated one implemented policy-constrained system. Alert-only monitoring and static-rule remediation were not implemented as experimental baselines. The results therefore characterize the proposed system’s behavior but do not demonstrate superiority over alternative monitoring or remediation approaches.

Third, the failure scenarios were injected deterministically using predefined mechanisms and severity levels. Real incidents may combine multiple simultaneous causes, evolve over time, exhibit ambiguous signals, or produce partial failures that do not match a single predefined category. The evaluation did not include compound or adversarial failure scenarios.

Fourth, source-failure and freshness-remediation outcomes were represented by scheduled retry plans rather than interaction with an external source system. These trials demonstrate policy selection and action initiation, but they do not establish successful end-to-end recovery from a real upstream dependency.

Fifth, schema-drift and volume-anomaly actions were intentionally held for human approval. This behavior validates the policy boundary, but the experiment did not model the subsequent approval decision, operator response time, or post-approval remediation outcome.

Sixth, runtime measurements were collected in a local Windows 11 Python virtual environment. The reported latency values reflect this implementation, hardware context, dataset size, and local execution model. They should not be interpreted as production throughput guarantees or as container, cloud, distributed, or large-scale performance results.

Seventh, the repository contained a Dockerfile and a separate remediation-registry artifact, but the reported experiment did not execute inside Docker and did not load the remediation registry at runtime. Claims about container reproducibility, registry-enforced rollback, registry-defined timeouts, or registry-defined validation checks are therefore outside the scope of the reported evidence.

Finally, the low-severity freshness condition was reclassified as a boundary control after the completed experiment was inspected. The correction preserved the raw records and followed the predefined 60-minute detector threshold, but it was not preregistered. This post-execution analytical decision is disclosed because it may introduce researcher judgment into the interpretation of the final metrics.
