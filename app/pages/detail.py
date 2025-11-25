# app/pages/detail.py
from dash import html, dash_table
import pandas as pd

def render_detail(df: pd.DataFrame):
    if df is None or df.empty or 'S/N' not in df.columns:
        return html.Div([html.Button('Back to dashboard', id='back-dashboard'), html.P("No detail available (data missing).")])
    if 1254 not in df['S/N'].values:
        row = df.iloc[0].to_dict()
    else:
        row = df[df['S/N']==1254].iloc[0].to_dict()
    return html.Div(children=[
        html.Button('Back to dashboard', id='back-dashboard'),
        html.H2(f"Investigation detail — S/N {row.get('S/N', '')}"),
        html.Div(f"Date: {row.get('Date', '')} | Airport: {row.get('Airport', '')} | Operator: {row.get('Operator', '')}"),
        html.H3('Brief description'), html.P(row.get('Brief Description', '')),
        html.H3('Findings'), html.Ul([html.Li(item.strip()) for item in str(row.get('Findings','')).split(';') if item]),
        html.H3('Probable cause'), html.P(row.get('Probable Cause', '')),
        html.Div(style={'padding':'12px','background':'rgba(255,255,255,0.02)','borderRadius':'8px','marginTop':'12px'}, children=[
            html.H4('Recommendations'), html.P(row.get('Recommendations','')), html.Div('ATR status: {}'.format(row.get('ATR of Recommendations',''))), html.Button('Upload ATR', id='btn-upload-atr')
        ])
    ])
