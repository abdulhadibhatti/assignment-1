"""
game.py
Round and phase logic. Every function mutates the room dict in place;
the caller (app.py) is responsible for saving it back to disk after.

Phase sequence per round:
  role_view  -> each player privately sees their own role, clicks Continue
  guessing   -> Badshah + Wazeer become public; Wazeer picks the suspected Chor
  result     -> everyone's role is revealed, scores update, players click Continue
  (loop back to role_view for the next round, or -> finished)
"""

import random
from utils import ROLES
from scoring import apply_round_scores


def start_game(room: dict):
    room["current_round"] = 1
    _start_round(room)


def _start_round(room: dict):
    player_ids = [p["id"] for p in room["players"]]
    shuffled_roles = ROLES[:]
    random.shuffle(shuffled_roles)
    room["roles"] = dict(zip(player_ids, shuffled_roles))
    room["confirmations"] = {pid: False for pid in player_ids}
    room["wazeer_guess"] = None
    room["phase"] = "role_view"


# ---- role_view phase ----

def confirm_role(room: dict, player_id: str):
    room["confirmations"][player_id] = True


def all_confirmed(room: dict) -> bool:
    return len(room["confirmations"]) > 0 and all(room["confirmations"].values())


def advance_to_guessing(room: dict):
    room["phase"] = "guessing"


# ---- guessing phase ----

def badshah_id(room: dict):
    return next((pid for pid, role in room["roles"].items() if role == "Badshah"), None)


def wazeer_id(room: dict):
    return next((pid for pid, role in room["roles"].items() if role == "Wazeer"), None)


def chor_id(room: dict):
    return next((pid for pid, role in room["roles"].items() if role == "Chor"), None)


def hidden_player_ids(room: dict):
    """The two players the Wazeer must choose between: Sipahi and Chor."""
    return [pid for pid, role in room["roles"].items() if role in ("Sipahi", "Chor")]


def submit_guess(room: dict, guessed_player_id: str) -> bool:
    room["wazeer_guess"] = guessed_player_id
    correct = guessed_player_id == chor_id(room)
    apply_round_scores(room, correct)

    room["round_history"].append({
        "round": room["current_round"],
        "roles": dict(room["roles"]),
        "guess": guessed_player_id,
        "correct": correct,
    })
    room["phase"] = "result"
    room["confirmations"] = {p["id"]: False for p in room["players"]}
    return correct


# ---- result phase ----

def ready_for_next(room: dict, player_id: str):
    room["confirmations"][player_id] = True


def all_ready(room: dict) -> bool:
    return len(room["confirmations"]) > 0 and all(room["confirmations"].values())


def next_round_or_finish(room: dict):
    if room["current_round"] >= room["total_rounds"]:
        room["phase"] = "finished"
    else:
        room["current_round"] += 1
        _start_round(room)
