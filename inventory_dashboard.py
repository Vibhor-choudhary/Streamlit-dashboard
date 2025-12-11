import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# PAGE CONFIG
st.set_page_config(
    page_title="Inventory Optimization Dashboard",
    page_icon="🏪",
    layout="wide"
)

# LOAD DATA
@st.cache_data
def load_data():
    df = pd.read_csv('/content/drive/MyDrive/Retail Store Inventory Enhanced.csv')
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%y', errors='coerce')
    df['Month_Name'] = df['Date'].dt.strftime('%B')
    df['Revenue'] = df['Units Sold'] * df['Price']
    df['Is_Low_Stock'] = df['Inventory Level'] < 100
    df['Is_Overstock'] = df['Inventory Level'] > 400
    return df

df = load_data()

# SIDEBAR FILTERS
st.sidebar.markdown("# 🎛️ FILTERS")
st.sidebar.markdown("---")

regions = st.sidebar.multiselect(
    "📍 Region",
    sorted(df['Region'].unique()),
    default=sorted(df['Region'].unique())
)

categories = st.sidebar.multiselect(
    "🏷️ Category",
    sorted(df['Category'].unique()),
    default=sorted(df['Category'].unique())
)

stores = st.sidebar.multiselect(
    "🏬 Store",
    sorted(df['Store ID'].unique()),
    default=sorted(df['Store ID'].unique())
)

# APPLY FILTERS
filtered_df = df[
    (df['Region'].isin(regions)) &
    (df['Category'].isin(categories)) &
    (df['Store ID'].isin(stores))
]

# TITLE
st.title("🏪 Inventory Optimization Dashboard")
st.markdown("**Real-time insights for smarter inventory decisions**")
st.markdown("---")

