# Reproducibility Checklist

## Paper Package

- [x] Final IEEE-format PDF included
- [x] Main LaTeX source included
- [x] BibTeX bibliography included
- [x] Section files included
- [x] Table files included
- [x] Figure files included
- [x] Build artifacts excluded
- [x] README included
- [x] Artifact statement included
- [x] Reproducibility checklist included

## Artifact Reproducibility

- [x] Synthetic/generated data used
- [x] No private or personally identifiable data included
- [x] Experiment workflow documented in repository
- [x] Figure-generation workflow available in repository
- [x] Tests available in repository
- [x] Evaluation outputs traceable to generated artifacts

## Expected Local Verification Commands

From the repository implementation root:

    python -m pytest
    python scripts/generate_figures.py

From the IEEE paper folder:

    pdflatex main.tex
    bibtex main
    pdflatex main.tex
    pdflatex main.tex

## Notes

Exact runtime may vary by machine and Python/LaTeX installation. The paper package is intended as a clean submission bundle, while full reproduction should be performed from the complete repository.
