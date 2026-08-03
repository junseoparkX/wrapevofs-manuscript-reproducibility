# 1. Executive summary

Step 3에서는 WrapEvoFS의 핵심 기여를 “감사 가능한(auditable), 개발 데이터 전용(development-only), 크기 제어형(size-controlled) 확률적 특징 선택과 사전 명시된 대표 실행 잠금 규칙”으로 재정렬했다. Step 1과 Step 2에서 확정한 분할, 전처리, 압축 분모, 성능 불확실성, 안정성 한계를 유지했으며, 참고문헌·인용·인용 자리표시자·관련연구 문장은 변경하지 않았다.

주요 해석 수정은 다음과 같다.

- 전체 7,411개 특징 Bayesian 모형의 계수 순위를 비추론적·기술적 posterior ordering으로 한정하고, 모든 95% credible interval이 0을 포함한다는 사실을 Abstract, Results, Figure 3 caption, Discussion에 명시했다.
- CN one-vs-rest AUROC와 argmax 분류 실패를 분리해 설명하고, held-out CN 참가자에게 CN 예측이 한 건도 없었다는 결과를 눈에 띄게 유지했다.
- 81개 후보 제한 Bayesian credible interval과 BLiP expected-FDR 해석이 개발 데이터에서 생성된 screen에 조건부이며 screening uncertainty와 원래 7,411차원 탐색의 multiplicity를 포함하지 않는다고 명시했다.
- “cross-method validation”을 “candidate-restricted interoperability analysis” 또는 “within-dataset cross-method concordance”로 교체했다.
- STABL 중복 선택을 독립 검증이나 생물학적 확인이 아니라 동일 개발 데이터 안의 방법 간 일치로 제한했다.
- primary BLiP가 81개 후보를 모두 유지하여 추가 압축을 제공하지 않았음을 중심 결과로 명확히 했고, 47개와 32개 선택 결과는 sensitivity analysis로 유지했다.
- CGGA 결과를 portability나 external validation이 아니라 두 번째 질병 영역의 binary gene-expression 내부 demonstration으로 재표현했다.
- Figure 5는 고정 분할 뒤 development와 locked held-out가 직접 갈라지는 구조로 다시 작성했다. Figure 1도 같은 개념 구조로 정리하여 기존 빨간 문장이 박스 밖으로 나가는 문제와 화살표–locked-signature 충돌을 제거했다.
- Figure 3의 calibration/predictive-uncertainty 패널은 본문 Figure 3에서 제거하고 Supplementary Figure S4A에만 유지하여 중복을 해소했다. 결과는 삭제하지 않았다.
- Bayesian, STABL, BLiP 분석은 “optional”이라는 표현 대신 “secondary” 또는 “complementary downstream analyses”로 통일했으며, WrapEvoFS 필수 단계가 아님을 명시했다.

저자는 보존된 CGGA preprocessing notebook이 실제 분석에 사용된 notebook임을 확인했다. 따라서 notebook 사용 여부는 더 이상 unresolved로 분류하지 않는다. 남은 저자 결정은 CGGA pre-split 원자료와 embedded 실행 산출물의 공개 가능 범위, 81개 후보 선택 이후의 정식 post-selection inference 필요 여부, 외부 cohort 검증 계획, OR≥1.10의 도메인 근거, 독립적인 생물학·assay 검증 범위이다.

# 2. Interpretation-audit table

