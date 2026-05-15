# database.py
import json
import os

ACTIVE_CHAT_FILE = "active_chat.json"

def save_active_chat(chat_id: int):
    """Active chat ID save karega"""
    data = {"active_chat": chat_id}
    with open(ACTIVE_CHAT_FILE, "w") as f:
        json.dump(data, f)

def get_active_chat():
    """Last active chat ID return karega"""
    if os.path.exists(ACTIVE_CHAT_FILE):
        with open(ACTIVE_CHAT_FILE, "r") as f:
            data = json.load(f)
            return data.get("active_chat")
    return None

def clear_active_chat():
    """Active chat clear karega"""
    if os.path.exists(ACTIVE_CHAT_FILE):
        os.remove(ACTIVE_CHAT_FILE)
