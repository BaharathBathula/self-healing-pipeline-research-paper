# Phase 2 Day 11 — PDF Layout Rebuild Summary

## Objective

Rebuild the IEEE Access working manuscript and fix LaTeX/page/layout issues.

## Build Result

PASS

Compiled PDF:

paper-ieee-access-working/build/main.pdf

PDF size: 292133 bytes

LaTeX output line:

Output written on C:\Research\self-healing-pipeline-research-paper\implementati

## Main Findings

Initial rebuild produced one serious overfull box:

Overfull \hbox (99.08801pt too wide)

The issue was traced to the artifact availability table in the Results section. The table contained long artifact filenames that exceeded the IEEE column width.

## Fix Applied

The artifact availability table in paper-ieee-access-working/sections/06_results.tex was replaced with a compact column-safe table using short figure identifiers and descriptions.

Additional cleanup:

- main.tex preserved in Day 11 planning folder before edits
- 06_results.tex preserved in Day 11 planning folder before edits
- abstract spacing typo fixed: 100\% root-cause
- email formatting made safer using \nolinkurl{}

## Final Diagnostics

Overfull boxes:

No overfull boxes found.

Bad references/citations:

No undefined references, undefined citations, or duplicate labels found.

Underfull boxes:

532: Underfull \vbox (badness 10000) has occurred while \output is active []
543: Underfull \hbox (badness 1629) in paragraph at lines 30--31
578: Underfull \hbox (badness 1442) in paragraph at lines 89--90
585: Underfull \hbox (badness 6316) in paragraph at lines 92--93
590: Underfull \hbox (badness 2277) in paragraph at lines 6--7
595: Underfull \hbox (badness 1571) in paragraph at lines 14--15
602: Underfull \hbox (badness 10000) in paragraph at lines 41--44

## Status

Day 11 layout rebuild completed successfully.
