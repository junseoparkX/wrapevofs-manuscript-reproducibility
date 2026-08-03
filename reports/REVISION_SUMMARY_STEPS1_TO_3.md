# WrapEvoFS 수정 요약: Steps 1–3

## 전체 요약

세 단계의 수정은 새 성능 결과를 만들어 원고를 강하게 보이게 하는 작업이 아니라, 기존 artifact가 실제로 지지하는 범위 안에서 방법, 수치, 시각 메시지, 해석을 일치시키는 작업이었다.

- 1단계: repository와 manuscript의 사실관계, 데이터 분할, 설정, 전처리, table/figure 수치, 재현성 경계를 감사했다.
- 2단계: 압축 분모, held-out 성능 차이, bootstrap interval, GA seed variability, ablation, 우월성·동등성·비열등성 부재를 원고 전반에 일관되게 반영했다.
- 3단계: Bayesian, STABL, BLiP, biomarker, portability 해석을 보정하고, core contribution을 development-only stochastic feature-selection workflow와 representative-run locking으로 재집중했다. Figure 1과 Figure 5의 split/locking 구조를 바로잡고 Figure 3/S4A 중복을 제거했다.

최종 중심 주장은 다음과 같다.

> WrapEvoFS는 감사 가능한 개발 데이터 전용, 크기 제어형 확률적 특징 선택 workflow이며, held-out 결과를 사용하지 않고 대표 stochastic run을 잠그는 사전 명시 규칙을 제공한다.

현재 증거는 workflow operation과 branch-level compression을 지지하지만 predictive superiority, feature-set stability, external validation, validated biomarkers 또는 clinical utility를 확립하지 않는다.

## 1단계 요약

1단계에서는 원고, 표, 그림 source, package 설정, aggregate artifact를 대조했다. ADNI는 제공된 532/133 fixed internal partition으로, CGGA는 214/92 locked internal partition으로 정리했다. Package가 binary와 multiclass를 모두 지원한다는 점, branch별 preprocessing/scaling 근거, RFECV와 GA 설정, Jaccard medoid locking, fixed-random-forest primary CGGA analysis를 문서화했다.

완전한 end-to-end 재현을 막는 항목도 명시했다. ADNI participant-level matrix, split-generation manifest, upstream preprocessing report, complete run directory, exact empirical commit은 제공되지 않았다. CGGA preprocessing notebook은 저자가 실제 사용된 notebook이라고 확인했으므로 upstream-unresolved로 분류하지 않는다. 다만 pre-split raw source file, embedded execution output, source hash, removed/imputed counts, batch-processing evidence가 없어 제3자의 완전한 raw-to-final 독립 검증은 제한된다.

## 2단계 요약

2단계에서는 성능과 압축 claim을 재계산 가능한 aggregate 수치에 맞췄다.

- ADNI compression은 original 7,411 features가 아니라 각 first-stage signature를 분모로 보고했다.
- CGGA 54.3%–72.9% reduction도 24,326개 전체 gene이 아니라 branch-specific Direct set을 분모로 명시했다.
- ADNI locked-minus-first-stage metric change가 branch와 metric에 따라 양·음 방향으로 달라짐을 보고했다.
- 평균 AUROC ratio 98.6%는 descriptive summary이며 equivalence/non-inferiority 증거가 아님을 명시했다.
- CGGA full-medoid–minus-RFECV-only paired bootstrap interval이 음수와 양수를 모두 포함하므로 predictive superiority를 확립하지 않았다고 정리했다.
- Jaccard 0.247–0.385는 seed-dependent variability를 보여주며 stable biomarker signature를 입증하지 않는다고 명시했다.
- Run locking은 favorable seed를 사후 선택하지 않게 하는 procedural safeguard이지 selection variability를 제거하는 기법으로 과장하지 않았다.

## 3단계 요약

3단계에서는 해석과 manuscript focus를 재구성했다.

