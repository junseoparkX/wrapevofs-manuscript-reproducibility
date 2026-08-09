# Supplementary graphic cleanup report

Date: 2026-08-09

## Scope

This in-place V12 pass changed only the presentation of Supplementary Figures S9, S19, and S21--S23. It did not rerun GA, Direct selection, RFECV, model fitting, held-out evaluation, bootstrap analysis, simulation banks, or any empirical analysis. No plotted estimate, interval, feature-importance value, feature count, selected run, label identity, or scientific conclusion was changed.

## Changes

- Supplementary Figure S9 was rebuilt at 170 mm from three manuscript-local frozen aggregate CSVs. The redundant table-like selected-settings block at the right of panel c was removed, and the primary SVM-L1 feature-importance display now spans the full panel width. The caption now describes only the information actually shown.
- Supplementary Figure S19 was re-split at the blank band after panel b. Panels a--b are complete on the first page, and panels c--d are complete on the continuation page; no panel content was cropped or redrawn.
- Supplementary Figure S21 received wider interpanel spacing and smaller contrast-panel y labels.
- Supplementary Figure S22 received wider interpanel spacing and a compact y-label treatment for panel c.
- Supplementary Figure S23 received wider interpanel spacing and a wrapped `Balanced accuracy` label in panel c.
- `build_postfreeze_results.py` now raises an error if a right-panel y tick label overlaps the preceding axes.

## Reproducibility and QA

- Two consecutive rebuilds of the 12 PDF/SVG/PNG assets for S9 and S21--S23 produced zero SHA-256 changes.
- The independent Supplementary LuaLaTeX/BibTeX build passed at 42 pages with zero warning-pattern, undefined-reference, overfull/underfull-box, duplicate-destination, or oversized-float matches.
- Supplementary pages 15, 24--25, 27, and 28 were rendered at 180 dpi and inspected. The S9 settings block is absent; S19 panel b is complete on its first page; S21--S23 labels do not cover neighboring data panels; all axes, markers, intervals, legends, panel letters, and captions are visible.
- Final Supplementary PDF SHA-256: `b9f451183daa1ca309b0e3bb0fdb5bc5ca02386b2a2a4f863590b3dbb3714d25`.