| ID | Analysis | Original interpretation | Evidence limitation | Revised interpretation | Status |
|---|---|---|---|---|---|
| S3-01 | 전체 7,411-feature Bayesian model | 상위 분자를 molecular effects/signals처럼 읽을 여지 | 모든 계수의 95% CrI가 0 포함; 강한 shrinkage; MCI–CN 계수는 거의 0 | descriptive posterior coefficient ordering이며 feature-level inference가 아님 | 완료 |
| S3-02 | Bayesian prediction | macro OvR AUROC 0.780 중심의 성공 인상 | balanced accuracy 0.485, macro F1 0.433, CN argmax 예측 0건 | 순위 판별, calibration, 확률 배분, argmax 배정을 분리해 보고 | 완료 |
| S3-03 | Restricted Bayesian model | 0을 제외하는 구간을 확인 근거처럼 읽을 위험 | 81개 후보가 같은 개발 데이터에서 사전 선별됨; screening uncertainty와 원공간 multiplicity 미반영 | screen에 조건부인 posterior description; 독립 확인이나 post-selection inference가 아님 | 완료 |
| S3-04 | WrapEvoFS–STABL overlap | cross-method validation | 두 방법 모두 동일 개발 표본 사용 | within-dataset cross-method concordance | 완료 |
| S3-05 | BLiP primary | signature refinement 또는 추가 feature reduction 인상 | primary OR≥1.10, q=0.20에서 81개 전부 유지 | interoperability는 보이나 추가 압축은 없음 | 완료 |
| S3-06 | BLiP sensitivity | 47개 또는 32개 결과가 primary처럼 보일 위험 | q 또는 practical-effect threshold 변경 결과 | 명시적 sensitivity analysis로만 유지 | 완료 |
| S3-07 | Practical-effect PIP | 정확히 0이 아닌 계수의 inclusion probability처럼 오해 가능 | threshold 기반 활동 확률이며 screened model에 조건부 | practical-effect posterior activity probability로 정의 | 완료 |
| S3-08 | CGGA example | portability/generalization 인상 | 한 내부 고정 분할; 외부 기관·인구·assay 검증 없음 | 두 번째 binary disease-domain demonstration | 완료 |
| S3-09 | Feature stability | 대표 medoid가 안정 signature를 확립한다는 인상 | 동일 표본에서 seed만 바꾼 Jaccard 0.247–0.385 | favorable-seed 선택을 방지하는 잠금 규칙이며 안정성 입증은 아님 | 보존·강화 |
| S3-10 | Figure 3/S4A | calibration panels가 본문과 supplement에 중복 | 동일 결과가 두 번 제시됨 | 본문 Figure 3은 predictive reference와 ranking만, calibration은 S4A만 | 완료 |
| S3-11 | Figure 5 split | development가 held-out를 생성하는 듯한 순차 인상 | strict isolation 메시지와 도식 불일치 | split에서 두 partition이 직접 분기하고 evaluation에서만 결합 | 완료 |
| S3-12 | 전체 manuscript focus | 여러 downstream 분석이 공동 주기여처럼 보임 | 각 분석의 증거 수준과 목적이 다름 | core workflow를 중심으로 하고 downstream 분석은 보조적 interoperability로 배치 | 완료 |

# 3. Bayesian wording audit

