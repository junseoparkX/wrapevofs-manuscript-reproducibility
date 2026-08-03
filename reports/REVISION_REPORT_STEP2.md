# 1. Executive summary

Step 2에서는 WrapEvoFS 원고 전반의 성능 유지, 안정성, GA의 추가 가치, 내부 검증 범위에 관한 주장을 저장된 기계 판독형 결과와 통계 설계에 맞게 재조정하였다. Abstract, Methods, Results, Discussion, Limitations, Conclusion, 주·보조 그림 캡션, 표 주석을 함께 점검하였다.

주요 수정은 다음과 같다.

- “maintained/preserved performance”를 정식 동등성 또는 비열등성 결론처럼 읽히지 않도록 삭제하거나 제한하였다.
- ADNI의 절대 macro OvR AUROC 변화(−0.034~+0.002)를 98.6% 평균 비율보다 먼저 제시하였다.
- 98.6%를 세 branch별 `100 × locked/first-stage` 비율의 산술평균으로 명시하고, 설명적 요약값으로만 유지하였다.
- 고정 held-out set 격리와 반복적인 development-CV 재사용에 따른 적응적 선택 낙관성을 구분하였다.
- GA의 기여를 예측 우월성이 아니라 크기 유도 부분집합 탐색, 반복 실행 기록, 사전 규정된 대표 실행 잠금 및 감사 가능성으로 한정하였다.
- medoid locking을 안정적인 biomarker 발견으로 해석하지 않고, 확률적 실행 중 하나를 재현 가능한 규칙으로 선택하는 절차로 기술하였다.
- seed 변화와 participant resampling을 명시적으로 구분하였다.
- ADNI의 최종 27–30개 feature 크기가 최대 30의 RFECV 탐색 한계 및 크기 페널티에 의해 부분적으로 설계된 값임을 밝혔다.
- RFECV AUROC, GA/실행 순위 balanced accuracy, headline macro OvR AUROC라는 단계별 metric 차이를 “staged heuristic”으로 설명하였다.
- 단일 고정 내부 split, 누락된 단순 size-matched baseline, random-forest evaluator 의존성, 임상 준비성 부재를 Limitations에 포함하였다.

유지한 주장은 held-out set이 잠금 전 개발에 사용되지 않았다는 점, 후보 집합이 크게 축소되었다는 점, 사전 규정된 locking 절차가 감사 가능하다는 점, 그리고 저장된 held-out point estimate와 불확실성 구간 자체이다. 해결되지 않은 문제는 formal equivalence/non-inferiority margin 및 paired ADNI difference가 없다는 점, 대체 split 또는 외부 cohort 분석이 없다는 점, 독립 classifier family에 대한 포괄적 검증이 없다는 점이다.

새 모델 적합, 새 bootstrap, 새 confidence interval, 새 equivalence/non-inferiority 분석은 수행하지 않았다. 아래의 차이와 비율은 기존 CSV의 저장값을 재계산하여 문구를 검증한 것이며 새로운 분석 결과가 아니다. Step 3은 수행하지 않았다.

# 2. Claim-audit table

