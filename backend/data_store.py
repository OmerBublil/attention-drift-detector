import json
from pathlib import Path

# Path to the JSON file used as a simple database
DATA_FILE = Path("data.json")

def save_event(event: dict):
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

    # Print event to terminal for debugging
    print("Saved event:", event)
