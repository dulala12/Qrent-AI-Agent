from .views import fetch_and_save_limits_core

def auto_update_limits():
    """��ʱ����ִ�еĺ���"""
    try:
        data = fetch_and_save_limits_core()
        print(f"? ��ʱ����ɹ����� {len(data)} ������")
    except Exception as e:
        print(f"? ��ʱ����ʧ��: {e}")
