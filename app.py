import streamlit as st
import pandas as pd
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID
import plotly.express as px

# --- 1. SETTINGS & THEME ---
st.set_page_config(page_title="SmartStock Pro BI",
                   page_icon="📈", layout="wide")

# Modern Dark UI Styling
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #001f3f 0%, #000814 100%); color: white; }
    [data-testid="stMetric"] {
        background: rgba(0, 212, 255, 0.1);
        border: 1px solid #00d4ff;
        border-radius: 15px;
        padding: 15px;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: rgba(255,255,255,0.05);
        border-radius: 5px; color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE CONNECTION ---
try:
    client = Client()
    client.set_endpoint(st.secrets["APPWRITE_ENDPOINT"])
    client.set_project(st.secrets["APPWRITE_PROJECT_ID"])
    client.set_key(st.secrets["APPWRITE_API_KEY"])
    db = Databases(client)

    DB_ID = st.secrets["DATABASE_ID"]
    COLL_ID = st.secrets["INVENTORY_COLLECTION_ID"]
except Exception as e:
    st.error(f"❌ Configuration Error: {e}")
    st.stop()

# --- 3. CHART STYLING HELPER ---


def apply_pro_style(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="#00d4ff",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig


# --- 4. NAVIGATION SIDEBAR ---
st.sidebar.title("🚀 SmartStock Pro")
page = st.sidebar.radio(
    "Navigate", ["Business Dashboard", "Inventory Control", "Customer Churn"])

# --- 5. PAGE: BUSINESS DASHBOARD ---
if page == "Business Dashboard":
    st.title("📊 Executive Overview")

    try:
        # Fetch data using .documents (Object Style)
        result = db.list_documents(DB_ID, COLL_ID)
        raw_docs = result.documents

        if raw_docs:
            # Prepare data for analytics
            df = pd.DataFrame([d.data for d in raw_docs])

            # KPI Metrics
            m1, m2, m3 = st.columns(3)
            m1.metric("Total SKU Count", len(df))
            total_stock = df['current_stock'].sum()
            m2.metric("Total Units in Warehouse", f"{total_stock:,}")

            low_stock = len(df[df['current_stock'] <= 5])
            m3.metric("Low Stock Alerts", low_stock,
                      delta="- Urgent" if low_stock > 0 else "Optimal")

            # Visual Analytics
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Inventory Distribution")
                fig_pie = px.pie(df, names="item_name",
                                 values="current_stock", hole=0.5)
                st.plotly_chart(apply_pro_style(fig_pie),
                                use_container_width=True)

            with c2:
                st.subheader("Stock Levels by Asset")
                fig_bar = px.bar(df, x="item_name", y="current_stock",
                                 color_discrete_sequence=['#00d4ff'])
                st.plotly_chart(apply_pro_style(fig_bar),
                                use_container_width=True)

            st.subheader("📋 Detailed Inventory Log")
            st.dataframe(df[['item_name', 'current_stock']],
                         use_container_width=True, hide_index=True)

        else:
            st.info("No data available. Please add items in Inventory Control.")

    except Exception as e:
        st.error(f"Data Sync Error: {e}")

# --- 6. PAGE: INVENTORY CONTROL ---
elif page == "Inventory Control":
    st.title("⚙️ Warehouse Operations")

    # Organize operations into Tabs
    tab1, tab2, tab3 = st.tabs(
        ["🆕 Register Item", "🔄 Update Quantity", "🗑️ Remove Asset"])

    # Fetch fresh list of items for dropdowns
    result = db.list_documents(DB_ID, COLL_ID)
    items_list = {d.data['item_name']: d.id for d in result.documents}
    stock_values = {d.data['item_name']: d.data['current_stock']
                    for d in result.documents}

    with tab1:
        with st.form("new_item_form"):
            new_name = st.text_input("Product Name")
            new_qty = st.number_input("Starting Quantity", min_value=0)
            if st.form_submit_button("Deploy to Cloud"):
                if new_name:
                    db.create_document(DB_ID, COLL_ID, ID.unique(), {
                                       "item_name": new_name, "current_stock": int(new_qty)})
                    st.success(f"Successfully added {new_name}")
                    st.rerun()

    with tab2:
        if items_list:
            target = st.selectbox("Select Item to Update",
                                  list(items_list.keys()))
            change = st.number_input(
                "Adjustment (+ for restock, - for sales)", step=1)
            if st.button("Apply Stock Adjustment"):
                new_total = stock_values[target] + change
                db.update_document(DB_ID, COLL_ID, items_list[target], {
                                   "current_stock": int(new_total)})
                st.success(f"Updated {target} to {new_total} units")
                st.rerun()
        else:
            st.warning("No items found to update.")

    with tab3:
        if items_list:
            to_delete = st.selectbox("Select Item to Delete", list(
                items_list.keys()), key="del_box")
            if st.button("Confirm Permanent Deletion"):
                db.delete_document(DB_ID, COLL_ID, items_list[to_delete])
                st.warning(f"Deleted {to_delete}")
                st.rerun()

# --- 7. PAGE: CUSTOMER CHURN ---
else:
    st.title("📉 Churn Prediction Engine")
    st.write("Analyze customer retention risk based on engagement metrics.")

    engagement = st.slider("User Engagement Score (%)", 0, 100, 80)
    risk_score = 100 - engagement

    c1, c2 = st.columns([1, 2])
    with c1:
        st.metric("Risk Level", f"{risk_score}%",
                  delta="CRITICAL" if risk_score > 60 else "HEALTHY",
                  delta_color="inverse")
    with c2:
        st.progress(risk_score / 100)

    if risk_score > 60:
        st.error("High Priority: Schedule customer success call immediately.")
    else:
        st.success("Customer is stable and engaged.")
