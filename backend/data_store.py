import json
from pathlib import Path
from typing import List, Dict

# Path to the JSON file used as a simple database
DATA_FILE = Path("data.json")


def save_event(event: Dict):
    """
    Save a single event into data.json.
    If the file does not exist, it is created.
    """
    # Create file if missing
    if not DATA_FILE.exists():
        with open(DATA_FILE, "w") as f:
            json.dump([], f)

    # Load existing events
    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    # Append new event
    data.append(event)

    # Save updated list back to file
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

    # Debug print to see saved events in the backend terminal
    print("Saved event:", event)


def load_all_events() -> List[Dict]:
    """
    Load all events from data.json.
    Returns an empty list if the file does not exist yet.
    """
    if not DATA_FILE.exists():
        return []

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    return data


def get_events_by_session(session_id: str) -> List[Dict]:
    """
    Return all events that belong to a specific session_id.
    """
    all_events = load_all_events()
    return [e for e in all_events if e.get("session_id") == session_id]
