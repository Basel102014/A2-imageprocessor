# import os
# import json
# import time
# from flask import current_app

# # Resolve to <project-root>/data
# PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
# DATA_DIR = os.path.join(PROJECT_ROOT, "data")
# os.makedirs(DATA_DIR, exist_ok=True)

# # File paths
# DATA_FILE = os.path.join(DATA_DIR, "results.json")
# UPLOAD_DATA_FILE = os.path.join(DATA_DIR, "uploads.json")


# # ---------- Results ----------

# def load_results():
#     """Load results metadata from file."""
#     print(f"[DEBUG] load_results() called → {DATA_FILE}")
#     if not os.path.exists(DATA_FILE):
#         print("[DEBUG] Results file not found, returning []")
#         return []
#     try:
#         with open(DATA_FILE, "r") as f:
#             data = json.load(f)
#             print(f"[DEBUG] Loaded {len(data)} result records")
#             return data
#     except Exception as e:
#         print(f"[DEBUG] Error loading results: {e}")
#         return []


# def save_results_metadata(input_file, output_file, user):
#     """Save a new result record with guaranteed timestamp and return it."""
#     print(f"[DEBUG] save_results_metadata(input={input_file}, output={output_file}, user={user})")
#     metadata = load_results()

#     record = {
#         "input": input_file,
#         "output": output_file,
#         "user": user.get("username") if isinstance(user, dict) else str(user),
#         "timestamp": int(time.time())  # always set timestamp here
#     }

#     metadata.append(record)
#     with open(DATA_FILE, "w") as f:
#         json.dump(metadata, f, indent=2)
#         print(f"[DEBUG] Appended new result record, total now {len(metadata)}")

#     return record


# # ---------- Uploads ----------

# def load_uploads():
#     """Load upload metadata from file."""
#     print(f"[DEBUG] load_uploads() called → {UPLOAD_DATA_FILE}")
#     if not os.path.exists(UPLOAD_DATA_FILE):
#         print("[DEBUG] Uploads file not found, returning []")
#         return []
#     try:
#         with open(UPLOAD_DATA_FILE, "r") as f:
#             data = json.load(f)
#             print(f"[DEBUG] Loaded {len(data)} upload records")
#             return data
#     except Exception as e:
#         print(f"[DEBUG] Error loading uploads: {e}")
#         return []


# def save_upload_metadata(filename, resolution, size_bytes, user):
#     """Save metadata for an uploaded file."""
#     print(f"[DEBUG] save_upload_metadata(filename={filename}, resolution={resolution}, size={size_bytes}, user={user})")
#     metadata = load_uploads()

#     record = {
#         "filename": filename,
#         "resolution": resolution,
#         "size_bytes": size_bytes,
#         "user": user.get("username") if isinstance(user, dict) else str(user),
#         "timestamp": int(time.time())  # track when upload happened
#     }

#     metadata.append(record)
#     with open(UPLOAD_DATA_FILE, "w") as f:
#         json.dump(metadata, f, indent=2)
#         print(f"[DEBUG] Appended new upload record, total now {len(metadata)}")

#     return record


# def prune_upload(filename):
#     """Remove an upload entry by filename."""
#     print(f"[DEBUG] prune_upload(filename={filename})")
#     metadata = load_uploads()
#     before = len(metadata)
#     metadata = [m for m in metadata if m.get("filename") != filename]
#     after = len(metadata)

#     with open(UPLOAD_DATA_FILE, "w") as f:
#         json.dump(metadata, f, indent=2)
#         print(f"[DEBUG] Pruned upload records: {before} → {after}")
