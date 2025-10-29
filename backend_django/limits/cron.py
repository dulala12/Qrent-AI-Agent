from .views import fetch_and_save_limits_core

def auto_update_limits():
    """定时任务执行的函数"""
    try:
        data = fetch_and_save_limits_core()
        print(f"? 定时任务成功更新 {len(data)} 条数据")
    except Exception as e:
        print(f"? 定时任务失败: {e}")
