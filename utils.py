"""
utils.py
Shared helpers: ID generation, room-code generation, and JSON file
storage for room state. Rooms are stored as one JSON file per room
under data/rooms/<ROOM_CODE>.json, which is what lets four separate
browser sessions (on four separate devices) see the same game state.
"""

import json
import os
import random
import string
import time
import uuid
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "rooms"
DATA_DIR.mkdir(parents=True, exist_ok=True)

ROLES = ["Badshah", "Wazeer", "Sipahi", "Chor"]

ROLE_EMOJI = {
    "Badshah": "👑",
    "Wazeer": "🧠",
    "Sipahi": "🛡️",
    "Chor": "🥷",
}

ROLE_COLOR = {
    "Badshah": "#D4AF37",
    "Wazeer": "#4C6EF5",
    "Sipahi": "#2F9E44",
    "Chor": "#B02525",
}

ROLE_DESCRIPTIONS = {
    "Badshah": "The King. Revealed to everyone as soon as roles are dealt.",
    "Wazeer": "The Minister. Also revealed, and must correctly point out the Chor.",
    "Sipahi": "The Soldier. Stays hidden until the result phase.",
    "Chor": "The Thief. Stays hidden until the result phase — the Wazeer is trying to catch you.",
}


def new_id() -> str:
    """Short unique id used for players (not shown to users)."""
    return uuid.uuid4().hex[:12]


def generate_room_code(length: int = 5) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(random.choice(alphabet) for _ in range(length))


def room_path(room_code: str) -> Path:
    return DATA_DIR / f"{room_code.upper()}.json"


def room_exists(room_code: str) -> bool:
    return room_path(room_code).exists()


def read_room(room_code: str):
    path = room_path(room_code)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        # Extremely rare race with a concurrent write; caller should retry.
        return None


def write_room(room_code: str, data: dict):
    """Atomic write: write to a temp file then os.replace, so a reader
    never sees a half-written file even with several clients polling."""
    path = room_path(room_code.upper())
    tmp_path = path.with_suffix(f".{new_id()}.tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp_path, path)


def now() -> float:
    return time.time()
