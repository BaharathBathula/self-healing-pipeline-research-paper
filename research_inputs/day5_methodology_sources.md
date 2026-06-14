# Day 5 Methodology Source Extraction

Documents 04–07 extracted for methodology and experimental-results drafting.

# 04_System_Architecture_and_Experimental_Boundary

## System Architecture and Experimental Boundary

### 1. Purpose

This document defines the technical architecture that will be implemented and evaluated in the research study.

The system is a control plane placed above a data-pipeline execution environment. It observes pipeline behavior, detects failures, classifies probable root causes, selects permitted remediation actions, validates recovery, and records the complete incident lifecycle.

The research will evaluate the control-plane logic rather than attempting to build a new orchestration platform.

## 2. High-Level Architecture

The proposed system consists of nine components:

Pipeline execution environment

Telemetry collector

Failure detector

Root-cause classifier

Remediation registry

Policy evaluation engine

Remediation executor

Recovery validator and rollback manager

Incident evidence store

### Control Flow

Pipeline Execution → Telemetry Collection → Failure Detection → Root-Cause Classification → Remediation Candidate Selection → Policy Evaluation → Execute or Escalate → Validate Recovery → Roll Back if Validation Fails → Record Final Evidence

## 3. Pipeline Execution Environment

The execution environment will contain reproducible data pipelines that support controlled failure injection.

The pipeline should include:

Source-data ingestion

Schema validation

Data transformation

Data-quality validation

Output writing

Downstream verification

The pipeline environment must produce:

Execution status

Start and completion timestamps

Input and output record counts

Schema metadata

Data-quality measurements

Error messages

Resource and retry information

Output-validation status

The experiment must run locally or in a reproducible containerized environment.

Cloud deployment may be added later, but cloud infrastructure is not required to establish the research contribution.

## 4. Telemetry Collector

The telemetry collector will gather signals from every pipeline execution.

### Operational Signals

Job status

Task status

Execution duration

Retry count

Error code

Exception message

Resource utilization, where available

### Data Signals

Input record count

Output record count

Null-value rate

Duplicate rate

Schema fingerprint

Data-freshness delay

Distribution or volume deviation

Validation-rule failures

### Telemetry Requirement

Each execution must generate a structured telemetry record using a consistent schema.

The control plane must make decisions from recorded telemetry rather than manually entered incident descriptions.

## 5. Failure Detector

The failure detector determines whether a pipeline execution is healthy, degraded, or failed.

The detector will support:

Explicit execution failures

Schema-change detection

Missing-data anomalies

Duplicate anomalies

Freshness violations

Unexpected volume changes

Output-quality failures

Partial-write detection

The detector must generate:

Incident identifier

Detection timestamp

Detected failure category

Triggering signals

Severity

Detection confidence

## 6. Root-Cause Classifier

The classifier will map observed telemetry to a probable root cause.

Initial root-cause classes will include:

Schema drift

Missing-data spike

Duplicate-data generation

Data-freshness delay

Unexpected volume change

Transformation-logic failure

Source-system failure

Partial or corrupted output

Unknown failure

The first implementation may use deterministic or probabilistic classification logic.

A machine-learning classifier is not mandatory unless it provides a valid experimental advantage.

The research contribution is the complete control architecture, not the unnecessary use of machine learning.

The classifier must return:

Predicted root cause

Confidence score

Alternative candidate causes, where applicable

Evidence supporting the classification

## 7. Remediation Registry

The remediation registry contains tested recovery actions associated with known failure classes.

Example remediation actions include:

Retry failed ingestion

Restart failed task

Reprocess from checkpoint

Restore expected schema mapping

Quarantine invalid records

Remove duplicate output and replay

Switch to approved fallback source

Roll back transformation version

Restore last valid output

Escalate to human operator

Every remediation action must define:

Applicable failure categories

Required preconditions

Permitted resources

Maximum blast radius

Rollback action

Validation checks

Approval requirement

Execution timeout

## 8. Policy Evaluation Engine

The policy engine determines whether a proposed remediation may execute automatically.

### Policy Inputs

Failure category

Classification confidence

Incident severity

Dataset sensitivity

Number of affected records

Number of downstream consumers

Remediation risk

Rollback availability

Historical success rate

Whether the failure type is known

### Example Policy Rules

Automatic execution is permitted only when:

Root-cause confidence is above the defined threshold

The remediation is registered for the predicted failure

The affected resource is explicitly authorized

The expected blast radius is below the allowed limit

A tested rollback exists

The dataset is not classified as requiring manual approval

No conflicting failure diagnosis exists

Otherwise, the incident must be escalated.

