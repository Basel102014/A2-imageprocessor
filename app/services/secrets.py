import boto3, json
from botocore.exceptions import ClientError

def get_secret():
    secret_name = "n11326158-secret-key"
    region_name = "ap-southeast-2"

    client = boto3.client("secretsmanager", region_name=region_name)
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret_str = get_secret_value_response["SecretString"]
        secret_dict = json.loads(secret_str)
        return secret_dict["COGNITO_CLIENT_SECRET"] 
    except ClientError as e:
        print("[DEBUG] Failed to retrieve secret:", e)
        return None
