 
import streamlit as st
import pandas as pd
import plotly.express as px

st.markdown("""
<style>
/* Reduce sidebar width */
[data-testid="stSidebar"] {
    min-width: 200px !important;
    max-width: 200px !important;
    width: 200px !important;
}

/* Expand main content to take remaining space */
.main .block-container {
    max-width: 95% !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* Reduce spacing between charts and components */
.css-1y4p8pa, .css-1oe6wy4, .element-container {
    padding: 0px !important;
    margin: 0px !important;
}

/* Reduce spacing between headers and charts */
h1, h2, h3, h4, h5 {
    margin-top: 0px !important;
    margin-bottom: 5px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* REMOVE left padding between sidebar and main content */
.main .block-container {
    padding-left: 1rem !important;  /* reduce from default ~5rem */
    padding-right: 1rem !important;
    margin-left: 0rem !important;
}

/* OPTIONAL: make everything slightly tighter vertically */
.css-1y4p8pa, .css-1oe6wy4, .element-container {
    padding-top: 0rem !important;
    margin-top: 0rem !important;
}
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>

/* REMOVE LEFT + RIGHT SPACE BETWEEN SIDEBAR AND HEADER */
.main .block-container {
    padding-left: 0rem !important;
    padding-right: 0rem !important;
    margin-left: 0rem !important;
    margin-right: 0rem !important;
}

/* Make header align fully left */
h1 {
    padding-left: 0rem !important;
    margin-left: 0rem !important;
}

</style>
""", unsafe_allow_html=True)

st.markdown ("""
<style>

/* Make the sidebar wider */
[data-testid="stSidebar"] {
    min-width: 320px !important;   /* Increase width */
    max-width: 320px !important;
    width: 320px !important;
}

/* Adjust main content to start after wider sidebar */
.main .block-container {
    padding-left: 2rem !important;
}

</style>
""", unsafe_allow_html=True)





# =====================================
# LOAD + CLEAN DATA
# =====================================
df = pd.read_excel("Tesla deliveries 2015-2025.xlsx")
df.columns = df.columns.str.lower().str.replace(" ", "_")

df = df.rename(columns={
    "monthly_revenue_(millions)": "monthly_revenue_millions",
    "model_mix_%": "model_mix_pct",
    "yoy_growth": "yoy_growth",
    "qo_q_growth": "qo_q_growth"
})

# =====================================
# DASHBOARD HEADER
# =====================================
st.markdown(
    """
    <h1 style='text-align:centre; color:#333;'> Tesla Global Deliveries & Production Dashboard (2015–2025)</h1>
    """,
    unsafe_allow_html=True
)

# =====================================
# SIDEBAR — PARAMETERS
# =====================================
st.sidebar.header("Parameters")

time_selector = st.sidebar.radio(
    "Time Selector", ["Year", "Month"]
)

model = st.sidebar.selectbox(
    "Select Model", sorted(df["model"].unique())
)

region = st.sidebar.selectbox(
    "Select Region", sorted(df["region"].unique())
)

metric_map = {
    "Estimated Deliveries": "estimated_deliveries",
    "Production Units": "production_units",
    "Monthly Revenue (Millions)": "monthly_revenue_millions",
    "Efficiency (%)": "delivery_efficiency_rate",
    "YoY Growth (%)": "yoy_growth"
}

metric_label = st.sidebar.selectbox("Choose Model Metric", list(metric_map.keys()))
metric_col = metric_map[metric_label]

# =====================================
# SIDEBAR — FILTERS
# =====================================
st.sidebar.header("Filters")

years = st.sidebar.multiselect(
    "Year",
    sorted(df["year"].unique()),
    default=sorted(df["year"].unique())
)

quarters = st.sidebar.multiselect(
    "Quarter",
    sorted(df["quarter"].unique()),
    default=sorted(df["quarter"].unique())
)

# =====================================
# APPLY FILTERS
# =====================================
filtered = df[
    (df["model"] == model) &
    (df["region"] == region) &
    (df["year"].isin(years)) &
    (df["quarter"].isin(quarters))
]

