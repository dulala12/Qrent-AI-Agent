# survey/utils.py
import json, uuid
from pathlib import Path
from datetime import datetime
from typing import Optional

DATA_DIR = Path("data")

def _normalize_bool_unknown(v):
    if v in (None, "", "unknown"):
        return None
    return bool(v)

def _to_int_or_none(s: Optional[str]):
    if s is None or str(s).strip() == "":
        return None
    try:
        return int(str(s).strip())
    except ValueError:
        return None

def _normalize_commute(v: Optional[str]):
    allowed = {"15","30","45","60",">60","none"}
    if v in (None, "", "unknown"):
        return None
    return v if v in allowed else None

def build_data_json(s: dict) -> dict:
    return {
        "meta": {
            "version": 1,
            "saved_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        },
        "survey": {
            "budget": {
                "weekly_min": _to_int_or_none(s.get("budgetMin")),
                "weekly_max": _to_int_or_none(s.get("budgetMax")),
                "weekly_total": _to_int_or_none(s.get("weeklyTotal")),
                "bills_included": _normalize_bool_unknown(s.get("billsIncluded")),
            },
            "property": {
                "type": s.get("propertyType") or None,
                "furnished": _normalize_bool_unknown(s.get("furnished")),
                "co_rent": s.get("coRent") or None,
                "accept_overpriced": s.get("acceptOverpriced") or None,
                "accept_small": s.get("acceptSmall") or None,
            },
            "lifestyle": {
                "commute": _normalize_commute(s.get("commute")),
                "move_in": s.get("moveIn") or None,
                "lease_months": _to_int_or_none(s.get("leaseMonths")),
            },
        },
    }

def save_data_json(data: dict, filename_stem: Optional[str] = None) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    stem = filename_stem or f"data_{uuid.uuid4().hex}"
    safe = "".join(ch for ch in stem if ch.isalnum() or ch in ("_", "-")) or f"data_{uuid.uuid4().hex}"
    file_path = DATA_DIR / f"{safe}.json"
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return file_path
