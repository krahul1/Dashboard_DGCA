# app/pages/example.py
from dash import html

def layout():
    return html.Div([
        html.H3("Example page"),
        html.P("Secondary page. Add your components here.")
    ])
