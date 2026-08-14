# Property test report

Date: 2026-08-03
Package: companion repository `junseoparkX/wrapevofs-package`
Scope: locking/configuration behavior only; no empirical feature-selection analysis was executed.

## Result

The proposition-focused suite passed:

```text
.\.revision_env\Scripts\python.exe -m pytest -q tests/test_locking.py tests/test_config_defaults.py --basetemp .tmp/pytest_regret_locking_20260803_final
68 passed in 6.56s
```

Adjacent artifact, CLI, and metric-alignment checks also passed:

```text
.\.revision_env\Scripts\python.exe -m pytest -q tests/test_artifacts.py tests/test_cli_options.py tests/test_metric_alignment.py --basetemp .tmp/pytest_regret_locking_adjacent_20260803
5 passed, 1 warning in 2.60s
```

The warning was a pre-existing scikit-learn `Liblinear` convergence warning in the small artifact-export test. It did not affect locking and was not suppressed.

## Required-case coverage

| Required case | Verification |
|---|---|
| Empty candidate bank | Rejected with an actionable `ValueError`. |
| `delta < 0` | Rejected before eligibility calculation. |
| Singleton bank | Selected directly; empirical regret is zero and mean Jaccard is missing. |
| Unique best at `delta = 0` | The sole score maximizer is selected. |
| Multiple exact best-score ties at `delta = 0` | The complete zero-regret pool undergoes Jaccard-medoid selection. |
| All candidates eligible | Full-bank medoid behavior is verified. |
| Strict selected regret `<= delta` | Exact boundary comparison, runtime postcondition, and 25 generated banks were checked. |
| Candidate-record permutations | All six permutations of a three-record bank produced identical selected features and canonical audits. |
| Duplicated masks | Multiplicity is retained as voting mass and serialized. |
| Identical masks and scores | One scientific mask is selected; one run ID is retained only as provenance. |
| Stable hash across processes | Two independent Python processes produced the same digest. |
| Feature-order canonicalization | Reordered feature input produced the same canonical features and digest. |
| Nonfinite scores | `NaN`/infinite scores are rejected. |
| Inconsistent supplied universes | Reordered/different supplied universes are rejected. |
| Lower-is-better misuse | Any orientation other than `larger_is_better` is rejected. |
| Serialization and reload | Candidate audit, pairwise audit, and metadata were saved and reloaded. |
| Deterministic audit reproduction | Repeated executions produced identical DataFrames and metadata. |

## Generated property checks

- Strict feasibility was evaluated on 25 deterministically generated six-candidate banks with varying masks, finite scores, and tolerances.
- Permutation invariance and repeated-execution determinism were evaluated on 12 additional generated five-candidate banks.
- An exhaustive permutation test covered every ordering of a fixed three-candidate bank.

These are deterministic generated-case property tests implemented with `pytest` parametrization; they do not depend on an optional Hypothesis installation.

## Scope boundary

No test ran the GA, RFECV, Direct selection, held-out evaluation, Bayesian analysis, STABL, BLiP, bootstrap analysis, or any manuscript empirical experiment. The tests establish package behavior for supplied artificial candidate banks; they do not test predictive superiority, external validity, generalization error, or biomarker stability.
