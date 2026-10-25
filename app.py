
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests
from datetime import datetime

st.set_page_config(
    page_title="AirSight | Environmental Intelligence",
    page_icon="🌬️",
    layout="wide",
)

CITIES = {
    "Delhi": (28.6139, 77.2090),
    "Mumbai": (19.0760, 72.8777),
    "Hyderabad": (17.3850, 78.4867),
    "Vijayawada": (16.5062, 80.6480),
    "Bengaluru": (12.9716, 77.5946),
    "Chennai": (13.0827, 80.2707),
    "Kolkata": (22.5726, 88.3639),
    "Jaipur": (26.9124, 75.7873),
    "Pune": (18.5204, 73.8567),
    "Ahmedabad": (23.0225, 72.5714),
    "Lucknow": (26.8467, 80.9462),
    "Bhopal": (23.2599, 77.4126),
}

COLORS = [
    "#38D9C5", "#6CA8FF", "#A78BFA", "#F5B942",
    "#F4778B", "#56D69A", "#E99AD5", "#F59E5B"
]

if "airsight_theme" not in st.session_state:
    st.session_state.airsight_theme = "Dark"

theme = st.session_state.airsight_theme

if theme == "Dark":
    C = {
        "bg": "#08111F", "card": "#111D2D",
        "text": "#F3F7FF", "muted": "#A5B4C8",
        "border": "#293A50", "grid": "#293A50",
        "hero": "#102A43", "plot": "plotly_dark",
    }
