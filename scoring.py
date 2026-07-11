"""
scoring.py
The default scoring table from the project spec. Feel free to tune
these numbers — apply_round_scores() is the only place that needs to
change to adjust game balance.
"""

CORRECT_GUESS_POINTS = {
    "Badshah": 100,
    "Wazeer": 80,
    "Sipahi": 50,
    "Chor": 0,
}

INCORRECT_GUESS_POINTS = {
    "Badshah": 100,
    "Wazeer": -20,
    "Sipahi": 50,
    "Chor": 120,
}


def points_for_round(role: str, guess_correct: bool) -> int:
    table = CORRECT_GUESS_POINTS if guess_correct else INCORRECT_GUESS_POINTS
    return table.get(role, 0)


def apply_round_scores(room: dict, guess_correct: bool):
    """Mutates room['players'] in place, adding this round's points and
    recording last_round_points for display on the result screen."""
    for player in room["players"]:
        role = room["roles"].get(player["id"])
        pts = points_for_round(role, guess_correct)
        player["score"] = player.get("score", 0) + pts
        player["last_round_points"] = pts


def leaderboard(room: dict):
    return sorted(room["players"], key=lambda p: p.get("score", 0), reverse=True)
