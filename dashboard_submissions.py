import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ✅ THIS MUST BE FIRST Streamlit COMMAND
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
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/line-awesome/1.3.0/line-awesome/css/line-awesome.min.css">
""", unsafe_allow_html=True)

# ──────────────────────────────
# 🌗 THEME SWITCHING
# ──────────────────────────────
theme = st.sidebar.radio("🌓 Theme", ["Light", "Dark"])

if theme == "Dark":
    bg_color = "#1E1E1E"
    text_color = "#FFFFFF"
    sidebar_bg = "#333333"
    plotly_template = "plotly_dark"
else:
    bg_color = "#FFFFFF"
    text_color = "#000000"
    sidebar_bg = "#F0F2F6"
    plotly_template = "plotly"

st.markdown(
    f"""
    <style>
    .reportview-container {{
        background-color: {bg_color};
        color: {text_color};
    }}
    .sidebar .sidebar-content {{
        background-color: {sidebar_bg};
        color: {text_color};
    }}
    h1, h2, h3 {{
        color: {text_color};
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ──────────────────────────────
# 📋 PAGE CONFIG
# ──────────────────────────────
st.set_page_config(page_title="Submissions Dashboard", layout="wide")
st.markdown('<h1><i class="fas fa-chart-pie"></i> Submissions Dashboard <small style="font-size:16px;">(Last 8 Months)</small></h1>', unsafe_allow_html=True)

# ──────────────────────────────
# 📁 Load Excel files
# ──────────────────────────────
dataframes = []
for file in os.listdir():
    if file.startswith("submissions_") and file.endswith(".xlsx"):
        df = pd.read_excel(file)
        df["Source File"] = file
        dataframes.append(df)

if not dataframes:
    st.warning("⚠️ No Excel files found.")
    st.stop()

df_all = pd.concat(dataframes, ignore_index=True)
df_all = df_all[df_all["Date"] != "TOTAL"]
df_all["Date"] = pd.to_datetime(df_all["Date"], errors="coerce")
df_all["Month"] = df_all["Date"].dt.month_name()
df_all["Year"] = df_all["Date"].dt.year

# ──────────────────────────────
# 🎯 FILTERS IN SIDEBAR
# ──────────────────────────────
st.sidebar.header("📁 Filters")
year = st.sidebar.selectbox("📅 Year", sorted(df_all["Year"].unique(), reverse=True))
month = st.sidebar.selectbox("🗓 Month", sorted(df_all[df_all["Year"] == year]["Month"].unique()))
employees = st.sidebar.multiselect("👤 Employees", df_all["Name"].unique(), default=df_all["Name"].unique())

filtered = df_all[
    (df_all["Year"] == year) &
    (df_all["Month"] == month) &
    (df_all["Name"].isin(employees))
]

# ──────────────────────────────
# 🗂 TABS SECTION
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
    st.markdown('<h3><i class="las la-chart-bar"></i> Daily Submissions Trend</h3>', unsafe_allow_html=True)
    pivot = filtered.pivot(index="Date", columns="Name", values="Total Submissions")
    fig_line = px.line(pivot, x=pivot.index, y=pivot.columns,
                       title="Daily Submissions",
                       template=plotly_template)
    st.plotly_chart(fig_line, use_container_width=True)

    st.markdown('<h3><i class="las la-user"></i> Total Submissions by Employee</h3>', unsafe_allow_html=True)
    totals = filtered.groupby("Name")["Total Submissions"].sum().reset_index()
    fig_bar = px.bar(totals, x="Name", y="Total Submissions",
                     title="Total Submissions",
                     color="Total Submissions",
                     template=plotly_template)
    st.plotly_chart(fig_bar, use_container_width=True)

with tab3:
    st.markdown('<h3><i class="fas fa-chart-pie"></i> Share of Submissions</h3>', unsafe_allow_html=True)
    fig_pie = px.pie(totals, names="Name", values="Total Submissions",
                     title="Submission Share",
                     template=plotly_template)
    st.plotly_chart(fig_pie, use_container_width=True)

# ──────────────────────────────
# ✅ FOOTER
# ──────────────────────────────
st.markdown("<hr style='margin-top: 2em;'>", unsafe_allow_html=True)
st.markdown("<center><small><i class='fas fa-code'></i> Built with Streamlit | Designed with ❤️ by You</small></center>", unsafe_allow_html=True)