# ===========================================================
# KPI CARDS (Top Row) — Tableau Style Red Accent
# ===========================================================
kpi_css = """
<style>
.kpi-card {
    background-color: #fff;
    padding: 18px;
    border-radius: 10px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    border-left: 6px solid #E82127;
    text-align: center;
    font-size: 18px;
    margin-bottom: 10px;
}
.kpi-card b {
    font-size: 17px;
    color: #444;
}
</style>
"""
st.markdown(kpi_css, unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(
        f"""
        <div class='kpi-card'>
            <b>Estimated Deliveries </b><br>{filtered['estimated_deliveries'].sum():,}
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class='kpi-card'>
            <b>Production Units</b><br>{filtered['production_units'].sum():,}
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    revenue_total = filtered["monthly_revenue_millions"].sum()/1_000_0
    st.markdown(
        f"""
        <div class='kpi-card'>
            <b>Revenue ($M)</b><br>{revenue_total:,.1f}
        </div>
        """,
        unsafe_allow_html=True
    )

efficiency_val = filtered['delivery_efficiency_rate'].mean()

with col4:
    st.markdown(
        f"""
        <div class='kpi-card'>
            <b>Efficiency (%)</b><br>{efficiency_val:.2f}%
        </div>
        """,
        unsafe_allow_html=True
    )


yoy_val = filtered['yoy_growth'].mean()

with col5:
    st.markdown(
        f"""
        <div class='kpi-card'>
            <b>YoY Growth (%)</b><br>{yoy_val:.2f}%
        </div>
        """,
        unsafe_allow_html=True
    )


 
# =====================================
# LINE CHART — TIME SELECTOR (Year / Month)
# =====================================

if time_selector == "Year":
    # All years for full axis
    years_all = sorted(df["year"].unique())

    # Aggregate filtered data, reindex to show missing years as zero
    year_df = (
        filtered.groupby("year")[["estimated_deliveries", "production_units"]]
        .sum()
        .reindex(years_all, fill_value=0)
        .reset_index()
    )

    fig_line = px.line(
        year_df,
        x="year",
        y=["estimated_deliveries", "production_units"],
        markers=True,
        title="Tesla Deliveries vs Production Trend (Yearly)",
        color_discrete_sequence=["#E82127", "#000000"]
    )

    fig_line.update_xaxes(
        categoryorder="array",
        categoryarray=years_all,
        tickmode="array",
        tickvals=years_all
    )

else:  # MONTH VIEW
    # Full month axis (1–12)
    months_all = list(range(1, 13))

    month_df = (
        filtered.groupby("month")[["estimated_deliveries", "production_units"]]
        .sum()
        .reindex(months_all, fill_value=0)
        .reset_index()
    )

    fig_line = px.line(
        month_df,
        x="month",
        y=["estimated_deliveries", "production_units"],
        markers=True,
        title="Tesla Deliveries vs Production Trend (Monthly)",
        color_discrete_sequence=["#E82127", "#000000"]
    )

    fig_line.update_xaxes(
        tickmode="array",
        tickvals=months_all
    )

st.plotly_chart(fig_line, use_container_width=True)


# =====================================
# BAR CHART — SELECTED METRIC (Year / Month)
# =====================================
# =====================================
# BAR CHART — SELECTED METRIC
# =====================================

if time_selector == "Year":
    years_all = sorted(df["year"].unique())

    bar_df = (
        filtered.groupby("year")[metric_col]
        .sum()
        .reindex(years_all, fill_value=0)
        .reset_index()
    )

    fig_bar = px.bar(
        bar_df,
        x=metric_col,
        y="year",
        orientation="h",
        title=f"{metric_label} by Year",
        color_discrete_sequence=["#E82127"]
    )

    fig_bar.update_yaxes(
        tickmode="array",
        tickvals=years_all
    )

else:  # MONTH BAR VIEW
    months_all = list(range(1, 13))

    bar_df = (
        filtered.groupby("month")[metric_col]
        .sum()
        .reindex(months_all, fill_value=0)
        .reset_index()
    )

    fig_bar = px.bar(
        bar_df,
        x=metric_col,
        y="month",
        orientation="h",
        title=f"{metric_label} by Month",
        color_discrete_sequence=["#E82127"]
    )

    fig_bar.update_yaxes(
        tickmode="array",
        tickvals=months_all
    )

st.plotly_chart(fig_bar, use_container_width=True)

 

# =====================================
# SUMMARY TABLE
# =====================================
st.markdown("""
<h4 style='margin-top:0rem; margin-bottom:0.5rem; font-size:18px;'>
📄 Summary Table — Deliveries, Production & Efficiency Metrics
</h4>
""", unsafe_allow_html=True)
 


summary_cols = [
    "year", "region", "model", "quarter",
    "estimated_deliveries", "market_share",
    "monthly_revenue_millions", "production_units",
    "qo_q_growth", "delivery_efficiency_rate", "yoy_growth"
]

summary_cols = [c for c in summary_cols if c in filtered.columns]

# 🟢 Remove row numbers by resetting index
summary_df = (
    filtered[summary_cols]
    .sort_values(["year", "quarter"])
    .reset_index(drop=True)
)

st.dataframe(summary_df, hide_index=True, use_container_width=True)

 





