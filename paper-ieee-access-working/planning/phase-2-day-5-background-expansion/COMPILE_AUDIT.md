# Phase 2 Day 5 — Compile Audit

## Objective

Verify that the IEEE Access working manuscript compiles after expanding the Background and Related Work section.

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

273468 bytes

## Notes

The Background section compiled with the existing bibliography keys.
