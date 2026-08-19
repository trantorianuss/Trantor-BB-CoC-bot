"""Initial state tracking for the bot attack flow.

This is intentionally a small first step toward a state machine.
The states and transitions are expected to evolve as the flow grows.
"""

import os
import time

import config
from logger import log


# Initial flow states.
# These names are provisional and may change when the state machine grows.
IDLE = "IDLE"
STARTING = "STARTING"
WAITING_FIND = "WAITING_FIND"
ATTACKING = "ATTACKING"
WAITING_SURRENDER = "WAITING_SURRENDER"
WAITING_SURRENDER_CONFIRM = "WAITING_SURRENDER_CONFIRM"
WAITING_RESULT = "WAITING_RESULT"


# Current state of the game flow.
current_state = IDLE


_STATE_LOG_DIR = "logs"
_STATE_LOG_FILE = os.path.join(_STATE_LOG_DIR, "state_machine.log")


def get_state():
    """Return the current game-flow state."""
    return current_state


def set_state(new_state):
    """Change the current game-flow state and record the transition."""
    global current_state

    previous_state = current_state
    current_state = new_state

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    message = f"STATE: {previous_state} -> {new_state}"

    # Visible in the normal application logger.
    log(message, debug=True, category="state")

    # Keep a simple historical state-transition log independent of the GUI.
    if config.DEBUG_FILE_LOGS.get("state_machine", False):
        os.makedirs(_STATE_LOG_DIR, exist_ok=True)
        with open(_STATE_LOG_FILE, "a", encoding="utf-8") as file:
            file.write(f"{timestamp} - {previous_state} - {new_state}\n")