- Methods의 “Posterior molecular effects” 계열 제목을 “Descriptive posterior coefficient summaries”로 교체했다.
- Results의 해당 제목을 “Descriptive posterior coefficient rankings”로 교체했다.
- 전체 모형에서 상위 feature를 “important protein”, “molecular signal”, “candidate biomarker”로 해석하지 않고 posterior mean의 절댓값에 따른 기술적 순서로 정의했다.
- “Every 95% credible interval for all 7,411 coefficients in every contrast included zero”를 Results에 명시하고, 이 순위가 feature-level inferential evidence나 established molecular association이 아니라고 덧붙였다.
- MCI-versus-CN 계수가 약 ±0.001이고 direction probability가 약 0.5라는 결과를 기술적 순위의 제한 근거로 유지했다.
- 전체 모형을 computational/predictive reference under strong shrinkage로 재배치했다.
- CN OvR AUROC 0.819와 CN sensitivity/F1 0을 함께 보고했다. posterior-mean argmax가 어떤 held-out 참가자에게도 CN을 배정하지 않았다는 결과를 Results, Figure 3 caption, Supplementary Figure S4A caption, Discussion에 유지했다.
- calibration과 uncertainty 결과는 Supplementary Figure S4A에만 남겼으며, 본문 Figure 3과 중복하지 않았다.
- Restricted model의 81개 후보가 locked WrapEvoFS union과 training-only STABL에서 같은 개발 표본을 사용해 구성되었다고 명시했다.
- Restricted-model credible interval은 training-derived screen에 조건부이며 WrapEvoFS/STABL selection variability, screening uncertainty, 원래 7,411-feature space의 multiplicity를 반영하지 않는다고 Methods, Results, Figure 4 caption, Table 4 note, Discussion, Supplementary Table S9 caption에 반영했다.
- Restricted credible interval이 0을 제외하는 경우도 독립 biomarker association 확인으로 해석하지 않도록 수정했다.
- 전체 모델과 restricted 모델을 분리해, 전자는 전체 특징의 강한 shrinkage reference, 후자는 screen에 조건부인 downstream demonstration으로 정의했다.
- 새로운 posterior probability, credible interval, 모형 적합 또는 생물학적 해석은 생성하지 않았다.

# 4. STABL and BLiP audit

STABL은 동일 개발 데이터에서 WrapEvoFS와 일부 후보가 중복된다는 사실을 보여준다. 이는 방법 간 선택 선호의 일치와 interoperability를 보여줄 수 있으나, 외부 복제, 독립 검증, robust biomarker reproducibility 또는 생물학적 확인을 확립하지 않는다. “Five candidates were selected by both…”와 “within-dataset cross-method concordance”를 사용하고 “validated by STABL” 표현은 제거했다.

BLiP은 restricted posterior의 PEP를 singleton group으로 받아 posterior expected-FDR 도구와 연결할 수 있음을 보여준다. 그러나 FDR 해석은 screen과 fitted restricted model에 조건부이고, 후보 선별 불확실성을 포함하지 않으며, 7,411개 원래 predictor 전체에 대한 control이 아니다.

- Primary: OR≥1.10, q=0.20에서 81개를 모두 유지했다. 따라서 더 작은 primary signature나 추가 압축은 생성되지 않았다.
- Sensitivity: q=0.10에서 47개, OR≥1.20과 q=0.20에서 32개를 유지했다. 이 결과는 primary conclusion을 대체하지 않는다.
- OR≥1.10은 임상적으로 확립된 threshold가 아니라 사전 명시된 operational setting으로 기술했다.
- PIP는 practical-effect posterior activity probability이며 spike-and-slab의 exact-nonzero inclusion probability가 아니라고 명시했다.
- BLiP 결과를 biomarker discovery, refined signature identification, successful primary feature reduction 또는 external confirmation으로 설명하지 않았다.

# 5. Figure 5 revision record

- 원래 개념 문제: cohort panel이 development dataset에서 held-out dataset으로 순차 이동하는 것처럼 보일 수 있어 strict split isolation과 충돌했다.
- 수정 source: `analysis/build_revised_figure_sources.py`
- plotting specification: `analysis/figure_specs.json`
- 설계 변경: “All eligible CGGA samples”에서 “Stratified 70:30 split”로 이동한 뒤, development n=214와 locked held-out n=92가 직접 두 갈래로 분기하도록 재작성했다. development branch만 preprocessing, candidate generation, RFECV, GA×5, development-CV ranking, Jaccard medoid locking을 거친다. locked signature/model settings와 held-out branch는 one-time evaluation 지점에서만 결합한다.
- 새 label: “Untouched until signature and model settings were locked.”, “One-time held-out evaluation”, “Development n=214 (110 methylated; 104 unmethylated)”, “Locked held-out n=92 (47 methylated; 45 unmethylated)”.
- provenance wording: 저자 확인에 따라 Figure 5 caption과 Methods에서 해당 notebook을 실제 사용된 preprocessing notebook으로 명시했다. 실행 여부를 unresolved로 두지 않았으며, embedded output과 pre-split raw source 부재는 독립 검증 한계로만 기록했다.
- caption 변경: split 직후 두 partition이 직접 분기하며 development decisions가 held-out outcomes를 사용하지 않았음을 명시했다.
- export: `manuscript/figures/main/Figure_5/Figure_5_CGGA_locked_heldout_evaluation.svg`, `.pdf`, `.png`; Google Docs asset용 `manuscript/google_docs_assets/Figure_5.png`.
- visual validation: SVG/PDF/600-dpi PNG를 재생성하고 raster render에서 branch 방향, 텍스트 잘림, box 겹침, participant/class count, held-out isolation을 확인했다. 최종 manuscript PDF에서도 페이지 단위 검사를 수행했다.

