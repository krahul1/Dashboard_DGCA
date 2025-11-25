# app/auth.py
from flask import Blueprint, redirect, url_for, session

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    # TODO: implement login flow (Flask-Login / OAuth)
    return "Login placeholder"

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

def init_auth(server):
    """Register the auth blueprint with the Flask server."""
    server.register_blueprint(auth_bp, url_prefix="/auth")
