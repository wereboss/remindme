import os
from flask import Flask, render_template, send_from_directory
from app.db import init_app_db, get_db

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True, static_folder="static", template_folder="templates")
    
    # Default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-key-change-in-prod-12345"),
        DATABASE=os.path.join(app.instance_path, "notes.sqlite"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )

    if test_config is not None:
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Initialize database
    init_app_db(app)

    # Register blueprints
    from app.auth import auth_bp
    from app.notes import notes_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(notes_bp)

    # Main PWA entrypoint
    @app.route("/")
    def index():
        return render_template("index.html")

    # Serve service worker from root scope
    @app.route("/sw.js")
    def service_worker():
        response = send_from_directory(app.static_folder, "sw.js")
        response.headers["Content-Type"] = "application/javascript"
        response.headers["Service-Worker-Allowed"] = "/"
        return response

    return app
