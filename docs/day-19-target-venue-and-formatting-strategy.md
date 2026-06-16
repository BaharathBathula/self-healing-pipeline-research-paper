# Day 19 — Target Venue and Formatting Strategy

Paper title: **Reliability-Aware Self-Healing Data Pipelines: Automated Failure Detection, Root-Cause Classification, and Policy-Constrained Recovery**

Date: 2026-06-15

## Day 19 Objective

Day 19 decides the target-venue strategy and formatting path for the current manuscript.

The current manuscript status is:

- `manuscript-v0.3.md` exists.
- The paper has a strong core argument.
- Runtime statistics and artifact traceability are included.
- Related Work has been upgraded.
- The paper is not submission-ready yet.
- The remaining weaknesses are synthetic-only evaluation, no true baseline comparison, limited data observability references, and venue-specific formatting.

The goal of Day 19 is to decide where the paper should go and what format should be built next.

---

# Executive Decision

## Recommended Path

Use a two-track strategy:

```text
Track 1: arXiv-style technical preprint first
Track 2: peer-reviewed submission after v0.4/v0.5 cleanup
```

This is the most practical path.

Do **not** immediately force the paper into a high-tier database conference or journal. The current paper is credible, but it is not strong enough for top-tier venues without additional baseline experiments or real-world incident data.

## Recommended Primary Formatting Path

Create an IEEE-style LaTeX manuscript as the base format.

Why:

- It works well for arXiv.
- It works well for technical reviewers.
- It supports numbered citations.
- It is easier to convert into IEEE Access later.
- It is cleaner than maintaining only Markdown.
- It handles figures, tables, and references properly.

Recommended next format file:

```text
paper/main.tex
paper/references.bib
paper/figures/
```

---

# 1. Venue Options

## Option A — arXiv Preprint First

### Recommendation

Strongly recommended as the first public research artifact, but only after `manuscript-v0.4.md` fixes the remaining quality issues.

### Why It Fits

The paper is currently a reproducible technical research draft. arXiv is useful for:

- timestamping the work,
- making the paper publicly accessible,
- linking paper + GitHub artifacts,
- supporting citation discovery,
- creating a stable public research object before journal submission.

### Limitations

arXiv is not peer review. It should not be treated as a peer-reviewed publication.

### Formatting

Use LaTeX.

arXiv accepts TeX/LaTeX and PDF, but TeX/LaTeX is preferred. Use PNG or PDF figures. Avoid spaces and unusual characters in file names.

### Recommended arXiv Categories

Primary category:

```text
cs.SE — Software Engineering
```

Possible cross-list categories:

```text
cs.DB — Databases
cs.DC — Distributed, Parallel, and Cluster Computing
cs.AI — Artificial Intelligence
```

Best choice:

```text
Primary: cs.SE
Cross-list: cs.DB
```

Reason:

The paper is about software reliability and data-pipeline systems. It is not primarily an AI model paper.

---

## Option B — SoftwareX

### Recommendation

Good peer-reviewed option **if** the paper is reframed as a software publication.

### Why It Fits

SoftwareX is specifically focused on research software and gives recognition to software artifacts. This matches the repository-driven nature of the work.

### Fit Score

```text
Fit: 8/10 if rewritten as a software paper
Fit: 5.5/10 if submitted as-is
```

### Required Changes

SoftwareX submissions are not normal full research articles. They require:

- a short descriptive paper,
- a software package,
- open-source distribution,
- journal-specific template,
- strong software availability and reuse framing.

### Problem

The current manuscript is too long and too research-paper-like for SoftwareX. SoftwareX has a 3000-word limit for the descriptive paper.

### How to Adapt

Create a separate SoftwareX version:

```text
docs/softwarex-draft-v1.md
```

Structure:

1. Motivation and significance
2. Software description
3. Architecture
4. Implementation details
5. Illustrative examples
6. Impact
7. Reuse potential
8. Availability
9. References

### Verdict

SoftwareX is a good target, but not for the current manuscript format. It requires a separate rewrite.

---

## Option C — IEEE Access

### Recommendation

Possible, but not the first step.

### Why It Fits

IEEE Access is broad, multidisciplinary, open-access, and accepts applied technical research across IEEE fields. It is more suitable than top-tier conferences for a synthetic experimental framework paper.

### Fit Score

```text
Fit: 7/10 after v0.4/v0.5
Fit: 5.5/10 right now
```

### Required Improvements Before Submission

