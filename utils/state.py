import json
import os

STATE_FILE = "last_signal.json"


def load_state():
    if not os.path.exists(STATE_FILE):
        return {}
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def already_signaled(pair, candle_time):
    state = load_state()
    return state.get(pair) == candle_time


def mark_signaled(pair, candle_time):
    state = load_state()
    state[pair] = candle_time
    save_state(state)
