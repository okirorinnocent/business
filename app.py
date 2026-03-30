import streamlit as st
import pandas as pd
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID
import plotly.express as px

# --- 1. APP CONFIG & ENHANCED STYLING ---
st.set_page_config(page_title="SmartStock BI", page_icon="📊", layout="wide")

# Outstanding Background & UI Enhancements
st.markdown("""
    <style>
    /* Main App Background Gradient */
    .stApp {
        background: linear-gradient(135deg, #001f3f 0%, #000814 100%);
        color: white;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #000814 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Glassmorphism for Metrics and Cards */
    [data-testid="stMetric"], .stExpander, .stDataFrame {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !items;
        backdrop-filter: blur(10px);
        border-radius: 12px !important;
        padding: 15px;
    }

    /* Customizing Headings */
    h1, h2, h3 {
        color: #00d4ff !important;
        font-family: 'Inter', sans-serif;
    }

    /* Button Styling */
    .stButton>button {
        background-color: #007bff;
        color: white;
        border-radius: 8px;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        box-shadow: 0px 0px 15px rgba(0, 123, 255, 0.6);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. APPWRITE CONNECTION ---
# Note: Keep these secure if you ever share this app publicly!
APPWRITE_ENDPOINT = "https://fra.cloud.appwrite.io/v1"
APPWRITE_PROJECT_ID = "69caa235001a80451107"
APPWRITE_API_KEY = "standard_4be6add50fbb8e35010a8c86de7133f164e5839e2f55c172a5eaa642c4317c65d4bf4e4c998ab89cb7d5a5febe79775aa691a21791e6d082b1df53a8cdc7562745ab5c10701c7df7dc106e334c49e0ef4e557528350583fb2c9e680d4ced46b9c775386d8d1bbdaf0e5e180b712067158c09d89ac13866fa371ee6fe57741c8c"
DATABASE_ID = "69caa399001e100948dd"

client = Client()
client.set_endpoint(APPWRITE_ENDPOINT)
client.set_project(APPWRITE_PROJECT_ID)
client.set_key(APPWRITE_API_KEY)
db = Databases(client)

# --- 3. NAVIGATION ---
st.sidebar.markdown("# 🚀 SmartStock")
st.sidebar.markdown("---")
menu = st.sidebar.selectbox(
    "Select View", ["Inventory Hub", "Customer Churn", "Marketing ROI"])

# Helper function to make charts match the background


def style_chart(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="white",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig


# --- 4. MODULE: INVENTORY HUB ---
if menu == "Inventory Hub":
    st.title("📦 SmartStock Inventory")

    # Add Item Form
    with st.expander("➕ Register New Stock"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Item Name")
        with col2:
            stock = st.number_input("Current Quantity", min_value=0)

        if st.button("Add to Database"):
            db.create_document(DATABASE_ID, 'inventory', ID.unique(), {
                "item_name": name,
                "current_stock": int(stock)
            })
            st.success(f"Successfully added {name}!")
            st.rerun()

    # Fetch and Display Data
    try:
        response = db.list_documents(DATABASE_ID, 'inventory')
        df = pd.DataFrame([doc['data'] for doc in response['documents']])

        if not df.empty:
            st.subheader("Live Inventory Levels")
            st.dataframe(df, use_container_width=True)

            fig = px.bar(df, x="item_name", y="current_stock",
                         title="Stock Levels by Product",
                         color_discrete_sequence=['#00d4ff'])
            st.plotly_chart(style_chart(fig), use_container_width=True)
    except Exception as e:
        st.info("No data found. Add your first item to get started!")

# --- 5. MODULE: CUSTOMER CHURN ---
elif menu == "Customer Churn":
    st.title("📉 Churn Prediction")

    col1, col2 = st.columns([1, 2])
    with col1:
        name = st.text_input("Customer Name")
        eng = st.slider("Engagement Score", 0, 100, 70)

        if st.button("Calculate Risk"):
            risk = 100 - eng
            db.create_document(DATABASE_ID, 'customers', ID.unique(), {
                "customer_name": name,
                "churn_risk": risk
            })

            delta_val = "Low Risk" if risk < 40 else "High Risk"
            st.metric("Risk Score", f"{risk}%",
                      delta=delta_val, delta_color="inverse")

# --- 6. MODULE: MARKETING ROI ---
else:
    st.title("💰 Marketing ROI")
    st.info("This module tracks your Campaign Spend vs Revenue via Appwrite.")
    # Placeholder for ROI Logic
    st.write("Connect your marketing spend collection here to visualize performance.")