# 6. Manuscript-focus audit

| Section | Previous emphasis | Revised emphasis | Reason |
|---|---|---|---|
| Abstract | software, Bayesian, STABL, BLiP 결과가 병렬적 기여처럼 보임 | auditable development-only workflow, branch-level compression, prespecified medoid locking을 우선; downstream 분석은 secondary | 핵심 기여와 보조 분석의 증거 수준을 분리 |
| Introduction aims | package, CGGA portability, Bayesian/STABL/BLiP를 폭넓게 제시 | ADNI multiclass와 CGGA binary에서 core workflow를 평가하고, downstream 분석은 interoperability 예시로 제한 | 하나의 명확한 연구 질문 유지 |
| Results organization | Bayesian molecular effects와 cross-method validation이 강한 해석을 유도 | full-model predictive reference와 descriptive ranking, candidate-restricted interoperability로 재명명 | 분석 목적과 한계를 제목에서부터 명시 |
| Discussion opening | 다양한 결과의 폭을 강조 | core workflow의 auditability, size control, representative-run locking을 첫 문단에 배치 | 가장 방어 가능한 기여를 중심화 |
| Conclusion | 폭넓은 applicability와 downstream 성공을 암시할 위험 | workflow operation과 compression을 인정하되 superiority, stable biomarkers, external validation, clinical utility는 확립되지 않았다고 결론 | 결과의 증거 수준과 일치 |

# 7. Terminology replacements

| 이전 또는 위험 표현 | 수정 표현 | 적용 원칙 |
|---|---|---|
| cross-method validation | candidate-restricted interoperability analysis; within-dataset cross-method concordance | 동일 개발 데이터 사용은 독립 validation이 아님 |
| portability demonstration | second disease-domain demonstration; separate binary gene-expression example | 한 내부 split은 transportability를 확립하지 않음 |
| biomarker, candidate biomarker | selected predictor; model-derived candidate; exploratory follow-up priority | predictive selection은 biomarker validation이 아님 |
| posterior molecular effects | descriptive posterior coefficient summaries/rankings | 모든 full-model interval이 0 포함 |
| stable signature | locked representative-run signature; seed-sensitive feature set | medoid locking은 stability 입증이 아니라 선택 규칙 표준화 |
| independent confirmation | conditional posterior description; within-dataset agreement | screen과 모델이 같은 개발 데이터에 의존 |
| validated by STABL | selected by both methods within the same development dataset | STABL overlap의 범위 제한 |
| optional downstream analysis | secondary/complementary downstream analysis | 필수 pipeline 단계와 구분하되 사용자 선호에 따라 “optional” 용어 제거 |
| clinically meaningful OR≥1.10 | prespecified operational practical-effect threshold | 임상적 근거가 제공되지 않음 |

# 8. Files modified

Step 3에서 생성하거나 수정한 파일은 다음과 같다.

