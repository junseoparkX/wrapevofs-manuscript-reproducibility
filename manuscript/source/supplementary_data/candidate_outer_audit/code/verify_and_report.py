"""Independent diagnostic spot checks and a source-accounted Korean strengthening report."""
import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def read(path):
    with path.open(newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def main():
    protocol = json.loads((HERE / 'protocol.json').read_text())
    ph = sha(HERE / 'protocol.json')
    assert ph == (HERE / 'FROZEN_BEFORE_NEW_PREDICTIONS.sha256').read_text().strip()
    for name, digest in protocol['code_sha256'].items():
        assert sha(HERE / name) == digest
    amendment = json.loads((HERE / 'reference_amendment.json').read_text())
    assert sha(HERE / 'predict_candidates_v2.py') == amendment['predictor_sha256']
    validation = json.loads((HERE / 'results/analysis_validation.json').read_text())
    for name, digest in validation['output_sha256'].items():
        assert sha(HERE / 'results' / name) == digest
    predictions = json.loads((HERE / 'prediction_verification.json').read_text())
    training = json.loads((HERE / 'training_manifest.json').read_text())
    assert training['fits'] == 150 and training['hostname'] == 'fenn10'
    assert predictions['original_policy_checks'] == 120 and predictions['maximum_original_probability_difference'] < 1e-12
    banks = json.loads((HERE / 'candidate_inventory.json').read_text())
    diagnostic = {(r['bank_id'], int(r['split'])): r for r in read(HERE / 'results/independent_half_selection_diagnostics.csv')}
    with np.load(HERE / 'private_predictions/candidate_oof.npz', allow_pickle=False) as d:
        probability, labels, folds = d['probabilities'], d['y'], d['folds']
    rng = np.random.default_rng(protocol['selection_optimism']['seed'])
    checks = 0
    for bank_index, bank in enumerate(banks):
        b, r = protocol['branches'].index(bank['branch']), bank['repeat'] - 1
        ix = np.flatnonzero(folds[b, r] == bank['fold'])
        y = labels[ix]
        values = probability[b, :, r][:, ix, :]
        class_indices = [np.flatnonzero(y == c) for c in range(4)]
        for k in range(200):
            chosen = np.concatenate([rng.permutation(indices)[:len(indices) // 2] for indices in class_indices])
            if bank_index not in [0, 14, 29] or k not in [0, 199]:
                continue
            other = np.setdiff1d(np.arange(len(y)), chosen)
            a = np.array([roc_auc_score(y[chosen], v[chosen], multi_class='ovr', average='macro') for v in values])
            b_auc = np.array([roc_auc_score(y[other], v[other], multi_class='ovr', average='macro') for v in values])
            cs = bank['candidates']
            priority = sorted(range(5), key=lambda run: (-cs[run]['locking_score'], cs[run]['feature_count'], cs[run]['mask_hash']))
            wa, wb = max(priority, key=lambda run: a[run]), max(priority, key=lambda run: b_auc[run])
            row = diagnostic[(bank['bank_id'], k)]
            assert [wa, wb] == [int(row['selected_on_A_run']), int(row['selected_on_B_run'])]
            apparent = (a[wa] + b_auc[wb]) / 2
            independent = (b_auc[wa] + a[wb]) / 2
            assert abs(apparent - float(row['apparent_selection_half_AUROC'])) < 1e-12
            assert abs(independent - float(row['independent_half_AUROC'])) < 1e-12
            for policy, run in bank['policy_runs'].items():
                assert abs((a[run] + b_auc[run]) / 2 - float(row[f'fixed_{policy}_half_AUROC'])) < 1e-12
            checks += 1
    original = read(ROOT / 'manuscript/latex_v19_overleaf/supplementary_data/tcga_nested_v1_v2/oof_metrics.csv')
    estimates = {(r['branch'], r['method']): float(r['estimate']) for r in original if r['metric'] == 'macro_ovr_auroc'}
    oof_checks = 0
    for row in read(HERE / 'results/repeated_oof_AUROC.csv'):
        if row['policy'] in protocol['policies']:
            assert abs(float(row['mean_repeated_OOF_AUROC']) - estimates[(row['branch'], row['policy'])]) < 1e-12
            oof_checks += 1
    assert checks == 6 and oof_checks == 12
    manuscript_diff = subprocess.run(['git', 'diff', '--name-only', '--', 'manuscript/latex_v19_overleaf'], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    assert not manuscript_diff.strip()
    result = {'verified_utc': datetime.now(timezone.utc).isoformat(), 'protocol_sha256': ph,
              'all_frozen_code_hashes_unchanged': True, 'reference_correction_is_recorded': True,
              'all_7_output_hashes_match': True, 'original_OOF_point_estimates_reproduced': oof_checks,
              'independent_sklearn_array_slicing_selection_checks': checks,
              'original_policy_prediction_checks': 120, 'trained_candidates_on_fenn10': 150,
              'tracked_manuscript_files_unchanged': True}
    (HERE / 'results/final_verification.json').write_text(json.dumps(result, indent=2) + '\n')
    summary = read(HERE / 'results/summary_by_branch.csv')
    table = '\n'.join(f"{r['branch']}: 候補範囲={float(r['mean_within_bank_outer_AUROC_range']):.6f}; 선택자료 AUROC={float(r['mean_apparent_selection_half_AUROC']):.6f}; 반대쪽 AUROC={float(r['mean_independent_half_AUROC']):.6f}; 낙관성={float(r['mean_selection_optimism']):.6f}".replace('候補範囲','후보 간 AUROC 범위') for r in summary)
    report = f'''WrapEvoFS v19: 긍정적 기여 강화와 fenn10 추가 실험
날짜: 2026-11-12 (America/Whitehorse)

Material Passport
Type: experiment-result and argument blueprint
Status: VERIFIED
Scope: fixed-bank retrospective internal diagnostic; manuscript unchanged
Protocol SHA256: {ph}
Raw participant data/model artifacts: private, not publication artifacts

1. 가장 강한 중심 주장

반복 탐색으로 얻은 서로 다른 압축 signature 중 하나를, 사전에 정한 개발점수 손실 한도 안에서 대표성 기준으로 확정하는 실용적 선택 절차를 전면에 둔다.
독자가 바로 이해할 질문은 '여러 run에서 다른 signature가 나오면 무엇을 최종 결과로 남기는가?'이다. 그 답을 점수 한도, 후보 간 겹침, 고정된 선택 기록으로 제공한다.
표현의 중심을 compact signature, 실제 결정 변화, 정량적 trade-off, 사용 조건에 둔다. 구현 검증과 내부 개발 이력은 뒤로 옮긴다.
근접 성능 모델의 다양성은 기존 model-multiplicity 연구와 연결할 수 있다. 새로 주장할 대상은 그 현상의 최초 발견이 아니라 이 연구의 구체적 선택 절차와 검증된 사용 사례다.
관련 1차 문헌: Marx et al. 2020, https://proceedings.mlr.press/v119/marx20a.html

2. 기존 CSV에서 재확인한 앞부분의 핵심 수치

TCGA: 491명, 두 번의 5-fold outer CV, 30개 bank, 후보 150개.
SVM-L1: Direct 81.0개 -> locked 14.6개, 81.98% 감소; AUROC 0.839708 -> 0.826502, 차이 -0.013207 [원래 95% CI -0.024171,-0.003142].
XGBoost: Direct 100.0개 -> locked 20.0개, 80.00% 감소; AUROC 0.831363 -> 0.827020, 차이 -0.004343 [-0.014393,+0.006325].
Boruta-RF: Direct 100.0개 -> locked 18.0개, 82.00% 감소; AUROC 0.843283 -> 0.827705, 차이 -0.015578 [-0.024851,-0.006171].
압축은 Direct 이후의 감소율이며, 25,118개 전체 입력 대비 감소를 locking만의 효과로 돌리지 않는다. 이 압축은 전체 pipeline 결과다.
AUROC의 98.2-99.5%를 유지했다는 비율은 수학적으로 맞지만, 초록에서는 절대 AUROC와 절대 차이가 더 명확하다.

δ=0.01 초과 bank: highest-score 0/30; top-three medoid 5/30 (최대 0.023614); full-bank medoid 14/30 (최대 0.038689); 제안 규칙 0/30 (최대 0.009784).
highest-score 역시 gap 제약을 충족한다. 제안 규칙의 추가 목표는 eligible pool 안에서 대표성도 반영하는 것이다.
최고 개발점수 후보와 선택이 달라진 bank는 11/30; 바뀐 경우 eligible-pool mean Jaccard 증가 중앙값은 0.042857이다. 이는 최적화한 선택 기준의 증가이며, 별도의 생물학적 재현성 개선으로 해석하지 않는다.

본문에 native comparator의 성능과 feature 수를 한 번 명료하게 함께 쓴다. Native Elastic Net은 SVM-L1과 Boruta-RF에서 높은 AUROC를 보였고, native stability selection도 SVM-L1에서 높았다. 같은 크기로 제한한 비교의 이점과 서로 다른 질문임을 설명한다.
Random-bank 대비 차이 -0.0018,+0.0102,-0.0043을 함께 보여 주고, 저장된 random bank에도 규칙을 적용할 수 있다는 생성기 독립성을 부각한다. 이를 GA 비용의 우월성으로 주장하지 않는다.

3. 이번에 완료한 fenn10 추가 실험

서버 경로: /data2/junseo/wrapevofs/v19_candidate_outer_audit_20261112
기존에 승인된 development NPZ만 읽어 후보 150개에 각각 RF 500 trees를 적합했다. workers=4, 학습 약 47.19초.
기존 common condition final seed, 후보 순서, feature 집합, hyperparameter를 유지했다. GA, Direct, RFECV, δ, 원래 선택은 변경하지 않았다.
새 outer 자료/label/ID/prediction은 fenn10에 보내지 않았다. 서버 학습 모델을 로컬로 받아 원래 outer-test에 예측했다.
원고에 쓰인 common-seed 평가본과 네 규칙 × 30 bank의 120개 예측을 대조해 최대 오차 {predictions['maximum_original_probability_difference']:.3g}로 재현했다.
초기 검증에서 pre-refresh raw prediction 파일을 참조한 오류를 발견했다. reference_amendment.json에 수정 사유와 올바른 원본 hash를 기록했다. 원래 frozen protocol과 모델은 유지했고, 성능 지표를 계산하기 전에 참조를 수정했다.

모든 후보의 전체 outer-fold AUROC를 계산했다. 같은 bank의 다섯 후보 간 범위는 평균 0.030933이었다.
추가로 각 bank의 outer-test 약 98-99명을 class별로 거의 절반씩 나누는 200개 고정 난수 분할을 만들었다.
한 절반에서 AUROC가 가장 높은 run을 선택한 뒤 선택에 쓴 절반과 반대 절반에서 그 run을 평가했다. A/B를 바꿔 양방향 결과를 평균했다.
총 6,000개 분할 진단이며 독립 코호트 6,000개가 아니다. 각 후보 모델은 다시 학습하지 않았다.

{table}

주요 새 메시지: 평가자료를 보고 보고할 run을 고르는 행위의 낙관성을, 현재 논문의 후보군과 실제 예측으로 수치화했다. 전체 평균 차이는 +0.025331 AUROC였다.
절반당 약 49명에서 수행한 고정-bank 진단이므로, 원래 전체 outer-test에서의 정확한 편향이나 외부 환자군의 편향 추정치로 일반화하지 않는다. 분할 분위수는 신뢰구간이 아니다.
이 결과는 outcome을 보기 전에 선택 규칙을 고정해야 한다는 근거다. 사전에 고정한 highest-score도 이 원칙을 충족하므로 제안 medoid만의 고유한 편향 감소로 주장하지 않는다. 제안 medoid의 고유 역할은 점수 허용범위와 대표성의 결합이다.
선택에 쓴 자료에서 계산한 최댓값이 재평가값보다 크다는 방향 자체는 선택 연산에서 예상되는 성질이다. 이 분석의 실증적 기여는 현재 후보군에서 나타나는 크기를 정량화했다는 데 있다.

4. 가장 설득력 있는 Results와 figure 순서

(1) 결정 문제와 규칙: 최고점수, top-three medoid, full-bank medoid, 제안 규칙이 무엇을 선택하는지 보여 준다.
(2) TCGA의 실제 선택 변화: 11/30과 대안 규칙의 gap 초과 빈도. 단순히 30/30 충족을 반복하지 않는다.
(3) 압축과 예측 trade-off: 80-82% 감소, AUROC 0.827-0.828, Direct와 native/matched comparator를 같은 맥락에서 보고한다.
(4) 선택을 고정해야 하는 이유: 이번 후보 전수평가 및 반분 낙관성 진단. 본문에는 핵심 수치와 작은 패널, 상세 150개/6,000개 결과는 Supplement.
(5) 언제 대표성 기준이 도움이 되는가: 기존 시뮬레이션에서 aligned/competing topology, noise ratio 1 이상인 54개 시나리오는 모두 최고점수보다 oracle regret이 작았다. 효과 크기는 작으므로 방향과 조건을 설명한다.
(6) frozen held-out-center 평가로 실제 적용 범위를 보인다.
(7) objective 수정과 구현 검증은 마지막 기술 검증으로 둔다. 내부 legacy/archived 명칭은 Methods와 Supplement의 필요한 위치에 모은다.
Figure 1 workflow, Figure 2 결정/선택 변화, Figure 3 압축-성능, Figure 4 run 선택 진단과 사용 조건, Figure 5 held-out-center처럼 각 그림이 하나의 질문에 답하게 정리할 수 있다. 실제 재배치는 저자 검토 후이며 이번에 그림 파일은 수정하지 않았다.

5. 초록·Discussion·커버레터에서 앞세울 내용

초록 첫 문장은 독자의 결정 문제로 시작한다. 뒤이어 80-82% 압축, 11/30 선택 변화, 대안 medoid의 5/30 및 14/30 gap 초과 중 핵심 수치를 고른다.
이번 새 +0.0253 수치는 본문에서 진단 설계를 충분히 설명하는 것이 우선이다. 이를 초록에 넣을 경우 반드시 repeated half-sample diagnostic임을 붙이며, 분량이 짧은 초록의 주 수치로 무리하게 압축하지 않는다.
초록 결과 문장 예시: In the nested TCGA analysis, locked signatures retained 15-20 of 81-100 screened features, reducing feature counts by 80-82%, with macro AUROC estimates of 0.827-0.828.
선택 변화 문장 예시: The rule changed 11 of 30 highest-score selections while restricting the development-score gap to 0.01; rank-based and unrestricted medoids exceeded this gap in 5 and 14 banks, respectively.
이 두 문장에 필요한 성능 trade-off를 간결하게 연결한다. CI가 0을 포함한다는 사실로 동등성 또는 성능 비용 0을 선언하지 않는다.

Discussion은 기여와 정량 결과 -> 누가 언제 사용하는가 -> 다른 선택법과의 관계 -> 한계 한 문단 -> 구체적 사용 메시지의 순서로 쓴다.
적용 상황은 여러 run이 이미 존재하고, downstream assay나 후속 분석에 넘길 하나의 compact signature를 확정해야 하며, 허용 가능한 경험적 점수 차이를 사전에 정할 수 있는 경우다.
커버레터는 이 문제, 규칙의 구체적 해결 방식, 압축 및 결정 변화 수치, 실제 후보의 선택 낙관성 진단을 한 문단씩 연결한다. 코드 수정의 내부 이력으로 첫 문단을 시작하지 않는다.

6. 리뷰 제안에서 그대로 사용하면 안 되는 해석

개발 fold SE 평균 0.010905는 δ=0.01의 척도를 설명하는 사후 맥락이다. 이를 δ를 원래 그렇게 골랐다는 근거로 쓰지 않는다. 독립적 fold SE도, 두 후보의 paired 차이에 대한 SE도 아니다. 기존 one-SE 규칙과 유사한 선택 철학을 논의할 수 있지만 동일한 통계적 규칙으로 명명하지 않는다.
관측 Jaccard 0.114883에 대한 고정 cardinality·균등부분집합 null 기대값은 정확한 hypergeometric 합으로 0.103450이다. 이 비교만으로 차이가 유의하지 않다고 판정하거나 biological stability를 주장하지 않는다. 실제 search와 균등 null은 다르다.
시뮬레이션의 bank-size 결과를 단조 개선으로 쓰지 않는다. 저장된 sensitivity 표에서 R=5의 평균 oracle 차이는 +0.000018로, R=3과 R=100의 음수 값 사이에도 비단조 결과가 있다.
대표성 증가는 eligible pool에 대한 것이다. 전체 bank 대표성은 별도이며, 현재 30개 bank 중 일부에서는 최고점수보다 감소한다.
보조로 재계산한 2,000회 participant-cluster bootstrap은 새 난수 seed를 쓴 탐색적 민감도다. 원래 원고의 CI를 대체하거나 유리한 CI를 선택하지 않는다. 경계에 가까운 XGBoost/full-bank 비교의 새 CI는 0을 포함한다.

7. 검증 및 파일

고정 코드/설계 hash 유지, 기존 120개 예측 재현, 기존 12개 OOF 점추정 재현, weighted AUROC 600개 독립 sklearn 대조, 실제 배열 분리 방식의 추가 6개 독립 spot check를 통과했다.
학습·수정된 예측 검증·통계분석 stderr는 모두 0 byte. 원고의 tracked 파일 diff는 없다.
results/summary_by_branch.csv: 가장 짧은 신규 결과 표.
results/all_candidate_outer_metrics.csv: 후보 150개 전수 결과.
results/bank_diagnostics.csv: 후보별 성능 범위와 null reference.
results/independent_half_selection_diagnostics.csv: 분할 진단 6,000개 전체.
results/original_policy_geometry.csv: 네 규칙의 모든 bank별 gap·대표성.
results/repeated_oof_AUROC.csv 및 paired_original_policy_contrasts.csv: 네 규칙과 fixed-run 결과/보조 CI.
results/final_verification.json: 최종 검증.
private_models/, private_predictions/, local_dependencies/는 비공개 또는 실행환경 파일이며 publication source data에 포함하지 않는다.
'''
    (HERE / 'STRENGTHENING_REPORT_KO.txt').write_text(report, encoding='utf-8')
    print(json.dumps(result, indent=2))
    print('REPORT:', HERE / 'STRENGTHENING_REPORT_KO.txt')


if __name__ == '__main__':
    main()
