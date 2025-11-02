import json
import time
from pathlib import Path
from utils.logger import log_message

def load_history(file_path: Path) -> dict:

    if file_path.exists():
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return {k: v for k, v in data.items() if time.time() - v < 86400}
        except (json.JSONDecodeError, TypeError) as e:
            log_message(f"Warning: Could not read history file {file_path.name}: {e}")
    return {}

def save_history(file_path: Path, data: dict):

    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