# KPI SECTION
st.markdown("### 📊 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_revenue = filtered_df['Revenue'].sum()
    st.metric("💰 Total Revenue", f"${total_revenue:,.0f}")

with col2:
    avg_inventory = filtered_df['Inventory Level'].mean()
    st.metric("📦 Avg Inventory", f"{avg_inventory:,.0f} units")

with col3:
    low_stock_count = filtered_df['Is_Low_Stock'].sum()
    st.metric("⚠️ Low Stock Items", f"{low_stock_count:,}")

with col4:
    overstock_count = filtered_df['Is_Overstock'].sum()
    st.metric("📈 Overstocked Items", f"{overstock_count:,}")

st.markdown("---")

# PAGE SELECTION
page = st.radio(
    "Select View:",
    ["📈 Sales Overview", "📦 Inventory Status", "📅 Trends & Patterns"],
    horizontal=True
)

# PAGE 1: SALES OVERVIEW
if page == "📈 Sales Overview":

    st.markdown("## 📈 Sales Performance")

    col1, col2 = st.columns(2)

    with col1:
        revenue_region = filtered_df.groupby('Region')['Revenue'].sum().sort_values(ascending=False)
        fig_region = px.bar(
            x=revenue_region.index,
            y=revenue_region.values,
            title="Revenue by Region",
            color=revenue_region.values,
            color_continuous_scale='Blues'
        )
        fig_region.update_layout(height=400, showlegend=False, template='plotly_white')
        st.plotly_chart(fig_region, use_container_width=True)

    with col2:
        revenue_category = filtered_df.groupby('Category')['Revenue'].sum().sort_values(ascending=False)
        fig_category = px.bar(
            x=revenue_category.index,
            y=revenue_category.values,
            title="Revenue by Category",
            color=revenue_category.values,
            color_continuous_scale='Greens'
        )
        fig_category.update_layout(height=400, showlegend=False, template='plotly_white')
        st.plotly_chart(fig_category, use_container_width=True)

    st.markdown("---")

    st.markdown("## 🏬 Top Performing Stores")
    store_revenue = filtered_df.groupby('Store ID')['Revenue'].sum().sort_values(ascending=False)
    fig_stores = px.bar(
        x=store_revenue.index,
        y=store_revenue.values,
        title="Top Stores by Revenue",
        color=store_revenue.values,
        color_continuous_scale='Oranges'
    )
    fig_stores.update_layout(height=400, showlegend=False, template='plotly_white')
    st.plotly_chart(fig_stores, use_container_width=True)

# PAGE 2: INVENTORY STATUS
elif page == "📦 Inventory Status":

    st.markdown("## 📦 Inventory Analysis")

    col1, col2 = st.columns(2)

    with col1:
        fig_inv_dist = px.histogram(
            filtered_df,
            x='Inventory Level',
            nbins=30,
            title="Inventory Distribution",
            color_discrete_sequence=['#3498db']
        )
        fig_inv_dist.update_layout(height=400, template='plotly_white', showlegend=False)
        st.plotly_chart(fig_inv_dist, use_container_width=True)

    with col2:
        inv_region = filtered_df.groupby('Region')['Inventory Level'].mean().sort_values()
        fig_inv_region = px.bar(
            x=inv_region.values,
            y=inv_region.index,
            orientation='h',
            title="Avg Inventory by Region",
            color=inv_region.values,
            color_continuous_scale='Viridis'
        )
        fig_inv_region.update_layout(height=400, showlegend=False, template='plotly_white')
        st.plotly_chart(fig_inv_region, use_container_width=True)

    st.markdown("---")
    st.markdown("## ⚠️ Stock Status")

    status_col1, status_col2, status_col3 = st.columns(3)

    with status_col1:
        low_stock = (filtered_df['Inventory Level'] < 100).sum()
        st.metric("🔴 Low Stock", f"{low_stock:,} items")

    with status_col2:
        optimal = ((filtered_df['Inventory Level'] >= 100) & (filtered_df['Inventory Level'] <= 400)).sum()
        st.metric("🟢 Optimal Stock", f"{optimal:,} items")

    with status_col3:
        high_stock = (filtered_df['Inventory Level'] > 400).sum()
        st.metric("🟡 High Stock", f"{high_stock:,} items")

    st.markdown("---")
    st.markdown("## 📊 Inventory by Category")

    inv_category = filtered_df.groupby('Category')['Inventory Level'].sum()
    fig_inv_cat = px.pie(
        values=inv_category.values,
        names=inv_category.index,
        title="Inventory Distribution",
        hole=0.3
    )
    fig_inv_cat.update_layout(height=400)
    st.plotly_chart(fig_inv_cat, use_container_width=True)

# PAGE 3: TRENDS & PATTERNS
elif page == "📅 Trends & Patterns":

    st.markdown("## 📅 Seasonal Patterns")

    col1, col2 = st.columns(2)

    with col1:
        monthly_data = filtered_df.groupby('Month_Name')['Revenue'].sum().reset_index()
        month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        monthly_data['Month_Name'] = pd.Categorical(monthly_data['Month_Name'], categories=month_order, ordered=True)
        monthly_data = monthly_data.sort_values('Month_Name')

        fig_monthly = px.line(
            monthly_data,
            x='Month_Name',
            y='Revenue',
            title="Monthly Revenue Trend",
            markers=True
        )
        fig_monthly.update_traces(line=dict(color='#e74c3c', width=3))
        fig_monthly.update_layout(height=400, template='plotly_white', hovermode='x unified')
        st.plotly_chart(fig_monthly, use_container_width=True)

    with col2:
        seasonal_data = filtered_df.groupby('Seasonality')['Units Sold'].sum().reset_index()
        fig_seasonal = px.bar(
            seasonal_data,
            x='Seasonality',
            y='Units Sold',
            title="Units Sold by Season",
            color='Units Sold',
            color_continuous_scale='Viridis'
        )
        fig_seasonal.update_layout(height=400, template='plotly_white', showlegend=False)
        st.plotly_chart(fig_seasonal, use_container_width=True)

    st.markdown("---")
    st.markdown("## 📊 Revenue Heatmap")

    pivot_data = filtered_df.pivot_table(
        values='Revenue',
        index='Category',
        columns='Region',
        aggfunc='sum'
    )

    fig_heatmap = px.imshow(
        pivot_data,
        labels=dict(x="Region", y="Category", color="Revenue"),
        title="Revenue: Category × Region",
        color_continuous_scale='Blues'
    )
    fig_heatmap.update_layout(height=400)
    st.plotly_chart(fig_heatmap, use_container_width=True)
