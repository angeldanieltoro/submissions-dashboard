import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json
from google.oauth2.service_account import Credentials
import gspread

# ✅ MUST be the first Streamlit command
st.set_page_config(page_title="Submissions Dashboard", layout="wide")

# ──────────────────────────────
# 🧠 ICON CSS LIBRARIES
# ──────────────────────────────
st.markdown("""
    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <!-- Iconoir -->
    <link href="https://cdn.jsdelivr.net/npm/iconoir@latest/css/iconoir.css" rel="stylesheet">
    <!-- Line Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/line-awesome/1.3.0/line-awesome.min.css">
""", unsafe_allow_html=True)

# ──────────────────────────────
# 📋 PAGE HEADER
# ──────────────────────────────
st.markdown('<h1><i class="fas fa-chart-pie"></i> Submissions Dashboard <small style="font-size:16px;">(Last 8 Months)</small></h1>', unsafe_allow_html=True)

# ──────────────────────────────
# ☁️ Load April from Google Sheets
# ──────────────────────────────
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"])
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
client = gspread.authorize(creds)

sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1b0CTtJPUQT_4MCaSzuUja6gPJS-nwZeSsezZaz3Z1gk")
worksheet = sheet.worksheet("April2025")

april_data = worksheet.get_all_records()
df_april = pd.DataFrame(april_data)
df_april["Date"] = pd.to_datetime(df_april["Date"], errors="coerce")
df_april["Month"] = df_april["Date"].dt.month_name()
df_april["Year"] = df_april["Date"].dt.year
df_april["Source File"] = "Google Sheets"

# ──────────────────────────────
# 📁 Load Excel Files for Other Months
# ──────────────────────────────
dataframes = []

for file in os.listdir():
    if file.startswith("submissions_") and file.endswith(".xlsx"):
        df = pd.read_excel(file)
        df["Source File"] = file
        dataframes.append(df)

# ✅ Append April Google Sheet data
dataframes.append(df_april)

if not dataframes:
    st.warning("⚠️ No Excel files found.")
    st.stop()

df_all = pd.concat(dataframes, ignore_index=True)
df_all = df_all[df_all["Date"] != "TOTAL"]
df_all["Date"] = pd.to_datetime(df_all["Date"], errors="coerce")
df_all["Month"] = df_all["Date"].dt.month_name()
df_all["Year"] = df_all["Date"].dt.year

# ──────────────────────────────
# 🎯 FILTERS
# ──────────────────────────────
if "selected_year" not in st.session_state:
    st.session_state.selected_year = None
if "selected_month" not in st.session_state:
    st.session_state.selected_month = None
if "selected_date" not in st.session_state:
    st.session_state.selected_date = None

st.sidebar.header("📁 Filters")
year = st.sidebar.selectbox("📅 Year", sorted(df_all["Year"].unique(), reverse=True))
month = st.sidebar.selectbox("🗓 Month", sorted(df_all[df_all["Year"] == year]["Month"].unique()))

if year != st.session_state.selected_year or month != st.session_state.selected_month:
    st.session_state.selected_date = None

st.session_state.selected_year = year
st.session_state.selected_month = month

employees = st.sidebar.multiselect("👤 Employees", df_all["Name"].unique(), default=df_all["Name"].unique())
selected_date = st.sidebar.date_input("📆 Select a Date", value=st.session_state.selected_date)
st.session_state.selected_date = selected_date

filtered = df_all[
    (df_all["Year"] == year) &
    (df_all["Month"] == month) &
    (df_all["Name"].isin(employees))
]

if selected_date:
    filtered = filtered[filtered["Date"] == pd.to_datetime(selected_date)]

# ──────────────────────────────
# 🗂 TABS SECTION
# ──────────────────────────────
tab1, tab2, tab3 = st.tabs(["📄 Data Table", "📊 Charts", "🧩 Submission Share"])

with tab1:
    st.markdown('<h3><i class="iconoir-report-columns"></i> Filtered Data Table</h3>', unsafe_allow_html=True)
    st.dataframe(filtered.sort_values(by="Date"))

with tab2:
    st.markdown('<h3><i class="las la-chart-bar"></i> Daily Submissions Trend</h3>', unsafe_allow_html=True)
    if not filtered.empty:
        pivot = filtered.pivot(index="Date", columns="Name", values="Total Submissions")
        fig_line = px.line(pivot, x=pivot.index, y=pivot.columns, title="Daily Submissions", template="plotly")
        st.plotly_chart(fig_line, use_container_width=True)

        st.markdown('<h3><i class="las la-user"></i> Total Submissions by Employee</h3>', unsafe_allow_html=True)
        totals = filtered.groupby("Name")["Total Submissions"].sum().reset_index()
        fig_bar = px.bar(totals, x="Name", y="Total Submissions", color="Total Submissions", template="plotly")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("No data available for the selected filters.")

with tab3:
    st.markdown('<h3><i class="fas fa-chart-pie"></i> Share of Submissions</h3>', unsafe_allow_html=True)
    if not filtered.empty:
        totals = filtered.groupby("Name")["Total Submissions"].sum().reset_index()
        fig_pie = px.pie(totals, names="Name", values="Total Submissions", title="Submission Share", template="plotly")
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("No data available for the selected filters.")

# ──────────────────────────────
# ✅ FOOTER
# ──────────────────────────────
st.markdown("<hr style='margin-top: 2em;'>", unsafe_allow_html=True)
st.markdown("<center><small><i class='fas fa-code'></i> Built with Streamlit | Designed with ❤️ by You</small></center>", unsafe_allow_html=True)
