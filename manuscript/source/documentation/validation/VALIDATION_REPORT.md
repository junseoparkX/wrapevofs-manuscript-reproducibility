# Submission validation report

## Build and visual QA

- `main.tex`: PASS under LuaLaTeX; 16 pages.
- `supplementary_information.tex`: PASS under LuaLaTeX; 48 pages.
- Main PDF SHA-256: `93dc1e1cb1eee2abeca450a243104403d3454687d57cf74413efc9d1fa7a8768`.
- Supplementary PDF SHA-256: `bdec38d8f69782ff789360d2bf2702e91499d1a764fc187ead2b93ba7299f5c0`.
- Undefined references or citations: none.
- Overfull or underfull boxes: none in the final logs.
- Main figures: five; main tables: two.
- Supplementary figures: S1--S28 in first-citation order. Multi-page Figures S5, S16, and S17 show a continuation notice on the first page and the complete numbered caption only after all panels on the second page.
- Supplementary tables: S1--S28.
- Submission counter: title 9 words; Abstract 150 words; Introduction, Results, and Discussion 2,090 words; Methods 3,206 words.
- All 16 main pages and all 48 Supplementary pages were rendered to PNG and inspected. The Supplementary title, both Algorithm S1 pages, first-citation-ordered TCGA figures and tables, multi-page Figures S5/S16/S17, post-freeze AMP-AD display, and terminal provenance table were additionally inspected at page resolution. No clipping, overlap, unreadable label, blank page, or unintended grid was found.
- The `S2 Supplementary Figures` heading and Supplementary Figure S1 are fixed to the same page; the preceding Supplementary Methods end cleanly on the prior page.
- Algorithm S1 retains coherent run, generation, chromosome, conditional, and termination indentation across its page break.
- Every main Figure 1--5 and Table 1--2 is cited in the main text. Every Supplementary Figure S1--S28 and Table S1--S28 is cited, and compiled counters are strictly sequential without missing or duplicated labels.
- The corrected TCGA common-seed audit records 180 final method fits and 17,676 participant--method outer-prediction records; the earlier erroneous phrase "420 expected outer-prediction rows" was removed.
- Figures 3--5 and S8 use 170-mm publication assets. Panel-label validators pass with equal bold labels within each figure.
- Figure 1 SHA-256 freeze validation passes.

## New TCGA selector-layer extension

- Frozen protocol SHA-256: `c9c808d591918779961a7f236f6beb588c640e1b8932a8b030428f3d988a4ff1`.
- Validation status: PASS; 30 expected and 30 verified conditions; zero errors.
- Validation manifest SHA-256: `6d59a4c15ae89b1fd02a3905171706d7397a6f4eda4dd943e99f7ab1e680bddc`.
- Exact verified TCGA outer partitions, post-Direct universes, and common-seed parent predictions were reused.
- Direct, RFECV, GA search, candidate rescoring, and locking were not rerun or altered.
- Feature lists and hashes were serialized before outer-test values or outcomes were opened. Every new final estimator used the parent condition's common seed.
- The result set includes multinomial Elastic Net, subsampling stability selection, native and matched-cardinality signatures, and five random banks per condition.
- The extension is explicitly interpreted as a retrospective selector-layer sensitivity conditional on post-Direct universes, not a standalone full-pipeline, external, or compute-equivalent benchmark.

## Numerical cross-checks

- Existing TCGA locking audit remains unchanged: 30 banks, 150 candidates, maximum selected empirical regret 0.00978447, and 11 medoid changes with positive representativeness gain.
- Main Figure 3 and Supplementary Figure S8 are generated from validated aggregate CSVs under `supplementary_data/tcga_matched_comparator/`.
- WrapEvoFS repeated-OOF macro one-vs-rest AUROC is 0.8265, 0.8270, and 0.8277 for SVM-L1, XGBoost, and Boruta-RF.
- Matched-cardinality WrapEvoFS-minus-Elastic-Net effects are +0.0176 [0.0008, 0.0341], -0.0017 [-0.0146, 0.0111], and -0.0109 [-0.0236, 0.0024].
- Matched-cardinality WrapEvoFS-minus-stability effects are +0.0261 [0.0082, 0.0434], -0.0015 [-0.0136, 0.0105], and -0.0128 [-0.0260, 0.0012].
- Mean WrapEvoFS-minus-random-bank effects are -0.0018, +0.0102, and -0.0043 across the three branches.
- These values agree between source CSVs, Figure 3, Supplementary Figure S8, Supplementary Table S6, Abstract-level direction statements, Results, Methods, and the analysis report.

## Existing scientific-integrity checks

- Frozen-value and decision-path validation: PASS.
- Locking-simulation protocol, 4,995,000-bank strict-regret audit, rendered hashes, and integration: PASS.
- Private-radiomics aggregate, checksum, privacy, split, and empirical-regret invariants: PASS.
- TCGA cleaned-SCNV provenance remains documented as provider-confirmed label-independent variance filtering with a label-blind 4,999/5,000 reconstruction and an exact variance tie at the cutoff.
- Figure source-data manifest parses as CSV and every listed display output exists.
- No em dash character occurs in the manuscript TeX sources.

## Claim audit

- The mathematical guarantee remains limited to configured empirical development-CV regret within a finite candidate bank.
- The new comparison is reported as branch-dependent performance--compression evidence. It is not called predictive equivalence, universal GA benefit, external validity, biomarker stability, or global feature-selection optimality.
- Native supports, matched-cardinality sensitivities, and random banks are distinguished explicitly.
- Random controls are described as matching five-candidate bank size and locking-evaluation budget, not total GA compute.
- Similar signature cardinality with different feature identity is retained as a substantive participant-partition finding.

## Remaining external submission actions

The following were intentionally not inferred or completed here: private-radiomics research-ethics-board and consent/waiver wording; verified reviewer-accessible public code release and archive identifier; ADNI publication review; and Nature Source Data/reporting/ML/software checklists. These are external submission requirements, not computational manuscript defects.

## Final editorial QA refresh (2026-08-13)

- Final main PDF: 16 pages.
- Final Supplementary PDF: 48 pages.
- Table 1 contains all five datasets on one page with its header; Table 2 appears in Section 2.2 and interrupts no sentence.
- All 16 main pages and all 48 Supplementary pages were visually inspected after rendering. No clipping, overlap, orphaned table row, unintended blank page, missing panel, or detached final caption was found.
- Automated citation/display, main-panel, frozen-value, and Figure 1 freeze validations passed.
- The final logs contained no undefined references, undefined citations, duplicate labels, missing figures, overfull or underfull boxes, or fatal LaTeX errors.
- Authoritative final main PDF SHA-256: `93dc1e1cb1eee2abeca450a243104403d3454687d57cf74413efc9d1fa7a8768`.
- Authoritative final Supplementary PDF SHA-256: `bdec38d8f69782ff789360d2bf2702e91499d1a764fc187ead2b93ba7299f5c0`.
