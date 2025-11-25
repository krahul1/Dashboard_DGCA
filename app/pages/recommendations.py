# app/pages/recommendations.py
from dash import html, dash_table
import pandas as pd

def render_recommendations(df: pd.DataFrame):
    if df is None or df.empty:
        pending = pd.DataFrame()
    else:
        pending = df[df['ATR of Recommendations'].str.lower()=='pending'] if ('ATR of Recommendations' in df.columns) else df.iloc[0:0]
    return html.Div(children=[
        html.H2('Recommendations Board'), html.Div(f'Pending: {len(pending)}'),
        dash_table.DataTable(columns=[{'name':c,'id':c} for c in ['S/N','Recommendations','ATR of Recommendations','Status']],
                             data=pending[['S/N','Recommendations','ATR of Recommendations','Status']].to_dict('records') if not pending.empty and set(['S/N','Recommendations','ATR of Recommendations','Status']).issubset(pending.columns) else [],
                             page_size=8)
    ])
