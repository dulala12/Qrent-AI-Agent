# survey/utils.py
import json, uuid
from pathlib import Path
from datetime import datetime
from typing import Optional

# 获取绝对路径，确保在任何工作目录下都能正确访问数据文件夹
BASE_DIR = Path(__file__).parent.parent  # 获取backend_django目录
DATA_DIR = BASE_DIR / "data"

def _normalize_bool_unknown(v):
    if v in (None, "", "unknown", "不确定"):
        return None
    if isinstance(v, str):
        return v in ("True", "true", "包含", "愿意", "视情况而定", "是", "yes", "Yes")
    return bool(v)

def _to_int_or_none(s: Optional[str]):
    if s is None or str(s).strip() == "":
        return None
    try:
        # 尝试直接转换
        return int(str(s).strip())
    except ValueError:
        # 尝试从包含数字的字符串中提取数字
        import re
        match = re.search(r'\d+', str(s))
        if match:
            return int(match.group())
        return None

def _normalize_commute(v: Optional[str]):
    if v in (None, "", "unknown"):
        return None
    # 转换前端的"15 分钟"格式为后端需要的"15"格式
    import re
    match = re.search(r'(\d+)', str(v))
    if match:
        minutes = match.group(1)
        if minutes in ["15", "30", "45", "60"]:
            return minutes
        elif int(minutes) > 60:
            return ">60"
    return "none"

def _convert_frontend_to_backend_format(frontend_data: dict) -> dict:
    """将前端提交的数据格式转换为后端需要的格式"""
    # 提取每周预算值（取中间值作为total）
    min_budget = _to_int_or_none(frontend_data.get("minBudget"))
    max_budget = _to_int_or_none(frontend_data.get("maxBudget"))
    weekly_total = None
    if min_budget and max_budget:
        weekly_total = (min_budget + max_budget) // 2
    elif min_budget:
        weekly_total = min_budget
    elif max_budget:
        weekly_total = max_budget
    
    # 转换通勤时间
    commute_time = _normalize_commute(frontend_data.get("commuteTime"))
    
    # 转换合租意愿
    shared_room = frontend_data.get("sharedRoom", "")
    co_rent = None
    if shared_room == "愿意":
        co_rent = "yes"
    elif shared_room == "不愿意":
        co_rent = "no"
    elif shared_room == "视情况而定":
        co_rent = "maybe"
    
    # 转换是否接受小户型
    accept_small = None
    flexibility = frontend_data.get("flexibility", [])
    if "可以接受稍小的房间面积" in flexibility:
        accept_small = "yes"
    elif "对上述条件均不妥协" in flexibility:
        accept_small = "no"
    
    # 转换是否接受高价
    accept_overpriced = None
    if "对上述条件均不妥协" in flexibility:
        accept_overpriced = "yes"  # 不妥协可能意味着接受高价
    
    # 转换租期为月份数
    lease_term = frontend_data.get("leaseTerm", "")
    lease_months = None
    if "6" in lease_term:
        lease_months = 6
    elif "12" in lease_term:
        lease_months = 12
    
    # 假设用户选择的房型意味着家具齐全
    furnished = _normalize_bool_unknown(frontend_data.get("roomType") not in (None, "", "不确定"))
    
    return {
        # 映射到后端期望的字段名
        "budgetMin": frontend_data.get("minBudget"),
        "budgetMax": frontend_data.get("maxBudget"),
        "weeklyTotal": str(weekly_total) if weekly_total else "",
        "billsIncluded": frontend_data.get("includeBills"),
        "propertyType": frontend_data.get("roomType"),
        "furnished": furnished,
        "coRent": co_rent,
        "commute": commute_time,
        "moveIn": frontend_data.get("moveInDate"),
        "leaseMonths": str(lease_months) if lease_months else "",
        "acceptOverpriced": accept_overpriced,
        "acceptSmall": accept_small,
        # 保留原始数据用于参考
        "university": frontend_data.get("university"),
        "flexibility": flexibility
    }

def build_data_json(frontend_data: dict) -> dict:
    # 首先转换数据格式
    converted_data = _convert_frontend_to_backend_format(frontend_data)
    
    return {
        "meta": {
            "version": 1,
            "saved_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            # 保留前端原始数据用于调试
            "frontend_raw_data": frontend_data,
            "converted_data": converted_data
        },
        "survey": {
            "budget": {
                "weekly_min": _to_int_or_none(converted_data.get("budgetMin")),
                "weekly_max": _to_int_or_none(converted_data.get("budgetMax")),
                "weekly_total": _to_int_or_none(converted_data.get("weeklyTotal")),
                "bills_included": _normalize_bool_unknown(converted_data.get("billsIncluded")),
            },
            "property": {
                "type": converted_data.get("propertyType") or None,
                "furnished": converted_data.get("furnished"),
                "co_rent": converted_data.get("coRent"),
                "accept_overpriced": converted_data.get("acceptOverpriced"),
                "accept_small": converted_data.get("acceptSmall"),
            },
            "lifestyle": {
                "commute": converted_data.get("commute"),
                "move_in": converted_data.get("moveIn"),
                "lease_months": _to_int_or_none(converted_data.get("leaseMonths")),
                # 添加额外信息
                "university": converted_data.get("university"),
                "flexibility": converted_data.get("flexibility")
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
