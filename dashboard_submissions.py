import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
import json
from google.oauth2.service_account import Credentials

#  Streamlit Config
st.set_page_config(page_title="Submissions Dashboard", layout="wide")

#  Page Header
st.markdown('<h1><i class="fas fa-chart-pie"></i> Submissions Dashboard <small style="font-size:16px;">(Last 8 Months)</small></h1>', unsafe_allow_html=True)

#  Connect to Google Sheets
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"])
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
client = gspread.authorize(creds)

sheet_id = "1b0CTtJPUQT_4MCaSzuUja6gPJS-nwZeSsezZaz3Z1gk"
sheet = client.open_by_key(sheet_id)
worksheet = sheet.sheet1  # Assuming combined sheet is first tab

#  Load Data
sheet_data = worksheet.get_all_records()
df_all = pd.DataFrame(sheet_data)

#  Basic Cleaning
if not df_all.empty:
    df_all["Date"] = pd.to_datetime(df_all["Date"], errors="coerce")
    df_all["Month"] = df_all["Date"].dt.month_name()
    df_all["Year"] = df_all["Date"].dt.year

#  Filters Sidebar
with st.sidebar.expander("\ud83d\udcc1 Filters", expanded=True):
    year = st.selectbox("\ud83d\udcc5 Year", sorted(df_all["Year"].dropna().unique(), reverse=True), key="selected_year")
    month = st.selectbox("\ud83d\uddd3 Month", sorted(df_all[df_all["Year"] == year]["Month"].dropna().unique()), key="selected_month")

    employee_options = sorted(df_all["Name"].dropna().unique())
    selected_employees = st.session_state.get("selected_employee", employee_options)
    if not isinstance(selected_employees, list):
        selected_employees = employee_options

    employees = st.multiselect(
        "\ud83d\udc64 Employees",
        options=employee_options,
        default=selected_employees,
        key="selected_employee"
    )

#  Select Date
new_date = st.sidebar.date_input("\ud83d\uddd5\ufe0f Select a Specific Date", value=st.session_state.get("selected_date"))

# Auto-clear if Year/Month changes
if (year != st.session_state.get("last_selected_year")) or (month != st.session_state.get("last_selected_month")):
    st.session_state["selected_date"] = None

# Save Date and Selections
st.session_state["selected_date"] = new_date
st.session_state["last_selected_year"] = year
st.session_state["last_selected_month"] = month

#  Manual Refresh Button
if st.button("\ud83d\udd04 Refresh App"):
    st.rerun()

#  Apply Filters
filtered = df_all[
    (df_all["Year"] == year) &
    (df_all["Month"] == month) &
    (df_all["Name"].isin(employees))
]

#  Apply Date Filter if Selected
if st.session_state.get("selected_date"):
    filtered = filtered[filtered["Date"] == pd.to_datetime(st.session_state["selected_date"])]

# 🖥 Main Layout
if not filtered.empty:
    tab1, tab2, tab3 = st.tabs(["\ud83d\udccb Data Table", "\ud83d\udcc8 Charts", "\ud83c\udf1f Submission Share"])

    with tab1:
        st.markdown('<h3><i class="iconoir-report-columns"></i> Filtered Data Table</h3>', unsafe_allow_html=True)
        st.dataframe(filtered.sort_values(by="Date"))

    with tab2:
        st.markdown('<h3><i class="las la-chart-bar"></i> Daily Submissions Trend</h3>', unsafe_allow_html=True)
        pivot = filtered.pivot_table(index="Date", columns="Name", values="Total Submissions", aggfunc="sum")
        fig_line = px.line(pivot, x=pivot.index, y=pivot.columns, title="Daily Submissions", template="plotly")
        st.plotly_chart(fig_line, use_container_width=True)

    with tab3:
        st.markdown('<h3><i class="las la-user"></i> Total Submissions by Employee</h3>', unsafe_allow_html=True)
        totals = filtered.groupby("Name")["Total Submissions"].sum().reset_index()
        fig_bar = px.bar(totals, x="Name", y="Total Submissions", color="Total Submissions", title="Total Submissions", template="plotly")
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown('<h3><i class="fas fa-chart-pie"></i> Share of Submissions</h3>', unsafe_allow_html=True)
        fig_pie = px.pie(totals, names="Name", values="Total Submissions", title="Submission Share", template="plotly")
        st.plotly_chart(fig_pie, use_container_width=True)

else:
    st.warning("\u26a0\ufe0f No data available for the selected filters.")

#  Footer
st.markdown("<hr style='margin-top: 2em;'>", unsafe_allow_html=True)
st.markdown(f"<center><small><i class='fas fa-code'></i> Built with Streamlit | Last update: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</small></center>", unsafe_allow_html=True)
