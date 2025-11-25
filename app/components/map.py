# app/components/map.py
"""
Map builder (merged pipeline inside map module).

Behavior:
- If caller passes a dataframe `df`, the module will try to use its Latitude/Longitude.
- If df is None, the module will read incidents from DATA_CSV (from utils.py) and
  airport master from AIRPORT_MASTER_CSV and perform merging here.
- Merge strategy:
    1) exact join: incidents["Airport / Place of occurrence"] == master["Code"]
    2) if very few matches, fuzzy-match incident text to master["Airport Name"] and map coordinates
- Finally builds a plotly scatter_mapbox using mapbox_style='open-street-map' and returns dcc.Graph.
"""

from typing import Optional
import pandas as pd
from dash import dcc, html
import plotly.express as px
import difflib
import os

# Try import constants from utils; if not present, fallback to known workspace path
try:
    from ..utils import DATA_CSV, AIRPORT_MASTER_CSV, INCIDENT_AIRPORT_COL, MASTER_CODE_COL, MASTER_NAME_COL, MASTER_LAT_COL, MASTER_LON_COL
except Exception:
    # fallback defaults
    DATA_CSV = "/Users/karunatirkey/Downloads/sample_data.csv"
    AIRPORT_MASTER_CSV = "/mnt/data/c09c22cc-0788-45c5-b104-40c36b5a48d1.csv"
    INCIDENT_AIRPORT_COL = "Airport / Place of occurrence"
    MASTER_CODE_COL = "Code"
    MASTER_NAME_COL = "Airport Name"
    MASTER_LAT_COL = "Latitude"
    MASTER_LON_COL = "Longitude"


def _safe_read_csv(path, **kwargs):
    """Read CSV safely; return empty df on failure and print diagnostics."""
    try:
        df = pd.read_csv(path, **kwargs)
        return df
    except Exception as e:
        print(f"[map._safe_read_csv] failed to read {path}: {e}")
        return pd.DataFrame()


def _normalize_column_names(df: pd.DataFrame):
    """Strip leading/trailing whitespace from string columns used as keys."""
    for c in df.columns:
        if df[c].dtype == object:
            try:
                df[c] = df[c].astype(str).str.strip()
            except Exception:
                pass
    return df


def _attempt_exact_join(incidents: pd.DataFrame, master: pd.DataFrame):
    """
    Try to join incidents -> master by INCIDENT_AIRPORT_COL -> MASTER_CODE_COL.
    Returns merged df and number matched.
    """
    if INCIDENT_AIRPORT_COL not in incidents.columns or MASTER_CODE_COL not in master.columns:
        return None, 0

    incidents['_inc_key'] = incidents[INCIDENT_AIRPORT_COL].astype(str).str.strip()
    master['_master_code'] = master[MASTER_CODE_COL].astype(str).str.strip()

    merged = incidents.merge(
        master[['_master_code', MASTER_LAT_COL, MASTER_LON_COL, MASTER_NAME_COL]].drop_duplicates(),
        left_on='_inc_key',
        right_on='_master_code',
        how='left',
        validate='m:1'
    )

    # coerce numeric
    merged[MASTER_LAT_COL] = pd.to_numeric(merged.get(MASTER_LAT_COL), errors='coerce')
    merged[MASTER_LON_COL] = pd.to_numeric(merged.get(MASTER_LON_COL), errors='coerce')

    matched = int(merged.dropna(subset=[MASTER_LAT_COL, MASTER_LON_COL]).shape[0])
    return merged, matched


