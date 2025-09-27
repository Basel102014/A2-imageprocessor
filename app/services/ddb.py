import boto3
import time
import uuid

from app.services.param_store import get_param

REGION = get_param("/n11326158/REGION")
UPLOADS_TABLE = get_param("/n11326158/dynamodb/UPLOADS_TABLE")
RESULTS_TABLE = get_param("/n11326158/dynamodb/RESULTS_TABLE")

dynamodb = boto3.resource("dynamodb", region_name=REGION)
uploads_table = dynamodb.Table(UPLOADS_TABLE)
results_table = dynamodb.Table(RESULTS_TABLE)


# ---------- Uploads ----------
def save_upload_metadata(filename, resolution, size_bytes, user):
    record = {
        "id": str(uuid.uuid4()),
        "filename": filename,
        "resolution": resolution,
        "size_bytes": size_bytes,
        "user": user.get("username"),
        "timestamp": int(time.time())
    }
    print(f"[DEBUG] Saving upload metadata → {record}")
    uploads_table.put_item(Item=record)
    return record


def load_uploads():
    """Return all upload records with pagination handling."""
    print("[DEBUG] Scanning DynamoDB for uploads")
    items = []
    response = uploads_table.scan()
    items.extend(response.get("Items", []))

    while "LastEvaluatedKey" in response:
        response = uploads_table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        items.extend(response.get("Items", []))

    print(f"[DEBUG] Loaded {len(items)} upload records from DynamoDB")
    return items


def delete_upload_metadata(upload_id):
    print(f"[DEBUG] Deleting upload metadata id={upload_id}")
    uploads_table.delete_item(Key={"id": upload_id})


def clear_uploads():
    print("[DEBUG] Clearing all uploads from DynamoDB")
    items = load_uploads()
    with uploads_table.batch_writer() as batch:
        for item in items:
            batch.delete_item(Key={"id": item["id"]})
    print(f"[DEBUG] Cleared {len(items)} upload records")


# ---------- Results ----------
def save_result_metadata(input_file, output_file, user):
    record = {
        "id": str(uuid.uuid4()),
        "input": input_file,
        "output": output_file,
        "user": user.get("username"),
        "timestamp": int(time.time())
    }
    print(f"[DEBUG] Saving result metadata → {record}")
    results_table.put_item(Item=record)
    return record


def load_results():
    """Return all result records with pagination handling."""
    print("[DEBUG] Scanning DynamoDB for results")
    items = []
    response = results_table.scan()
    items.extend(response.get("Items", []))

    while "LastEvaluatedKey" in response:
        response = results_table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        items.extend(response.get("Items", []))

    print(f"[DEBUG] Loaded {len(items)} result records from DynamoDB")
    return items


def delete_result_metadata(result_id):
    print(f"[DEBUG] Deleting result metadata id={result_id}")
    results_table.delete_item(Key={"id": result_id})


def clear_results():
    print("[DEBUG] Clearing all results from DynamoDB")
    items = load_results()
    with results_table.batch_writer() as batch:
        for item in items:
            batch.delete_item(Key={"id": item["id"]})
    print(f"[DEBUG] Cleared {len(items)} result records")
