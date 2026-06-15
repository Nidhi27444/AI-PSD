from constants import *
import pandas as pd
import streamlit as st
import plotly.express as px
from summary_utils import build_summary_table


EXCLUDED_SW_VERSIONS = {"R36.6"}


def exclude_sw_versions(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "VUT.SW" not in df.columns:
        return df.copy()

    return df[
        ~df["VUT.SW"].astype(str).str.strip().isin(EXCLUDED_SW_VERSIONS)
    ].copy()


def build_group_overview_table(filtered_df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    if filtered_df.empty or group_col not in filtered_df.columns:
        return pd.DataFrame()

    working_df = filtered_df.copy()

    if group_col == "VUT.SW":
        working_df = exclude_sw_versions(working_df)

    if working_df.empty:
        return pd.DataFrame()

    trend_rows = []

    group_values = (
        working_df[group_col]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    for group_value in group_values:
        temp_df = working_df[
            working_df[group_col].astype(str).str.strip() == group_value
        ].copy()

        if temp_df.empty:
            continue

        temp_summary = build_summary_table(temp_df)
        if temp_summary.empty:
            continue

        total_env = temp_summary["TotalEnv"].sum()
        total_ai = temp_summary["TotalAI"].sum()
        total_missed = temp_summary["TotalMissed"].sum()
        total_false = temp_summary["TotalFalse"].sum()
        total_correct = temp_summary["Correct Count"].sum()

        if total_env > 0:
            miss_pct = round((total_missed / total_env) * 100, 1)
            false_pct = round((total_false / total_env) * 100, 1)
            correct_ratio = round((total_correct / total_env) * 100, 1)
            overcount_pct = round((max(total_ai - total_env, 0) / total_env) * 100, 1)
            coverage_pct = round((min(total_ai, total_env) / total_env) * 100, 1)
            count_error_pct = round((abs(total_ai - total_env) / total_env) * 100, 1)
        else:
            miss_pct = 0
            false_pct = 0
            correct_ratio = 0
            overcount_pct = 0
            coverage_pct = 0
            count_error_pct = 0

        quality_score = round(correct_ratio - overcount_pct, 1)

        trend_rows.append(
            {
                group_col: str(group_value),
                "TotalEnv": int(total_env),
                "TotalAI": int(total_ai),
                "TotalMissed": int(total_missed),
                "TotalFalse": int(total_false),
                "Miss%": miss_pct,
                "False%": false_pct,
                "Correct Spot Ratio": correct_ratio,
                "Overcount %": overcount_pct,
                "Coverage %": coverage_pct,
                "Count Error %": count_error_pct,
                "Quality Score": quality_score,
                "Correct Count": int(total_correct),
            }
        )

    trend_df = pd.DataFrame(trend_rows)

    if trend_df.empty:
        return trend_df

    if group_col == "VUT.SW":
        sw_order_map = {
            "DD4.0": 1,
            "R38.2": 3,
        }
        trend_df["order"] = trend_df[group_col].map(sw_order_map).fillna(999)
        trend_df = trend_df.sort_values(["order", group_col]).drop(columns=["order"])
    else:
        trend_df = trend_df.sort_values(group_col)

    return trend_df.reset_index(drop=True)


def render_variable_chart(filtered_df: pd.DataFrame):
    st.markdown('<div class="section-title">Variable Chart</div>', unsafe_allow_html=True)

    compare_options = {
        "VUT.SW": "VUT.SW",
        "Env.Weather": "Env.Weather",
        "Env.Lighting": "Env.Lighting",
        "Env.RoadSurface": "Env.RoadSurface",
        "Env.Contrast": "Env.Contrast",
        "Env.Roof": "Env.Roof",
        "Env.Groundmarking": "Env.Groundmarking",
        "Env.Location": "Env.Location",
        "Env.Temperature": "Env.Temperature",
        "Driver.Name": "Driver.Name",
        "Driver.SearchVelocity": "Driver.SearchVelocity",
        "Driver.SearchdistRight": "Driver.SearchdistRight",
        "Driver.SearchdistLeft": "Driver.SearchdistLeft",
        "VUT.Brand": "VUT.Brand",
        "VUT.Platform": "VUT.Platform",
        "VUT.Derivat": "VUT.Derivat",
        "VUT.Aunumber": "VUT.Aunumber",
        "VUT.Network": "VUT.Network",
    }

    c0, c1, c2 = st.columns(3)

    with c0:
        st.markdown("**Select Dimension**")
        compare_label = st.selectbox(
            "",
            list(compare_options.keys()),
            key="compare_dimension",
        )

    group_col = compare_options[compare_label]
    trend_df = build_group_overview_table(filtered_df, group_col)

    if trend_df.empty:
        st.info(f"No data available for {compare_label}.")
        return

    numeric_columns = [
        col for col in trend_df.columns
        if col != group_col and pd.api.types.is_numeric_dtype(trend_df[col])
    ]

    with c1:
        st.markdown("**Select Y-axis**")
        y_axis = st.selectbox(
            "",
            numeric_columns,
            index=numeric_columns.index("Quality Score") if "Quality Score" in numeric_columns else 0,
            key="y_axis_select",
        )

    with c2:
        st.markdown("**Chart Type**")
        chart_type = st.selectbox(
            "",
            ["Line", "Bar"],
            key="chart_type_select",
        )

    title_text = f"{y_axis} over {group_col}"

    if chart_type == "Bar":
        fig = px.bar(
            trend_df,
            x=group_col,
            y=y_axis,
            text=y_axis,
            title=title_text,
            hover_data=["TotalEnv", "Correct Count", "TotalMissed", "TotalFalse"],
        )
        fig.update_traces(textposition="outside")
    else:
        fig = px.line(
            trend_df,
            x=group_col,
            y=y_axis,
            markers=True,
            text=y_axis,
            title=title_text,
            hover_data=["TotalEnv", "Correct Count", "TotalMissed", "TotalFalse"],
        )
        fig.update_traces(textposition="top center")

    fig.update_layout(
        height=500,
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font_color=TEXT,
        title_font_color=TEXT,
        xaxis_title=group_col,
        yaxis_title=y_axis,
        margin=dict(l=20, r=20, t=60, b=20),
    )

    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CHART_CONFIG)

    low_sample_groups = trend_df[trend_df["TotalEnv"] < 10][group_col].astype(str).tolist()
    if low_sample_groups:
        st.markdown(
            f"""
            <div class="warning-callout">
                ⚠ Low sample size for: {", ".join(low_sample_groups)}.
                Interpretation may be less reliable.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.dataframe(trend_df, use_container_width=True, hide_index=True)

    csv_data = trend_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download comparison table",
        data=csv_data,
        file_name="comparison_table.csv",
        mime="text/csv",
    )


def render_sw_trend_chart(filtered_df: pd.DataFrame):
    st.markdown('<div class="section-title">SW Version Trend</div>', unsafe_allow_html=True)

    if filtered_df.empty:
        st.info("No data available for SW trend.")
        return

    if "VUT.SW" not in filtered_df.columns:
        st.info("Column 'VUT.SW' not found.")
        return

    filtered_df = exclude_sw_versions(filtered_df)

    if filtered_df.empty:
        st.info("No SW trend data available after excluding unwanted versions.")
        return

    st.markdown(
        """
        <div class="guide-banner">
            <strong>How to read this:</strong>
            This section shows KPI trends over software version and also lets you compare weather, lighting, contrast, driver, and speed impact on AI performance.
        </div>
        """,
        unsafe_allow_html=True,
    )

    sw_df = build_group_overview_table(filtered_df, "VUT.SW")

    if sw_df.empty:
        st.info("No SW trend data available after filtering.")
        return

    low_sample_versions = sw_df[sw_df["TotalEnv"] < 10]["VUT.SW"].astype(str).tolist()
    if low_sample_versions:
        st.markdown(
            f"""
            <div class="warning-callout">
                ⚠ Low sample size for version(s): {", ".join(low_sample_versions)}.
                Trend interpretation may be less reliable.
            </div>
            """,
            unsafe_allow_html=True,
        )

    c1, c2 = st.columns(2)

    with c1:
        fig_recall = px.line(
            sw_df,
            x="VUT.SW",
            y="Correct Spot Ratio",
            markers=True,
            text="Correct Spot Ratio",
            title="Correct Spot Ratio by Software Version",
        )
        fig_recall.update_traces(textposition="top center")
        fig_recall.update_layout(
            height=420,
            paper_bgcolor=BG,
            plot_bgcolor=BG,
            font_color=TEXT,
            title_font_color=TEXT,
            xaxis_title="Software Version",
            yaxis_title="Correct Spot Ratio (%)",
            margin=dict(l=20, r=20, t=60, b=20),
        )
        st.plotly_chart(fig_recall, use_container_width=True, config=PLOTLY_CHART_CONFIG)

    with c2:
        fig_miss = px.line(
            sw_df,
            x="VUT.SW",
            y="Miss%",
            markers=True,
            text="Miss%",
            title="Miss Rate by Software Version",
        )
        fig_miss.update_traces(textposition="top center")
        fig_miss.update_layout(
            height=420,
            paper_bgcolor=BG,
            plot_bgcolor=BG,
            font_color=TEXT,
            title_font_color=TEXT,
            xaxis_title="Software Version",
            yaxis_title="Miss Rate (%)",
            margin=dict(l=20, r=20, t=60, b=20),
        )
        st.plotly_chart(fig_miss, use_container_width=True, config=PLOTLY_CHART_CONFIG)

    st.markdown('<div class="section-title">All Overview Values over VUT.SW</div>', unsafe_allow_html=True)
    st.dataframe(sw_df, use_container_width=True, hide_index=True)

    csv_data = sw_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download SW overview table",
        data=csv_data,
        file_name="sw_overview_table.csv",
        mime="text/csv",
    )

    render_variable_chart(filtered_df)