| ID | Claim | Manuscript location | Evidence available | Original strength | Revised wording | Status |
|---|---|---|---|---|---|---|
| C01 | 압축 후 discrimination이 유지되었다 | Abstract, ADNI Results, Discussion, Conclusion, Figure 2 | branch별 held-out point estimate와 별도 CI; ADNI paired difference 없음 | 동등성/보존을 암시 | 변화는 branch와 metric에 따라 달랐고 macro OvR AUROC 차이는 −0.034~+0.002였다고 기술 | resolved |
| C02 | 평균 AUROC의 98.6%가 유지되었다 | Abstract, Figure 2, Supplementary Figure S19 | 세 branch별 비율의 산술평균 98.5846% | headline 통계 결론처럼 강조 | 절대 차이 뒤에 설명적 비율로 제시; 동등성·비열등성 근거가 아님을 명시 | resolved |
| C03 | CGGA 압축 성능이 유지되었다 | CGGA Results, Table 5, Figures 5–6, Discussion | full-medoid−RFECV-only paired bootstrap 9개 구간 모두 음·양 값을 포함 | no loss/유지 암시 | 표본 크기 내 명확한 gain 또는 loss가 확립되지 않았고 동등성·비열등성을 검정하지 않았다고 기술 | resolved |
| C04 | held-out 격리로 개발 점수가 편향되지 않았다 | Methods, Discussion, Limitations, Figure 1 | 잠금된 test set 격리는 확인되나 같은 development sample을 반복 재사용 | test isolation을 unbiased validation처럼 해석 가능 | development-CV는 적응적 모델 선택으로 낙관적일 수 있음을 명시 | resolved |
| C05 | 두 실증이 robustness/외부 검증을 제공한다 | Methods, Discussion, Limitations | ADNI와 CGGA 각각 단일 고정 내부 split | 일반화 가능성 암시 | internal locked-split demonstration이며 대체 분할 변동성과 population transportability를 평가하지 않았다고 기술 | resolved |
| C06 | GA가 예측을 개선한다 | Abstract, Results, Discussion, Figure 6 | RFECV-only 대비 paired difference CI가 0을 가로지름 | incremental predictive refinement/개선 암시 | GA의 확인된 역할을 size-guided stochastic search와 auditability로 제한; 우월성 미확립 | resolved |
| C07 | medoid signature가 안정적이다 | Abstract, Results, Discussion, Figures 2/6 | top-three mean Jaccard 0.247–0.385 | 높은 안정성/robust signature 암시 | 낮음~중간 정도의 seed-dependent agreement이며 medoid는 variability를 제거하지 않는다고 기술 | resolved |
| C08 | 반복 GA가 표본 안정성을 평가한다 | Methods, captions, Limitations | 동일 development sample에서 seed만 변화 | sample stability로 오해 가능 | algorithmic seed variability만 평가하며 participant resampling stability가 아님을 명시 | resolved |
| C09 | top-three medoid가 최적의 locking rule이다 | Methods, Results, Discussion | 5회 중 dev-CV 상위 3개의 관측 실행 medoid; 이론적 최적성 근거 없음 | 최적/생물학적 대표성 암시 | pragmatic, prespecified operational choice로 기술 | resolved |
| C10 | 27–30개가 데이터가 발견한 자연적 크기다 | Methods, Results, Discussion | ADNI RFECV 상한 30, GA size penalty λ=0.015 | 자연적 최적 signature size 암시 | RFECV-derived target 및 명시적 size preference에 의해 부분적으로 설계됨을 기술 | resolved |
| C11 | 파이프라인이 하나의 통합 metric을 최적화한다 | Methods, Supplementary Table S1A, Discussion | RFECV=weighted OvR AUROC; GA/ranking=balanced accuracy; headline=macro OvR AUROC | 통합 목적함수처럼 서술 | 서로 다른 목적의 staged heuristic이며 scoring 조합은 사전 지정된 설계 선택이라고 기술 | resolved |
| C12 | GA-medoid가 단순 대안보다 우수하다 | Limitations, Figure 6 | 일부 component ablation만 존재 | 광범위한 우월성 암시 | size-matched top-k, random subset, consensus, Elastic Net, greedy selection 등이 없어 완전한 우월성 비교가 아니라고 기술 | resolved |
| C13 | 선택 feature가 classifier-agnostic하다 | Methods, Discussion, Limitations | RFECV, GA fitness, 주 held-out 비교가 RF 중심; Boruta-RF도 RF 사용 | 보편적 feature utility 암시 | 보고 결과는 공통 RF evaluator 아래의 utility를 반영하며 독립 classifier family 검증이 부족하다고 기술 | resolved |
| C14 | 실증 성능이 임상 준비성을 뒷받침한다 | Abstract, Discussion, Conclusion, Limitations | ADNI BA/F1 약 0.58, AUROC 약 0.78–0.81; CGGA AUROC 약 0.65–0.70 | translational/clinical readiness로 확장 가능 | workflow demonstration 및 moderate discrimination으로 한정; diagnostic-ready 또는 clinical utility가 아님을 명시 | resolved |
| C15 | nested CGGA sensitivity가 전체 feature-selection pipeline을 검증한다 | Supplementary Figure S9/Table S22, Limitations | 잠긴 signature 이후 secondary evaluator tuning만 nested | 전체 pipeline nested validation으로 오해 가능 | upstream feature selection의 full nested validation이 아님을 명시 | resolved |

