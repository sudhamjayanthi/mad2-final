from flask import Flask
from .auth import auth_bp
from .admin import admin_bp
from .user import user_bp


def init_routes(app: Flask):
    """Initialize all blueprints with their respective URL prefixes"""
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(user_bp, url_prefix="/api/user")
