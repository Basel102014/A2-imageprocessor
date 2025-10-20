# import jwt, datetime
# from config import Config

# def encode_jwt(username, role):
#     payload = {
#         "user": username,
#         "role": role,
#         "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
#     }
#     print(f"[DEBUG] Encoding JWT for user='{username}', role='{role}', exp={payload['exp']}")
#     token = jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")
#     print(f"[DEBUG] Generated JWT: {token}")
#     return token

# def decode_jwt(token):
#     print(f"[DEBUG] Decoding JWT: {token}")
#     try:
#         decoded = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
#         print(f"[DEBUG] Decoded JWT payload: {decoded}")
#         return decoded
#     except jwt.ExpiredSignatureError:
#         print("[DEBUG] JWT decode failed: ExpiredSignatureError")
#         return None
#     except Exception as e:
#         print(f"[DEBUG] JWT decode failed: {e}")
#         return None
