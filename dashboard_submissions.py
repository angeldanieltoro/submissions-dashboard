import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
import json
from google.oauth2.service_account import Credentials
from datetime import datetime
# dashboard_submissions.py

import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials
import json
from datetime import datetime

# ✅ THIS MUST BE THE FIRST Streamlit COMMAND
st.set_page_config(page_title="Submissions Dashboard", layout="wide")

# ──────────────────────────────
# 📋 PAGE HEADER
# ──────────────────────────────
st.markdown('<h1><i class="fas fa-chart-pie"></i> Submissions Dashboard <small style="font-size:16px;">(Live Data)</small></h1>', unsafe_allow_html=True)

# ──────────────────────────────
# ☁️ Load Data from Google Sheets
# ──────────────────────────────
sheet_id = "1b0CTtJPUQT_4MCaSzuUja6gPJS-nwZeSsezZaz3Z1gk"
sheet_name = "Submissions"

scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"])
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
client = gspread.authorize(creds)

try:
    sheet = client.open_by_key(sheet_id)
    worksheet = sheet.worksheet(sheet_name)
    sheet_data = worksheet.get_all_records()

    if not sheet_data:
        st.error("⚠️ No data found in the Submissions sheet.")
        st.stop()

    df_all = pd.DataFrame(sheet_data)
    df_all["Date"] = pd.to_datetime(df_all["Date"], errors="coerce")
    df_all["Month"] = df_all["Date"].dt.month_name()
    df_all["Year"] = df_all["Date"].dt.year

except Exception as e:
    st.error(f"🚨 Error loading data: {str(e)}")
    st.stop()

# ──────────────────────────────
# 🎯 Sidebar Filters
# ──────────────────────────────
st.sidebar.header("📁 Filters")

# Clear Filters Button
if st.sidebar.button("🔄 Clear Filters"):
    for key in ["selected_year", "selected_month", "selected_employee", "selected_date"]:
        if key in st.session_state:
            del st.session_state[key]
    st.experimental_rerun()

# Refresh App Button
if st.sidebar.button("♻️ Refresh App"):
    st.experimental_rerun()

# Initialize session states
if "selected_year" not in st.session_state:
    st.session_state.selected_year = None
if "selected_month" not in st.session_state:
    st.session_state.selected_month = None
if "selected_employee" not in st.session_state:
    st.session_state.selected_employee = None
if "selected_date" not in st.session_state:
    st.session_state.selected_date = None

# Filters
year = st.sidebar.selectbox("📅 Year", sorted(df_all["Year"].dropna().unique(), reverse=True), key="selected_year")
month = st.sidebar.selectbox("🗓 Month", sorted(df_all[df_all["Year"] == year]["Month"].dropna().unique()), key="selected_month")
employees = st.sidebar.multiselect(
    "👤 Employees",
    options=sorted(df_all["Name"].dropna().unique()),
    default=sorted(df_all["Name"].dropna().unique()),
    key="selected_employee"
)
selected_date = st.sidebar.date_input("📆 Select a Specific Date", key="selected_date")

# Apply filtering logic
filtered = df_all[
    (df_all["Year"] == year) &
    (df_all["Month"] == month) &
    (df_all["Name"].isin(employees))
]

# Date Filter if Selected
if selected_date:
    filtered = filtered[filtered["Date"] == pd.to_datetime(selected_date)]

# ──────────────────────────────
# 📊 Display Tabs
# ──────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "📄 Data Table",
    "📈 Charts",
    "🧩 Submission Share"
])

with tab1:
    st.markdown('<h3><i class="iconoir-report-columns"></i> Filtered Data Table</h3>', unsafe_allow_html=True)
    st.dataframe(filtered.sort_values(by="Date"))

with tab2:
    st.markdown('<h3><i class="las la-chart-bar"></i> Daily Submissions Trend</h3>', unsafe_allow_html=True)
    if not filtered.empty:
        pivot = filtered.pivot(index="Date", columns="Name", values="Total Submissions")
        fig_line = px.line(pivot, x=pivot.index, y=pivot.columns,
                           title="Daily Submissions", template="plotly")
        st.plotly_chart(fig_line, use_container_width=True)

        st.markdown('<h3><i class="las la-user"></i> Total Submissions by Employee</h3>', unsafe_allow_html=True)
        totals = filtered.groupby("Name")["Total Submissions"].sum().reset_index()
        fig_bar = px.bar(totals, x="Name", y="Total Submissions",
                         title="Total Submissions", color="Total Submissions", template="plotly")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("⚠️ No data available for the selected filters.")

with tab3:
    st.markdown('<h3><i class="fas fa-chart-pie"></i> Share of Submissions</h3>', unsafe_allow_html=True)
    if not filtered.empty:
        totals = filtered.groupby("Name")["Total Submissions"].sum().reset_index()
        fig_pie = px.pie(totals, names="Name", values="Total Submissions",
                         title="Submission Share", template="plotly")
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("⚠️ No data available for the selected filters.")

# ──────────────────────────────
# ✅ Footer Info
# ──────────────────────────────
st.markdown("<hr style='margin-top: 2em;'>", unsafe_allow_html=True)
st.markdown(f"<center><small><i class='fas fa-code'></i> Built with Streamlit | Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small></center>", unsafe_allow_html=True)

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

# ______________________________________
# 🔵 Load monthly tabs from Google Sheets
# ______________________________________
sheet_id = "1b0CTtJPUQT_4MCaSzuUja6gPJS-nwZeSsezZaz3Z1gk"
sheet = client.open_by_key(sheet_id)

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
            dataframes.append(df_tab)
    except Exception as e:
        errors.append((tab, str(e)))

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
