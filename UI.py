import streamlit as st
import pandas as pd
import plotly.express as px
import math
from constants import *
from non_ai_summary import build_non_ai_summary_table

BG = "#050B16"
PANEL = "#0B1322"
BORDER = "#23324A"
TEXT = "#F5F7FA"
MUTED = "#9FB0C8"
ACCENT = "#00A3FF"
ACCENT_2 = "#39B8FF"
GOOD = "#18C37E"
WARN = "#FFB020"
BAD = "#FF5A5F"

BLUE_DARK = "#0066CC"
BLUE_MEDIUM = "#3399FF"
BLUE_LIGHT = "#99CCFF"

GREEN_DARK = "#0F2B9D"
GREEN_MEDIUM = "#18C37E"
GREEN_LIGHT = "#7EE2B8"

RED_DARK = "#CC2B2B"
RED_MEDIUM = "#FF5A5F"
RED_LIGHT = "#FF9999"

PLOTLY_CHART_CONFIG = {
    "displayModeBar": True,
    "displaylogo": False,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
    "toImageButtonOptions": {
        "format": "png",
        "filename": "parking_spot_chart",
        "height": 700,
        "width": 1200,
        "scale": 2,
    },
}

SPOT_ORDER = [
    "LongSpotLeft",
    "PerpSpotLeft",
    "DiagSpotLeft",
    "LongSpotRight",
    "PerpSpotRight",
    "DiagSpotRight",
]

SPOT_LABELS = {
    "LongSpotLeft": "LongSpot (Left)",
    "PerpSpotLeft": "Perpendicular (Left)",
    "DiagSpotLeft": "Diagonal (Left)",
    "LongSpotRight": "LongSpot (Right)",
    "PerpSpotRight": "Perpendicular (Right)",
    "DiagSpotRight": "Diagonal (Right)",
}