# 3. Performance-language audit

| 표현군 | 판정 및 조치 |
|---|---|
| maintained | 정식 성능 유지 결론으로 사용된 경우 삭제하였다. 남은 문구는 “not established”와 같이 부정·제한 맥락뿐이다. |
| preserved | performance preservation을 단정한 문구를 제거하였다. References/파일 보존 같은 비통계적 용례는 유지하였다. |
| retained | “BLiP retained features/draws”처럼 선택 여부를 나타내는 사실적 용례는 유지하였다. AUROC retained/retention은 설명적 ratio로 재명명하고 공식 동등성 근거가 아님을 명시하였다. |
| equivalent | equivalent performance라는 긍정적 결론은 사용하지 않았다. “equivalence was not established/tested”만 허용하였다. |
| non-inferior | margin이 없으므로 긍정적 비열등성 표현을 모두 배제하였다. “non-inferiority was not tested/established”만 유지하였다. |
| superior | GA 또는 locked signature의 predictive superiority를 주장하지 않았다. paired CI가 양·음 값을 모두 포함함을 근거로 우월성 미확립을 명시하였다. |
| improved | prediction/discrimination improvement 표현을 삭제하거나 descriptive point estimate로 제한하였다. |
| no loss | “no clear gain or loss was established within the available sample size”로 수정하였다. 이는 absence of loss의 증거가 아니라 불확실성에 대한 설명이다. |
| similar | “compatible with similar discrimination”은 wide uncertainty 및 equivalence 미확립 문장과 함께만 사용하였다. |
| comparable | formal 비교 결론으로 사용하지 않았다. 별도 CI 중첩은 paired equivalence의 근거로 해석하지 않았다. |

ADNI에는 first-stage와 locked prediction의 participant-level paired bootstrap difference 파일이 확인되지 않았다. 따라서 별도 confidence interval의 중첩이나 비유의성을 성능 보존으로 해석하지 않았다. CGGA paired bootstrap difference는 full-medoid와 RFECV-only 비교이며, 모든 구간이 0을 포함해 predictive superiority를 지지하지 않는다. 또한 사전 정의된 margin이 없으므로 동등성이나 비열등성도 지지하지 않는다.

# 4. Stability-language audit

| 표현 | Step 2 해석 |
|---|---|
| stable | feature signature에 사용하지 않았다. MCMC convergence 등 다른 기술적 맥락은 문맥별로 구분하였다. |
| reproducible | 결과 feature 자체가 아니라 실행 가능한 절차, 사전 규정된 locking rule, artifact provenance에 한정하였다. |
| robust | 대체 participant split, cohort, batch, classifier에 대한 결과가 없으므로 biomarker robustness를 주장하지 않았다. |
| representative | medoid는 상위 세 관측 실행 중 규칙에 따라 고른 representative run이며 생물학적으로 대표적인 signature가 아니다. |
| agreement | Jaccard 0.247–0.385를 낮음~중간 정도의 seed-dependent agreement로 직접 해석하였다. |
| medoid | stochastic search 이후 deterministic한 최종 실행 선택 규칙이지만 underlying selection variability를 제거하지 않는다고 밝혔다. |
| stochastic variability | 동일 development sample에서 seed 변화에 따른 algorithmic search variability로 한정하였다. |

