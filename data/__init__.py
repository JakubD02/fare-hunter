import json
from pathlib import Path

DATA_DIR = Path(__file__).parent


def load_json(filename: str) -> list[dict]:
    with open(DATA_DIR / filename, encoding="utf-8") as file:
        return json.load(file)


AIRLINES_DATA = load_json("airlines.json")
AIRPORTS_DATA = load_json("airports.json")
