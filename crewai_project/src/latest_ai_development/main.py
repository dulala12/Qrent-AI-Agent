
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
    自动查找最新的 data.json 和 limits.json 文件，并返回输入字典。
    """
    # 自动查找 backend_django/data 下的最新 data_*.json 文件
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(base_dir, "../../../backend_django/data"))
    data_files = glob.glob(os.path.join(data_dir, "data_*.json"))  
    if data_files:
        data_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        data_file = data_files[0]
    else:
        # 如果没找到则使用默认路径
        data_file = 'data.json'

    # limits.json 与 data 文件在同一目录下
    data_dir = os.path.dirname(data_file)
    limits_file = os.path.join(data_dir, 'limits.json')

    def load_json(path):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    print(f"文件解析失败：{path}，请检查 JSON 格式。")
                    return None
        else:
            print(f"文件未找到：{path}")
            return None

    data_content = load_json(data_file)
    limits_content = load_json(limits_file)

    return {
        'data': data_content,
        'limits': limits_content
    }

def run():
    """
    Run the crew.
    """
    # 自动查找最新的data.json文件（按生成时间排序）
    inputs = get_inputs()
    
    try:
        LatestAiDevelopment().crew().kickoff(inputs=inputs)
    except Exception as e:
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
