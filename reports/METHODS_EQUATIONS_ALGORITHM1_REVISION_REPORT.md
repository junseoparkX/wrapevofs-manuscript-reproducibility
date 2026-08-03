# Executive summary

최신 WrapEvoFS 원고의 RFECV, genetic search, representative-run locking 수학적 명세를 실제 패키지 구현과 저장된 ADNI·CGGA 실행 설정에 맞추어 개정하였다. 핵심 수정은 다음과 같다.

- RFECV 식에서 ADNI 실험값인 고정 상한 30을 제거하고, 사용자 구성 가능한 branch-specific cap \(K_m^{\max}\)와 RFECV가 산출하는 target \(k_m^\star\)를 분리하였다.
- genetic search의 binary chromosome, 선택 subset, base score, nonnegative penalized fitness를 일반식으로 정의하였다.
- 일반 fitness 식에서 balanced accuracy와 \(\lambda=0.015\)를 제거하고 configured score와 사용자 구성 가능한 \(\lambda\)를 사용하였다.
- CGGA의 GA fitness가 balanced accuracy가 아니라 `accuracy`였음을 여섯 개 저장 notebook과 여섯 개 configuration snapshot에서 재확인하여 Methods와 관련 설명을 수정하였다.
- Jaccard similarity와 top-\(q\) representative-run medoid를 명시적으로 정의하였다.
- 중복된 \(78+8-5=81\) standalone display equation을 삭제하되 결과 수치와 Figure 4a의 시각적 산술 표현은 유지하였다.
- held-out data를 입력으로 받지 않는 editable Word Algorithm 1을 26개 번호 행으로 삽입하였다.
- ADNI, CGGA guided, CGGA no-guidance 설정을 구분하는 Supplementary Table S1C를 추가하였다.

경험적 결과, figure plot-data CSV 26개, References 영역은 변경하지 않았다. 최종 DOCX는 16개 자동 검사를 모두 통과했으며 Word로 생성한 43쪽 PDF 전체와 핵심 4쪽을 시각적으로 검토하였다.

# Evidence files inspected

## 구현 및 테스트

- `wrapevofs-package/src/wrapevofs/config.py`
- `wrapevofs-package/src/wrapevofs/selectors/rfecv_target.py`
- `wrapevofs-package/src/wrapevofs/selectors/genetic_rf.py`
- `wrapevofs-package/src/wrapevofs/pipeline.py`
- `wrapevofs-package/tests/test_rfecv_target.py`
- `wrapevofs-package/tests/test_genetic_rf.py`
- `wrapevofs-package/tests/test_config_defaults.py`
- `wrapevofs-package/tests/test_artifacts.py`

## 원고, revision 기록, ADNI 근거

- 최신 editable manuscript와 직전 PDF
- `REVISION_REPORT_STEP1.md`, `REVISION_REPORT_STEP2.md`, `REVISION_REPORT_STEP3.md`
- `REVISION_SUMMARY_STEPS1_TO_3.md`
- Supplementary Tables S1A, S1B, S2 및 관련 caption/source files
- `data\plot_data\Figure_2\source_corrected_methods_hyperparameters.csv`

## CGGA 근거

- 제공 ZIP: `CCGA_ALL GLIOMA-20260726T222045Z-1-001.zip`
- ZIP SHA-256: `E32F3746CB3296726D91B4BECEBE4FD8DA8518D8D7D875C7A85830929D668813`
- read-only audit extraction: `audit\cgga_zip_evidence_e32f3746\CCGA_ALL GLIOMA`
- guided/no-guidance × SVM-L1/XGBoost/Boruta-RF의 총 여섯 개 저장 notebook과 실행 output
- `analysis\figure5_figure6_cgga_package\inputs\runs\*\*\experiment_config_snapshot.json`의 여섯 개 snapshot
- `analysis\figure5_figure6_cgga_package\inputs\analysis_contract.json`
- `analysis\figure5_figure6_cgga_package\outputs\tables\five_run_medoid_locking_audit.csv`

제공 ZIP의 notebook들은 저장된 실행 output을 포함하며, 동일 설정이 repository의 configuration snapshots와 일치했다. 따라서 이번 수정은 단순한 사용자 진술이 아니라 실제 저장 실행물과 설정 기록에 근거한다.

