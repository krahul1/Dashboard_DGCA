# app/pages/storyboard.py
from dash import html
from ..utils import UPLOADED_IMAGE

def render_storyboard(df):
    return html.Div(children=[
        html.H2('Storyboard / UI Sketches'),
        html.Img(src=UPLOADED_IMAGE, style={'maxWidth':'100%','borderRadius':'6px','border':'1px solid rgba(255,255,255,0.03)'}),
        html.P('Notes: Use this column order when importing data into the mock dataset: S/N, Date, Airport / Place of occurrence, Operator, Aircraft Type, Registration, Flight No., Sector, Phase of flight, Brief Description, Classification...')
    ])
