# 1. Executive summary

이번 Step 1에서는 현재 원고, 원고 재생성 스크립트, Supplementary Table S1, ADNI Figure 2 집계 자료, CGGA Figures 5–6 및 Supplementary Tables S12–S22의 기계 판독 자료, 저장소 감사 메타데이터, 데이터 접근 문서, 그리고 제공된 CGGA development/held-out CSV 네 개를 대조하였다. 모델 fitting, feature selection, bootstrap 생성, Bayesian sampling은 다시 실행하지 않았다.

확인된 주요 불일치는 다음과 같다.

- CGGA의 54.3%–72.9% 감소율이 원래 24,326개 predictor를 분모로 한 것처럼 읽혔으나, 실제 분모는 branch별 first-stage candidate set인 35, 70, 26개였다.
- ADNI empirical partition은 532/133으로 제공된 fixed external split이지만 Supplementary Table S1에는 7:3, random state 42, shuffle=true, stratify=true가 실제 분할 생성값처럼 제시되어 있었다.
- 공통 WrapEvoFS preprocessing의 `scaling=none`, SVM-L1의 branch-specific `standardize=true`, Bayesian 분석의 development-fitted scaling이 하나의 일반적인 표준화 문장으로 혼합되어 있었다.
- ADNI 입력에 upstream minimum/2 imputation이 있었다는 서술과 WrapEvoFS median-imputation 설정이 실행된 단계처럼 혼합되어 있었다.
- figure-reproduction package가 participant-level restricted data와 원래 run directory 없이도 empirical run 전체를 재현할 수 있는 것처럼 읽힐 수 있었다.

해결한 사항은 CGGA 감소율 분모, ADNI fixed-partition의 operational definition, 7:3 관련 설정의 비적용 표시, 분석별 bootstrap/CV 범위, component별 scaling 구분, upstream과 in-pipeline preprocessing 경계, 제한 데이터에 맞춘 reproducibility 표현, CGGA 파일 schema이다. CGGA 제공 CSV에서는 214/92 rows, 24,326 predictors, development 110/104 및 held-out 47/45 class counts, 결측·무한값 0, partition 내부 duplicate ID 0, partition 간 ID overlap 0을 직접 확인하였다.

미해결 사항은 ADNI original split 생성 과정과 participant overlap, upstream minimum/2 imputation의 계산 범위·시점, WrapEvoFS median imputation 및 missingness filtering의 실제 trigger count, ADNI/CGGA 최종 fixed-RF backend, STABL scaling, exact empirical-run package commit과 environment, 그리고 cohort/assay/QC/batch provenance 일부이다. 따라서 empirical run settings는 일부는 명확히 재구성되지만 전체를 단일하고 완전한 실행 기록으로 재구성할 수는 없다.

# 2. Issue-resolution table

