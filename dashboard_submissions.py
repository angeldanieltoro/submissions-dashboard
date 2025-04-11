import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Submissions Dashboard", layout="wide")
st.title("📊 Employee Submissions Dashboard (Last 8 Months)")

# Load all Excel files in the directory
dataframes = []
for file in os.listdir():
    if file.startswith("submissions_") and file.endswith(".xlsx"):
        df = pd.read_excel(file)
        df["Source File"] = file
        dataframes.append(df)

# Combine into one DataFrame
if not dataframes:
    st.warning("⚠️ No Excel files found.")
    st.stop()

df_all = pd.concat(dataframes, ignore_index=True)

# Remove 'TOTAL' row and convert dates
df_all = df_all[df_all["Date"] != "TOTAL"]
df_all["Date"] = pd.to_datetime(df_all["Date"], errors="coerce")
df_all["Month"] = df_all["Date"].dt.month_name()
df_all["Year"] = df_all["Date"].dt.year

# Sidebar filters
st.sidebar.header("Filters")
year = st.sidebar.selectbox("Year", sorted(df_all["Year"].unique(), reverse=True))
month = st.sidebar.selectbox("Month", sorted(df_all[df_all["Year"] == year]["Month"].unique()))
employees = st.sidebar.multiselect("Employees", df_all["Name"].unique(), default=df_all["Name"].unique())

# Filter data
filtered = df_all[
    (df_all["Year"] == year) &
    (df_all["Month"] == month) &
    (df_all["Name"].isin(employees))
]

# Show filtered data
st.subheader(f"📅 Submissions for {month} {year}")
st.dataframe(filtered.sort_values(by="Date"))

# Line Chart – Daily Trends
st.subheader("📈 Daily Submissions")
pivot = filtered.pivot(index="Date", columns="Name", values="Total Submissions")
st.line_chart(pivot.fillna(0))

# Bar Chart – Total Submissions
st.subheader("📊 Total Submissions by Employee")
totals = filtered.groupby("Name")["Total Submissions"].sum().reset_index()
fig1, ax1 = plt.subplots()
ax1.bar(totals["Name"], totals["Total Submissions"], color='royalblue')
ax1.set_title("Total Submissions")
ax1.set_ylabel("Submissions")
plt.xticks(rotation=45)
st.pyplot(fig1)

# Pie Chart – Share
st.subheader("🧩 Submission Share")
fig2, ax2 = plt.subplots()
ax2.pie(totals["Total Submissions"], labels=totals["Name"], autopct="%1.1f%%", startangle=90)
ax2.axis("equal")
st.pyplot(fig2)