def _fuzzy_map(incidents: pd.DataFrame, master: pd.DataFrame, cutoff_name: float = 0.38, cutoff_code: float = 0.6):
    """
    Fuzzy-match incidents[INCIDENT_AIRPORT_COL] to master[MASTER_NAME_COL] or master code,
    return incidents with mapped latitude/longitude columns `_mapped_lat`/_mapped_lon`.
    """
    master = master.copy()
    # prepare lists
    master['_m_name_lc'] = master.get(MASTER_NAME_COL, "").fillna("").astype(str).str.strip()
    master['_m_code_lc'] = master.get(MASTER_CODE_COL, "").fillna("").astype(str).str.strip()

    name_list = master['_m_name_lc'].tolist()
    code_list = master['_m_code_lc'].tolist()

    mapped_lats = []
    mapped_lons = []
    mapped_matches = []

    inc_keys = incidents.get(INCIDENT_AIRPORT_COL, pd.Series([""] * len(incidents))).astype(str).str.strip().tolist()

    for val in inc_keys:
        if not val:
            mapped_matches.append(None); mapped_lats.append(None); mapped_lons.append(None); continue
        # try matching to master names first
        matches = difflib.get_close_matches(val, name_list, n=1, cutoff=cutoff_name)
        if matches:
            m = matches[0]
            idx = name_list.index(m)
            lat = master.iloc[idx].get(MASTER_LAT_COL)
            lon = master.iloc[idx].get(MASTER_LON_COL)
            mapped_matches.append(master.iloc[idx].get(MASTER_CODE_COL))
            mapped_lats.append(lat)
            mapped_lons.append(lon)
            continue
        # else try matching to master codes (maybe incidents contain code-like text)
        code_matches = difflib.get_close_matches(val, code_list, n=1, cutoff=cutoff_code)
        if code_matches:
            cm = code_matches[0]; idx = code_list.index(cm)
            mapped_matches.append(master.iloc[idx].get(MASTER_CODE_COL))
            mapped_lats.append(master.iloc[idx].get(MASTER_LAT_COL))
            mapped_lons.append(master.iloc[idx].get(MASTER_LON_COL))
            continue
        # nothing matched
        mapped_matches.append(None); mapped_lats.append(None); mapped_lons.append(None)

    incidents['_mapped_code'] = mapped_matches
    incidents['_mapped_lat'] = mapped_lats
    incidents['_mapped_lon'] = mapped_lons
    return incidents


