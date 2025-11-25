# debug_map.py
import os, pandas as pd
from pathlib import Path

AIRPORT_MASTER = "airports_india.csv"
INCIDENTS = "/Users/karunatirkey/Downloads/sample_data.csv"  # change if needed

print("Airports path:", AIRPORT_MASTER, "exists:", os.path.exists(AIRPORT_MASTER))
print("Incidents path:", INCIDENTS, "exists:", os.path.exists(INCIDENTS))

am = pd.read_csv(AIRPORT_MASTER) if os.path.exists(AIRPORT_MASTER) else pd.DataFrame()
inc = pd.read_csv(INCIDENTS, parse_dates=['Date']) if os.path.exists(INCIDENTS) else pd.DataFrame()

print("\n--- Airport master ---")
print("shape:", None if am is None else getattr(am,'shape',None))
print("columns:", list(am.columns)[:50])
print(am.head().to_string(index=False))

print("\n--- Incidents ---")
print("shape:", None if inc is None else getattr(inc,'shape',None))
print("columns:", list(inc.columns)[:50])
print(inc.head().to_string(index=False))

# try common join keys
possible_inc_keys = [c for c in inc.columns if c.lower() in ('airport','airport name','airport code','iata','icao','code')]
possible_am_keys  = [c for c in am.columns if 'airport' in c.lower() or 'code' in c.lower() or 'iata' in c.lower() or 'icao' in c.lower()]
print("\nDetected incident keys:", possible_inc_keys)
print("Detected airport master keys:", possible_am_keys)

# If we can detect a pair, test the join
if possible_inc_keys and possible_am_keys:
    inc_key = possible_inc_keys[0]
    am_key = possible_am_keys[0]
    print(f"\nTrying join: incidents.{inc_key} -> airport_master.{am_key}")
    merged = inc.merge(am[[am_key] + [c for c in am.columns if 'lat' in c.lower() or 'lon' in c.lower()]],
                       left_on=inc_key, right_on=am_key, how='left')
    # count how many got coords
    lat_cols = [c for c in merged.columns if 'lat' in c.lower()]
    lon_cols = [c for c in merged.columns if any(x in c.lower() for x in ('lon','lng','long'))]
    print("Found lat cols in merged:", lat_cols)
    print("Found lon cols in merged:", lon_cols)
    if lat_cols and lon_cols:
        merged[lat_cols[0]] = pd.to_numeric(merged[lat_cols[0]], errors='coerce')
        merged[lon_cols[0]] = pd.to_numeric(merged[lon_cols[0]], errors='coerce')
        print("Rows with coords after join:", merged.dropna(subset=[lat_cols[0], lon_cols[0]]).shape[0], "of", merged.shape[0])
    else:
        print("No lat/lon columns found in airport master.")
else:
    print("Could not detect sensible join keys automatically. Please post the column names of both CSVs.")
