# Archived singleton BLiP function; feature_names is the canonical candidate list.
# Source: 02_restricted_blip_rf_and_csv_exports_COLAB.ipynb.
# Activity per feature: mean(max(abs(beta_MCI_CN), abs(beta_Dementia_CN),
# abs(beta_Dementia_CN-beta_MCI_CN)) > log(OR_threshold)) across posterior draws.
# The function is preserved verbatim. Its source notebook supplies numpy, pandas,
# CandidateGroup, BLiP, and feature_names; this excerpt does not execute a fit.

def run_singleton_blip(activity_probability, q, analysis_name):
    activity_probability = np.asarray(activity_probability, dtype=float)
    candidate_groups = [
        CandidateGroup(
            group={int(index)},
            pep=float(1.0 - activity_probability[index]),
            data={"feature_index": int(index), "feature": feature_names[index]},
        )
        for index in range(len(feature_names))
    ]
    detections, problem_status = BLiP(
        cand_groups=candidate_groups,
        q=float(q),
        error="fdr",
        max_pep=1.0,
        deterministic=True,
        perturb=False,
        verbose=False,
        solver="CLARABEL",
        return_problem_status=True,
    )

    rows = []
    for detection in detections:
        group = sorted(int(i) for i in detection.group)
        if len(group) != 1:
            raise RuntimeError(f"Singleton BLiP returned non-singleton group: {group}")
        index = group[0]
        rows.append({
            "analysis": analysis_name,
            "feature_index": index,
            "feature": feature_names[index],
            "posterior_activity_probability": float(activity_probability[index]),
            "posterior_error_probability": float(1.0 - activity_probability[index]),
            "blip_reported_pep": float(detection.pep),
            "blip_q": float(q),
        })
    columns = [
        "analysis", "feature_index", "feature", "posterior_activity_probability",
        "posterior_error_probability", "blip_reported_pep", "blip_q",
    ]
    return pd.DataFrame(rows, columns=columns), problem_status
