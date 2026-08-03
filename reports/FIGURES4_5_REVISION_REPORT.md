# Figure 4–5 수정 보고서

## 1. Files inspected

최신 `manuscript/WrapEvoFS_manuscript_final_revised_step3.docx`의 관련 Methods 및 Results 문단, Figure 4·5 캡션, Table 4A/4B, Table 5, Supplementary Tables S11A/S11B, `REVISION_REPORT_STEP1.md`, `REVISION_REPORT_STEP2.md`, `REVISION_REPORT_STEP3.md`를 검토했다. Figure 4에는 `Table_4A.csv`, `Table_4B.csv`, `Table_S11A.csv`, `Table_S11B.csv`를, Figure 5에는 `figure5a_cohort_and_workflow.csv`, `figure5b_compression_auroc.csv`, `figure5c_additional_metrics.csv`를 근거 자료로 사용했다.

## 2. Editable sources modified

내보낸 raster를 직접 수정하지 않고 `analysis/build_revised_figure_sources.py`의 `build_figure_4()`와 `build_figure_5()`를 수정했다. `analysis/figure_specs.json`, 각 Figure 폴더의 README, caption 및 alt text, Google Docs용 caption/alt text, `analysis/revise_manuscript.py`도 최종 도식과 동기화했다. 수정 전 SVG/PDF/PNG와 editable source는 `data/revised_assets/Figure_4/versions/2026-07-26_pre_fig45_revision/` 및 대응 Figure 5 버전 폴더에 보존했다.

## 3. Figure 4 changes

Panel a 제목을 “Training-derived candidate-set construction”으로 바꾸고, 시간적 pipeline처럼 보이던 화살표를 모두 제거했다. 네 개의 일관된 카드와 수학 연산자를 사용하여 locked WrapEvoFS union 78 + training-only STABL 8 − shared candidates 5 = restricted candidate set 81을 직접 표현했다. 작고 중복되던 회색 five-feature 명단은 삭제했으며 다른 소형 feature 명단으로 대체하지 않았다.

Panel b의 feature 순서, posterior mean, 95% credible interval, contrast color 및 zero-reference line은 변경하지 않았다.

Panel c에는 세 metric이 공유하는 정량 x축을 추가했다. Full Bayesian reference는 별도 diamond point-only 표식으로 표시했으며 CI를 생성하지 않았다. Restricted Laplace Bayesian, candidate-union RF 및 STABL RF만 저장 자료에 존재하는 95% CI를 표시했다. 범례는 두 줄로 분리해 Panel d와 충돌하지 않도록 했다.

Panel d에서는 “Lower effect threshold: OR≥1.05”와 “Higher effect threshold: OR≥1.20”을 사용했다. Primary bar를 더 어둡게 하고 내부에 “No additional compression”을 추가했다. 81/81, 47/81, 81/81, 32/81 endpoint label은 유지했다.

## 4. Figure 5 changes

Panel a 제목을 “CGGA locked-split design and one-time held-out evaluation”로 변경하고 “prespecified”를 사용하지 않았다. All eligible CGGA samples와 stratified 70:30 split 다음에 development n=214와 locked held-out n=92가 같은 split에서 직접 분기한다. 개발 경로는 “Development-only WrapEvoFS selection and locking” 한 카드로 축약했으며 Figure 1의 세부 workflow를 반복하지 않았다.

Held-out 경로는 preprocessing, candidate generation, RFECV, GA, ranking 및 medoid locking을 통과하지 않는다. Locked settings는 보라색 실선, held-out data는 청색 점선으로 one-time evaluation에 직접 들어간다. 상단을 가로지르는 긴 held-out 점선, loop, 교차선 또는 detached arrowhead는 없다. Cohort 수, partition 수 및 class 수는 유지했다.

Panels b와 c의 Direct/Locked 구분, feature counts, estimates, confidence intervals, marker 및 method color는 변경하지 않았다. Reduction 표시도 모두 Direct candidate set을 분모로 한 일관된 정수 반올림값 54%, 73%, 65%를 유지했다.

## 5. Axis limits and ticks used

Figure 4c의 공통 x축 범위는 0.35–0.90이다. Major ticks는 0.40, 0.50, 0.60, 0.70, 0.80, 0.90이며 축 라벨은 “Held-out metric value”이다. Major tick 위치에만 얇은 수직 gridline을 두었다. 0.50은 별도 reference line으로 강조하지 않았다. 가장 낮은 CI 0.383과 가장 높은 CI 0.856이 모두 축 내부에 들어간다.

## 6. Caption changes

Figure 4 캡션은 training-derived set arithmetic, within-dataset concordance, conditional credible intervals, point-only full Bayesian reference, available interval만 표시했다는 사실, primary BLiP의 no-compression 결과를 명시하도록 갱신했다.

