# Post-freeze analysis validation report

Date: 2026-08-08

## Passed checks

- Rush recovery: PASS; 6 banks, 30 candidates, 0 duplicate candidates beyond the first, all selections matched archived and frozen records, maximum selected regret 0.
- AMP-AD completion sentinel: complete for exactly 24 conditions; `ga_rerun=false`; protocol SHA-256 `7bc7b27e00f7337654b6f81c1448a831ce3979129e68d14666389445d3ec93b5`.
- CGGA benchmark manifest: full-matrix reconstruction verified against the archived compact matrix; held-out outcomes were not used for selection; `ga_rerun=false`.
- CGGA nested re-lock manifest: complete; 214 development participants; 5 selection changes; `ga_rerun=false`; original 92-participant held-out cohort not accessed.
- Package locking tests: 66 passed. An initial run had 65 passes and one setup error caused only by denied access to the Windows default pytest temporary directory; rerunning the unchanged tests with a fresh workspace-local `--basetemp` produced 66/66 passes.
- Figure/table rebuild reproducibility: two consecutive runs produced identical SHA-256 values for Supplementary Figures S21--S23 in PDF/SVG/PNG, Tables S22--S24, and the figure manifest. Approved main Figure 5 is independently reproduced by `build_cgga_figure5.py`; main Figure 4 is derived deterministically from its preserved editable SVG.
- Figure policy: new Supplementary Figures S21--S23 use native 170-mm width, no background grids, and bold panel letters only. Main Figure 4 preserves its scientific content while a deterministic presentation cleanup removes 63 background-grid paths and one empty annotation box.
- Main and Supplementary LuaLaTeX/BibTeX builds: PASS.
- Final logs: zero undefined citations/references, multiply defined labels, overfull/underfull boxes, or LaTeX/package warnings.
- Render QA: main pages 7--8 and Supplementary pages 26--27 were rendered with Poppler and visually inspected after the placement correction; no clipping, obscured labels, missing axes, table overflow, duplicate captions, or empty pages were found.
- Main PDF: 16 pages; SHA-256 `3d07f2684fbb0ff43fc43ed882690300a722bbd10539a937e6ace141155f1e3e`.
- Supplementary PDF: 41 pages; SHA-256 `b7b41bbecbc681b54819cbc989c0384b09182fccefea88c3ce5c6f9139f88cd7`.

## Claim-boundary checks

- The manuscript calls the AMP-AD analysis a one-time post-freeze cross-center evaluation, not prospective clinical or independent external validation.
- The manuscript does not claim predictive superiority from either AMP-AD or CGGA.
- The adverse nested CGGA sensitivity is disclosed rather than suppressed.
- Approved main Figures 4 and 5 retain their archived scientific roles; the post-freeze analyses are additive Supplementary Figures S21--S23 rather than replacements.
- The regret guarantee is stated only for configured empirical development-CV score-gap feasibility.
- The excluded locking-layer simulation has no manuscript citation or integration.

## Remaining non-computational submission items

Private-radiomics REB/IRB approval or exemption wording and consent/waiver basis, all-author declaration approval, and ADNI DPC upload/review remain outside machine verification.
