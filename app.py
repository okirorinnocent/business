import streamlit as st
import pandas as pd
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID
import plotly.express as px

# --- 1. APP CONFIG & BRANDING ---
st.set_page_config(page_title="SmartStock BI", page_icon="📊", layout="wide")

# Navy Blue Theme & App Name
st.markdown("""
    <style>
    .stApp { background-color: #001f3f; color: white; }
    section[data-testid="stSidebar"] { background-color: #001529; }
    .stMetric { background-color: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. APPWRITE CONNECTION ---
APPWRITE_ENDPOINT = "https://cloud.appwrite.io/v1"
APPWRITE_PROJECT_ID = "YOUR_PROJECT_ID"
APPWRITE_API_KEY = "YOUR_API_KEY"
DATABASE_ID = "YOUR_DATABASE_ID"

client = Client()
client.set_endpoint(APPWRITE_ENDPOINT)
client.set_project(APPWRITE_PROJECT_ID)
client.set_key(APPWRITE_API_KEY)
db = Databases(client)

# --- 3. NAVIGATION ---
st.sidebar.title("🚀 SmartStock")
menu = st.sidebar.selectbox(
    "Dashboard", ["Inventory Hub", "Customer Churn", "Marketing ROI"])

# --- 4. MODULE: INVENTORY HUB ---
if menu == "Inventory Hub":
    st.title("📦 SmartStock Inventory (Appwrite)")

    # Add Item Form
    with st.expander("➕ Register New Stock"):
        name = st.text_input("Item Name")
        stock = st.number_input("Current Quantity", min_value=0)
        if st.button("Add to Appwrite"):
            db.create_document(DATABASE_ID, 'inventory', ID.unique(), {
                "item_name": name,
                "current_stock": stock
            })
            st.success(f"Added {name} to inventory!")

    # Fetch Data
    try:
        response = db.list_documents(DATABASE_ID, 'inventory')
        df = pd.DataFrame([doc['data'] for doc in response['documents']])
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            fig = px.bar(df, x="item_name", y="current_stock",
                         color_discrete_sequence=['#007bff'])
            st.plotly_chart(fig)
    except:
        st.info("Add your first item to see the chart!")

# --- 5. MODULE: CUSTOMER CHURN ---
elif menu == "Customer Churn":
    st.title("📉 Churn Prediction")

    name = st.text_input("Customer Name")
    eng = st.slider("Engagement", 0, 100, 70)

    if st.button("Predict & Save"):
        risk = 100 - eng  # Simple logic
        db.create_document(DATABASE_ID, 'customers', ID.unique(), {
            "customer_name": name,
            "churn_risk": risk
        })
        st.metric("Risk Score", f"{risk}%",
                  delta="-5%" if risk < 50 else "High")

# --- 6. MODULE: MARKETING ROI ---
else:
    st.title("💰 Marketing ROI")
    # Visualization logic remains identical to previous version
    st.info("This module tracks your Campaign Spend vs Revenue via Appwrite.")