반복 GA는 participant resampling, cohort composition, measurement variation, batch effect 또는 대체 train/test partition에 대한 민감도를 평가하지 않는다. 따라서 “reproducible selection protocol”과 “reproducible biomarker”를 명확히 분리하였다.

# 5. Metric-alignment table

| Stage | Metric | Purpose | Data used | Limitation |
|---|---|---|---|---|
| ADNI first-stage SVM-L1 | balanced accuracy | 후보 feature 생성/모델 선택 | development sample 내부 CV | downstream RF utility와 동일 목적함수가 아님 |
| ADNI first-stage XGBoost | 설정 기반 `auto` scoring | 후보 feature 생성/튜닝 | development sample 내부 CV | branch 간 목적함수 불일치 가능 |
| ADNI first-stage Boruta-RF | RF importance 기반 relevance | 후보 feature 생성 | development sample | 예측 metric 최적화와 직접 동일하지 않음 |
| RFECV | weighted one-vs-rest AUROC | GA의 soft target size 제공 | development sample 내부 CV | balanced-accuracy 최적 크기를 보장하지 않음; ADNI max 30 |
| GA fitness | size penalty가 포함된 balanced accuracy | target 근처 subset 탐색 | 동일 development sample 내부 평가 | 반복 적응적 재사용으로 CV 낙관성 가능; 통합 AUROC 목적함수 아님 |
| GA run ranking | balanced accuracy | 5회 실행 중 상위 3개 식별 | 동일 development sample CV | favourable development realization 선택 가능; test set은 사용하지 않음 |
| medoid locking | top-three 내부 mean Jaccard | 관측 실행 중 대표 실행의 사전 규정 선택 | 같은 development sample의 seed별 실행 | 성능 최적화 또는 participant-resampling 안정성 기준이 아님 |
| ADNI held-out evaluation | balanced accuracy, macro F1, macro OvR AUROC | 잠긴 signature의 내부 고정 split 평가 | 133명 held-out set | 한 번의 split이며 paired difference artifact 없음 |
| ADNI headline reporting | 절대 macro OvR AUROC 차이; 보조적으로 branch ratio 평균 | branch별 held-out 변화 요약 | held-out point estimate | 평균 ratio가 branch/metric heterogeneity를 숨길 수 있어 절대 차이를 우선 제시 |
| CGGA first-stage selection | branch-specific selector objective | 24,326개에서 branch 후보 생성 | development n=214 | 서로 다른 selector 목적을 직접 통합하지 않음 |
| CGGA RFECV | AUROC | soft target size | development CV | GA accuracy와 metric 불일치 |
| CGGA GA fitness | size-penalized accuracy | target 근처 subset 탐색 | development sample | adaptive reuse 및 RF evaluator 의존 |
| CGGA lock audit/ranking | development-CV AUROC | 저장된 후보의 순위 및 locking audit | development sample | fitness와 ranking metric 조합은 prespecified design choice |
| CGGA held-out evaluation | AUROC, AUPRC, balanced accuracy | 고정 RF로 Direct/locked/ablation 비교 | held-out n=92 | 단일 내부 split, wide interval, 0.5 threshold |

따라서 전체 절차는 하나의 통합 목적함수 최적화가 아니라 서로 다른 단계별 목적을 연결한 staged heuristic으로 해석하였다.

# 6. Files modified

