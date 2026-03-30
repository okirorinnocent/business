import streamlit as st
import pandas as pd
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID
import plotly.express as px

# --- 1. APP CONFIG & UI STYLING ---
st.set_page_config(page_title="SmartStock Pro BI",
                   page_icon="📈", layout="wide")

# High-End "Cyber-Dark" Theme
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

# --- 3. HELPER FUNCTIONS ---


def apply_executive_style(fig):
    fig.update_traces(marker=dict(
        colors=['#00d4ff', '#007bff', '#90e0ef', '#002855']))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="#00d4ff",
        legend=dict(orientation="h", y=-0.1)
    )
    return fig


# --- 4. NAVIGATION ---
st.sidebar.title("🚀 SmartStock Pro")
st.sidebar.caption("AI-Driven Inventory Management")
menu = st.sidebar.selectbox("Dashboard", ["Inventory Hub", "Customer Churn"])

# --- 5. MODULE: INVENTORY HUB ---
if menu == "Inventory Hub":
    st.title("📊 Strategic Inventory Dashboard")

    # A. QUICK REGISTRATION
    with st.expander("➕ Register New Stock Asset"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input(
                "Product Name", placeholder="e.g. Server Rack")
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

    # B. DATA FETCH & PROCESSING
    try:
        result = db.list_documents(DB_ID, COLL_ID)
        # Handle the 'DocumentList' object vs Dict response
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

            # --- MARKET FEATURE 1: SEARCH & FILTER ---
            search = st.text_input("🔍 Search Assets...",
                                   placeholder="Type to filter table...")
            if search:
                df = df[df['item_name'].str.contains(search, case=False)]

            # --- MARKET FEATURE 2: PROACTIVE ALERTS ---
            LOW_THRESHOLD = 5
            low_stock_df = df[df['current_stock'] <= LOW_THRESHOLD]

            if not low_stock_df.empty:
                st.markdown(f"""
                <div class="low-stock-card">
                    <h4>⚠️ CRITICAL STOCK ALERT</h4>
                    <p>There are <b>{len(low_stock_df)}</b> items below the safety threshold of {LOW_THRESHOLD} units.</p>
                </div>
                """, unsafe_allow_html=True)

            # C. MAIN VISUALS
            col_metrics, col_chart = st.columns([1, 1])

            with col_metrics:
                st.subheader("Inventory Metrics")
                total_stock = df['current_stock'].sum()
                st.metric("Total Units Managed", f"{total_stock:,}")

                # Display Table
                st.dataframe(df, use_container_width=True, hide_index=True)

                # Management Tools
                with st.popover("🗑️ Bulk Delete / Edit"):
                    target = st.selectbox(
                        "Select Asset:", df['item_name'].tolist())
                    if st.button("Permanently Remove"):
                        idx = df[df['item_name'] == target].index[0]
                        db.delete_document(DB_ID, COLL_ID, item_ids[idx])
                        st.rerun()

            with col_chart:
                st.subheader("Asset Value Distribution")
                fig = px.pie(df, names="item_name",
                             values="current_stock", hole=0.5)
                st.plotly_chart(apply_executive_style(fig),
                                use_container_width=True)

                # --- MARKET FEATURE 3: AI FORECASTING (Simulated) ---
                st.subheader("🔮 7-Day Forecast")
                st.caption(
                    "AI prediction of stock exhaustion based on 2026 sales trends")
                # Creating a quick bar chart for predicted depletion
                # Assuming 1.5 sales/day
                df['Days Until Empty'] = (df['current_stock'] / 1.5).round(1)
                fig_forecast = px.bar(df, x='item_name', y='Days Until Empty', color='Days Until Empty',
                                      color_continuous_scale='Reds_r')
                st.plotly_chart(apply_executive_style(
                    fig_forecast), use_container_width=True)

        else:
            st.info("Database online. Awaiting first asset entry...")

    except Exception as e:
        st.error(f"Fetch Error: {e}")

# --- 6. MODULE: CUSTOMER CHURN ---
else:
    st.title("📉 Churn Prediction Engine")
    st.markdown("Analyze customer retention risks using engagement metrics.")

    c1, c2 = st.columns(2)
    with c1:
        eng = st.slider("Customer Engagement Level (%)", 0, 100, 75)
        ticket_count = st.number_input(
            "Support Tickets (Last 30 Days)", 0, 50, 2)

    with c2:
        # Simple AI logic: High tickets + Low engagement = High Churn
        churn_risk = (100 - eng) + (ticket_count * 5)
        churn_risk = min(churn_risk, 100)  # Cap at 100%

        st.metric("Churn Risk Score", f"{churn_risk}%",
                  delta="CRITICAL" if churn_risk > 70 else "STABLE",
                  delta_color="inverse")

    st.progress(churn_risk / 100)
