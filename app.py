import streamlit as st
import pandas as pd
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID
import plotly.express as px

# --- 1. APP CONFIG & HIGH-END STYLING ---
st.set_page_config(page_title="SmartStock BI", page_icon="📊", layout="wide")

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
    [data-testid="stMetric"], .stExpander, [data-testid="stPopover"] > button {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(12px);
        border-radius: 12px !important;
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
    </style>
    """, unsafe_allow_html=True)

# --- 2. SECURE CONNECTION ---
try:
    # Ensure these match your Streamlit Secrets exactly
    client = Client()
    client.set_endpoint(st.secrets["APPWRITE_ENDPOINT"])
    client.set_project(st.secrets["APPWRITE_PROJECT_ID"])
    client.set_key(st.secrets["APPWRITE_API_KEY"])
    db = Databases(client)

    DB_ID = st.secrets["DATABASE_ID"]
    COLL_ID = st.secrets["INVENTORY_COLLECTION_ID"]
except Exception as e:
    st.error(f"Credential Error: {e}")
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


# --- 4. NAVIGATION ---
st.sidebar.title("🚀 SmartStock")
st.sidebar.markdown("---")
menu = st.sidebar.selectbox("Dashboard", ["Inventory Hub", "Customer Churn"])

# --- 5. MODULE: INVENTORY HUB ---
if menu == "Inventory Hub":
    st.title("📦 SmartStock Inventory")

    with st.expander("➕ Register New Stock Item"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Item Name", placeholder="e.g. MacBook Pro")
        with c2:
            stock = st.number_input("Quantity", min_value=0, step=1)

        if st.button("Add to Appwrite"):
            if name:
                try:
                    db.create_document(DB_ID, COLL_ID, ID.unique(), {
                        "item_name": name,
                        "current_stock": int(stock)
                    })
                    st.success(f"✅ {name} added!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Write Error: {e}")
            else:
                st.warning("Please enter an item name.")

    # --- FETCH DATA (UNIVERSAL FIX) ---
    try:
        response = db.list_documents(DB_ID, COLL_ID)

        # Determine if it's an Object or Dictionary
        docs = getattr(response, 'documents', response.get('documents', [])) if not isinstance(
            response, dict) else response.get('documents', [])

        if docs:
            items_list = []
            doc_ids = []
            for doc in docs:
                # UNIVERSAL EXTRACTION: Works for Objects and Dicts
                data = getattr(doc, 'data', doc.get('data', {})
                               if isinstance(doc, dict) else {})
                d_id = getattr(doc, '$id', doc.get('$id')
                               if isinstance(doc, dict) else None)

                if data:
                    items_list.append(data)
                    doc_ids.append(d_id)

            if items_list:
                df = pd.DataFrame(items_list)

                col_left, col_right = st.columns([1.2, 1])
                with col_left:
                    st.subheader("Live Inventory")
                    st.dataframe(df, use_container_width=True, hide_index=True)

                    with st.popover("🗑️ Manage Inventory"):
                        to_delete = st.selectbox(
                            "Select item to remove:", df['item_name'].tolist())
                        if st.button("Confirm Delete"):
                            idx = df[df['item_name'] == to_delete].index[0]
                            db.delete_document(DB_ID, COLL_ID, doc_ids[idx])
                            st.rerun()

                with col_right:
                    st.subheader("Stock Distribution")
                    fig = px.pie(df, names="item_name",
                                 values="current_stock", hole=0.4)
                    st.plotly_chart(apply_chart_style(
                        fig), use_container_width=True)
        else:
            st.info("No items in stock. Add one above!")
    except Exception as e:
        st.error(f"Fetch Error: {e}")

# --- 6. MODULE: CUSTOMER CHURN ---
else:
    st.title("📉 Churn Prediction")
    eng = st.slider("Engagement Level (%)", 0, 100, 50)
    if st.button("Predict Risk"):
        risk = 100 - eng
        st.metric("Risk Score", f"{risk}%", delta="High Risk" if risk >
                  60 else "Healthy", delta_color="inverse")
