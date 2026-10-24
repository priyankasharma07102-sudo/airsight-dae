
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# =========================================================
# AIRSIGHT | AIR QUALITY & WEATHER ANALYTICS
# =========================================================
st.set_page_config(
    page_title="AirSight | Intelligence Dashboard",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

GREEN = "#10B981"
TEAL = "#2DD4BF"
BLUE = "#60A5FA"
AMBER = "#FBBF24"
RED = "#FB7185"
INK = "#142D27"
MUTED = "#647A72"
PALETTE = [GREEN, BLUE, TEAL, AMBER, RED, "#A78BFA", "#F472B6"]

# ---------------------- PREMIUM THEME ----------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --green: #10B981;
    --dark: #10251F;
    --text: #18372D;
    --muted: #688077;
    --border: #DCE9E2;
    --surface: #FFFFFF;
}

.stApp {
    background: #F3F7F4;
    color: var(--text);
    font-family: 'DM Sans', sans-serif;
}
[data-testid="stHeader"] {
    background: rgba(243,247,244,.94);
}
.block-container {
    max-width: 1500px;
    padding-top: 1.4rem;
    padding-bottom: 3rem;
}
h1, h2, h3, h4 {
    color: #18372D;
    font-family: 'Manrope', sans-serif;
    letter-spacing: -0.5px;
}
p, label, .stMarkdown, [data-testid="stCaptionContainer"] {
    color: #526D62;
}
.hero {
    position: relative;
    overflow: hidden;
    padding: 32px 34px;
    margin-bottom: 22px;
    border-radius: 24px;
    color: white;
    background: linear-gradient(120deg, #102D25 0%, #145B45 55%, #13866B 100%);
    box-shadow: 0 12px 35px rgba(16, 77, 57, .16);
}
.hero:after {
    content: "";
    position: absolute;
    width: 240px;
    height: 240px;
    border: 1px solid rgba(255,255,255,.14);
    border-radius: 50%;
    right: -50px;
    top: -115px;
    box-shadow: 0 0 0 28px rgba(255,255,255,.035),
                0 0 0 58px rgba(255,255,255,.025);
}
.hero h1 {
    color: #FFFFFF !important;
    font-size: 2.6rem;
    font-weight: 800;
    margin: 0;
}
.hero p {
    color: #D5F5E8 !important;
    margin: 6px 0 0 0;
    font-size: 1rem;
}
.hero-tag {
    display: inline-block;
    color: #BDF7DF;
    border: 1px solid rgba(189,247,223,.3);
    background: rgba(255,255,255,.08);
    padding: 5px 11px;
    border-radius: 99px;
    font-size: .78rem;
    margin-bottom: 12px;
}
[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #DFEAE3;
    border-radius: 17px;
    padding: 17px 19px;
    box-shadow: 0 4px 14px rgba(20, 55, 41, .035);
    transition: transform .18s ease, box-shadow .18s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 9px 22px rgba(20, 55, 41, .08);
}
[data-testid="stMetricLabel"] {
    color: #688077 !important;
}
[data-testid="stMetricValue"] {
    color: #173C2E !important;
    font-family: 'Manrope', sans-serif;
    font-weight: 800;
}
[data-testid="stMetricDelta"] {
    font-size: .78rem;
}
[data-testid="stTabs"] button {
    border-radius: 10px;
    font-weight: 600;
    color: #426357;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #087A54;
}
div[data-testid="stPlotlyChart"] {
    background: #FFFFFF;
    border: 1px solid #E1EBE5;
    border-radius: 17px;
    padding: 8px;
    box-shadow: 0 4px 16px rgba(20, 55, 41, .025);
}
div[data-testid="stDataFrame"] {
    border: 1px solid #DFEAE3;
    border-radius: 12px;
    overflow: hidden;
}
.stButton button, .stDownloadButton button {
    border-radius: 10px;
    font-weight: 600;
}
.stButton button[kind="primary"] {
    background: #087A54;
    border: 0;
}
.section-label {
    color: #14805D;
    font-size: .75rem;
    font-weight: 800;
    letter-spacing: 1.7px;
    text-transform: uppercase;
    margin-bottom: 4px;
}
div[data-testid="stAlert"] {
    border-radius: 12px;
}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="hero-tag">● DATA INTELLIGENCE PLATFORM</div>
  <h1>🌿 AirSight</h1>
  <p>Air Quality & Weather Analytics · Explore the patterns behind the air we breathe.</p>
</div>
""", unsafe_allow_html=True)

# ---------------------- DEMO DATA ----------------------
@st.cache_data
def create_demo_data():
    rng = np.random.default_rng(42)
    places = [
        ("Delhi", "Delhi"), ("Mumbai", "Maharashtra"),
        ("Hyderabad", "Telangana"), ("Vijayawada", "Andhra Pradesh"),
        ("Kolkata", "West Bengal"), ("Bengaluru", "Karnataka"),
        ("Chennai", "Tamil Nadu"), ("Jaipur", "Rajasthan")
    ]
    dates = pd.date_range("2025-01-01", periods=180, freq="D")
    rows = []
    for i, date in enumerate(dates):
        for city, state in places:
            seasonal = 1 + .22 * np.sin(i / 18)
            rows.append({
                "Date": date,
                "City": city,
                "State": state,
                "PM2.5": round(max(3, rng.normal(45, 18) * seasonal), 1),
                "PM10": round(max(8, rng.normal(88, 28) * seasonal), 1),
                "NO2": round(max(2, rng.normal(23, 7)), 1),
                "SO2": round(max(1, rng.normal(10, 3)), 1),
                "CO": round(max(.1, rng.normal(.8, .2)), 2),
                "O3": round(max(2, rng.normal(32, 10)), 1),
                "Temperature": round(rng.normal(28, 5), 1),
                "Humidity": round(np.clip(rng.normal(60, 15), 15, 98), 1)
            })
    return pd.DataFrame(rows)

# ---------------------- DATA SOURCE ----------------------
st.sidebar.markdown("## 🌿 AirSight")
st.sidebar.caption("AIR QUALITY INTELLIGENCE")
st.sidebar.divider()

with st.sidebar.expander("📂 Data source (optional)", expanded=False):
    uploaded = st.file_uploader(
        "Upload your project CSV",
        type=["csv"],
        help="Optional. Without an upload, AirSight opens with synthetic demonstration data."
    )
    st.caption("For your final presentation, use your actual dataset.")

if uploaded is not None:
    try:
        df = pd.read_csv(uploaded)
        data_mode = "Uploaded dataset"
    except Exception as e:
        st.error(f"Unable to read the uploaded CSV: {e}")
        st.stop()
else:
    df = create_demo_data()
    data_mode = "Synthetic demo data"

df.columns = [str(c).strip() for c in df.columns]
df = df.dropna(how="all").copy()

if df.empty:
    st.error("This dataset has no usable rows.")
    st.stop()

# Convert columns containing mostly numeric values
for c in df.columns:
    if df[c].dtype == "object":
        cleaned = df[c].astype(str).str.strip()
        converted = pd.to_numeric(
            cleaned.str.replace(",", "", regex=False), errors="coerce"
        )
        valid_count = cleaned.ne("").sum()
        if valid_count and converted.notna().sum() / valid_count >= .85:
            df[c] = converted

def detect(aliases):
    lookup = {str(c).strip().lower().replace("_", "").replace(" ", ""): c
              for c in df.columns}
    for alias in aliases:
        key = alias.lower().replace("_", "").replace(" ", "")
        if key in lookup:
            return lookup[key]
    return None

date_col = detect(["date", "datetime", "timestamp", "measurement_date"])
city_col = detect(["city", "city_name", "location", "station", "place"])
state_col = detect(["state", "state_name", "region"])
aqi_col = detect(["aqi", "air_quality_index", "india_aqi", "us_aqi"])
lat_col = detect(["latitude", "lat"])
lon_col = detect(["longitude", "lon", "lng"])

numeric_cols = df.select_dtypes(include="number").columns.tolist()
pollutant_cols = [
    c for c in numeric_cols
    if any(p in str(c).lower().replace(" ", "").replace("_", "")
           for p in ["pm2.5", "pm25", "pm10", "no2", "so2", "co", "o3", "aqi"])
]
if not pollutant_cols:
    pollutant_cols = numeric_cols

if data_mode == "Synthetic demo data":
    st.info(
        "DEMO MODE · Showing generated example data, not live or official "
        "air-quality observations. Upload your real project CSV when available."
    )
else:
    st.success(f"Data loaded successfully · {len(df):,} records · {len(df.columns)} columns")

# ---------------------- FILTERS ----------------------
st.sidebar.markdown("### 🎛️ Dashboard filters")
view = df.copy()

if state_col:
    state_options = sorted(view[state_col].dropna().astype(str).unique())
    selected_states = st.sidebar.multiselect(
        "State / region", state_options, default=state_options
    )
    view = view[view[state_col].astype(str).isin(selected_states)]

if city_col:
    city_options = sorted(view[city_col].dropna().astype(str).unique())
    selected_cities = st.sidebar.multiselect(
        "City / location", city_options, default=city_options
    )
    view = view[view[city_col].astype(str).isin(selected_cities)]

if date_col:
    parsed = pd.to_datetime(view[date_col], errors="coerce")
    valid = parsed.dropna()
    if not valid.empty:
        low, high = valid.min().date(), valid.max().date()
        date_range = st.sidebar.date_input(
            "Date range", value=(low, high), min_value=low, max_value=high
        )
        if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
            start = pd.Timestamp(date_range[0])
            end = pd.Timestamp(date_range[1]) + pd.Timedelta(days=1)
            view_dates = pd.to_datetime(view[date_col], errors="coerce")
            view = view[(view_dates >= start) & (view_dates < end)]

if view.empty:
    st.warning("No records match the filters. Clear a filter or select more locations.")
    st.stop()

# Recalculate candidates after loading and filtering
numeric_cols = view.select_dtypes(include="number").columns.tolist()
pollutant_cols = [
    c for c in numeric_cols
    if any(p in str(c).lower().replace(" ", "").replace("_", "")
           for p in ["pm2.5", "pm25", "pm10", "no2", "so2", "co", "o3", "aqi"])
]
if not pollutant_cols:
    pollutant_cols = numeric_cols

# Consistent Plotly styling
def polish(fig, height=360):
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=18, r=18, t=60, b=18),
        font=dict(family="DM Sans, sans-serif", color=INK, size=12),
        title=dict(font=dict(size=16, color=INK), x=0.02, xanchor="left"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1),
        hoverlabel=dict(bgcolor="#102D25", font_color="white"),
    )
    fig.update_xaxes(showgrid=False, linecolor="#E3ECE6")
    fig.update_yaxes(gridcolor="#EAF0EC", zeroline=False)
    return fig

def nice_num(x):
    return "—" if pd.isna(x) else f"{x:,.2f}"

# ---------------------- NAVIGATION ----------------------
tabs = st.tabs([
    "✨ Overview",
    "🧪 Pollutant Lab",
    "📍 Location Insights",
    "🗂️ Data Explorer",
    "🛡️ Data Quality"
])

# ---------------------- OVERVIEW ----------------------
with tabs[0]:
    st.markdown('<div class="section-label">LIVE VIEW OF SELECTED DATA</div>',
                unsafe_allow_html=True)
    st.header("Your air-quality overview")
    st.caption("Use the sidebar filters to explore different locations and dates.")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total records", f"{len(view):,}")
    k2.metric("Locations", f"{view[city_col].nunique():,}" if city_col else "N/A")
    k3.metric("Pollutant measures", f"{len(pollutant_cols):,}")
    k4.metric("Missing values", f"{int(view.isna().sum().sum()):,}")

    if pollutant_cols:
        default_measure = aqi_col if aqi_col in pollutant_cols else pollutant_cols[0]
        measure = st.selectbox(
            "Choose a measure", pollutant_cols,
            index=pollutant_cols.index(default_measure),
            key="overview_measure"
        )
        left, right = st.columns([1.55, 1])

        with left:
            if date_col:
                temp = view.copy()
                temp["_date"] = pd.to_datetime(temp[date_col], errors="coerce")
                trend = temp.dropna(subset=["_date"]).groupby(
                    temp["_date"].dt.date
                )[measure].mean().reset_index()
                trend.columns = ["Date", measure]
                fig = px.line(
                    trend, x="Date", y=measure,
                    title=f"{measure} · Daily trend",
                    markers=True
                )
                fig.update_traces(line=dict(color=GREEN, width=3),
                                  marker=dict(size=5))
                st.plotly_chart(polish(fig), use_container_width=True)
            elif city_col:
                summary = view.groupby(city_col)[measure].mean().reset_index()
                fig = px.bar(summary, x=city_col, y=measure,
                             title=f"Average {measure} by location",
                             color=measure, color_continuous_scale=["#BDEFE0", GREEN])
                st.plotly_chart(polish(fig), use_container_width=True)
            else:
                st.info("A date or location column is needed for a trend chart.")

        with right:
            stats = view[measure].describe()
            st.markdown("#### Statistical snapshot")
            for label, key in [
                ("Average", "mean"), ("Median", "50%"),
                ("Minimum", "min"), ("Maximum", "max")
            ]:
                st.metric(label, nice_num(stats.get(key, np.nan)))
            st.caption("Statistics describe the selected data and its units.")

        if city_col:
            summary = view.groupby(city_col)[measure].mean().reset_index()
            summary = summary.sort_values(measure, ascending=False)
            fig = px.bar(
                summary, x=city_col, y=measure,
                title=f"Location comparison · Average {measure}",
                color=measure, color_continuous_scale=["#BDEFE0", GREEN],
                hover_data={measure: ":.2f"}
            )
            st.plotly_chart(polish(fig, 380), use_container_width=True)
    else:
        st.warning("No numeric measures detected. Check the CSV column names and data types.")

# ---------------------- POLLUTANT LAB ----------------------
with tabs[1]:
    st.markdown('<div class="section-label">DISTRIBUTIONS · VARIABILITY · RELATIONSHIPS</div>',
                unsafe_allow_html=True)
    st.header("Pollutant exploration")
    if not pollutant_cols:
        st.warning("No numeric pollutant or measure columns are available.")
    else:
        measure = st.selectbox("Select a pollutant / numeric measure",
                               pollutant_cols, key="lab_measure")
        values = pd.to_numeric(view[measure], errors="coerce").dropna()
        a, b, c, d = st.columns(4)
        a.metric("Valid readings", f"{len(values):,}")
        b.metric("Mean", nice_num(values.mean()))
        c.metric("Median", nice_num(values.median()))
        d.metric("Standard deviation", nice_num(values.std()))

        left, right = st.columns(2)
        with left:
            fig = px.histogram(
                view, x=measure, nbins=35, marginal="rug",
                title=f"Distribution of {measure}",
                color_discrete_sequence=[GREEN]
            )
            st.plotly_chart(polish(fig), use_container_width=True)
        with right:
            fig = px.box(
                view, y=measure, points="outliers",
                title=f"Spread and potential outliers",
                color_discrete_sequence=[TEAL]
            )
            st.plotly_chart(polish(fig), use_container_width=True)

        if len(pollutant_cols) >= 2:
            st.subheader("Correlation explorer")
            st.caption("Correlation shows linear association, not causation.")
            corr = view[pollutant_cols].corr(numeric_only=True)
            fig = px.imshow(
                corr, text_auto=".2f", aspect="auto",
                color_continuous_scale=[
                    "#EAF5EF", "#80D9B7", "#15966D", "#15513D"
                ],
                zmin=-1, zmax=1, title="Pollutant correlation matrix"
            )
            st.plotly_chart(polish(fig, 470), use_container_width=True)

# ---------------------- LOCATION INSIGHTS ----------------------
with tabs[2]:
    st.markdown('<div class="section-label">COMPARE PLACES · FIND PATTERNS</div>',
                unsafe_allow_html=True)
    st.header("Location intelligence")
    location_col = state_col or city_col

    if location_col and pollutant_cols:
        measure = st.selectbox("Measure to compare", pollutant_cols, key="location_measure")
        summary = view.groupby(location_col)[measure].agg(
            Average="mean", Median="median", Records="count"
        ).reset_index().sort_values("Average", ascending=False)

        fig = px.bar(
            summary, x=location_col, y="Average",
            color="Average", color_continuous_scale=["#C5F1E1", GREEN],
            hover_data=["Median", "Records"],
            title=f"Average {measure} across {location_col}"
        )
        st.plotly_chart(polish(fig, 420), use_container_width=True)
        st.subheader("Ranked comparison")
        st.dataframe(summary, use_container_width=True, hide_index=True)

        if lat_col and lon_col:
            coords = view[[lat_col, lon_col]].copy()
            coords[lat_col] = pd.to_numeric(coords[lat_col], errors="coerce")
            coords[lon_col] = pd.to_numeric(coords[lon_col], errors="coerce")
            coords = coords.dropna()
            coords = coords[
                coords[lat_col].between(-90, 90) &
                coords[lon_col].between(-180, 180)
            ]
            if not coords.empty:
                st.subheader("Recorded coordinates")
                st.map(coords, latitude=lat_col, longitude=lon_col)
    else:
        st.info("This section needs a location column and at least one numeric measure.")

# ---------------------- DATA EXPLORER ----------------------
with tabs[3]:
    st.markdown('<div class="section-label">SEARCH · INSPECT · EXPORT</div>',
                unsafe_allow_html=True)
    st.header("Explore your dataset")
    search = st.text_input("🔎 Search all columns", placeholder="Search a city, state, or value...")
    result = view.copy()
    if search.strip():
        mask = result.astype(str).apply(
            lambda col: col.str.contains(search.strip(), case=False, na=False)
        )
        result = result[mask.any(axis=1)]

    st.caption(f"Showing {len(result):,} of {len(view):,} selected records")
    st.dataframe(result, use_container_width=True, hide_index=True, height=430)
    st.download_button(
        "⬇️ Download selected records (CSV)",
        result.to_csv(index=False).encode("utf-8"),
        file_name="airsight_filtered_data.csv",
        mime="text/csv",
        type="primary"
    )

# ---------------------- DATA QUALITY ----------------------
with tabs[4]:
    st.markdown('<div class="section-label">TRANSPARENCY · RELIABILITY · COMPLETENESS</div>',
                unsafe_allow_html=True)
    st.header("Data quality centre")
    total = view.shape[0] * view.shape[1]
    missing = int(view.isna().sum().sum())
    duplicates = int(view.duplicated().sum())
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Rows", f"{len(view):,}")
    q2.metric("Columns", f"{len(view.columns):,}")
    q3.metric("Missing cells", f"{missing:,}",
              f"{missing / total * 100:.1f}% of cells" if total else "—")
    q4.metric("Duplicate rows", f"{duplicates:,}")

    missing_df = view.isna().sum().rename("Missing values").reset_index()
    missing_df.columns = ["Column", "Missing values"]
    missing_df = missing_df[missing_df["Missing values"] > 0]
    if not missing_df.empty:
        fig = px.bar(
            missing_df, x="Column", y="Missing values",
            color="Missing values", color_continuous_scale=["#FDE68A", RED],
            title="Missing values by column"
        )
        st.plotly_chart(polish(fig), use_container_width=True)
        st.dataframe(missing_df, use_container_width=True, hide_index=True)
    else:
        st.success("No missing values found in the current selection.")

    types = pd.DataFrame({
        "Column": view.columns,
        "Data type": [str(t) for t in view.dtypes],
        "Unique values": [view[c].nunique(dropna=True) for c in view.columns]
    })
    st.subheader("Column profile")
    st.dataframe(types, use_container_width=True, hide_index=True)

# ---------------------- FOOTER ----------------------
st.divider()
st.caption(
    "AirSight · Data Analytics & Exploration project · "
    "Charts are based on the currently selected dataset. "
    "Demo values are synthetic, not live AQI readings."
)