- `manuscript/WrapEvoFS_manuscript_final_revised_step3.docx`: 영문 본문, 제목·저자 블록, 섹션명, 해석, caption, Figure 1/3/5 교체, 페이지 흐름 수정.
- `manuscript/WrapEvoFS_manuscript_final_revised_step3.pdf`: Word 렌더 기반 최종 PDF.
- `analysis/revise_manuscript.py`: Step 3 문구 교체, caption 교체, 새 manuscript output 경로.
- `analysis/build_revised_figure_sources.py`: Figure 1 locked-split 도식, Figure 3 a/b 전용 구성, Figure 5 direct branching split 재설계.
- `analysis/figure_specs.json`: Figure 3과 Figure 5 크기·source specification 갱신.
- `analysis/validate_step3_revision.py`: Step 1/2 보존, Step 3 해석, Figure 1/3/5, provenance, report 자동 검사.
- `manuscript/figures/main/Figure_1/Figure_1_WrapEvoFS_workflow.svg`, `.pdf`, `.png`: 전문적인 split/locking 도식.
- `manuscript/figures/main/Figure_1/caption.md`: revised Figure 1 caption.
- `manuscript/figures/main/Figure_3/Figure_3_Bayesian_full_model_reference.svg`, `.pdf`, `.png`: a/b만 유지하고 S4A 중복 제거.
- `manuscript/figures/main/Figure_3/caption.md`, `alt_text.txt`: descriptive ranking 및 S4A 위치 명시.
- `manuscript/figures/main/Figure_4/caption.md`: interoperability와 conditional-screening 해석 반영.
- `manuscript/figures/main/Figure_5/Figure_5_CGGA_locked_heldout_evaluation.svg`, `.pdf`, `.png`: locked split direct branching.
- `manuscript/figures/main/Figure_5/caption.md`, `alt_text.txt`: held-out isolation과 one-time evaluation 명시.
- `manuscript/figures/supplementary/Supplementary_Figure_S4A_caption.md`: calibration 결과를 supplement 전용으로 명시.
- `manuscript/google_docs_assets/Figure_1.png`, `Figure_3.png`, `Figure_5.png`: 최신 figure asset.
- `manuscript/google_docs_assets/captions.md`, `alt_text.csv`: figure caption과 accessibility text 동기화.
- `manuscript/tables/main/Table_4_caption.md`: cross-method concordance와 conditional posterior framing.
- `manuscript/tables/supplementary/supplementary_table_captions.md`: S8, S9, S11A, S11B 해석 제한 보강.
- `data/provenance/CGGA_PMID32021566_ALL_GLIOMA_MGMT_preprocessing.ipynb`: 저자 제공 preprocessing notebook의 provenance copy.
- `data/provenance/README.md`: notebook 출처, SHA-256, 확인 가능한 내용과 확인 불가능한 내용을 기록.
- `data/access/README.md`: CGGA 원자료 비포함 및 notebook 기반 확인 범위 갱신.
- `README.md`: Step 3 manuscript, figure, provenance, 해석 경계 안내.
- `audit/step3_interpretation_audit.json`: Step 3 machine-readable 검사 결과.
- `audit/step3_validation/visual_inspection_report.md`: Word/Poppler 기반 39쪽 전 페이지 시각 검증 기록.
- `audit/reproducibility_audit.json`: 최종 Step 3 산출물과 남은 재현성 한계 갱신.
- `REVISION_REPORT_STEP3.md`: 본 보고서.
- `REVISION_SUMMARY_STEPS1_TO_3.md`: 3단계 통합 요약.
- `checksums.sha256`: 최종 repository manifest.

# 9. Material moved to Supplementary Information

