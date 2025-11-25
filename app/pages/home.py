# app/pages/home.py
from dash import html, dcc, dash_table
from pandas.tseries.offsets import MonthEnd
import plotly.express as px
import pandas as pd
from typing import Optional

from ..components.map import build_map_component
from .detail import render_detail as render_detail
from .recommendations import render_recommendations as render_recommendations
from .storyboard import render_storyboard as render_storyboard

def render_dashboard(df: Optional[pd.DataFrame]):
    if df is None:
        df = pd.DataFrame()

    total = len(df)
    open_count = df[df['Status'].str.lower() == 'open'].shape[0] if 'Status' in df.columns else 0
    recs_outstanding = df[df['ATR of Recommendations'].str.lower().isin(['pending'])].shape[0] if 'ATR of Recommendations' in df.columns else 0
    avg_close = '42 days'
    '''
    if not df.empty and 'Date' in df.columns:
        df_monthly = df.groupby(pd.Grouper(key='Date', freq='ME')).size().reset_index(name='count')
        fig_trend = px.line(df_monthly, x='Date', y='count', title='Open investigations trend')
    else:
        fig_trend = {}
    '''    
    # ----- Occurrences by Month -----
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    else:
        df['Date'] = pd.NaT

    today = pd.Timestamp.now()
    start = pd.Timestamp(year=today.year - 2, month=today.month, day=1)
    end = pd.Timestamp(year=today.year, month=today.month, day=1) + MonthEnd(0)

# filter rows inside window
    if not df.empty and df['Date'].notna().any():
        df_window = df[(df['Date'] >= start) & (df['Date'] <= end)].copy()
    else:
        df_window = df.iloc[0:0].copy()
    
    month_index = pd.date_range(start=start + MonthEnd(0), end=end, freq='M')  # month-end points
    if not df_window.empty:
    # resample by month-end (so the x axis shows months)
        monthly = df_window.set_index('Date').resample('M').size().reindex(month_index, fill_value=0)
    else:
        monthly = pd.Series(0, index=month_index)

    df_monthly = monthly.reset_index()
    df_monthly.columns = ['Date', 'count']

# build bar chart
    fig_month = px.bar(
        df_monthly,
        x='Date',
        y='count',
        title=f"Occurrences {start.strftime('%b %Y')} to {end.strftime('%b %Y')}",
        labels={'count': 'Occurrences', 'Date': 'Month'},
        height=360  # increase height (px) — change this value to taste
    )

# tidy x-axis formatting: show month and year, rotate ticks if crowded
    fig_month.update_xaxes(tickformat='%b\n%Y', tickangle=0)
    fig_month.update_layout(margin={'l': 20, 'r': 10, 't': 36, 'b': 30})

    table_columns = ['S/N', 'Date', 'Airport / Place of occurrence', 'Operator', 'Aircraft Type', 'Phase of flight', 'Status']
    table = dash_table.DataTable(
        id='table-occ',
        columns=[{'name': c, 'id': c} for c in table_columns],
        data=(df[table_columns].to_dict('records') if not df.empty and set(table_columns).issubset(df.columns) else []),
        page_size=8,
        style_table={'overflowX': 'auto'},
        style_cell_conditional=[{'if': {'column_id': 'S/N'}, 'width': '60px'}]
    )

    map_component = build_map_component(df)

    card_height = "360px"

    return html.Div(children=[
        html.Div(style={'display':'flex','gap':'12px','marginTop':'6px','marginBottom':'12px'}, children=[
            html.Div(style={'flex':'1','padding':'12px','background':'rgba(255,255,255,0.02)','borderRadius':'8px'}, children=[html.Div('Total occurrences', style={'fontSize':'14px'}), html.Div(total, style={'fontSize':'22px','fontWeight':'600'}), html.Div('(last 12 months)', style={'fontSize':'12px','color':'#94a3b8'})]),
            html.Div(style={'flex':'1','padding':'12px','background':'rgba(255,255,255,0.02)','borderRadius':'8px'}, children=[html.Div('Open investigations', style={'fontSize':'14px'}), html.Div(open_count, style={'fontSize':'22px','fontWeight':'600'})]),
            html.Div(style={'flex':'1','padding':'12px','background':'rgba(255,255,255,0.02)','borderRadius':'8px'}, children=[html.Div('Recommendations outstanding', style={'fontSize':'14px'}), html.Div(recs_outstanding, style={'fontSize':'22px','fontWeight':'600'})]),
            html.Div(style={'flex':'1','padding':'12px','background':'rgba(255,255,255,0.02)','borderRadius':'8px'}, children=[html.Div('Avg days to close', style={'fontSize':'14px'}), html.Div(avg_close, style={'fontSize':'22px','fontWeight':'600'})]),
        ]),

        html.Div(style={'display':'flex','gap':'12px'}, children=[
            html.Div(style={'flex':'2','padding':'0'}, children=[map_component]),
            html.Div(style={'flex':'1','display':'flex','flexDirection':'column'}, children=[
                html.Div(style={'padding':'0','background':'rgba(255,255,255,0.02)'}, children=[dcc.Graph(figure=fig_month, style={'height':card_height})]),
                #html.Div(style={'padding':'12px','background':'rgba(255,255,255,0.02)','borderRadius':'8px'}, children=[dcc.Graph(figure=fig_trend, style={'height':'160px'})])
            ])
        ]),

        html.Div(style={'marginTop':'12px','display':'flex','gap':'12px'}, children=[
            html.Div(style={'flex':'1','padding':'12px','background':'rgba(255,255,255,0.02)','borderRadius':'8px'}, children=[html.H4('Top Operators'), html.Ul([html.Li(f"{op} — {cnt}") for op,cnt in (df['Operator'].value_counts().head(6).items() if 'Operator' in df.columns else [])])]),
            html.Div(style={'flex':'1','padding':'12px','background':'rgba(255,255,255,0.02)','borderRadius':'8px'}, children=[html.H4('Top Airports'), html.Ul([html.Li(f"{ap} — {cnt}") for ap,cnt in (df['Airport / Place of occurrence'].value_counts().head(6).items() if 'Airport / Place of occurrence' in df.columns else [])])]),
            html.Div(style={'flex':'1','padding':'12px','background':'rgba(255,255,255,0.02)','borderRadius':'8px'}, children=[html.H4('Recommendations Board'), html.Div('ATR pending: {}'.format(recs_outstanding)), html.Button('View Recommendations', id='btn-view-recs')])
        ]),

        #html.Div(style={'marginTop':'12px','padding':'12px','background':'rgba(255,255,255,0.02)','borderRadius':'8px'}, children=[html.H4('Investigations table'), table])
    ])

# re-export convenience names for callbacks
__all__ = ["render_dashboard", "render_detail", "render_recommendations", "render_storyboard"]
