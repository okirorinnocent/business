# SmartStock Pro BI 📈

A dark-themed warehouse inventory dashboard built with **Streamlit**, **Appwrite** and **Plotly**. It gives managers a live overview of stock levels, simple tools to register, adjust and remove items, and a small churn-risk calculator.

## Features

- **📊 Business Dashboard**
  - KPI cards: total SKU count, total units in the warehouse and low-stock alerts (items with 5 units or fewer).
  - Interactive Plotly charts: inventory distribution (donut) and stock levels by item (bar).
  - A detailed inventory table.
- **⚙️ Inventory Control**
  - **Register Item:** add a new product with a starting quantity.
  - **Update Quantity:** add or remove stock with a `+/-` adjustment (blocked if it would go below zero).
  - **Remove Asset:** permanently delete an item.
- **📉 Customer Churn:** a slider-based risk calculator. Risk = 100 − engagement score; above 60% it shows a high-priority call alert. This is a simple rule, not a trained machine learning model.
- High-contrast navy and cyan theme, styled metrics, tabs and buttons.

## Tech Stack

- [Streamlit](https://streamlit.io): UI
- [Appwrite](https://appwrite.io) (Cloud, Frankfurt region): database
- [Plotly Express](https://plotly.com/python/plotly-express/): charts
- [pandas](https://pandas.pydata.org): data handling

## Project Structure

```
.
├── app.py              # The whole app (your main Streamlit file)
├── requirements.txt
└── .streamlit/
    └── secrets.toml    # Appwrite credentials (not committed)
```

## Setup

### 1. Install

```bash
pip install streamlit pandas plotly appwrite
```

`requirements.txt`:

```
streamlit
pandas
plotly
appwrite
```

### 2. Prepare Appwrite

1. Create a project in the [Appwrite Console](https://cloud.appwrite.io).
2. Create a **Database**, then a **Collection** with these attributes:

   | Attribute | Type | Required |
   |---|---|---|
   | `item_name` | String | Yes |
   | `current_stock` | Integer | Yes |

3. Create an **API key** with only the scopes this app needs: `databases.read`, `documents.read` and `documents.write` (use the narrowest scopes your Appwrite version offers).
4. Note your **endpoint**, **project ID**, **database ID** and **collection ID**.

### 3. Add your credentials

Create `.streamlit/secrets.toml`:

```toml
APPWRITE_ENDPOINT   = "https://fra.cloud.appwrite.io/v1"
APPWRITE_PROJECT_ID = "<project-id>"
APPWRITE_API_KEY    = "<api-key>"
APPWRITE_DB_ID      = "<database-id>"
APPWRITE_COLL_ID    = "<collection-id>"
```

Then replace the hardcoded block in `app.py` with:

```python
client = Client()
client.set_endpoint(st.secrets["APPWRITE_ENDPOINT"])
client.set_project(st.secrets["APPWRITE_PROJECT_ID"])
client.set_key(st.secrets["APPWRITE_API_KEY"])
db = Databases(client)

DB_ID = st.secrets["APPWRITE_DB_ID"]
COLL_ID = st.secrets["APPWRITE_COLL_ID"]
```

On Streamlit Community Cloud, paste the same content into **Settings → Secrets**.

### 4. Run

```bash
streamlit run app.py
```

## Security: please read

The API key in the current code is a **server API key**, which gives full access to whatever its scopes allow. If it has ever been committed to GitHub or shared anywhere:

1. **Delete it and create a new key** in the Appwrite Console (Overview → Integrations → API keys). Removing it from the code is not enough, because it stays in your git history.
2. Give the new key only the scopes it needs.
3. Keep it in `secrets.toml` or your host's secrets manager, and add `.streamlit/secrets.toml` to `.gitignore`.

This app also has **no login**: anyone who can open it can add, change or delete stock. Add authentication before using it with real data.

## Known limitations and improvements

- **Only the first 25 items load.** Appwrite's `list_documents` returns 25 documents by default. Add pagination or `Query.limit(100)` and use `Query.offset` / `Query.cursor_after` for larger inventories.
- **Failed loads are silent in Inventory Control.** A bare `except:` hides errors and leaves the dropdown empty. Show the error instead.
- **No price or sales data.** Stock levels are tracked, but not value, sales history or restock history. Add `price` and a separate movements collection to get revenue and trend charts.
- **The churn page is a placeholder.** To make it real, train a model (for example scikit-learn logistic regression) on actual customer data and load it in the app.
- **Deprecated parameter.** Newer Streamlit versions (1.50+) replace `use_container_width=True` with `width="stretch"`.
- **Low-stock threshold** (5 units) is hardcoded. Consider making it configurable per item.

## Author

**Okiror Innocent**, Computer Science student, Mbarara University of Science and Technology (MUST), Uganda.

## License

© 2026 Okiror Innocent. All rights reserved.
