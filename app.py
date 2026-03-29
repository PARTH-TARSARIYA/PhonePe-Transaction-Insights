import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- LOAD DATA ----------------
agg_transaction = pd.read_csv("https://raw.githubusercontent.com/PARTH-TARSARIYA/PhonePe-Transaction-Insights/main/Data/agg_transaction.csv")
agg_insurance = pd.read_csv("https://raw.githubusercontent.com/PARTH-TARSARIYA/PhonePe-Transaction-Insights/main/Data/agg_insurance.csv")
agg_user = pd.read_csv("https://raw.githubusercontent.com/PARTH-TARSARIYA/PhonePe-Transaction-Insights/main/Data/agg_user.csv")
map_transaction = pd.read_csv("https://raw.githubusercontent.com/PARTH-TARSARIYA/PhonePe-Transaction-Insights/main/Data/map_transaction.csv")
map_user = pd.read_csv("https://raw.githubusercontent.com/PARTH-TARSARIYA/PhonePe-Transaction-Insights/main/Data/map_user.csv")
top_transaction = pd.read_csv("https://raw.githubusercontent.com/PARTH-TARSARIYA/PhonePe-Transaction-Insights/main/Data/top_transaction.csv")
top_user = pd.read_csv("https://raw.githubusercontent.com/PARTH-TARSARIYA/PhonePe-Transaction-Insights/main/Data/top_user.csv")

# ---------------- RENAME COLUMNS (CRITICAL FIX) ----------------
agg_transaction.rename(columns={"entity_name": "transaction_type"}, inplace=True)
agg_insurance.rename(columns={"entity_name": "insurance_type"}, inplace=True)
top_transaction.rename(columns={"entity_name": "entity"}, inplace=True)

# 🔥 FIX USER DATASET
map_user.rename(columns={
    "registered_users": "user_count",
    "app_opens": "app_opens_count"
}, inplace=True)

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="PhonePe Dashboard", layout="wide")
st.title("📊 PhonePe Data Dashboard")

# ---------------- SIDEBAR ----------------
st.sidebar.header("Filters")

states = sorted(agg_transaction['state'].dropna().unique())
years = sorted(agg_transaction['year'].unique())
quarters = sorted(agg_transaction['quarter'].unique())

selected_state = st.sidebar.selectbox("Select State", states)
selected_year = st.sidebar.selectbox("Select Year", years)
selected_quarter = st.sidebar.selectbox("Select Quarter", quarters)

# ---------------- FILTER FUNCTION ----------------
def filter_df(df):
    return df[(df['state'] == selected_state) &
              (df['year'] == selected_year) &
              (df['quarter'] == selected_quarter)]

agg_txn_f = filter_df(agg_transaction)
agg_ins_f = filter_df(agg_insurance)
agg_user_f = filter_df(agg_user)
map_txn_f = filter_df(map_transaction)
map_user_f = filter_df(map_user)
top_txn_f = filter_df(top_transaction)

# ---------------- KPIs ----------------
st.subheader("📌 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

col1.metric("Transactions", f"{agg_txn_f['count'].sum():,}")
col2.metric("Transaction Amount", f"₹ {agg_txn_f['amount'].sum():,.0f}")
col3.metric("Insurance Amount", f"₹ {agg_ins_f['amount'].sum():,.0f}")
col4.metric("Users", f"{map_user_f['user_count'].sum():,}")

# ---------------- TRANSACTION TYPE ----------------
st.subheader("💳 Transaction Type Analysis")
fig1 = px.bar(agg_txn_f, x='transaction_type', y='amount')
st.plotly_chart(fig1, use_container_width=True)

# ---------------- INSURANCE ----------------
st.subheader("🛡 Insurance Analysis")
fig2 = px.bar(agg_ins_f, x='insurance_type', y='amount')
st.plotly_chart(fig2, use_container_width=True)

# ---------------- BRAND ----------------
st.subheader("📱 User Brand Distribution")
fig3 = px.pie(agg_user_f, names='brand', values='count')
st.plotly_chart(fig3, use_container_width=True)

# ---------------- TOP STATES ----------------
st.subheader("🏆 Top States by Transactions")
top_states = (
    top_txn_f.groupby('entity')['amount']
    .sum()
    .nlargest(10)
    .reset_index()
)
fig4 = px.bar(top_states, x='entity', y='amount')
st.plotly_chart(fig4, use_container_width=True)

# ---------------- DISTRICT ----------------
st.subheader("📍 Top Districts")
top_districts = (
    map_txn_f.groupby('district')['amount']
    .sum()
    .nlargest(10)
    .reset_index()
)
fig5 = px.bar(top_districts, x='district', y='amount')
st.plotly_chart(fig5, use_container_width=True)

# ---------------- USER ENGAGEMENT ----------------
st.subheader("📊 User Engagement")
fig6 = px.scatter(map_user_f, x='user_count', y='app_opens_count')
st.plotly_chart(fig6, use_container_width=True)

# ---------------- CORRELATION ----------------
st.subheader("🔗 Users vs Transactions")
merged = map_txn_f.merge(
    map_user_f,
    on=['state','district','year','quarter']
)

fig7 = px.scatter(merged, x='user_count', y='amount')
st.plotly_chart(fig7, use_container_width=True)

# ---------------- TREND ----------------
st.subheader("📈 Growth Trend")
agg_transaction['time'] = (
    agg_transaction['year'].astype(str) + " Q" +
    agg_transaction['quarter'].astype(str)
)

trend = agg_transaction.groupby('time')['amount'].sum().reset_index()
fig8 = px.line(trend, x='time', y='amount', markers=True)
st.plotly_chart(fig8, use_container_width=True)

# ---------------- INSURANCE RATIO ----------------
st.subheader("📉 Insurance Penetration")
merged_state = agg_txn_f.merge(
    agg_ins_f,
    on=['state','year','quarter']
)

merged_state['insurance_ratio'] = (
    merged_state['amount_y'] / merged_state['amount_x']
)

fig9 = px.bar(merged_state, x='state', y='insurance_ratio')
st.plotly_chart(fig9, use_container_width=True)

st.success("🚀 Dashboard Ready")
