import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret")
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
    RESULT_FOLDER = os.path.join(os.getcwd(), "results")
    JWT_SECRET = os.environ.get("JWT_SECRET", "jwt_secret")