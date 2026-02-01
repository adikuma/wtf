import json
from datetime import datetime
from pathlib import Path

from .models import StandupResult

WTF_DIR = Path.home() / ".wtf"
HISTORY_DIR = WTF_DIR / "history"
SPENDING_FILE = WTF_DIR / "spending.json"


def init_storage():
    # create directories if they don't exist
    WTF_DIR.mkdir(exist_ok=True)
    HISTORY_DIR.mkdir(exist_ok=True)


def save_standup(result: StandupResult):
    # save standup to history
    init_storage()
    filename = f"{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.json"
    path = HISTORY_DIR / filename
    path.write_text(result.model_dump_json(indent=2), encoding="utf-8")


def load_history(limit: int = 10) -> list[StandupResult]:
    # load recent standups
    init_storage()
    files = sorted(HISTORY_DIR.glob("*.json"), reverse=True)[:limit]
    results = []
    for f in files:
        try:
            results.append(
                StandupResult.model_validate_json(f.read_text(encoding="utf-8"))
            )
        except Exception:
            # skip invalid files
            continue
    return results


def add_spending(cost: float, model: str):
    # append spending record
    init_storage()
    records = load_spending()
    records.append(
        {"timestamp": datetime.now().isoformat(), "model": model, "cost": cost}
    )
    SPENDING_FILE.write_text(json.dumps(records, indent=2), encoding="utf-8")


def get_total_spent() -> float:
    # calculate cumulative spending
    records = load_spending()
    return sum(r.get("cost", 0) for r in records)


def load_spending() -> list:
    if not SPENDING_FILE.exists():
        return []
    return json.loads(SPENDING_FILE.read_text(encoding="utf-8"))
