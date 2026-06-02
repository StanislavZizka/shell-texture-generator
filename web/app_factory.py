"""Flask application factory."""

from __future__ import annotations

import io
import os
import sys

import matplotlib
matplotlib.use("Agg")
from flask import Flask

from config import STATIC_DIR, TEMPLATES_DIR, config
from routes.api import api
from routes.pages import pages


def _ensure_utf8_streams() -> None:
    if sys.stdout.encoding != "utf-8":
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        except (TypeError, ValueError):
            pass
    if sys.stderr.encoding != "utf-8":
        try:
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
        except (TypeError, ValueError):
            pass


def register_error_handlers(app: Flask) -> None:
    """Register consistent JSON error handlers."""

    @app.errorhandler(400)
    def bad_request_error(_error):
        return {"error": "Bad request"}, 400

    @app.errorhandler(404)
    def not_found_error(_error):
        return {"error": "Page not found"}, 404

    @app.errorhandler(500)
    def internal_error(_error):
        return {"error": "Internal server error"}, 500


def create_app(config_name: str | None = None) -> Flask:
    """Create and configure the Flask application."""

    if config_name is None:
        config_name = os.environ.get("FLASK_CONFIG", "development")

    app = Flask(
        __name__,
        template_folder=str(TEMPLATES_DIR),
        static_folder=str(STATIC_DIR),
        static_url_path="/static",
    )
    app.config.from_object(config[config_name])
    app.register_blueprint(pages)
    app.register_blueprint(api)
    register_error_handlers(app)
    return app
