
import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Lulu UAE Sales Dashboard", layout="wide", initial_sidebar_state="expanded")

# ==============================
# LOAD DATA
# ==============================
@st.cache_data
def load_data(path):
    df = pd.read_csv(path, parse_dates=["order_datetime"], infer_datetime_format=True)
    df.columns = [c.strip() for c in df.columns]
    df['order_month_dt'] = pd.to_datetime(df['order_month'], errors='coerce')
    df['day_of_week'] = df['order_datetime'].dt.day_name()
    df['hour_of_day'] = df['order_datetime'].dt.hour
    df['line_value_aed'] = pd.to_numeric(df['line_value_aed'], errors='coerce')
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
    return df

# === Path to your dataset ===
DATA_PATH = "data/lulu_uae_master_2000.csv"  # <- place your dataset here
df = load_data(DATA_PATH)

# ==============================
# SIDEBAR FILTERS
# ==============================
st.sidebar.header("🔍 Filters")

department = st.sidebar.selectbox("Department", ["All"] + sorted(df['department'].unique()))
category = st.sidebar.selectbox("Category", ["All"] + sorted(df['category'].unique()))
nationality = st.sidebar.selectbox("Nationality", ["All"] + sorted(df['nationality_group'].unique()))
age_min, age_max = st.sidebar.slider("Age Range", int(df['age'].min()), int(df['age'].max()), (int(df['age'].min()), int(df['age'].max())))
month = st.sidebar.selectbox("Month", ["All"] + sorted(df['order_month'].unique()))

graph_choice = st.sidebar.selectbox("Choose Visualization", [
    "Monthly Revenue Trend",
    "Channel Ratio",
    "Orders by Day of Week",
    "Top Cities",
    "Top City Zones",
    "Average Order Value (AOV)",
    "Department Sales",
    "Category Sales",
    "Basket Size Distribution"
])

# Apply filters
df_filtered = df.copy()
if department != "All":
    df_filtered = df_filtered[df_filtered['department'] == department]
if category != "All":
    df_filtered = df_filtered[df_filtered['category'] == category]
if nationality != "All":
    df_filtered = df_filtered[df_filtered['nationality_group'] == nationality]
df_filtered = df_filtered[(df_filtered['age'] >= age_min) & (df_filtered['age'] <= age_max)]
if month != "All":
    df_filtered = df_filtered[df_filtered['order_month'] == month]

# ==============================
# KPIs
# ==============================
st.title("📊 Lulu UAE Sales Dashboard")
col1, col2, col3, col4 = st.columns(4)

total_sales = df_filtered['line_value_aed'].sum()
unique_orders = df_filtered['order_id'].nunique()
avg_order_value = df_filtered.groupby('order_id')['line_value_aed'].sum().mean()
loyalty_ratio = (df_filtered['loyalty_member'].mean()) * 100

col1.metric("Total Sales (AED)", f"{total_sales:,.0f}")
col2.metric("Unique Orders", f"{unique_orders:,}")
col3.metric("Avg Order Value (AED)", f"{avg_order_value:,.2f}")
col4.metric("Loyalty Members (%)", f"{loyalty_ratio:.1f}%")

st.markdown("---")

# ==============================
# BUSINESS INSIGHTS
# ==============================
st.subheader("💡 Business Insights & Recommendations")

insights = [
    "• **Loyalty Flash Sales:** Schedule flash sales on quiet weekdays to increase store traffic.",
    f"• **Free-Shipping Threshold:** Current AOV ≈ AED {avg_order_value:,.2f}. Test threshold at **{avg_order_value * 1.15:,.2f}** (AOV +15%).",
    "• **SKU Localization:** Identify and stock top 50 SKUs per city_zone to prevent stockouts.",
    "• **Online Strategy:** In online-heavy cities, offer app-only next-day delivery and exclusive coupons.",
    "• **Mid-Month Retention:** Run loyalty-only flash sales mid-month for top customers by frequency."
]
for line in insights:
    st.markdown(line)

st.markdown("---")

# ==============================
# VISUALIZATIONS
# ==============================
st.subheader("📈 Visual Analysis")

