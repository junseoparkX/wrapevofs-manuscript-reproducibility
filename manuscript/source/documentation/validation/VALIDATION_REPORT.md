# Submission validation report

## Build and submission counts

- `main.tex`: PASS under LuaLaTeX; 18 pages.
- `supplementary_information.tex`: PASS under LuaLaTeX; 51 pages.
- Main PDF SHA-256: `c0b2f1b63471bf79d69cb7ae3db8600af54a3de909390f8790c61bc90c656640`.
- Supplementary PDF SHA-256: `b823ef0878d88426de9497ec95aff4d6cc0672214953a6fba6021ee1e9248b31`.
- Final logs contain no undefined references, undefined citations, duplicate labels, missing figures, missing characters, overfull boxes, or fatal LaTeX errors. The only logged font notice is a benign 0.5-point substitution for the small ORCID icon glyphs.
- Deterministic submission counts: title 9 words; Abstract 150 words; Introduction, Results, and Discussion 2,134 words; Methods 2,928 words; five main figures and two main tables.

## Display, citation, and visual QA

- Every main Figure 1--5 and Table 1--2 is cited in the main text.
- Supplementary Figures S1--S28 and Supplementary Tables S1--S28 are numbered sequentially and cited.
- Supplementary Figure S1 begins on the same page as the `S2 Supplementary Figures` heading.
- Supplementary Figures S1 and S3 use the same bold lowercase `a)`, `b)`, `c)` panel-label convention as the remaining figures; both were regenerated from their source builder rather than edited as raster images.
- Multi-page Figures S5, S16, and S17 retain their continuation notices and show the complete caption after all panels.
- Every multi-section Supplementary Table title precedes its section headings. Page-break guards keep each subsection heading with its first table rows; the continuation identifier for Supplementary Table S21 is correct.
- Supplementary Table S6 is the TCGA selector-layer table; the AMP-AD cohort note follows Supplementary Table S12.
- The full-feature Bayesian reference in Supplementary Table S21 cites Supplementary Fig. S24.
- The main and Supplementary title pages use one restrained, shared, format-neutral academic submission hierarchy for title, authors, affiliations, correspondence, contact information, and the ADNI corporate-author note. The Supplementary title page also gives a compact contents inventory.
- All 18 main pages and all 51 Supplementary pages were rendered to PNG. The revised title pages and full-document contact sheets were visually inspected; no clipping, overlap, unreadable labels, orphaned subtable headings, missing panels, detached captions, unintended grids, or blank pages were found.
- Automated PDF-boundary validation found no blank page and no text glyph outside a page boundary. All Supplementary Figure S1--S28 and Supplementary Table S1--S28 labels were recovered from the rendered PDF. The machine-readable report is `submission_pdf_layout_qa.json`.
- All 28 Supplementary Figure captions were reviewed for a short standalone title, complete panel coverage, and definition of displayed symbols, intervals, or reference lines where applicable. The S1 and S3 captions were expanded to define their panel encodings without changing any result.
- Main-panel label validation passes for Figures 1--5; equal bold panel labels are used within each figure.
- Main Table 1 remains wholly on one page. Inter-row spacing and controlled line breaks separate the TCGA GBM/LGG and CGGA MGMT entries without expanding the table to another page.
- The main and Supplementary title pages use a centered sans-serif title, centered byline, one black divider, and black metadata headings. No `ARTICLE` or other imitated journal-production label is used.
- The ADNI consortium byline note now includes the official data-source and investigator-role statement plus a direct external link to the complete ADNI acknowledgement list. Both ADNI links are encoded as PDF `/URI` actions, not internal document jumps; the browser window or tab used for an external URI remains controlled by the reader's PDF viewer.
- All multipart Supplementary Table section headings use one shared style: lowercase `a.`, `b.`, `c.`, and `d.` (or `e.` where required), footnote-sized bold type, and common spacing. Rendered checks of Tables S8--S12 and S23 confirm the same visual size across first and subsequent sections.
- Figure 1 SHA-256 freeze validation passes.
- The final five-author byline, affiliations 1--5, five email addresses, correspondence line, and Author contributions were rendered and visually inspected in both PDFs. Mohammad Sadegh Mashayekhi was removed from the byline, metadata, email list, and contribution statement at the author's direction. No clipping, overlap, or detached affiliation line was found.
- The rendered contribution statement records DICOM and clinical-metadata provision and ethics-information verification by M.F.H. and E.S., and DICOM de-identification and radiomics-data generation by J.P.

## Scientific and implementation checks

- Frozen-value and decision-path validation: PASS.
- Controlled locking simulation: PASS for the frozen protocol and all 4,995,000 banks; configured empirical-regret violations: zero.
- VGH brain-tumour radiomics integration invariants: PASS.
- The VGH brain-tumour radiomics cohort is identified under University of British Columbia approval H20-02354 (``Brain Tumor Image Analysis''; principal investigator Stephen Yip), with anonymized data, a waiver of consent for the retrospective study, and permission for secondary analysis.
- CPU/GPU labels were removed from Results, Methods, general captions, and non-runtime summary tables because they do not affect interpretation. The exact cuML/scikit-learn backend distinction is retained once in Supplementary Table S24 because it is needed for computational reproducibility.
- Existing TCGA locking audit remains unchanged: 30 banks, 150 candidates, maximum selected empirical regret 0.00978447, and 11 medoid changes with positive representativeness gain.
- The TCGA selector-layer extension remains protocol-frozen at SHA-256 `c9c808d591918779961a7f236f6beb588c640e1b8932a8b030428f3d988a4ff1`; all 30 expected conditions and output checksums passed.
- Direct, RFECV, GA search, candidate rescoring, locking, held-out evaluation, Bayesian analysis, STABL, BLiP, and empirical feature selection were not rerun for this editorial revision.
- The finalized canonical stable-hash rule and duplicate-mask policy are unchanged.
- TCGA SCNV provenance is documented as provider-confirmed label-independent variance filtering, supported by a label-blind 4,999/5,000 reconstruction and an exact variance tie at the cutoff.
- ADNI re-locking uses the recovered complete five-mask banks. At absolute delta 0.01, each branch has a singleton eligible pool and zero selected empirical regret; no GA or held-out evaluation was rerun.

## Claim boundary

- The mathematical guarantee concerns only configured empirical development-CV regret within a finite candidate bank.
- The selector comparison is branch-dependent performance--compression evidence, not predictive equivalence, universal GA benefit, external validity, biomarker stability, or global feature-selection optimality.
- Native supports, matched-cardinality sensitivities, and random banks remain explicitly distinguished.
- No pooled cross-dataset performance figure or meta-analysis was created because the five datasets use materially different validation designs.
- Absolute delta 0.01 is reported as a fixed, metric-scale operating tolerance, not a universal, uniquely optimal, or clinically acceptable threshold.

## Validation scope

This report covers the reproducibility repository, manuscript source, rendered PDFs, and machine-readable audit outputs. Journal-portal review steps and publisher-specific reporting forms are managed separately and are not represented as repository validation results.
