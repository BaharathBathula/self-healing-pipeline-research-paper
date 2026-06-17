# Phase 2 Day 3 — Compile Audit

## Objective

Verify that the IEEE Access working manuscript compiles after replacing the placeholder Experiments section.

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

262374 bytes

## Notes

The build output is only for verification. The build folder should not be treated as a final submission package.
