import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret")
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
    RESULT_FOLDER = os.path.join(os.getcwd(), "results")
    JWT_SECRET = os.environ.get("JWT_SECRET", "jwt_secret")

    print("[DEBUG] Config loaded:")
    print(f"  SECRET_KEY → {'set from env' if os.environ.get('SECRET_KEY') else 'using default'}")
    print(f"  JWT_SECRET → {'set from env' if os.environ.get('JWT_SECRET') else 'using default'}")
    print(f"  UPLOAD_FOLDER → {UPLOAD_FOLDER}")
    print(f"  RESULT_FOLDER → {RESULT_FOLDER}")
