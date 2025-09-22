from flask import Flask
from app.routes.auth import auth_bp
from app.routes.upload import upload_bp
from app.routes.process import process_bp
from app.routes.results import results_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(upload_bp, url_prefix="/upload")
    app.register_blueprint(process_bp, url_prefix="/process")
    app.register_blueprint(results_bp, url_prefix="/results")

    return app
