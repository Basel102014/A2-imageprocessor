import os

class Config:
    # Flask secret
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret")

    # App paths
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
    RESULT_FOLDER = os.path.join(os.getcwd(), "results")

    # Cognito config
    COGNITO_DOMAIN = "https://ap-southeast-2og65686wi.auth.ap-southeast-2.amazoncognito.com"
    COGNITO_USER_POOL_ID = "ap-southeast-2_Og65686Wi"
    COGNITO_CLIENT_ID = "60ueg8ts3d58d4vdod86vc95rl"
    COGNITO_CLIENT_SECRET = "3gtqge8jb0av1pv8161onf925sprc5th7u43ad63ltne5014jno"
    COGNITO_REDIRECT_URI = "http://localhost:8080/auth/authorize"

    # Debug info
    print("[DEBUG] Config loaded:")
    print(f"  SECRET_KEY → {'set from env' if os.environ.get('SECRET_KEY') else 'using default'}")
    print(f"  UPLOAD_FOLDER → {UPLOAD_FOLDER}")
    print(f"  RESULT_FOLDER → {RESULT_FOLDER}")
    print(f"  COGNITO_DOMAIN → {COGNITO_DOMAIN}")
    print(f"  COGNITO_USER_POOL_ID → {COGNITO_USER_POOL_ID}")
    print(f"  COGNITO_CLIENT_ID → {COGNITO_CLIENT_ID}")
    print(f"  COGNITO_CLIENT_SECRET → {'set' if COGNITO_CLIENT_SECRET else 'missing'}")
    print(f"  COGNITO_REDIRECT_URI → {COGNITO_REDIRECT_URI}")
