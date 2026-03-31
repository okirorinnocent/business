import streamlit as st
import pandas as pd
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID
import plotly.express as px

# --- 1. SETTINGS ---
st.set_page_config(page_title="SmartStock Pro BI",
                   page_icon="📈", layout="wide")

# --- 2. DATABASE CONNECTION (HARD-CODED FOR STABILITY) ---
try:
    client = Client()
    client.set_endpoint("https://fra.cloud.appwrite.io/v1")
    client.set_project("69caa235001a80451107")
    client.set_key("standard_4be6add50fbb8e35010a8c86de7133f164e5839e2f55c172a5eaa642c4317c65d4bf4e4c998ab89cb7d5a5febe79775aa691a21791e6d082b1df53a8cdc7562745ab5c10701c7df7dc106e334c49e0ef4e557528350583fb2c9e680d4ced46b9c775386d8d1bbdaf0e5e180b712067158c09d89ac13866fa371ee6fe57741c8c")
    db = Databases(client)

    DB_ID = "69caa399001e100948dd"
    COLL_ID = "69cace6f0013b2a6aace"
except Exception as e:
    st.error(f"❌ Connection Setup Failed: {e}")
    st.stop()

# --- 3. NAVIGATION ---
st.sidebar.title("🚀 SmartStock Pro")
page = st.sidebar.radio(
    "Navigate", ["Business Dashboard", "Inventory Control"])

# --- 4. PAGE: BUSINESS DASHBOARD ---
if page == "Business Dashboard":
    st.title("📊 Executive Overview")

    try:
        # Fetch data
        result = db.list_documents(DB_ID, COLL_ID)

        # SAFETY CHECK 1: Is there any data?
        if not result.documents:
            st.info(
                "👋 Welcome! Your database is empty. Go to 'Inventory Control' to add your first product.")
        else:
            # Convert to DataFrame
            df = pd.DataFrame([d.data for d in result.documents])

            # SAFETY CHECK 2: Do the columns exist?
            if 'item_name' in df.columns and 'current_stock' in df.columns:
                # Top Metrics
                m1, m2 = st.columns(2)
                m1.metric("Total SKUs", len(df))

                # Convert stock to numbers just in case they were saved as text
                df['current_stock'] = pd.to_numeric(
                    df['current_stock'], errors='coerce')
                total_stock = df['current_stock'].sum()
                m2.metric("Warehouse Volume", f"{int(total_stock):,}")

                # Chart
                fig = px.bar(df, x="item_name", y="current_stock",
                             title="Live Stock Levels", color_discrete_sequence=['#00f2fe'])
                fig.update_layout(template="plotly_dark",
                                  paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error(
                    "⚠️ Data structure mismatch. Ensure your Appwrite Attributes are 'item_name' and 'current_stock'.")
                st.write("Found columns:", list(df.columns))

    except Exception as e:
        st.error(f"⚠️ Dashboard Error: {e}")

# --- 5. PAGE: INVENTORY CONTROL ---
else:
    st.title("⚙️ Warehouse Operations")

    with st.form("add_item_form"):
        st.subheader("Register New Item")
        new_name = st.text_input("Item Name (e.g. iPhone 15)")
        new_qty = st.number_input("Opening Stock", min_value=0, step=1)
        submit = st.form_submit_button("Add to Cloud")

        if submit:
            if new_name:
                try:
                    db.create_document(DB_ID, COLL_ID, ID.unique(), {
                        "item_name": new_name,
                        "current_stock": int(new_qty)
                    })
                    st.success(f"✅ {new_name} added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to save: {e}")
            else:
                st.warning("Please enter a name for the item.")