def apply_theme():
    st.markdown(
        f"""
        <style>
        :root {{
            --bg: {BG};
            --panel: {PANEL};
            --border: {BORDER};
            --text: {TEXT};
            --muted: {MUTED};
            --accent: {ACCENT};
            --accent2: {ACCENT_2};
            --good: {GOOD};
            --warn: {WARN};
            --bad: {BAD};
        }}

        .stApp {{
            background:
                radial-gradient(circle at 15% 15%, rgba(59,130,246,0.16), transparent 24%),
                radial-gradient(circle at 85% 10%, rgba(96,165,250,0.10), transparent 20%),
                linear-gradient(180deg, #030712 0%, #06101D 45%, #050B16 100%);
            color: var(--text);
        }}

        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, rgba(8,14,26,0.98) 0%, rgba(9,16,30,0.98) 100%);
            border-right: 1px solid var(--border);
        }}

        section[data-testid="stSidebar"] * {{
            color: var(--text);
        }}

        .block-container {{
            max-width: 1450px;
            padding-top: 2rem;
            padding-bottom: 2.5rem;
        }}

        .hero-wrap {{
            position: relative;
            overflow: hidden;
            background: linear-gradient(135deg, rgba(15,23,42,0.96) 0%, rgba(8,14,26,0.96) 100%);
            border: 1px solid rgba(110,160,255,0.14);
            border-radius: 28px;
            padding: 34px 34px 28px 34px;
            margin-bottom: 1.4rem;
            box-shadow: 0 12px 40px rgba(0,0,0,0.34);
        }}

        .hero-wrap::before {{
            content: "";
            position: absolute;
            width: 420px;
            height: 420px;
            right: -100px;
            top: -120px;
            background: radial-gradient(circle, rgba(59,130,246,0.28) 0%, transparent 65%);
            pointer-events: none;
        }}

        .hero-badge {{
            display: inline-block;
            padding: 8px 14px;
            border-radius: 999px;
            background: rgba(59,130,246,0.14);
            border: 1px solid rgba(96,165,250,0.28);
            color: #B9D6FF;
            font-size: 0.78rem;
            font-weight: 700;
            margin-bottom: 16px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }}

        .hero-title {{
            font-size: 3rem;
            line-height: 1.04;
            font-weight: 850;
            letter-spacing: -0.04em;
            color: var(--text);
            max-width: 820px;
            margin-bottom: 0.65rem;
        }}

        .hero-subtitle {{
            color: var(--muted);
            font-size: 1.05rem;
            line-height: 1.7;
            max-width: 860px;
            margin-bottom: 1.1rem;
        }}

        .hero-actions {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}

        .hero-pill {{
            padding: 10px 14px;
            border-radius: 999px;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.06);
            color: var(--text);
            font-size: 0.9rem;
            font-weight: 600;
        }}

        .section-title {{
            font-size: 1.5rem;
            font-weight: 800;
            color: var(--text);
            margin-top: 1.4rem;
            margin-bottom: 0.9rem;
        }}

        .kpi-card {{
            background: linear-gradient(180deg, rgba(12,20,36,0.95) 0%, rgba(8,14,26,0.96) 100%);
            border: 1px solid rgba(110,160,255,0.14);
            border-radius: 22px;
            padding: 22px;
            min-height: 172px;
            box-shadow: 0 10px 28px rgba(0,0,0,0.24);
        }}

        .kpi-label {{
            color: var(--muted);
            font-size: 0.76rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 700;
            margin-bottom: 0.9rem;
        }}

        .kpi-value-number {{
            font-size: 2.2rem;
            font-weight: 850;
            line-height: 1.1;
            color: var(--text);
        }}

        .kpi-value-text {{
            font-size: 1.12rem;
            font-weight: 800;
            line-height: 1.45;
            color: var(--text);
        }}

        .kpi-note {{
            margin-top: 0.65rem;
            color: #A9C4F8;
            font-size: 0.93rem;
            line-height: 1.5;
        }}

        .info-card {{
            background: linear-gradient(180deg, rgba(11,19,34,0.92) 0%, rgba(7,13,24,0.95) 100%);
            border: 1px solid rgba(110,160,255,0.14);
            border-radius: 18px;
            padding: 18px;
            min-height: 122px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.20);
        }}

        .good-card {{
            border-left: 4px solid var(--good);
        }}

        .warn-card {{
            border-left: 4px solid var(--warn);
        }}

        .bad-card {{
            border-left: 4px solid var(--bad);
        }}

        .guide-banner {{
            background: linear-gradient(90deg, rgba(0,163,255,0.16) 0%, rgba(57,184,255,0.08) 100%);
            border: 1px solid rgba(0,163,255,0.35);
            border-radius: 16px;
            padding: 14px 18px;
            margin: 0.4rem 0 1rem 0;
            color: var(--text);
        }}

        .guide-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 14px;
            margin-bottom: 1rem;
        }}

        .guide-card {{
            background: rgba(11,19,34,0.78);
            border: 1px solid rgba(110,160,255,0.14);
            border-radius: 14px;
            padding: 14px 16px;
            min-height: 88px;
        }}

        .guide-step {{
            color: var(--accent2);
            font-size: 0.82rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 0.35rem;
        }}

        .guide-title {{
            color: var(--text);
            font-size: 1rem;
            font-weight: 800;
            margin-bottom: 0.25rem;
        }}

        .guide-text {{
            color: var(--muted);
            font-size: 0.9rem;
            line-height: 1.4;
        }}

        .arrow-callout {{
            background: rgba(255,176,32,0.10);
            border: 1px dashed rgba(255,176,32,0.45);
            border-radius: 14px;
            padding: 12px 14px;
            margin: 0.4rem 0 1rem 0;
            color: var(--text);
            font-size: 0.95rem;
        }}

        .warning-callout {{
            background: rgba(255,90,95,0.10);
            border: 1px dashed rgba(255,90,95,0.50);
            border-radius: 14px;
            padding: 12px 14px;
            margin: 0.4rem 0 1rem 0;
            color: var(--text);
            font-size: 0.95rem;
        }}

        .small-muted {{
            color: var(--muted);
            font-size: 0.94rem;
            margin-top: 0.35rem;
            line-height: 1.5;
        }}

        .upload-shell {{
            display: grid;
            grid-template-columns: 1.2fr 1fr;
            gap: 24px;
            align-items: center;
            background: linear-gradient(180deg, rgba(12,20,36,0.95) 0%, rgba(8,14,26,0.96) 100%);
            border: 1px solid rgba(110,160,255,0.14);
            border-radius: 24px;
            padding: 26px 28px;
            margin-bottom: 1.2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.22);
        }}

        .upload-badge {{
            display: inline-block;
            padding: 8px 14px;
            border-radius: 999px;
            background: rgba(59,130,246,0.12);
            border: 1px solid rgba(96,165,250,0.25);
            color: var(--accent2);
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 12px;
        }}

        .upload-title {{
            font-size: 1.6rem;
            font-weight: 800;
            color: var(--text);
            margin-bottom: 0.4rem;
        }}

        .upload-text {{
            color: var(--muted);
            font-size: 1rem;
            line-height: 1.6;
            max-width: 620px;
        }}

        .upload-right {{
            background: rgba(255,255,255,0.02);
            border: 1px dashed rgba(255,255,255,0.08);
            border-radius: 18px;
            padding: 18px;
        }}

        .sheet-shell {{
            margin-top: 0.3rem;
            margin-bottom: 0.6rem;
        }}

        .sheet-title {{
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--text);
            margin-bottom: 0.2rem;
        }}

        .sheet-text {{
            color: var(--muted);
            font-size: 0.93rem;
            margin-bottom: 0.5rem;
        }}

        .empty-state {{
            background: linear-gradient(180deg, rgba(11,19,34,0.92) 0%, rgba(7,13,24,0.95) 100%);
            border: 1px solid rgba(110,160,255,0.14);
            border-radius: 22px;
            padding: 34px 28px;
            text-align: center;
            margin-top: 1rem;
            box-shadow: 0 10px 26px rgba(0,0,0,0.20);
        }}

        .empty-title {{
            color: var(--text);
            font-size: 1.45rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
        }}

        .empty-text {{
            color: var(--muted);
            font-size: 1rem;
            line-height: 1.6;
        }}

        .dataset-status {{
            background: rgba(24,195,126,0.10);
            border: 1px solid rgba(24,195,126,0.28);
            border-radius: 16px;
            padding: 12px 16px;
            color: var(--text);
            margin: 0.8rem 0 1rem 0;
        }}

        .stSelectbox > div > div,
        .stMultiSelect > div > div,
        .stTextInput > div > div {{
            background-color: var(--panel) !important;
            border: 1px solid rgba(110,160,255,0.14) !important;
            border-radius: 12px !important;
            color: var(--text) !important;
        }}

        [data-testid="stExpander"] {{
            border: 1px solid rgba(110,160,255,0.14);
            border-radius: 14px;
            background: rgba(11,19,34,0.65);
        }}

        div[role="radiogroup"] {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-bottom: 0.7rem;
        }}

        div[role="radiogroup"] label {{
            background: rgba(10,18,32,0.88);
            border: 1px solid rgba(110,160,255,0.14);
            border-radius: 999px;
            padding: 8px 16px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header():
    st.markdown(
        """
        <div class="hero-wrap">
            <div class="hero-badge">AI Parking Analytics</div>
            <div class="hero-title">Parking Spot Evaluation Dashboard</div>
            <div class="hero-subtitle">
                Internal analytics for parking spot detection performance,
                scenario-based failures, and reliability insights.
            </div>
            <div class="hero-actions">
                <span class="hero-pill">Detection Quality</span>
                <span class="hero-pill">Scenario Analysis</span>
                <span class="hero-pill">Spot-Type Insights</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_feature_row():
    st.markdown(
        """
        <div class="section-title">Analysis Modules</div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:18px;">
            <div class="info-card">
                <strong>Detection Performance</strong><br><br>
                Spot-wise detection and miss-rate comparison.
            </div>
            <div class="info-card">
                <strong>Failure Hotspots</strong><br><br>
                Identify the worst-performing spot types and conditions.
            </div>
            <div class="info-card">
                <strong>Scenario Breakdown</strong><br><br>
                Filter by driver, environment, and vehicle signals.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
def render_header():
    render_logo()
    st.markdown(
        """
        <div class="hero-wrap">
            <div class="hero-badge">AI Parking Analytics</div>
            <div class="hero-title">Parking Spot Evaluation Dashboard</div>
            <div class="hero-subtitle">
                Internal analytics for parking spot detection performance,
                scenario-based failures, and reliability insights.
            </div>
            <div class="hero-actions">
                <span class="hero-pill">Detection Quality</span>
                <span class="hero-pill">Scenario Analysis</span>
                <span class="hero-pill">Spot-Type Insights</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
def render_insights_page(df: pd.DataFrame):
    st.markdown('<div class="section-title">Insights</div>', unsafe_allow_html=True)
    st.write("Add summary insights, top 5 worst conditions, and scenario breakdown here.")

def render_settings_page():
    st.markdown('<div class="section-title">Settings</div>', unsafe_allow_html=True)
    st.write("Add theme controls, export settings, chart preferences, or metric explanation here.")
    
def render_logo():
    with open("assets/cariad-logo-twilight.svg", "r", encoding="utf-8") as f:
        svg = f.read()

    st.markdown(
        f"""
        <div style="display:flex; align-items:center; width:200px; margin-top:30px;margin-bottom:10px;">
            {svg}
        
        """,
        unsafe_allow_html=True,
    )

def add_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.markdown("## Filters")

    filtered_df = df.copy()
    filtered_df.columns = [str(col).strip() for col in filtered_df.columns]

    driver_vehicle_filters = [
        "Driver.Name",
        "Driver.SearchVelocity",
        "Driver.SearchdistRight",
        "Driver.SearchdistLeft",
        "VUT.Brand",
        "VUT.Platform",
        "VUT.Derivat",
        "VUT.Aunumber",
        "VUT.SW",
        "VUT.Network",
    ]

    environment_filters = [
        "Env.Weather",
        "Env.Lighting",
        "Env.Roof",
        "Env.RoadSurface",
        "Env.Groundmarking",
        "Env.Contrast",
        "Env.Temperatur",
        "Env.Location",
    ]

    st.sidebar.markdown("### Driver & Vehicle")
    for col in driver_vehicle_filters:
        if col in filtered_df.columns:
            options = sorted(filtered_df[col].dropna().astype(str).unique().tolist())
            selected = st.sidebar.multiselect(col, options, key=f"filter_{col}")
            if selected:
                filtered_df = filtered_df[filtered_df[col].astype(str).isin(selected)]

    st.sidebar.markdown("### Environment")
    for col in environment_filters:
        if col in filtered_df.columns:
            options = sorted(filtered_df[col].dropna().astype(str).unique().tolist())
            selected = st.sidebar.multiselect(col, options, key=f"filter_{col}")
            if selected:
                filtered_df = filtered_df[filtered_df[col].astype(str).isin(selected)]

    return filtered_df


def prepare_summary(summary_df: pd.DataFrame) -> pd.DataFrame:
    if summary_df.empty:
        return summary_df

    df = summary_df.copy()
    df["SpotType"] = pd.Categorical(df["SpotType"], categories=SPOT_ORDER, ordered=True)
    df = df.sort_values("SpotType").reset_index(drop=True)
    df["SpotLabel"] = df["SpotType"].map(SPOT_LABELS)
    return df


def get_valid_summary(summary_df: pd.DataFrame, min_env: int = 10) -> pd.DataFrame:
    if summary_df.empty:
        return summary_df.copy()
    return summary_df[(summary_df["TotalEnv"] >= min_env)].copy()


def render_guidance():
    st.markdown(
        """
        <div class="guide-banner">
            <strong>👀 Where to look first:</strong> 1) Use the <strong>left filters</strong> to narrow the scenario, 2) read the <strong>Overview cards</strong> for the main result, 3) open <strong>Visual Analytics</strong> to compare detected versus missed performance by spot type.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="guide-grid">
            <div class="guide-card">
                <div class="guide-step">⬅ Step 1</div>
                <div class="guide-title">Start with Filters</div>
                <div class="guide-text">Choose driver, vehicle, weather, lighting, or road condition from the sidebar.</div>
            </div>
            <div class="guide-card">
                <div class="guide-step">⬇ Step 2</div>
                <div class="guide-title">Read Overview</div>
                <div class="guide-text">Check total spots, correctly detected spots, recall, miss rate, and best/worst spot types.</div>
            </div>
            <div class="guide-card">
                <div class="guide-step">➡ Step 3</div>
                <div class="guide-title">Open Visual Analytics</div>
                <div class="guide-text">Use the charts to understand both proportional performance and actual detected versus missed counts.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="arrow-callout">
            <strong>Tip:</strong> In the percentage chart, <strong>more dark blue means better detection</strong> and <strong>more light blue means more missed spots</strong>.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_low_data_warning(summary_df: pd.DataFrame):
    total_env = summary_df["TotalEnv"].sum()

    zero_data_spots = summary_df[summary_df["TotalEnv"] == 0]["SpotLabel"].tolist()
    low_data_spots = summary_df[(summary_df["TotalEnv"] > 0) & (summary_df["TotalEnv"] < 10)]["SpotLabel"].tolist()

    messages = []

    if total_env < 100:
        messages.append(f"Filtered dataset is small (n={int(total_env)}), so results may be less stable.")

    if zero_data_spots:
        messages.append("No ground-truth data for: " + ", ".join(zero_data_spots) + ".")

    if low_data_spots:
        messages.append("Very low sample size for: " + ", ".join(low_data_spots) + " (n < 10).")

    if messages:
        warning_text = "⚠ Low data warning: " + " ".join(messages)
        st.markdown(
            f"""
            <div class="warning-callout">
                <strong>{warning_text}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )

def render_kpis(summary_df: pd.DataFrame):
    total_env = summary_df["TotalEnv"].sum()
    total_ai = summary_df["TotalAI"].sum()
    total_missed = summary_df["TotalMissed"].sum()
    total_correct = summary_df["Correct Count"].sum()

    overall_miss = round((total_missed / total_env) * 100, 1) if total_env > 0 else 0
    overall_correct = round((total_correct / total_env) * 100, 1) if total_env > 0 else 0
    recall = round((total_correct / total_env) * 100, 1) if total_env > 0 else 0

    valid_spots = get_valid_summary(summary_df)

    if valid_spots.empty:
        worst_spot = None
        best_spot = None
        single_valid_spot = False
    elif len(valid_spots) == 1:
        worst_spot = valid_spots.iloc[0]
        best_spot = None
        single_valid_spot = True
    else:
        worst_spot = valid_spots.sort_values("Miss%", ascending=False).iloc[0]
        best_spot = valid_spots.sort_values("Miss%", ascending=True).iloc[0]
        single_valid_spot = False

    miss_color = BAD if overall_miss > 60 else WARN if overall_miss > 30 else GOOD
    detect_color = GOOD if recall > 60 else WARN if recall > 30 else BAD

    st.markdown('<div class="section-title">Overview</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 4px solid {BLUE_MEDIUM};">
                <div class="kpi-label">Total Ground Truth Spots</div>
                <div class="kpi-value-number">{int(total_env)}</div>
                <div class="kpi-note">Filtered scenario volume</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 4px solid {GREEN_MEDIUM};">
                <div class="kpi-label">Correctly Detected Spots</div>
                <div class="kpi-value-number">{int(total_correct)}</div>
                <div class="kpi-note">out of {int(total_env)} ground-truth spots</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 4px solid {detect_color};">
                <div class="kpi-label">Recall</div>
                <div class="kpi-value-number">{recall}%</div>
                <div class="kpi-note">Actual spots correctly detected</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 4px solid {miss_color};">
                <div class="kpi-label">Overall Miss Rate</div>
                <div class="kpi-value-number">{overall_miss}%</div>
                <div class="kpi-note">Spots missed by AI</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col5:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 4px solid {RED_MEDIUM};">
                <div class="kpi-label">Worst Spot Type</div>
                <div class="kpi-value-text">{worst_spot["SpotLabel"] if worst_spot is not None else "Not enough data"}</div>
                <div class="kpi-note">{str(worst_spot["Miss%"]) + "% miss rate • n=" + str(int(worst_spot["TotalEnv"])) if worst_spot is not None else "Reliable sample size not available"}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col6:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 4px solid {GREEN_MEDIUM};">
                <div class="kpi-label">Best Spot Type</div>
                <div class="kpi-value-text">{best_spot["SpotLabel"] if best_spot is not None else "Not enough data"}</div>
                <div class="kpi-note">{str(best_spot["Miss%"]) + "% miss rate • n=" + str(int(best_spot["TotalEnv"])) if best_spot is not None else "Reliable sample size not available"}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    st.markdown(
        f"""
        <div class="small-muted">
        👉 Out of <b>{int(total_env)}</b> actual parking spots, AI coorectly detected <b>{int(total_correct)}</b> spots,
        and it missed <b>{int(total_missed)}</b> spots.
        </div>
        """,
        unsafe_allow_html=True,
    )

    return overall_miss, overall_correct, recall, worst_spot, best_spot

def render_non_ai_kpis(summary_df: pd.DataFrame):
    total_env = summary_df["TotalEnv"].sum()
    total_detected = summary_df["Correct Count"].sum()
    total_missed = summary_df["TotalMissed"].sum()

    recall = round((total_detected / total_env) * 100, 1) if total_env > 0 else 0
    miss_rate = round((total_missed / total_env) * 100, 1) if total_env > 0 else 0

    valid_spots = get_valid_summary(summary_df)

    if valid_spots.empty:
        worst_spot = None
        best_spot = None
    elif len(valid_spots) == 1:
        worst_spot = valid_spots.iloc[0]
        best_spot = valid_spots.iloc[0]
    else:
        worst_spot = valid_spots.sort_values("Miss%", ascending=False).iloc[0]
        best_spot = valid_spots.sort_values("Miss%", ascending=True).iloc[0]

    st.markdown('<div class="section-title">Overview</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 4px solid {BLUE_MEDIUM};">
                <div class="kpi-label">Total Ground Truth Spots</div>
                <div class="kpi-value-number">{int(total_env)}</div>
                <div class="kpi-note">Baseline parking reference volume</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 4px solid {GREEN_MEDIUM};">
                <div class="kpi-label">Correctly Detected by Non-AI</div>
                <div class="kpi-value-number">{int(total_detected)}</div>
                <div class="kpi-note">out of {int(total_env)} ground-truth spots</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 4px solid {GREEN_MEDIUM};">
                <div class="kpi-label">Non-AI Recall</div>
                <div class="kpi-value-number">{recall}%</div>
                <div class="kpi-note">Actual spots correctly detected by baseline function</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 4px solid {RED_MEDIUM};">
                <div class="kpi-label">Non-AI Miss Rate</div>
                <div class="kpi-value-number">{miss_rate}%</div>
                <div class="kpi-note">Spots missed by baseline function</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col5:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 4px solid {WARN};">
                <div class="kpi-label">Weakest Spot Type</div>
                <div class="kpi-value-text">{worst_spot['SpotLabel'] if worst_spot is not None else 'Not enough data'}</div>
                <div class="kpi-note">{str(worst_spot['Miss%']) + '% miss rate • n=' + str(int(worst_spot['TotalEnv'])) if worst_spot is not None else 'Reliable sample size not available'}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col6:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 4px solid {GOOD};">
                <div class="kpi-label">Best Spot Type</div>
                <div class="kpi-value-text">{best_spot['SpotLabel'] if best_spot is not None else 'Not enough data'}</div>
                <div class="kpi-note">{str(best_spot['Miss%']) + '% miss rate • n=' + str(int(best_spot['TotalEnv'])) if best_spot is not None else 'Reliable sample size not available'}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div class="small-muted">
        👉 Out of <b>{int(total_env)}</b> actual parking spots, the <b>non-AI baseline</b> correctly detected <b>{int(total_detected)}</b> spots and missed <b>{int(total_missed)}</b> spots.
        </div>
        """,
        unsafe_allow_html=True,
    )

    return miss_rate, recall, worst_spot, best_spot

def is_only_r366(filtered_df: pd.DataFrame) -> bool:
    if "VUT.SW" not in filtered_df.columns:
        return False

    sw_values = (
        filtered_df["VUT.SW"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    return len(sw_values) > 0 and all(sw == "R36.6" for sw in sw_values)

def render_insights(overall_miss, overall_correct, worst_spot, best_spot):
    st.markdown('<div class="section-title">Key Insights</div>', unsafe_allow_html=True)

    box_class = "bad-card" if overall_miss >= 60 else "warn-card" if overall_miss >= 30 else "good-card"

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            f"""
            <div class="info-card {box_class}">
                <strong>Overall detection quality</strong><br><br>
                Miss rate is <strong>{overall_miss}%</strong> and correct detection rate is <strong>{overall_correct}%</strong>.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        failure_text = (
            f'<strong>{worst_spot["SpotLabel"]}</strong> is the weakest case with <strong>{worst_spot["Miss%"]}%</strong> missed detections.'
            if worst_spot is not None
            else "Not enough reliable data to identify the weakest spot type."
        )
        st.markdown(
            f"""
            <div class="info-card bad-card">
                <strong>Main failure area</strong><br><br>
                {failure_text}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        best_text = (
            f'<strong>{best_spot["SpotLabel"]}</strong> performs best with <strong>{best_spot["Correct Spot Ratio"]}%</strong> correct detection.'
            if best_spot is not None and "Correct Spot Ratio" in best_spot
            else f'<strong>{best_spot["SpotLabel"]}</strong> shows the lowest miss rate in the current filtered scenario.'
            if best_spot is not None
            else "Not enough reliable data to identify the best spot type."
        )
        st.markdown(
            f"""
            <div class="info-card good-card">
                <strong>Best observed case</strong><br><br>
                {best_text}
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_raw_data_section(filtered_df: pd.DataFrame):
    st.markdown('<div class="section-title">Raw Data Explorer</div>', unsafe_allow_html=True)
    st.caption(f"Filtered rows: {len(filtered_df)}")

    csv_data = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered raw data",
        data=csv_data,
        file_name="filtered_raw_data.csv",
        mime="text/csv",
    )

    st.dataframe(filtered_df, use_container_width=True, height=320)


def render_chart_insight(summary_df: pd.DataFrame):
    if summary_df.empty:
        return

    best_spot = summary_df.sort_values("Miss%", ascending=True).iloc[0]
    worst_spot = summary_df.sort_values("Miss%", ascending=False).iloc[0]

    st.markdown(
        f"""
        <div class="guide-banner">
            <strong>Insight:</strong>
            AI performs best on <strong>{best_spot["SpotLabel"]}</strong> with
            <strong>{best_spot["Correct Spot Ratio"]}%</strong> correct detection
            (n={int(best_spot["TotalEnv"])}),
            while <strong>{worst_spot["SpotLabel"]}</strong> shows the weakest performance with
            <strong>{worst_spot["Miss%"]}%</strong> miss rate
            (n={int(worst_spot["TotalEnv"])}).
        </div>
        """,
        unsafe_allow_html=True,
    )

def wilson_ci(successes: int, n: int, z: float = 1.96):
    """
    Wilson score interval for a binomial proportion.
    Returns lower and upper bounds in percentage.
    """
    if n == 0:
        return 0.0, 0.0

    p = successes / n
    denominator = 1 + (z**2 / n)
    center = (p + (z**2 / (2 * n))) / denominator
    margin = (
        z
        * math.sqrt((p * (1 - p) / n) + (z**2 / (4 * n**2)))
        / denominator
    )

    lower = max(0.0, center - margin) * 100
    upper = min(1.0, center + margin) * 100
    return round(lower, 1), round(upper, 1)

def render_best_chart(summary_df: pd.DataFrame):
    if summary_df.empty:
        st.info("Not enough reliable data to show chart.")
        return

    df = summary_df.copy()
    df["Detected %"] = ((df["Correct Count"] / df["TotalEnv"]) * 100).fillna(0).round(1)
    df["Missed %"] = ((df["TotalMissed"] / df["TotalEnv"]) * 100).fillna(0).round(1)
    df["Label_with_n"] = df["SpotLabel"].astype(str) + "<br>n=" + df["TotalEnv"].astype(int).astype(str)
    
      # Confidence interval for detection %
    ci_bounds = df.apply(
        lambda row: wilson_ci(int(row["Correct Count"]), int(row["TotalEnv"])),
        axis=1
    )
    df["Detect CI Low"] = [x[0] for x in ci_bounds]
    df["Detect CI High"] = [x[1] for x in ci_bounds]

    chart_df = df.melt(
        id_vars=["SpotLabel", "Label_with_n", "TotalEnv", "Detect CI Low", "Detect CI High"],
        value_vars=["Detected %", "Missed %"],
        var_name="Metric",
        value_name="Value",
    )

    color_map = {
        "Detected %": BLUE_MEDIUM,
        "Missed %": BLUE_LIGHT,
    }

    fig = px.bar(
        chart_df,
        x="Label_with_n",
        y="Value",
        color="Metric",
        barmode="stack",
        text=chart_df["Value"].round(0).astype(int).astype(str) + "%",
        title="How Well AI Detects Parking Spots (by Type)",
        color_discrete_map=color_map,
         custom_data=["TotalEnv", "Detect CI Low", "Detect CI High"],
    )
    

    fig.update_traces(
    textposition="inside",
    textfont=dict(
        color="#000000",  
        size=16
    ),
    hovertemplate=(
        "<b>%{x}</b><br>"
        "%{legendgroup}: %{y:.1f}%<br>"
        "n=%{customdata[0]}<br>"
        "95% CI for detection: %{customdata[1]:.1f}% to %{customdata[2]:.1f}%"
        "<extra></extra>"
    )
)

    fig.update_layout(
    height=520,
    paper_bgcolor="#050B16",
    plot_bgcolor="#07101D",
    font_color="#F5F7FA",
    title_font_color="#F5F7FA",
    title_font_size=22,
    xaxis=dict(
        title="Spot Type",
        showgrid=False,
        zeroline=False,
        color="#C7D2E3"
    ),
    yaxis=dict(
        title="Percentage (%)",
        gridcolor="rgba(255,255,255,0.08)",
        zeroline=False,
        color="#C7D2E3"
    ),
    legend_title="",
    margin=dict(l=20, r=20, t=70, b=20),
)
    

    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CHART_CONFIG)


def render_count_chart(summary_df: pd.DataFrame):
    if summary_df.empty:
        st.info("Not enough data to show count chart.")
        return

    df = summary_df.copy()
    df["SpotLabelWithN"] = (
        df["SpotLabel"].astype(str) + " (n=" + df["TotalEnv"].astype(int).astype(str) + ")"
    )

    chart_df = df.melt(
        id_vars=["SpotLabelWithN"],
        value_vars=["Correct Count", "TotalMissed"],
        var_name="Metric",
        value_name="Value",
    )

    color_map = {
        "Correct Count": BLUE_MEDIUM,
        "TotalMissed": BLUE_LIGHT,
    }

    fig = px.bar(
        chart_df,
        y="SpotLabelWithN",
        x="Value",
        color="Metric",
        barmode="group",
        orientation="h",
        text="Value",
        title="Detected vs Missed Spots by Spot Type",
        color_discrete_map=color_map,
    )

    fig.update_traces(textposition="outside")

    fig.update_layout(
        height=520,
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font_color=TEXT,
        title_font_color=TEXT,
        xaxis_title="Number of Spots",
        yaxis_title="Spot Type",
        legend_title="",
        margin=dict(l=20, r=20, t=60, b=20),
    )

    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CHART_CONFIG)


def render_summary_table(summary_df: pd.DataFrame):
    st.markdown('<div class="section-title">Detailed Tables</div>', unsafe_allow_html=True)

    required_cols = [
        "SpotLabel",
        "TotalEnv",
        "Correct Count",
        "TotalMissed",
        "Miss%",
        "Correct Spot Ratio",
        "False%",
        "Coverage %",
        "Quality Score",
    ]
    available_cols = [col for col in required_cols if col in summary_df.columns]

    table_df = summary_df[available_cols].copy()
    if "Miss%" in table_df.columns:
        table_df = table_df.sort_values("Miss%", ascending=False)

    csv_data = table_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download summary table",
        data=csv_data,
        file_name="summary_table.csv",
        mime="text/csv",
    )

    st.dataframe(table_df, use_container_width=True, hide_index=True, height=320)

def build_condition_summary_table(filtered_df: pd.DataFrame, condition_col: str) -> pd.DataFrame:
    if filtered_df.empty or condition_col not in filtered_df.columns:
        return pd.DataFrame()

    spot_columns = [
        "Env.LongSpotLeft",
        "Env.PerpSpotLeft",
        "Env.DiagSpotLeft",
        "Env.LongSpotRight",
        "Env.PerpSpotRight",
        "Env.DiagSpotRight",
    ]

    available_spot_columns = [col for col in spot_columns if col in filtered_df.columns]
    if not available_spot_columns:
        return pd.DataFrame()

    temp_df = filtered_df.copy()

    temp_df = temp_df[
    temp_df[condition_col].notna() & 
    (temp_df[condition_col].astype(str).str.strip() != "")
]


    temp_df[condition_col] = temp_df[condition_col].astype(str).str.strip()
    for col in available_spot_columns:
        temp_df[col] = pd.to_numeric(temp_df[col], errors="coerce").fillna(0)

    summary_table = (
        temp_df.groupby(condition_col, dropna=False)[available_spot_columns]
        .sum()
        .reset_index()
    )

    total_row = pd.DataFrame([{
        condition_col: "Total",
        **{col: summary_table[col].sum() for col in available_spot_columns}
    }])

    summary_table = pd.concat([summary_table, total_row], ignore_index=True)

    for col in available_spot_columns:
        summary_table[col] = summary_table[col].round(0)

    return summary_table

def render_all_condition_summaries(filtered_df: pd.DataFrame):
    st.markdown('<div class="section-title">Column-wise Summary Tables</div>', unsafe_allow_html=True)

    condition_columns = [
        "Driver.Name",
        "Driver.SearchVelocity",
        "Driver.SearchdistRight",
        "Driver.SearchdistLeft",
        "VUT.Brand",
        "VUT.Platform",
        "VUT.Derivat",
        "VUT.Aunumber",
        "VUT.SW",
        "VUT.Network",
        "Env.Weather",
        "Env.Lighting",
        "Env.Roof",
        "Env.RoadSurface",
        "Env.Groundmarking",
        "Env.Contrast",
        "Env.Location",
        "Env.Temperatur",
    ]

    available_conditions = [col for col in condition_columns if col in filtered_df.columns]

    if not available_conditions:
        st.info("None of the requested summary columns are available.")
        return

    selected_condition = st.selectbox(
        "Select column for summary table",
        available_conditions,
        key="all_condition_summary_select"
    )

    summary_table = build_condition_summary_table(filtered_df, selected_condition)

    if summary_table.empty:
        st.info(f"No summary data available for {selected_condition}.")
        return

    st.markdown(f"### {selected_condition} Summary", unsafe_allow_html=True)
    st.dataframe(summary_table, use_container_width=True, hide_index=True)

    csv_data = summary_table.to_csv(index=False).encode("utf-8")
    st.download_button(
        f"Download {selected_condition} summary",
        data=csv_data,
        file_name=f"{selected_condition.replace('.', '_')}_summary.csv",
        mime="text/csv",
        key=f"download_{selected_condition}_summary"
    )

def is_non_ai_mode(filtered_df: pd.DataFrame) -> bool:
    if "VUT.SW" not in filtered_df.columns:
        return False

    sw_values = (
        filtered_df["VUT.SW"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    return len(sw_values) > 0 and all(sw == "R36.6" for sw in sw_values)

def render_dashboard(df: pd.DataFrame):
    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]

    
    # Apply filters on FULL data
    filtered_df = add_sidebar_filters(df)

    if filtered_df.empty:
        st.warning("No data after applying filters.")
        return

    from summary_utils import build_summary_table
    from sw_trend_analysis import render_sw_trend_chart

    if is_non_ai_mode(filtered_df):
        filtered_summary = build_non_ai_summary_table(filtered_df)
    else:
        filtered_summary = build_summary_table(filtered_df)

    filtered_summary = prepare_summary(filtered_summary)

    if filtered_summary.empty:
        st.warning("No summary could be generated for the filtered data.")
        return

    valid_summary = get_valid_summary(filtered_summary, min_env=10)
    
    render_guidance()
    render_low_data_warning(filtered_summary)


    if is_only_r366(filtered_df):
        overall_miss, recall, worst_spot, best_spot = render_non_ai_kpis(filtered_summary)
    else:
        overall_miss, overall_correct, recall, worst_spot, best_spot = render_kpis(filtered_summary)
        render_insights(overall_miss, overall_correct, worst_spot, best_spot)


    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "Visual Analytics"

    tabs = ["Raw Data", "Visual Analytics", "SW Trend", "Details"]

    selected_tab = st.radio(
        "",
        tabs,
        horizontal=True,
        key="active_tab",
        label_visibility="collapsed",
    )

    if selected_tab == "Raw Data":
        render_all_condition_summaries(filtered_df)   
        render_raw_data_section(filtered_df)

    elif selected_tab == "Visual Analytics":
        st.markdown('<div class="section-title">Detection Performance</div>', unsafe_allow_html=True)
        render_chart_insight(valid_summary)
        render_best_chart(valid_summary)

        st.markdown('<div class="section-title">Detected vs Missed Counts</div>', unsafe_allow_html=True)
        render_count_chart(valid_summary)

    elif selected_tab == "SW Trend":
        render_sw_trend_chart(filtered_df)

    elif selected_tab == "Details":
        render_summary_table(filtered_summary)

        with st.expander("Show raw filtered data"):
            st.dataframe(filtered_df, use_container_width=True)

        with st.expander("Show full summary table"):
            st.dataframe(filtered_summary, use_container_width=True, hide_index=True)