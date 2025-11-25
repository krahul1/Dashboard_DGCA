# run.py
from app import dash_app, get_layout, register_callbacks
from app.utils import load_data, load_airport_master
from app.auth import init_auth
import os

# Apply layout and register callbacks
dash_app.layout = get_layout()
register_callbacks(dash_app)

# Init auth (auth stub registers a blueprint on the Flask server)
try:
    init_auth(dash_app.server)
except Exception:
    # ignore if not configured
    pass

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    dash_app.run(host='0.0.0.0', port=port, debug=True)
