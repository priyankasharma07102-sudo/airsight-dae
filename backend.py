
from pathlib import Path
import json

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AirSight Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

DATASET_PATH = Path(__file__).resolve().parent / "dataset1.csv"


def load_data():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            "dataset1.csv is missing from the GitHub repository."
        )

    df = pd.read_csv(DATASET_PATH)
    df.columns = [str(c).strip() for c in df.columns]

    required = [
        "city", "state", "pollutant_id", "pollutant_avg"
    ]
    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError(
            "Missing CSV columns: " + ", ".join(missing)
        )

    df = df.dropna(how="all").copy()

    for col in ["city", "state", "pollutant_id"]:
        df[col] = df[col].astype("string").str.strip()

    df["pollutant_id"] = df["pollutant_id"].str.upper()
    df["pollutant_avg"] = pd.to_numeric(
        df["pollutant_avg"], errors="coerce"
    )

    df = df.dropna(
        subset=["city", "state", "pollutant_id", "pollutant_avg"]
    )

    df = df[
        df["city"].ne("")
        & df["state"].ne("")
        & df["pollutant_id"].ne("")
    ]

    if df.empty:
        raise ValueError("No usable pollutant records were found.")

    # Convert pollutant names to the dashboard's naming style.
    pollutant_names = {
        "PM25": "PM2.5",
        "PM2_5": "PM2.5",
        "NO2": "NO₂",
        "SO2": "SO₂",
        "O3": "O₃",
        "OZONE": "O₃",
    }
    df["pollutant_id"] = df["pollutant_id"].replace(
        pollutant_names
    )

    # Find a date column if your CSV contains one.
    date_candidates = {
        "date", "datetime", "timestamp",
        "last_update", "last_updated", "measurement_date"
    }
    date_col = next(
        (c for c in df.columns if c.lower() in date_candidates),
        None
    )

    if date_col:
        df["Date"] = pd.to_datetime(
            df[date_col], errors="coerce"
        ).dt.strftime("%Y-%m-%d")

    # One row per city/state, and per date if available.
    index_cols = ["city", "state"]
    if date_col:
        index_cols = ["Date", "city", "state"]

    wide = df.pivot_table(
        index=index_cols,
        columns="pollutant_id",
        values="pollutant_avg",
        aggfunc="mean",
    ).reset_index()

    wide.columns.name = None
    wide = wide.rename(
        columns={"city": "City", "state": "State"}
    )

    # Ensure missing values become JSON null.
    records = json.loads(
        wide.to_json(orient="records", date_format="iso")
    )

    return records, sorted(df["city"].unique().tolist())


@app.get("/")
def home():
    return {
        "service": "AirSight Backend",
        "status": "running",
        "data_endpoint": "/api/data",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/api/data")
def get_data():
    try:
        records, cities = load_data()
        return {
            "status": "success",
            "source": "dataset1.csv",
            "record_count": len(records),
            "cities": cities,
            "records": records,
        }
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Data processing failed: {exc}",
        )
