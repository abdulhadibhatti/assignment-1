"""
app.py
Badshah Ka Wazeer Kon — digital multiplayer game.

Run with:  streamlit run app.py

Multiplayer model (important to understand — see README):
Streamlit has no built-in networking between browser sessions. This
app fakes real-time multiplayer by keeping one JSON file per room on
disk (see utils.py / room.py). Every connected device polls that file
on an interval (via streamlit-autorefresh if installed, otherwise a
manual Refresh button) and re-renders based on whatever the file says
right now. Whoever's action changes the room state (joining, guessing,
clicking Continue) writes the new state back to the same file.
"""

import streamlit as st

import game
import room as room_mod
from players import get_player, get_role, name_for, is_host, other_players
from scoring import leaderboard
from utils import ROLE_EMOJI, ROLE_COLOR, ROLE_DESCRIPTIONS

st.set_page_config(
    page_title="Badshah Ka Wazeer Kon",
    page_icon="👑",
    layout="centered",
)

# ---------------------------------------------------------------------------
# Styling — modern "royal court" theme: deep navy base, gold + violet accents,
# glassmorphism cards, Poppins/Inter type.
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@700;900&family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --bg-0: #1b1d22;
        --bg-1: #22252c;
        --panel: #262a32;
        --gold: #c9a227;
        --teal: #3a7a72;
        --ink: #ece9e2;
        --ink-dim: #a3a7ad;
        --card-bg: #262a32;
        --card-border: #3a3e47;
    }

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; font-size: 16px; }
    h1, h2, h3, h4 { font-family: 'Merriweather', serif !important; letter-spacing: 0; }

    .stApp { background: var(--bg-0); }

    h1, h2, h3, h4, p, span, label, li, .stMarkdown, .stCaption { color: var(--ink) !important; }
    .stCaption, small, [data-testid="stCaptionContainer"] p { color: var(--ink-dim) !important; }

    .hero { text-align: center; padding: 10px 0 6px 0; }
    .hero .crown { font-size: 40px; }
    .hero h1 { font-size: 30px; font-weight: 900; margin: 8px 0 4px 0; color: var(--gold) !important; }
    .hero .subtitle { color: var(--ink-dim) !important; font-size: 15px; margin-bottom: 8px; }

    .card {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-left: 4px solid var(--teal);
        border-radius: 10px;
        padding: 24px 22px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.25);
        margin: 16px 0;
    }

    .role-card { text-align: center; padding: 34px 24px; border-radius: 12px; border-left: 4px solid var(--gold); }
    .role-card .emoji { font-size: 56px; line-height: 1; }
    .role-card .title { font-family: 'Merriweather', serif; font-size: 26px; font-weight: 900; margin: 10px 0 6px 0; }
    .role-card .desc { color: var(--ink-dim) !important; font-size: 15px; line-height: 1.5; }

    .mini-role-card {
        border-radius: 10px; padding: 18px 12px; text-align: center;
        background: var(--card-bg); border: 1px solid var(--card-border); border-top: 3px solid var(--teal);
    }
    .mini-role-card .emoji { font-size: 30px; }
    .mini-role-card .label { font-size: 12px; color: var(--ink-dim) !important; text-transform: uppercase; letter-spacing: 0.06em; }
    .mini-role-card .name { font-family: 'Merriweather', serif; font-weight: 700; font-size: 17px; margin-top: 4px; }

    .room-code {
        font-family: 'Inter', monospace;
        font-size: 30px; font-weight: 700; letter-spacing: 7px;
        text-align: center; padding: 16px 10px; border-radius: 10px;
        background: var(--panel);
        border: 1px solid var(--gold);
        color: var(--gold) !important;
    }
    .room-code.small { font-size: 19px; letter-spacing: 4px; padding: 9px; }

    .player-pill {
        display: inline-flex; align-items: center; gap: 8px;
        padding: 8px 15px; margin: 4px 6px 4px 0; border-radius: 8px;
        background: var(--panel); border: 1px solid var(--card-border);
        font-weight: 500; font-size: 14.5px;
    }
    .player-pill .avatar {
        width: 22px; height: 22px; border-radius: 50%;
        background: var(--teal);
        display: inline-flex; align-items: center; justify-content: center;
        font-size: 11px; font-weight: 700; color: #eef4f3;
    }

    .score-row {
        display: flex; justify-content: space-between; align-items: center;
        font-size: 16px; padding: 12px 16px; margin: 8px 0;
        background: var(--card-bg); border: 1px solid var(--card-border);
        border-radius: 8px;
    }
    .score-row .rank { color: var(--gold) !important; font-weight: 700; margin-right: 10px; }

    section[data-testid="stSidebar"] { background: var(--bg-1) !important; border-right: 1px solid var(--card-border); }
    section[data-testid="stSidebar"] * { color: var(--ink) !important; }

    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 15.5px !important;
        padding: 10px 18px !important;
        border: 1px solid var(--teal) !important;
        background: var(--teal) !important;
        color: #f3f6f5 !important;
        transition: background 0.15s ease;
    }
    .stButton > button:hover { background: #2e625b !important; }
    .stButton > button:disabled { opacity: 0.4 !important; }

    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0; padding: 10px 20px; font-weight: 600; font-size: 15px;
        background: var(--panel);
    }
    .stTabs [aria-selected="true"] { background: var(--card-bg) !important; border-bottom: 2px solid var(--gold) !important; }

    .stTextInput input, .stNumberInput input {
        border-radius: 8px !important;
        background: var(--panel) !important;
        border: 1px solid var(--card-border) !important;
        color: var(--ink) !important;
        font-size: 15.5px !important;
        padding: 10px 12px !important;
    }

    hr { border-color: var(--card-border) !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Autorefresh (optional dependency) so other players' actions show up
# without everyone needing to manually reload.
# ---------------------------------------------------------------------------

AUTOREFRESH_AVAILABLE = False
try:
    from streamlit_autorefresh import st_autorefresh
    AUTOREFRESH_AVAILABLE = True
except ImportError:
    pass


# ---------------------------------------------------------------------------
# Session bootstrap — recover identity from the URL so an accidental page
# reload doesn't kick a player out of the room mid-game.
# ---------------------------------------------------------------------------

def init_session():
    if "player_id" not in st.session_state:
        qp = st.query_params
        st.session_state.player_id = qp.get("pid")
        st.session_state.room_code = qp.get("room")


def enter_room(room_code: str, player_id: str):
    st.session_state.room_code = room_code
    st.session_state.player_id = player_id
    st.query_params.update({"room": room_code, "pid": player_id})


def leave_room():
    st.session_state.room_code = None
    st.session_state.player_id = None
    st.query_params.clear()


def avatar_letter(name: str) -> str:
    return (name.strip()[:1] or "?").upper()


init_session()

# ---------------------------------------------------------------------------
# Home page: create or join a room
# ---------------------------------------------------------------------------

def render_home():
    st.markdown(
        """
        <div class="hero">
            <div class="crown">👑</div>
            <h1>Badshah Ka Wazeer Kon</h1>
            <div class="subtitle">The classic 4-player deduction game — now online.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_create, tab_join = st.tabs(["🏠  Create Room", "🔑  Join Room"])

    with tab_create:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        with st.form("create_form"):
            name = st.text_input("Your name", max_chars=20, key="create_name", placeholder="e.g. Ali")
            rounds = st.number_input("Number of rounds", min_value=1, max_value=20, value=5, step=1)
            submitted = st.form_submit_button("✨ Create Room", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        if submitted:
            if not name.strip():
                st.error("Enter your name first.")
            else:
                room_code, player_id = room_mod.create_room(name, total_rounds=rounds)
                enter_room(room_code, player_id)
                st.rerun()

    with tab_join:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        with st.form("join_form"):
            name = st.text_input("Your name", max_chars=20, key="join_name", placeholder="e.g. Sara")
            code = st.text_input("Room code", max_chars=5, key="join_code", placeholder="ABCDE").upper()
            submitted = st.form_submit_button("🚪 Join Room", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        if submitted:
            player_id, error = room_mod.join_room(code, name)
            if error:
                st.error(error)
            else:
                enter_room(code.upper(), player_id)
                st.rerun()


# ---------------------------------------------------------------------------
# Waiting room
# ---------------------------------------------------------------------------

def render_waiting(room, player_id):
    st.markdown("<h2 style='text-align:center'>Waiting Room</h2>", unsafe_allow_html=True)
    st.markdown(f"<div class='room-code'>{room['room_code']}</div>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center;color:#9aa1c4;margin-top:8px'>Share this code with the other players.</p>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"**Players joined ({len(room['players'])}/{room['max_players']}):**")
    pills = "".join(
        f"<span class='player-pill'><span class='avatar'>{avatar_letter(p['name'])}</span>{p['name']}</span>"
        for p in room["players"]
    )
    st.markdown(pills, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    remaining = room["max_players"] - len(room["players"])
    if remaining > 0:
        st.info(f"⏳ Waiting for {remaining} more player(s) to join…")
    else:
        st.success("✅ All 4 players are in! Starting the game…")

    if is_host(room, player_id) and len(room["players"]) >= 2 and len(room["players"]) < room["max_players"]:
        st.divider()
        st.caption("Testing convenience — normal play requires exactly 4 players.")
        if st.button("Start now anyway (host, testing only)"):
            game.start_game(room)
            room_mod.save_room(room)
            st.rerun()

    if len(room["players"]) >= room["max_players"] and room["phase"] == "waiting":
        game.start_game(room)
        room_mod.save_room(room)
        st.rerun()


# ---------------------------------------------------------------------------
# Role view phase — each player privately sees only their own role
# ---------------------------------------------------------------------------

def render_role_view(room, player_id):
    role = get_role(room, player_id)
    color = ROLE_COLOR[role]
    st.markdown(
        f"<p style='text-align:center;color:#9aa1c4;font-weight:600'>ROUND {room['current_round']} / {room['total_rounds']}</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="card role-card" style="background:linear-gradient(160deg,{color}2e,{color}0d);
                    border:1px solid {color}77;">
            <div class="emoji">{ROLE_EMOJI[role]}</div>
            <div class="title" style="color:{color} !important;">{role}</div>
            <p class="desc">{ROLE_DESCRIPTIONS[role]}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("🔒 Only you can see this. No one else knows your role yet.")

    already_confirmed = room["confirmations"].get(player_id, False)
    if not already_confirmed:
        if st.button("I've seen my role — Continue", use_container_width=True):
            game.confirm_role(room, player_id)
            room_mod.save_room(room)
            st.rerun()
    else:
        waiting_on = [name_for(room, pid) for pid, ok in room["confirmations"].items() if not ok]
        if waiting_on:
            st.info("Waiting for: " + ", ".join(waiting_on))
        else:
            st.info("Everyone's ready — moving on…")

    if game.all_confirmed(room):
        game.advance_to_guessing(room)
        room_mod.save_room(room)
        st.rerun()


# ---------------------------------------------------------------------------
# Guessing phase — Badshah + Wazeer are public; Wazeer picks the Chor
# ---------------------------------------------------------------------------

def render_guessing(room, player_id):
    st.markdown(
        f"<p style='text-align:center;color:#9aa1c4;font-weight:600'>ROUND {room['current_round']} / {room['total_rounds']}</p>",
        unsafe_allow_html=True,
    )
    st.subheader("🔎 Reveal")

    b_id, w_id = game.badshah_id(room), game.wazeer_id(room)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"<div class='mini-role-card' style='border-color:{ROLE_COLOR['Badshah']}77;"
            f"background:{ROLE_COLOR['Badshah']}18;'>"
            f"<div class='emoji'>{ROLE_EMOJI['Badshah']}</div>"
            f"<div class='label'>Badshah</div><div class='name'>{name_for(room, b_id)}</div></div>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"<div class='mini-role-card' style='border-color:{ROLE_COLOR['Wazeer']}77;"
            f"background:{ROLE_COLOR['Wazeer']}18;'>"
            f"<div class='emoji'>{ROLE_EMOJI['Wazeer']}</div>"
            f"<div class='label'>Wazeer</div><div class='name'>{name_for(room, w_id)}</div></div>",
            unsafe_allow_html=True,
        )

    st.divider()

    if player_id == w_id:
        st.subheader("🕵️ Your move, Wazeer")
        st.write("One of these two is the **Chor**. Choose wisely:")
        hidden_ids = game.hidden_player_ids(room)
        options = {name_for(room, pid): pid for pid in hidden_ids}
        choice_name = st.radio("Who is the Chor?", list(options.keys()))
        if st.button("Submit Guess", use_container_width=True):
            game.submit_guess(room, options[choice_name])
            room_mod.save_room(room)
            st.rerun()
    else:
        st.info(f"⏳ Waiting for **{name_for(room, w_id)}** (the Wazeer) to decide who the Chor is…")


# ---------------------------------------------------------------------------
# Result phase
# ---------------------------------------------------------------------------

def render_result(room, player_id):
    entry = room["round_history"][-1]
    st.markdown(f"<h3 style='text-align:center'>Round {entry['round']} Result</h3>", unsafe_allow_html=True)

    if entry["correct"]:
        st.success(f"✅ The Wazeer correctly caught the Chor: **{name_for(room, entry['guess'])}**!")
    else:
        st.error(
            f"❌ Wrong guess! The Wazeer accused **{name_for(room, entry['guess'])}**, "
            f"but the real Chor was **{name_for(room, game_chor_from_entry(entry))}**."
        )

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("**All roles this round:**")
    pills = "".join(
        f"<span class='player-pill'>{ROLE_EMOJI[role]} {name_for(room, pid)} — {role}</span>"
        for pid, role in entry["roles"].items()
    )
    st.markdown(pills, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("**Scoreboard:**")
    for i, p in enumerate(leaderboard(room), start=1):
        delta = p.get("last_round_points", 0)
        sign = "+" if delta >= 0 else ""
        st.markdown(
            f"<div class='score-row'><span><span class='rank'>#{i}</span>{p['name']}</span>"
            f"<span>{p['score']} pts <span style='color:#9aa1c4'>({sign}{delta})</span></span></div>",
            unsafe_allow_html=True,
        )

    st.write("")
    already_ready = room["confirmations"].get(player_id, False)
    if not already_ready:
        label = "Finish Game — See Results" if room["current_round"] >= room["total_rounds"] else "Continue"
        if st.button(label, use_container_width=True):
            game.ready_for_next(room, player_id)
            room_mod.save_room(room)
            st.rerun()
    else:
        st.caption("Waiting for other players to continue…")

    if game.all_ready(room):
        game.next_round_or_finish(room)
        room_mod.save_room(room)
        st.rerun()


def game_chor_from_entry(entry):
    return next((pid for pid, role in entry["roles"].items() if role == "Chor"), None)


# ---------------------------------------------------------------------------
# Final leaderboard
# ---------------------------------------------------------------------------

def render_finished(room, player_id):
    st.markdown("<h2 style='text-align:center'>🏆 Final Results</h2>", unsafe_allow_html=True)
    ranked = leaderboard(room)
    winner = ranked[0]
    st.markdown(
        f"<div class='card role-card' style='background:linear-gradient(160deg,{ROLE_COLOR['Badshah']}2e,{ROLE_COLOR['Badshah']}0d);"
        f"border:1px solid {ROLE_COLOR['Badshah']}77;'>"
        f"<div class='emoji'>🏆</div><div class='title'>{winner['name']} wins!</div>"
        f"<p class='desc'>{winner['score']} points</p></div>",
        unsafe_allow_html=True,
    )

    st.write("**Final standings:**")
    for i, p in enumerate(ranked, start=1):
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, "▪️")
        st.markdown(
            f"<div class='score-row'><span>{medal} <b>{p['name']}</b></span><span>{p['score']} pts</span></div>",
            unsafe_allow_html=True,
        )

    st.divider()
    if is_host(room, player_id):
        if st.button("🔁 Play Again (same room, reset scores)", use_container_width=True):
            room_mod.reset_for_rematch(room)
            room_mod.save_room(room)
            st.rerun()
    else:
        st.caption("Waiting for the host to start a new game, or you can leave the room.")

    if st.button("Leave Room"):
        leave_room()
        st.rerun()


# ---------------------------------------------------------------------------
# Main router
# ---------------------------------------------------------------------------

def render_sidebar(room, player_id):
    with st.sidebar:
        st.markdown("### 🎲 Room")
        st.markdown(f"<div class='room-code small'>{room['room_code']}</div>", unsafe_allow_html=True)
        st.write(f"You are: **{name_for(room, player_id)}**")
        if room["phase"] not in ("waiting",):
            st.write(f"Round: **{room['current_round']} / {room['total_rounds']}**")
        st.divider()
        st.write("**Players:**")
        for p in room["players"]:
            tag = " (host)" if is_host(room, p["id"]) else ""
            st.write(f"- {p['name']}{tag} — {p.get('score', 0)} pts")
        st.divider()
        if not AUTOREFRESH_AVAILABLE:
            if st.button("🔄 Refresh"):
                st.rerun()
            st.caption("Install `streamlit-autorefresh` for automatic syncing.")
        if st.button("🚪 Leave Room"):
            leave_room()
            st.rerun()


def main():
    room_code = st.session_state.get("room_code")
    player_id = st.session_state.get("player_id")

    if not room_code or not player_id:
        render_home()
        return

    room = room_mod.get_room(room_code)
    if room is None or get_player(room, player_id) is None:
        st.error("That room no longer exists or you're not in it.")
        if st.button("Back to Home"):
            leave_room()
            st.rerun()
        return

    if AUTOREFRESH_AVAILABLE:
        st_autorefresh(interval=2000, key="room_poll")

    render_sidebar(room, player_id)

    phase = room["phase"]
    if phase == "waiting":
        render_waiting(room, player_id)
    elif phase == "role_view":
        render_role_view(room, player_id)
    elif phase == "guessing":
        render_guessing(room, player_id)
    elif phase == "result":
        render_result(room, player_id)
    elif phase == "finished":
        render_finished(room, player_id)
    else:
        st.error(f"Unknown phase: {phase}")


if __name__ == "__main__":
    main()