### Policy Outcomes

Approved for automatic execution

Denied

Human approval required

No valid remediation available

## 9. Remediation Executor

The executor performs the approved recovery action.

It must:

Execute only approved actions

Record every command or operation

Enforce timeout limits

Prevent access to unauthorized resources

Capture execution output

Stop when a safety condition is violated

Return a clear execution result

An action completing without an error does not mean recovery succeeded.

Recovery success is determined only by the validation component.

## 10. Recovery Validator

The validator determines whether the system has actually recovered.

Validation must confirm:

Pipeline execution succeeds

Expected record counts are restored

Schema validation passes

Quality checks pass

Freshness requirements are met

Duplicate thresholds are satisfied

Output integrity is preserved

Downstream verification passes

No new failure was introduced

### Validation Outcomes

Recovery successful

Recovery incomplete

Recovery failed

Recovery created a new incident

## 11. Rollback Manager

Rollback is triggered when:

The remediation action fails

Validation fails

Output quality decreases

An unauthorized modification is detected

The incident blast radius increases

The action exceeds its execution timeout

The rollback manager must:

Restore the previous valid state

Record rollback actions

Validate the restored state

Escalate the incident when rollback fails

## 12. Incident Evidence Store

Every experimental incident must produce a structured evidence record.

The record must contain:

Incident ID

Experiment ID

Failure-injection configuration

Pipeline version

Dataset version

Detection timestamp

Triggering telemetry

Predicted root cause

Confidence score

Selected remediation

Policy decision

Execution details

Validation results

Rollback details

Final resolution

Total detection and recovery time

Evidence records must not be manually rewritten after an experiment.

Corrections must be recorded as new versions or annotations.

## 13. Comparison Systems

### Baseline A — Alert-Only Monitoring

This baseline will:

Detect explicit or configured failures

Produce an alert

Require manual diagnosis

Require manual remediation

Require manual recovery validation

### Baseline B — Static Rule-Based Automation

This baseline will:

Match a detected signal to a predefined action

Execute the action automatically

Not evaluate contextual risk policies

Have limited or no confidence-based escalation

Primarily evaluate job completion

### Proposed System — Policy-Constrained Self-Healing Control Plane

This system will:

Use multiple operational and data signals

Classify probable root causes

Evaluate remediation risk and policy

Execute only authorized actions

Escalate uncertain or high-risk incidents

Validate data correctness after recovery

Roll back unsuccessful remediation

Record the complete decision lifecycle

The baselines must use the same pipeline, datasets, failure scenarios, and computing environment.

## 14. Experimental Boundary

The research will evaluate:

Failure detection

Root-cause classification

Remediation selection

Policy enforcement

Automated execution

Human escalation decisions

Recovery validation

Rollback behavior

Incident auditability

The research will not evaluate:

General-purpose workflow-scheduler performance

Large-scale cloud cost optimization

Model drift

Fraud-model accuracy

Organizational maturity

Human productivity across real enterprises

Every possible data-pipeline technology

Fully autonomous infrastructure management

## 15. Implementation Principle

The first version must remain technically simple enough to reproduce.

A smaller system with:

Clear component boundaries

Verified measurements

Repeatable experiments

Public implementation

Honest limitations

is scientifically stronger than a complex architecture that cannot be reproduced or validated.

---

# 05_Failure_Injection_and_Experiment_Matrix

## Failure Injection and Experiment Matrix

### 1. Purpose

This document defines the controlled failure scenarios that will be used to evaluate the proposed self-healing data-pipeline control plane.

Every failure must be:

Reproducible

Programmatically injectable

Detectable through recorded telemetry

Associated with a known ground-truth cause

Recoverable through a documented action

Repeatable across all comparison systems

The same dataset, pipeline version, computing environment, and failure configuration must be used for each comparison approach.

## 2. Experimental Approaches

Each failure scenario will be tested against three approaches.

### Approach A — Alert-Only Monitoring

Detects a failure or threshold violation

Generates an alert

Requires manual diagnosis

Requires manual remediation

Uses manual recovery validation

### Approach B — Static Rule-Based Automation

Matches an observed signal to a predefined action

Executes remediation automatically

Does not evaluate contextual risk

Does not use confidence-based escalation

Primarily evaluates whether the job completes successfully

### Approach C — Policy-Constrained Self-Healing

Uses multiple operational and data signals

Classifies the probable root cause

Selects a registered remediation

Evaluates policy and operational risk

Executes or escalates

Validates output correctness

Rolls back failed remediation

Records the full incident lifecycle

## 3. Failure Scenario F1 — Schema Drift

### Failure Injection

