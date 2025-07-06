import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Membership Dashboard", layout="wide")

st.title("📊 Membership & Rentals Dashboard")

conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(worksheet="1427641855")

# Data prep
df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month_name()
df['Quarter'] = df['Date'].dt.to_period("Q")
df['Day'] = df['Date'].dt.date

df['Fees'] = df['Fees'].replace('[\u20B9,]', '', regex=True).astype(float)
df = df[df["Membership"] != "Active_Member"]

# Sidebar view selection
st.sidebar.header("🔎 Filter Data")
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
st.markdown("### 📈 Summary Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Revenue", f"₹{filtered['Fees'].sum():,.0f}")
col2.metric("👣 Total Visits", len(filtered))
col3.metric("🎯 Total Rentals", int(filtered['Rentals'].sum()))
col4.metric("🙋‍♂️ Unique Customers", filtered['Name'].nunique())

st.divider()

# Membership Chart
with st.expander("📌 Membership Type Distribution", expanded=True):
    membership_counts = filtered['Membership'].value_counts().reset_index()
    membership_counts.columns = ['Membership Type', 'Count']

    fig1 = px.bar(
        membership_counts,
        x='Membership Type',
        y='Count',
        color='Membership Type',
        title="Membership Type Counts",
        template="plotly_white"
    )
    st.plotly_chart(fig1, use_container_width=True)

# Online vs Cash Revenue
with st.expander("💳 Payment Mode - Revenue", expanded=True):
    payment_revenue = filtered.dropna().groupby("Mode of Payment")['Fees'].sum().reset_index()

    fig2 = px.bar(
        payment_revenue,
        x="Mode of Payment",
        y="Fees",
        color="Mode of Payment",
        title="Revenue by Mode of Payment",
        template="plotly_white"
    )
    st.plotly_chart(fig2, use_container_width=True)

# Mode of Payment Frequency
with st.expander("🧾 Payment Frequency", expanded=True):
    payment_counts = filtered['Mode of Payment'].fillna('Membership').value_counts().reset_index()
    payment_counts.columns = ['Mode of Payment', 'Count']

    fig3 = px.pie(
        payment_counts,
        names='Mode of Payment',
        values='Count',
        title="Transaction Counts by Payment Mode"
    )
    st.plotly_chart(fig3, use_container_width=True)

# Revenue Over Time
if view in ["Monthly", "Quarterly", "Annual"]:
    with st.expander("📅 Revenue Over Time", expanded=True):
        fig4 = px.line(
            filtered.groupby('Date')['Fees'].sum().reset_index(),
            x='Date', y='Fees',
            title="Revenue Trend",
            markers=True,
            template="plotly_white"
        )
        st.plotly_chart(fig4, use_container_width=True)

# Optional raw data
with st.expander("🧾 Raw Data"):
    st.dataframe(
        filtered.sort_values(by='Date', ascending=False).reset_index(drop=True),
        use_container_width=True,
        height=300
    )