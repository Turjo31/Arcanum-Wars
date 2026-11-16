"""Save file: unlocked fighters and rival progress (stored as save.json in the project root)."""
import json, pathlib
from ai.teams import STARTERS

PATH = pathlib.Path(__file__).resolve().parent.parent / "save.json"


def default():
    return {"unlocked": list(STARTERS), "tier": 0, "wins": 0, "battles": 0}


def load():
    data = default()
    try:
        data.update(json.loads(PATH.read_text(encoding="utf-8")))
    except (OSError, ValueError):
        pass
    return data


def save(data):
    try:
        PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except OSError:
        pass


def reset():
    d = default(); save(d); return d
