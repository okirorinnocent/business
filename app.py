import streamlit as st
import pandas as pd
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID
import plotly.express as px

# --- 1. SETTINGS & HIGH-CONTRAST THEME ---
st.set_page_config(page_title="SmartStock Pro BI",
                   page_icon="📈", layout="wide")

# High-Visibility, Clean Dark Theme (Optimized for Readability)
st.markdown("""
    <style>
    /* 1. Main Background: Clean, Solid Midnight Blue (No distracting gradients) */
    .stApp {
        background-color: #000b1a;
        color: #FFFFFF; /* High-contrast Pure White text by default */
    }

    /* 2. Sidebar: Slightly lighter for definition, keeping text sharp */
    [data-testid="stSidebar"] {
        background-color: #001529;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }

    /* 3. Metric Cards: Darker box with sharp 'Electric Cyan' borders and text */
    [data-testid="stMetric"] {
        background-color: #001f3f; /* Deep blue card */
        border: 2px solid #00f2fe; /* Glowing Cyan border */
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 242, 254, 0.1);
    }
    /* Metric Label (e.g., "Total SKU Count") */
    [data-testid="stMetricLabel"] {
        color: #BBBBBB !important;
        font-weight: bold;
    }
    /* Metric Value (e.g., "5,000") */
    [data-testid="stMetricValue"] {
        color: #00f2fe !important; /* Vivid Cyan for the main number */
        font-weight: 800;
    }

    /* 4. Tabs & Buttons: Bright Blue for clear interaction */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #001f3f;
        border-radius: 4px;
        color: #FFFFFF;
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #007bff; /* Bright Blue when active */
    }

    /* 5. Generic Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #007bff, #00f2fe);
        color: #000000; /* Dark text on bright button for contrast */
        font-weight: 900;
        border: none;
    }
    
    /* 6. Titles & Subheaders */
    h1, h2, h3 {
        color: #FFFFFF !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE CONNECTION (RETAINED) ---
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

# --- 3. HIGH-VISIBILITY CHART HELPER ---


def apply_clean_style(fig, chart_type="bar"):
    # Define a high-contrast color palette
    if chart_type == "pie":
        # Use a distinct, bright color sequence for pie slices
        fig.update_traces(marker=dict(
            colors=['#00f2fe', '#4facfe', '#a1c4fd', '#c2e9fb']))
    else:
        # Solid Electric Cyan for bars
        fig.update_traces(marker_color='#00f2fe')

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent chart area
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="#FFFFFF",          # Pure White labels
        font_size=12,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),  # Subtle grid
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)')
    )
    return fig


# --- 4. NAVIGATION SIDEBAR (RETAINED) ---
st.sidebar.title("🚀 SmartStock Pro")
page = st.sidebar.radio(
    "Navigate", ["Business Dashboard", "Inventory Control", "Customer Churn"])

# --- 5. PAGE: BUSINESS DASHBOARD (RETAINED LOGIC) ---
if page == "Business Dashboard":
    st.title("📊 Executive Overview")

    try:
        result = db.list_documents(DB_ID, COLL_ID)
        raw_docs = result.documents

        if raw_docs:
            df = pd.DataFrame([d.data for d in raw_docs])

            # KPI Metrics: Floating on the clean background
            m1, m2, m3 = st.columns(3)
            m1.metric("Total SKU Count", len(df))

            total_stock = df['current_stock'].sum()
            m2.metric("Total Units in Warehouse", f"{total_stock:,}")

            low_stock_threshold = 5
            low_stock_df = df[df['current_stock'] <= low_stock_threshold]
            m3.metric("Low Stock Alerts", len(low_stock_df),
                      delta=f"- Critical" if not low_stock_df.empty else "Optimal",
                      delta_color="inverse")

            # Visual Analytics: Distinct columns
            st.write("---")  # Visual separator
            c1, c2 = st.columns(2)

            with c1:
                st.subheader("Inventory Distribution")
                # Updated chart styling function
                fig_pie = px.pie(df, names="item_name",
                                 values="current_stock", hole=0.6)
                st.plotly_chart(apply_clean_style(
                    fig_pie, "pie"), use_container_width=True)

            with c2:
                st.subheader("Stock Levels by Asset")
                # Updated chart styling function
                fig_bar = px.bar(df, x="item_name", y="current_stock")
                st.plotly_chart(apply_clean_style(
                    fig_bar, "bar"), use_container_width=True)

            # Data Table: Simplified styling for maximum clarity
            st.write("---")
            st.subheader("📋 Detailed Inventory Log")
            st.dataframe(df[['item_name', 'current_stock']],
                         use_container_width=True,
                         hide_index=True)

        else:
            st.info("No data available. Please add items in 'Inventory Control'.")

    except Exception as e:
        st.error(f"Data Sync Error: {e}")

# --- 6. PAGE: INVENTORY CONTROL (RETAINED LOGIC) ---
elif page == "Inventory Control":
    st.title("⚙️ Warehouse Operations")

    # Use standard Streamlit columns and forms for better readability
    tab1, tab2, tab3 = st.tabs(
        ["🆕 Register Item", "🔄 Update Quantity", "🗑️ Remove Asset"])

    # Fetch fresh list of items for dropdowns
    result = db.list_documents(DB_ID, COLL_ID)
    items_list = {d.data['item_name']: d.id for d in result.documents}
    stock_values = {d.data['item_name']: d.data['current_stock']
                    for d in result.documents}

    with tab1:
        st.subheader("Add New Product SKU")
        with st.form("new_item_form"):
            new_name = st.text_input("Product Name (e.g., 'MacBook Pro')")
            new_qty = st.number_input("Starting Quantity", min_value=0, step=1)
            st.write("---")
            if st.form_submit_button("Deploy to Cloud Database"):
                if new_name:
                    try:
                        db.create_document(DB_ID, COLL_ID, ID.unique(), {
                                           "item_name": new_name, "current_stock": int(new_qty)})
                        st.success(f"Successfully added {new_name}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    with tab2:
        st.subheader("Adjust Inventory Levels")
        if items_list:
            target = st.selectbox("Select Item to Update",
                                  list(items_list.keys()))
            current_val = stock_values[target]
            st.info(f"Current Stock: {current_val} units")

            change = st.number_input(
                "Adjustment Quantity (use '+' for restock, '-' for sales)", step=1)
            st.write("---")
            if st.button("Apply Stock Adjustment"):
                new_total = current_val + change
                if new_total < 0:
                    st.error("Error: Cannot adjust stock below zero.")
                else:
                    try:
                        db.update_document(DB_ID, COLL_ID, items_list[target], {
                                           "current_stock": int(new_total)})
                        st.success(f"Updated {target} to {new_total} units")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.warning("No items found to update. Register items first.")

    with tab3:
        st.subheader("Danger Zone")
        if items_list:
            to_delete = st.selectbox("Select Item to Delete Forever", list(
                items_list.keys()), key="del_box")
            st.write("---")
            st.warning(
                f"Warning: This will permanently remove '{to_delete}' from the database.")
            if st.button("Confirm Permanent Deletion"):
                try:
                    db.delete_document(DB_ID, COLL_ID, items_list[to_delete])
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("No items found to delete.")

# --- 7. PAGE: CUSTOMER CHURN (RETAINED LOGIC) ---
else:
    st.title("📉 Churn Prediction Engine")
    st.write("Analyze customer retention risk based on engagement metrics.")

    # Simple, high-contrast inputs
    engagement = st.slider("User Engagement Score (%)", 0, 100, 80)
    risk_score = 100 - engagement

    st.write("---")

    c1, c2 = st.columns([1, 2])
    with c1:
        st.metric("Risk Level", f"{risk_score}%",
                  delta="CRITICAL" if risk_score > 60 else "HEALTHY",
                  delta_color="inverse")
    with c2:
        # Progress bar is white/cyan on dark background
        st.progress(risk_score / 100)

    if risk_score > 60:
        st.error("⚠️ High Priority: Schedule customer success call immediately.")
    else:
        st.success("✅ Customer is stable and engaged.")
