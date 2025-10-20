import boto3, json
from botocore.exceptions import ClientError

from app.services.param_store import get_param

def get_secret():
    secret_name = get_param("/n11326158/secrets/COGNITO_SECRET_NAME")
    region_name = get_param("/n11326158/REGION")

    client = boto3.client("secretsmanager", region_name=region_name)
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret_str = get_secret_value_response["SecretString"]
        secret_dict = json.loads(secret_str)
        return secret_dict["COGNITO_CLIENT_SECRET"] 
    except ClientError as e:
        print("[DEBUG] Failed to retrieve secret:", e)
        return None
