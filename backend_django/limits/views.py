import os
import json
import http.client
from django.conf import settings
from django.http import JsonResponse

def fetch_and_save_limits_core():
    """核心逻辑，可被视图和定时任务调用"""
    conn = http.client.HTTPSConnection("api.qrent.rent")
    conn.request("GET", "/properties/region-summary?regions=zetland%20waterloo%20syd%20wolli")
    res = conn.getresponse()
    data = res.read()
    decoded = data.decode("utf-8")
    json_data = json.loads(decoded)

    processed_data = []
    for region in json_data.get("regions", []):
        processed_data.append({
            "region": region.get("region"),
            "avg_rent": region.get("averageWeeklyPrice"),
            "count": region.get("averageCommuteTime"),
        })

    save_path = os.path.join(settings.BASE_DIR, "data", "limits.json")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=4)

    return processed_data


def fetch_and_save_limits(request):
    """Django 视图接口"""
    try:
        data = fetch_and_save_limits_core()
        return JsonResponse({"status": "success", "count": len(data), "preview": data[:2]})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