Modify the incoming dataset by:

Renaming a required column

Removing a required column

Changing a numeric column to a string

Adding an unexpected field

### Expected Signals

Schema fingerprint mismatch

Missing required field

Type-validation failure

Transformation exception

Output record-count reduction

### Ground-Truth Root Cause

Schema drift in the upstream source.

### Approved Remediation

Apply an approved schema mapping

Quarantine incompatible records

Reprocess the affected batch

### Unsafe Remediation Example

Automatically dropping the changed field and continuing without verifying downstream requirements.

### Recovery Validation

Required schema restored

All expected records processed

No required values lost

Downstream validation passes

## 4. Failure Scenario F2 — Missing-Value Spike

### Failure Injection

Increase null values in a required field beyond the permitted threshold.

Example:

Normal null rate: below 1%

Injected null rate: 10%, 25%, and 50%

### Expected Signals

Completeness score decreases

Null-rate threshold violation

Quality SLA failure

Output-quality failure

### Ground-Truth Root Cause

Upstream field-population failure.

### Approved Remediation

Quarantine invalid records

Use an approved fallback field where permitted

Reprocess valid records

Escalate when the required value cannot be safely reconstructed

### Unsafe Remediation Example

Replacing all missing values with zero or an arbitrary default.

### Recovery Validation

Invalid records isolated

Valid records preserved

No unsupported imputation performed

Completeness and validity checks pass

## 5. Failure Scenario F3 — Duplicate-Record Generation

### Failure Injection

Insert duplicate records or replay an already processed input batch.

### Expected Signals

Duplicate-rate increase

Primary-key collision

Input-output count inconsistency

Uniqueness SLA failure

### Ground-Truth Root Cause

Non-idempotent replay or repeated ingestion.

### Approved Remediation

Identify duplicate keys

Remove duplicate output

Restore the last valid checkpoint

Reprocess using idempotent logic

### Unsafe Remediation Example

Deleting all records sharing a duplicate key without preserving the valid original.

### Recovery Validation

Exactly one valid record remains per business key

Record counts match expected values

No legitimate records are removed

Output checksum or reconciliation passes

## 6. Failure Scenario F4 — Data-Freshness Violation

### Failure Injection

Delay source-data arrival or process an outdated input file.

### Expected Signals

Event-time delay

Processing-time delay

Freshness SLA violation

Stale partition detected

### Ground-Truth Root Cause

Delayed or stale upstream data.

### Approved Remediation

Retry approved source retrieval

Switch to an approved fallback source

Hold downstream publication

Escalate when no current source is available

### Unsafe Remediation Example

Publishing stale data as current without a warning or hold.

### Recovery Validation

Data timestamp falls within the freshness SLA

Correct partition is processed

Downstream publication uses the latest valid data

No stale data is certified

## 7. Failure Scenario F5 — Unexpected Volume Change

### Failure Injection

Change the input volume relative to the expected baseline.

Test levels:

50% decrease

80% decrease

200% increase

500% increase

### Expected Signals

Input-volume anomaly

Output-volume anomaly

Throughput deviation

Resource-pressure signal

Reconciliation failure

### Ground-Truth Root Cause

Upstream data loss, repeated extraction, or abnormal source volume.

### Approved Remediation

Pause publication

Compare against source control totals

Retry extraction where appropriate

Scale resources only when the increase is legitimate

Escalate unexplained changes

### Unsafe Remediation Example

Automatically accepting or scaling for a 500% increase without checking whether the data was duplicated.

### Recovery Validation

Input volume reconciled with the source

Output volume matches expected transformation behavior

No missing or repeated records remain

Resource use returns to acceptable limits

## 8. Failure Scenario F6 — Transformation-Logic Failure

### Failure Injection

Introduce an incorrect transformation such as:

Wrong currency conversion

Sign inversion

Incorrect join condition

Incorrect filter boundary

Invalid unit conversion

### Expected Signals

Semantic validation failure

Distribution deviation

Reconciliation mismatch

Business-rule violation

Output anomaly despite successful job completion

### Ground-Truth Root Cause

Defective transformation logic.

### Approved Remediation

Roll back to the last validated transformation version

Reprocess affected data

Quarantine outputs from the defective version

### Unsafe Remediation Example

Retrying the same defective transformation repeatedly.

### Recovery Validation

Known-answer tests pass

Business-rule checks pass

Output reconciles with expected values

Defective output is removed

## 9. Failure Scenario F7 — Source-System Failure

### Failure Injection

Simulate:

API timeout

Connection refusal

Authentication failure

Partial response

Rate-limit response

### Expected Signals

Connection error

Timeout

