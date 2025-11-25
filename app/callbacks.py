# app/callbacks.py
from dash.dependencies import Input, Output
from dash import callback_context
import pandas as pd
from pandas.tseries.offsets import MonthEnd

from .utils import load_data
from .pages.home import (
    render_dashboard,
    render_detail,
    render_recommendations,
    render_storyboard,
)

# -----------------------------------------
# Helper: dropdown option builder
# -----------------------------------------
def make_options_from_series(series):
    if series is None:
        return [{'label': 'All', 'value': 'All'}]

    try:
        vals = sorted([str(x) for x in pd.Series(series).dropna().unique()])
        return [{'label': 'All', 'value': 'All'}] + [
            {'label': v, 'value': v} for v in vals
        ]
    except:
        return [{'label': 'All', 'value': 'All'}]


# -----------------------------------------
# Filtering logic
# -----------------------------------------
def apply_filters(df, store):
    if df is None or df.empty:
        return df
    s = store or {}

    # Exact filters
    airport_val = s.get('airport')
    if airport_val and airport_val != 'All':
        if 'Airport / Place of occurrence' in df.columns:
            df = df[df['Airport / Place of occurrence'] == airport_val]

    operator_val = s.get('operator')
    if operator_val and operator_val != 'All' and 'Operator' in df.columns:
        df = df[df['Operator'] == operator_val]

    aircraft_val = s.get('aircraft')
    if aircraft_val and aircraft_val != 'All' and 'Aircraft Type' in df.columns:
        df = df[df['Aircraft Type'] == aircraft_val]

    phase_val = s.get('phase')
    if phase_val and phase_val != 'All' and 'Phase of flight' in df.columns:
        df = df[df['Phase of flight'] == phase_val]

    status_val = s.get('status')
    if status_val and status_val != 'All' and 'Status' in df.columns:
        df = df[df['Status'].str.lower() == status_val.lower()]

    # Month filter
    month_val = s.get('month')
    if month_val and 'Date' in df.columns:
        try:
            selected = pd.to_datetime(month_val, errors='coerce')
            if pd.notna(selected):
                start = pd.Timestamp(selected.year, selected.month, 1)
                end = start + MonthEnd(0)
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                df = df[(df['Date'] >= start) & (df['Date'] <= end)]
        except:
            pass

    # Free text search
    q = (s.get('search') or "").strip().lower()
    if q:
        def match(row):
            for col in [
                'S/N', 'Flight No', 'Operator',
                'Brief Description', 'Airport / Place of occurrence'
            ]:
                if col in df.columns and pd.notna(row.get(col)):
                    if q in str(row[col]).lower():
                        return True
            return False

        df = df[df.apply(match, axis=1)]

    return df


# -----------------------------------------
# Register Callbacks
# -----------------------------------------
def register_callbacks(app):

    # Populate dropdown options
    @app.callback(
        [
            Output('airport-filter', 'options'),
            Output('operator-filter', 'options'),
            Output('aircraft-filter', 'options'),
            Output('phase-filter', 'options'),
            Output('status-filter', 'options'),
        ],
        [Input('page-content', 'children')],
        prevent_initial_call=False
    )
    def populate_filter_options(_children):
        df = load_data()
        if df is None or df.empty:
            return [{'label': 'All', 'value': 'All'}] * 5

        # Determine correct airport column
        airport_series = None
        if 'Airport / Place of occurrence' in df.columns:
            airport_series = df['Airport / Place of occurrence']
        elif 'Airport' in df.columns:
            airport_series = df['Airport']

        airport_opts = make_options_from_series(airport_series)
        operator_opts = make_options_from_series(df['Operator']) if 'Operator' in df.columns else [{'label': 'All', 'value': 'All'}]
        aircraft_opts = make_options_from_series(df['Aircraft Type']) if 'Aircraft Type' in df.columns else [{'label': 'All', 'value': 'All'}]
        phase_opts = make_options_from_series(df['Phase of flight']) if 'Phase of flight' in df.columns else [{'label': 'All', 'value': 'All'}]
        status_opts = make_options_from_series(df['Status']) if 'Status' in df.columns else [{'label': 'All', 'value': 'All'}]

        return airport_opts, operator_opts, aircraft_opts, phase_opts, status_opts

    # Update store when any filter changes
    @app.callback(
        Output('store-filter', 'data'),
        [
            Input('search-input', 'value'),
            Input('airport-filter', 'value'),
            Input('operator-filter', 'value'),
            Input('aircraft-filter', 'value'),
            Input('phase-filter', 'value'),
            Input('status-filter', 'value'),
            Input('month-picker', 'date'),
        ],
        prevent_initial_call=False
    )
    def update_store(search, airport, operator, aircraft, phase, status, month_date):
        return {
            'search': search or "",
            'airport': airport or "All",
            'operator': operator or "All",
            'aircraft': aircraft or "All",
            'phase': phase or "All",
            'status': status or "All",
            'month': month_date or "",
        }

    # Router + reactive dashboard
    @app.callback(
        Output('page-content', 'children'),
        [
            Input('nav-dashboard', 'n_clicks'),
            Input('nav-detail', 'n_clicks'),
            Input('nav-recs', 'n_clicks'),
            Input('nav-story', 'n_clicks'),
            Input('store-filter', 'data'),
        ],
        prevent_initial_call=False
    )
    def display_page(*args):
        ctx = callback_context
        df = load_data()

        store = args[-1]
        filtered_df = apply_filters(df.copy() if df is not None else df, store)

        if not ctx.triggered:
            return render_dashboard(filtered_df)

        trig = ctx.triggered[0]['prop_id'].split('.')[0]

        if trig == 'store-filter':
            return render_dashboard(filtered_df)
        if trig == 'nav-detail':
            return render_detail(filtered_df)
        if trig == 'nav-recs':
            return render_recommendations(filtered_df)
        if trig == 'nav-story':
            return render_storyboard(filtered_df)

        return render_dashboard(filtered_df)