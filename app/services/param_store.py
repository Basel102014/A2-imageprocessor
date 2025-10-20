import boto3


def get_param(name):
    client = boto3.client("ssm", region_name="ap-southeast-2")
    response = client.get_parameter(Name=name)
    return response["Parameter"]["Value"]