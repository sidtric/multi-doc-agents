import os
import json
import uuid

DATA_DIR    = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
STATE_FILE  = os.path.join(DATA_DIR, "state.json")
REPORTS_DIR = os.path.join(DATA_DIR, "reports")
CHATS_DIR   = os.path.join(DATA_DIR, "chats")


# ── sources / reports ──────────────────────────────────────────────────────────

def save_state(sources, reports):
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

    saved_reports = []
    for r in reports:
        path = os.path.join(REPORTS_DIR, r["filename"])
        with open(path, "wb") as f:
            f.write(r["bytes"])
        saved_reports.append({"filename": r["filename"]})

    with open(STATE_FILE, "w") as f:
        json.dump({"sources": sources, "reports": saved_reports}, f, indent=2)


def load_state():
    if not os.path.exists(STATE_FILE):
        return [], []

    with open(STATE_FILE) as f:
        state = json.load(f)

    reports = []
    for r in state.get("reports", []):
        path = os.path.join(REPORTS_DIR, r["filename"])
        if os.path.exists(path):
            with open(path, "rb") as fh:
                reports.append({"filename": r["filename"], "bytes": fh.read()})

    return state.get("sources", []), reports


def clear_state():
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
    if os.path.exists(REPORTS_DIR):
        for f in os.listdir(REPORTS_DIR):
            os.remove(os.path.join(REPORTS_DIR, f))


# ── chats ──────────────────────────────────────────────────────────────────────

def new_chat_id():
    return str(uuid.uuid4())


def _chat_path(chat_id):
    return os.path.join(CHATS_DIR, f"{chat_id}.json")


def save_chat(chat_id, title, messages):
    os.makedirs(CHATS_DIR, exist_ok=True)
    with open(_chat_path(chat_id), "w") as f:
        json.dump({"id": chat_id, "title": title, "messages": messages}, f, indent=2)


def load_chat(chat_id):
    path = _chat_path(chat_id)
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return json.load(f).get("messages", [])


def list_chats():
    if not os.path.exists(CHATS_DIR):
        return []
    chats = []
    for fname in sorted(os.listdir(CHATS_DIR), reverse=True):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(CHATS_DIR, fname)
        with open(path) as f:
            data = json.load(f)
        if data.get("messages"):
            chats.append({"id": data["id"], "title": data.get("title", "Untitled")})
    return chats


def delete_chat(chat_id):
    path = _chat_path(chat_id)
    if os.path.exists(path):
        os.remove(path)
