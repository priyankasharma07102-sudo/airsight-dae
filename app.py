
import os
import requests
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# ============================================================
# AIRSIGHT | ENVIRONMENTAL INTELLIGENCE DASHBOARD
# Frontend connected to the AirSight FastAPI backend
# ============================================================

st.set_page_config(
    page_title="AirSight | Environmental Intelligence",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------- CONFIGURATION -------------------------

COLORS = [
    "#38D9C5", "#6CA8FF", "#A78BFA", "#F5B942",
    "#F4778B", "#56D69A", "#E99AD5", "#F59E5B",
]

POLLUTANTS = ["PM2.5", "PM10", "NO₂", "SO₂", "CO", "O₃"]

ALIASES = {
    "city": "City",
    "location": "City",
    "station": "City",
    "state": "State",
    "date": "Date",
    "datetime": "Date",
    "timestamp": "Date",
    "time": "Date",
    "measurement_date": "Date",
    "pm2_5": "PM2.5",
    "pm25": "PM2.5",
    "pm2.5": "PM2.5",
    "pm10": "PM10",
    "no2": "NO₂",
    "nitrogen_dioxide": "NO₂",
    "so2": "SO₂",
    "sulphur_dioxide": "SO₂",
    "co": "CO",
    "carbon_monoxide": "CO",
    "o3": "O₃",
    "ozone": "O₃",
    "us_aqi": "AQI",
    "european_aqi": "AQI",
    "air_quality_index": "AQI",
    "temperature": "Temperature",
    "temperature_2m": "Temperature",
    "temp": "Temperature",
    "humidity": "Humidity",
    "relative_humidity_2m": "Humidity",
    "wind_speed": "Wind Speed",
    "wind_speed_10m": "Wind Speed",
}

# ------------------------- THEME -------------------------

if "airsight_theme" not in st.session_state:
    st.session_state.airsight_theme = "Dark"

theme = st.session_state.airsight_theme

if theme == "Dark":
    C = {
        "bg": "#08111F",
        "card": "#111D2D",
        "text": "#F3F7FF",
        "muted": "#A5B4C8",
        "border": "#293A50",
        "grid": "#293A50",
        "hero": "#102A43",
        "plot": "plotly_dark",
    }
else:
    C = {
        "bg": "#F3F6FB",
        "card": "#FFFFFF",
        "text": "#152238",
        "muted": "#5F6F85",
        "border": "#DCE4EF",
        "grid": "#E1E8F0",
        "hero": "#E1F5F3",
        "plot": "plotly_white",
    }

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

    .stApp {{
        background: {C['bg']};
        color: {C['text']};
        font-family: 'DM Sans', sans-serif;
    }}

    .block-container {{
        max-width: 1600px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }}

    h1, h2, h3 {{
        color: {C['text']} !important;
        font-family: 'Manrope', sans-serif !important;
    }}

    p, label {{
        color: {C['muted']};
    }}

    [data-testid="stSidebar"] {{
        background: {C['card']};
        border-right: 1px solid {C['border']};
    }}

    [data-testid="stSidebar"] * {{
        color: {C['text']};
    }}

    .hero {{
        padding: 30px;
        border-radius: 22px;
        margin-bottom: 22px;
        background: linear-gradient(115deg, {C['hero']}, #124B55);
        border: 1px solid {C['border']};
    }}

    .hero h1 {{
        color: #FFFFFF !important;
        font-size: 2.7rem;
        font-weight: 800;
        margin-bottom: 4px;
    }}

    .hero p {{
        color: #E0EDF7;
    }}

    .eyebrow {{
        font-size: .75rem;
        letter-spacing: 2px;
        font-weight: 800;
        color: #38D9C5;
    }}

    [data-testid="stMetric"] {{
        background: {C['card']};
        border: 1px solid {C['border']};
        border-radius: 16px;
        padding: 17px;
        transition: transform .2s ease;
    }}

    [data-testid="stMetric"]:hover {{
        transform: translateY(-3px);
    }}

    [data-testid="stMetricLabel"] {{
        color: {C['muted']} !important;
    }}

    [data-testid="stMetricValue"] {{
        color: {C['text']} !important;
        font-family: 'Manrope', sans-serif;
        font-weight: 800;
    }}

    [data-testid="stPlotlyChart"] {{
        border: 1px solid {C['border']};
        border-radius: 16px;
        padding: 5px;
    }}

    .stButton button, .stDownloadButton button {{
        border-radius: 10px;
        font-weight: 700;
    }}

    hr {{
        border-color: {C['border']};
    }}

    footer {{
        visibility: hidden;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------- BACKEND CONNECTION -------------------------

def get_backend_url():
    """Read the backend URL from Streamlit Secrets or environment."""
    try:
        secret_url = st.secrets.get("AIRSIGHT_BACKEND_URL", "")
    except Exception:
        secret_url = ""

    return os.getenv(
        "AIRSIGHT_BACKEND_URL", secret_url
    ).strip().rstrip("/")


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_backend_data(backend_url):
    """Fetch the fixed dataset from the deployed FastAPI backend."""
    response = requests.get(
        f"{backend_url}/api/data",
        timeout=60,
    )
    response.raise_for_status()

    payload = response.json()

    if payload.get("status") != "success":
        raise ValueError(
            payload.get("detail", "The backend returned an error.")
        )

    records = payload.get("records", [])

    if not records:
        raise ValueError("The backend returned zero data records.")

    return pd.DataFrame(records), payload


# ------------------------- DATA PREPARATION -------------------------

def prepare_data(data):
    """Standardize column names and safely prepare chart fields."""
    df = data.copy()
    df.columns = [str(col).strip() for col in df.columns]

    rename = {}
    existing = set(df.columns)

    for col in df.columns:
        normalized = col.strip().lower()
        target = ALIASES.get(normalized)

        if target and target not in existing:
            rename[col] = target
            existing.add(target)

    df.rename(columns=rename, inplace=True)

    if "City" not in df.columns:
        df["City"] = "Dataset location"

    df["City"] = df["City"].fillna("Unknown").astype(str)

    if "State" in df.columns:
        df["State"] = df["State"].fillna("Unknown").astype(str)

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    else:
        df["Date"] = pd.NaT

    numeric_columns = ["AQI"] + POLLUTANTS + [
        "Temperature", "Humidity", "Wind Speed"
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        else:
            df[col] = np.nan

    return df.dropna(how="all").copy()


def aqi_category(value):
    """European AQI categories; used only when AQI values exist."""
    if pd.isna(value):
        return "Unavailable"
    if value <= 20:
        return "Good"
    if value <= 40:
        return "Fair"
    if value <= 60:
        return "Moderate"
    if value <= 80:
        return "Poor"
    if value <= 100:
        return "Very Poor"
    return "Extremely Poor"


def category_color(category):
    return {
        "Good": "#56D69A",
        "Fair": "#38D9C5",
        "Moderate": "#F5B942",
        "Poor": "#F59E5B",
        "Very Poor": "#F4778B",
        "Extremely Poor": "#D94F70",
        "Unavailable": "#94A3B8",
    }.get(category, "#6CA8FF")


def style_chart(fig, height=360):
    """Apply consistent styling to all Plotly charts."""
    fig.update_layout(
        template=C["plot"],
        height=height,
        margin=dict(l=25, r=25, t=65, b=35),
        font=dict(family="DM Sans", color=C["text"], size=12),
        paper_bgcolor=C["card"],
        plot_bgcolor=C["card"],
        title_font=dict(family="Manrope", size=16),
        hovermode="closest",
        legend_title_text="",
    )
    fig.update_xaxes(
        gridcolor=C["grid"],
        automargin=True,
        showline=True,
        linecolor=C["border"],
    )
    fig.update_yaxes(
        gridcolor=C["grid"],
        automargin=True,
        showline=True,
        linecolor=C["border"],
    )
    return fig


# ------------------------- SIDEBAR -------------------------

st.sidebar.markdown("# 🌬️ AirSight")
st.sidebar.caption("ENVIRONMENTAL INTELLIGENCE")
st.sidebar.divider()

st.sidebar.radio(
    "Appearance",
    ["Dark", "Light"],
    key="airsight_theme",
    horizontal=True,
)

st.sidebar.markdown("### Data source")

uploaded_file = st.sidebar.file_uploader(
    "Upload a CSV (optional)",
    type=["csv"],
    help="Normally, AirSight loads dataset1.csv automatically from its backend.",
)

if st.sidebar.button("↻ Refresh backend data", use_container_width=True):
    fetch_backend_data.clear()
    st.rerun()

# ------------------------- LOAD DATA -------------------------

backend_url = get_backend_url()
backend_payload = {}
source_mode = ""
source_error = None

if uploaded_file is not None:
    try:
        raw_df = pd.read_csv(uploaded_file)
        source_mode = "Uploaded CSV"
    except Exception as exc:
        st.error(f"Could not read the uploaded CSV: {exc}")
        st.stop()
else:
    if not backend_url:
        st.error(
            "The backend URL has not been configured. "
            "Add AIRSIGHT_BACKEND_URL to Streamlit Cloud → App settings → Secrets."
        )
        st.stop()

    try:
        with st.spinner("Connecting to the AirSight backend..."):
            raw_df, backend_payload = fetch_backend_data(backend_url)
        source_mode = "Fixed CSV backend"
    except Exception as exc:
        source_error = str(exc)
        st.error(
            "AirSight could not load data from the backend. "
            "Check that your Render service is running and its URL is correct."
        )
        st.caption(source_error)
        st.stop()

df = prepare_data(raw_df)

if df.empty:
    st.error("The selected data source contains no usable records.")
    st.stop()

available_cities = sorted(df["City"].dropna().unique().tolist())

if not available_cities:
    st.error("No locations are available in the selected dataset.")
    st.stop()

default_cities = available_cities[:min(6, len(available_cities))]

selected_cities = st.sidebar.multiselect(
    "Filter locations",
    options=available_cities,
    default=default_cities,
)

if not selected_cities:
    st.warning("Select at least one location to view the dashboard.")
    st.stop()

df = df[df["City"].isin(selected_cities)].copy()

if df.empty:
    st.warning("No rows match your selected locations.")
    st.stop()

df["AQI Category"] = df["AQI"].apply(aqi_category)

st.sidebar.success(
    "Backend connected" if source_mode == "Fixed CSV backend"
    else "CSV loaded"
)
st.sidebar.caption(f"Source: {source_mode}")
st.sidebar.caption(f"{len(df):,} rows in current view")

# ------------------------- HEADER -------------------------

st.markdown(
    f"""
    <div class="hero">
        <div class="eyebrow">● ENVIRONMENTAL INTELLIGENCE PLATFORM</div>
        <h1>AirSight</h1>
        <p>Air quality, pollution patterns and environmental insights in one workspace.</p>
        <p><b>Source:</b> {source_mode} &nbsp; · &nbsp;
        <b>Locations:</b> {len(selected_cities)}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if source_mode == "Fixed CSV backend":
    st.success(
        "Connected to the AirSight backend. "
        "The fixed dataset loads automatically without a manual CSV upload."
    )
else:
    st.info("Viewing the CSV you uploaded for this session.")

st.caption(
    "The backend serves your saved dataset. Values are not live sensor readings "
    "unless the underlying source provides live measurements."
)

# ------------------------- KPI CARDS -------------------------

st.caption("DATASET OVERVIEW")
st.header("Air quality at a glance")

valid_aqi = df["AQI"].dropna()
valid_pm25 = df["PM2.5"].dropna()
valid_pm10 = df["PM10"].dropna()

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric(
    "Average AQI",
    f"{valid_aqi.mean():.1f}" if not valid_aqi.empty else "N/A",
)
k2.metric(
    "Average PM2.5",
    f"{valid_pm25.mean():.1f} µg/m³" if not valid_pm25.empty else "N/A",
)
k3.metric(
    "Average PM10",
    f"{valid_pm10.mean():.1f} µg/m³" if not valid_pm10.empty else "N/A",
)
k4.metric("Locations", f"{df['City'].nunique():,}")
k5.metric("Records", f"{len(df):,}")

if not valid_aqi.empty:
    st.caption(
        f"Average AQI category: **{aqi_category(valid_aqi.mean())}**"
    )
else:
    st.info(
        "AQI is not present in the supplied dataset. "
        "AQI-specific charts will remain unavailable until real AQI values are provided."
    )

st.divider()

# ------------------------- CHART 1: AQI TREND -------------------------

left, right = st.columns([1.5, 1])

with left:
    st.subheader("AQI timeline")

    trend = df.dropna(subset=["Date", "AQI"])

    if not trend.empty:
        trend = trend.sort_values("Date")
        fig = px.line(
            trend,
            x="Date",
            y="AQI",
            color="City",
            markers=True,
            color_discrete_sequence=COLORS,
            hover_data=["PM2.5", "PM10"],
            title="AQI over time by location",
            labels={"Date": "Date and time", "AQI": "Air Quality Index"},
        )
        fig.update_traces(line_width=2)
        st.plotly_chart(
            style_chart(fig, 380),
            use_container_width=True,
        )
    else:
        st.info(
            "No date and AQI combination is available. "
            "This chart will appear when the dataset contains both."
        )

# ------------------------- CHART 2: CATEGORY / COVERAGE -------------------------

with right:
    if not valid_aqi.empty:
        st.subheader("AQI category distribution")

        counts = (
            df["AQI Category"]
            .value_counts()
            .rename_axis("Category")
            .reset_index(name="Readings")
        )

        fig = px.pie(
            counts,
            names="Category",
            values="Readings",
            hole=0.60,
            color="Category",
            color_discrete_map={
                category: category_color(category)
                for category in counts["Category"]
            },
            title="Distribution of AQI categories",
        )
        fig.update_traces(
            textinfo="percent",
            hovertemplate="%{label}<br>Records: %{value}<br>%{percent}<extra></extra>",
        )
        st.plotly_chart(
            style_chart(fig, 380),
            use_container_width=True,
        )
    else:
        st.subheader("Pollutant data coverage")

        available = [p for p in POLLUTANTS if df[p].notna().any()]

        if available:
            coverage = pd.DataFrame({
                "Pollutant": available,
                "Records": [int(df[p].notna().sum()) for p in available],
            })
            fig = px.pie(
                coverage,
                names="Pollutant",
                values="Records",
                hole=0.60,
                color="Pollutant",
                color_discrete_sequence=COLORS,
                title="Available pollutant measurements",
            )
            fig.update_traces(textinfo="percent")
            st.plotly_chart(
                style_chart(fig, 380),
                use_container_width=True,
            )
        else:
            st.info("No pollutant measurements are available.")

# ------------------------- CHART 3: CITY COMPARISON -------------------------

c1, c2 = st.columns(2)

with c1:
    st.subheader("Average AQI by location")

    city_aqi = (
        df.groupby("City", as_index=False)["AQI"]
        .mean()
        .dropna()
        .sort_values("AQI")
    )

    if not city_aqi.empty:
        fig = px.bar(
            city_aqi,
            x="AQI",
            y="City",
            orientation="h",
            color="AQI",
            color_continuous_scale=["#38D9C5", "#F5B942", "#F4778B"],
            title="Average AQI comparison",
            labels={"AQI": "Average AQI", "City": "Location"},
        )
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(style_chart(fig), use_container_width=True)
    else:
        st.info("No AQI values are available for location comparison.")

with c2:
    st.subheader("Average pollutant concentrations")

    available_pollutants = [
        p for p in POLLUTANTS if df[p].notna().any()
    ]

    if available_pollutants:
        means = (
            df[available_pollutants]
            .mean()
            .rename_axis("Pollutant")
            .reset_index(name="Average concentration")
        )

        fig = px.bar(
            means,
            x="Pollutant",
            y="Average concentration",
            color="Pollutant",
            color_discrete_sequence=COLORS,
            title="Average recorded concentration",
            labels={"Average concentration": "Average value"},
        )
        st.plotly_chart(style_chart(fig), use_container_width=True)
    else:
        st.info("No pollutant measurements are available.")

# ------------------------- CHART 4: HISTOGRAM -------------------------

c3, c4 = st.columns(2)

with c3:
    st.subheader("Pollution distribution")

    histogram_options = [
        p for p in POLLUTANTS if df[p].notna().any()
    ]

    if df["AQI"].notna().any():
        histogram_options.insert(0, "AQI")

    if histogram_options:
        histogram_column = st.selectbox(
            "Choose a measure for the histogram",
            histogram_options,
            key="histogram_column",
        )

        hist_df = df.dropna(subset=[histogram_column])

        fig = px.histogram(
            hist_df,
            x=histogram_column,
            color="City",
            nbins=30,
            opacity=0.78,
            barmode="overlay",
            color_discrete_sequence=COLORS,
            title=f"Distribution of {histogram_column}",
        )
        st.plotly_chart(style_chart(fig), use_container_width=True)
    else:
        st.info("No numeric pollutant data is available for the histogram.")

# ------------------------- CHART 5: BOX PLOT -------------------------

with c4:
    st.subheader("Spread and outliers")

    box_options = [
        p for p in POLLUTANTS if df[p].notna().any()
    ]

    if df["AQI"].notna().any():
        box_options.insert(0, "AQI")

    if box_options:
        box_column = st.selectbox(
            "Choose a measure for the box plot",
            box_options,
            key="box_column",
        )

        box_df = df.dropna(subset=[box_column])

        fig = px.box(
            box_df,
            x="City",
            y=box_column,
            color="City",
            points="outliers",
            color_discrete_sequence=COLORS,
            title=f"{box_column} distribution by location",
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(style_chart(fig), use_container_width=True)
    else:
        st.info("No numeric data is available for the box plot.")

# ------------------------- CHART 6: SCATTER -------------------------

c5, c6 = st.columns(2)

with c5:
    st.subheader("Variable relationship")

    scatter_options = [
        col for col in
        ["AQI"] + POLLUTANTS + ["Temperature", "Humidity", "Wind Speed"]
        if df[col].notna().any()
    ]

    if len(scatter_options) >= 2:
        sc1, sc2 = st.columns(2)

        x_choice = sc1.selectbox(
            "X-axis",
            scatter_options,
            index=0,
            key="scatter_x",
        )

        y_default = 1 if len(scatter_options) > 1 else 0
        y_choice = sc2.selectbox(
            "Y-axis",
            scatter_options,
            index=y_default,
            key="scatter_y",
        )

        scatter_df = df.dropna(subset=[x_choice, y_choice])

        if x_choice != y_choice and not scatter_df.empty:
            fig = px.scatter(
                scatter_df,
                x=x_choice,
                y=y_choice,
                color="City",
                hover_data=["Date"],
                color_discrete_sequence=COLORS,
                title=f"{y_choice} vs {x_choice}",
            )
            st.plotly_chart(style_chart(fig), use_container_width=True)
        else:
            st.info("Choose two different variables with available data.")
    else:
        st.info("At least two numeric variables are needed for this chart.")

# ------------------------- CHART 7: CORRELATION HEATMAP -------------------------

with c6:
    st.subheader("Correlation heatmap")

    numeric_columns = [
        col for col in
        ["AQI"] + POLLUTANTS + ["Temperature", "Humidity", "Wind Speed"]
        if df[col].notna().any()
    ]

    numeric_df = df[numeric_columns].dropna(axis=1, how="all")
    numeric_df = numeric_df.loc[
        :, numeric_df.nunique(dropna=True) > 1
    ]

    if numeric_df.shape[1] >= 2:
        correlation = numeric_df.corr()

        fig = px.imshow(
            correlation,
            text_auto=".2f",
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
            aspect="auto",
            title="Correlation between available variables",
        )
        st.plotly_chart(style_chart(fig), use_container_width=True)
    else:
        st.info(
            "The heatmap needs at least two numeric columns "
            "with varying values."
        )

# ------------------------- DATA EXPLORER -------------------------

st.divider()
st.header("Explore your dataset")

with st.expander("📍 Location summary", expanded=False):
    summary_columns = [
        col for col in
        ["AQI"] + POLLUTANTS + ["Temperature", "Humidity", "Wind Speed"]
        if df[col].notna().any()
    ]

    if summary_columns:
        summary = (
            df.groupby("City", as_index=False)[summary_columns]
            .mean(numeric_only=True)
            .round(2)
        )

        if "AQI" in summary.columns:
            summary["AQI Category"] = summary["AQI"].apply(aqi_category)

        st.dataframe(
            summary,
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "Download location summary",
            summary.to_csv(index=False).encode("utf-8"),
            "airsight_location_summary.csv",
            "text/csv",
        )
    else:
        st.info("No numeric fields are available for a location summary.")

with st.expander("🗂️ View and download records", expanded=False):
    st.caption(f"{len(df):,} rows · {len(df.columns)} columns")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.download_button(
        "Download current dataset",
        df.to_csv(index=False).encode("utf-8"),
        "airsight_data.csv",
        "text/csv",
    )

with st.expander("🛡️ Data quality report", expanded=False):
    quality = pd.DataFrame({
        "Check": [
            "Rows",
            "Columns",
            "Duplicate rows",
            "Rows with missing values",
            "Missing cells",
        ],
        "Result": [
            len(df),
            len(df.columns),
            int(df.duplicated().sum()),
            int(df.isna().any(axis=1).sum()),
            int(df.isna().sum().sum()),
        ],
    })

    st.dataframe(quality, use_container_width=True, hide_index=True)

    missing = (
        df.isna().mean().mul(100).round(1)
        .rename("Missing %")
        .reset_index()
        .rename(columns={"index": "Column"})
    )

    st.dataframe(missing, use_container_width=True, hide_index=True)

# ------------------------- FOOTER -------------------------

st.divider()
st.caption(
    f"AirSight · Source: {source_mode}. "
    "Charts use available dataset measurements. Missing AQI, weather, "
    "or date values are not fabricated. This educational dashboard "
    "is not an official regulatory alert system."
)
