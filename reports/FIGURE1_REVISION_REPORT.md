# Figure 1 수정 보고서

## 1. Editable source file modified

편집 가능한 원본인 `analysis/build_revised_figure_sources.py`의 `build_figure_1()`을 수정했다. 내보낸 이미지 자체만 편집하지 않았으며, 크기 설정은 `analysis/figure_specs.json`에 170 × 125 mm로 반영했다. 수정 전 두 번째 버전은 `data/revised_assets/Figure_1/versions/2026-07-26_v2/`에 보존했다.

## 2. Exported files generated

같은 생성 원본에서 `manuscript/figures/main/Figure_1/`의 SVG, 벡터 PDF, 600-dpi PNG를 다시 생성했다. PNG는 4,016 × 2,953 px이며, 출판용 TIFF도 같은 해상도에서 LZW 압축으로 생성했다. Google Docs용 Figure 1 자산도 새 PNG로 교체했다.

## 3. Panel a workflow changes

패널 제목을 “Locked-split WrapEvoFS workflow”로 정리했다. Supplied matrices에서 fixed study split으로 이동한 뒤 development partition과 locked held-out partition이 같은 split에서 직접 갈라지도록 구성했다. 개발 경로에는 in-pipeline preprocessing, candidate generation, RFECV target-size estimation, five size-guided GA runs, development-CV ranking, top-three Jaccard-medoid locking, locked signature + model settings를 순서대로 배치했다. Candidate generation 아래에는 `SVM-L1 · XGBoost · Boruta-RF`를 보조 문구로 넣었다. 검증 범위 문장은 중립 회색 footer band로 분리했다.

## 4. Held-out pathway and arrow-routing changes

Held-out 경로는 청회색 점선으로 표시하고 preprocessing, candidate generation, RFECV, GA, CV ranking 및 locking 단계와 완전히 분리했다. Locked signature + model settings는 보라색 실선으로 one-time held-out evaluation에 연결했다. 두 입력만 최종 평가 상자로 수렴하며, 모든 화살표 머리는 연결선에 부착되어 있다. 상자나 텍스트를 관통하거나 서로 교차하는 화살표는 없다.

## 5. Confirmation that Panel b contains no arrows

패널 b의 SVG 구간을 구조적으로 검사했으며 `<line>`, `<path>`, `marker-end`가 모두 0개였다. 따라서 ADNI, CGGA, component ablation, Bayesian, STABL 및 BLiP 사이에 순서·인과·검증 관계를 암시하는 화살표가 없다.

## 6. Core-container layout changes

왼쪽의 큰 solid-green 컨테이너를 “Core workflow demonstrations”로 구성했다. 같은 높이의 ADNI multiclass와 CGGA binary 카드를 위쪽에 나란히 놓고, 더 넓은 component-ablation 카드를 아래 중앙에 배치했다. 이 컨테이너가 패널 b의 약 64% 폭을 차지하여 core demonstrations가 시각적으로 우세하다.

## 7. Component-ablation coral styling

Component ablation을 footer 문구가 아니라 완전한 둥근 사각형 카드로 만들었다. `#D85A4A` 계열의 muted-coral 테두리와 `#FBEFEB` 계열의 옅은 채움, 별도의 하단 행 위치 및 명시적 제목을 사용했다. Coral은 이 카드에만 사용되어 오류나 경고 의미로 보이지 않는다.

## 8. Secondary-analysis purple styling

오른쪽에는 눈에 보이는 lavender fill과 dashed muted-purple 외곽선을 가진 “Secondary downstream analyses” 컨테이너를 배치했다. 내부에 “Full-feature Bayesian reference”와 “Restricted Bayesian · STABL · BLiP”를 각각 독립된 보라색 카드로 분리했다. 두 카드와 core 컨테이너 사이에는 연결선이 없다.

## 9. `Fig. X` typography and placement

`Fig. 2`부터 `Fig. 6`까지 모두 각 카드 내부 하단 중앙에 배치했다. 같은 크기, regular weight, muted secondary-text color를 적용했으며 제목이나 설명보다 한 단계 작게 설정했다. Figure 번호는 badge나 굵은 글씨로 강조하지 않아 원고 탐색용 보조 정보로만 기능한다.

## 10. Caption changes

캡션을 최종 도식과 일치하도록 갱신했다. Fixed split의 직접 분기, 개발 단계, locked held-out의 격리, 두 입력의 one-time evaluation 합류, supplied matrices에서 시작하는 검증 범위, ADNI/CGGA core demonstrations, component ablation 및 secondary downstream analyses의 비필수적 성격을 모두 명시했다. 동일한 캡션을 Figure 1 폴더, Google Docs 자산 및 최종 DOCX 생성 코드에 동기화했다.

## 11. Grayscale and accessibility validation

회색조 렌더를 직접 검사했다. 개발·held-out·signature 경로는 실선/점선, 위치 및 라벨로 구분되고, core와 secondary 컨테이너는 solid/dashed 외곽선으로 구분된다. Component ablation은 별도 하단 카드와 완전한 테두리로 식별된다. 색상에 의존하지 않아도 모든 분석 범주와 경로가 구분되며, 최종 원고 크기에서 텍스트와 `Fig. X` 라벨이 읽힌다.

## 12. Remaining unresolved terminology

“Fixed study split”은 제공된 고정 development/held-out 행렬과 일치하므로 유지했다. 다만 ADNI 원 split 생성 절차가 독립적으로 복원되지 않았으므로 “prespecified”라는 표현은 사용하지 않았다. 전체 데이터 이력에 대한 전역적 “training-only” 주장도 사용하지 않았고, verified workflow boundary가 supplied matrices에서 시작함을 명시했다. CGGA는 external validation으로 부르지 않았으며 Bayesian, STABL 및 BLiP도 biomarker validation으로 기술하지 않았다.

## 13. Final visual-validation result

최종 SVG, PDF, PNG, TIFF와 원고 내 Figure 1을 확인했다. 패널 a는 두 번째 버전의 true branching split을 보존하고, held-out 격리와 최종 합류를 정확히 표시한다. 패널 b는 완전한 no-arrow study map이며 coral ablation 카드, lavender secondary 컨테이너, 두 개의 독립 secondary 카드 및 일관된 작은 `Fig. X` 라벨을 포함한다. 40쪽 Word-PDF 전체 렌더를 점검했으며 Figure 1은 3쪽에서 clipping, 겹침, 누락 글꼴 또는 캡션 분리 없이 정상 배치되었다.