HTTP error code

Partial input count

Retry exhaustion

### Ground-Truth Root Cause

Source-system unavailability or access failure.

### Approved Remediation

Retry with bounded exponential backoff

Use an approved fallback source

Resume from checkpoint

Escalate authentication or authorization failures

### Unsafe Remediation Example

Retrying indefinitely or switching to an unapproved source.

### Recovery Validation

Complete source data retrieved

No duplicated ingestion

Checkpoint continuity preserved

Authentication and access policies satisfied

## 10. Failure Scenario F8 — Partial or Corrupted Output

### Failure Injection

Simulate:

Partial file write

Truncated output

Invalid checksum

Output partition missing

Corrupted serialization

### Expected Signals

Input-output count mismatch

Missing partition

Checksum mismatch

File-read failure

Downstream validation failure

### Ground-Truth Root Cause

Incomplete or corrupted output write.

### Approved Remediation

Remove invalid output

Restore the previous valid output

Reprocess from the last safe checkpoint

Perform atomic replacement after validation

### Unsafe Remediation Example

Marking the job successful because an output file exists.

### Recovery Validation

Output checksum passes

All expected partitions exist

Record counts reconcile

Downstream read succeeds

No corrupted file remains accessible

## 11. Unknown-Failure Scenario

At least one scenario must be deliberately excluded from the remediation registry.

The proposed system must:

Detect abnormal behavior

Assign low classification confidence or unknown status

Refuse automatic remediation

Escalate to a human operator

Preserve all incident evidence

The static automation baseline may apply an incorrect rule, allowing remediation-safety differences to be measured.

## 12. Trial Structure

Each failure category will be executed at multiple severity levels.

Minimum target:

8 failure categories

3 severity levels where applicable

10 repeated trials per approach and configuration

The final number of trials may be adjusted after pilot testing, but the decision must be documented before final experiments begin.

## 13. Required Measurements Per Trial

Every trial must record:

Experiment ID

Approach

Failure category

Failure severity

Injection timestamp

Detection timestamp

Detection result

Predicted root cause

Classification confidence

Selected remediation

Policy outcome

Remediation start time

Remediation end time

Validation result

Rollback result

Human escalation result

Final recovery status

False-remediation status

Total MTTD

Total MTTR

SLA violation

Notes on anomalies

## 14. Fairness Rule

All approaches must receive:

The same input data

The same injected failure

The same severity

The same resource limits

The same pipeline implementation

The same recovery-success definition

No approach may receive easier failure scenarios or more favorable validation criteria.

## 15. Final Integrity Rule

A trial must not be deleted because:

The proposed system fails

A baseline performs better

The result is unexpected

The result weakens a hypothesis

Invalid trials may be excluded only when a documented infrastructure or instrumentation error makes the measurement unusable.

The exclusion reason must be preserved in the experiment log.

---

# 06_Experiment_Data_Schema

## Experiment Data Schema

### 1. Purpose

This document defines the structured records required for every experiment.

All trial results must be captured consistently so that:

Results can be reproduced

Approaches can be compared fairly

Statistical analysis can be performed

Failed trials remain traceable

Evidence can be audited

Results are not manually rewritten after execution

The final implementation may store these records in CSV, JSON, Parquet, or a relational database. The same logical schema must be maintained regardless of storage format.

## 2. Experiment Run Record

Each experiment trial must create one experiment-run record.

### Identity Fields

## 3. Experimental Configuration Fields

## 4. Failure-Injection Record

Every trial must preserve how the failure was introduced.

A failed failure injection does not count as a valid experiment trial.

It must be preserved as an invalid trial with the reason documented.

## 5. Telemetry Record

Each pipeline execution must produce telemetry.

### Operational Telemetry

### Data Telemetry

## 6. Detection Record

## 7. Root-Cause Classification Record

## 8. Remediation Decision Record

## 9. Remediation Execution Record

## 10. Recovery Validation Record

Recovery is successful only when all mandatory validation conditions pass.

## 11. Rollback Record

## 12. Final Outcome Record

## 13. Trial Validity Record

Every experiment must be labeled as valid or invalid.

A trial may not be excluded merely because the proposed system performed poorly.

## 14. Controlled Vocabulary

The implementation must use consistent values.

### Approach

alert_only

static_rule

policy_constrained

### Failure Category

schema_drift

missing_value_spike

duplicate_generation

freshness_violation

volume_anomaly

transformation_failure

source_failure

corrupted_output

unknown_failure

healthy_control

### Severity

low

medium

high

### Final Status

recovered

escalated

unresolved

failed

## 15. Healthy Control Runs