| ID | Issue | Manuscript location | Original value or wording | Verified evidence | Revised value or wording | Status |
|---|---|---|---|---|---|---|
| 1 | CGGA compression denominator | Abstract; Results; Discussion; Figure 5; Figure 6; Table 5 note | “compressed 24,326-gene inputs by 54.3%–72.9%” | `figure5b_compression_auroc.csv`: 35→16, 70→19, 26→9 | Percentages are explicitly reductions from branch-specific first-stage candidate sets; 24,326 is the original input space before first-stage generation | resolved |
| 2 | ADNI 7:3 versus 532/133 | Methods; Supplementary Table S1A; Figure 1 | 7:3, random state 42, shuffle=true, stratify=true presented with 532/133 | `source_corrected_methods_hyperparameters.csv` labels 532/133 records “Fixed external split”; original split manifest/code absent | 532/133 described as supplied fixed external split; 7:3 and related fields marked not applicable to partition creation | partially resolved |
| 2a | ADNI participant overlap | Methods limitations; report | No verification statement | Participant-level ADNI identifiers are not included | Verification is explicitly marked unavailable | unresolved |
| 3 | Missingness and imputation sequence | ADNI data Methods; Supplementary Table S1A | Upstream minimum/2 plus median imputation could be read as two executed steps | No ADNI matrices or preprocessing report; median and 0.2 are present only as configured rules | Upstream minimum/2 provenance and in-pipeline configured rules are separated; trigger counts are unresolved | partially resolved |
| 4 | Scaling scope | Methods; Supplementary Table S1B | Broad statement that all continuous predictors were standardized | S1A: common scaling=none; SVM-L1 standardize=true; Bayesian descriptions specify development-fitted scaling | Component-specific table distinguishes none, internal estimator standardization, development-fitted scaling, not applicable, and unresolved | partially resolved |
| 5 | Defaults versus empirical settings | Supplementary Table S1A | Blank fields and configured values presented uniformly as resolved analytical steps | Corrected settings summary plus absence of original YAML/notebooks/run directories | Added Classification column; unused split fields, inherited defaults, explicit settings, and unresolved trigger states are identified | partially resolved |
| 6 | Bootstrap/CV/backend consistency | Methods; Figure 2 caption; Figure 5/6 captions; supplementary notes | ADNI and CGGA bootstrap scopes not always explicit; backend generalized | ADNI comparison: 1,000 class-stratified percentile resamples; CGGA: 2,000 stratified resamples, seed 42; RFECV/GA five folds; ADNI GA-RF backend=gpu | Analysis-specific counts and seeds added; exact final-RF backends and ADNI bootstrap seed marked unresolved | partially resolved |
| 7 | Count consistency | Tables 1–5; Figures 2, 4–6; Supplement | Counts distributed across multiple artifacts | `audit/step1_consistency_audit.json`: 21/21 checks passed | All arithmetic identities and displayed counts retained consistently | resolved |
| 8 | Data provenance and cohort definition | ADNI/CGGA Methods; limitations; data access | ADNI-derived and CGGA PMID32021566 used without complete local provenance | CGGA CSV schema and IDs verified; upstream assay/QC/batch/cohort records absent; ADNI restricted inputs absent | Supported facts added; unavailable provenance moved to limitations and author questions | partially resolved |
| 9 | Reproducibility claim precision | Abstract; Discussion; Conclusion; Data and code availability; README | “test-isolated” and “reproducible” could imply full end-to-end rerun | Public repository is plotting/artifact reproduction; restricted matrices and complete run directories absent | Claims now refer to an auditable in-pipeline analysis path and figure/artifact reproduction subject to restricted-data access | resolved |
| 10 | Workflow boundary | Abstract; Methods; Figure 1; Discussion; Conclusion | Upstream preprocessing and WrapEvoFS isolation were merged | ADNI upstream imputation and CGGA upstream log2 provenance not recoverable | In-pipeline isolation and upstream unknowns are explicitly separated | resolved |

# 3. Data and setting provenance table

