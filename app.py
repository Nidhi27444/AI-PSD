import streamlit as st
import pandas as pd

from summary_utils import prepare_raw_data
from UI import apply_theme, render_header, render_dashboard

st.set_page_config(
    page_title="Parking Spot Evaluation Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()
render_header()

# 🔁 State control
if "page" not in st.session_state:
    st.session_state.page = "upload"


# =========================
# 📥 PAGE 1: UPLOAD SCREEN
# =========================
if st.session_state.page == "upload":

    st.markdown(
        """
        <div class="upload-shell">
            <div>
                <div class="upload-badge">DATA INPUT</div>
                <div class="upload-title">Load your evaluation dataset</div>
                <div class="upload-text">
                    Upload the Excel file containing the parking spot evaluation data,
                    then select the raw sheet to begin scenario-based analysis.
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])

    st.markdown("</div>", unsafe_allow_html=True)

    if uploaded_file is not None:
        excel_file = pd.ExcelFile(uploaded_file)
        sheet_names = excel_file.sheet_names

        selected_sheet = st.selectbox("Select sheet", sheet_names)

        if st.button("Load Dashboard"):
            df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
            df = prepare_raw_data(df)

            st.session_state.df = df
            st.session_state.page = "dashboard"
            st.rerun()


# =========================
# 📊 PAGE 2: DASHBOARD
# =========================
elif st.session_state.page == "dashboard":

    if "df" not in st.session_state:
        st.error("No data found.")
        st.session_state.page = "upload"
        st.rerun()

    # 🔙 Back button
    col1, col2 = st.columns([1, 10])
    with col1:
        if st.button("⬅ Back"):
            st.session_state.page = "upload"
            st.rerun()

    df = st.session_state.df

    render_dashboard(df)