The experiment must include pipeline runs where no failure is injected.

Healthy control runs are required to measure:

False-positive detection

Unnecessary remediation

Incorrect escalation

Normal execution latency

Normal data-quality variation

Each approach must receive the same number of healthy control runs.

## 16. Data Preservation Rule

Raw experiment records must be immutable.

Any correction must:

Preserve the original record

Create a corrected version

Record who or what made the correction

Record the reason

Record the correction timestamp

Summary tables and charts must always be reproducible from the preserved raw records.

## 17. Publication Requirement

The final paper must describe:

The experiment schema

The meaning of each primary outcome

Trial exclusion rules

Data-preservation procedures

How raw records were converted into reported metrics

Where legally and technically possible, anonymized raw experiment records must be included in the supporting repository.

## Extracted Table 1

| Field | Type | Description |
| --- | --- | --- |
| experiment_id | String | Unique identifier for the trial |
| experiment_batch_id | String | Identifier grouping related trials |
| run_number | Integer | Repetition number |
| timestamp_started | Datetime | Trial start time |
| timestamp_completed | Datetime | Trial completion time |
| experiment_version | String | Version of experiment configuration |
| pipeline_version | String | Pipeline code version |
| dataset_version | String | Dataset version |
| control_plane_version | String | Self-healing system version |

## Extracted Table 2

| Field | Type | Description |
| --- | --- | --- |
| approach | Category | alert_only, static_rule, or policy_constrained |
| failure_category | Category | Ground-truth injected failure |
| failure_severity | Category | low, medium, or high |
| failure_configuration | JSON | Exact injection parameters |
| random_seed | Integer | Seed used for reproducibility |
| environment_id | String | Runtime environment identifier |
| resource_limit_cpu | Numeric | CPU limit |
| resource_limit_memory | Numeric | Memory limit |
| timeout_seconds | Numeric | Maximum permitted execution time |

## Extracted Table 3

| Field | Type | Description |
| --- | --- | --- |
| injection_id | String | Unique failure-injection identifier |
| injection_timestamp | Datetime | Time failure was introduced |
| injection_method | String | Function or process used |
| affected_component | String | Pipeline component affected |
| affected_dataset | String | Dataset or partition affected |
| affected_record_count | Integer | Number of affected records |
| expected_failure_category | Category | Ground-truth failure class |
| expected_failure_effect | String | Expected operational or data impact |
| injection_success | Boolean | Whether the intended failure was introduced |
| injection_validation | String | Evidence confirming injection |

## Extracted Table 4

| Field | Type | Description |
| --- | --- | --- |
| pipeline_status | Category | running, successful, degraded, or failed |
| task_statuses | JSON | Status of individual tasks |
| execution_duration_ms | Numeric | Total runtime |
| retry_count | Integer | Number of retries |
| exception_type | String | Exception class |
| exception_message | String | Exception message |
| cpu_utilization | Numeric | CPU utilization where available |
| memory_utilization | Numeric | Memory utilization where available |

## Extracted Table 5

| Field | Type | Description |
| --- | --- | --- |
| input_record_count | Integer | Number of input records |
| output_record_count | Integer | Number of output records |
| null_rate | Numeric | Fraction of null values |
| duplicate_rate | Numeric | Fraction of duplicate records |
| schema_fingerprint | String | Hash or identifier of schema |
| freshness_delay_seconds | Numeric | Data delay relative to SLA |
| volume_deviation_percent | Numeric | Deviation from expected volume |
| checksum_valid | Boolean | Output checksum result |
| quality_score | Numeric | Composite data-quality score |
| business_rule_failures | Integer | Failed semantic validation rules |

## Extracted Table 6

| Field | Type | Description |
| --- | --- | --- |
| detection_timestamp | Datetime | Time failure was detected |
| failure_detected | Boolean | Whether the system detected the incident |
| detected_failure_category | Category | Detected incident category |
| detection_confidence | Numeric | Confidence between 0 and 1 |
| triggering_signals | JSON | Signals responsible for detection |
| severity_assigned | Category | Assigned severity |
| detection_latency_ms | Numeric | Time from injection to detection |
| false_positive | Boolean | Healthy run incorrectly flagged |
| false_negative | Boolean | Injected failure not detected |

## Extracted Table 7

| Field | Type | Description |
| --- | --- | --- |
| predicted_root_cause | Category | Predicted cause |
| ground_truth_root_cause | Category | Injected cause |
| classification_correct | Boolean | Whether prediction matches ground truth |
| classification_confidence | Numeric | Confidence between 0 and 1 |
| alternative_causes | JSON | Other candidate causes |
| classification_evidence | JSON | Signals supporting prediction |
| unknown_classification | Boolean | Whether cause was marked unknown |

