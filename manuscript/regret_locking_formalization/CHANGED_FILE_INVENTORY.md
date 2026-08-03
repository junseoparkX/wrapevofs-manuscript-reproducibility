# Changed-file inventory

## Authoritative manuscript tree

Root: `manuscript/`

| File | Change |
|---|---|
| `sections/main_text.tex` | Inserted the concise guarantee, canonical tie rule, complexity summary, claim boundary, and revised Discussion wording. |
| `tables/table_01.tex` | Revised only Algorithm 1 locking/tie/audit lines 17--22. |
| `sections/supplementary.tex` | Included the complete proofs, detailed complexity derivation, correspondence reference, and final S17 table; adjusted only the first Supplementary Figure placement to avoid a heading-only page. |
| `tables/table_39.tex` | Added Supplementary Table S17; existing tables S1--S16 retain their numbers. |
| `main.pdf` | Recompiled authoritative 43-page manuscript PDF. |
| `main.aux`, `main.bbl`, `main.blg`, `main.fdb_latexmk`, `main.fls`, `main.log`, `main.out` | Refreshed LaTeX build products. |

No file under `figures/` was edited. No existing empirical table source was edited.

## Formalization deliverables

Directory: `regret_locking_formalization/`

1. `REGRET_LOCKING_PROPOSITIONS.md`
2. `REGRET_LOCKING_PROPOSITIONS.tex`
3. `REGRET_LOCKING_COMPLEXITY.md`
4. `IMPLEMENTATION_PROPOSITION_CROSSWALK.csv`
5. `PROPERTY_TEST_REPORT.md`
6. `proposed_main_methods_insertion.md`
7. `proposed_algorithm1_revision.md`
8. `proposed_supplementary_methods_proofs.md`
9. `proposed_discussion_insertion.md`
10. `REGRET_LOCKING_PACKAGE_PATCH.patch`
11. `CHANGED_FILE_INVENTORY.md`
12. `VALIDATION_REPORT.md`

## Package tree

Root: companion `wrapevofs-package` repository

| File | Necessary change |
|---|---|
| `src/wrapevofs/locking.py` | Exact eligibility, common-universe masks, unchanged authoritative stable hash, canonical selection/audits, duplicate policy, postcondition, and input validation. |
| `src/wrapevofs/config.py` | Explicit larger-is-better orientation and canonical tie configuration. |
| `configs/default.yaml` | Serialized orientation and canonical tie defaults. |
| `configs/recommended_regret_constrained.yaml` | Recommended strict-lock configuration. |
| `tests/test_locking.py` | Unit, generated-property, permutation, cross-process, and serialization tests. |
| `tests/test_config_defaults.py` | Configuration contract tests. |
| `README.md` | Scientific tie, duplicate, provenance, and strict-feasibility documentation. |
| `docs/ARTIFACT_SCHEMA.md` | Canonical masks/hashes, exact eligibility, duplicate multiplicity, singleton, and audit-schema documentation. |
| `CHANGELOG.md` | Correct strict-pool and stable-tie behavior. |

The package worktree contained extensive pre-existing uncommitted changes. No unrelated file was reverted, staged, or committed. The supplied patch was generated with a temporary Git index and is restricted to the nine paths above; the real Git index was not modified.

## Validation scratch

- Manuscript `.tmp/texmf-*`, `.tmp/xdg-cache`, `.tmp/regret_render/`, and `.tmp/regret_render_final/` contain font-cache and page-render QA files.
- Package `.tmp/pytest_regret_locking_*` contains isolated pytest temporary files; `.tmp/regret_locking_patch.index` and `.tmp/git-objects/` were used only to generate the focused patch without touching the real index.

These scratch paths are not manuscript, package, empirical, or deliverable inputs.