## Internal evidence map

| Manuscript concept | Implementation source | Empirical setting source | Verified behavior |
|---|---|---|---|
| Branch candidate space | `pipeline.py`와 first-stage `SelectionResult` | ADNI corrected methods summary; CGGA notebooks/snapshots | GA는 branch별 전체 first-stage candidate matrix를 입력받는다. |
| RFECV eligible cap | `config.py`, `pipeline.py`, `rfecv_target.py` | ADNI S1A; CGGA snapshots/notebooks | 사용자는 global fallback 또는 method-specific cap을 구성하며, cap은 eligible counts를 제한하지만 target 자체는 아니다. |
| RFECV target | `find_rfecv_target()`, `_pick_target_from_table()` 및 tests | ADNI hyperparameter source; CGGA outputs | eligible path에서 최고 mean score를 선택하고 score tie 시 더 작은 subset을 선택한다. 산출 target은 GA로 전달된다. |
| Binary subset | `_initial_population()`, `_evaluate_chromosome()`, `_mutate()` | 저장 masks와 feature sets | Boolean chromosome이 모든 branch candidate를 포함하며, empty child는 한 feature를 활성화해 repair한다. |
| GA base score/fitness | `_score_fold()`, `_evaluate_chromosome()` 및 metric tests | ADNI S1A; CGGA snapshots/notebooks | configured fold score의 평균에서 절대 size deviation penalty를 빼고 음수 fitness를 0으로 truncate한다. |
| Fixed folds/run seeds | `run_genetic_rf()` | ADNI S1A; CGGA settings | stratified folds는 run loop 밖에서 한 번 만들고, run seed는 `random_state + run_id`이다. |
| GA operators | `_selection_indices()`, `_crossover()`, `_mutate()`, generation loop | empirical configs | clipped nonnegative fitness-proportional selection, uniform fallback, one-point crossover, bit-flip mutation, elitism을 사용한다. |
| Retained run candidates | `_update_top_solutions()`와 artifact test | ADNI S1A; six CGGA snapshots | run당 최대 한 개 best를 만든 뒤 `top_k`로 truncate한다. 보고된 분석은 `top_k=n_runs=5`라 다섯 run이 모두 남는다. |
| Locking score | post-run locking audit artifacts | ADNI S2; CGGA contract/audit | ADNI는 development-CV balanced accuracy, CGGA는 development-CV AUROC를 사용하며 held-out outcome은 사용하지 않는다. |
| Jaccard locking | post-run audit; core pipeline 밖의 분석 단계 | ADNI S2; CGGA contract/audit | locking score 상위 3개에서 mean Jaccard가 가장 큰 run을 선택한다. |
| ADNI settings | package schema/metric support | S1A와 corrected hyperparameters | RFECV weighted OvR AUROC; caps 30; targets 29/30/27; GA balanced accuracy; \(\lambda=0.015\); runs 5; \(q=3\). |
| CGGA settings | package sources | ZIP, notebooks, snapshots, contract | RFECV AUROC; GA accuracy; guided \(\lambda=0.015\), no-guidance \(\lambda=0\); runs 5; AUROC ranking; \(q=3\). |

# Equations removed

1. 고정 조건 \(k\le30\)을 포함한 RFECV target 식을 제거하였다. 30은 ADNI에서 사용한 empirical cap이며 framework constant가 아니다.
2. balanced accuracy와 \(\lambda=0.015\)를 고정한 GA fitness 식을 제거하였다.
3. \(78+8-5=81\) standalone display equation을 제거하였다. 81-feature restricted model의 구성 수치는 connected prose와 Figure 4a에 유지하였다.
4. roulette-wheel selection, crossover, mutation, empty-chromosome repair에 대한 별도 main-text 수식은 추가하지 않았다. 이 동작들은 Algorithm 1에서 구현 수준으로 기술하였다.

# Equations added or generalized

총 9개의 editable native Word equation object를 삽입하였다.

