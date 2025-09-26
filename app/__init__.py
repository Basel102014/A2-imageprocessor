from flask import Flask
# from app.routes.auth import auth_bp
# from app.routes.upload import upload_bp
# from app.routes.process import process_bp
# from app.routes.results import results_bp
# from app.routes.client import client_bp

def create_app():
    print("[DEBUG] Creating Flask app instance")
    app = Flask(__name__)
    app.config.from_object("config.Config")
    print("[DEBUG] Loaded config from config.Config")

    # # Register blueprints
    # app.register_blueprint(auth_bp, url_prefix="/auth")
    # print("[DEBUG] Registered blueprint: auth_bp (/auth)")

    # app.register_blueprint(upload_bp, url_prefix="/upload")
    # print("[DEBUG] Registered blueprint: upload_bp (/upload)")

    # app.register_blueprint(process_bp, url_prefix="/process")
    # print("[DEBUG] Registered blueprint: process_bp (/process)")

    # app.register_blueprint(results_bp, url_prefix="/results")
    # print("[DEBUG] Registered blueprint: results_bp (/results)")

    # app.register_blueprint(client_bp)
    # print("[DEBUG] Registered blueprint: client_bp (no prefix)")

    print("[DEBUG] Flask app creation complete")
    return app
