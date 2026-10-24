
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="AirSight | Air Quality Analytics",
                   page_icon="🌿", layout="wide")

st.markdown("""
<style>
.stApp {background:#f5f8f6}
.block-container {padding-top:2rem; max-width:1400px}
.hero {background:linear-gradient(120deg,#123d32,#258568);
padding:28px;border-radius:18px;color:white;margin-bottom:20px}
.hero h1 {color:white;margin:0}
.hero p {color:#e2f5ec}
div[data-testid="stMetric"] {background:white;padding:15px;
border-radius:12px;border:1px solid #dce8e0}
</style>
<div class="hero">
<h1>🌿 AirSight</h1>
<p>Air Quality & Weather Analysis System | DAE Project</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.title("🌿 AirSight")
st.sidebar.caption("Data Analytics & Exploration")
uploaded = st.sidebar.file_uploader("Upload your real CSV dataset", type="csv")

@st.cache_data
def demo_data():
    rng = np.random.default_rng(42)
    cities = ["Delhi","Mumbai","Hyderabad","Vijayawada",
              "Kolkata","Bengaluru","Chennai","Jaipur"]
    dates = pd.date_range("2025-01-01", periods=120)
    rows = []
    for d in dates:
        for c in cities:
            rows.append({
                "Date": d, "City": c,
                "PM2.5": round(max(3,rng.normal(48,20)),1),
                "PM10": round(max(8,rng.normal(90,30)),1),
                "NO2": round(max(2,rng.normal(24,8)),1),
                "Temperature": round(rng.normal(28,5),1),
                "Humidity": round(rng.uniform(25,90),1)
            })
    return pd.DataFrame(rows)

if uploaded:
    try:
        df = pd.read_csv(uploaded)
        st.sidebar.success("Uploaded dataset loaded")
    except Exception as e:
        st.error(f"Could not read CSV: {e}")
        st.stop()
else:
    df = demo_data()
    st.warning("DEMO MODE: synthetic sample data, not live measurements. Upload your actual dataset before presenting results.")

df.columns = [str(c).strip() for c in df.columns]
df = df.dropna(how="all")
if df.empty:
    st.error("No data rows found. Please upload a valid CSV.")
    st.stop()

# Identify common column names
def find_col(names):
    return next((c for c in df.columns if c.strip().lower() in names), None)

city_col = find_col({"city","location","station","place","city_name"})
state_col = find_col({"state","region","state_name"})
date_col = find_col({"date","datetime","timestamp","time"})
numeric_cols = df.select_dtypes(include="number").columns.tolist()
pollutants = [c for c in numeric_cols if any(
    p in c.lower().replace(" ","") for p in
    ["pm2.5","pm25","pm10","no2","so2","co","o3","aqi"])]
if not pollutants:
    pollutants = numeric_cols

st.sidebar.subheader("Filters")
view = df.copy()
if state_col:
    options = sorted(view[state_col].dropna().unique().tolist(), key=str)
    chosen = st.sidebar.multiselect("State", options, default=options)
    view = view[view[state_col].isin(chosen)]
if city_col:
    options = sorted(view[city_col].dropna().unique().tolist(), key=str)
    chosen = st.sidebar.multiselect("City", options, default=options)
    view = view[view[city_col].isin(chosen)]
if view.empty:
    st.warning("No rows match the selected filters. Change your filters.")
    st.stop()

overview, explore, geography, data, quality = st.tabs([
    "📊 Overview", "🧪 Pollutant Explorer",
    "📍 Location Insights", "🗂️ Data Explorer", "🔍 Data Quality"
])

with overview:
    st.subheader("Air quality at a glance")
    a,b,c,d = st.columns(4)
    a.metric("Records", f"{len(view):,}")
    b.metric("Locations", view[city_col].nunique() if city_col else "Not available")
    c.metric("Numeric measures", len(numeric_cols))
    d.metric("Missing cells", f"{int(view.isna().sum().sum()):,}")

    if pollutants:
        measure = st.selectbox("Choose a pollutant or measure", pollutants)
        left,right = st.columns(2)
        with left:
            if date_col:
                temp = view.copy()
                temp[date_col] = pd.to_datetime(temp[date_col], errors="coerce")
                trend = temp.groupby(temp[date_col].dt.date)[measure].mean().reset_index()
                trend.columns = ["Date", measure]
                st.plotly_chart(px.line(trend, x="Date", y=measure,
                               title=f"{measure} over time"), use_container_width=True)
            elif city_col:
                summary = view.groupby(city_col)[measure].mean().reset_index()
                st.plotly_chart(px.bar(summary, x=city_col, y=measure,
                               title=f"Average {measure} by city"), use_container_width=True)
            else:
                st.info("Add a date or location column for trend analysis.")
        with right:
            st.plotly_chart(px.histogram(view, x=measure, nbins=30,
                             title=f"Distribution of {measure}"),
                            use_container_width=True)
        st.subheader("Descriptive statistics")
        st.dataframe(view[pollutants].describe().T.round(2),
                     use_container_width=True)

with explore:
    st.subheader("Pollutant Explorer")
    if pollutants:
        measure = st.selectbox("Select measure", pollutants, key="pollutant")
        vals = pd.to_numeric(view[measure], errors="coerce")
        a,b,c,d = st.columns(4)
        a.metric("Mean", f"{vals.mean():.2f}" if vals.notna().any() else "N/A")
        b.metric("Median", f"{vals.median():.2f}" if vals.notna().any() else "N/A")
        c.metric("Minimum", f"{vals.min():.2f}" if vals.notna().any() else "N/A")
        d.metric("Maximum", f"{vals.max():.2f}" if vals.notna().any() else "N/A")
        st.plotly_chart(px.box(view, y=measure, points="outliers",
                         title=f"{measure}: spread and outliers"),
                        use_container_width=True)
        if len(pollutants)>1:
            corr = view[pollutants].corr(numeric_only=True)
            st.plotly_chart(px.imshow(corr, text_auto=".2f",
                color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
                title="Correlation between numeric measures"),
                use_container_width=True)
    else:
        st.info("No numeric columns detected.")

with geography:
    st.subheader("Location Insights")
    loc = state_col or city_col
    if loc and pollutants:
        measure = st.selectbox("Compare locations by", pollutants, key="geo")
        summary = view.groupby(loc)[measure].agg(
            Average="mean", Median="median", Records="count"
        ).reset_index().sort_values("Average", ascending=False)
        st.plotly_chart(px.bar(summary, x=loc, y="Average",
            hover_data=["Median","Records"],
            title=f"Average {measure} by {loc}"),
            use_container_width=True)
        st.dataframe(summary, use_container_width=True, hide_index=True)
    else:
        st.info("A city/state column and numeric measure are needed.")

with data:
    st.subheader("Data Explorer")
    search = st.text_input("Search records")
    result = view
    if search:
        mask = result.astype(str).apply(
            lambda col: col.str.contains(search, case=False, na=False))
        result = result[mask.any(axis=1)]
    st.write(f"{len(result):,} records")
    st.dataframe(result, use_container_width=True, hide_index=True)
    st.download_button("Download filtered CSV",
        result.to_csv(index=False).encode("utf-8"),
        "airsight_filtered.csv", "text/csv")

with quality:
    st.subheader("Data Quality")
    a,b,c = st.columns(3)
    a.metric("Rows", f"{len(view):,}")
    b.metric("Missing cells", f"{int(view.isna().sum().sum()):,}")
    c.metric("Duplicate rows", f"{int(view.duplicated().sum()):,}")
    missing = view.isna().sum().rename("Missing values")
    st.dataframe(missing[missing>0].to_frame(),
                 use_container_width=True)
    st.dataframe(pd.DataFrame({
        "Column": view.columns,
        "Data type": view.dtypes.astype(str).values
    }), use_container_width=True, hide_index=True)

st.divider()
st.caption("AirSight | DAE Project | Data source and measurement units must be verified.")