- branch candidate space \(\mathcal C_m=\{1,\ldots,p_m\}\)
- mean RFECV score \(\overline S_{R,m}(k)\)
- smaller-subset tie break를 포함한 RFECV target \(k_m^\star\)
- binary chromosome \(\mathbf z\in\{0,1\}^{p_m}\)
- selected subset \(F_m(\mathbf z)\)와 cardinality
- generic GA base score \(\overline S_{G,m}(\mathbf z)\)
- nonnegative penalized fitness \(\Phi_m(\mathbf z)\)
- Jaccard similarity \(J(F_r,F_s)\)
- top-\(q\) representative-run medoid \(r^\star\)

본문 prose에서 \(K_m^{\max}\)는 사용자 구성 가능한 RFECV eligibility cap, \(k_m^\star\)는 RFECV-derived soft target, \(S_{R,m}^{(v)}\)와 \(S_{G,m}^{(v)}\)는 각각 구성된 fold score임을 분명히 했다. \(\lambda=0\)은 size guidance를 제거하며, \(\lambda>0\)은 target deviation에 선형 penalty를 부과한다. 외부 `max(0, ·)`는 구현의 negative-fitness truncation을 그대로 반영한다.

# CGGA metric correction

여섯 개 CGGA snapshot의 `fitness_metric`은 모두 `accuracy`였다. 여섯 개 실행 notebook의 설정 및 출력도 동일했다. 따라서 원고의 CGGA objective sequence를 다음과 같이 바로잡았다.

- RFECV scoring: AUROC
- chromosome fitness: accuracy
- guided size penalty: \(\lambda=0.015\)
- no-guidance size penalty: \(\lambda=0\)
- run-level locking rank: development-CV AUROC

이는 하나의 통합 objective 최적화가 아니라 서로 다른 stage-specific objective의 조합임을 명시하였다. ADNI의 GA balanced accuracy 설정은 근거가 확인되어 변경하지 않았다. held-out 결과표에 보고되는 balanced accuracy는 평가 metric이므로 CGGA GA fitness correction과 충돌하지 않는다.

# Algorithm 1 design

caption은 “Algorithm 1. Branch-level WrapEvoFS search and representative-run locking.”으로 삽입하였다.

- editable Word table 사용
- 좁은 line-number column과 넓은 pseudocode column
- vertical border와 배경색 없음
- restrained top/bottom horizontal rules
- 본문 글꼴 사용
- Input, Output, For, If, End for, Return keyword 강조
- line numbers는 neutral gray
- nested blocks는 일관된 indentation 적용
- 1–26의 연속 번호 사용
- 한 페이지에 완전히 배치

Input은 development data, branch candidates, RFECV configuration, GA configuration, development-CV locking score, top-pool size만 포함한다. held-out/test partition은 입력에 포함하지 않았다. RFECV target derivation, repeated GA search, development-only representative-run locking의 세 경계를 순서대로 분리하였다.

# Implementation-to-pseudocode audit

| Audit point | Verified implementation | Algorithm 1 treatment |
|---|---|---|
| GA fold construction | run loop 밖에서 한 번 구성 | line 3 |
| Run-specific seed | `random_state + run_id` | independent run 구조와 audit record에 반영; code-specific 표현은 본문 prose에서 설명 |
| Initial population | `initial_off_ratio` 사용, nonempty 보장 | line 5 |
| Stored scores | penalized score와 base score 모두 보존 | lines 8–10 |
| Selection | nonnegative fitness-proportional | line 12 |
| Selection fallback | total이 zero/nonfinite이면 uniform | line 12 |
| Crossover | one-point | line 13 |
| Mutation | position별 independent bit flip | line 14 |
| Empty repair | 무작위 한 feature 활성화 | line 15 |
| Elitism | top \(E\) chromosomes 유지 | line 11 |
| Run best | run당 highest-fitness candidate 유지 | line 18 |
| Locking | fixed development-CV evaluator와 top-\(q\) Jaccard | lines 20–24 |
| Audit export | RFECV, GA, locking artifacts 조립 | line 25 |
| Held-out boundary | algorithm 완료 뒤에만 평가 | 입력에서 제외; algorithm 앞 문장과 뒤 문단에서 명시 |

Algorithm 1은 Python 함수명이나 임시 변수명을 복사하지 않고, 구현에 대응하는 language-independent pseudocode로 작성하였다. standard GA operators를 새 방법론적 기여로 주장하지 않았다.

# n_runs/top_k/run-level candidate resolution

