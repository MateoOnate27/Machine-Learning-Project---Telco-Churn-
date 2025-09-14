import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Telco Customer Churn — Interactive EDA", layout="wide")

# -----------------------------
# Helpers
# -----------------------------
@st.cache_data
def load_data_from_csv(uploaded_file):
    df = pd.read_csv(uploaded_file)
    return df

def coerce_telco_types(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Normalize commonly messy columns in Telco dataset
    if 'TotalCharges' in df.columns:
        df['TotalCharges'] = pd.to_numeric(df['TotalCharges'].replace(" ", np.nan), errors='coerce')
    # Coerce churn to categorical Yes/No if exists
    if 'Churn' in df.columns:
        df['Churn'] = df['Churn'].astype(str)
    # tenure often is int
    if 'tenure' in df.columns:
        df['tenure'] = pd.to_numeric(df['tenure'], errors='coerce')
    if 'MonthlyCharges' in df.columns:
        df['MonthlyCharges'] = pd.to_numeric(df['MonthlyCharges'], errors='coerce')
    return df

def tenure_bin(val):
    if pd.isna(val):
        return np.nan
    if val < 6: return "0–6"
    if val < 12: return "6–12"
    if val < 24: return "12–24"
    if val < 36: return "24–36"
    if val < 48: return "36–48"
    if val < 60: return "48–60"
    return "60+"

# -----------------------------
# Sidebar — Data Loading
# -----------------------------
st.sidebar.title("Data")
st.sidebar.write("Upload the Telco Customer Churn CSV. The app will adapt to available columns.")
uploaded = st.sidebar.file_uploader("Upload CSV", type=["csv"])

if uploaded is None:
    st.info("👋 Upload the Telco Customer Churn CSV to begin (e.g., WA_Fn-UseC_-Telco-Customer-Churn.csv).")
    st.stop()

raw = load_data_from_csv(uploaded)
df = coerce_telco_types(raw)

# Basic checks
missing_core = [c for c in ["Churn", "MonthlyCharges", "tenure"] if c not in df.columns]
if missing_core:
    st.warning(f"The following expected columns were not found: {missing_core}. The app will still run with available columns.")
    
# Tenure bins for certain charts
if "tenure" in df.columns:
    df["tenure_bin"] = df["tenure"].apply(tenure_bin)
    df["tenure_bin"] = pd.Categorical(df["tenure_bin"], ordered=True,
                                      categories=["0–6","6–12","12–24","24–36","36–48","48–60","60+"])

st.title("📊 Telco Customer Churn — Interactive EDA")
st.caption("Explore key drivers of churn with interactive controls, dynamic charts, and live KPIs.")

# -----------------------------
# Sidebar — Filters
# -----------------------------
st.sidebar.title("Filters")

def multiselect_if(col):
    if col in df.columns:
        vals = sorted(df[col].dropna().astype(str).unique())
        return st.sidebar.multiselect(col, vals, default=vals)
    return None

def range_slider_if_numeric(col, step=1.0):
    if col in df.columns and np.issubdtype(df[col].dropna().dtype, np.number):
        cmin, cmax = float(np.nanmin(df[col])), float(np.nanmax(df[col]))
        return st.sidebar.slider(col, min_value=cmin, max_value=cmax, value=(cmin, cmax), step=step)
    return None

# Common categorical filters
opt_gender = multiselect_if("gender")
opt_contract = multiselect_if("Contract")
opt_payment = multiselect_if("PaymentMethod")
opt_internet = multiselect_if("InternetService")
opt_partner = multiselect_if("Partner")
opt_dependents = multiselect_if("Dependents")
opt_senior = multiselect_if("SeniorCitizen")  # sometimes 0/1 or "Yes"/"No"

# Numeric ranges
rng_tenure = range_slider_if_numeric("tenure", step=1.0)
rng_monthly = range_slider_if_numeric("MonthlyCharges", step=1.0)

# Apply filters
fdf = df.copy()
def apply_multiselect(col, opts):
    global fdf
    if opts is not None and col in fdf.columns:
        fdf = fdf[fdf[col].astype(str).isin(opts)]

apply_multiselect("gender", opt_gender)
apply_multiselect("Contract", opt_contract)
apply_multiselect("PaymentMethod", opt_payment)
apply_multiselect("InternetService", opt_internet)
apply_multiselect("Partner", opt_partner)
apply_multiselect("Dependents", opt_dependents)
apply_multiselect("SeniorCitizen", opt_senior)

if rng_tenure and "tenure" in fdf.columns:
    fdf = fdf[(fdf["tenure"] >= rng_tenure[0]) & (fdf["tenure"] <= rng_tenure[1])]

if rng_monthly and "MonthlyCharges" in fdf.columns:
    fdf = fdf[(fdf["MonthlyCharges"] >= rng_monthly[0]) & (fdf["MonthlyCharges"] <= rng_monthly[1])]

# -----------------------------
# KPI Cards
# -----------------------------
kpi_cols = st.columns(4)
with kpi_cols[0]:
    st.subheader("📉 Churn Rate")
    if "Churn" in fdf.columns:
        churn_rate = np.mean(fdf["Churn"].astype(str).str.lower().eq("yes")) * 100 if len(fdf) else 0.0
        st.metric(label="", value=f"{churn_rate:.1f}%")
    else:
        st.write("N/A")

with kpi_cols[1]:
    st.subheader("💵 Avg. Monthly Charges")
    if "MonthlyCharges" in fdf.columns and len(fdf):
        st.metric(label="", value=f"${fdf['MonthlyCharges'].mean():.2f}")
    else:
        st.write("N/A")

with kpi_cols[2]:
    st.subheader("🗓️ Avg. Tenure (months)")
    if "tenure" in fdf.columns and len(fdf):
        st.metric(label="", value=f"{fdf['tenure'].mean():.1f}")
    else:
        st.write("N/A")

with kpi_cols[3]:
    st.subheader("👥 Customers (filtered)")
    st.metric(label="", value=f"{len(fdf):,}")

st.markdown("---")

# -----------------------------
# Charts — Layout
# -----------------------------
tab1, tab2, tab3 = st.tabs(["🔎 Overview", "📈 Drivers", "🧪 Correlations"])

# -----------------------------
# Tab 1 — Overview
# -----------------------------
with tab1:
    c1, c2 = st.columns(2)
    if "Churn" in fdf.columns:
        churn_counts = fdf["Churn"].value_counts().reset_index()
        churn_counts.columns = ["Churn", "Count"]
        fig = px.pie(churn_counts, names="Churn", values="Count", hole=0.35)
        c1.plotly_chart(fig, use_container_width=True)
    if "tenure" in fdf.columns:
        fig = px.histogram(fdf, x="tenure", nbins=40, color="Churn" if "Churn" in fdf.columns else None, barmode="overlay")
        c2.plotly_chart(fig, use_container_width=True)
    
    if "MonthlyCharges" in fdf.columns:
        fig = px.histogram(fdf, x="MonthlyCharges", nbins=40, color="Churn" if "Churn" in fdf.columns else None, barmode="overlay")
        st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Tab 2 — Drivers
# -----------------------------
with tab2:
    left, right = st.columns(2)
    # Churn rate by a selected categorical feature
    cat_cols = [c for c in fdf.columns if fdf[c].dtype == 'object' and c not in ["customerID"]]
    cat_choice = left.selectbox("Churn rate by category", options=cat_cols or ["(no categorical columns)"])
    if cat_choice != "(no categorical columns)" and "Churn" in fdf.columns:
        grp = (fdf
               .assign(churn_num=fdf["Churn"].astype(str).str.lower().eq("yes").astype(int))
               .groupby(cat_choice, dropna=False)["churn_num"].mean()
               .reset_index())
        grp["Churn Rate (%)"] = grp["churn_num"] * 100
        fig = px.bar(grp.sort_values("Churn Rate (%)", ascending=False), x=cat_choice, y="Churn Rate (%)")
        left.plotly_chart(fig, use_container_width=True)

    # Boxplot MonthlyCharges by Churn
    if "MonthlyCharges" in fdf.columns and "Churn" in fdf.columns:
        fig = px.box(fdf, x="Churn", y="MonthlyCharges", points="all")
        right.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Crossed View")
    c1, c2 = st.columns(2)
    # Cross tab heatmap (two categorical axes, churn as color)
    if len(cat_cols) >= 2 and "Churn" in fdf.columns:
        cross_x = c1.selectbox("Axis X (category)", options=cat_cols, index=0)
        cross_y = c2.selectbox("Axis Y (category)", options=[c for c in cat_cols if c != cross_x], index=0)
        tmp = (fdf
               .assign(churn_num=fdf["Churn"].astype(str).str.lower().eq("yes").astype(int))
               .groupby([cross_x, cross_y], dropna=False)["churn_num"].mean()
               .reset_index())
        tmp["Churn Rate (%)"] = (tmp["churn_num"] * 100).round(1)
        fig = px.density_heatmap(tmp, x=cross_x, y=cross_y, z="Churn Rate (%)", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)

    # Scatter: tenure vs MonthlyCharges colored by churn
    if "tenure" in fdf.columns and "MonthlyCharges" in fdf.columns:
        fig = px.scatter(fdf, x="tenure", y="MonthlyCharges", color="Churn" if "Churn" in fdf.columns else None,
                         hover_data=[c for c in ["Contract","PaymentMethod","InternetService"] if c in fdf.columns])
        st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Tab 3 — Correlations
# -----------------------------
with tab3:
    # try to convert yes/no to 1/0 for correlation
    num_df = fdf.copy()
    for col in num_df.columns:
        if num_df[col].dtype == 'object':
            vals = num_df[col].dropna().unique().tolist()
            if set(map(str.lower, map(str, vals))) <= {"yes","no"}:
                num_df[col] = num_df[col].astype(str).str.lower().map({"yes":1, "no":0})
    # keep numeric
    num_df = num_df.select_dtypes(include=[np.number])
    if not num_df.empty:
        corr = num_df.corr(numeric_only=True)
        corr = corr.round(2).reset_index().melt(id_vars="index", var_name="feature2", value_name="corr").rename(columns={"index":"feature1"})
        fig = px.density_heatmap(corr, x="feature1", y="feature2", z="corr", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No numeric columns available to compute correlations.")

st.markdown("---")
st.header("📌 Key Findings")
st.write("""
- Explore filters to compare churn rates across **Contract** types, **PaymentMethod**, and **InternetService**.
- Higher **MonthlyCharges** often align with higher churn in many Telco datasets—verify this pattern with your filters.
- **Shorter tenure** groups can show higher churn; use *tenure* range to check.
""")
