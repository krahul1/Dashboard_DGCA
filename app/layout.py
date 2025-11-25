# app/layout.py
from dash import html, dcc
import datetime
from datetime import datetime

APP_STYLE = {
    'fontFamily': 'Inter, Arial, sans-serif',
    'background': '#071028',
    'color': '#e6eef6',
    'minHeight': '100vh'
}

HEADER_STYLE = {
    'display': 'flex',
    'justifyContent': 'space-between',
    'alignItems': 'center',
    'padding': '18px 24px',
    'borderBottom': '1px solid rgba(255,255,255,0.03)'
}

NAV_STYLE_WRAPPER = {'padding': '12px 24px'}

FILTER_BAR_STYLE = {
    'display': 'flex',
    'gap': '12px',
    'alignItems': 'center',
    'padding': '12px 24px',
    'background': 'rgba(255,255,255,0.02)',
    'borderRadius': '8px',
    'margin': '12px 24px',
    'flexWrap': 'wrap'
}

CONTROL_STYLE = {
    "height": "36px",
    "padding": "6px 10px",
    "borderRadius": "8px",
    "border": "1px solid rgba(255,255,255,0.15)",
    "background": "rgba(0,0,0,0.2)",
    "color": "#e6eef6",
    "boxSizing": "border-box",
}

SMALL_CONTROL_STYLE = {**CONTROL_STYLE, "minWidth": "120px"}


def header():
    return html.Div(style=HEADER_STYLE, children=[
        html.Div(html.H1("Occurrence & Investigation Dashboard",
                         style={'fontSize': '18px', 'margin': 0})),
        
        html.Div([
            
            html.Button("Export Storyboard as PDF", id="btn-print",
                        style={
                            'background': '#2dd4bf',
                            'color': '#042024',
                            'border': 'none',
                            'padding': '8px 12px',
                            'borderRadius': '8px'
                        }),
                        
        
            html.Div(
                f"Last refresh: {datetime.today().strftime('%d-%m-%Y')}",
                     style={'fontSize': '12px', 'color': '#94a3b8',
                            'display': 'inline-block', 'marginLeft': '12px'})
        ])
    ])


def nav():
    return html.Div(style=NAV_STYLE_WRAPPER, children=[
        html.Div(style={'display': 'flex', 'gap': '10px'}, children=[
            html.Button("Dashboard", id="nav-dashboard"),
            html.Button("Detail", id="nav-detail"),
            html.Button("Recommendations", id="nav-recs"),
            html.Button("Storyboard", id="nav-story"),
        ])
    ])


def filters_bar():
    base_style = {
        'height': '40px',
        'display': 'inline-flex',
        'alignItems': 'center',
        'border': '1px solid rgba(255,255,255,0.15)',
        'borderRadius': '8px',
        'padding': '0 10px',
        'background': 'rgba(255,255,255,0.05)',
        'color': '#e6eef6',
        'minWidth': '140px'
    }

    return html.Div(style={
        'display': 'flex',
        'gap': '12px',
        'alignItems': 'center',
        'padding': '12px 24px',
        'flexWrap': 'nowrap',
        'overflowX': 'visible'
    }, children=[

        # SEARCH INPUT
        html.Div(style={**base_style, 'flex': '1', 'minWidth': '260px'}, children=[
            dcc.Input(
                id='search-input',
                placeholder='Search S/N, Flight No., Remarks...',
                type='text',
                style={'width': '100%', 'background': 'transparent', 'border': 'none'}
            )
        ]),

        # AIRPORT
        html.Div(style=base_style, children=[
            dcc.Dropdown(
                id='airport-filter',
                options=[],
                value=None,
                placeholder='Airport',
                clearable=True,
                style={'background': 'transparent', 'border': 'none', 'width': '100%'}
            )
        ]),

        # OPERATOR
        html.Div(style=base_style, children=[
            dcc.Dropdown(
                id='operator-filter',
                options=[],
                value=None,
                placeholder='Operator',
                clearable=True,
                style={'background': 'transparent', 'border': 'none', 'width': '100%'}
            )
        ]),

        # AIRCRAFT
        html.Div(style=base_style, children=[
            dcc.Dropdown(
                id='aircraft-filter',
                options=[],
                value=None,
                placeholder='Aircraft Type',
                clearable=True,
                style={'background': 'transparent', 'border': 'none', 'width': '110%'}
            )
        ]),

        # PHASE
        html.Div(style=base_style, children=[
            dcc.Dropdown(
                id='phase-filter',
                options=[],
                value=None,
                placeholder='Phase',
                clearable=True,
                style={'background': 'transparent', 'border': 'none', 'width': '110%'}
            )
        ]),

        # STATUS
        html.Div(style=base_style, children=[
            dcc.Dropdown(
                id='status-filter',
                options=[],
                value=None,
                placeholder='Status',
                clearable=True,
                style={'background': 'transparent', 'border': 'none', 'width': '100%'}
            )
        ]),

        # MONTH PICKER – SAME BOX
        html.Div(style=base_style, children=[
            dcc.DatePickerSingle(
                id='month-picker',
                placeholder='Month / Year',
                display_format='MMMM YYYY',
                clearable=True,
                
                style={'background': 'transparent', 'border': 'none'}
            )
        ])
    ])



def get_layout():
    return html.Div(style=APP_STYLE, children=[
        header(),
        nav(),
        filters_bar(),
        html.Div(id='page-content', style={'padding': '0 20px 20px'}),  # dynamic page content
        dcc.Store(
            id='store-filter',
            data={
                'search': '',
                'airport': 'All',
                'operator': 'All',
                'aircraft': 'All',
                'phase': 'All',
                'status': 'All',
                'month': ''
            }
        )
    ])