Figure 5 캡션은 저자 확인 notebook의 stratified 70:30 split과 random state 42, development-only model development, held-out isolation, Direct-set reduction denominator 및 Figure 6의 양·음 값을 포함하는 paired interval을 명시하도록 갱신했다. CGGA를 external validation으로 표현하지 않았다.

## 7. Numerical-integrity check

수치 자료는 수정하지 않았다. 수정 전 repository manifest와 대조한 Figure 4·5 plotting CSV 7개의 SHA-256이 모두 동일했다. Figure 4c에는 3 metrics × 3 interval-available analyses의 CI 선 9개만 존재하며 full Bayesian CI는 계속 미보고 상태이다. BLiP count는 primary 81, q=0.10 47, OR≥1.05 81, OR≥1.20 32로 확인했다.

Figure 5의 Panels b/c는 plot data와 geometry를 유지하면서 Panel a와의 세로 간격을 넓혔고, Panel b 제목을 `Feature compression and held-out AUROC`로 다듬었으며, −65%, −54%, Boruta-RF 라벨만 error bar와 겹치지 않도록 미세 이동했다. Direct→locked feature reduction은 SVM-L1 35→16 = 54.3%, XGBoost 70→19 = 72.9%, Boruta-RF 26→9 = 65.4%로 재확인했다. 어떤 estimate, interval, sample count, feature count 또는 model label도 변경하거나 새로 추정하지 않았다.

## 8. Rendered-PDF visual inspection

최종 DOCX를 Microsoft Word 숨김 모드로 PDF 내보낸 뒤 Poppler로 약 200 dpi 렌더했다. Figure 4는 최종 PDF 15쪽, Figure 5는 16쪽에 배치되었다. 두 페이지를 full-page 및 figure/caption 확대 view로 직접 검사했다. Figure 4의 set arithmetic, posterior interval, 공통 metric axis, point-only diamond, 범례 및 BLiP bar가 원고 크기에서 읽혔다. Figure 5의 cohort/split/partition counts와 두 입력의 evaluation 합류도 원고 크기에서 구분되었다.

문서 스킬의 기본 LibreOffice 렌더러는 이 환경에 `soffice`가 없어 실행되지 않았으나, Word 기반 PDF와 200-dpi page PNG가 정상 생성되어 실제 Word 레이아웃을 검증했다.

## 9. Clipping and overlap checks

Figure 4b의 feature label과 모든 CrI endpoint가 plot 영역 안에 있고, Figure 4c의 모든 CI가 0.35–0.90 범위 내에 있다. 범례는 Panel d 제목과 겹치지 않으며 d의 긴 threshold label도 잘리지 않는다.

Figure 5a의 box text, cohort/class count, held-out annotation 및 모든 arrowhead가 box 경계 안팎에서 정상 배치되었다. b/c 제목과 plot 영역, legend, axis title, method label 및 confidence interval에 clipping이나 overlap이 없다. 두 figure의 caption도 같은 페이지에서 완전하게 표시된다.

## 10. Exported files

- `manuscript/figures/main/Figure_4/Figure_4_candidate_restricted_interoperability.svg`
- `manuscript/figures/main/Figure_4/Figure_4_candidate_restricted_interoperability.pdf`
- `manuscript/figures/main/Figure_4/Figure_4_candidate_restricted_interoperability.png` — 4,016 × 4,488 px, 600 dpi
- `manuscript/figures/main/Figure_5/Figure_5_CGGA_locked_heldout_evaluation.svg`
- `manuscript/figures/main/Figure_5/Figure_5_CGGA_locked_heldout_evaluation.pdf`
- `manuscript/figures/main/Figure_5/Figure_5_CGGA_locked_heldout_evaluation.png` — 4,016 × 3,543 px, 600 dpi
- `manuscript/WrapEvoFS_manuscript_final_revised_step3.docx`
- `manuscript/WrapEvoFS_manuscript_final_revised_step3.pdf`

Google Docs용 Figure 4·5 PNG와 caption/alt-text 자산도 같은 최종 버전으로 갱신했다.

## 11. Unresolved issues

Figure 4·5의 시각적 또는 수치적 미해결 문제는 발견되지 않았다. 다만 기존 원고에 명시된 substantive limitation은 그대로 남는다. Figure 4의 posterior interval 및 expected-FDR는 training-derived screen과 fitted restricted model에 조건부이며 screening uncertainty를 포함하지 않는다. Figure 5는 한 번의 내부 locked split demonstration이며 external validation이나 equivalence/non-inferiority를 확립하지 않는다. 이 한계를 완화하는 새로운 분석은 본 수정 범위에서 수행하지 않았다.
