import streamlit as st
import pandas as pd
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID
import plotly.express as px

# --- 1. APP CONFIG & UI STYLING ---
st.set_page_config(page_title="SmartStock Pro BI",
                   page_icon="📈", layout="wide")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #001f3f 0%, #000814 100%); color: white; }
    [data-testid="stMetric"] {
        background: rgba(0, 212, 255, 0.05);
        border: 1px solid #00d4ff;
        border-radius: 15px;
        padding: 15px;
    }
    .low-stock-card {
        padding: 20px;
        background: rgba(255, 75, 75, 0.1);
        border-left: 5px solid #ff4b4b;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #007bff, #00d4ff);
        color: white; border: none; font-weight: bold;
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

# --- 3. FIXED HELPER FUNCTION ---


def apply_executive_style(fig):
    # This color palette makes the app look premium
    premium_colors = ['#00d4ff', '#007bff', '#90e0ef', '#002855']

    # Check if the chart is a Pie chart or Bar chart to avoid the 'marker' error
    if hasattr(fig, 'data') and len(fig.data) > 0:
        if fig.data[0].type == 'pie':
            fig.update_traces(marker=dict(colors=premium_colors))
        else:
            # For Bar charts, we use a slightly different approach
            fig.update_traces(marker_color='#00d4ff')

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="#00d4ff",
        legend=dict(orientation="h", y=-0.1)
    )
    return fig


# --- 4. NAVIGATION ---
st.sidebar.title("🚀 SmartStock Pro")
menu = st.sidebar.selectbox("Dashboard", ["Inventory Hub", "Customer Churn"])

# --- 5. MODULE: INVENTORY HUB ---
if menu == "Inventory Hub":
    st.title("📊 Strategic Inventory Dashboard")

    with st.expander("➕ Register New Stock Asset"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Product Name")
        with c2:
            stock = st.number_input("Initial Quantity", min_value=0, step=1)

        if st.button("Deploy to Database"):
            if name:
                try:
                    db.create_document(DB_ID, COLL_ID, ID.unique(), {
                        "item_name": name,
                        "current_stock": int(stock)
                    })
                    st.success("Asset Registered Successfully")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    try:
        result = db.list_documents(DB_ID, COLL_ID)
        all_docs = getattr(result, 'documents', [])

        if all_docs:
            items_data = []
            item_ids = []
            for doc in all_docs:
                d = getattr(doc, 'data', {})
                d_id = getattr(doc, '$id', getattr(doc, 'id', None))
                if d:
                    items_data.append(d)
                    item_ids.append(d_id)

            df = pd.DataFrame(items_data)

            # SEARCH FILTER
            search = st.text_input("🔍 Search Assets...")
            if search:
                df = df[df['item_name'].str.contains(search, case=False)]

            # LOW STOCK ALERTS
            LOW_THRESHOLD = 5
            low_stock_df = df[df['current_stock'] <= LOW_THRESHOLD]
            if not low_stock_df.empty:
                st.warning(f"⚠️ {len(low_stock_df)} items are low on stock!")

            col_metrics, col_chart = st.columns([1, 1])

            with col_metrics:
                st.subheader("Inventory Metrics")
                st.metric("Total Units", f"{df['current_stock'].sum():,}")
                st.dataframe(df, use_container_width=True, hide_index=True)

                with st.popover("🗑️ Manage"):
                    target = st.selectbox(
                        "Select Asset:", df['item_name'].tolist())
                    if st.button("Delete"):
                        idx = df[df['item_name'] == target].index[0]
                        db.delete_document(DB_ID, COLL_ID, item_ids[idx])
                        st.rerun()

            with col_chart:
                st.subheader("Stock Mix")
                fig_pie = px.pie(df, names="item_name",
                                 values="current_stock", hole=0.5)
                st.plotly_chart(apply_executive_style(
                    fig_pie), use_container_width=True)

                st.subheader("🔮 7-Day Exhaustion Forecast")
                df['Days Until Empty'] = (df['current_stock'] / 1.5).round(1)
                fig_bar = px.bar(df, x='item_name', y='Days Until Empty')
                st.plotly_chart(apply_executive_style(
                    fig_bar), use_container_width=True)

        else:
            st.info("No data found.")

    except Exception as e:
        st.error(f"Fetch Error: {e}")

# --- 6. MODULE: CUSTOMER CHURN ---
else:
    st.title("📉 Churn Prediction Engine")
    eng = st.slider("Engagement (%)", 0, 100, 75)
    risk = max(0, 100 - eng)
    st.metric("Churn Risk Score",
              f"{risk}%", delta="CRITICAL" if risk > 70 else "STABLE", delta_color="inverse")
    st.progress(risk / 100)