else:
    C = {
        "bg": "#F3F6FB", "card": "#FFFFFF",
        "text": "#152238", "muted": "#5F6F85",
        "border": "#DCE4EF", "grid": "#E1E8F0",
        "hero": "#E1F5F3", "plot": "plotly_white",
    }

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
.stApp {{background:{C['bg']}; color:{C['text']}; font-family:'DM Sans',sans-serif;}}
.block-container {{max-width:1600px;padding-top:1.4rem;padding-bottom:3rem;}}
h1,h2,h3 {{font-family:'Manrope',sans-serif!important;color:{C['text']}!important;}}
p,label {{color:{C['muted']};}}
[data-testid="stSidebar"] {{background:{C['card']};border-right:1px solid {C['border']};}}
[data-testid="stSidebar"] * {{color:{C['text']};}}
.hero {{padding:30px;border-radius:22px;margin-bottom:22px;
background:linear-gradient(115deg,{C['hero']},#124B55);
border:1px solid {C['border']};}}
.hero h1 {{color:{'#FFFFFF' if theme == 'Dark' else '#152238'}!important;font-size:2.7rem;}}
.hero p {{color:{'#D5E6F5' if theme == 'Dark' else '#40536B'};}}
.eyebrow {{font-size:.75rem;letter-spacing:2px;font-weight:800;color:#38D9C5;}}
[data-testid="stMetric"] {{background:{C['card']};border:1px solid {C['border']};
border-radius:16px;padding:17px;transition:transform .2s;}}
[data-testid="stMetric"]:hover {{transform:translateY(-3px);}}
[data-testid="stMetricLabel"] {{color:{C['muted']}!important;}}
[data-testid="stMetricValue"] {{color:{C['text']}!important;font-family:'Manrope',sans-serif;font-weight:800;}}
[data-testid="stPlotlyChart"] {{border:1px solid {C['border']};border-radius:16px;padding:5px;}}
.stButton button,.stDownloadButton button {{border-radius:10px;font-weight:700;}}
hr {{border-color:{C['border']};}}
footer {{visibility:hidden;}}
</style>
""", unsafe_allow_html=True)


def aqi_category(value):
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


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_city(city, latitude, longitude):
    """Retrieve recent air-quality and weather data from Open-Meteo."""
    base = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": (
            "european_aqi,us_aqi,pm2_5,pm10,"
            "nitrogen_dioxide,sulphur_dioxide,carbon_monoxide,ozone"
        ),
        "past_days": 7,
        "forecast_days": 1,
        "timezone": "Asia/Kolkata",
    }

    response = requests.get(base, params=params, timeout=15)
    response.raise_for_status()
    payload = response.json()

    if not payload.get("hourly", {}).get("time"):
        raise ValueError("No hourly measurements returned.")

    data = pd.DataFrame(payload["hourly"])
    data["Date"] = pd.to_datetime(data.pop("time"), errors="coerce")
    data["City"] = city

    if "european_aqi" in data:
        data["AQI"] = data["european_aqi"]
    else:
        data["AQI"] = data.get("us_aqi", np.nan)

    data.rename(columns={
        "pm2_5": "PM2.5",
        "pm10": "PM10",
        "nitrogen_dioxide": "NO₂",
        "sulphur_dioxide": "SO₂",
        "carbon_monoxide": "CO",
        "ozone": "O₃",
    }, inplace=True)

    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        "past_days": 7,
        "forecast_days": 1,
        "timezone": "Asia/Kolkata",
    }

    try:
        weather_response = requests.get(
            weather_url, params=weather_params, timeout=15
        )
        weather_response.raise_for_status()
        hourly = weather_response.json().get("hourly", {})
        if hourly.get("time"):
            weather = pd.DataFrame(hourly)
            weather["Date"] = pd.to_datetime(
                weather.pop("time"), errors="coerce"
            )
            data = data.merge(weather, on="Date", how="left")
    except Exception:
        pass

    data.rename(columns={
        "temperature_2m": "Temperature",
        "relative_humidity_2m": "Humidity",
        "wind_speed_10m": "Wind Speed",
    }, inplace=True)

    data["Source"] = "Open-Meteo API"
    return data


@st.cache_data(ttl=3600, show_spinner=False)
def demo_data():
    """Clearly labelled synthetic fallback; never presented as live readings."""
    rng = np.random.default_rng(42)
    dates = pd.date_range(
        end=pd.Timestamp.now().floor("h"), periods=24 * 8, freq="h"
    )
    records = []

    for city in CITIES:
        base = rng.uniform(25, 105)
        for i, date in enumerate(dates):
            pm25 = max(3, rng.normal(base * .55, 12))
            records.append({
                "Date": date,
                "City": city,
                "AQI": max(1, min(250, base + 12 * np.sin(i / 23)
                                 + rng.normal(0, 12))),
                "PM2.5": pm25,
                "PM10": max(5, rng.normal(pm25 * 1.8, 18)),
                "NO₂": max(1, rng.normal(22, 8)),
                "SO₂": max(1, rng.normal(9, 3)),
                "CO": max(.1, rng.normal(.8, .2)),
                "O₃": max(2, rng.normal(32, 10)),
                "Temperature": rng.normal(28, 4),
                "Humidity": np.clip(rng.normal(62, 13), 15, 98),
                "Wind Speed": max(0, rng.normal(10, 4)),
                "Source": "Synthetic demo data",
            })

    return pd.DataFrame(records)


def style_chart(fig, height=350):
    fig.update_layout(
        template=C["plot"],
        height=height,
        margin=dict(l=20, r=20, t=65, b=25),
        font=dict(family="DM Sans", color=C["text"], size=12),
        paper_bgcolor=C["card"],
        plot_bgcolor=C["card"],
        title_font=dict(family="Manrope", size=16),
        hovermode="closest",
    )
    fig.update_xaxes(gridcolor=C["grid"], automargin=True)
    fig.update_yaxes(gridcolor=C["grid"], automargin=True)
    return fig


# -------------------- Sidebar --------------------

st.sidebar.markdown("# 🌬️ AirSight")
st.sidebar.caption("ENVIRONMENTAL INTELLIGENCE")
st.sidebar.divider()

st.sidebar.radio(
    "Appearance",
    ["Dark", "Light"],
    key="airsight_theme",
    horizontal=True,
)


# -------------------- Load fixed dataset from backend --------------------

try:
    BACKEND_URL = st.secrets.get("AIRSIGHT_BACKEND_URL", "").strip().rstrip("/")
except Exception:
    BACKEND_URL = ""

if not BACKEND_URL:
    st.error(
        "Backend URL is missing. Configure AIRSIGHT_BACKEND_URL "
        "in Streamlit Cloud Secrets."
    )
    st.stop()


@st.cache_data(ttl=3600, show_spinner=False)
def get_backend_data(base_url):
    response = requests.get(
        f"{base_url}/api/data",
        timeout=60,
    )
    response.raise_for_status()

    payload = response.json()

    if payload.get("status") != "success":
        raise ValueError(
            payload.get("detail", "Backend returned an error.")
        )

    records = payload.get("records", [])

    if not records:
        raise ValueError("The backend returned no data records.")

    return pd.DataFrame(records), payload


if st.sidebar.button(
    "↻ Reload fixed dataset",
    use_container_width=True,
):
    get_backend_data.clear()
    st.rerun()

try:
    with st.spinner("Loading AirSight dataset from backend..."):
        df, backend_payload = get_backend_data(BACKEND_URL)

except Exception as exc:
    st.error(
        "Unable to load the dataset from the AirSight backend. "
        "Check that the Render service is deployed and working."
    )
    st.caption(str(exc))
    st.stop()

# Let the user filter cities that actually exist in the dataset.
df.columns = [str(c).strip() for c in df.columns]

if "City" not in df.columns:
    st.error("The backend data does not contain a City column.")
    st.stop()

available_cities = sorted(
    df["City"].dropna().astype(str).unique().tolist()
)

if not available_cities:
    st.error("No cities were found in the dataset.")
    st.stop()

cities = st.sidebar.multiselect(
    "Select cities",
    available_cities,
    default=available_cities[:min(6, len(available_cities))],
)

if not cities:
    st.warning("Select at least one city to view the dashboard.")
    st.stop()

df = df[df["City"].isin(cities)].copy()

mode = "FIXED CSV BACKEND"
updated = "Loaded from dataset1.csv"

st.sidebar.success("Backend connected")
st.sidebar.caption(
    f"{backend_payload.get('record_count', len(df)):,} records available"
)

# Continue with the existing:
# # Normalise common CSV column names.
# section below.


# Normalise common CSV column names.
aliases = {
    "date": "Date", "datetime": "Date", "timestamp": "Date",
    "time": "Date", "city": "City", "location": "City",
    "station": "City", "pm2_5": "PM2.5", "pm25": "PM2.5",
    "pm10": "PM10", "no2": "NO₂", "nitrogen_dioxide": "NO₂",
    "so2": "SO₂", "sulphur_dioxide": "SO₂",
    "co": "CO", "carbon_monoxide": "CO",
    "o3": "O₃", "ozone": "O₃",
    "temperature": "Temperature", "temp": "Temperature",
    "humidity": "Humidity", "relative_humidity_2m": "Humidity",
    "wind_speed": "Wind Speed", "us_aqi": "AQI",
    "european_aqi": "AQI", "air_quality_index": "AQI",
}

rename = {}
for col in df.columns:
    normal = str(col).strip().lower()
    if normal in aliases and aliases[normal] not in df.columns:
        rename[col] = aliases[normal]
df.rename(columns=rename, inplace=True)

if "Date" in df:
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
else:
    df["Date"] = pd.NaT

if "City" not in df:
    df["City"] = "Uploaded dataset"

for col in [
    "AQI", "PM2.5", "PM10", "NO₂", "SO₂", "CO",
    "O₃", "Temperature", "Humidity", "Wind Speed"
]:
    if col in df:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    else:
        df[col] = np.nan

df["AQI Category"] = df["AQI"].apply(aqi_category)

if df.empty:
    st.error("No data is available. Please check the source or CSV.")
    st.stop()

# -------------------- Header --------------------

st.markdown(f"""
<div class="hero">
  <div class="eyebrow">● ENVIRONMENTAL INTELLIGENCE PLATFORM</div>
  <h1>AirSight</h1>
  <p>Air quality, pollution patterns and weather insights in one workspace.</p>
  <p><b>{mode}</b> &nbsp; · &nbsp; Updated: {updated}</p>
</div>
""", unsafe_allow_html=True)

if mode == "LIVE API":
    st.info(
        "Live source connected. Open-Meteo provides modelled air-quality "
        "estimates for these coordinates, not necessarily official station "
        "measurements. Check official monitoring sources for regulatory decisions."
    )
elif mode == "DEMO FALLBACK":
    st.warning(
        "The live API could not be reached. You are viewing synthetic "
        "demonstration data, not current measured AQI."
    )
else:
    st.info("CSV mode is active. Confirm the dataset's units and column meanings.")

if errors:
    with st.expander("Location requests that failed"):
        st.write("\n".join(errors))

# Date filter
if df["Date"].notna().any():
    minimum = df["Date"].dropna().min().date()
    maximum = df["Date"].dropna().max().date()

    selected_dates = st.sidebar.date_input(
        "Date range",
        value=(minimum, maximum),
        min_value=minimum,
        max_value=maximum,
    )

    if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
        start = pd.Timestamp(selected_dates[0])
        end = pd.Timestamp(selected_dates[1]) + pd.Timedelta(days=1)
        df = df[(df["Date"] >= start) & (df["Date"] < end)]

if df.empty:
    st.warning("No rows match the selected date range.")
    st.stop()

# -------------------- KPI cards --------------------

st.caption("LIVE MONITORING")
st.header("Air quality at a glance")

latest = (
    df.sort_values("Date").groupby("City", as_index=False).tail(1)
    if df["Date"].notna().any() else df.groupby("City", as_index=False).tail(1)
)

latest_aqi = latest["AQI"].dropna()
aqi_value = latest_aqi.mean() if not latest_aqi.empty else np.nan
pm25_avg = df["PM2.5"].mean()
pm10_avg = df["PM10"].mean()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Latest average AQI", f"{aqi_value:.1f}" if pd.notna(aqi_value) else "N/A")
k2.metric("Average PM2.5", f"{pm25_avg:.1f} µg/m³" if pd.notna(pm25_avg) else "N/A")
k3.metric("Average PM10", f"{pm10_avg:.1f} µg/m³" if pd.notna(pm10_avg) else "N/A")
k4.metric("Locations", f"{df['City'].nunique()}")
k5.metric("Records", f"{len(df):,}")

if pd.notna(aqi_value):
    st.caption(f"Latest average AQI category: **{aqi_category(aqi_value)}**")

st.divider()

# -------------------- Interactive charts --------------------

left, right = st.columns([1.5, 1])

with left:
    trend = df.dropna(subset=["Date", "AQI"])
    if not trend.empty:
        fig = px.line(
            trend, x="Date", y="AQI", color="City",
            color_discrete_sequence=COLORS,
            hover_data=["PM2.5", "PM10", "Temperature"],
            title="AQI timeline by location",
        )
        fig.update_traces(line_width=2)
        st.plotly_chart(style_chart(fig, 390), use_container_width=True)
    else:
        st.info("The timeline needs valid date and AQI columns.")

with right:
    counts = df["AQI Category"].value_counts().rename_axis(
        "Category"
    ).reset_index(name="Readings")

    if not counts.empty:
        fig = px.pie(
            counts, names="Category", values="Readings",
            hole=.62, title="AQI category distribution",
            color="Category",
            color_discrete_map={
                name: category_color(name) for name in counts["Category"]
            },
        )
        fig.update_traces(textinfo="percent")
        st.plotly_chart(style_chart(fig, 390), use_container_width=True)

c1, c2 = st.columns(2)

with c1:
    city_avg = df.groupby("City", as_index=False)["AQI"].mean().dropna()
    if not city_avg.empty:
        city_avg = city_avg.sort_values("AQI")
        fig = px.bar(
            city_avg, x="AQI", y="City", orientation="h",
            color="AQI", color_continuous_scale=[
                "#38D9C5", "#F5B942", "#F4778B"
            ],
            title="Average AQI by location",
        )
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(style_chart(fig), use_container_width=True)
    else:
        st.info("No AQI values available for location comparison.")

with c2:
    pollutants = ["PM2.5", "PM10", "NO₂", "SO₂", "CO", "O₃"]
    available = [
        col for col in pollutants
        if df[col].notna().any()
    ]

    if available:
        means = df[available].mean().rename_axis(
            "Pollutant"
        ).reset_index(name="Average concentration")
        fig = px.bar(
            means, x="Pollutant", y="Average concentration",
            color="Pollutant", color_discrete_sequence=COLORS,
            title="Average pollutant concentrations",
        )
        st.plotly_chart(style_chart(fig), use_container_width=True)
    else:
        st.info("No pollutant measurements are available.")

c3, c4 = st.columns(2)

with c3:
    hist_column = "PM2.5" if df["PM2.5"].notna().any() else "AQI"
    if df[hist_column].notna().any():
        fig = px.histogram(
            df.dropna(subset=[hist_column]),
            x=hist_column, color="City", nbins=30,
            opacity=.78, barmode="overlay",
            color_discrete_sequence=COLORS,
            title=f"Distribution of {hist_column}",
        )
        st.plotly_chart(style_chart(fig), use_container_width=True)
    else:
        st.info("No numeric data available for the histogram.")

with c4:
    box_column = "PM2.5" if df["PM2.5"].notna().any() else "AQI"
    box_data = df.dropna(subset=[box_column])
    if not box_data.empty:
        fig = px.box(
            box_data, x="City", y=box_column, color="City",
            points="outliers", color_discrete_sequence=COLORS,
            title=f"{box_column} spread by location",
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(style_chart(fig), use_container_width=True)
    else:
        st.info("No numeric data available for the box plot.")

c5, c6 = st.columns(2)

with c5:
    scatter_data = df.dropna(subset=["Temperature", "PM2.5"])
    if len(scatter_data) > 2:
        fig = px.scatter(
            scatter_data, x="Temperature", y="PM2.5",
            color="City", size="AQI", size_max=18,
            color_discrete_sequence=COLORS,
            hover_data=["Date", "Humidity"],
            title="Temperature vs PM2.5",
            labels={
                "Temperature": "Temperature (°C)",
                "PM2.5": "PM2.5 (µg/m³)",
            },
        )
        st.plotly_chart(style_chart(fig), use_container_width=True)
    else:
        st.info("Scatter plot needs Temperature and PM2.5 data.")

with c6:
    numeric = df.select_dtypes(include=np.number)
    numeric = numeric.loc[:, numeric.nunique(dropna=True) > 1]
    if numeric.shape[1] >= 2:
        correlation = numeric.corr()
        fig = px.imshow(
            correlation, text_auto=".2f",
            color_continuous_scale="RdBu_r",
            zmin=-1, zmax=1, aspect="auto",
            title="Pollutant and weather correlation",
        )
        st.plotly_chart(style_chart(fig), use_container_width=True)
    else:
        st.info("Heatmap needs at least two varying numeric columns.")

# -------------------- Data tools --------------------

st.divider()

with st.expander("📍 Location comparison table"):
    columns = [
        col for col in [
            "AQI", "PM2.5", "PM10", "NO₂", "SO₂",
            "CO", "O₃", "Temperature", "Humidity"
        ] if col in df.columns and df[col].notna().any()
    ]
    if columns:
        summary = df.groupby("City", as_index=False)[columns].mean().round(2)
        summary["AQI Category"] = summary["AQI"].apply(aqi_category) if "AQI" in summary else "N/A"
        st.dataframe(summary, use_container_width=True, hide_index=True)
        st.download_button(
            "Download location summary",
            summary.to_csv(index=False).encode("utf-8"),
            "airsight_location_summary.csv",
            "text/csv",
        )

with st.expander("🗂️ Explore and download data"):
    st.caption(f"{len(df):,} rows · {len(df.columns)} columns")
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button(
        "Download current dataset",
        df.to_csv(index=False).encode("utf-8"),
        "airsight_data.csv",
        "text/csv",
    )

with st.expander("🛡️ Data quality report"):
    quality = pd.DataFrame({
        "Check": [
            "Rows", "Columns", "Duplicate rows",
            "Rows with missing values", "Missing cells"
        ],
        "Result": [
            len(df), len(df.columns), int(df.duplicated().sum()),
            int(df.isna().any(axis=1).sum()), int(df.isna().sum().sum())
        ],
    })
    st.dataframe(quality, use_container_width=True, hide_index=True)

    missing = (
        df.isna().mean().mul(100).round(1)
        .rename("Missing %").reset_index()
        .rename(columns={"index": "Column"})
    )
    st.dataframe(missing, use_container_width=True, hide_index=True)

st.divider()
st.caption(
    f"AirSight · Source mode: {mode}. Live data is retrieved from "
    "Open-Meteo when available. AQI categories use the European AQI "
    "scale for the live API. This educational dashboard is not an "
    "official regulatory alert system."
)
