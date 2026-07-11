"""
room.py
Everything to do with creating a room, joining a room, and persisting
room state to disk. The room dict is the single source of truth that
every connected device reads and writes.

Room shape:
{
  "room_code": "AB12C",
  "created_at": <float timestamp>,
  "max_players": 4,
  "total_rounds": 5,
  "current_round": 0,
  "phase": "waiting" | "role_view" | "guessing" | "result" | "finished",
  "host_id": "<player id>",
  "players": [{"id", "name", "score", "last_round_points"}, ...],
  "roles": {"<player id>": "Badshah"/"Wazeer"/"Sipahi"/"Chor"},
  "confirmations": {"<player id>": bool},   # used for role_view + result phases
  "wazeer_guess": "<player id>" | None,
  "round_history": [ {round, roles, guess, correct} ]
}
"""

from utils import generate_room_code, room_exists, read_room, write_room, new_id, now

MAX_PLAYERS = 4


def create_room(host_name: str, total_rounds: int = 5):
    room_code = generate_room_code()
    while room_exists(room_code):
        room_code = generate_room_code()

    host_id = new_id()
    room = {
        "room_code": room_code,
        "created_at": now(),
        "max_players": MAX_PLAYERS,
        "total_rounds": max(1, int(total_rounds)),
        "current_round": 0,
        "phase": "waiting",
        "host_id": host_id,
        "players": [
            {"id": host_id, "name": host_name.strip(), "score": 0, "last_round_points": 0}
        ],
        "roles": {},
        "confirmations": {},
        "wazeer_guess": None,
        "round_history": [],
    }
    write_room(room_code, room)
    return room_code, host_id


def join_room(room_code: str, player_name: str):
    """Returns (player_id, error_message). Exactly one will be None."""
    room = read_room(room_code)
    if room is None:
        return None, "Room not found. Double-check the room code."
    if room["phase"] != "waiting":
        return None, "This game has already started — ask the host for a new room."
    if len(room["players"]) >= room["max_players"]:
        return None, "This room is already full (4/4 players)."
    if not player_name.strip():
        return None, "Enter a name to join."
    for p in room["players"]:
        if p["name"].strip().lower() == player_name.strip().lower():
            return None, "That name is already taken in this room — pick another."

    player_id = new_id()
    room["players"].append({"id": player_id, "name": player_name.strip(), "score": 0, "last_round_points": 0})
    write_room(room_code, room)
    return player_id, None


def get_room(room_code: str):
    if not room_code:
        return None
    return read_room(room_code)


def save_room(room: dict):
    write_room(room["room_code"], room)


def reset_for_rematch(room: dict):
    """Keeps the same players + room code, resets scores and rounds."""
    for p in room["players"]:
        p["score"] = 0
        p["last_round_points"] = 0
    room["current_round"] = 0
    room["phase"] = "waiting"
    room["roles"] = {}
    room["confirmations"] = {}
    room["wazeer_guess"] = None
    room["round_history"] = []