`_update_top_solutions()`는 각 run에서 최대 한 개 best candidate를 유지한 뒤 전체 retained list를 `top_k`개로 truncate한다. 그러므로 generic package가 모든 run의 candidate를 항상 보존한다고 말할 수 없다.

보고된 ADNI 및 여섯 CGGA configuration에서는 `n_runs=5`와 `top_k=5`가 확인되었다. 따라서 이 경험적 workflow에서는 다섯 run 각각의 best candidate가 representative-run locking에 사용 가능했다. 본문과 S1C note에 다음 구분을 명시하였다.

- reported workflow: `top_k=n_runs=5`, 따라서 run당 한 candidate 보존
- general package: `top_k<n_runs`이면 모든 run의 보존을 보장하지 않음

패키지 동작은 변경하지 않았으며, Algorithm 1은 보고된 five-run workflow를 요약하는 것으로 설명하였다.

# Supplementary settings-table changes

Supplementary Table S1C를 다음 네 column으로 추가하였다.

| Setting | ADNI | CGGA guided | CGGA no guidance |
|---|---|---|---|

포함된 항목은 RFECV metric, branch caps, recovered targets, GA fitness metric, run-ranking metric, \(\lambda\), RFECV/GA/locking folds, population, generations, runs, `top_k`, crossover, mutation, elites, initial-off ratio, medoid pool \(q\), RF evaluator/backend, final run-ID tie rule이다.

확인된 cap/target pair는 다음과 같다.

- ADNI: SVM-L1 30/29, XGBoost 30/30, Boruta-RF 30/27
- CGGA guided: SVM-L1 15/15, XGBoost 20/20, Boruta-RF 10/9
- CGGA no guidance: SVM-L1 15/15, XGBoost 20/20, Boruta-RF 15/14

CGGA 실행 output에서는 GA backend가 GPU로 resolve된 것이 확인되었다. 정확한 RAPIDS version은 저장되지 않아 기입하지 않았다.

# Files modified

- `analysis\revise_manuscript.py`
- `analysis\validate_methods_equations_algorithm1.py`
- `manuscript\WrapEvoFS_manuscript_final_methods_algorithm1.docx`
- `manuscript\WrapEvoFS_manuscript_final_methods_algorithm1.pdf`
- `manuscript\tables\supplementary\Table_S1C_empirical_search_settings.csv`
- `manuscript\tables\supplementary\Supplementary_Table_captions.md`
- `manuscript\tables\supplementary\Table_S1B_component_scaling.csv`
- `REVISION_REPORT_STEP2.md`
- `audit\methods_equations_evidence_map.md`
- `audit\methods_equations_algorithm1_validation.json`
- `audit\methods_algorithm1_render\*`
- `audit\methods_algorithm1_full_render\*`
- `audit\methods_algorithm1_contact_sheets\*`
- `METHODS_EQUATIONS_ALGORITHM1_REVISION_REPORT.md`

# Numerical-integrity check

- `data\plot_data`의 기존 CSV 26개를 기존 manifest와 비교: 26/26 unchanged
- CGGA snapshot 확인: 6/6에서 `fitness_metric=accuracy`
- reported configurations 확인: 6/6에서 `top_k=n_runs=5`
- native framework equations: 9개
- editable Algorithm 1 numbered lines: 26개
- standalone \(78+8-5=81\) display: 없음
- old hard-coded framework equations: 없음
- References 시작부터 Supplementary Information 직전까지의 reference XML: 직전 Step 3 원고와 identical
- empirical result values와 figure plot data: 변경 없음

전용 validator `analysis\validate_methods_equations_algorithm1.py`는 16/16 검사를 통과하였다. bundled Python runtime에는 `pytest` module이 없어 package unit tests를 재실행하지는 못했다. 대신 관련 test source를 직접 검토하고, 이번 원고 산출물에는 별도 구현-원고 validator를 적용하였다.

# Rendered-page visual validation

최종 DOCX를 Microsoft Word로 PDF export한 뒤 Poppler로 렌더링하였다.

- 최종 PDF: 43쪽, Letter size
- 전체 43쪽: 100 dpi 렌더와 5개 contact sheet로 전수 검토
- Methods equations: pages 4–5, 180 dpi 상세 검토
- Algorithm 1: page 6, 180 dpi 상세 검토
- Supplementary Table S1C: page 28, 180 dpi 상세 검토