1. Add stronger data observability references.
2. Add confidence intervals or statistical uncertainty if possible.
3. Add implementation summary.
4. Strengthen reproducibility instructions.
5. Make figure formatting publication-ready.
6. Make sure all claims are conservative.
7. Be prepared for open-access publication cost.

### Risk

IEEE Access reviewers may question:

- synthetic-only evaluation,
- no true baseline comparison,
- 100% detection/classification accuracy,
- lack of real production incidents.

### Verdict

Good second-stage target after arXiv preprint and v0.5 cleanup.

---

## Option D — Journal of Systems and Software

### Recommendation

Not recommended immediately.

### Why

JSS is stronger and more demanding. It is relevant because the paper is about software systems and reliability, but the current experimental evidence is not strong enough yet.

### Fit Score

```text
Fit: 4.5/10 right now
Fit: 7/10 after real baseline comparison or production incident evaluation
```

### What JSS Would Likely Need

1. Stronger empirical methodology.
2. Clear comparison against alternatives.
3. Better statistical analysis.
4. More software engineering theory connection.
5. More rigorous limitations and validity analysis.
6. Possibly real-world case studies.

### Verdict

Keep as a future target, not immediate.

---

## Option E — Top-Tier Data/Systems Conferences

Examples:

- SIGMOD
- VLDB
- ICDE
- KDD
- ICSE
- FSE

### Recommendation

Do not target now.

### Why

The current paper is not ready for these venues.

Main blockers:

- synthetic-only evaluation,
- no true baseline comparison,
- no production deployment,
- no large-scale benchmark,
- no strong algorithmic novelty,
- no comparison against commercial/academic systems.

### Verdict

Avoid for now. The opportunity cost is too high.

---

# 2. Target Venue Decision Matrix

| Venue/path | Fit now | Fit after v0.4/v0.5 | Speed | Peer-reviewed | Cost risk | Main issue |
|---|---:|---:|---:|---:|---:|---|
| arXiv preprint | 8/10 | 9/10 | High | No | Low | Not peer-reviewed |
| SoftwareX | 5.5/10 | 8/10 | Medium | Yes | Medium | Needs software-paper rewrite |
| IEEE Access | 5.5/10 | 7/10 | Medium/High | Yes | High | Synthetic-only evaluation |
| Journal of Systems and Software | 4.5/10 | 7/10 | Low | Yes | Medium | Needs stronger empirical evidence |
| Top-tier conference | 2/10 | 5/10 | Low | Yes | Medium | Needs major new experiments |

---

# 3. Final Recommendation

## Primary Recommendation

Build an arXiv-ready IEEE-style LaTeX preprint first.

Then decide between:

```text
SoftwareX rewrite
or
IEEE Access submission
```

## Best Practical Route

```text
Day 20: Create manuscript-v0.4.md with final quality fixes
Day 21: Convert manuscript-v0.4.md to IEEE-style LaTeX
Day 22: Create arXiv-ready package
Day 23: Create reproducibility-checklist.md
Day 24: Decide peer-reviewed target: SoftwareX vs IEEE Access
```

## Why This Route Is Best

The current paper needs visibility and structure before it needs journal submission.

An arXiv-style preprint lets the work become public and citable faster, while preserving flexibility for later journal submission.

---

# 4. Formatting Strategy

## Base Format

Use:

```text
IEEE-style LaTeX
```

Recommended structure:

```text
paper/
├── main.tex
├── references.bib
├── sections/
│   ├── 01_introduction.tex
│   ├── 02_related_work.tex
│   ├── 03_methodology.tex
│   ├── 04_results.tex
│   ├── 05_discussion.tex
│   ├── 06_threats_to_validity.tex
│   └── 07_conclusion.tex
└── figures/
    ├── figure_1_accuracy_by_scenario.pdf
    ├── figure_2_recovery_by_scenario.pdf
    ├── figure_3_runtime_distribution.pdf
    └── figure_4_classification_confusion_matrix.pdf
```

## Citation Style

Use numbered IEEE-style citations for now.

Reason:

- Current manuscript already uses numbered references.
- IEEE-style citations work well for arXiv and IEEE Access.
- They are easier to manage in LaTeX with BibTeX.

## Figure Format

Use PDF figures for final paper rendering where possible.

Preferred:

```text
PDF for LaTeX paper
PNG for GitHub README/Markdown preview
```

The repository already has both PNG and PDF versions of the figures, so use PDF in LaTeX.

## Page Target

For the arXiv/IEEE-style draft:

```text
8–10 pages excluding references and appendix
```

