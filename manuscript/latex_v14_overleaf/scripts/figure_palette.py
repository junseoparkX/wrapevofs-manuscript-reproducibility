"""Submission palette shared by all reproducible WrapEvoFS figures.

The three branch colors are semantic and must not be reassigned.  Remaining
colors are muted structural accents for comparisons that do not encode a GA
branch.  Figure 1 is an externally edited workflow graphic and is deliberately
outside this palette module.
"""

BRANCH_COLORS = {
    "svm_l1": "#1F7A8C",
    "xgboost": "#C78A0A",
    "boruta_rf": "#8B5E83",
}
BRANCH_LABEL_COLORS = {
    "SVM-L1": BRANCH_COLORS["svm_l1"],
    "XGBoost": BRANCH_COLORS["xgboost"],
    "Boruta-RF": BRANCH_COLORS["boruta_rf"],
}

DARK = "#263746"
MID = "#637381"
LIGHT = "#C8D1D8"
PALE = "#EEF2F4"

ORIGINAL = "#727A82"
CURRENT = "#4F7188"
STRESS = "#A65E3B"
SECONDARY = "#746A88"
SAGE = "#6F8F78"
TERRACOTTA = "#A65E3B"
OCHRE = "#B1843E"

DATASET_COLORS = {"AMP-AD": CURRENT, "CGGA": SECONDARY}
FEATURE_SPACE_COLORS = {"full_1781": CURRENT, "stable_1346": OCHRE}
