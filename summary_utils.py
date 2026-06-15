import pandas as pd


SPOT_MAPPING = {
    "LongSpotLeft": {
        "env": "Env.LongSpotLeft",
        "ai": "AI.LongSpotLeft",
        "missed": "Missed_LongSpotLeft",
        "false": "False_LongSpotLeft",
    },
    "PerpSpotLeft": {
        "env": "Env.PerpSpotLeft",
        "ai": "AI.PerpSpotLeft",
        "missed": "Missed_PerpSpotLeft",
        "false": "False_PerSpotLeft",
    },
    "DiagSpotLeft": {
        "env": "Env.DiagSpotLeft",
        "ai": "AI.DiagSpotLeft",
        "missed": "Missed_DiagSpotLeft",
        "false": "False_DiagSpotLeft",
    },
    "LongSpotRight": {
        "env": "Env.LongSpotRight",
        "ai": "AI.LongSpotRight",
        "missed": "Missed_LongSpotRight",
        "false": "False_LongSpotRight",
    },
    "PerpSpotRight": {
        "env": "Env.PerpSpotRight",
        "ai": "AI.PerpSpotRight",
        "missed": "Missed_PerpSpotRight",
        "false": "False_PerpSpotRight",
    },
    "DiagSpotRight": {
        "env": "Env.DiagSpotRight",
        "ai": "AI.DiagSpotRight",
        "missed": "Missed_DiagSpotRight",
        "false": "False_DiagSpotRight",
    },
}


def prepare_raw_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]
    df = df.dropna(how="all")

    for spot_info in SPOT_MAPPING.values():
        for col in spot_info.values():
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


def build_summary_table(df: pd.DataFrame) -> pd.DataFrame:
    summary_rows = []

    for spot_type, cols in SPOT_MAPPING.items():
        env_col = cols["env"]
        ai_col = cols["ai"]
        missed_col = cols["missed"]
        false_col = cols["false"]

        required_cols = [env_col, ai_col, missed_col, false_col]
        if not all(col in df.columns for col in required_cols):
            continue

        total_env = df[env_col].sum()
        total_ai = df[ai_col].sum()
        total_missed = df[missed_col].sum()
        total_false = df[false_col].sum()
      

        correct_count = total_env - total_missed

        miss_pct = round(total_missed / total_env * 100) if total_env != 0 else 0
        false_pct = round((total_false / total_env * 100), 1) if total_env != 0 else 0
        correct_ratio = round((total_env - total_missed) / total_env * 100) if total_env != 0 else 0
        overcount_pct = round((max(total_ai - total_env, 0) / total_env * 100), 1) if total_env != 0 else 0
        coverage_pct = round((min(total_ai, total_env) / total_env * 100), 1) if total_env != 0 else 0
        count_error_pct = round((abs(total_ai - total_env) / total_env * 100), 1) if total_env != 0 else 0
        quality_score   = round(correct_ratio - overcount_pct, 1)
        
        summary_rows.append({
            "SpotType": spot_type,
            "TotalEnv": int(total_env),
            "TotalAI": int(total_ai),
            "TotalMissed": int(total_missed),
            "TotalFalse": int(total_false),
            "Miss%": round(miss_pct, 1),
            "False%": round(false_pct, 1),
            "Correct Spot Ratio": round(correct_ratio, 1),
            "Overcount %": round(overcount_pct, 1),
            "Coverage %": round(coverage_pct, 1),
            "Count Error %": round(count_error_pct, 1),
            "Quality Score": round(quality_score, 1),
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