- Main Figure 3에 중복되던 calibration 및 posterior predictive-uncertainty 3개 패널을 제거하고 Supplementary Figure S4A에만 보존했다. 관련 Results 문단은 S4A를 직접 참조하며, CN probability assignment, confidence, margin, calibration 결과는 삭제하지 않았다.
- Full-model sampler trace, R-hat, ESS는 Supplementary Figure S4B와 Supplementary Tables S5–S7에 유지했다.
- 전체 posterior coefficient ranking 세부 값은 Supplementary Table S8에 유지하고 main text에는 핵심 제한만 남겼다.
- STABL path와 전체 81-candidate provenance는 Supplementary Figure S5 및 Supplementary Table S9에 유지했다.
- Restricted-model diagnostics와 BLiP primary/sensitivity 세부 결과는 Supplementary Figure S6 및 Supplementary Tables S10–S11에 유지했다.
- 이동 또는 축약 과정에서 음성 결과, CN failure, zero-containing intervals, primary all-81 BLiP 결과를 포함한 어떤 분석 결과도 삭제하지 않았다.

# 10. Unresolved author questions

1. 실제 사용이 확인된 CGGA preprocessing notebook의 pre-split 원자료, 원자료 SHA-256, embedded 실행 output, 제거·대치된 값의 수, batch 처리 기록을 공개하거나 제한적 audit 환경에서 제공할 수 있는가?
2. 81개 후보 screen 이후의 credible interval을 feature-level inference로 사용하려면 participant-resampling을 포함한 selection-aware/post-selection 분석을 추가할 것인가? 현재 원고는 이를 수행하지 않았다고 명시한다.
3. ADNI와 CGGA 결과를 넘어서는 portability 또는 external validation 주장을 위해 독립 cohort, 기관, population, assay platform 검증을 계획하는가?
4. OR≥1.10 practical-effect threshold에 임상적 또는 생물학적 근거가 있는가? 없다면 현재의 operational-setting 표현을 유지해야 한다.
5. 선택된 protein, metabolite, gene에 대해 독립 assay replication, biological mechanism study, preregistered external confirmation을 수행할 계획이 있는가?
6. 원래 ADNI split-generation manifest, participant identifiers, upstream preprocessing report, complete run directories, 정확한 empirical source commit을 복구할 수 있는가?
7. BLiP package에 남아 있는 `[BLiP citation required]` 자리표시자는 저자가 최종 reference 단계에서 채워야 한다. Step 3 지시에 따라 이 citation placeholder는 수정하지 않았다.

# 11. Validation checklist

- [x] Full-model rankings를 descriptive/non-inferential로 표시했다.
- [x] 7,411개 전체 계수의 95% credible interval이 0을 포함한다는 결과를 올바르게 해석했다.
- [x] Restricted-model interval을 screen에 조건부라고 표시했다.
- [x] Screening uncertainty와 original-space multiplicity 미반영을 명시했다.
- [x] 부적절한 cross-method validation 용어를 제거했다.
- [x] STABL overlap을 독립 validation이나 biological confirmation으로 제시하지 않았다.
- [x] Primary BLiP가 81개 후보를 모두 유지했다는 사실을 명시했다.
- [x] BLiP sensitivity 결과를 secondary로 유지했다.
- [x] Biological claim을 hypothesis-generating candidate description으로 제한했다.
- [x] CGGA에서 portability를 과장하지 않았다.
- [x] Figure 5가 fixed split에서 두 partition으로 직접 분기한다.
- [x] Held-out data가 development 단계에서 시각적으로 격리되어 있다.
- [x] Figure 1의 넘치는 빨간 문장과 부자연스러운 화살표를 제거하고 논문형 도식으로 정리했다.
- [x] Figure 3과 Supplementary Figure S4A의 중복을 제거했다.
- [x] Core software contribution이 Abstract, Introduction, Discussion, Conclusion에서 중심이다.
- [x] Bayesian, STABL, BLiP는 clearly secondary이며 core pipeline에 필수적이지 않다.
- [x] Abstract와 Conclusion이 biomarker validation을 주장하지 않는다.
- [x] References, citations, bibliography, citation placeholder를 수정하지 않았다.
- [x] Step 1과 Step 2의 분할, 분모, 성능 불확실성, 안정성, 재현성 관련 수정을 보존했다.