- 모든 7,411개 full-model coefficient interval이 0을 포함하므로 posterior ranking을 descriptive ordering으로 제한했다.
- CN OvR AUROC와 CN argmax prediction 0건을 함께 강조했다.
- Restricted Bayesian interval과 BLiP expected-FDR를 training-derived 81-candidate screen에 조건부로 정의했다.
- “cross-method validation”을 within-dataset concordance/interoperability로 교체했다.
- STABL overlap을 독립 확인으로 제시하지 않았다.
- Primary BLiP가 81개 모두를 유지해 추가 압축을 제공하지 않았음을 명확히 했다.
- OR≥1.10을 universal clinical threshold가 아니라 operational setting으로 제한했다.
- CGGA를 portability가 아니라 second binary disease-domain demonstration으로 표현했다.
- Figure 1의 넘치는 빨간 경계 문장과 화살표 충돌을 제거하고 fixed split–locking–one-time evaluation을 논문형 branching diagram으로 재작성했다.
- Figure 5는 split 직후 development와 locked held-out가 직접 갈라지도록 재설계했다.
- Main Figure 3의 calibration/uncertainty panel을 제거하고 Supplementary Figure S4A에만 유지했다.

## 남은 미해결 사항

- ADNI 원 participant-level data, split-generation manifest, upstream preprocessing report, exact empirical code commit, complete run directories가 없다.
- 실제 사용이 저자 확인된 CGGA notebook의 pre-split raw source files, raw hashes, embedded execution outputs, removed/imputed value counts, batch-processing evidence가 없다. 이는 notebook 사용 여부의 불확실성이 아니라 독립 실행기록 검증의 한계이다.
- 두 empirical demonstration은 각각 하나의 internal fixed split이며 외부 cohort validation이 아니다.
- ADNI participant-level paired difference artifact가 없어 locked versus first-stage equivalence/non-inferiority를 평가하지 못했다.
- Adaptive selection 전체를 포함하는 nested resampling 또는 selection-aware uncertainty가 없다.
- Restricted Bayesian credible interval과 BLiP expected-FDR는 candidate screening uncertainty를 포함하지 않는다.
- OR≥1.10의 임상적·생물학적 threshold 근거가 없다.
- 선택된 feature에 대한 독립 assay replication, causal/mechanistic study, preregistered biomarker validation이 없다.
- `[BLiP citation required]` 자리표시자는 저자 확인이 필요하나 Step 3 범위에서는 보존했다.

## 수정된 원고 섹션

- Title/author/affiliation block: 논문 형식의 중앙 정렬과 계층을 유지했고 전문적인 제목을 사용했다.
- Abstract: core workflow, compression, branch-dependent performance, secondary downstream interoperability, 부정적 한계를 함께 제시했다.
- Introduction final aim paragraph: core workflow 평가와 secondary downstream demonstration을 분리했다.
- Overall analytical workflow: fixed split, development-only stages, locked one-time held-out evaluation을 명확히 했다.
- Software implementation: binary와 multiclass 지원을 명시했다.
- ADNI 및 CGGA Methods: split와 preprocessing 경계를 정리했다.
- Bayesian Methods: full-feature reference와 candidate-restricted conditional model을 분리했다.
- Results headings: molecular-effects/validation 언어를 descriptive ranking/interoperability로 변경했다.
- Results: CN failure, all-zero-containing full-model intervals, conditional restricted intervals, primary BLiP all-81 결과를 강화했다.
- Discussion: core workflow 기여, predictive results, Bayesian limitations, STABL/BLiP limitations, CGGA 범위, 전체 limitations를 분리했다.
- Conclusion: workflow operation은 인정하되 superiority, stable biomarker, external validation, clinical utility를 부정했다.
- Data and code availability: provenance notebook과 남은 raw-data 한계를 반영했다.
- Supplementary Appendix B/C headings와 captions: descriptive/conditional 해석으로 조정했다.

## 수정된 그림과 표