def build_map_component(df: Optional[pd.DataFrame] = None):
    """
    Main entrypoint:
    - If df provided and contains Latitude/Longitude -> plot from it.
    - Else read DATA_CSV and AIRPORT_MASTER_CSV and perform merging here, then plot.
    Returns a dcc.Graph (Plotly scatter_mapbox) or an informative html.Div on failure.
    """
    # Defensive checks
    if df is None:
        # read incidents
        if not os.path.exists(DATA_CSV):
            return html.Div(f"Incidents file not found: {DATA_CSV}", style={'color':'#ff6b6b','paddingTop':'120px','textAlign':'center','height':'360px'})
        df = _safe_read_csv(DATA_CSV, parse_dates=['Date'], low_memory=False)

    if df is None or df.empty:
        return html.Div("No incident data available.", style={'color':'#94a3b8','paddingTop':'120px','textAlign':'center','height':'360px'})

    # If Latitude/Longitude already present, use them directly
    if 'Latitude' in df.columns and 'Longitude' in df.columns:
        coords = df.dropna(subset=['Latitude','Longitude']).copy()
        # try numeric coercion
        coords['Latitude'] = pd.to_numeric(coords['Latitude'], errors='coerce')
        coords['Longitude'] = pd.to_numeric(coords['Longitude'], errors='coerce')
        coords = coords.dropna(subset=['Latitude','Longitude'])
        if coords.empty:
            return html.Div("Coordinates present but invalid format in provided data.", style={'color':'#94a3b8','paddingTop':'120px','textAlign':'center','height':'360px'})
    else:
        # Need to merge airport master here
        if not os.path.exists(AIRPORT_MASTER_CSV):
            return html.Div(f"Airport master file not found: {AIRPORT_MASTER_CSV}", style={'color':'#ff6b6b','paddingTop':'120px','textAlign':'center','height':'360px'})

        master = _safe_read_csv(AIRPORT_MASTER_CSV)
        if master is None or master.empty:
            return html.Div("Airport master is empty or couldn't be read.", style={'color':'#94a3b8','paddingTop':'120px','textAlign':'center','height':'360px'})

        # Normalize names to avoid whitespace issues
        df = _normalize_column_names(df)
        master = _normalize_column_names(master)

        # Attempt exact join first
        merged, matched = _attempt_exact_join(df, master)
        total = merged.shape[0] if merged is not None else 0
        pct = (matched / total * 100) if total else 0
        print(f"[map.build_map_component] exact join matched {matched} / {total} rows ({pct:.1f}%).")

        # If too few matches, do fuzzy fallback
        if matched == 0 or pct < 5.0:
            print("[map.build_map_component] performing fuzzy matching fallback...")
            # perform fuzzy mapping - returns incidents with mapped coords
            incidents_with_mapped = _fuzzy_map(df.copy(), master)
            # combine mapped coords into merged result
            # use mapped lat/lon where merged lacks them
            if merged is None:
                merged = incidents_with_mapped.copy()
            else:
                merged['_mapped_lat'] = incidents_with_mapped.get('_mapped_lat')
                merged['_mapped_lon'] = incidents_with_mapped.get('_mapped_lon')
                merged['_final_lat'] = merged[MASTER_LAT_COL].combine_first(merged['_mapped_lat'])
                merged['_final_lon'] = merged[MASTER_LON_COL].combine_first(merged['_mapped_lon'])
                merged['Latitude'] = pd.to_numeric(merged['_final_lat'], errors='coerce')
                merged['Longitude'] = pd.to_numeric(merged['_final_lon'], errors='coerce')

            # if we didn't set Latitude/Longitude yet, set from mapped
            if 'Latitude' not in merged.columns:
                merged['Latitude'] = pd.to_numeric(merged.get('_mapped_lat'), errors='coerce')
            if 'Longitude' not in merged.columns:
                merged['Longitude'] = pd.to_numeric(merged.get('_mapped_lon'), errors='coerce')

            n_final = merged.dropna(subset=['Latitude','Longitude']).shape[0]
            pct_final = (n_final / total * 100) if total else 0
            print(f"[map.build_map_component] after fuzzy fallback: {n_final} / {total} rows have coordinates ({pct_final:.1f}%).")

            coords = merged.dropna(subset=['Latitude','Longitude']).copy()
        else:
            # exact join is fine; ensure Latitude/Longitude columns exist
            merged['Latitude'] = pd.to_numeric(merged.get(MASTER_LAT_COL), errors='coerce')
            merged['Longitude'] = pd.to_numeric(merged.get(MASTER_LON_COL), errors='coerce')
            coords = merged.dropna(subset=['Latitude','Longitude']).copy()

    # If, after all attempts, no coords, return message
    if coords is None or coords.empty:
        return html.Div("No incidents with valid coordinates after joining/mapping.", style={'color':'#94a3b8','paddingTop':'120px','textAlign':'center','height':'360px'})

    # Build hover text for each point
    def hover_text(row):
        parts = []
        if 'S/N' in row.index and pd.notna(row['S/N']): parts.append(f"S/N: {row['S/N']}")
        if 'Date' in row.index and pd.notna(row['Date']): parts.append(f"Date: {row['Date']}")
        if INCIDENT_AIRPORT_COL in row.index and pd.notna(row[INCIDENT_AIRPORT_COL]): parts.append(f"Airport: {row[INCIDENT_AIRPORT_COL]}")
        # include master code if present
        if '_master_code' in row.index and pd.notna(row.get('_master_code')): parts.append(f"Code: {row.get('_master_code')}")
        if '_mapped_code' in row.index and pd.notna(row.get('_mapped_code')): parts.append(f"Mapped: {row.get('_mapped_code')}")
        return "<br>".join(parts)

    coords['hover'] = coords.apply(hover_text, axis=1)

    # center map
    center_lat = coords['Latitude'].mean()
    center_lon = coords['Longitude'].mean()

    fig = px.scatter_mapbox(
        coords,
        lat='Latitude',
        lon='Longitude',
        hover_name='hover',
        hover_data={c: True for c in ['S/N', 'Date'] if c in coords.columns},
        zoom=4,
        height=360
    )
    fig.update_layout(mapbox_style='open-street-map', margin={'l':0,'r':0,'t':0,'b':0}, mapbox_center={'lat': center_lat, 'lon': center_lon})

    return dcc.Graph(figure=fig, config={'displayModeBar': False}, style={'height':'360px'})
