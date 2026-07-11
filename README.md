# 👑 Badshah Ka Wazeer Kon — Digital Multiplayer Game

A web-based version of the classic Pakistani childhood deduction game, built with **Python + Streamlit**.
Four players join a shared room from four different devices, get secret roles each round,
and the Wazeer has to catch the Chor.

## Roles

| Role | Emoji | Behaviour |
|---|---|---|
| Badshah (King) | 👑 | Revealed to everyone immediately |
| Wazeer (Minister) | 🧠 | Revealed immediately, must guess the Chor |
| Sipahi (Soldier) | 🛡️ | Hidden until the result phase |
| Chor (Thief) | 🥷 | Hidden until the result phase — the Wazeer's target |

## How multiplayer works (read this first)

Streamlit does not have built-in real-time networking between separate browser
sessions — it's a single-user, rerun-on-interaction framework. To make four
devices share one game, this app uses a simple, well-understood trick:

- Each room's full state (players, roles, phase, scores, round history) lives
  in one JSON file: `data/rooms/<ROOM_CODE>.json`.
- Every connected device polls that file every ~2 seconds
  (via the `streamlit-autorefresh` package) and re-renders whatever the file
  currently says.
- Whoever performs an action (joins, confirms their role, submits a guess,
  clicks Continue) writes the updated state back to the same file.
- Writes are atomic (write to a temp file, then `os.replace`) so a reader
  never sees a half-written file.

This means **all players must be pointed at the same running Streamlit server**
(same machine/network — e.g. run it on one laptop and have others open it via
its local network URL, or deploy it to Streamlit Community Cloud so it has one
public URL everyone can hit from their own device).

If `streamlit-autorefresh` isn't installed, the app still works — a manual
"🔄 Refresh" button appears in the sidebar instead of automatic polling.

## Project Structure

```
Badshah-Ka-Wazeer-Kon/
├── app.py            # Streamlit UI + page routing (the entry point)
├── game.py           # Round/phase logic (role assignment, guessing, scoring transitions)
├── room.py           # Room creation/joining + persistence
├── scoring.py        # Scoring table and score application
├── players.py        # Player/role lookup helpers
├── utils.py           # IDs, room codes, JSON file storage
├── assets/            # images/icons/sounds (empty — add your own)
├── data/rooms/         # one JSON file per active room (auto-created)
├── requirements.txt
└── README.md
```

## Setup

```bash
# 1. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

Streamlit will print a **Local URL** and a **Network URL**. Share the Network
URL with other devices on the same Wi-Fi so they can join the same room.
For play across different networks, deploy the app (e.g. Streamlit
Community Cloud) and share the public URL instead.

## How to Play

1. **Host** opens the app, goes to *Create Room*, enters their name and the
   number of rounds (default 5), and gets a 5-character **Room Code**.
2. The other three players open the app on their own devices, go to *Join
   Room*, and enter the room code + their name.
3. Once 4 players have joined, the game starts automatically.
4. Each round:
   - Every player privately sees their own role and clicks **Continue**.
   - Once everyone has continued, **Badshah** and **Wazeer** are revealed to
     everyone.
   - The **Wazeer** picks which of the two remaining players is the **Chor**.
   - Results are revealed to everyone: correct/incorrect, all roles, and the
     updated scoreboard. Everyone clicks **Continue** to move to the next round.
5. After the configured number of rounds, the **Final Leaderboard** is shown
   with the winner. The host can start a rematch in the same room.

## Scoring (default — tune in `scoring.py`)

| Role | If Wazeer guesses correctly | If Wazeer guesses incorrectly |
|---|---|---|
| Badshah | +100 | +100 |
| Wazeer | +80 | -20 |
| Sipahi | +50 | +50 |
| Chor | 0 | +120 |

## Known limitations / things to extend

- Polling-based sync (every 2s), not push-based — fine for a 4-player party
  game, noticeably laggier than a websocket-based approach.
- No authentication — anyone with the room code can join until it's full.
- Single-process file storage assumes one Streamlit server instance; it
  won't work correctly if you run multiple server processes behind a load
  balancer without a shared filesystem.
- Bonus ideas from the spec (timers, chat, AI-filled seats, themes, sound,
  Firebase/DB backend, tournament mode, etc.) are not implemented — the
  code is structured (separate `game.py`/`room.py`/`scoring.py`) to make
  adding them straightforward.
