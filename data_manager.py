import json
import os
from typing import Dict, Any

DATA_FILE = "kamp_planning.json"

def init_default_data() -> Dict[str, Any]:
    return {
        "leiding": ["Hathi", "Baloe", "Raksha", "Kotick","Ferao", "Mor", "Malchi"],
        "activiteiten": ["Ochtendgym", "Ontbijt", "Corvee", "Spel", "Koken", "Avondritueel", "Vrije invulling"],
        "dagen": {
            "Maandag": {
                "start_tijd": "08:00",
                "blokken": [],
                "notulen": {"pluimen": "", "morgen": "", "kinderen": "", "nacht": ""}
            }
        }
    }

def load_data() -> Dict[str, Any]:
    if not os.path.exists(DATA_FILE):
        data = init_default_data()
        save_data(data)
        return data
    
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return init_default_data()

def save_data(data: Dict[str, Any]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
