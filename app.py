import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="NEXUS | Sales Intelligence",
    page_icon="📈",
    layout="wide"
)

# ---------- DESIGN ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #F5F7FB;
    color: #172033;
}

.block-container {
    max-width: 1450px;
    padding: 2rem 2.5rem 3rem;
}

header[data-testid="stHeader"] {
    background: transparent;
}

section[data-testid="stSidebar"] {
    background: #111827;
}

section[data-testid="stSidebar"] * {
    color: #E5E7EB;
}

.hero {
    background: linear-gradient(115deg, #172554, #1D4ED8);
    padding: 30px 34px;
    border-radius: 18px;
    color: white;
    margin-bottom: 28px;
}

.hero-label {
    font-size: 11px;
    letter-spacing: 2px;
    font-weight: 700;
    color: #BFDBFE;
}

.hero-title {
    font-size: 32px;
    font-weight: 800;
    margin-top: 8px;
    color: white;
}

.hero-text {
    color: #DBEAFE;
    margin-top: 7px;
    font-size: 14px;
}

.section-title {
    font-size: 20px;
    font-weight: 700;
    color: #172033;
    margin: 25px 0 15px;
}

div[data-testid="stMetric"] {
    background: white;
    padding: 20px;
    border: 1px solid #E5EAF2;
    border-radius: 15px;
    box-shadow: 0 3px 12px rgba(15, 23, 42, 0.035);
}

div[data-testid="stMetricLabel"] {
    color: #64748B;
    font-size: 13px;
}

div[data-testid="stMetricValue"] {
    color: #172554;
    font-weight: 800;
}

div[data-testid="stMetricDelta"] {
    font-size: 12px;
}

div[data-testid="stPlotlyChart"] {
    background: white;
    border: 1px solid #E5EAF2;
    border-radius: 15px;
    padding: 12px;
}

div[data-testid="stDataFrame"] {
    background: white;
    border-radius: 12px;
}

div.stDownloadButton > button {
    background: #1D4ED8;
    color: white;
    border: none;
    border-radius: 9px;
    padding: 10px 18px;
    font-weight: 600;
}

div.stDownloadButton > button:hover {
    background: #1E40AF;
    color: white;
}

div[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.06);
    border: 1px dashed #64748B;
    border-radius: 12px;
    padding: 12px;
}

</style>
""", unsafe_allow_html=True)


# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("## ◈ NEXUS")
    st.caption("SALES INTELLIGENCE")
    st.divider()

    st.markdown("### Data source")

    uploaded_file = st.file_uploader(
        "Upload sales file",
        type=["csv", "xlsx"]
    )

    st.divider()
    st.markdown("### Required columns")
    st.code("Product\nPrice\nQuantity", language="text")
    st.caption("Date column is optional.")


# ---------- HEADER ----------
st.markdown("""
<div class="hero">
    <div class="hero-label">BUSINESS INTELLIGENCE PLATFORM</div>
    <div class="hero-title">Sales Overview</div>
    <div class="hero-text">
        Understand your performance. Discover your best products.
    </div>
