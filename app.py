import streamlit as st
import pandas as pd
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID
import plotly.express as px

# --- 1. SETTINGS & HIGH-CONTRAST THEME ---
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
    }
    [data-testid="stMetricValue"] { color: #00f2fe !important; font-weight: 800; }
    .stButton>button {
        background: linear-gradient(90deg, #007bff, #00f2fe);
        color: #000000; font-weight: 900; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DIRECT DATABASE CONNECTION (NO SECRETS FILE NEEDED) ---
# I have embedded your keys here so the app doesn't have to look for a file
try:
    client = Client()
    client.set_endpoint("https://fra.cloud.appwrite.io/v1")
    client.set_project("69caa235001a80451107")
    client.set_key("standard_4be6add50fbb8e35010a8c86de7133f164e5839e2f55c172a5eaa642c4317c65d4bf4e4c998ab89cb7d5a5febe79775aa691a21791e6d082b1df53a8cdc7562745ab5c10701c7df7dc106e334c49e0ef4e557528350583fb2c9e680d4ced46b9c775386d8d1bbdaf0e5e180b712067158c09d89ac13866fa371ee6fe57741c8c")
    db = Databases(client)

    DB_ID = "69caa399001e100948dd"
    COLL_ID = "69cace6f0013b2a6aace"
except Exception as e:
    st.error(f"❌ Connection Error: {e}")
    st.stop()

# --- 3. CHART HELPER ---


def apply_clean_style(fig, chart_type="bar"):
    if chart_type == "pie":
        fig.update_traces(marker=dict(
            colors=['#00f2fe', '#4facfe', '#a1c4fd', '#c2e9fb']))
    else:
        fig.update_traces(marker_color='#00f2fe')
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color="#FFFFFF", font_size=12, margin=dict(l=10, r=10, t=30, b=10)
    )
    return fig


# --- 4. NAVIGATION ---
st.sidebar.title("🚀 SmartStock Pro")
page = st.sidebar.radio(
    "Navigate", ["Business Dashboard", "Inventory Control", "Customer Churn"])

# --- 5. PAGE: BUSINESS DASHBOARD ---
if page == "Business Dashboard":
    st.title("📊 Executive Overview")
    try:
        result = db.list_documents(DB_ID, COLL_ID)
        df = pd.DataFrame([d.data for d in result.documents])
        if not df.empty:
            m1, m2, m3 = st.columns(3)
            m1.metric("Total SKU Count", len(df))
            m2.metric("Total Units", f"{df['current_stock'].sum():,}")
            m3.metric("Low Stock Alerts", len(df[df['current_stock'] <= 5]))

            st.write("---")
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Inventory Distribution")
                st.plotly_chart(apply_clean_style(px.pie(
                    df, names="item_name", values="current_stock", hole=0.6), "pie"), use_container_width=True)
            with c2:
                st.subheader("Stock Levels")
                st.plotly_chart(apply_clean_style(
                    px.bar(df, x="item_name", y="current_stock")), use_container_width=True)
        else:
            st.info("No data found in Appwrite.")
    except Exception as e:
        st.error(f"Data Sync Error: {e}")

# --- 6. PAGE: INVENTORY CONTROL ---
elif page == "Inventory Control":
    st.title("⚙️ Warehouse Operations")
    tab1, tab2 = st.tabs(["🆕 Register Item", "🔄 Update Quantity"])

    with tab1:
        with st.form("new_item"):
            name = st.text_input("Product Name")
            qty = st.number_input("Starting Quantity", min_value=0)
            if st.form_submit_button("Add to Database"):
                db.create_document(DB_ID, COLL_ID, ID.unique(), {
                                   "item_name": name, "current_stock": int(qty)})
                st.success("Added!")
                st.rerun()

    with tab2:
        result = db.list_documents(DB_ID, COLL_ID)
        items = {d.data['item_name']: d.id for d in result.documents}
        if items:
            target = st.selectbox("Select Item", list(items.keys()))
            change = st.number_input("Adjustment (+/-)", step=1)
            if st.button("Update"):
                # Get current stock first
                doc = db.get_document(DB_ID, COLL_ID, items[target])
                new_val = doc.data['current_stock'] + change
                db.update_document(DB_ID, COLL_ID, items[target], {
                                   "current_stock": int(new_val)})
                st.success("Updated!")
                st.rerun()

# --- 7. PAGE: CHURN ---
else:
    st.title("📉 Churn Prediction")
    score = st.slider("Engagement %", 0, 100, 80)
    st.metric("Risk", f"{100-score}%")
