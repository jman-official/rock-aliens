import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

conn = st.connection("gsheets", type=GSheetsConnection)

df = conn.read(worksheet="1427641855")
# st.dataframe(df)

df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month_name()
df['Quarter'] = df['Date'].dt.to_period("Q")
df['Day'] = df['Date'].dt.date

df['Fees'] = df['Fees'].replace('[\u20B9,]', '', regex=True).astype(float)
df = df[df["Membership"] != "Active_Member"]

st.title("📊 Membership & Rentals")

view = st.sidebar.selectbox("Select View", ["Daily", "Monthly", "Quarterly", "Annual"])

if view == "Daily":
    selected_day = st.sidebar.date_input("Select Day", df['Date'].max())
    filtered = df[df['Day'] == selected_day]

elif view == "Monthly":
    selected_year = st.sidebar.selectbox("Select Year", sorted(df['Year'].unique(), reverse=True))
    selected_month = st.sidebar.selectbox("Select Month", df[df['Year'] == selected_year]['Month'].unique())
    filtered = df[(df['Year'] == selected_year) & (df['Month'] == selected_month)]

elif view == "Quarterly":
    selected_year = st.sidebar.selectbox("Select Year", sorted(df['Year'].unique(), reverse=True))
    selected_quarter = st.sidebar.selectbox("Select Quarter", df[df['Year'] == selected_year]['Quarter'].astype(str).unique())
    filtered = df[(df['Quarter'].astype(str) == selected_quarter)]

elif view == "Annual":
    selected_year = st.sidebar.selectbox("Select Year", sorted(df['Year'].unique(), reverse=True))
    filtered = df[df['Year'] == selected_year]

# Summary metrics
st.subheader(f"Summary for {view} View")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"₹{filtered['Fees'].sum():,.0f}")
col2.metric("Total Visits", len(filtered))
col3.metric("Total Rentals", filtered['Rentals'].sum())
col4.metric("Total Customers", filtered['Name'].nunique())

# Charts
st.subheader("Membership Type")
st.bar_chart(filtered['Membership'].value_counts())

st.subheader("Online vs Cash")
st.bar_chart(filtered.dropna().groupby("Mode of Payment")['Fees'].sum())

st.subheader("Mode of Payment")
st.bar_chart(filtered['Mode of Payment'].fillna('Membership').value_counts())

if view in ["Monthly", "Quarterly", "Annual"]:
    st.subheader("Revenue Over Time")
    revenue_series = filtered.groupby('Date')['Fees'].sum()
    st.line_chart(revenue_series)

# st.subheader("Raw Data")
# st.dataframe(filtered.sort_values(by='Date', ascending=False).reset_index(drop=True))