| Item | Reported manuscript value | Repository evidence | Final resolved value | Confidence |
|---|---|---|---|---|
| ADNI partition | development 532; held-out 133; 7:3 settings | Dataset rows name “Fixed external split”; no split manifest | Supplied fixed external 532/133 partition; generation procedure unresolved | moderate |
| ADNI classes | development 103/187/242; held-out 26/47/60 | Table 1; Figure 2 source tables | Values reconcile to 532 and 133 | high |
| ADNI features | 7,002 proteomic + 409 metabolomic | Table 1 and selection records | 7,411 total | high |
| ADNI upstream preprocessing | minimum/2 then log2 | Manuscript statement only; matrices/report absent | Retained as reported upstream history, with scope and timing unresolved | low |
| ADNI WrapEvoFS imputation | median; threshold 0.2 | Resolved configuration summary only | Configured rules; actual trigger counts unresolved | moderate |
| Common WrapEvoFS scaling | none | S1A resolved value | none | high |
| SVM-L1 scaling | standardize=true | S1A branch setting | internal estimator standardization | high |
| XGBoost/Boruta-RF scaling | not separately stated | No branch scaling setting; common scaling=none | no additional scaling documented | moderate |
| ADNI RFECV/GA backend | gpu | S1A resolved backend; saved runtime table | GPU; exact RAPIDS version unresolved | moderate |
| ADNI final fixed-RF backend | fixed random forest | Aggregate comparison outputs only | unresolved | unresolved |
| ADNI bootstrap | 1,000; class stratified; percentile CI | Figure 2 comparison setting table | 1,000 class-stratified percentile resamples; seed unresolved | high |
| Full Bayesian scaling | standardized predictors | Model description; scaler absent | development-fitted standardization according to description | moderate |
| Restricted Bayesian scaling | StandardScaler on 532, applied to 133 | Methods description; scaler absent | development-fitted StandardScaler | moderate |
| STABL scaling | unstated | Complete run artifact absent | unresolved | unresolved |
| BLiP scaling | unstated | BLiP uses posterior PEPs | not applicable to raw predictors | high |
| CGGA partition | development 214; held-out 92 | Supplied CSVs and Table S12 | Supplied fixed partition | high |
| CGGA endpoint counts | 110/104 and 47/45 | Direct CSV inspection | Counts confirmed | high |
| CGGA predictors | 24,326 | Direct CSV inspection | 24,326 predictors plus `CGGA_ID` | high |
| CGGA data integrity | not fully stated | Direct CSV inspection | missing=0, infinite=0, duplicate IDs=0, train/test ID overlap=0 | high |
| CGGA upstream preprocessing | log2-transformed | Filenames and values; source pipeline absent | Upstream log2 status retained; transformation/filtering/batch provenance unresolved | moderate |
| CGGA bootstrap | 2,000, seed 42 | Figures 5–6 plot data and seed file | 2,000 stratified resamples; seed 42 | high |
| CGGA final fixed-RF backend | fixed random forest | Prediction/aggregate outputs; fitting code absent | unresolved | unresolved |
| Package version/commit | WrapEvoFS v0.1.0 | Manuscript and repository URL; no empirical commit record | v0.1.0 reported; exact empirical commit unresolved | moderate |

# 4. Files modified

- `analysis/revise_manuscript.py`: Step 1 wording, Supplementary Table S1A classification, S1B scaling table, and final DOCX generation.
- `analysis/build_revised_figure_sources.py`: Figure 1 split label and verified workflow-boundary wording.
- `analysis/validate_step1_consistency.py`: machine-checked count, percentage, split-evidence, and supplied-CGGA integrity audit.
- `README.md`: figure/artifact reproduction scope and restricted-data limitation clarified; numbered notebook terminology removed.
- `data/access/README.md`: in-pipeline versus upstream preprocessing boundary clarified.
- `data/access/schema_cgga.csv`: actual `MGMT_label` and `MGMT_status` columns documented.
- `manuscript/figures/main/Figure_1/Figure_1_WrapEvoFS_workflow.{svg,pdf,png}`: fixed study split and upstream-boundary language.
- `manuscript/figures/main/Figure_1/caption.md`: fixed supplied partition and boundary language.
- `manuscript/figures/main/Figure_2/caption.md`: ADNI bootstrap design and 1,000 resamples.
- `manuscript/figures/main/Figure_5/caption.md`: CGGA first-stage reduction denominators and supplied split.
- `manuscript/figures/main/Figure_6/caption.md`: Direct set defined as branch-specific first-stage candidate set.
- `manuscript/google_docs_assets/Figure_1.png` 및 `manuscript/google_docs_assets/captions.md`: updated figure/caption copies.
- `manuscript/tables/supplementary/Supplementary_Table_captions.md`: S1A/S1B captions and non-numbered secondary-analysis terminology.
- `manuscript/tables/supplementary/Table_S1A_resolved_settings_and_provenance.csv`: every S1 setting with classification.
- `manuscript/tables/supplementary/Table_S1B_component_scaling.csv`: component-level scaling evidence.
- `audit/step1_consistency_audit.json`: 21 machine checks and supplied-CGGA file hashes/summaries.
- `manuscript/WrapEvoFS_manuscript_final_revised_step1.docx`: revised manuscript.
- `manuscript/WrapEvoFS_manuscript_final_revised_step1.pdf`: rendered manuscript.
- `audit/reproducibility_audit.json`: final Step 1 outputs and audit scope.
- `analysis/validate_final_revision.py`: Step 1 deliverable validation.
- `REVISION_REPORT_STEP1.md`: 본 보고서.