검토 결과:

- 9개 수식 모두 clip 또는 margin overflow 없음
- `min arg max`와 하첨자 범위가 분리되어 식별 가능
- Algorithm 1 전체가 한 페이지에 유지됨
- line numbering 1–26 연속
- nested indentation과 keyword 강조 일관
- held-out/test data가 Algorithm input에 없음
- S1C의 19개 setting row가 한 페이지에서 읽을 수 있게 배치됨
- figure, table, reference page에서 새 overflow 또는 잘림 없음

page 5 하단의 여백은 Algorithm 1을 다음 페이지에 온전히 유지하기 위한 의도적 page break이다.

# Unresolved issues

1. ADNI의 Jaccard와 development-CV locking score가 모두 동률일 때 적용한 최종 run-identifier rule은 제공 artifact에 남아 있지 않다. 원고와 S1C에 “not retained”로 표기하였다.
2. CGGA GA output은 GPU backend 사용을 확인하지만 정확한 RAPIDS version은 저장 artifact에서 확인되지 않는다.
3. 제공 runtime에 `pytest`가 없어 package unit-test suite를 이번 revision 환경에서 재실행하지 못했다. 이는 저장 구현과 test source의 감사 결과를 무효화하지 않지만, 별도의 clean environment test run은 남은 reproducibility action이다.
4. representative-run locking audit는 core `WrapEvoPipeline` 내부 단계가 아니라 저장 후 분석 artifact에 구현되어 있다. 원고에서는 이를 숨기지 않고 post-run development-only locking 단계로 기술하였다.

| Item | Previous manuscript | Verified implementation | Revised manuscript | Status |
|---|---|---|---|---|
| RFECV cap | framework 식에 30 고정 | cap은 user-configurable; target은 RFECV-derived | \(K_m^{\max}\)와 \(k_m^\star\) 분리, 30은 ADNI setting으로만 보고 | Resolved |
| RFECV tie break | 불충분 | score tie 시 smaller subset | \(\min\arg\max\)로 명시 | Resolved |
| Binary representation | 수식 없음 | Boolean chromosome이 branch candidate 전체를 표현 | \(\mathbf z\), \(F_m(\mathbf z)\), cardinality 추가 | Resolved |
| GA metric | balanced accuracy hard-coded | metric configurable | generic \(S_G\) 사용 | Resolved |
| GA lambda | 0.015 hard-coded | \(\lambda\ge0\) configurable | generic fitness와 empirical settings 분리 | Resolved |
| Negative fitness | 명시 불충분 | 0으로 truncate | outer `max(0, ·)` 추가 | Resolved |
| CGGA GA fitness | balanced accuracy로 기술 | six snapshots/notebooks 모두 accuracy | accuracy로 전면 수정 | Resolved |
| ADNI GA fitness | balanced accuracy | artifact에서 balanced accuracy 확인 | 유지 | Verified |
| Jaccard definition | 불완전 | set intersection/union | explicit Jaccard equation 추가 | Resolved |
| Representative run | top-three medoid 설명 불완전 | development ranking 후 mean Jaccard, tie rules | generic top-\(q\) medoid와 empirical \(q=3\) 구분 | Resolved |
| `n_runs`/`top_k` | 모든 run 보존처럼 읽힐 수 있음 | run당 최대 1개 후 `top_k` truncation | reported `top_k=n_runs=5`; generic limitation 명시 | Resolved |
| \(78+8-5=81\) | standalone display | arithmetic은 결과 구성 설명 | display 제거, prose/Figure 4a 유지 | Resolved |
| Algorithm 1 | 없음 | RFECV → GA → post-run locking | editable 26-line Word algorithm 추가 | Resolved |
| Held-out boundary | prose에 분산 | development-only selection/locking | Algorithm input에서 제외하고 전후 문장으로 명시 | Resolved |
| ADNI final identifier tie rule | 구체적 규칙 불명 | artifact에 미보존 | “not retained” 표기 | Unresolved, transparently reported |
| References/citations | 확정된 Step 3 상태 | 수정 금지 | XML identical | Verified unchanged |
| Empirical results | 확정된 수치 | 수정 대상 아님 | plot data 26/26 unchanged | Verified unchanged |