def plot_monthly_trend(df):
    monthly = df.groupby('order_month_dt')['line_value_aed'].sum().sort_index()
    fig, ax = plt.subplots(figsize=(10,4))
    ax.plot(monthly.index, monthly.values, marker='o')
    ax.set_title("Monthly Revenue Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue (AED)")
    st.pyplot(fig)

def plot_channel_ratio(df):
    ch = df.groupby('channel')['line_value_aed'].sum()
    fig, ax = plt.subplots(figsize=(6,4))
    ax.pie(ch, labels=ch.index, autopct='%1.1f%%')
    ax.set_title("Online vs Offline Sales Share")
    st.pyplot(fig)

def plot_dow(df):
    dow = df.groupby('day_of_week')['order_id'].nunique().reindex(
        ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    )
    fig, ax = plt.subplots(figsize=(8,4))
    sns.barplot(x=dow.index, y=dow.values, ax=ax)
    ax.set_title("Orders by Day of Week")
    st.pyplot(fig)

def plot_top_cities(df):
    cities = df.groupby('city')['line_value_aed'].sum().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(8,4))
    sns.barplot(x=cities.values, y=cities.index, ax=ax)
    ax.set_title("Top Cities by Revenue")
    st.pyplot(fig)

def plot_top_city_zones(df):
    zones = df.groupby('city_zone')['line_value_aed'].sum().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(8,4))
    sns.barplot(x=zones.values, y=zones.index, ax=ax)
    ax.set_title("Top City Zones by Revenue")
    st.pyplot(fig)

def plot_aov(df):
    orders = df.groupby('order_id')['line_value_aed'].sum()
    fig, ax = plt.subplots(figsize=(8,4))
    sns.histplot(orders, bins=30, kde=True, ax=ax)
    ax.set_title("Average Order Value Distribution")
    st.pyplot(fig)

def plot_department_sales(df):
    dept = df.groupby('department')['line_value_aed'].sum().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(8,4))
    sns.barplot(x=dept.values, y=dept.index, ax=ax)
    ax.set_title("Department Sales")
    st.pyplot(fig)

def plot_category_sales(df):
    cat = df.groupby('category')['line_value_aed'].sum().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(8,4))
    sns.barplot(x=cat.values, y=cat.index, ax=ax)
    ax.set_title("Category Sales")
    st.pyplot(fig)

def plot_basket_size(df):
    fig, ax = plt.subplots(figsize=(8,4))
    sns.histplot(df['basket_size_items'], bins=20, ax=ax)
    ax.set_title("Basket Size Distribution")
    st.pyplot(fig)

# Show the selected visualization
if graph_choice == "Monthly Revenue Trend":
    plot_monthly_trend(df_filtered)
elif graph_choice == "Channel Ratio":
    plot_channel_ratio(df_filtered)
elif graph_choice == "Orders by Day of Week":
    plot_dow(df_filtered)
elif graph_choice == "Top Cities":
    plot_top_cities(df_filtered)
elif graph_choice == "Top City Zones":
    plot_top_city_zones(df_filtered)
elif graph_choice == "Average Order Value (AOV)":
    plot_aov(df_filtered)
elif graph_choice == "Department Sales":
    plot_department_sales(df_filtered)
elif graph_choice == "Category Sales":
    plot_category_sales(df_filtered)
elif graph_choice == "Basket Size Distribution":
    plot_basket_size(df_filtered)

st.markdown("---")

# ==============================
# TABULAR INSIGHTS
# ==============================
st.subheader("📋 Tabular Insights")

top_skus = (
    df_filtered.groupby(['sku_id','brand','city_zone'])['line_value_aed']
    .sum().reset_index().sort_values('line_value_aed', ascending=False).head(50)
)
st.dataframe(top_skus)

st.download_button(
    label="Download Filtered Data",
    data=df_filtered.to_csv(index=False).encode('utf-8'),
    file_name="C:/Users/Neel/OneDrive/Desktop/Major Project/Project code/Lulu_Dashboard/data/lulu_uae_master_2000.csv",
    mime="text/csv"
)

st.caption("Built by IP Group 1(Neel Kapadia,Weiqi Liu,Neha Thapa and Gagandeep Singh) | Lulu Hypermarket UAE | Streamlit Dashboard")
