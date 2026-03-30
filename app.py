import streamlit as st
import pandas as pd
import numpy as np
from supabase import create_client, Client
import plotly.express as px

# --- 1. APP CONFIGURATION & BRANDING ---
st.set_page_config(
    page_title="SmartStock BI",
    page_icon="📊",
    layout="wide"
)

# --- 2. CUSTOM CSS (Navy Theme & PWA Setup) ---
st.markdown("""
    <style>
    /* Navy Blue Header and Background */
    .stApp {
        background-color: #001f3f; /* Navy Blue */
        color: #ffffff;
    }
    
    /* Change Sidebar color */
    section[data-testid="stSidebar"] {
        background-color: #001529;
    }
    
    /* Make buttons and inputs look clean */
    .stButton>button {
        background-color: #007bff;
        color: white;
        border-radius: 8px;
    }

    /* Glassmorphism containers */
    div.block-container {
        padding-top: 2rem;
    }
    </style>
    
    <script>
      if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
          navigator.serviceWorker.register('/sw.js').then(function(registration) {
            console.log('ServiceWorker registration successful');
          }, function(err) {
            console.log('ServiceWorker registration failed: ', err);
          });
        });
      }
    </script>
    """, unsafe_allow_html=True)

# --- 3. DATABASE CONNECTION ---
# Replace these with your project's info
SUPABASE_URL = "YOUR_SUPABASE_URL"
SUPABASE_KEY = "YOUR_SUPABASE_KEY"


@st.cache_resource
def init_db():
    return create_client(SUPABASE_URL, SUPABASE_KEY)


try:
    supabase = init_db()
except:
    st.error("⚠️ Connection Pending: Please add your Supabase Keys.")

# --- 4. NAVIGATION ---
st.sidebar.title("🚀 SmartStock")
st.sidebar.markdown("---")
menu = st.sidebar.selectbox(
    "Dashboard", ["Inventory Hub", "Customer Churn", "Marketing ROI"])

# --- 5. INVENTORY HUB (Supply Chain) ---
if menu == "Inventory Hub":
    st.title("📦 SmartStock Inventory")

    # Summary Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Warehouse Capacity", "84%", "+2%")
    c2.metric("Items Below Safety", "5 Items",
              "Critical", delta_color="inverse")
    c3.metric("Total Asset Value", "$124,500")

    # Fetch Data from Supabase
    res = supabase.table("smartstock_inventory").select("*").execute()
    if res.data:
        df = pd.DataFrame(res.data)
        st.dataframe(df, use_container_width=True)

        # Optimization Chart
        fig = px.bar(df, x="item_name", y="current_stock",
                     color="current_stock", title="Current Stock Levels",
                     color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)

# --- 6. CUSTOMER CHURN ---
elif menu == "Customer Churn":
    st.title("📉 Churn Prediction Engine")

    with st.expander("Analyze New Customer"):
        name = st.text_input("Customer Name")
        eng = st.slider("Engagement Level", 0, 100, 50)
        tix = st.number_input("Support Tickets (Last 30 Days)", 0, 20)

        # Simple Logic for the score
        calculated_risk = (tix * 10) + (100 - eng) / 2

        if st.button("Calculate Risk Score"):
            supabase.table("smartstock_customers").insert({
                "customer_name": name,
                "engagement_score": eng,
                "support_tickets": tix,
                "churn_risk_score": min(100, calculated_risk)
            }).execute()
            st.success(f"Analysis Complete for {name}!")

# --- 7. MARKETING ROI ---
else:
    st.title("💰 Marketing ROI Analyzer")
    st.info("Visualizing return on ad spend across channels.")

    # Mock Data for Visualization
    mkt_data = pd.DataFrame({
        'Channel': ['Google Ads', 'TikTok', 'Email', 'LinkedIn'],
        'ROI': [3.2, 5.8, 8.1, 2.4]
    })
    fig_mkt = px.line(mkt_data, x='Channel', y='ROI',
                      markers=True, title="ROI Trend")
    st.plotly_chart(fig_mkt, use_container_width=True)
