# ai/utils.py - AI分析相关的工具函数
import json
import uuid
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# 定义数据目录
DATA_DIR = Path(__file__).resolve().parents[2] / "data"

# 确保数据目录存在
DATA_DIR.mkdir(exist_ok=True)

def build_data_json(data):
    """构建数据JSON结构"""
    try:
        # 构建基础数据结构
        data_json = {
            "renting_requirements": data,
            "timestamp": str(uuid.uuid4()),
            "analysis_type": "comprehensive"
        }
        return data_json
    except Exception as e:
        logger.error(f"构建数据JSON时发生错误: {str(e)}")
        raise

def save_data_json(data_json, analysis_id=None, filename_stem=None):
    """保存数据到JSON文件"""
    try:
        # 如果没有提供analysis_id，则生成一个新的
        if analysis_id is None:
            # 如果提供了filename_stem，则使用它作为基础
            if filename_stem:
                analysis_id = f"{filename_stem}_{uuid.uuid4()}"
            else:
                analysis_id = str(uuid.uuid4())
        
        # 创建文件路径
        file_path = DATA_DIR / f"{analysis_id}.json"
        
        # 保存数据
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data_json, f, ensure_ascii=False, indent=2)
        
        logger.info(f"数据已保存到: {file_path}")
        return file_path, analysis_id
    except Exception as e:
        logger.error(f"保存数据JSON时发生错误: {str(e)}")
        raise

def load_data_json(analysis_id):
    """从JSON文件加载数据"""
    try:
        file_path = DATA_DIR / f"{analysis_id}.json"
        if not file_path.exists():
            raise FileNotFoundError(f"数据文件不存在: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data
    except Exception as e:
        logger.error(f"加载数据JSON时发生错误: {str(e)}")
        raise

def validate_survey_data(data):
    """验证问卷数据的有效性"""
    try:
        # 基本验证：确保数据是字典类型
        if not isinstance(data, dict):
            raise ValueError("问卷数据必须是JSON对象")
        
        # 验证必要字段
        required_fields = ['renting_requirements']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"缺少必要字段: {field}")
        
        # 可以添加更多的验证逻辑
        return True
    except Exception as e:
        logger.error(f"验证问卷数据时发生错误: {str(e)}")
        raise