## Extracted Table 8

| Field | Type | Description |
| --- | --- | --- |
| remediation_candidate | String | Proposed recovery action |
| remediation_registry_match | Boolean | Whether action exists in registry |
| policy_decision | Category | approved, denied, approval_required, or unavailable |
| policy_rules_evaluated | JSON | Policies checked |
| policy_rules_failed | JSON | Policies not satisfied |
| risk_score | Numeric | Estimated remediation risk |
| predicted_blast_radius | Numeric | Estimated affected scope |
| rollback_available | Boolean | Whether rollback exists |
| human_escalation_required | Boolean | Whether manual intervention is required |
| decision_timestamp | Datetime | Time decision was made |

## Extracted Table 9

| Field | Type | Description |
| --- | --- | --- |
| remediation_started | Datetime | Action start time |
| remediation_completed | Datetime | Action completion time |
| remediation_executed | Boolean | Whether action was executed |
| remediation_action | String | Action performed |
| remediation_result | Category | successful, failed, timed_out, or blocked |
| execution_output | String | Captured output |
| unauthorized_change_detected | Boolean | Whether action exceeded permissions |
| execution_duration_ms | Numeric | Action duration |
| records_modified | Integer | Number of records changed |
| resources_modified | JSON | Resources affected |

## Extracted Table 10

| Field | Type | Description |
| --- | --- | --- |
| validation_timestamp | Datetime | Validation time |
| pipeline_execution_valid | Boolean | Pipeline executes successfully |
| schema_valid | Boolean | Schema checks pass |
| record_count_valid | Boolean | Counts reconcile |
| data_quality_valid | Boolean | Quality checks pass |
| freshness_valid | Boolean | Freshness SLA passes |
| duplicate_check_valid | Boolean | Duplicate limit passes |
| checksum_valid_after_recovery | Boolean | Output integrity passes |
| downstream_validation_valid | Boolean | Downstream checks pass |
| new_incident_created | Boolean | Remediation introduced another failure |
| recovery_validated | Boolean | Overall recovery result |

## Extracted Table 11

| Field | Type | Description |
| --- | --- | --- |
| rollback_required | Boolean | Whether rollback was triggered |
| rollback_started | Datetime | Rollback start time |
| rollback_completed | Datetime | Rollback completion time |
| rollback_action | String | Rollback performed |
| rollback_successful | Boolean | Whether previous valid state was restored |
| restored_version | String | Restored pipeline or data version |
| post_rollback_validation | Boolean | Whether restored state passed validation |
| rollback_failure_reason | String | Reason rollback failed |

## Extracted Table 12

| Field | Type | Description |
| --- | --- | --- |
| final_status | Category | recovered, escalated, unresolved, or failed |
| successful_recovery | Boolean | Validated recovery result |
| unsafe_remediation | Boolean | Whether an unsafe action occurred |
| human_intervention_used | Boolean | Whether human action was required |
| SLA_violation | Boolean | Whether recovery exceeded SLA |
| MTTD_ms | Numeric | Mean-time-to-detection value for trial |
| MTTR_ms | Numeric | Mean-time-to-recovery value for trial |
| total_incident_duration_ms | Numeric | Injection to final resolution |
| notes | String | Additional observations |

## Extracted Table 13

| Field | Type | Description |
| --- | --- | --- |
| trial_valid | Boolean | Whether trial can be analyzed |
| invalid_reason | String | Reason trial is invalid |
| instrumentation_failure | Boolean | Whether measurement failed |
| infrastructure_failure | Boolean | Whether unrelated environment failure occurred |
| failure_injection_valid | Boolean | Whether injection worked correctly |
| excluded_from_analysis | Boolean | Whether excluded from final statistics |
| exclusion_approved_before_analysis | Boolean | Whether exclusion follows predefined rules |

---

# 07_Technical_Feasibility_and_Implementation_Stack

## Technical Feasibility and Implementation Stack

### 1. Feasibility Verdict

The proposed research system is technically feasible within the defined research scope.

The study does not require:

A production cloud account

Kubernetes

Apache Kafka

Apache Airflow

A distributed Spark cluster

Large language models

A machine-learning root-cause classifier

Proprietary enterprise datasets

Access to confidential production incidents

The system can be implemented as a reproducible local research prototype using Python, DuckDB, versioned files, containerization, and structured experiment records.

The objective is not to reproduce the scale of a Fortune 500 data platform. The objective is to demonstrate and measure the behavior of the proposed control-plane architecture under controlled pipeline failures.

