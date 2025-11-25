# app/app.py
from dash import Dash
import flask

def create_dash_app(server=None, url_base_pathname='/'):
    """Create and return a Dash app instance.
    Keep suppress_callback_exceptions True to allow modular callbacks.
    """
    if server is None:
        server = flask.Flask(__name__)
    app = Dash(__name__, server=server, url_base_pathname=url_base_pathname,
               suppress_callback_exceptions=True)
    return app

dash_app = create_dash_app()
