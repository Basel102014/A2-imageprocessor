import json
import os
from datetime import datetime
from PIL import Image  # <-- new import

DATA_FILE = os.path.join(os.path.dirname(__file__), "../../data/metadata.json")
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "../../uploads")

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

    resolution = None
    input_path = os.path.join(UPLOADS_DIR, input_file)
    if os.path.exists(input_path):
        try:
            with Image.open(input_path) as img:
                resolution = f"{img.width}x{img.height}"
        except Exception:
            resolution = "Unknown"

    record = {
        "input": input_file,
        "output": output_file,
        "user": user,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "resolution": resolution or "Unknown"
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