# 5. Numerical corrections

- CGGA SVM-L1: 35→16, reduction 54.3%; denominator is 35 first-stage candidates.
- CGGA XGBoost: 70→19, reduction 72.9%; denominator is 70 first-stage candidates.
- CGGA Boruta-RF: 26→9, reduction 65.4%; denominator is 26 first-stage candidates.
- CGGA 24,326→9–19 is now described as the combined result of first-stage candidate generation and subsequent WrapEvoFS compression; 54.3%–72.9% is not applied to 24,326.
- ADNI 532/133 is the empirical partition. The 7:3 value, random state 42, shuffle=true, stratify=true, and empty stratify columns are marked not applicable to generation of this supplied partition.
- ADNI bootstrap is specified as 1,000 class-stratified percentile resamples; bootstrap seed is unresolved.
- CGGA bootstrap remains 2,000 stratified resamples with seed 42.
- ADNI RFECV folds=5, GA fitness folds=5, run-ranking folds=5, GA runs=5, population=50, generations=50, mutation=0.05, crossover=0.8, elitism=2, lambda=0.015, top-k=5, RFECV maximum count=30 were retained as recoverable settings and classified.
- Blank correlation threshold, class weight, and checkpoint directory are rendered as `None` rather than blank verified values.
- `7,002 + 409 = 7,411`, `78 + 8 − 5 = 81`, `103 + 187 + 242 = 532`, `26 + 47 + 60 = 133`, `110 + 104 = 214`, `47 + 45 = 92`, and `214 + 92 = 306` all passed the machine audit.
- No reported performance estimate, confidence interval, Bayesian result, BLiP result, or feature-stability result was changed.

# 6. Textual claim corrections

- “24,326-gene inputs were reduced by 54.3%–72.9%” was replaced with wording that identifies branch-specific first-stage candidate sets as the denominator.
- “prespecified split” was operationalized as fixed development and held-out files supplied before modeling; the original split-generation procedure is not claimed.
- 7:3, shuffle, stratification, and split seed are no longer described as operations that created the ADNI 532/133 partition.
- Upstream minimum/2 imputation and log2 transformation are separated from WrapEvoFS median-imputation and missingness-threshold configuration.
- A configured imputation/filtering rule is no longer presented as proof that imputation or filtering occurred.
- Broad training-only standardization language was replaced by component-specific scaling statements.
- Common scaling=none, SVM-L1 internal standardization, Bayesian development-fitted scaling, STABL unresolved scaling, and BLiP not-applicable status are separated.
- “test-isolated” and “all preprocessing” claims were narrowed to the documented WrapEvoFS pipeline boundary.
- “reproducible” is qualified as an auditable software/analysis path and figure/artifact reproduction subject to restricted source data.
- Exact empirical package commit and full-run reconstruction are no longer implied.

# 7. Unresolved author questions

1. **ADNI 532/133 partition은 누가, 언제, 어떤 코드와 seed로 생성했는가?**
   - 중요성: 7:3 설정과 empirical partition의 관계 및 “prespecified”의 시간적 의미를 확정하려면 필요하다.
   - 점검 파일: `source_corrected_methods_hyperparameters.csv`, embedded Supplementary Table S1, Figure 2 tables, data-access documents.
   - 확정 불가 문장: split ratio, random state, shuffle, stratification을 실제 partition-generation procedure로 기술하는 문장.

2. **ADNI participant identifier와 visit/specimen identifier를 제공하여 partition 간 중복을 확인할 수 있는가?**
   - 중요성: repeated visits, aliquots, duplicated subjects에 의한 leakage를 배제하려면 필요하다.
   - 점검 파일: 공개 저장소 전체, expected-file manifest, 원고 및 plotting tables.
   - 확정 불가 문장: participant-level leakage가 없었다는 단정.

3. **ADNI minimum/2 imputation 값은 development only, 각 partition별, combined data, 또는 외부 pipeline 중 어디에서 계산되었는가?**
   - 중요성: upstream held-out isolation의 범위를 결정한다.
   - 점검 파일: 원고, S1 설정 요약, README, access documentation.
   - 확정 불가 문장: complete end-to-end test isolation.

4. **ADNI WrapEvoFS preprocessing report에서 missing cells, imputed cells, missingness-filtered features, zero-variance-removed features 수는 각각 얼마인가?**
   - 중요성: median imputation과 threshold 0.2가 실제 실행되었는지 구분한다.
   - 점검 파일: S1 요약 및 저장소 전체; 원본 report는 없음.
   - 확정 불가 문장: “zero values were imputed” 또는 “median imputation was executed.”

5. **ADNI final fixed random forest와 CGGA final fixed random forest의 정확한 implementation/backend와 버전은 무엇인가?**
   - 중요성: GPU RAPIDS와 scikit-learn의 수치적 동일성을 가정할 수 없다.
   - 점검 파일: S1A, Table S20, Figure 2/5 aggregate outputs, archived figure source.
   - 확정 불가 문장: final held-out estimates를 특정 CPU/GPU implementation에 귀속하는 문장.

6. **ADNI bootstrap seed는 무엇인가?**
   - 중요성: 1,000-resample interval의 exact reconstruction에 필요하다.
   - 점검 파일: Figure 2 comparison settings and prediction table; seed 기록 없음.
   - 확정 불가 문장: ADNI bootstrap의 exact deterministic regeneration.

7. **STABL에 scaling이 적용되었는가? 적용되었다면 scaler type과 fitting partition은 무엇인가?**
   - 중요성: candidate-generation preprocessing을 구성요소별로 완결하려면 필요하다.
   - 점검 파일: Figure 4 aggregate tables and captions; run code/scaler 없음.
   - 확정 불가 문장: STABL preprocessing의 정확한 재현.

8. **CGGA PMID32021566 데이터의 exact accession/download URL, expression platform, MGMT endpoint derivation, inclusion/exclusion, QC, batch handling, duplicate handling을 제공할 수 있는가?**
   - 중요성: disease-domain cohort와 upstream processing provenance를 독립적으로 확인하려면 필요하다.
   - 점검 파일: 제공 CSV 네 개, schema, Table S12, Methods, README.
   - 확정 불가 문장: upstream cohort construction과 preprocessing의 상세 기술.

9. **Empirical run에 사용된 WrapEvoFS exact commit hash, environment lock, RAPIDS/scikit-learn/XGBoost versions는 무엇인가?**
   - 중요성: v0.1.0 표기만으로 exact run environment를 고정할 수 없다.
   - 점검 파일: `CITATION.cff`, `audit/software_versions.json`, environment files, repository metadata.
   - 확정 불가 문장: exact end-to-end empirical reconstruction.

# 8. Validation checklist

- [x] ADNI split counts and split description agree. 단, original split-generation procedure는 unresolved이다.
- [x] CGGA compression denominators are explicit.
- [x] All sample and class totals reconcile.
- [x] All feature counts reconcile.
- [x] Missing-value and imputation steps are distinguished.
- [x] Upstream and in-pipeline preprocessing are distinguished.
- [x] Scaling is documented by analytical component. STABL 및 일부 scaler artifacts는 unresolved로 표시했다.
- [x] Software defaults are separated from empirical settings.
- [x] Bootstrap settings are analysis-specific.
- [x] CV settings are analysis-specific.
- [ ] CPU/GPU backends are fully identified. ADNI RFECV/GA는 GPU로 확인되었으나 final fixed-RF backends와 exact versions는 unresolved이다.
- [x] Reproducibility claims match available artifacts.
- [x] No references or citations were modified.
- [x] No Step 2 or Step 3 issues were substantively edited.

Step 1의 evidence-supported 수정은 완료되었다. 다만 위 unresolved 항목 때문에 empirical run 전체가 단일한 실행 기록으로 완전하고 모호함 없이 재구성되었다고 주장하지 않는다.
