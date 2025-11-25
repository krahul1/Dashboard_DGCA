
# app/utils.py
import os
import pandas as pd

# >>> EDIT THESE PATHS if you store your CSVs elsewhere <<<
# Path to incidents CSV (change to your actual file if needed)
DATA_CSV = "/Users/karunatirkey/Downloads/sample_data.csv"
UPLOADED_IMAGE = "/mnt/data/87226007-e0d9-4f49-833d-9d563f059920.png"
# Airport master path (uploaded file in workspace)
AIRPORT_MASTER_CSV = "/Users/karunatirkey/Library/CloudStorage/OneDrive-Personal/DGCA/airports_india.csv"

# Column mapping
INCIDENT_AIRPORT_COL = "Airport / Place of occurrence"
MASTER_CODE_COL = "Code"
MASTER_LAT_COL = "Latitude"
MASTER_LON_COL = "Longitude"

def load_airport_master(path: str = None) -> pd.DataFrame:
    p = path or AIRPORT_MASTER_CSV
    if not os.path.exists(p):
        # try relative
        rel = os.path.join(os.getcwd(), p)
        if os.path.exists(rel):
            p = rel
    try:
        df = pd.read_csv(p)
        return df
    except Exception as e:
        print(f"[load_airport_master] failed to read {p}: {e}")
        return pd.DataFrame()

def load_data(path: str = None, parse_dates: list = None) -> pd.DataFrame:
    """
    Load incidents and merge airport master coordinates.
    Returns incidents DataFrame augmented with Latitude and Longitude columns (if available).
    """
    p = path or DATA_CSV
    parse_dates = parse_dates or ["Date"]
    try:
        df = pd.read_csv(p, parse_dates=parse_dates, low_memory=False)
    except Exception as e:
        print(f"[load_data] failed to read {p}: {e}")
        return pd.DataFrame()

    # ensure column names are present (rename common alternates)
    if INCIDENT_AIRPORT_COL not in df.columns:
        for alt in ["Airport", "Airport Name", "Airport/Place of occurrence", "Airport / Place of occurrence"]:
            if alt in df.columns:
                df.rename(columns={alt: INCIDENT_AIRPORT_COL}, inplace=True)
                break

    am = load_airport_master()
    if am is None or am.empty:
        print("[load_data] airport master missing or empty; returning incidents without coords")
        return df

    # normalize master column names if needed
    if MASTER_CODE_COL not in am.columns:
        alt_code = next((c for c in am.columns if c.lower() in ("code", "iata", "icao")), None)
        if alt_code:
            am.rename(columns={alt_code: MASTER_CODE_COL}, inplace=True)

    if MASTER_LAT_COL not in am.columns or MASTER_LON_COL not in am.columns:
        lat_candidate = next((c for c in am.columns if "lat" in c.lower()), None)
        lon_candidate = next((c for c in am.columns if any(x in c.lower() for x in ("lon","lng","long"))), None)
        if lat_candidate:
            am.rename(columns={lat_candidate: MASTER_LAT_COL}, inplace=True)
        if lon_candidate:
            am.rename(columns={lon_candidate: MASTER_LON_COL}, inplace=True)

    # left join incidents -> airport master using INCIDENT_AIRPORT_COL -> MASTER_CODE_COL
    if INCIDENT_AIRPORT_COL in df.columns and MASTER_CODE_COL in am.columns:
        merged = df.merge(
            am[[MASTER_CODE_COL, MASTER_LAT_COL, MASTER_LON_COL]].drop_duplicates(),
            left_on=INCIDENT_AIRPORT_COL,
            right_on=MASTER_CODE_COL,
            how="left",
            validate="m:1"
        )
        # coerce to numeric
        merged[MASTER_LAT_COL] = pd.to_numeric(merged[MASTER_LAT_COL], errors="coerce")
        merged[MASTER_LON_COL] = pd.to_numeric(merged[MASTER_LON_COL], errors="coerce")
        # expose as Latitude/Longitude in incidents
        merged["Latitude"] = merged.get(MASTER_LAT_COL)
        merged["Longitude"] = merged.get(MASTER_LON_COL)
        return merged
    else:
        print("[load_data] could not find join columns; returning raw incidents")
        return df
