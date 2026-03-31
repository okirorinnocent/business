import streamlit as st
import pandas as pd
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID
import plotly.express as px
from datetime import datetime

# --- 1. APP CONFIG & UI STYLING ---
st.set_page_config(page_title="SmartStock Pro BI",
                   page_icon="📈", layout="wide")

# Custom CSS for a "Premium Night Mode" look
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #001f3f 0%, #000814 100%); color: white; }
    [data-testid="stMetric"] {
        background: rgba(0, 212, 255, 0.05);
        border: 1px solid #00d4ff;
        border-radius: 15px;
        padding: 15px;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #007bff, #00d4ff);
        color: white; border: none; font-weight: bold;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SECURE CONNECTION ---
try:
    client = Client()
    client.set_endpoint(st.secrets["APPWRITE_ENDPOINT"])
    client.set_project(st.secrets["APPWRITE_PROJECT_ID"])
    client.set_key(st.secrets["APPWRITE_API_KEY"])
    db = Databases(client)

    DB_ID = st.secrets["DATABASE_ID"]
    COLL_ID = st.secrets["INVENTORY_COLLECTION_ID"]
except Exception as e:
    st.error(f"⚠️ Connection Error: {e}")
    st.stop()

# --- 3. UI HELPER FUNCTIONS ---


def apply_executive_style(fig):
    """Adds a premium look to Plotly charts."""
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="#00d4ff",
        legend=dict(orientation="h", y=-0.1)
    )
    if fig.data[0].type != 'pie':
        fig.update_traces(marker_color='#00d4ff')
    return fig


# --- 4. NAVIGATION ---
st.sidebar.title("🚀 SmartStock Pro")
menu = st.sidebar.selectbox(
    "Navigate", ["Inventory Hub", "Stock Operations", "Customer Churn"])

# --- 5. MODULE: INVENTORY HUB (Dashboard) ---
if menu == "Inventory Hub":
    st.title("📊 Strategic Inventory Dashboard")

    try:
        # Fetch data from Appwrite
        result = db.list_documents(DB_ID, COLL_ID)
        df = pd.DataFrame([doc['data'] for doc in result['documents']])

        if not df.empty:
            # Layout: Metrics on top
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Assets", len(df))
            m2.metric("Total Units", f"{df['current_stock'].sum():,}")

            low_stock_count = len(df[df['current_stock'] <= 5])
            m3.metric("Low Stock Alerts", low_stock_count,
                      delta="- Critical" if low_stock_count > 0 else "Clear")

            # Charts Row
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Inventory Composition")
                fig_pie = px.pie(df, names="item_name",
                                 values="current_stock", hole=0.4)
                st.plotly_chart(apply_executive_style(
                    fig_pie), use_container_width=True)

            with c2:
                st.subheader("Current Stock Levels")
                fig_bar = px.bar(df, x="item_name", y="current_stock")
                st.plotly_chart(apply_executive_style(
                    fig_bar), use_container_width=True)

            # Data Table
            st.subheader("📝 Live Inventory Registry")
            st.dataframe(df[['item_name', 'current_stock']],
                         use_container_width=True)
        else:
            st.info(
                "Your warehouse is empty. Head to 'Stock Operations' to add items.")

    except Exception as e:
        st.error(f"Data Fetch Error: {e}")

# --- 6. MODULE: STOCK OPERATIONS (Add/Update/Delete) ---
elif menu == "Stock Operations":
    st.title("⚙️ Warehouse Operations")

    tab1, tab2, tab3 = st.tabs(
        ["🆕 Add New Item", "🔄 Update Stock", "🗑️ Remove Asset"])

    with tab1:
        st.subheader("Register New Product")
        with st.form("add_form"):
            new_name = st.text_input("Product Name")
            new_stock = st.number_input("Initial Quantity", min_value=0)
            if st.form_submit_button("Confirm Registration"):
                db.create_document(DB_ID, COLL_ID, ID.unique(), {
                                   "item_name": new_name, "current_stock": int(new_stock)})
                st.success(f"{new_name} added!")
                st.rerun()

    with tab2:
        st.subheader("Restock or Sale")
        result = db.list_documents(DB_ID, COLL_ID)
        items = {doc['item_name']: doc['$id'] for doc in result['documents']}
        current_vals = {doc['item_name']: doc['current_stock']
                        for doc in result['documents']}

        target_item = st.selectbox(
            "Select Product to Update", list(items.keys()))
        adjustment = st.number_input(
            "Adjustment (use negative for sales, positive for restock)", step=1)

        if st.button("Apply Changes"):
            new_total = current_vals[target_item] + adjustment
            db.update_document(DB_ID, COLL_ID, items[target_item], {
                               "current_stock": int(new_total)})
            st.success(f"Stock updated to {new_total}")
            st.rerun()

    with tab3:
        st.subheader("Danger Zone")
        target_del = st.selectbox(
            "Select Product to Delete Forever", list(items.keys()))
        if st.button("Permanently Delete"):
            db.delete_document(DB_ID, COLL_ID, items[target_del])
            st.warning("Item removed.")
            st.rerun()

# --- 7. MODULE: CUSTOMER CHURN ---
else:
    st.title("📉 Churn Prediction Engine")
    eng = st.slider("Engagement (%)", 0, 100, 75)
    risk = max(0, 100 - eng)
    st.metric("Churn Risk Score",
              f"{risk}%", delta="CRITICAL" if risk > 70 else "STABLE", delta_color="inverse")
    st.progress(risk / 100)
