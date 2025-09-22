import jwt, datetime
from config import Config

def encode_jwt(username):
    payload = {
        "user": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")

def decode_jwt(token):
    try:
        return jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
