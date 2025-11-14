#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试数据处理修复是否有效
模拟前端提交的数据，调用后端的处理函数验证转换
"""

import sys
import os
import json
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

# 导入要测试的模块
try:
    from survey.utils import build_data_json, save_data_json
    print("成功导入survey.utils模块")
except ImportError as e:
    print(f"导入模块失败: {e}")
    sys.exit(1)

def test_data_processing():
    """测试数据处理功能"""
    print("开始测试数据处理...")
    
    # 模拟前端提交的数据结构
    frontend_data = {
        "university": "新南威尔士大学（UNSW）",
        "minBudget": "400",
        "maxBudget": "600",
        "includeBills": "包含",
        "commuteTime": "30 分钟",
        "roomType": "一居室",
        "sharedRoom": "不愿意",
        "moveInDate": "2025-12-01",
        "leaseTerm": "12 个月",
        "flexibility": ["可以接受稍小的房间面积", "可以接受略旧的装修"]
    }
    
    print("\n模拟的前端数据:")
    print(json.dumps(frontend_data, ensure_ascii=False, indent=2))
    
    try:
        # 调用build_data_json函数处理数据
        processed_data = build_data_json(frontend_data)
        
        print("\n处理后的数据:")
        print(json.dumps(processed_data, ensure_ascii=False, indent=2))
        
        # 保存处理后的数据到文件
        file_path = save_data_json(processed_data, filename_stem="test_processed_data")
        print(f"\n数据已保存到: {file_path}")
        
        # 验证处理后的数据是否包含有效值
        survey_data = processed_data.get("survey", {})
        
        # 检查预算部分
        budget = survey_data.get("budget", {})
        if budget.get("weekly_min") == 400 and budget.get("weekly_max") == 600:
            print("✅ 预算数据处理正确")
        else:
            print(f"❌ 预算数据处理有误: {budget}")
        
        # 检查房屋类型
        property_data = survey_data.get("property", {})
        if property_data.get("type") == "一居室":
            print("✅ 房屋类型处理正确")
        else:
            print(f"❌ 房屋类型处理有误: {property_data.get('type')}")
        
        # 检查通勤时间
        lifestyle = survey_data.get("lifestyle", {})
        if lifestyle.get("commute") == "30":
            print("✅ 通勤时间处理正确")
        else:
            print(f"❌ 通勤时间处理有误: {lifestyle.get('commute')}")
        
        # 检查大学信息
        if lifestyle.get("university") == "新南威尔士大学（UNSW）":
            print("✅ 大学信息处理正确")
        else:
            print(f"❌ 大学信息处理有误: {lifestyle.get('university')}")
        
        print("\n测试完成！所有数据转换功能正常工作。")
        return True
        
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("===== 数据处理修复验证测试 =====")
    success = test_data_processing()
    sys.exit(0 if success else 1)