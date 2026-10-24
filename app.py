
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# AIRSIGHT | AIR QUALITY & WEATHER ANALYTICS
# Complete single-file Streamlit application
# ============================================================

st.set_page_config(
    page_title="AirSight | Air Quality Intelligence",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------- THEME -----------------------------

BG = "#F3F7F4"
WHITE = "#FFFFFF"
INK = "#18372D"
MUTED = "#526D62"
GREEN = "#0DAB78"
DARK_GREEN = "#123C30"
MINT = "#B8F2D9"
BLUE = "#3978D4"
TEAL = "#14B8A6"
AMBER = "#E9A23B"
RED = "#E65C6A"
PURPLE = "#8B79D9"

PALETTE = [GREEN, BLUE, TEAL, AMBER, RED, PURPLE, "#E879B0"]

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --green: #0DAB78;
    --dark: #123C30;
    --ink: #18372D;
    --muted: #526D62;
    --border: #DFEAE3;
}

.stApp {
    background: #F3F7F4;
    color: #18372D;
    font-family: 'DM Sans', sans-serif;
}
[data-testid="stHeader"] {
    background: rgba(243,247,244,.96);
}
.block-container {
    max-width: 1500px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}
h1, h2, h3, h4 {
    color: #18372D !important;
    font-family: 'Manrope', sans-serif;
    letter-spacing: -.4px;
}
p, label, .stMarkdown, [data-testid="stCaptionContainer"] {
    color: #526D62;
}
.hero {
    position: relative;
    overflow: hidden;
    padding: 34px;
    margin-bottom: 22px;
    border-radius: 24px;
    color: white;
    background: linear-gradient(120deg, #102D25, #145B45 55%, #119477);
    box-shadow: 0 12px 35px rgba(16,77,57,.15);
}
.hero:after {
    content: "";
    position: absolute;
    width: 230px;
    height: 230px;
    right: -60px;
    top: -110px;
    border: 1px solid rgba(255,255,255,.15);
    border-radius: 50%;
    box-shadow: 0 0 0 28px rgba(255,255,255,.035),
                0 0 0 58px rgba(255,255,255,.025);
    pointer-events: none;
}
.hero h1 {
    color: #FFFFFF !important;
    font-size: 2.65rem;
    font-weight: 800;
    margin: 0;
}
.hero p {
    color: #D8F5E9 !important;
    margin: 8px 0 0 0;
    font-size: 1rem;
}
.hero-tag {
    display: inline-block;
    color: #C8F8E4;
    border: 1px solid rgba(200,248,228,.3);
    background: rgba(255,255,255,.08);
    padding: 5px 11px;
    border-radius: 99px;
    font-size: .76rem;
    letter-spacing: 1px;
    margin-bottom: 12px;
}
[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #DFEAE3;
    border-radius: 17px;
    padding: 17px 19px;
    box-shadow: 0 4px 14px rgba(20,55,41,.035);
    transition: transform .18s ease, box-shadow .18s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 9px 22px rgba(20,55,41,.08);
}
[data-testid="stMetricLabel"] {
    color: #526D62 !important;
}
[data-testid="stMetricValue"] {
    color: #18372D !important;
    font-family: 'Manrope', sans-serif;
    font-weight: 800;
}
[data-testid="stMetricDelta"] {
    font-size: .78rem;
}
[data-testid="stTabs"] button {
    color: #36594B;
    font-weight: 600;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #087A54;
}
div[data-testid="stPlotlyChart"] {
    background: #FFFFFF;
    border: 1px solid #DFEAE3;
    border-radius: 17px;
    padding: 8px;
    box-shadow: 0 4px 16px rgba(20,55,41,.025);
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
    color: #087A54;
    font-size: .74rem;
    font-weight: 800;
    letter-spacing: 1.7px;
    text-transform: uppercase;
    margin-bottom: 4px;
}
div[data-testid="stAlert"] {
    border-radius: 12px;
}
footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <div class="hero-tag">● AIR QUALITY INTELLIGENCE PLATFORM</div>
    <h1>🌿 AirSight</h1>
    <p>Air Quality & Weather Analytics · Explore the patterns behind the air we breathe.</p>
</div>
""", unsafe_allow_html=True)


# --------------------- DEMONSTRATION DATA -------------------

@st.cache_data
def create_demo_data():
    """Generate clearly labelled synthetic data for exploring the dashboard."""
    rng = np.random.default_rng(42)

    places = [
        ("Delhi", "Delhi"),
        ("Mumbai", "Maharashtra"),
        ("Hyderabad", "Telangana"),
        ("Vijayawada", "Andhra Pradesh"),
        ("Kolkata", "West Bengal"),
        ("Bengaluru", "Karnataka"),
        ("Chennai", "Tamil Nadu"),
        ("Jaipur", "Rajasthan"),
    ]

    dates = pd.date_range("2025-01-01", periods=180, freq="D")
    rows = []

    for i, date in enumerate(dates):
        seasonal = 1 + 0.20 * np.sin(i / 18)

        for city, state in places:
            rows.append({
                "Date": date,
                "City": city,
                "State": state,
                "PM2.5": round(max(3, rng.normal(45, 18) * seasonal), 1),
                "PM10": round(max(8, rng.normal(88, 28) * seasonal), 1),
                "NO2": round(max(2, rng.normal(23, 7)), 1),
                "SO2": round(max(1, rng.normal(10, 3)), 1),
                "CO": round(max(0.1, rng.normal(0.8, 0.2)), 2),
                "O3": round(max(2, rng.normal(32, 10)), 1),
                "Temperature": round(rng.normal(28, 5), 1),
                "Humidity": round(np.clip(rng.normal(60, 15), 15, 98), 1),
            })

    return pd.DataFrame(rows)


# --------------------- DATA UTILITIES -----------------------

def normalise_name(value):
    """Normalise names for flexible CSV column detection."""
    return "".join(ch.lower() for ch in str(value) if ch.isalnum())


def detect_column(columns, aliases):
    lookup = {normalise_name(col): col for col in columns}

    for alias in aliases:
        key = normalise_name(alias)
        if key in lookup:
            return lookup[key]

    return None


def numeric_conversion(frame):
    """Convert columns to numeric only when most non-empty values are numeric."""
    frame = frame.copy()

    for col in frame.columns:
        if frame[col].dtype == "object":
            cleaned = frame[col].astype(str).str.strip()
            cleaned = cleaned.replace({"": np.nan, "nan": np.nan, "None": np.nan})

            converted = pd.to_numeric(
                cleaned.str.replace(",", "", regex=False),
                errors="coerce",
            )

            nonempty = cleaned.notna().sum()

            if nonempty > 0 and converted.notna().sum() / nonempty >= 0.85:
                frame[col] = converted
            else:
                frame[col] = frame[col].replace({"": np.nan})

    return frame


def polish(fig, height=390):
    """Consistent chart theme with readable axes and interactive hover labels."""
    fig.update_layout(
        template="plotly_white",
        height=height,
        autosize=True,
        margin=dict(l=75, r=30, t=78, b=75),
        font=dict(
            family="Arial, sans-serif",
            size=13,
            color=INK,
        ),
        title=dict(
            font=dict(size=18, color=DARK_GREEN),
            x=0.025,
            xanchor="left",
        ),
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        hovermode="closest",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12, color=INK),
            bgcolor="rgba(255,255,255,0.9)",
        ),
        hoverlabel=dict(
            bgcolor=DARK_GREEN,
            bordercolor=GREEN,
            font=dict(color=WHITE, size=13),
        ),
    )

    axis_style = dict(
        showgrid=True,
        gridcolor="#E5EDE8",
        gridwidth=1,
        zeroline=False,
        showline=True,
        linecolor="#B9C9BF",
        linewidth=1,
        tickfont=dict(size=12, color="#344E43"),
        title_font=dict(size=14, color="#203D31"),
        automargin=True,
        ticks="outside",
        tickcolor="#B9C9BF",
    )

    fig.update_xaxes(**axis_style)
    fig.update_yaxes(**axis_style)

    return fig


def nice_num(value):
    if pd.isna(value):
        return "—"
    return f"{value:,.2f}"


def chart_line(frame, x, y, title, x_title, y_title, show_average=False):
    """Build a reusable, readable time-series chart."""
    data = frame[[x, y]].copy()
    data[x] = pd.to_datetime(data[x], errors="coerce")
    data[y] = pd.to_numeric(data[y], errors="coerce")
    data = data.dropna().sort_values(x)

    if data.empty:
        return None

    data = data.groupby(x, as_index=False)[y].mean()
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=data[x],
        y=data[y],
        mode="lines+markers",
        name=y,
        line=dict(color=GREEN, width=2.5),
        marker=dict(size=5, color=GREEN),
        hovertemplate=(
            "<b>%{x|%d %b %Y}</b><br>"
            + y + ": %{y:.2f}<extra></extra>"
        ),
    ))

    if show_average:
        data["Moving average"] = data[y].rolling(7, min_periods=1).mean()

        fig.add_trace(go.Scatter(
            x=data[x],
            y=data["Moving average"],
            mode="lines",
            name="7-day moving average",
            line=dict(color=BLUE, width=3),
            hovertemplate=(
                "<b>%{x|%d %b %Y}</b><br>"
                "7-day average: %{y:.2f}<extra></extra>"
            ),
        ))

    fig.update_layout(
        title=title,
        xaxis_title=x_title,
        yaxis_title=y_title,
        hovermode="x unified",
    )

    fig.update_xaxes(tickformat="%b %Y", nticks=7, rangeslider_visible=True)
    return polish(fig, 440)


# --------------------- SIDEBAR / DATA SOURCE ----------------

st.sidebar.markdown("## 🌿 AirSight")
st.sidebar.caption("AIR QUALITY ANALYTICS")
st.sidebar.divider()

st.sidebar.markdown("### 📂 Data source")

uploaded = st.sidebar.file_uploader(
    "Upload your CSV (optional)",
    type=["csv"],
    help=(
        "The dashboard works without an upload. "
        "Use your real project dataset for final analysis."
    ),
)

if uploaded is None:
    df = create_demo_data()
    data_mode = "Synthetic demonstration data"
else:
    try:
        df = pd.read_csv(uploaded)
        data_mode = "Uploaded dataset"
    except Exception as exc:
        st.error(f"Unable to read this CSV: {exc}")
        st.stop()

df.columns = [str(col).strip() for col in df.columns]
df = df.dropna(how="all").copy()

if df.empty:
    st.error("The selected dataset contains no usable rows.")
    st.stop()

df = numeric_conversion(df)

if data_mode == "Synthetic demonstration data":
    st.info(
        "DEMO MODE · These are generated example values, not live or official "
        "air-quality measurements. Upload your real dataset for your final DAE analysis."
    )
else:
    st.success(
        f"Dataset loaded · {len(df):,} rows · {len(df.columns)} columns"
    )

# Detect common column names
date_col = detect_column(
    df.columns,
    ["date", "datetime", "timestamp", "measurement_date", "time"],
)
city_col = detect_column(
    df.columns,
    ["city", "city_name", "location", "station", "place"],
)
state_col = detect_column(
    df.columns,
    ["state", "state_name", "region"],
)
aqi_col = detect_column(
    df.columns,
    ["aqi", "air_quality_index", "india_aqi", "us_aqi"],
)
lat_col = detect_column(df.columns, ["latitude", "lat"])
lon_col = detect_column(df.columns, ["longitude", "lon", "lng"])

# --------------------- SIDEBAR FILTERS -----------------------

st.sidebar.divider()
st.sidebar.markdown("### 🎛️ Explore your data")

view = df.copy()

if state_col:
    states = sorted(view[state_col].dropna().astype(str).unique())
    chosen_states = st.sidebar.multiselect(
        "State / region",
        states,
        default=states,
    )

    if chosen_states:
        view = view[view[state_col].astype(str).isin(chosen_states)]
    else:
        view = view.iloc[0:0]

if city_col and not view.empty:
    cities = sorted(view[city_col].dropna().astype(str).unique())
    chosen_cities = st.sidebar.multiselect(
        "City / location",
        cities,
        default=cities,
    )

    if chosen_cities:
        view = view[view[city_col].astype(str).isin(chosen_cities)]
    else:
        view = view.iloc[0:0]

if date_col and not view.empty:
    parsed_dates = pd.to_datetime(view[date_col], errors="coerce")
    valid_dates = parsed_dates.dropna()

    if not valid_dates.empty:
        earliest = valid_dates.min().date()
        latest = valid_dates.max().date()

        if earliest < latest:
            selected_dates = st.sidebar.date_input(
                "Date range",
                value=(earliest, latest),
                min_value=earliest,
                max_value=latest,
            )

            if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
                start_date = pd.Timestamp(selected_dates[0])
                end_date = pd.Timestamp(selected_dates[1]) + pd.Timedelta(days=1)

                parsed = pd.to_datetime(view[date_col], errors="coerce")
                view = view[(parsed >= start_date) & (parsed < end_date)]

if view.empty:
    st.warning(
        "No rows match your current filters. Select at least one location "
        "or clear a filter in the sidebar."
    )
    st.stop()

st.sidebar.caption(f"Showing {len(view):,} selected records")

# Identify numeric measures after loading and filtering
numeric_cols = view.select_dtypes(include="number").columns.tolist()

pollutant_cols = [
    col for col in numeric_cols
    if any(token in normalise_name(col) for token in [
        "pm25", "pm10", "no2", "so2", "co", "o3", "aqi"
    ])
]

if not pollutant_cols:
    pollutant_cols = numeric_cols

# --------------------- NAVIGATION ----------------------------

tabs = st.tabs([
    "✨ Overview",
    "🧪 Pollutant Lab",
    "📍 Location Insights",
    "🗂️ Data Explorer",
    "🛡️ Data Quality",
])


# ======================= OVERVIEW ============================

with tabs[0]:
    st.markdown(
        '<div class="section-label">AIR QUALITY · TRENDS · DISCOVERY</div>',
        unsafe_allow_html=True,
    )
    st.header("Air quality at a glance")
    st.caption(
        "Explore measurements, compare locations and discover patterns "
        "in the currently selected dataset."
    )

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total records", f"{len(view):,}")
    k2.metric(
        "Locations",
        f"{view[city_col].nunique():,}" if city_col else "Not available",
    )
    k3.metric("Numeric measures", f"{len(numeric_cols):,}")
    k4.metric("Missing cells", f"{int(view.isna().sum().sum()):,}")

    st.divider()

    if not pollutant_cols:
        st.warning(
            "No numeric measurements were detected. Check your CSV column "
            "names and ensure measurements are stored as numbers."
        )
    else:
        default_measure = (
            aqi_col if aqi_col in pollutant_cols else pollutant_cols[0]
        )

        control1, control2 = st.columns([2, 1])

        with control1:
            measure = st.selectbox(
                "🧪 Select a pollutant or numeric measure",
                pollutant_cols,
                index=pollutant_cols.index(default_measure),
                key="overview_measure",
            )

        with control2:
            show_average = st.checkbox(
                "Show 7-day moving average",
                value=True,
                key="overview_average",
            )

        valid_values = pd.to_numeric(view[measure], errors="coerce").dropna()

        s1, s2, s3 = st.columns(3)
        s1.metric("Average reading", nice_num(valid_values.mean()))
        s2.metric("Median reading", nice_num(valid_values.median()))
        s3.metric("Highest reading", nice_num(valid_values.max()))

        st.markdown("### 📈 Measurement trends")

        if date_col:
            trend_fig = chart_line(
                view,
                date_col,
                measure,
                f"{measure} · Daily trend",
                "Date",
                f"{measure} (dataset units)",
                show_average=show_average,
            )

            if trend_fig is not None:
                st.plotly_chart(
                    trend_fig,
                    use_container_width=True,
                    key="overview_trend",
                )
                st.caption(
                    "Daily averages are shown where dates are available. "
                    "The moving average smooths fluctuations; it does not "
                    "predict future readings."
                )
            else:
                st.info("No valid date and measurement pairs were found.")
        elif city_col:
            location_data = (
                view.groupby(city_col, as_index=False)[measure]
                .mean()
                .dropna()
                .sort_values(measure)
            )

            fig = px.bar(
                location_data,
                x=measure,
                y=city_col,
                orientation="h",
                title=f"Average {measure} by location",
                color=measure,
                color_continuous_scale=["#B8F2D9", GREEN, DARK_GREEN],
                labels={measure: f"{measure} (dataset units)", city_col: "Location"},
            )
            st.plotly_chart(
                polish(fig, 420),
                use_container_width=True,
                key="overview_location",
            )
        else:
            st.info(
                "A date or location column is needed to display a trend chart."
            )

        if city_col:
            st.markdown("### 📍 Location comparison")

            comparison = (
                view.groupby(city_col)[measure]
                .agg(["mean", "median", "count"])
                .reset_index()
                .rename(columns={
                    "mean": "Average",
                    "median": "Median",
                    "count": "Readings",
                })
                .dropna(subset=["Average"])
                .sort_values("Average", ascending=False)
            )

            if not comparison.empty:
                fig = px.bar(
                    comparison,
                    x=city_col,
                    y="Average",
                    color="Average",
                    color_continuous_scale=["#B8F2D9", GREEN, DARK_GREEN],
                    hover_data={"Median": ":.2f", "Readings": True},
                    title=f"Location ranking · Average {measure}",
                    labels={
                        city_col: "Location",
                        "Average": f"Average {measure} (dataset units)",
                    },
                )
                st.plotly_chart(
                    polish(fig, 410),
                    use_container_width=True,
                    key="overview_ranking",
                )

                with st.expander("View location statistics"):
                    st.dataframe(
                        comparison,
                        use_container_width=True,
                        hide_index=True,
                    )


# ===================== POLLUTANT LAB ========================

with tabs[1]:
    st.markdown(
        '<div class="section-label">DISTRIBUTIONS · VARIABILITY · RELATIONSHIPS</div>',
        unsafe_allow_html=True,
    )
    st.header("Pollutant exploration")
    st.caption(
        "Explore the distribution, spread and relationships of numeric measurements."
    )

    if not pollutant_cols:
        st.warning("No numeric pollutant or measurement columns are available.")
    else:
        measure = st.selectbox(
            "Select a measurement",
            pollutant_cols,
            key="lab_measure",
        )
        values = pd.to_numeric(view[measure], errors="coerce").dropna()

        a, b, c, d = st.columns(4)
        a.metric("Valid readings", f"{len(values):,}")
        b.metric("Mean", nice_num(values.mean()))
        c.metric("Median", nice_num(values.median()))
        d.metric("Standard deviation", nice_num(values.std()))

        left, right = st.columns(2)

        with left:
            fig = px.histogram(
                view,
                x=measure,
                nbins=35,
                marginal="rug",
                title=f"Distribution of {measure}",
                color_discrete_sequence=[GREEN],
                labels={measure: f"{measure} (dataset units)"},
            )
            st.plotly_chart(
                polish(fig),
                use_container_width=True,
                key="lab_histogram",
            )

        with right:
            fig = px.box(
                view,
                y=measure,
                points="outliers",
                title=f"Spread and potential outliers · {measure}",
                color_discrete_sequence=[TEAL],
                labels={measure: f"{measure} (dataset units)"},
            )
            st.plotly_chart(
                polish(fig),
                use_container_width=True,
                key="lab_box",
            )

        if len(pollutant_cols) >= 2:
            st.markdown("### 🔗 Correlation explorer")
            st.caption(
                "Correlation measures linear association. It does not establish causation."
            )

            corr = view[pollutant_cols].corr(numeric_only=True)

            fig = px.imshow(
                corr,
                text_auto=".2f",
                aspect="auto",
                color_continuous_scale=[
                    "#F5F7F5", "#B8F2D9", GREEN, DARK_GREEN
                ],
                zmin=-1,
                zmax=1,
                title="Correlation matrix",
            )
            fig.update_layout(
                xaxis_title="Measurement",
                yaxis_title="Measurement",
            )
            st.plotly_chart(
                polish(fig, 490),
                use_container_width=True,
                key="lab_correlation",
            )
        else:
            st.info(
                "At least two numeric measures are required for a correlation matrix."
            )


# ===================== LOCATION INSIGHTS =====================

with tabs[2]:
    st.markdown(
        '<div class="section-label">COMPARE PLACES · FIND PATTERNS</div>',
        unsafe_allow_html=True,
    )
    st.header("Location intelligence")

    location_col = city_col or state_col

    if location_col and pollutant_cols:
        measure = st.selectbox(
            "Measure to compare",
            pollutant_cols,
            key="location_measure",
        )

        summary = (
            view.groupby(location_col)[measure]
            .agg(["mean", "median", "count"])
            .reset_index()
            .rename(columns={
                "mean": "Average",
                "median": "Median",
                "count": "Readings",
            })
            .dropna(subset=["Average"])
            .sort_values("Average", ascending=False)
        )

        fig = px.bar(
            summary,
            x=location_col,
            y="Average",
            color="Average",
            color_continuous_scale=["#B8F2D9", GREEN, DARK_GREEN],
            hover_data={"Median": ":.2f", "Readings": True},
            title=f"Average {measure} by {location_col}",
            labels={
                location_col: "Location",
                "Average": f"Average {measure} (dataset units)",
            },
        )
        st.plotly_chart(
            polish(fig, 430),
            use_container_width=True,
            key="location_comparison",
        )

        st.markdown("### 🏆 Location rankings")
        st.dataframe(
            summary,
            use_container_width=True,
            hide_index=True,
        )

        if lat_col and lon_col:
            coords = view[[lat_col, lon_col]].copy()
            coords[lat_col] = pd.to_numeric(coords[lat_col], errors="coerce")
            coords[lon_col] = pd.to_numeric(coords[lon_col], errors="coerce")
            coords = coords.dropna()
            coords = coords[
                coords[lat_col].between(-90, 90)
                & coords[lon_col].between(-180, 180)
            ]

            if not coords.empty:
                st.markdown("### 🗺️ Recorded coordinates")
                st.map(coords, latitude=lat_col, longitude=lon_col)
    else:
        st.info(
            "This section needs a recognised city or state column and at least "
            "one numeric measurement."
        )


# ======================= DATA EXPLORER ======================

with tabs[3]:
    st.markdown(
        '<div class="section-label">SEARCH · INSPECT · EXPORT</div>',
        unsafe_allow_html=True,
    )
    st.header("Explore your dataset")

    search = st.text_input(
        "🔎 Search across all columns",
        placeholder="Try a city name, state or value...",
    )

    result = view.copy()

    if search.strip():
        mask = result.astype(str).apply(
            lambda col: col.str.contains(
                search.strip(),
                case=False,
                na=False,
                regex=False,
            )
        )
        result = result[mask.any(axis=1)]

    st.caption(f"Showing {len(result):,} of {len(view):,} selected records")

    st.dataframe(
        result,
        use_container_width=True,
        hide_index=True,
        height=430,
    )

    st.download_button(
        "⬇️ Download selected records (CSV)",
        data=result.to_csv(index=False).encode("utf-8"),
        file_name="airsight_filtered_data.csv",
        mime="text/csv",
        type="primary",
    )


# ======================= DATA QUALITY =======================

with tabs[4]:
    st.markdown(
        '<div class="section-label">TRANSPARENCY · RELIABILITY · COMPLETENESS</div>',
        unsafe_allow_html=True,
    )
    st.header("Data quality centre")

    total_cells = view.shape[0] * view.shape[1]
    missing = int(view.isna().sum().sum())
    duplicates = int(view.duplicated().sum())
    missing_pct = (missing / total_cells * 100) if total_cells else 0

    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Rows", f"{len(view):,}")
    q2.metric("Columns", f"{len(view.columns):,}")
    q3.metric("Missing cells", f"{missing:,}", f"{missing_pct:.1f}% of cells")
    q4.metric("Duplicate rows", f"{duplicates:,}")

    missing_df = (
        view.isna().sum()
        .rename("Missing values")
        .reset_index()
    )
    missing_df.columns = ["Column", "Missing values"]
    missing_df = missing_df[missing_df["Missing values"] > 0]

    if not missing_df.empty:
        fig = px.bar(
            missing_df,
            x="Column",
            y="Missing values",
            color="Missing values",
            color_continuous_scale=["#FDE68A", RED],
            title="Missing values by column",
        )
        st.plotly_chart(
            polish(fig),
            use_container_width=True,
            key="quality_missing",
        )
        st.dataframe(
            missing_df,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.success("No missing values found in the current selection.")

    types = pd.DataFrame({
        "Column": view.columns,
        "Data type": [str(dtype) for dtype in view.dtypes],
        "Unique values": [view[col].nunique(dropna=True) for col in view.columns],
    })

    st.markdown("### Column profile")
    st.dataframe(
        types,
        use_container_width=True,
        hide_index=True,
    )

    if duplicates:
        st.caption(
            "Duplicate rows are counted for inspection; they are not removed automatically."
        )


# ========================== FOOTER ==========================

st.divider()
st.caption(
    "🌿 AirSight · Data Analytics & Exploration project · "
    "Interactive analysis of the selected dataset. "
    "Synthetic demonstration values are not live air-quality readings."
)