- `analysis/revise_manuscript.py`: Abstract, Methods, Results, Discussion, Limitations, Conclusion, 주·보조 캡션과 표 주석의 Step 2 문구 및 Step 2 출력 경로를 반영하였다.
- `analysis/build_revised_figure_sources.py`: Figure 2의 “performance retained” 제목을 설명적 metric ratio로 변경하고 Figure 6의 AUROC/Direct ratio 주석과 prespecified run 1 설명을 정리하였다.
- `analysis/validate_step2_claims.py`: Step 2 수치·문구·reference·수식 보존 검증기를 추가하였다.
- `README.md`: 유지/우월성 과장을 제거하고 고정 split, 적응적 재사용, seed-only variability, RF 의존성을 요약하였다.
- `manuscript/figures/main/Figure_1/caption.md`: held-out isolation과 development-CV 낙관성을 구분하였다.
- `manuscript/figures/main/Figure_2/*`: 절대 차이와 설명적 ratio, medoid/Jaccard 해석을 반영해 SVG/PDF/PNG 및 caption을 갱신하였다.
- `manuscript/figures/main/Figure_4/caption.md`: 기존 Step 1 구조와 맞추어 “Optional”을 “Complementary”로 통일하였다.
- `manuscript/figures/main/Figure_5/caption.md`: 별도 CI가 동등성·비열등성을 확립하지 않음을 명시하였다.
- `manuscript/figures/main/Figure_6/*`: descriptive AUROC ratio, participant-resampling과 다른 seed variability, paired CI 해석을 반영해 SVG/PDF/PNG 및 caption을 갱신하였다.
- `manuscript/figures/supplementary/Supplementary_Figure_S7_caption.md`, `Supplementary_Figure_S8_caption.md`, `Supplementary_Figure_S9_caption.md`: 각각 formal equivalence 부재, seed-only variability, evaluator-only nested sensitivity 범위를 명시하였다.
- `manuscript/tables/main/Table_5_caption.md`: 별도 interval이 equality/equivalence/non-inferiority test가 아님을 명시하였다.
- `manuscript/tables/supplementary/Supplementary_Table_captions.md`: S14, S16–S19, S22의 locking, seed variability, descriptive ratio, nested sensitivity 범위를 보정하였다.
- `manuscript/google_docs_assets/captions.md`, `alt_text.csv`, Figure 2/6 PNG: Google Docs용 설명과 그림을 본문과 동기화하였다.
- `manuscript/figures/main/Figure_2/alt_text.txt`, `Figure_6/alt_text.txt`: 접근성 설명을 통계적 해석과 일치시켰다.
- `manuscript/WrapEvoFS_manuscript_final_revised_step2.docx` 및 `.pdf`: Step 2 최종 전달본이다.
- `audit/step2_claim_audit.json`: 자동 검증 결과를 기록하였다.
- `audit/reproducibility_audit.json`, `audit/repository_manifest.csv`: Step 2 최종 산출물 경로와 repository inventory를 갱신하였다.

References, bibliography entries, citation placeholders 및 related-work text는 수정하지 않았다. 기계 판독형 원결과 CSV의 값이나 컬럼은 변경하지 않았다.

# 7. Numerical statements checked

- ADNI macro OvR AUROC:
  - SVM-L1: 0.782 → 0.784, 표시 반올림 차이 +0.002; 저장값 차이 +0.00145.
  - XGBoost: 0.809 → 0.775, 차이 −0.034.
  - Boruta-RF: 0.790 → 0.788, 표시 반올림 차이 −0.002; 저장값 차이 −0.00180.
  - 표시 반올림 범위: −0.034~+0.002.