## 2. Locked Technology Stack

### Programming Language

Python 3.12

Python will be used for:

Pipeline execution

Synthetic-data generation

Failure injection

Telemetry collection

Failure detection

Root-cause classification

Policy evaluation

Remediation execution

Recovery validation

Experiment orchestration

Statistical analysis

The exact Python version must be recorded in the repository.

### Data Processing Engine

DuckDB

DuckDB will be used for:

Reading input files

Executing transformation queries

Writing processed outputs

Calculating validation metrics

Comparing source and output records

Querying experiment records

Reproducing analytical results

The system will use local execution so that reviewers can reproduce the experiments without creating cloud infrastructure.

### Data Formats

The project will use:

CSV for simple source-failure and schema-drift tests

Parquet for validated pipeline inputs and outputs

JSON or JSON Lines for telemetry and incident evidence

YAML for remediation and policy configuration

CSV or Parquet for final experiment-analysis datasets

Raw experiment evidence will be preserved separately from derived summary data.

### Testing Framework

pytest

pytest will be used to:

Test each pipeline component

Parameterize failure scenarios

Test severity configurations

Verify remediation behavior

Verify policy decisions

Validate rollback behavior

Execute healthy control runs

Prevent regression during implementation

Tests are supporting verification artifacts. They do not replace the full experimental trial records.

### Reproducible Runtime

Docker

Docker will be used to preserve:

Python version

Dependency versions

File-system structure

Environment variables

Execution commands

Runtime configuration

The completed project must be executable through a documented container command.

A non-containerized local execution method may also be provided, but the containerized method will be the primary reproducibility path.

### Version Control

Git

Every material research change must be committed.

Important experiment milestones must be tagged, including:

Initial pipeline implementation

Completed failure-injection system

Pilot experiment version

Frozen final experiment version

Submitted-paper artifact version

Final experiment code must not be modified after data collection without creating a new version and documenting the reason.

### Analysis Stack

The analysis environment may use:

pandas for tabular manipulation

NumPy for numerical operations

SciPy for statistical tests

Matplotlib for publication figures

DuckDB SQL for aggregations and validation

All reported tables and figures must be generated from scripts.

No publication table or figure may depend solely on manual spreadsheet calculations.

## 3. Reference Pipeline

The experiment will use a synthetic order-processing pipeline.

### Input Dataset

Each record will contain fields such as:

order_id

customer_id

event_timestamp

product_id

quantity

unit_price

currency

exchange_rate

payment_status

region

source_system

### Pipeline Stages

#### Stage 1 — Source ingestion

Read a versioned source dataset.

#### Stage 2 — Schema validation

Verify:

Required columns

Data types

Permitted values

Primary-key presence

#### Stage 3 — Data-quality validation

Calculate:

Completeness

Uniqueness

Validity

Freshness

Volume deviation

#### Stage 4 — Transformation

Calculate standardized values such as:

normalized currency amount

order total

regional aggregation

valid transaction status

#### Stage 5 — Output writing

Write validated records using an atomic or staged output process.

#### Stage 6 — Downstream verification

Verify:

Record reconciliation

Expected partitions

Checksums

Business-rule totals

Output readability

## 4. Why a Synthetic Dataset Is Appropriate

A synthetic dataset is acceptable because the research evaluates pipeline reliability and recovery behavior rather than customer behavior or business forecasting.

Synthetic data allows the study to:

Preserve exact failure ground truth

Avoid privacy and confidentiality restrictions

Reproduce identical failures

Control dataset size

Create known-answer validations

Publish the full dataset

Avoid unverifiable enterprise claims

The final paper must clearly state that the study uses a controlled synthetic benchmark.

It must not imply that the experiments were conducted using a real company’s production data.

## 5. Failure-Injection Implementation

Each failure category will have a dedicated injection function.

Example structure:

inject_schema_drift()

inject_missing_values()

inject_duplicates()

inject_freshness_delay()

inject_volume_anomaly()

inject_transformation_defect()

inject_source_failure()

inject_corrupted_output()

inject_unknown_failure()

Each function must:

Accept configuration parameters

Use a recorded random seed where randomness applies

Preserve the original source data

Produce evidence that the failure was successfully injected

Record the exact affected records or component

Return the expected ground-truth failure class

## 6. Root-Cause Classification Approach

The initial implementation will use an evidence-weighted deterministic classifier.

A machine-learning classifier will not be used unless later evidence demonstrates that it is necessary.

The classifier will assign weighted evidence to each potential root cause.

Example:

Schema mismatch strongly supports schema drift

Null-rate spike supports missing-data failure

Duplicate-rate spike supports replay or idempotency failure

