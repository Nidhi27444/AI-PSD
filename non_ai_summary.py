import pandas as pd

NON_AI_SPOT_MAPPING = {
    "LongSpotLeft": {
        "env": "Env.LongSpotLeft",
        "det": "NON_AI.LongSpotLeft",
    },
    "PerpSpotLeft": {
        "env": "Env.PerpSpotLeft",
        "det": "NON_AI.PerpSpotLeft",
    },
    "DiagSpotLeft": {
        "env": "Env.DiagSpotLeft",
        "det": "NON_AI.DiagSpotLeft",
    },
    "LongSpotRight": {
        "env": "Env.LongSpotRight",
        "det": "NON_AI.LongSpotRight",
    },
    "PerpSpotRight": {
        "env": "Env.PerpSpotRight",
        "det": "NON_AI.PerpSpotRight",
    },
    "DiagSpotRight": {
        "env": "Env.DiagSpotRight",
        "det": "NON_AI.DiagSpotRight",
    },
}


def prepare_non_ai_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]
    df = df.dropna(how="all")

    for spot_info in NON_AI_SPOT_MAPPING.values():
        for col in spot_info.values():
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


def build_non_ai_summary_table(df: pd.DataFrame) -> pd.DataFrame:
    df = prepare_non_ai_data(df)
    summary_rows = []

    for spot_type, cols in NON_AI_SPOT_MAPPING.items():
        env_col = cols["env"]
        det_col = cols["det"]

        required_cols = [env_col, det_col]
        if not all(col in df.columns for col in required_cols):
            continue

        temp = df[[env_col, det_col]].copy()
        temp["correct"] = temp[[env_col, det_col]].min(axis=1)
        temp["missed"] = (temp[env_col] - temp[det_col]).clip(lower=0)
        temp["false"] = (temp[det_col] - temp[env_col]).clip(lower=0)

        total_env = temp[env_col].sum()
        total_det = temp[det_col].sum()
        correct_count = temp["correct"].sum()
        total_missed = temp["missed"].sum()
        total_false = temp["false"].sum()

        miss_pct = round((total_missed / total_env) * 100, 1) if total_env != 0 else 0
        false_pct = round((total_false / total_env) * 100, 1) if total_env != 0 else 0
        correct_ratio = round((total_env - total_missed) / total_env * 100) if total_env != 0 else 0
        overcount_pct = round((max(total_det - total_env, 0) / total_env) * 100, 1) if total_env != 0 else 0
        coverage_pct = round((min(total_det, total_env) / total_env * 100), 1) if total_env != 0 else 0
        count_error_pct = round((abs(total_det - total_env) / total_env) * 100, 1) if total_env != 0 else 0
        quality_score = round(correct_ratio - overcount_pct, 1)

        summary_rows.append({
            "SpotType": spot_type,
            "TotalEnv": int(total_env),
            "TotalAI": int(total_det),
            "TotalMissed": int(total_missed),
            "TotalFalse": int(total_false),
            "Miss%": miss_pct,
            "False%": false_pct,
            "Correct Spot Ratio": correct_ratio,
            "Overcount %": overcount_pct,
            "Coverage %": coverage_pct,
            "Count Error %": count_error_pct,
            "Quality Score": quality_score,
            "Correct Count": int(correct_count),
        })

    if not summary_rows:
        return pd.DataFrame(columns=[
            "SpotType", "TotalEnv", "TotalAI", "TotalMissed", "TotalFalse",
            "Miss%", "False%", "Correct Spot Ratio", "Overcount %",
            "Coverage %", "Count Error %", "Quality Score", "Correct Count"
        ])

    return pd.DataFrame(summary_rows)[[
        "SpotType", "TotalEnv", "TotalAI", "TotalMissed", "TotalFalse",
        "Miss%", "False%", "Correct Spot Ratio", "Overcount %",
        "Coverage %", "Count Error %", "Quality Score", "Correct Count"
    ]]