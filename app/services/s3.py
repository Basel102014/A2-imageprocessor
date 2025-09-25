import boto3
import os

REGION = "ap-southeast-2"
BUCKET = "n11326158-assessment2"

s3 = boto3.client("s3", region_name=REGION)


def upload_file_to_s3(local_path, key):
    print(f"[DEBUG] Uploading {local_path} → s3://{BUCKET}/{key}")
    s3.upload_file(local_path, BUCKET, key)
    return key


def download_file_from_s3(key, local_path):
    print(f"[DEBUG] Downloading s3://{BUCKET}/{key} → {local_path}")
    s3.download_file(BUCKET, key, local_path)
    return local_path


def generate_presigned_url(key, expires=3600):
    print(f"[DEBUG] Generating presigned URL for {key}, expires={expires}s")
    try:
        # Optional: verify existence first
        s3.head_object(Bucket=BUCKET, Key=key)
    except s3.exceptions.ClientError as e:
        print(f"[DEBUG] Presigned URL failed, object not found: {key}")
        return None

    return s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": BUCKET, "Key": key},
        ExpiresIn=expires
    )


def delete_file_from_s3(key):
    print(f"[DEBUG] Deleting s3://{BUCKET}/{key}")
    s3.delete_object(Bucket=BUCKET, Key=key)


def clear_prefix(prefix):
    print(f"[DEBUG] Clearing all objects under s3://{BUCKET}/{prefix}")
    continuation = None
    while True:
        kwargs = {"Bucket": BUCKET, "Prefix": prefix}
        if continuation:
            kwargs["ContinuationToken"] = continuation

        response = s3.list_objects_v2(**kwargs)
        if "Contents" not in response:
            break

        for obj in response["Contents"]:
            print(f"[DEBUG] Deleting {obj['Key']}")
            s3.delete_object(Bucket=BUCKET, Key=obj["Key"])

        if response.get("IsTruncated"):
            continuation = response["NextContinuationToken"]
        else:
            break


def list_files_with_prefix(prefix):
    """Return list of keys under a given prefix."""
    print(f"[DEBUG] Listing objects under s3://{BUCKET}/{prefix}")
    keys = []
    continuation = None
    while True:
        kwargs = {"Bucket": BUCKET, "Prefix": prefix}
        if continuation:
            kwargs["ContinuationToken"] = continuation

        response = s3.list_objects_v2(**kwargs)
        for obj in response.get("Contents", []):
            keys.append(obj["Key"])

        if response.get("IsTruncated"):
            continuation = response["NextContinuationToken"]
        else:
            break
    print(f"[DEBUG] Found {len(keys)} objects")
    return keys
