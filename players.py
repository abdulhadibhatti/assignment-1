"""
players.py
Small helpers for looking up players and roles inside a room dict.
Kept separate from room.py so game logic reads cleanly.
"""


def get_player(room: dict, player_id: str):
    for p in room["players"]:
        if p["id"] == player_id:
            return p
    return None


def get_player_by_name(room: dict, name: str):
    target = name.strip().lower()
    for p in room["players"]:
        if p["name"].strip().lower() == target:
            return p
    return None


def get_role(room: dict, player_id: str):
    return room.get("roles", {}).get(player_id)


def other_players(room: dict, player_id: str):
    return [p for p in room["players"] if p["id"] != player_id]


def is_host(room: dict, player_id: str) -> bool:
    return room.get("host_id") == player_id


def name_for(room: dict, player_id: str) -> str:
    p = get_player(room, player_id)
    return p["name"] if p else "Unknown"
