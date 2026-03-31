import streamlit as st
import pandas as pd
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID
import plotly.express as px

# --- 1. SETTINGS & HIGH-CONTRAST THEME (ORIGINAL) ---
st.set_page_config(page_title="SmartStock Pro BI",
                   page_icon="📈", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000b1a; color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #001529; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    [data-testid="stMetric"] {
        background-color: #001f3f; 
        border: 2px solid #00f2fe; 
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 242, 254, 0.1);
    }
    [data-testid="stMetricLabel"] { color: #BBBBBB !important; font-weight: bold; }
    [data-testid="stMetricValue"] { color: #00f2fe !important; font-weight: 800; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #001f3f; border-radius: 4px; color: #FFFFFF; font-weight: bold; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #007bff; }
    .stButton>button { background: linear-gradient(90deg, #007bff, #00f2fe); color: #000000; font-weight: 900; border: none; }
    h1, h2, h3 { color: #FFFFFF !important; text-transform: uppercase; letter-spacing: 1px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE CONNECTION (FIXED WITH YOUR KEYS) ---
try:
    client = Client()
    client.set_endpoint("https://fra.cloud.appwrite.io/v1")
    client.set_project("69caa235001a80451107")
    client.set_key("standard_4be6add50fbb8e35010a8c86de7133f164e5839e2f55c172a5eaa642c4317c65d4bf4e4c998ab89cb7d5a5febe79775aa691a21791e6d082b1df53a8cdc7562745ab5c10701c7df7dc106e334c49e0ef4e557528350583fb2c9e680d4ced46b9c775386d8d1bbdaf0e5e180b712067158c09d89ac13866fa371ee6fe57741c8c")
    db = Databases(client)

    DB_ID = "69caa399001e100948dd"
    COLL_ID = "69cace6f0013b2a6aace"
except Exception as e:
    st.error(f"❌ Configuration Error: {e}")
    st.stop()

# --- 3. CHART HELPER (ORIGINAL) ---


def apply_clean_style(fig, chart_type="bar"):
    if chart_type == "pie":
        fig.update_traces(marker=dict(
            colors=['#00f2fe', '#4facfe', '#a1c4fd', '#c2e9fb']))
    else:
        fig.update_traces(marker_color='#00f2fe')
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color="#FFFFFF", font_size=12,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)')
    )
    return fig


# --- 4. NAVIGATION (ORIGINAL) ---
st.sidebar.title("🚀 SmartStock Pro")
page = st.sidebar.radio(
    "Navigate", ["Business Dashboard", "Inventory Control", "Customer Churn"])

# --- 5. PAGE: BUSINESS DASHBOARD (ORIGINAL LOGIC + SAFETY) ---
if page == "Business Dashboard":
    st.title("📊 Executive Overview")
    try:
        result = db.list_documents(DB_ID, COLL_ID)
        raw_docs = result.documents
        if raw_docs:
            df = pd.DataFrame([d.data for d in raw_docs])

            # Crash Fix: Ensure stock is numeric
            df['current_stock'] = pd.to_numeric(
                df['current_stock'], errors='coerce').fillna(0)

            m1, m2, m3 = st.columns(3)
            m1.metric("Total SKU Count", len(df))
            m2.metric("Total Units in Warehouse",
                      f"{int(df['current_stock'].sum()):,}")

            low_stock_df = df[df['current_stock'] <= 5]
            m3.metric("Low Stock Alerts", len(low_stock_df),
                      delta=f"- Critical" if not low_stock_df.empty else "Optimal",
                      delta_color="inverse")

            st.write("---")
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Inventory Distribution")
                fig_pie = px.pie(df, names="item_name",
                                 values="current_stock", hole=0.6)
                st.plotly_chart(apply_clean_style(
                    fig_pie, "pie"), use_container_width=True)
            with c2:
                st.subheader("Stock Levels by Asset")
                fig_bar = px.bar(df, x="item_name", y="current_stock")
                st.plotly_chart(apply_clean_style(
                    fig_bar, "bar"), use_container_width=True)

            st.write("---")
            st.subheader("📋 Detailed Inventory Log")
            st.dataframe(df[['item_name', 'current_stock']],
                         use_container_width=True, hide_index=True)
        else:
            st.info("No data available. Please add items in 'Inventory Control'.")
    except Exception as e:
        st.error(f"Data Sync Error: {e}")

# --- 6. PAGE: INVENTORY CONTROL (ORIGINAL LOGIC) ---
elif page == "Inventory Control":
    st.title("⚙️ Warehouse Operations")
    tab1, tab2, tab3 = st.tabs(
        ["🆕 Register Item", "🔄 Update Quantity", "🗑️ Remove Asset"])

    # Fetch data for dropdowns
    try:
        result = db.list_documents(DB_ID, COLL_ID)
        items_list = {d.data['item_name']: d.id for d in result.documents}
        stock_values = {d.data['item_name']: d.data['current_stock']
                        for d in result.documents}
    except:
        items_list = {}

    with tab1:
        st.subheader("Add New Product SKU")
        with st.form("new_item_form"):
            new_name = st.text_input("Product Name")
            new_qty = st.number_input("Starting Quantity", min_value=0, step=1)
            if st.form_submit_button("Deploy to Cloud Database"):
                if new_name:
                    db.create_document(DB_ID, COLL_ID, ID.unique(), {
                                       "item_name": new_name, "current_stock": int(new_qty)})
                    st.success(f"Added {new_name}")
                    st.rerun()

    with tab2:
        st.subheader("Adjust Inventory Levels")
        if items_list:
            target = st.selectbox("Select Item to Update",
                                  list(items_list.keys()))
            current_val = stock_values[target]
            st.info(f"Current Stock: {current_val}")
            change = st.number_input("Adjustment (+/-)", step=1)
            if st.button("Apply Stock Adjustment"):
                new_total = current_val + change
                if new_total >= 0:
                    db.update_document(DB_ID, COLL_ID, items_list[target], {
                                       "current_stock": int(new_total)})
                    st.success("Updated!")
                    st.rerun()
                else:
                    st.error("Cannot go below zero.")
        else:
            st.warning("No items found.")

    with tab3:
        st.subheader("Danger Zone")
        if items_list:
            to_delete = st.selectbox(
                "Select Item to Delete Forever", list(items_list.keys()))
            if st.button("Confirm Permanent Deletion"):
                db.delete_document(DB_ID, COLL_ID, items_list[to_delete])
                st.rerun()

# --- 7. PAGE: CUSTOMER CHURN (ORIGINAL LOGIC) ---
else:
    st.title("📉 Churn Prediction Engine")
    engagement = st.slider("User Engagement Score (%)", 0, 100, 80)
    risk_score = 100 - engagement
    st.write("---")
    c1, c2 = st.columns([1, 2])
    with c1:
        st.metric("Risk Level", f"{risk_score}%", delta="CRITICAL" if risk_score >
                  60 else "HEALTHY", delta_color="inverse")
    with c2:
        st.progress(risk_score / 100)
    if risk_score > 60:
        st.error("⚠️ High Priority: Schedule call immediately.")
    else:
        st.success("✅ Customer is stable.")