- Figure 1: fixed split branching, locked signature/settings, one-time held-out evaluation, core versus secondary analysis map으로 재설계.
- Figure 3: main figure를 panels a/b로 축약; calibration/uncertainty duplicate를 제거; panel b title/legend 위치와 x-axis 여백을 정리.
- Figure 4 caption: validation 대신 interoperability; restricted intervals와 BLiP의 conditional interpretation 명시.
- Figure 5: all eligible samples에서 fixed split 후 development/locked held-out direct branching; participant와 class count 유지.
- Figure 6: Step 2에서 확보한 ablation, size guidance, Jaccard variability, paired interval 해석을 보존.
- Supplementary Figure S4A: calibration과 posterior predictive uncertainty의 유일한 위치로 지정.
- Table 4 title/note: within-dataset concordance와 conditional posterior evidence로 재표현.
- Supplementary Tables S8, S9, S11A, S11B captions: descriptive rankings, screened-candidate conditioning, interval availability, primary/sensitivity distinction을 강화.
- Table 1의 ADNI/CGGA cohort·feature inventory와 Table 5 CGGA denominator는 Step 1/2 값 그대로 유지.

## 약화하거나 재구성한 주장

- performance preservation → branch-specific descriptive change; equivalence/non-inferiority 미검정.
- predictive superiority → 확립되지 않음.
- stable signature → seed-sensitive representative-run signature.
- molecular effects/signals → descriptive posterior coefficient ordering.
- cross-method validation → within-dataset cross-method concordance/interoperability.
- STABL validation → 동일 데이터에서의 중복 선택.
- BLiP signature refinement → primary all-81 retention, no additional compression.
- biomarker evidence → hypothesis-generating model-derived candidates.
- CGGA portability/generalization → second internal disease-domain demonstration.
- reproducible empirical analysis → auditable aggregate trail은 있으나 exact end-to-end rerun은 불가능.

## 수행하지 않은 분석

- 새로운 Bayesian fit, posterior sampling, STABL fit, BLiP fit을 수행하지 않았다.
- 추가 GA/RFECV run이나 long empirical rerun을 수행하지 않았다.
- 새로운 participant-level bootstrap 또는 paired test를 수행하지 않았다.
- equivalence 또는 non-inferiority margin을 사후 설정하지 않았다.
- 외부 validation, cross-site transport analysis, assay replication을 수행하지 않았다.
- selection-aware Bayesian inference 또는 formal post-selection inference를 수행하지 않았다.
- 새로운 biological pathway/mechanism analysis를 수행하지 않았다.
- 참고문헌 검색, citation 변경, bibliography 추가를 수행하지 않았다.

## 최종 내부 일관성 평가

원고의 수치·분모·split·preprocessing·figure caption·해석은 제공된 aggregate artifact와 Step 1/2 audit 범위 안에서 일관된다. Figure 1과 Figure 5는 development와 held-out를 분리하고 one-time evaluation에서만 결합한다. Figure 3과 Supplementary Figure S4A는 더 이상 같은 panel을 중복하지 않는다. Full/restricted Bayesian, STABL, BLiP의 증거 수준은 각각 분리되며, core WrapEvoFS claim은 downstream 분석의 성공에 의존하지 않는다.

다만 위의 provenance, external validation, selection uncertainty, biological confirmation 문제가 남아 있으므로 원고를 “모든 재현성·해석 문제가 완전히 해결된 상태”로 표현해서는 안 된다. 현재 상태는 제출 전 과학적·편집적 일관성을 크게 개선한 revised manuscript이며, 저자 확인과 독립 데이터가 필요한 한계는 명시적으로 남아 있다.

## 저자 확인이 필요한 사항

1. CGGA raw/source provenance와 실행 output 공개 가능 여부.
2. ADNI exact split 및 preprocessing provenance 복구 가능 여부.
3. `[BLiP citation required]` 자리표시자에 들어갈 정확한 reference.
4. OR≥1.10 threshold의 사전 근거 또는 operational-setting 표현 유지 여부.
5. Independent external cohort validation 계획 여부.
6. Selection-aware/post-selection inference 추가 여부.
7. 선택 feature에 대한 assay/biological replication 계획 여부.
8. 현재 제목 “WrapEvoFS: Evolutionary Feature Selection for Controlled Signature Compression in High-Dimensional Biomedical Data”의 최종 저자 승인.