- ADNI balanced accuracy 저장값 차이: SVM-L1 −0.00999, XGBoost +0.02906, Boruta-RF −0.04153.
- ADNI macro F1 저장값 차이: SVM-L1 −0.00358, XGBoost +0.05212, Boruta-RF −0.04978.
- 98.6% 계산: 각 branch의 `100 × locked macro OvR AUROC / first-stage macro OvR AUROC`를 계산한 뒤 세 값을 산술평균한 98.584621%를 소수점 한 자리로 반올림하였다. ratio of means(98.55659%)가 아니다.
- ADNI top-three locked-medoid mean Jaccard: SVM-L1 0.3817, XGBoost 0.2474, Boruta-RF 0.3846. 높은 안정성으로 해석하지 않았다.
- ADNI signature size: first-stage 110/174/96에서 locked 29/27/30으로 감소. 27–30은 RFECV max 30 및 GA size penalty의 영향을 받는다.
- CGGA Direct/locked full-medoid signature size: SVM-L1 35/16, XGBoost 70/19, Boruta-RF 26/9.
- CGGA locked held-out AUROC: SVM-L1 0.652, XGBoost 0.702, Boruta-RF 0.695; wide bootstrap interval을 고려해 임상 준비성을 주장하지 않았다.
- CGGA full-medoid−RFECV-only paired bootstrap: 3 methods × 3 metrics의 9개 CI 모두 음수와 양수를 포함하였다. 우월성, 동등성, 비열등성 어느 것도 확립하지 않는다.
- ADNI paired first-stage−locked difference: participant-level paired artifact가 없어 계산하거나 추정하지 않았다.
- 원고의 16개 display-equation paragraph와 reference section paragraph text는 Step 1 전달본과 동일하게 보존하도록 검증 대상으로 설정하였다.

# 8. Unresolved author questions

1. 후속 연구에서 동등성 또는 비열등성을 평가하려면, 어떤 임상·과학적 근거로 metric별 margin을 사전에 정할 것인가?
2. RFECV의 weighted OvR AUROC와 GA/run ranking의 balanced accuracy를 결합한 이유를 프로토콜 또는 domain rationale로 더 구체화할 수 있는가?
3. 5회 실행, 상위 3회, mean Jaccard, 관측 실행 medoid를 선택한 사전 근거 또는 sensitivity specification이 존재하는가?
4. ADNI first-stage와 locked 모델의 participant-level prediction 파일을 확보하여 paired difference CI를 계산할 수 있는가?
5. size-matched top-k, random subset, selection-frequency consensus, Elastic Net 또는 greedy selection 중 어떤 단순 baseline을 우선 비교할 것인가?
6. 대체 development–test split, repeated outer CV 또는 독립 cohort 평가를 어느 수준으로 추가할 수 있는가?
7. RF 외의 독립 classifier family에서 잠긴 signature의 utility를 평가할 계획이 있는가?
8. clinical utility를 논의하려면 어떤 error cost, operating threshold, calibration 기준 및 외부 cohort가 필요한가?
9. 후속 구현 변경 시 CGGA의 verified staged objective(RFECV AUROC, size-penalized accuracy, development-CV AUROC ranking)를 하나의 통합 metric으로 잘못 단순화하지 않아야 한다.

# 9. Validation checklist

- [x] nonsignificant difference 또는 0을 포함한 CI만으로 equivalence를 주장하지 않았다.
- [x] 사전 지정 margin이 없는 non-inferiority 주장을 제거하였다.
- [x] 98.6%보다 절대 branch별 변화가 먼저 보이도록 수정하였다.
- [x] held-out isolation과 unbiased development-CV를 구분하였다.
- [x] medoid locking을 stable feature selection과 동일시하지 않았다.
- [x] seed variability와 participant/sample variability를 구분하였다.
- [x] GA superiority를 직접 근거 없이 주장하지 않았다.
- [x] signature size가 partly design-controlled임을 명시하였다.
- [x] 단계별 metric inconsistency를 공개하였다.
- [x] 누락된 simpler size-matched baseline을 Limitations에 기술하였다.
- [x] random-forest dependence를 인정하였다.
- [x] single fixed split의 partition-choice uncertainty를 인정하였다.
- [x] 외부 검증, population transportability 또는 clinical readiness를 암시하지 않았다.
- [x] references, citations, bibliography, citation placeholders를 수정하지 않았다.
- [x] Step 3을 실행·초안·부분 구현하지 않았다.
