import os
import json
from flask import current_app

# Resolve to <project-root>/data
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# File paths
DATA_FILE = os.path.join(DATA_DIR, "results.json")
UPLOAD_DATA_FILE = os.path.join(DATA_DIR, "uploads.json")


# ---------- Results ----------

def load_results():
    """Load results metadata from file."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_results_metadata(input_file, output_file, user):
    """Save a new result record and return it."""
    record = {
        "input": input_file,
        "output": output_file,
        "user": user.get("username"),
        "timestamp": user.get("timestamp") if user.get("timestamp") else None
    }
    metadata = load_results()
    metadata.append(record)
    with open(DATA_FILE, "w") as f:
        json.dump(metadata, f, indent=2)
    return record


# ---------- Uploads ----------

def load_uploads():
    """Load upload metadata from file."""
    if not os.path.exists(UPLOAD_DATA_FILE):
        return []
    with open(UPLOAD_DATA_FILE, "r") as f:
        return json.load(f)


def save_upload_metadata(filename, resolution, size_bytes, user):
    """Save metadata for an uploaded file."""
    record = {
        "filename": filename,
        "resolution": resolution,
        "size_bytes": size_bytes,
        "user": user.get("username")
    }
    metadata = load_uploads()
    metadata.append(record)
    with open(UPLOAD_DATA_FILE, "w") as f:
        json.dump(metadata, f, indent=2)
    return record


def prune_upload(filename):
    """Remove an upload entry by filename."""
    metadata = load_uploads()
    metadata = [m for m in metadata if m.get("filename") != filename]
    with open(UPLOAD_DATA_FILE, "w") as f:
        json.dump(metadata, f, indent=2)
