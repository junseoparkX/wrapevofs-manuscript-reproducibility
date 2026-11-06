# v19: GA and RFECV target-guidance clarification (5 November 2026)

Four text locations were revised, using existing Supplementary Figure S17 only:

1. Abstract: explain that RFECV supplies a target count for soft-penalty genetic exploration before representative locking.
2. Introduction: distinguish the RFECV elimination path from alternative-subset exploration within the Direct-screened universe, and clarify that the penalty acts on deviations on either side of the target count.
3. Results: connect the archived CGGA guidance ablation to target-size control while retaining the absence of a uniform predictive advantage.
4. Discussion: replace repeated comparator prose with the archived five-run feature-count ranges: SVM-L1 16–23 to 15–16; XGBoost 33–39 to 19–21; Boruta-RF 10–14 to nine in every run. All six ranges were checked against the unchanged S17 source CSV.

The S17 comparison remains explicitly an archived original-configuration analysis. No claim of general predictive superiority or feature-identity stability was added. The separate common-RF-seed and subsequent outer-test experiments are not incorporated.

Only main.tex and sections/main_text.tex changed scientifically. Abstract: 130 whitespace-delimited words (previously 150). Main body: net increase of 17 whitespace-delimited tokens; the combined abstract/body length does not increase. Main PDF: 19 pages; Supplementary PDF: 55 pages. Five main figures, two main tables, 29 Supplementary Figures, and 30 Supplementary Tables remain.

No new experiments were performed. All figure files and captions, tables, Methods, Supplementary prose, references, numerical source data, author information, cover letter, Source Data workbook, and reporting forms are unchanged. Both PDFs were rebuilt; Supplementary PDF text is identical page by page. V18 baseline files remain unchanged.
