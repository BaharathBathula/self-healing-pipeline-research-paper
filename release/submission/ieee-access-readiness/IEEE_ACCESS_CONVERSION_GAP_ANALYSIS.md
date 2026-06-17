# IEEE Access Conversion Gap Analysis

## Current Paper State

The current manuscript is an IEEE-style 8-page paper package with:

- Final PDF
- LaTeX source
- BibTeX bibliography
- Figures
- Tables
- Artifact statement
- Reproducibility checklist
- Manifest and checksums
- Clean ZIP submission package

## Target Venue

IEEE Access

## Main Gap

The current paper is formatted as a compact IEEE-style paper, but IEEE Access requires venue-specific preparation using the IEEE Access template and submission expectations.

## Conversion Gaps

### 1. Template Gap

Current state:

- Existing paper uses IEEE-style LaTeX formatting.

Required action:

- Verify and convert to the official IEEE Access template.
- Confirm whether the current IEEE class/package matches IEEE Access requirements.
- Rebuild PDF after conversion.

Risk:

- Submitting a generic IEEE-style paper instead of the correct IEEE Access format may create administrative rejection risk.

### 2. Manuscript Depth Gap

Current state:

- Paper is concise and submission-ready as an 8-page package.

Required action:

- Expand into a fuller journal-style manuscript.
- Strengthen technical motivation, related work, evaluation depth, limitations, and artifact description.

Risk:

- An 8-page version may look too lightweight for a journal article.

### 3. Evaluation Gap

Current state:

- Evaluation uses reproducible synthetic experiments.

Required action:

- Explain why synthetic data is appropriate.
- Add stronger discussion of fault scenarios, baseline comparison, scalability, overhead, and threats to validity.
- Consider adding additional experiment tables if available.

Risk:

- Synthetic-only evaluation may be challenged unless defended clearly.

### 4. Related Work Gap

Current state:

- Related work is present but concise.

Required action:

- Expand comparison against data observability tools, data quality frameworks, workflow orchestration systems, pipeline monitoring, and self-healing infrastructure literature.

Risk:

- Weak related work can make the contribution appear incremental.

### 5. Contribution Framing Gap

Current state:

- The paper presents a self-healing pipeline framework.

Required action:

- Make the contribution explicit:
  - Failure detection
  - Failure classification
  - Automated recovery
  - Telemetry and auditability
  - Reproducible artifact
  - Reliability-oriented evaluation

Risk:

- If framed as only monitoring or data quality checking, novelty becomes weaker.

### 6. Author Metadata Gap

Current state:

- Author name is corrected.

Required action:

- Confirm author email.
- Confirm affiliation.
- Confirm ORCID if used.
- Prepare author biography.
- Prepare author photo if required after acceptance or submission.

Risk:

- Incomplete author metadata can delay submission.

### 7. Compliance Gap

Current state:

- Submission statements exist.

Required action:

- Verify IEEE Access AI-assistance disclosure expectations.
- Confirm conflict, funding, data availability, and code/artifact statements.
- Confirm supplemental material policy.
- Confirm APC acceptance.

Risk:

- Compliance mismatch can delay or block submission.

## Bottom Line

The current package is strong as a clean paper artifact, but it is not yet a final IEEE Access submission. The paper should be converted, expanded, rebuilt, and audited before submission.
