import json
import os

MEMORY_FILE = "memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_memory(conversation):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(conversation, f, ensure_ascii=False, indent=2)
