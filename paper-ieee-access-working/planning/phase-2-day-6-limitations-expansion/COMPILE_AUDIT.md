# Phase 2 Day 6 — Compile Audit

## Objective

Verify that the IEEE Access working manuscript compiles after expanding the Limitations and Threats to Validity section.

## Compile Commands Used

pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build main.tex
bibtex build\main
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build main.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build main.tex

## Result

PASS

## Output PDF

paper-ieee-access-working/build/main.pdf

## PDF Size

283219 bytes

## Notes

The expanded Limitations section compiled successfully.
