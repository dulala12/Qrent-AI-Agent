
import sys
import warnings
import os
import glob
import json
from datetime import datetime

from latest_ai_development.crew import LatestAiDevelopment

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def get_inputs():
    """
    自动查找最新的 data.json 文件，并返回输入字典。
    """
    print("开始查找数据文件...")
    # 自动查找 backend_django/data 下的最新 data_*.json 文件
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(base_dir, "../../../backend_django/data"))
    print(f"数据目录路径: {data_dir}")
    
    # 先尝试查找test_data.json（用于测试）
    test_file = os.path.join(data_dir, "test_data.json")
    if os.path.exists(test_file):
        data_file = test_file
        print(f"找到测试数据文件: {data_file}")
    else:
        # 查找所有data_*.json文件
        data_files = glob.glob(os.path.join(data_dir, "data_*.json"))  
        print(f"找到 {len(data_files)} 个数据文件")
        
        if data_files:
            data_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            data_file = data_files[0]
            print(f"使用最新的数据文件: {data_file}")
        else:
            # 如果没找到则使用默认路径
            data_file = os.path.join(data_dir, 'data.json')
            print(f"未找到数据文件，使用默认路径: {data_file}")

    def load_json(path):
        print(f"尝试加载文件: {path}")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        print(f"成功加载文件，数据类型: {type(data)}")
                        # 检查数据是否为空或所有值都是null
                        if isinstance(data, dict) and 'survey' in data:
                            survey_data = data['survey']
                            has_valid_data = False
                            for category in survey_data.values():
                                if isinstance(category, dict):
                                    for key, value in category.items():
                                        if value is not None:
                                            has_valid_data = True
                                            break
                                    if has_valid_data:
                                        break
                            if not has_valid_data:
                                print("警告: 数据文件中所有值都是null")
                        return data
                    except json.JSONDecodeError as e:
                        print(f"文件解析失败：{path}，错误: {str(e)}")
                        return None
            except Exception as e:
                print(f"读取文件时出错：{str(e)}")
                return None
        else:
            print(f"文件未找到：{path}")
            return None

    data_content = load_json(data_file)
    
    if data_content is None:
        print("警告: 无法加载数据，使用默认测试数据")
        # 使用默认测试数据
        data_content = {
            "meta": {"version": 1, "saved_at": datetime.now().isoformat()},
            "survey": {
                "budget": {"weekly_min": 400, "weekly_max": 600, "weekly_total": 500, "bills_included": True},
                "property": {"type": "apartment", "furnished": True, "co_rent": False, "accept_overpriced": False, "accept_small": True},
                "lifestyle": {"commute": 30, "move_in": "2025-12-01", "lease_months": 12}
            }
        }

    result = {
        'data': data_content
    }
    print(f"输入数据准备完成，包含有效数据: {bool(data_content)}")
    return result

def run():
    """
    Run the crew.
    """
    print("=== 开始运行CrewAI分析 ===")
    # 自动查找最新的data.json文件（按生成时间排序）
    inputs = get_inputs()
    
    # 确保inputs中只包含data键
    if 'limits' in inputs:
        del inputs['limits']
    
    print(f"准备传递给CrewAI的输入数据: {inputs.keys()}")
    
    try:
        print("正在初始化CrewAI...")
        crew_instance = LatestAiDevelopment().crew()
        print("正在启动CrewAI分析...")
        result = crew_instance.kickoff(inputs=inputs)
        print("=== CrewAI分析完成 ===")
        print(f"分析结果类型: {type(result)}")
        return result
    except Exception as e:
        print(f"运行CrewAI时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = get_inputs() # type: ignore
    try:
        LatestAiDevelopment().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        LatestAiDevelopment().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = get_inputs() # type: ignore
    
    try:
        LatestAiDevelopment().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
