# WrapEvoFS Methods, Figure 6, and tables consistency revision

## Files modified

- `analysis/revise_manuscript.py`
- `analysis/build_revised_figure_sources.py`
- `analysis/full_analysis/archived_figure_5_6_source.py`
- `analysis/validate_methods_figure6_tables_consistency.py`
- `data/revised_assets/Figure_6/source.svg`
- `manuscript/figures/main/Figure_6/Figure_6_GA_mechanistic_ablation.svg`
- `manuscript/figures/main/Figure_6/Figure_6_GA_mechanistic_ablation.png`
- `manuscript/figures/main/Figure_6/Figure_6_GA_mechanistic_ablation.pdf`
- `manuscript/figures/main/Figure_6/caption.md`
- `manuscript/google_docs_assets/captions.md`
- `manuscript/tables/supplementary/Table_S1C_empirical_search_settings.csv`
- `manuscript/tables/supplementary/Supplementary_Table_captions.md`
- `manuscript/WrapEvoFS_manuscript_final_methods_figure6_tables.docx`
- `manuscript/WrapEvoFS_manuscript_final_methods_figure6_tables.pdf`
- `audit/methods_figure6_tables_consistency_validation.json`

## Figure 6 changes

Figure 6 내부의 “Boruta-RF configuration contrast: target k=14 vs 9” 문구를 삭제하고 다음으로 교체하였다.

> No guidance: λ=0; stored target inactive in GA fitness

Figure 6 caption과 Results에는 다음 원칙을 동일하게 반영하였다.

- no-guidance에서는 \(\lambda=0\)이므로 저장 RFECV target이 GA fitness에 영향을 주지 않는다.
- 저장 cap과 target은 실제 RFECV 실행 provenance로 유지한다.
- Boruta-RF는 no-guidance에서 cap/recorded target 15/14, guided에서 10/9였다.
- 여섯 configuration snapshot을 비교한 결과, 각 guided/no-guidance pair에서 그 밖의 GA 설정은 동일했다. SVM-L1과 XGBoost는 \(\lambda\)만 달랐고, Boruta-RF는 \(\lambda\) 외에 RFECV cap이 달랐다. 이 cap 차이는 no-guidance GA의 \(\lambda=0\) fitness에는 들어가지 않는다.

따라서 더 이상 이를 target-k configuration-level contrast 또는 14 대 9 target 차이에 의한 비교로 기술하지 않는다.

## Table S1C changes

기존 cap/target 기록을 삭제하지 않고 다음 세 층으로 분리하였다.

- RFECV cap used in execution
- RFECV-derived target recorded
- Target used in GA size penalty

값은 다음과 같이 유지하였다.

| Condition | Execution cap | Recorded target | Target active in GA penalty | λ |
|---|---|---|---|---|
| ADNI | 30 / 30 / 30 | 29 / 30 / 27 | 29 / 30 / 27 | 0.015 |
| CGGA guided | 15 / 20 / 10 | 15 / 20 / 9 | 15 / 20 / 9 | 0.015 |
| CGGA no guidance | 15 / 20 / 15 | 15 / 20 / 14 | — | 0 |

dash는 \(\lambda=0\)으로 인해 저장 target이 GA size penalty에서 비활성임을 뜻한다는 note를 추가하였다. RFECV가 실행되었고 cap/target이 audit provenance로 유지된다는 점도 명시하였다. 다른 검증 설정은 변경하지 않았다.

## Methods subsection reorganization

Methods 순서를 다음과 같이 재구성하였다.

1. Overall analytical workflow
2. Software implementation and reproducibility
3. RFECV-guided genetic subset search and representative-run locking
4. Empirical evaluation across ADNI and CGGA
5. ADNI-derived multiclass demonstration: data, settings, and evaluation
6. CGGA binary disease-domain demonstration: data, settings, and evaluation

