# bot/game_storage.py
import json
from pathlib import Path
from threading import Lock

DATAFILE = Path("users.json")
_lock = Lock()

def _ensure():
    if not DATAFILE.exists():
        DATAFILE.write_text(json.dumps({}))

def load_users():
    _ensure()
    with _lock:
        return json.loads(DATAFILE.read_text())

def save_users(data):
    with _lock:
        DATAFILE.write_text(json.dumps(data, indent=2))
