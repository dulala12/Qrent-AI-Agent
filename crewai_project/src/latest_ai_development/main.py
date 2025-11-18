
import sys
import warnings
import os
import glob
import json
from datetime import datetime

from latest_ai_development.crew import QrentCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

# ======================================================
# 自动读取最新 data.json
# ======================================================
def get_inputs():
    """
    自动查找最新的 data.json 或 test_data.json 文件。
    返回 { "data": {...} }
    """
    print("开始查找数据文件...")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(base_dir, "../../../backend_django/data"))
    print(f"数据目录路径: {data_dir}")

    # 优先 test_data.json
    test_file = os.path.join(data_dir, "test_data.json")
    if os.path.exists(test_file):
        data_file = test_file
        print(f"找到测试数据文件: {data_file}")
    else:
        # 查找所有 data_*.json
        data_files = glob.glob(os.path.join(data_dir, "data_*.json"))
        print(f"找到 {len(data_files)} 个数据文件")

        if data_files:
            data_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            data_file = data_files[0]
            print(f"使用最新的数据文件: {data_file}")
        else:
            data_file = os.path.join(data_dir, "data.json")
            print(f"未找到 data_*.json，使用默认 data.json")

    # 尝试加载 JSON
    def load_json(path):
        print(f"尝试加载文件: {path}")
        if not os.path.exists(path):
            print(f"文件不存在: {path}")
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                print("文件加载成功")
                return data
        except Exception as e:
            print(f"加载 JSON 出错: {e}")
            return None

    data_content = load_json(data_file)

    # 如果无法加载，使用默认数据
    if data_content is None:
        print("警告: 数据损坏，使用默认测试数据")
        data_content = {
            "meta": {"version": 1, "saved_at": datetime.now().isoformat()},
            "survey": {
                "budget": {"weekly_min": 400, "weekly_max": 600, "weekly_total": 500, "bills_included": True},
                "property": {"type": "apartment", "furnished": True, "co_rent": False, "accept_overpriced": False, "accept_small": True},
                "lifestyle": {"commute": 30, "move_in": "2025-12-01", "lease_months": 12}
            }
        }

    return {"data": data_content}


# ======================================================
# 运行 CrewAI
# ======================================================
def run():
    print("=== 开始运行QrentCrew分析 ===")

    inputs = get_inputs()

    try:
        print("初始化 QrentCrew...")
        crew_instance = QrentCrew().crew()

        print("启动 QrentCrew 分析...")
        result = crew_instance.kickoff(inputs=inputs)

        print("=== QrentCrew 分析完成 ===")
        return result

    except Exception as e:
        print(f"运行出错: {e}")
        import traceback
        traceback.print_exc()
        raise


# ======================================================
# CrewAI Training
# ======================================================
def train():
    print("=== 训练 QrentCrew ===")

    inputs = get_inputs()

    try:
        QrentCrew().crew().train(
            n_iterations=int(sys.argv[1]),
            filename=sys.argv[2],
            inputs=inputs
        )
    except Exception as e:
        raise Exception(f"训练失败: {e}")


# ======================================================
# Replay
# ======================================================
def replay():
    print("=== 回放任务 ===")
    try:
        QrentCrew().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"回放失败: {e}")


# ======================================================
# 测试模式
# ======================================================
def test():
    print("=== 测试 QrentCrew ===")

    inputs = get_inputs()

    try:
        QrentCrew().crew().test(
            n_iterations=int(sys.argv[1]),
            eval_llm=sys.argv[2],
            inputs=inputs
        )
    except Exception as e:
        raise Exception(f"测试失败: {e}")