Freshness delay supports stale-source failure

Checksum mismatch supports corrupted output

Successful job status combined with failed semantic checks supports transformation failure

The classifier will output:

Predicted root cause

Confidence score

Supporting evidence

Alternative candidate causes

Unknown classification when evidence is insufficient

This design is easier to explain, audit, test, and reproduce than an unnecessarily opaque machine-learning model.

## 7. Policy Engine Design

Policies will be expressed in version-controlled YAML configuration.

Example policy properties:

minimum classification confidence

permitted remediation actions

protected datasets

maximum affected-record count

maximum downstream-consumer count

rollback requirement

manual-approval requirement

permitted failure severities

execution timeout

The Python policy evaluator will return one of four outcomes:

approved

denied

approval_required

unavailable

The study evaluates the effect of explicit policy constraints. It does not depend on adopting a particular commercial or open-source policy engine.

## 8. Remediation Registry Design

Every remediation will be registered using configuration and code.

A registry entry must specify:

remediation identifier

applicable failure classes

required preconditions

authorized datasets

execution function

validation function

rollback function

risk level

approval requirement

timeout

expected result

No dynamically invented remediation action will be permitted during final experiments.

## 9. Evidence Storage

Every experiment will generate append-only JSON Lines records.

Evidence will include:

Trial configuration

Failure injection

Telemetry

Detection

Classification

Policy decision

Remediation

Validation

Rollback

Final outcome

Derived CSV or Parquet files may be generated for analysis.

The raw JSON Lines records remain the source of truth.

## 10. Baseline Correction

### Baseline A — Alert-Only with Operator-Executed Runbook

The original phrase “manual recovery” is too vague.

The defensible baseline will be:

The monitoring system produces an alert

The operator receives the available telemetry

The operator follows a documented recovery runbook

Diagnosis time is recorded

Remediation start and completion are recorded

Recovery validation time is recorded

Where possible:

Trial order will be randomized

Failure labels will not be directly shown to the operator

The same operator and runbook format will be used

Practice trials will be separated from final trials

Learning effects will be acknowledged as a limitation

The paper must not fabricate or estimate human recovery times.

### Baseline B — Static Rule-Based Automation

This baseline will execute a predefined remediation based on the first matching signal.

It will not use:

Contextual risk scoring

Confidence-based escalation

Dataset sensitivity

Blast-radius constraints

Mandatory post-recovery correctness validation

### Approach C — Policy-Constrained Control Plane

This system will use:

Multi-signal detection

Evidence-weighted classification

Policy evaluation

Approved remediation registry

Post-recovery validation

Rollback

Human escalation

Complete audit records

## 11. Feasibility Constraints

To keep the study achievable, the following limits are locked:

One reference pipeline

One synthetic dataset domain

Eight known failure classes

One unknown-failure class

Three comparison approaches

Local or containerized execution

No distributed cloud benchmark

No production-company claims

No custom machine-learning model unless justified later

No expansion into general MLOps or model-drift research

## 12. Primary Technical Risks

### Risk 1 — Manual baseline bias

Operator performance may improve with experience.

Mitigation:

Randomized trial sequence

Practice trials excluded from final analysis

Standardized runbook

Learning effect reported as a limitation

### Risk 2 — Overly easy failure classification

If every failure produces one obvious signal, classification results will be artificially strong.

Mitigation:

Include overlapping signals

Include multiple severity levels

Include ambiguous and unknown cases

Report per-class performance

### Risk 3 — Rules designed after observing final results

This would create evaluation leakage.

Mitigation:

Freeze detection, classification, policy, and remediation rules before final experiments

Use pilot data only for development

Tag the frozen version in Git

### Risk 4 — Baseline intentionally weakened

An unrealistic baseline would invalidate comparisons.

Mitigation:

Implement reasonable alerting and recovery rules

Document every baseline capability

Use identical pipelines and datasets

Report situations where baselines perform equally or better

### Risk 5 — Excessive experiment count

The proposed matrix may produce hundreds of trials.

Mitigation:

Automate trial execution

Conduct pilot experiments first

Determine final repetition count before final data collection

Document any reduction in scope

## 13. Technical Feasibility Conclusion

The proposed research is implementable and reproducible using a local Python and DuckDB environment.

The strongest contribution will come from:

Controlled failure ground truth

Fair comparison approaches

Explicit safety policies

Post-remediation correctness validation

Transparent escalation

Immutable experimental evidence

Honest reporting of unsuccessful cases

The research does not require large-scale infrastructure to demonstrate whether the proposed control-plane architecture improves pipeline recovery effectiveness and safety.

---
