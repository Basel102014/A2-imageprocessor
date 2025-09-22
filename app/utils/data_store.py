import json
import os
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(__file__), "../../data/metadata.json")

def save_metadata(input_file, output_file, user):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                metadata = json.load(f)
            except json.JSONDecodeError:
                metadata = []
    else:
        metadata = []

    record = {
        "input": input_file,
        "output": output_file,
        "user": user,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    metadata.append(record)

    with open(DATA_FILE, "w") as f:
        json.dump(metadata, f, indent=2)

    return record

def load_metadata():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []
