import os
import json
from datetime import datetime

def ensure_dir(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def ensure_file(path, default):
    if not os.path.exists(path):
        ensure_dir(path)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, ensure_ascii=False, indent=2)

def load_json(path, default):
    ensure_file(path, default)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    ensure_dir(path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def snapshot_json(path, snapshot_folder="snapshots"):
    now = datetime.now().strftime("%Y%m%d-%H%M%S")
    ensure_dir(snapshot_folder)
    base = os.path.basename(path)
    backup_path = os.path.join(snapshot_folder, f"{now}_{base}")
    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump(load_json(path, []), f, ensure_ascii=False, indent=2)