새 general subsection으로 candidate-space notation, RFECV score/target, chromosome, GA base score/fitness, Jaccard, medoid 및 Algorithm 1을 이동하였다. 이 subsection에는 ADNI/CGGA 이름, cap 30, \(\lambda=0.015\), branch-specific target과 같은 empirical setting이 없다.

ADNI cap/target, balanced-accuracy fitness, \(\lambda=0.015\), ranking metric과 held-out evaluation은 ADNI subsection으로 이동하였다. CGGA cap/target, accuracy fitness, guided/no-guidance \(\lambda\), AUROC ranking 및 held-out evaluation은 CGGA subsection에 유지하였다. 문단 중복은 만들지 않았다.

## Algorithm 1 refinements

- parent-selection line을 “Sample parents with replacement in proportion to fitness; use uniform sampling if total fitness is zero or nonfinite.”로 단순화하였다.
- `prespecified development-CV locking score` 대신 `documented development-CV locking score`를 사용하였다.
- reported-run 설명은 `top_k=n_runs=5`이므로 모든 다섯 run-level candidate가 ranking과 locking에 사용 가능했다는 두 문장으로 압축하였다.
- Input, Output, 1–26 line numbering, nested indentation과 explicit Return을 유지하였다.
- held-out/test data는 Algorithm 1 input에 없다.
- Algorithm 1은 PDF page 5에서 한 페이지에 완전히 유지되며, 앞의 medoid equation과 불필요한 강제 page break 사이의 공백을 줄였다.

## Table 1 reorder

Table 1의 실제 Word body order를 다음과 같이 수정하였다.

1. A. ADNI-derived cohort composition
2. B. ADNI-derived molecular feature inventory
3. C. CGGA cohort composition
4. D. CGGA molecular feature inventory

값, 백분율, panel label과 note는 변경하지 않았다. 첫 렌더에서 B label이 페이지 하단에 고립되는 현상을 확인하여 Table 1을 새 페이지 상단에서 시작하도록 조정했다. 최종 PDF page 7에서 A–B–C–D 전체와 note가 한 페이지에 함께 표시된다.

## Numerical-integrity check

- 기존 `data/plot_data` CSV: 26/26 SHA-256 unchanged
- CGGA experiment configuration snapshots: 6/6 확인
- CGGA fitness metric: 6/6 `accuracy`
- CGGA `top_k=n_runs=5`: 6/6 확인
- Figure 6 plot data와 empirical point estimates/intervals: 변경 없음
- Table 1 수치와 백분율: 변경 없음
- native framework equations: 9개 유지
- Algorithm 1: 26 numbered lines 유지
- References-to-Supplementary-Information OOXML region: Step 3와 동일
- 전용 consistency validator: 13/13 PASS

## Rendered-PDF validation

최종 DOCX를 Microsoft Word로 PDF export하였다.

- 최종 PDF: 42 pages, US Letter
- 전체 42쪽을 100 dpi page images 및 5개 contact sheet로 검토
- Methods equations: page 4, 180 dpi 검토
- Algorithm 1: page 5, 180 dpi 검토
- ADNI empirical settings: page 6 검토
- Table 1: page 7, 180 dpi 검토
- Figure 6: page 18, 180 dpi 검토
- Supplementary Table S1C: page 27, 180 dpi 검토

수식, algorithm line, Figure 6 annotation/caption, Table 1 cell, S1C cell/note에서 clipping, overlap, margin overflow 또는 missing glyph를 발견하지 않았다. Figure 6 내부 annotation은 panel b와 c 사이에서 다른 label과 겹치지 않는다. S1C의 표와 전체 provenance note는 page 27에 함께 유지된다.

## Unresolved issues

- ADNI의 최종 run-ID tie rule은 제공 artifact에 남아 있지 않아 `Not retained`를 유지하였다.
- 정확한 RAPIDS version은 저장되지 않아 추정하지 않았다.
- documents skill의 LibreOffice renderer는 이 Windows 환경에 `soffice`가 없어 실행되지 않았다. 대신 Microsoft Word의 실제 export와 Poppler page rendering으로 42쪽 전체를 검토하였다.