Current manuscript is too long for SoftwareX but acceptable for an arXiv technical preprint.

For SoftwareX:

```text
3000-word short software paper
```

This requires a separate rewrite.

---

# 5. Required Before Formatting

Before creating LaTeX, produce `manuscript-v0.4.md`.

## Required v0.4 Edits

1. Add a short implementation summary subsection.
2. Add one paragraph explaining recovery variation by failure type.
3. Add synthetic data and taxonomy bias as a threat to validity.
4. Add 2–3 stronger data observability/data quality monitoring references.
5. Reduce Discussion repetition by 10–15%.
6. Ensure every figure is referenced before appearing.
7. Keep baseline comparison as future work only.

## Do Not Skip v0.4

Do not convert v0.3 directly to LaTeX.

Reason:

If we convert now, we will carry remaining weaknesses into the formatted version.

---

# 6. SoftwareX Alternative Plan

If the final target is SoftwareX, do not submit `manuscript-v0.3.md` or `manuscript-v0.4.md` as-is.

Create a separate short paper.

## SoftwareX Version Title

Recommended title:

```text
A Policy-Constrained Self-Healing Framework for Reproducible Data-Pipeline Failure Detection and Recovery
```

## SoftwareX Focus

The SoftwareX version should emphasize:

- software functionality,
- implementation,
- installation,
- reuse,
- examples,
- public repository,
- reproducibility,
- impact potential.

It should not spend too much space on broad Related Work.

## SoftwareX Required Repo Strengthening

Before SoftwareX:

1. Add clear installation instructions.
2. Add quick-start example.
3. Add API/CLI usage.
4. Add software metadata.
5. Add license.
6. Add CITATION.cff.
7. Add reproducibility checklist.
8. Add release tag.
9. Archive release with DOI if possible.

---

# 7. IEEE Access Alternative Plan

If the final target is IEEE Access, keep the current research-paper structure.

## IEEE Access Version Needs

1. IEEE LaTeX format.
2. Strong abstract.
3. IEEE-style references.
4. Figure captions in IEEE style.
5. Expanded Related Work.
6. Conservative claims.
7. Strong reproducibility appendix.
8. Clear limitations.
9. Possibly confidence intervals.
10. Disclosure of generative AI use if required by journal policy.

## Main Risk

IEEE Access may reject if reviewers see the work as too synthetic or insufficiently compared.

Mitigation:

- Emphasize evaluation framework contribution.
- Do not claim production readiness.
- Do not claim baseline superiority.
- Add confidence intervals if possible.
- Add reproducibility package as a strong contribution.

---

# 8. What Not To Do

Do not submit to a journal today.

Do not claim the paper is peer-reviewed because it is on arXiv.

Do not target top-tier data systems venues yet.

Do not submit to SoftwareX without rewriting into a software-paper format.

Do not submit to IEEE Access until the v0.4/v0.5 quality fixes are done.

Do not remove the synthetic-evaluation limitations. They protect the paper.

---

# 9. Day 19 Final Decision

## Selected Immediate Path

```text
Create manuscript-v0.4.md first.
Then convert to IEEE-style LaTeX.
Then prepare arXiv-ready preprint package.
```

## Selected Future Peer-Reviewed Targets

Primary peer-reviewed option:

```text
SoftwareX, if reframed as a software publication.
```

Secondary peer-reviewed option:

```text
IEEE Access, if kept as a full research article.
```

Not recommended now:

```text
Journal of Systems and Software
Top-tier conferences
```

---

# Day 19 Completion Checklist

- [x] Venue options reviewed.
- [x] arXiv path selected as immediate public preprint route.
- [x] SoftwareX evaluated as software-paper target.
- [x] IEEE Access evaluated as research-article target.
- [x] JSS evaluated and deferred.
- [x] Top-tier venues rejected for now.
- [x] Base format selected: IEEE-style LaTeX.
- [x] Citation style selected: IEEE numbered references.
- [x] Figure format selected: PDF for LaTeX, PNG for GitHub.
- [x] Page target defined.
- [x] v0.4 required edits defined.
- [x] Day 20 handoff defined.

---

# Day 20 Handoff

Day 20 should create:

```text
docs/manuscript-v0.4.md
```

Day 20 must make targeted quality edits before LaTeX conversion:

1. Add implementation summary.
2. Add recovery-variation paragraph.
3. Add synthetic data and taxonomy bias threat.
4. Add stronger data observability references.
5. Reduce Discussion repetition.
6. Prepare the manuscript for LaTeX conversion on Day 21.
