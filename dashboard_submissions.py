import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
import json
from google.oauth2.service_account import Credentials
from datetime import datetime

# ✅ Streamlit config
st.set_page_config(page_title="Submissions Dashboard", layout="wide")

# ──────────────────────────────
# 📋 PAGE HEADER
# ──────────────────────────────
st.markdown('<h1><i class="fas fa-chart-pie"></i> Submissions Dashboard <small style="font-size:16px;">(Last 8 Months)</small></h1>', unsafe_allow_html=True)

# ──────────────────────────────
# ☁️ Connect to Google Sheets
# ──────────────────────────────
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"])
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
client = gspread.authorize(creds)

# ──────────────────────────────
# 📚 Load monthly tabs from Google Sheets
# ──────────────────────────────
sheet_url = "https://docs.google.com/spreadsheets/d/1b0CTtJPUQT_4MCaSzuUja6gPJS-nwZeSsezZaz3Z1gk"
sheet = client.open_by_url(sheet_url)

tabs_to_load = [
    "September2024", "October2024", "November2024", "December2024",
    "January2025", "February2025", "March2025", "April2025"
]

dataframes = []
errors = []

for tab in tabs_to_load:
    try:
        worksheet = sheet.worksheet(tab)
        tab_data = worksheet.get_all_records()
        df_tab = pd.DataFrame(tab_data)
        if not df_tab.empty:
            df_tab["Date"] = pd.to_datetime(df_tab["Date"], errors="coerce")
            df_tab["Month"] = df_tab["Date"].dt.month_name()
            df_tab["Year"] = df_tab["Date"].dt.year
            df_tab["Source File"] = tab
            dataframes.append(df_tab)
    except Exception as e:
        errors.append(f"⚠️ Failed to load {tab}: {e}")

# Check if at least one tab loaded
if not dataframes:
    st.error("❌ No data could be loaded. Please check your Google Sheet setup.")
    st.stop()

# Merge all dataframes
df_all = pd.concat(dataframes, ignore_index=True)
df_all = df_all[df_all["Date"].notna()]  # Only rows with valid Date

# ──────────────────────────────
# 🎯 Sidebar Filters
# ──────────────────────────────
if "selected_year" not in st.session_state:
    st.session_state.selected_year = None
if "selected_month" not in st.session_state:
    st.session_state.selected_month = None
if "selected_date" not in st.session_state:
    st.session_state.selected_date = None

with st.sidebar.expander("📁 Filters", expanded=True):
    year = st.selectbox("📅 Year", sorted(df_all["Year"].unique(), reverse=True))
    month = st.selectbox("🗓 Month", sorted(df_all[df_all["Year"] == year]["Month"].unique()))
    employees = st.multiselect("👤 Employees", df_all["Name"].unique(), default=df_all["Name"].unique())
    selected_date = st.date_input("📆 Select a Date (optional)", value=st.session_state.selected_date)

    # Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Refresh App"):
            st.rerun()
    with col2:
        if st.button("🧹 Clear Filters"):
            st.session_state.selected_date = None
            st.experimental_rerun()

# Auto-clear "Select a Date" if year/month changes
if year != st.session_state.selected_year or month != st.session_state.selected_month:
    st.session_state.selected_date = None

# Update session states
st.session_state.selected_year = year
st.session_state.selected_month = month

# Filter data
filtered = df_all[
    (df_all["Year"] == year) &
    (df_all["Month"] == month) &
    (df_all["Name"].isin(employees))
]

# Apply specific date filter if chosen
if selected_date:
    filtered = filtered[filtered["Date"] == pd.to_datetime(selected_date)]

# ──────────────────────────────
# 🗂 Tabs Display
# ──────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "📄 Data Table",
    "📊 Charts",
    "🧩 Submission Share"
])

with tab1:
    st.markdown('<h3><i class="iconoir-report-columns"></i> Filtered Data Table</h3>', unsafe_allow_html=True)
    st.dataframe(filtered.sort_values(by="Date"))

with tab2:
    if not filtered.empty:
        st.markdown('<h3><i class="las la-chart-bar"></i> Daily Submissions Trend</h3>', unsafe_allow_html=True)
        pivot = filtered.pivot(index="Date", columns="Name", values="Total Submissions")
        fig_line = px.line(pivot, x=pivot.index, y=pivot.columns, title="Daily Submissions", template="plotly")
        st.plotly_chart(fig_line, use_container_width=True)

        st.markdown('<h3><i class="las la-user"></i> Total Submissions by Employee</h3>', unsafe_allow_html=True)
        totals = filtered.groupby("Name")["Total Submissions"].sum().reset_index()
        fig_bar = px.bar(totals, x="Name", y="Total Submissions", title="Total Submissions", color="Total Submissions", template="plotly")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("⚠️ No data available for the selected filters.")

with tab3:
    if not filtered.empty:
        totals = filtered.groupby("Name")["Total Submissions"].sum().reset_index()
        fig_pie = px.pie(totals, names="Name", values="Total Submissions", title="Submission Share", template="plotly")
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("⚠️ No data available for the selected filters.")

# ──────────────────────────────
# 📢 Footer
# ──────────────────────────────
st.markdown("<hr style='margin-top: 2em;'>", unsafe_allow_html=True)
st.markdown("<center><small><i class='fas fa-code'></i> Built with Streamlit | Last updated: {} UTC</small></center>".format(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)

# ──────────────────────────────
# ⚠️ Display warnings for missing months (if any)
# ──────────────────────────────
if errors:
    for error in errors:
        st.sidebar.warning(error)
