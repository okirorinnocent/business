import streamlit as st
import pandas as pd
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID
import plotly.express as px

# --- 1. APP CONFIG & HIGH-END STYLING ---
st.set_page_config(page_title="SmartStock BI", page_icon="📊", layout="wide")

# Modern Dark Theme with Glassmorphism
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #001f3f 0%, #000814 100%);
        color: white;
    }
    section[data-testid="stSidebar"] {
        background-color: #000814 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    [data-testid="stMetric"], .stExpander, .stDataFrame {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(12px);
        border-radius: 15px !important;
    }
    h1, h2, h3 { color: #00d4ff !important; }
    .stButton>button {
        width: 100%;
        background-color: #007bff;
        color: white;
        border-radius: 8px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        box-shadow: 0px 0px 15px rgba(0, 123, 255, 0.5);
    }
    /* Simple fix for dark mode dataframes */
    .stDataFrame div[data-testid="stTable"] {
        background-color: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SECURE CONNECTION (Using Streamlit Secrets) ---
try:
    APPWRITE_ENDPOINT = st.secrets["APPWRITE_ENDPOINT"]
    APPWRITE_PROJECT_ID = st.secrets["APPWRITE_PROJECT_ID"]
    APPWRITE_API_KEY = st.secrets["APPWRITE_API_KEY"]
    DATABASE_ID = st.secrets["DATABASE_ID"]
    INVENTORY_COLLECTION_ID = st.secrets["INVENTORY_COLLECTION_ID"]

    client = Client()
    client.set_endpoint(APPWRITE_ENDPOINT)
    client.set_project(APPWRITE_PROJECT_ID)
    client.set_key(APPWRITE_API_KEY)
    db = Databases(client)
except Exception as e:
    st.error(
        "Missing Credentials! Please add your Appwrite keys to Streamlit Secrets.")
    st.stop()

# --- 3. HELPER FUNCTIONS ---


def apply_chart_style(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="white",
        margin=dict(l=10, r=10, t=40, b=10)
    )
    return fig


# --- 4. SIDEBAR NAVIGATION ---
st.sidebar.title("🚀 SmartStock")
st.sidebar.markdown("---")
menu = st.sidebar.selectbox(
    "Dashboard", ["Inventory Hub", "Customer Churn", "Marketing ROI"])

# --- 5. MODULE: INVENTORY HUB ---
if menu == "Inventory Hub":
    st.title("📦 SmartStock Inventory")

    # Registration Form
    with st.expander("➕ Register New Stock Item"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Item Name", placeholder="e.g. Laptop")
        with c2:
            stock = st.number_input("Quantity", min_value=0, step=1)

        if st.button("Add to Appwrite"):
            if name:
                try:
                    db.create_document(DATABASE_ID, INVENTORY_COLLECTION_ID, ID.unique(), {
                        "item_name": name,
                        "current_stock": int(stock)
                    })
                    st.success(f"✅ {name} added!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Appwrite Error: {e}")
            else:
                st.warning("Please enter an item name.")

    # Data Display & Visualization
    try:
        response = db.list_documents(DATABASE_ID, INVENTORY_COLLECTION_ID)
        docs = response['documents']

        if docs:
            items = [doc['data'] for doc in docs]
            ids = [doc['$id'] for doc in docs]
            df = pd.DataFrame(items)

            col_left, col_right = st.columns([1.2, 1])

            with col_left:
                st.subheader("Live Inventory")
                st.dataframe(df, use_container_width=True, hide_index=True)

                # Deletion logic
                with st.popover("🗑️ Manage Inventory"):
                    to_delete = st.selectbox(
                        "Select item to remove:", df['item_name'].tolist())
                    if st.button("Confirm Delete"):
                        idx = df[df['item_name'] == to_delete].index[0]
                        db.delete_document(
                            DATABASE_ID, INVENTORY_COLLECTION_ID, ids[idx])
                        st.rerun()

            with col_right:
                st.subheader("Stock Distribution")
                fig = px.pie(df, names="item_name", values="current_stock",
                             hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r)
                st.plotly_chart(apply_chart_style(
                    fig), use_container_width=True)
        else:
            st.info("The database is currently empty.")
    except Exception as e:
        st.error(f"Fetch Error: {e}")

# --- 6. MODULE: CUSTOMER CHURN ---
elif menu == "Customer Churn":
    st.title("📉 Churn Prediction")
    st.markdown("Assess customer health and save results to Appwrite.")

    with st.container():
        cust_name = st.text_input("Customer Name")
        engagement = st.slider("Engagement Level (%)", 0, 100, 50)

        if st.button("Predict Churn Risk"):
            risk_score = 100 - engagement
            status = "High Risk" if risk_score > 60 else "Healthy"
            st.metric(label="Calculated Risk",
                      value=f"{risk_score}%", delta=status, delta_color="inverse")

# --- 7. MODULE: MARKETING ROI ---
else:
    st.title("💰 Marketing ROI")
    st.info("This module is ready for your Marketing Spend data collection.")