</div>
""", unsafe_allow_html=True)


# ---------- EMPTY STATE ----------
if uploaded_file is None:
    st.markdown("### Your business, at a glance")

    st.write(
        "Upload your sales data to explore revenue, "
        "product performance and useful business insights."
    )

    a, b, c = st.columns(3)

    a.metric("Revenue tracking", "Ready")
    b.metric("Product analytics", "Ready")
    c.metric("Report export", "Ready")

    st.info(
        "Start by uploading a CSV or Excel file "
        "containing Product, Price and Quantity."
    )

    st.stop()


# ---------- READ FILE ----------
try:
    if uploaded_file.name.lower().endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)

except Exception:
    st.error("Unable to read this file. Please check its format.")
    st.stop()


# ---------- VALIDATE DATA ----------
required = ["Product", "Price", "Quantity"]

missing = [column for column in required if column not in df.columns]

if missing:
    st.error("Missing required columns: " + ", ".join(missing))
    st.stop()

df = df.copy()

df["Product"] = (
    df["Product"]
    .fillna("")
    .astype(str)
    .str.strip()
)

df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")

df = df.dropna(subset=["Price", "Quantity"])
df = df[df["Product"] != ""]

if df.empty:
    st.warning("No valid sales records were found in this file.")
    st.stop()

df["Revenue"] = df["Price"] * df["Quantity"]


# ---------- FILTERS ----------
with st.sidebar:
    st.divider()
    st.markdown("### Filters")

    products = sorted(df["Product"].unique().tolist())

    selected_products = st.multiselect(
        "Products",
        products,
        default=products
    )

    date_column = next(
        (
            col for col in ["Date", "date", "Order Date", "order_date"]
            if col in df.columns
        ),
        None
    )

    date_range = None

    if date_column:
        df[date_column] = pd.to_datetime(
            df[date_column], errors="coerce"
        )

        valid_dates = df[date_column].dropna()

        if not valid_dates.empty:
            first_date = valid_dates.min().date()
            last_date = valid_dates.max().date()

            date_range = st.date_input(
                "Date range",
                value=(first_date, last_date),
                min_value=first_date,
                max_value=last_date
            )


filtered = df[df["Product"].isin(selected_products)].copy()

if date_column and date_range and len(date_range) == 2:
    start_date, end_date = date_range

    filtered = filtered[
        filtered[date_column].notna()
        & (filtered[date_column].dt.date >= start_date)
        & (filtered[date_column].dt.date <= end_date)
    ]

if filtered.empty:
    st.warning("No records match your filters. Please change the selection.")
    st.stop()


# ---------- METRICS ----------
revenue = filtered["Revenue"].sum()
units = filtered["Quantity"].sum()
product_count = filtered["Product"].nunique()
average_revenue = revenue / len(filtered)

st.markdown(
    '<div class="section-title">Performance snapshot</div>',
    unsafe_allow_html=True
)

m1, m2, m3, m4 = st.columns(4)

m1.metric("Total Revenue", f"{revenue:,.0f}")
m2.metric("Units Sold", f"{units:,.0f}")
m3.metric("Active Products", f"{product_count:,}")
m4.metric("Average Row Revenue", f"{average_revenue:,.0f}")


# ---------- CHARTS ----------
st.markdown(
    '<div class="section-title">Product performance</div>',
    unsafe_allow_html=True
)

chart_data = (
    filtered.groupby("Product", as_index=False)
    .agg(
        Revenue=("Revenue", "sum"),
        Quantity=("Quantity", "sum")
    )
    .sort_values("Revenue", ascending=False)
)

left, right = st.columns(2)

with left:
    fig_revenue = px.bar(
        chart_data,
        x="Product",
        y="Revenue",
        title="Revenue by Product",
        color="Revenue",
        color_continuous_scale=["#BFDBFE", "#1D4ED8"],
        template="plotly_white"
    )

    fig_revenue.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font_color="#334155",
        margin=dict(l=15, r=15, t=55, b=15),
        xaxis_title="",
        yaxis_title="Revenue"
    )

    st.plotly_chart(fig_revenue, use_container_width=True)

with right:
    fig_quantity = px.pie(
        chart_data,
        names="Product",
        values="Quantity",
        title="Sales Quantity Distribution",
        hole=0.58,
        color_discrete_sequence=[
            "#1D4ED8", "#06B6D4", "#8B5CF6",
            "#F59E0B", "#10B981", "#F43F5E"
        ],
        template="plotly_white"
    )

    fig_quantity.update_layout(
        paper_bgcolor="white",
        font_color="#334155",
        margin=dict(l=15, r=15, t=55, b=15),
        legend_title_text="Product"
    )

    st.plotly_chart(fig_quantity, use_container_width=True)


# ---------- TABLE ----------
st.markdown(
    '<div class="section-title">Product performance table</div>',
    unsafe_allow_html=True
)

st.dataframe(
    chart_data,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Product": st.column_config.TextColumn("Product"),
        "Revenue": st.column_config.NumberColumn(
            "Revenue", format="%.0f"
        ),
        "Quantity": st.column_config.NumberColumn(
            "Units Sold", format="%.0f"
        )
    }
)

st.markdown(
    '<div class="section-title">Detailed sales records</div>',
    unsafe_allow_html=True
)

st.dataframe(
    filtered,
    use_container_width=True,
    hide_index=True
)


# ---------- DOWNLOAD ----------
csv_file = filtered.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    "Download Sales Report",
    data=csv_file,
    file_name="sales_report.csv",
    mime="text/csv"
)

st.caption("NEXUS Sales Intelligence  |  Built with Python, Pandas and Streamlit")